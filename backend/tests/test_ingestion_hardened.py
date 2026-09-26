import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.models.ingestion_models import Base, DataSource, IngestionRun, FlightOffer, WeatherForecast
from app.services.ingestion.service import IngestionService
from app.services.ingestion.freshness import FreshnessEngine

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_successful_flight_ingestion_and_idempotency(db):
    service = IngestionService(db, env="DEMO")
    
    # Sync 1
    offers1 = service.sync_flights("JFK", "LHR", "2024-12-01")
    assert len(offers1) > 0
    
    # Sync 2 (Idempotent)
    offers2 = service.sync_flights("JFK", "LHR", "2024-12-01")
    assert len(offers2) > 0
    
    # Check deduplication
    count = db.query(FlightOffer).count()
    assert count == len(offers1) # Should not duplicate records

def test_failed_ingestion_weather(db, monkeypatch):
    service = IngestionService(db, env="DEMO")
    
    # Mock open_meteo failure
    def mock_fetch(*args, **kwargs):
        raise ValueError("Simulated Timeout")
    
    monkeypatch.setattr(service.open_meteo, "fetch_weather", mock_fetch)
    
    with pytest.raises(ValueError):
        service.sync_weather(40.7, -74.0, "NYC")
        
    ds = db.query(DataSource).filter(DataSource.provider_name == "OpenMeteo").first()
    assert ds.status == "ERROR"
    assert ds.error_count == 1
    
    run = db.query(IngestionRun).first()
    assert run.status == "FAILED"
    assert "Simulated Timeout" in run.error_message

def test_stale_data_detection(db):
    ds = DataSource(
        provider_name="Amadeus",
        provider_type="flights",
        mode="DEMO",
        status="HEALTHY",
        last_successful_sync=datetime.utcnow() - timedelta(minutes=45),
        enabled=True
    )
    db.add(ds)
    db.commit()
    
    FreshnessEngine.update_datasource_health(db, ds)
    
    assert ds.status == "STALE"
    assert ds.freshness_status == "STALE"

def test_freshness_engine():
    now = datetime.utcnow()
    # Flight is 30 mins
    assert FreshnessEngine.evaluate_freshness("flights", now - timedelta(minutes=15), now) == "FRESH"
    assert FreshnessEngine.evaluate_freshness("flights", now - timedelta(minutes=45), now) == "STALE"
    # Weather is 60 mins
    assert FreshnessEngine.evaluate_freshness("weather", now - timedelta(minutes=45), now) == "FRESH"
    assert FreshnessEngine.evaluate_freshness("weather", now - timedelta(minutes=75), now) == "STALE"

def test_optimizer_uses_fallback_if_no_fresh(db):
    from app.services.budget_optimizer import BudgetOptimizerService
    from app.models.core_models import ItineraryItem
    Base.metadata.create_all(bind=engine) # ensure all core tables are there (done by fixture, but they aren't imported there)

    # Core models need to be created
    from app.models.core_models import Base as CoreBase
    CoreBase.metadata.create_all(bind=engine)
    
    # Add a stale flight offer
    offer = FlightOffer(
        provider="Amadeus",
        external_id="flight1",
        origin="JFK",
        destination="LHR",
        total_price=500.0,
        currency="USD",
        fetched_at=datetime.utcnow() - timedelta(minutes=45),
        freshness_status="STALE"
    )
    db.add(offer)
    db.commit()
    
    item = ItineraryItem(activity_type="flight", estimated_cost=500.0, description="NYC to LHR")
    candidate = BudgetOptimizerService._fetch_candidates(db, item, "BALANCED")
    
    assert candidate is not None
    assert candidate["freshness_status"] in ["STALE", "FALLBACK"]
