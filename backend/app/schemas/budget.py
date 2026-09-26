from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class OptimizeRequest(BaseModel):
    target_budget: Optional[float] = None
    strategies: List[str] = ["MAX_SAVINGS", "BALANCED", "PRESERVE_EXPERIENCES"]
    preserve_item_ids: List[int] = []

class ComponentDiff(BaseModel):
    component_type: str
    original_cost: float
    optimized_cost: float
    savings: float
    reason: str
    source: str
    fetched_at: Optional[datetime] = None
    freshness: str

class OptimizationResult(BaseModel):
    scenario_id: str
    strategy: str
    name: str
    original_cost: float
    optimized_cost: float
    savings: float
    savings_percentage: float
    budget_fit: int
    preference_score: int
    feasibility: str
    currency: str = "USD"
    data_sources: List[str]
    changed_components: List[ComponentDiff]
    items: List[Dict[str, Any]]

class OptimizeResponse(BaseModel):
    current_cost: float
    target_budget: Optional[float] = None
    breakdown: Dict[str, float]
    scenarios: List[OptimizationResult]
    currency: str = "USD"

class ApplyScenarioRequest(BaseModel):
    scenario_items: List[dict]
    scenario_id: str
