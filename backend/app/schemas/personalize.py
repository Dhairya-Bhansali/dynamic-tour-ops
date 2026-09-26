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
