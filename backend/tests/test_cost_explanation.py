import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.core_models import Base, Trip, Itinerary, ItineraryItem, OptimizationAudit, Disruption
from app.models.enums import DisruptionStatus
from app.services.cost_explanation_service import CostExplanationService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    trip = Trip(id=1, destinations=["TestCity"], budget=5000)
    itin = Itinerary(id=1, trip_id=1, version=1, is_active=True)
    item = ItineraryItem(id=1, itinerary_id=1, estimated_cost=1000.0)
    
    audit = OptimizationAudit(
        trip_id=1,
        original_itinerary_version=1,
        optimization_strategy="BALANCED",
        target_budget=5000,
        original_cost=1000,
        optimized_cost=900,
        savings=100,
        changed_components=[{
            "component_type": "Flight",
            "original_cost": 1000,
            "optimized_cost": 900,
            "savings": 100,
            "source": "DEMO FALLBACK",
            "freshness": "< 1 hr"
        }],
        data_sources=["DEMO FALLBACK"]
    )
    
    disruption = Disruption(
        trip_id=1,
        disruption_type="PRICE_CHANGE",
        severity="HIGH",
        title="Flight Price Jump",
        status=DisruptionStatus.DETECTED,
        impact_summary={"cost_impact": 200},
        impact_radius={"downstream_affected": []}
    )
    
    db.add_all([trip, itin, item, audit, disruption])
    db.commit()
    
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_cost_explanation(db):
    exp = CostExplanationService.get_cost_explanation(db, 1)
    
    # 1. Correct original cost
    assert exp["original_total"] == 1000
    
    # 2. Correct optimized cost
    assert exp["optimized_total"] == 900
    
    # 3. Correct savings
    assert exp["savings"] == 100
    
    # 4. Correct component diff
    assert len(exp["components"]) == 1
    assert exp["components"][0]["component_type"] == "FLIGHT"
    
    # 5. Correct budget delta
    assert exp["budget_delta"] == -4000 # 1000 current - 5000 target
    
    # 6. Correct provenance
    assert exp["components"][0]["source"] == "DEMO FALLBACK"
    
    # 7. Correct freshness
    assert exp["components"][0]["freshness"] == "< 1 hr"
    
    # 8. Correct cost-of-inaction
    assert exp["projected_unmanaged_cost"] == 1200 # 1000 current + 200 impact
    assert exp["avoided_cost"] == 300 # 1200 - 900

def test_operator_cost_control(db):
    ctrl = CostExplanationService.get_operator_cost_control(db)
    
    assert ctrl["active_trips"] == 1
    assert ctrl["at_risk_trips"] == 1
    assert ctrl["potential_cost_impact"] == 200
    assert ctrl["potential_avoided_cost"] == 300
    
    risk = ctrl["cost_at_risk"][0]
    assert risk["current_cost"] == 1000
    assert risk["potential_impact"] == 200
    assert risk["optimized_cost"] == 900
    assert risk["potential_avoided_cost"] == 300
    assert risk["status"] == "DETECTED"
