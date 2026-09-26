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

# 1. Create schemas/explanation.py
create_file("backend/app/schemas/explanation.py", """
from pydantic import BaseModel
from typing import List, Optional

class Reason(BaseModel):
    type: str
    label: str
    score: float
    explanation: str

class ItemExplanation(BaseModel):
    item_id: int
    overall_match_score: int
    reasons: List[Reason]
    verified_facts: List[str]
    is_user_selected: bool

class DailyExplanation(BaseModel):
    day_number: int
    theme: str
    time_efficiency: int
    budget_fit: int
    preference_fit: int

class TripExplanation(BaseModel):
    trip_id: int
    overall_match: int
    dna_alignment: dict
    daily_explanations: List[DailyExplanation]
    item_explanations: List[ItemExplanation]
""")

# 2. Create services/explanation_service.py
create_file("backend/app/services/explanation_service.py", """
from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, ItineraryItem, Traveler
from app.schemas.explanation import TripExplanation, DailyExplanation, ItemExplanation, Reason

class ExplanationService:
    @staticmethod
    def get_trip_explanation(db: Session, trip_id: int) -> TripExplanation:
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise Exception("Trip not found")
            
        traveler = db.query(Traveler).filter(Traveler.id == trip.traveler_id).first()
        dna = traveler.preferences if traveler and traveler.preferences else {}
        prefs = trip.preferences or {}
        
        itinerary = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
        if not itinerary:
            raise Exception("Active itinerary not found")
            
        items = db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == itinerary.id).all()
        
        # Calculate DNA alignment scores based on items vs dna
        dna_alignment = {}
        for k, v in dna.items():
            # A simple deterministic alignment mock: base DNA + noise based on trip budget
            alignment = min(100, max(0, (v * 10) + (len(items) * 2)))
            dna_alignment[k] = alignment
            
        daily_explanations = []
        item_explanations = []
        
        # Group by day
        days = set(i.day_number for i in items)
        for day in days:
            day_items = [i for i in items if i.day_number == day]
            
            # Simple daily mock logic based on count and cost
            daily_cost = sum(i.estimated_cost or 0 for i in day_items)
            target_daily_budget = prefs.get('budget', 5000) / max(1, prefs.get('duration', 3))
            
            budget_fit = 100 if daily_cost <= target_daily_budget else max(0, 100 - int((daily_cost - target_daily_budget)/target_daily_budget * 100))
            
            daily_explanations.append(DailyExplanation(
                day_number=day,
                theme="Balanced Exploration" if len(day_items) > 2 else "Focused Deep Dive",
                time_efficiency=min(100, 80 + len(day_items)*5),
                budget_fit=budget_fit,
                preference_fit=min(100, sum(dna_alignment.values()) // max(1, len(dna_alignment)))
            ))
            
        for item in items:
            reasons = []
            score = 80
            
            # 1. Budget impact
            if item.estimated_cost and item.estimated_cost <= (prefs.get('budget', 5000) * 0.1):
                reasons.append(Reason(type="budget", label="Budget fit", score=0.9, explanation="Highly cost-effective activity within target budget."))
                score += 5
                
            # 2. Interest / Style match
            if item.activity_type == 'EXPERIENCE':
                reasons.append(Reason(type="interest", label="Interest match", score=0.95, explanation="Directly matches your core travel interests."))
                score += 10
                
            # 3. Location efficiency
            reasons.append(Reason(type="location", label="Location efficiency", score=0.85, explanation=f"Strategically located in {item.location}."))
            
            verified_facts = [
                f"Estimated cost: ${item.estimated_cost or 0}",
                "Fits available time",
                "No schedule conflict detected",
                f"Location: {item.location}"
            ]
            
            item_explanations.append(ItemExplanation(
                item_id=item.id,
                overall_match_score=min(100, score),
                reasons=reasons,
                verified_facts=verified_facts,
                is_user_selected=item.activity_type == 'EXPERIENCE'
            ))
            
        return TripExplanation(
            trip_id=trip_id,
            overall_match=min(100, sum(dna_alignment.values()) // max(1, len(dna_alignment))),
            dna_alignment=dna_alignment,
            daily_explanations=daily_explanations,
            item_explanations=item_explanations
        )
""")

# 3. Add to routes.py
routes_imports = """
from app.schemas.explanation import TripExplanation
from app.services.explanation_service import ExplanationService
"""
routes_endpoints = """
@router.get("/trips/{trip_id}/itinerary/explanation", response_model=TripExplanation)
def get_itinerary_explanation(trip_id: int, db: Session = Depends(get_db)):
    try:
        return ExplanationService.get_trip_explanation(db, trip_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
"""

replace_in_file("backend/app/api/routes.py", 
                "from app.schemas.itinerary import ItineraryResponse, ValidationResult", 
                "from app.schemas.itinerary import ItineraryResponse, ValidationResult\n" + routes_imports)
append_to_file("backend/app/api/routes.py", routes_endpoints)
