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
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# 1. Update Itinerary Item model to support reasoning, cost, priority
replace_in_file("backend/app/models/core_models.py",
                "location = Column(String)",
                "location = Column(String)\n    estimated_cost = Column(Float)\n    ai_reasoning = Column(String)\n    confidence_score = Column(Float)\n    day_date = Column(DateTime)")

# 2. Create schemas/itinerary.py
create_file("backend/app/schemas/itinerary.py", """
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ItineraryItemBase(BaseModel):
    day_number: int
    day_date: Optional[datetime] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    activity_type: str
    description: str
    location: str
    estimated_cost: float
    ai_reasoning: Optional[str] = None
    confidence_score: Optional[float] = None

class ItineraryItemResponse(ItineraryItemBase):
    id: int
    itinerary_id: int
    class Config:
        from_attributes = True

class ItineraryBase(BaseModel):
    trip_id: int
    version: int
    is_active: bool

class ItineraryResponse(ItineraryBase):
    id: int
    items: List[ItineraryItemResponse] = []
    class Config:
        from_attributes = True

class ValidationResult(BaseModel):
    valid: bool
    warnings: List[str] = []
    errors: List[str] = []
""")

# 3. Create services/itinerary_validator.py
create_file("backend/app/services/itinerary_validator.py", """
from typing import List

class ItineraryValidator:
    @staticmethod
    def validate_plan(items: List[dict], trip_budget: float) -> dict:
        errors = []
        warnings = []
        
        # 1. Budget check
        total_cost = sum(item.get('estimated_cost', 0) for item in items)
        if total_cost > trip_budget * 1.2:
            errors.append(f"Itinerary cost (${total_cost}) significantly exceeds budget (${trip_budget}).")
        elif total_cost > trip_budget:
            warnings.append(f"Itinerary cost (${total_cost}) slightly exceeds budget (${trip_budget}).")
            
        # 2. Time conflict check (basic)
        # Assuming items are sorted by start_time
        for i in range(len(items) - 1):
            if items[i].get('end_time') and items[i+1].get('start_time'):
                if items[i]['end_time'] > items[i+1]['start_time']:
                    errors.append(f"Time conflict detected between '{items[i]['description']}' and '{items[i+1]['description']}'.")
                    
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
""")

# 4. Create services/itinerary_planner.py
create_file("backend/app/services/itinerary_planner.py", """
from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, ItineraryItem, Experience, Destination
from app.services.itinerary_validator import ItineraryValidator
from datetime import datetime, timedelta
import random

class ItineraryPlanner:
    @staticmethod
    def generate_itinerary(db: Session, trip_id: int):
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise Exception("Trip not found")
        
        prefs = trip.preferences or {}
        duration = prefs.get("duration", 3)
        budget = prefs.get("budget", 5000)
        selected_exp_ids = prefs.get("selected_experiences", [])
        
        # Determine existing version
        existing_versions = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).count()
        new_version_num = existing_versions + 1
        
        new_itinerary = Itinerary(trip_id=trip_id, version=new_version_num, is_active=True)
        db.add(new_itinerary)
        db.flush()
        
        # Deactivate old versions
        db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.id != new_itinerary.id).update({"is_active": False})
        
        start_date = datetime.strptime(prefs.get("start_date", datetime.utcnow().strftime("%Y-%m-%d")), "%Y-%m-%d")
        
        # Deterministic Fallback logic: schedule selected experiences
        experiences = db.query(Experience).filter(Experience.id.in_(selected_exp_ids)).all() if selected_exp_ids else []
        
        items_payload = []
        current_exp_idx = 0
        
        for day in range(1, duration + 1):
            current_date = start_date + timedelta(days=day-1)
            
            # Morning Activity
            items_payload.append({
                "day_number": day,
                "day_date": current_date,
                "start_time": current_date + timedelta(hours=9),
                "end_time": current_date + timedelta(hours=11),
                "activity_type": "BREAKFAST",
                "description": "Local breakfast near hotel",
                "location": "City Center",
                "estimated_cost": 25.0,
                "ai_reasoning": "Fits your 'Relaxed' pace and 'Food' interest.",
                "confidence_score": 0.95
            })
            
            # Main Activity (Experiences)
            if current_exp_idx < len(experiences):
                exp = experiences[current_exp_idx]
                items_payload.append({
                    "day_number": day,
                    "day_date": current_date,
                    "start_time": current_date + timedelta(hours=12),
                    "end_time": current_date + timedelta(hours=12 + exp.duration),
                    "activity_type": "EXPERIENCE",
                    "description": exp.name,
                    "location": exp.location,
                    "estimated_cost": exp.price_estimate,
                    "ai_reasoning": f"You explicitly selected this experience. Fits category '{exp.category}'.",
                    "confidence_score": 1.0
                })
                current_exp_idx += 1
            else:
                items_payload.append({
                    "day_number": day,
                    "day_date": current_date,
                    "start_time": current_date + timedelta(hours=14),
                    "end_time": current_date + timedelta(hours=17),
                    "activity_type": "EXPLORATION",
                    "description": "Guided walking tour and sightseeing",
                    "location": "Historic District",
                    "estimated_cost": 50.0,
                    "ai_reasoning": "Highly rated cultural exploration based on your DNA.",
                    "confidence_score": 0.88
                })
                
        # Validate deterministic plan
        validation_res = ItineraryValidator.validate_plan(items_payload, budget)
        
        # Save to DB
        db_items = []
        for item in items_payload:
            it = ItineraryItem(
                itinerary_id=new_itinerary.id,
                **item
            )
            db.add(it)
            db_items.append(it)
            
        db.commit()
        db.refresh(new_itinerary)
        
        return new_itinerary, validation_res
""")

# 5. Update routes.py
routes_imports = """
from app.schemas.itinerary import ItineraryResponse, ValidationResult
from app.services.itinerary_planner import ItineraryPlanner
"""
routes_endpoints = """
@router.post("/trips/{trip_id}/itinerary/generate")
def generate_itinerary(trip_id: int, db: Session = Depends(get_db)):
    try:
        itinerary, validation = ItineraryPlanner.generate_itinerary(db, trip_id)
        return {
            "itinerary": ItineraryResponse.from_orm(itinerary),
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trips/{trip_id}/itinerary", response_model=ItineraryResponse)
def get_active_itinerary(trip_id: int, db: Session = Depends(get_db)):
    itinerary = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Active itinerary not found")
    return itinerary

@router.get("/trips/{trip_id}/itinerary/versions", response_model=List[ItineraryResponse])
def get_itinerary_versions(trip_id: int, db: Session = Depends(get_db)):
    itineraries = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).order_by(Itinerary.version.desc()).all()
    return itineraries
"""

replace_in_file("backend/app/api/routes.py", 
                "from app.schemas.personalize import TravelDNABase", 
                "from app.schemas.personalize import TravelDNABase\n" + routes_imports)
append_to_file("backend/app/api/routes.py", routes_endpoints)
