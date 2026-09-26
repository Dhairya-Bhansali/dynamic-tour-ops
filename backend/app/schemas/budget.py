from pydantic import BaseModel
from typing import List, Optional
from app.schemas.itinerary import ItineraryItemBase

class OptimizeRequest(BaseModel):
    target_budget: float
    optimization_priority: str = "balanced" # 'experience_max', 'minimal_travel', 'preserve_favorites', 'balanced'
    preserve_categories: List[str] = []
    preserve_item_ids: List[int] = []
    natural_language_request: Optional[str] = None

class ScenarioChange(BaseModel):
    removed_items: List[dict] = []
    added_items: List[dict] = []
    explanation: str

class OptimizedScenario(BaseModel):
    scenario_id: str
    name: str
    total_cost: float
    preference_match: int
    experience_coverage: int
    budget_fit: int
    time_efficiency: int
    location_efficiency: int
    changes: ScenarioChange
    items: List[dict]

class OptimizeResponse(BaseModel):
    current_cost: float
    target_budget: float
    scenarios: List[OptimizedScenario]

class ApplyScenarioRequest(BaseModel):
    scenario_items: List[dict]
