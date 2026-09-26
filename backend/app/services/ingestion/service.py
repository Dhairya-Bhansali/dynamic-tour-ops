from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
import uuid
from typing import Dict, List, Optional
from app.models.ingestion_models import DataSource, FlightOffer, HotelOffer, WeatherForecast, Route, IngestionRun
from app.services.ingestion.amadeus import AmadeusConnector
from app.services.ingestion.open_meteo import OpenMeteoConnector
from app.services.ingestion.osm import OSRMConnector
from app.services.ingestion.freshness import FreshnessEngine

class IngestionService:
    def __init__(self, db: Session, env: str = "DEMO"):
        self.db = db
        self.env = env
        self.amadeus = AmadeusConnector(db, env)
        self.open_meteo = OpenMeteoConnector(db, env)
        self.osrm = OSRMConnector(db, env)

    def _get_or_create_datasource(self, provider_name: str, provider_type: str) -> DataSource:
        ds = self.db.query(DataSource).filter(
            DataSource.provider_name == provider_name,
            DataSource.provider_type == provider_type,
            DataSource.mode == self.env
        ).first()
        if not ds:
            ds = DataSource(
                provider_name=provider_name,
                provider_type=provider_type,
                mode=self.env,
                status="HEALTHY",
                enabled=True,
                records_received=0,
                records_inserted=0,
                records_updated=0,
                records_rejected=0,
            )
            self.db.add(ds)
            self.db.commit()
            self.db.refresh(ds)
        return ds

    def _start_run(self, provider: str, dataset_type: str) -> IngestionRun:
        run = IngestionRun(
            run_id=str(uuid.uuid4()),
            provider=provider,
            dataset_type=dataset_type,
            started_at=datetime.utcnow(),
            status="RUNNING"
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def _end_run(self, run: IngestionRun, ds: DataSource, status: str, error: str = None):
        run.completed_at = datetime.utcnow()
        run.duration = (run.completed_at - run.started_at).total_seconds()
        run.status = status
        run.error_message = error
        
        ds.last_attempted_sync = run.started_at
        ds.records_received += run.records_received
        ds.records_inserted += run.records_inserted
        ds.records_updated += run.records_updated
        ds.records_rejected += run.records_rejected
        
        if status in ["SUCCESS", "PARTIAL"]:
            ds.last_successful_sync = run.completed_at
            
        FreshnessEngine.update_datasource_health(self.db, ds, error)
        self.db.commit()

    def sync_flights(self, origin: str, destination: str, date: str) -> List[FlightOffer]:
        ds = self._get_or_create_datasource("Amadeus", "flights")
        run = self._start_run("Amadeus", "flights")
        
        try:
            raw_offers = self.amadeus.fetch_flight_offers(origin, destination, date)
            run.records_received = len(raw_offers)
            
            # Normalization & Deduplication
            normalized_offers = []
            now = datetime.utcnow()
            valid_until = now + FreshnessEngine.get_threshold("flights")

            for raw in raw_offers:
                ext_id = raw.get("id")
                # Validation
                if not ext_id or not raw.get("price") or not raw["price"].get("total"):
                    run.records_rejected += 1
                    continue
                    
                price = float(raw["price"]["total"])
                if price <= 0:
                    run.records_rejected += 1
                    continue

                currency = raw["price"].get("currency", "USD")
                
                # Deduplication: check if exists
                existing = self.db.query(FlightOffer).filter(
                    FlightOffer.provider == "Amadeus",
                    FlightOffer.external_id == ext_id
                ).first()
                
                if existing:
                    existing.total_price = price
                    existing.updated_at = now
                    existing.fetched_at = now
                    existing.valid_from = now
                    existing.valid_until = valid_until
                    existing.freshness_status = "FRESH"
                    normalized_offers.append(existing)
                    run.records_updated += 1
                else:
                    new_offer = FlightOffer(
                        provider="Amadeus",
                        external_id=ext_id,
                        origin=origin,
                        destination=destination,
                        departure_time=now + timedelta(days=random.randint(1, 30)),
                        arrival_time=now + timedelta(days=random.randint(1, 30), hours=5),
                        duration=300,
                        stops=0,
                        airline=raw.get("validatingAirlineCodes", ["XX"])[0] if raw.get("validatingAirlineCodes") else "XX",
                        base_price=price * 0.8,
                        taxes=price * 0.2,
                        total_price=price,
                        currency=currency,
                        fetched_at=now,
                        updated_at=now,
                        valid_from=now,
                        valid_until=valid_until,
                        freshness_status="FRESH"
                    )
                    self.db.add(new_offer)
                    normalized_offers.append(new_offer)
                    run.records_inserted += 1
            
            self._end_run(run, ds, "SUCCESS" if run.records_rejected == 0 else "PARTIAL")
            return normalized_offers
        except Exception as e:
            self._end_run(run, ds, "FAILED", str(e))
            raise e

    def sync_weather(self, lat: float, lng: float, location_name: str) -> WeatherForecast:
        ds = self._get_or_create_datasource("OpenMeteo", "weather")
        run = self._start_run("OpenMeteo", "weather")
        
        try:
            raw_data = self.open_meteo.fetch_weather(lat, lng, "today")
            run.records_received = 1
            
            # Validation
            if not raw_data or "daily" not in raw_data or not raw_data["daily"].get("temperature_2m_max"):
                run.records_rejected += 1
                self._end_run(run, ds, "FAILED", "Invalid weather payload")
                raise ValueError("Invalid weather payload")
                
            today_temp = raw_data["daily"]["temperature_2m_max"][0]
            today_precip = raw_data["daily"].get("precipitation_probability_max", [0])[0]
            weather_code = str(raw_data["daily"].get("weathercode", [0])[0])
            
            now = datetime.utcnow()
            valid_until = now + FreshnessEngine.get_threshold("weather")
            
            # Deduplication logic (we can update existing forecast for the location for today)
            existing = self.db.query(WeatherForecast).filter(
                WeatherForecast.provider == "OpenMeteo",
                WeatherForecast.location == location_name
            ).first()
            
            if existing:
                existing.temperature = today_temp
                existing.precipitation_probability = today_precip
                existing.weather_code = weather_code
                existing.fetched_at = now
                existing.updated_at = now
                existing.valid_from = now
                existing.valid_until = valid_until
                existing.freshness_status = "FRESH"
                forecast = existing
                run.records_updated += 1
            else:
                forecast = WeatherForecast(
                    provider="OpenMeteo",
                    location=location_name,
                    latitude=lat,
                    longitude=lng,
                    date=now,
                    temperature=today_temp,
                    precipitation_probability=today_precip,
                    precipitation=0.0,
                    wind_speed=0.0,
                    visibility=10000.0,
                    weather_code=weather_code,
                    fetched_at=now,
                    updated_at=now,
                    valid_from=now,
                    valid_until=valid_until,
                    freshness_status="FRESH"
                )
                self.db.add(forecast)
                run.records_inserted += 1
                
            self._end_run(run, ds, "SUCCESS")
            return forecast
        except Exception as e:
            self._end_run(run, ds, "FAILED", str(e))
            raise e

    def get_data_sources_status(self) -> List[Dict]:
        sources = self.db.query(DataSource).all()
        # update health explicitly on query
        for s in sources:
            FreshnessEngine.update_datasource_health(self.db, s)
            
        return [
            {
                "id": s.id,
                "provider_name": s.provider_name,
                "provider_type": s.provider_type,
                "mode": s.mode,
                "status": s.status,
                "freshness_status": s.freshness_status,
                "last_successful_sync": s.last_successful_sync.isoformat() if s.last_successful_sync else None,
                "last_attempted_sync": s.last_attempted_sync.isoformat() if s.last_attempted_sync else None,
                "records_received": s.records_received,
                "records_inserted": s.records_inserted,
                "records_updated": s.records_updated,
                "records_rejected": s.records_rejected,
                "stale_record_count": s.stale_record_count,
                "error_count": s.error_count,
                "latency_ms": s.latency_ms,
                "enabled": s.enabled
            } for s in sources
        ]
