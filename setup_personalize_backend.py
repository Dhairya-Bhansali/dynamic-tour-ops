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

# 1. Update Trip model in core_models.py to add preferences
replace_in_file("backend/app/models/core_models.py",
                "budget = Column(Float)",
                "budget = Column(Float)\n    preferences = Column(JSON) # Trip-level personalization data")

# 2. Create schemas/personalize.py
create_file("backend/app/schemas/personalize.py", """
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class TravelDNABase(BaseModel):
    dimensions: Dict[str, int] # e.g. {"Adventure": 8, "Culture": 9, ...}

class TripPreferencesBase(BaseModel):
    destination_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[int] = None
    budget: Optional[float] = None
    currency: Optional[str] = "USD"
    accommodation: Optional[List[str]] = []
    transportation: Optional[List[str]] = []
    interests: Optional[List[str]] = []
    travel_style: Optional[str] = None
    activity_preferences: Optional[List[str]] = []
    selected_experiences: Optional[List[int]] = []

class TravelDNAResponse(BaseModel):
    traveler_id: int
    preferences: Optional[dict] = None

class TripPreferencesResponse(BaseModel):
    trip_id: int
    preferences: Optional[dict] = None
""")

# 3. Create services/personalize_service.py
create_file("backend/app/services/personalize_service.py", """
from sqlalchemy.orm import Session
from app.models.core_models import Traveler, Trip

class PersonalizeService:
    @staticmethod
    def get_travel_dna(db: Session, traveler_id: int):
        traveler = db.query(Traveler).filter(Traveler.id == traveler_id).first()
        return traveler

    @staticmethod
    def update_travel_dna(db: Session, traveler_id: int, dna: dict):
        traveler = db.query(Traveler).filter(Traveler.id == traveler_id).first()
        if traveler:
            traveler.preferences = dna
            db.commit()
            db.refresh(traveler)
        return traveler

    @staticmethod
    def get_trip_preferences(db: Session, trip_id: int):
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        return trip

    @staticmethod
    def update_trip_preferences(db: Session, trip_id: int, prefs: dict):
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if trip:
            trip.preferences = prefs
            db.commit()
            db.refresh(trip)
        return trip
""")

# 4. Update routes.py
routes_imports = """
from app.schemas.personalize import TravelDNABase, TripPreferencesBase, TravelDNAResponse, TripPreferencesResponse
from app.services.personalize_service import PersonalizeService
"""
routes_endpoints = """
@router.get("/travel-dna/{traveler_id}", response_model=TravelDNAResponse)
def get_travel_dna(traveler_id: int, db: Session = Depends(get_db)):
    traveler = PersonalizeService.get_travel_dna(db, traveler_id)
    if not traveler:
        raise HTTPException(status_code=404, detail="Traveler not found")
    return TravelDNAResponse(traveler_id=traveler.id, preferences=traveler.preferences)

@router.put("/travel-dna/{traveler_id}", response_model=TravelDNAResponse)
def update_travel_dna(traveler_id: int, payload: TravelDNABase, db: Session = Depends(get_db)):
    traveler = PersonalizeService.update_travel_dna(db, traveler_id, payload.model_dump()["dimensions"])
    if not traveler:
        raise HTTPException(status_code=404, detail="Traveler not found")
    return TravelDNAResponse(traveler_id=traveler.id, preferences=traveler.preferences)

@router.get("/trips/{trip_id}/preferences", response_model=TripPreferencesResponse)
def get_trip_preferences(trip_id: int, db: Session = Depends(get_db)):
    trip = PersonalizeService.get_trip_preferences(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripPreferencesResponse(trip_id=trip.id, preferences=trip.preferences)

@router.put("/trips/{trip_id}/preferences", response_model=TripPreferencesResponse)
def update_trip_preferences(trip_id: int, payload: TripPreferencesBase, db: Session = Depends(get_db)):
    trip = PersonalizeService.update_trip_preferences(db, trip_id, payload.model_dump())
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripPreferencesResponse(trip_id=trip.id, preferences=trip.preferences)
"""

replace_in_file("backend/app/api/routes.py", 
                "from app.schemas.discovery import DestinationResponse, ExperienceResponse", 
                "from app.schemas.discovery import DestinationResponse, ExperienceResponse\n" + routes_imports)
append_to_file("backend/app/api/routes.py", routes_endpoints)
