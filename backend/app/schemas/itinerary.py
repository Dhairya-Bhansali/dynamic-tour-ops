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
