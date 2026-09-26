import pytest
from app.schemas.budget import OptimizeRequest
from app.services.budget_optimizer import BudgetOptimizerService
from app.models.core_models import ItineraryItem, Itinerary

class MockDB:
    def __init__(self):
        self.added = []
    def query(self, model):
        class Query:
            def filter(self, *args, **kwargs): return self
            def first(self): 
                if model == Itinerary:
                    it = Itinerary()
                    it.id = 1
                    it.trip_id = 1
                    it.version = 1
                    return it
                return None
            def all(self):
                if model == ItineraryItem:
                    it1 = ItineraryItem(id=1, itinerary_id=1, estimated_cost=100.0, activity_type="Flight", description="Test Flight")
                    it2 = ItineraryItem(id=2, itinerary_id=1, estimated_cost=200.0, activity_type="Hotel", description="Test Hotel")
                    it3 = ItineraryItem(id=3, itinerary_id=1, estimated_cost=50.0, activity_type="Activity", description="Test Act")
                    return [it1, it2, it3]
                return [] # Return empty for FlightOffer/HotelOffer/ActivityOffer so fallback generates mock items
            def order_by(self, *args): return self
            def desc(self): return self
        return Query()
    def add(self, obj): self.added.append(obj)
    def commit(self): pass
    def flush(self): pass
    def refresh(self, obj): pass

def test_optimization_strategies():
    db = MockDB()
    req = OptimizeRequest(target_budget=200.0)
    res = BudgetOptimizerService.generate_scenarios(db, 1, req)
    
    assert res.current_cost == 350.0
    assert len(res.scenarios) == 3
    
    max_savings = next(s for s in res.scenarios if s.strategy == "MAX_SAVINGS")
    balanced = next(s for s in res.scenarios if s.strategy == "BALANCED")
    preserve = next(s for s in res.scenarios if s.strategy == "PRESERVE_EXPERIENCES")
    
    # Max savings should have highest savings
    assert max_savings.optimized_cost < balanced.optimized_cost
    assert max_savings.savings > 0
    assert len(max_savings.changed_components) > 0

    # Test audit creation
    assert len(db.added) > 0 # Audit logs should be created
