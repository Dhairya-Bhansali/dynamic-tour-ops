import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def append_to_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip() + "\n")

def replace_in_file(path, old, new):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if old not in content:
        print(f"Warning: '{old}' not found in {path}")
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# 1. Create schemas/budget.py
create_file("backend/app/schemas/budget.py", """
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
""")

# 2. Create services/budget_optimizer.py
create_file("backend/app/services/budget_optimizer.py", """
import copy
from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, ItineraryItem
from app.schemas.budget import OptimizeRequest, OptimizeResponse, OptimizedScenario, ScenarioChange

class BudgetOptimizerService:
    @staticmethod
    def generate_scenarios(db: Session, trip_id: int, request: OptimizeRequest) -> OptimizeResponse:
        active_itin = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
        if not active_itin:
            raise Exception("No active itinerary found.")
            
        current_items = db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == active_itin.id).all()
        current_cost = sum(i.estimated_cost or 0 for i in current_items)
        
        # We will mock the deterministic combinations for the hackathon context
        # A real engine would run combinatorial optimization (e.g. Knapsack variant)
        scenarios = []
        
        # Helpers to mock the data
        def build_scenario(name, cost_reduction, score_penalty, removed_desc, added_desc, exp_cov, time_eff, scenario_id):
            new_cost = max(request.target_budget * 0.9, current_cost - cost_reduction)
            budget_fit = 100 if new_cost <= request.target_budget else int((request.target_budget / new_cost) * 100)
            
            # Create modified items payload based on current items
            new_items = []
            removed = []
            
            for item in current_items:
                # Mock removing highest cost item
                if item.estimated_cost and item.estimated_cost > 30 and len(removed) == 0:
                    removed.append({"id": item.id, "description": item.description, "cost": item.estimated_cost})
                else:
                    item_dict = {
                        "day_number": item.day_number,
                        "day_date": item.day_date.isoformat() if item.day_date else None,
                        "start_time": item.start_time.isoformat() if item.start_time else None,
                        "end_time": item.end_time.isoformat() if item.end_time else None,
                        "activity_type": item.activity_type,
                        "description": item.description,
                        "location": item.location,
                        "estimated_cost": item.estimated_cost,
                        "ai_reasoning": item.ai_reasoning,
                        "confidence_score": item.confidence_score
                    }
                    new_items.append(item_dict)
                    
            added = [{"description": added_desc, "cost": 10.0}]
            
            return OptimizedScenario(
                scenario_id=scenario_id,
                name=name,
                total_cost=new_cost,
                preference_match=max(50, 91 - score_penalty),
                experience_coverage=exp_cov,
                budget_fit=budget_fit,
                time_efficiency=time_eff,
                location_efficiency=85,
                changes=ScenarioChange(
                    removed_items=removed,
                    added_items=added,
                    explanation=f"Removed {removed[0]['description'] if removed else 'some items'} and added {added_desc}."
                ),
                items=new_items
            )

        if request.optimization_priority == 'experience_max' or request.optimization_priority == 'balanced':
            scenarios.append(build_scenario(
                "SCENARIO A — EXPERIENCE MAX", 
                cost_reduction=current_cost * 0.2, 
                score_penalty=3, 
                removed_desc="expensive luxury dining", 
                added_desc="local food market", 
                exp_cov=95, 
                time_eff=88,
                scenario_id="scenario_a"
            ))
            
        if request.optimization_priority == 'minimal_travel' or request.optimization_priority == 'balanced':
            scenarios.append(build_scenario(
                "SCENARIO B — MINIMAL TRAVEL", 
                cost_reduction=current_cost * 0.25, 
                score_penalty=6, 
                removed_desc="distant excursions", 
                added_desc="nearby cultural walk", 
                exp_cov=82, 
                time_eff=98,
                scenario_id="scenario_b"
            ))

        if request.optimization_priority == 'preserve_favorites' or request.optimization_priority == 'balanced':
            scenarios.append(build_scenario(
                "SCENARIO C — PRESERVE FAVORITES", 
                cost_reduction=current_cost * 0.15, 
                score_penalty=1, 
                removed_desc="optional upgrades", 
                added_desc="budget alternatives", 
                exp_cov=90, 
                time_eff=85,
                scenario_id="scenario_c"
            ))
            
        return OptimizeResponse(
            current_cost=current_cost,
            target_budget=request.target_budget,
            scenarios=scenarios
        )
        
    @staticmethod
    def apply_scenario(db: Session, trip_id: int, request: dict):
        existing_versions = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).count()
        new_version_num = existing_versions + 1
        
        new_itinerary = Itinerary(
            trip_id=trip_id, 
            version=new_version_num, 
            is_active=True,
            generation_method="BUDGET OPTIMIZED"
        )
        db.add(new_itinerary)
        db.flush()
        
        # Deactivate old
        db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.id != new_itinerary.id).update({"is_active": False})
        
        for item in request.get('scenario_items', []):
            import dateutil.parser
            it = ItineraryItem(
                itinerary_id=new_itinerary.id,
                day_number=item.get('day_number'),
                day_date=dateutil.parser.isoparse(item.get('day_date')) if item.get('day_date') else None,
                start_time=dateutil.parser.isoparse(item.get('start_time')) if item.get('start_time') else None,
                end_time=dateutil.parser.isoparse(item.get('end_time')) if item.get('end_time') else None,
                activity_type=item.get('activity_type'),
                description=item.get('description'),
                location=item.get('location'),
                estimated_cost=item.get('estimated_cost'),
                ai_reasoning=item.get('ai_reasoning'),
                confidence_score=item.get('confidence_score')
            )
            db.add(it)
            
        db.commit()
        db.refresh(new_itinerary)
        return new_itinerary
""")

# 3. Add to routes.py
routes_imports = """
from app.schemas.budget import OptimizeRequest, OptimizeResponse, ApplyScenarioRequest
from app.services.budget_optimizer import BudgetOptimizerService
"""
routes_endpoints = """
@router.post("/trips/{trip_id}/budget/optimize", response_model=OptimizeResponse)
def optimize_budget(trip_id: int, request: OptimizeRequest, db: Session = Depends(get_db)):
    try:
        return BudgetOptimizerService.generate_scenarios(db, trip_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trips/{trip_id}/itinerary/apply-scenario")
def apply_scenario(trip_id: int, request: ApplyScenarioRequest, db: Session = Depends(get_db)):
    try:
        it = BudgetOptimizerService.apply_scenario(db, trip_id, request.dict())
        return {"status": "success", "itinerary_id": it.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
"""
replace_in_file("backend/app/api/routes.py", 
                "from app.schemas.explanation import TripExplanation", 
                "from app.schemas.explanation import TripExplanation\n" + routes_imports)
append_to_file("backend/app/api/routes.py", routes_endpoints)
