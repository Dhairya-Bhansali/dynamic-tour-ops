import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.core_models import Base, Trip, Itinerary, ItineraryItem, Disruption, AlternativePlan
from app.models.enums import DisruptionStatus
from app.services.disruption_engine import DisruptionEngine

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Setup initial mock data
    trip = Trip(id=1, destinations=["Test"], budget=5000)
    itin = Itinerary(id=1, trip_id=1, version=1, is_active=True)
    item = ItineraryItem(id=1, itinerary_id=1, activity_type="Flight", description="Mock Flight", estimated_cost=100.0, day_number=1)
    
    db.add(trip)
    db.add(itin)
    db.add(item)
    db.commit()
    
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_simulate_disruption(db):
    d = DisruptionEngine.simulate_disruption(db, 1, "PRICE_CHANGE")
    assert d.id is not None
    assert d.disruption_type == "PRICE_CHANGE"
    assert d.severity == "HIGH"
    assert d.status == DisruptionStatus.DETECTED
    assert d.trip_id == 1
    assert "cost_impact" in d.impact_summary

def test_analyze_disruption(db):
    d = DisruptionEngine.simulate_disruption(db, 1, "PRICE_CHANGE")
    d = DisruptionEngine.analyze_and_generate_alternatives(db, d.id)
    assert d.status == DisruptionStatus.ALTERNATIVES_READY
    
    alts = db.query(AlternativePlan).filter(AlternativePlan.disruption_id == d.id).all()
    assert len(alts) > 0
    assert alts[0].items is not None
    assert alts[0].cost_difference is not None

def test_reject_disruption(db):
    d = DisruptionEngine.simulate_disruption(db, 1, "PRICE_CHANGE")
    d = DisruptionEngine.reject_disruption(db, d.id)
    assert d.status == DisruptionStatus.REJECTED
    
    # Ensure active itinerary remains version 1
    active = db.query(Itinerary).filter(Itinerary.trip_id == 1, Itinerary.is_active == True).first()
    assert active.version == 1

def test_approve_disruption_alternative(db):
    d = DisruptionEngine.simulate_disruption(db, 1, "PRICE_CHANGE")
    d = DisruptionEngine.analyze_and_generate_alternatives(db, d.id)
    
    alts = db.query(AlternativePlan).filter(AlternativePlan.disruption_id == d.id).all()
    alt_to_approve = alts[0]
    
    new_itin = DisruptionEngine.approve_alternative(db, d.id, alt_to_approve.id)
    assert new_itin.version == 2
    assert new_itin.is_active == True
    
    # Old should be inactive
    old_itin = db.query(Itinerary).filter(Itinerary.id == 1).first()
    assert old_itin.is_active == False
    
    # Disruption should be approved
    db.refresh(d)
    assert d.status == DisruptionStatus.APPROVED
