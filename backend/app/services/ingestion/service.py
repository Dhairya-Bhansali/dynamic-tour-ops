from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from typing import Dict, List, Optional
from app.models.ingestion_models import DataSource, FlightOffer, HotelOffer, WeatherForecast, Route
from app.services.ingestion.amadeus import AmadeusConnector
from app.services.ingestion.open_meteo import OpenMeteoConnector
from app.services.ingestion.osm import OSRMConnector

class IngestionService:
    def __init__(self, db: Session, env: str = "DEMO"):
        self.db = db
        self.env = env
        self.amadeus = AmadeusConnector(db, env)
        self.open_meteo = OpenMeteoConnector(db, env)
        self.osrm = OSRMConnector(db, env)

    def _get_or_create_datasource(self, provider: str, data_type: str) -> DataSource:
        ds = self.db.query(DataSource).filter(
            DataSource.provider == provider,
            DataSource.data_type == data_type,
            DataSource.environment == self.env
        ).first()
        if not ds:
            ds = DataSource(
                provider=provider,
                data_type=data_type,
                environment=self.env,
                status="ACTIVE",
                enabled=True,
                records_ingested=0
            )
            self.db.add(ds)
            self.db.commit()
            self.db.refresh(ds)
        return ds

    def _update_datasource_status(self, ds: DataSource, success: bool, error: str = None, count: int = 0):
        if success:
            ds.last_success_at = datetime.utcnow()
            ds.records_ingested += count
            ds.status = "ACTIVE"
            ds.last_error = None
        else:
            ds.last_failure_at = datetime.utcnow()
            ds.status = "ERROR"
            ds.last_error = error
        self.db.commit()

    def sync_flights(self, origin: str, destination: str, date: str) -> List[FlightOffer]:
        ds = self._get_or_create_datasource("Amadeus", "flights")
        try:
            raw_offers = self.amadeus.fetch_flight_offers(origin, destination, date)
            # Normalization & Deduplication
            normalized_offers = []
            for raw in raw_offers:
                ext_id = raw.get("id")
                # Deduplication: check if exists
                existing = self.db.query(FlightOffer).filter(FlightOffer.external_id == ext_id).first()
                
                price = float(raw.get("price", {}).get("total", 0.0))
                currency = raw.get("price", {}).get("currency", "USD")
                
                if existing:
                    existing.total_price = price
                    existing.updated_at = datetime.utcnow()
                    normalized_offers.append(existing)
                else:
                    new_offer = FlightOffer(
                        provider="Amadeus",
                        external_id=ext_id,
                        origin=origin,
                        destination=destination,
                        departure_time=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                        arrival_time=datetime.utcnow() + timedelta(days=random.randint(1, 30), hours=5),
                        duration=300,
                        stops=0,
                        airline=raw.get("validatingAirlineCodes", ["XX"])[0] if raw.get("validatingAirlineCodes") else "XX",
                        base_price=price * 0.8,
                        taxes=price * 0.2,
                        total_price=price,
                        currency=currency,
                        valid_until=datetime.utcnow() + timedelta(hours=1)
                    )
                    self.db.add(new_offer)
                    normalized_offers.append(new_offer)
            
            self.db.commit()
            self._update_datasource_status(ds, True, count=len(normalized_offers))
            return normalized_offers
        except Exception as e:
            self._update_datasource_status(ds, False, error=str(e))
            raise e

    def sync_weather(self, lat: float, lng: float, location_name: str) -> WeatherForecast:
        ds = self._get_or_create_datasource("OpenMeteo", "weather")
        try:
            raw_data = self.open_meteo.fetch_weather(lat, lng, "today")
            # Normalization
            today_temp = raw_data.get("daily", {}).get("temperature_2m_max", [0])[0]
            today_precip = raw_data.get("daily", {}).get("precipitation_probability_max", [0])[0]
            
            forecast = WeatherForecast(
                provider="OpenMeteo",
                location=location_name,
                latitude=lat,
                longitude=lng,
                date=datetime.utcnow(),
                temperature=today_temp,
                precipitation_probability=today_precip,
                precipitation=0.0,
                wind_speed=0.0,
                visibility=10000.0,
                weather_code=str(raw_data.get("daily", {}).get("weathercode", [0])[0]),
                valid_until=datetime.utcnow() + timedelta(hours=12)
            )
            self.db.add(forecast)
            self.db.commit()
            self._update_datasource_status(ds, True, count=1)
            return forecast
        except Exception as e:
            self._update_datasource_status(ds, False, error=str(e))
            raise e

    def get_data_sources_status(self) -> List[Dict]:
        sources = self.db.query(DataSource).all()
        return [
            {
                "id": s.id,
                "provider": s.provider,
                "data_type": s.data_type,
                "environment": s.environment,
                "status": s.status,
                "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
                "last_failure_at": s.last_failure_at.isoformat() if s.last_failure_at else None,
                "last_error": s.last_error,
                "records_ingested": s.records_ingested,
                "enabled": s.enabled
            } for s in sources
        ]
