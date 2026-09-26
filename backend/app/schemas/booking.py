from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BookableItem(BaseModel):
    itinerary_item_id: int
    activity_type: str
    description: str
    location: str
    estimated_cost: float
    currency: str = "INR"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AvailabilityResponse(BaseModel):
    available: bool
    reason: Optional[str] = None
    price: Optional[float] = None
    provider_id: Optional[str] = None

class BookingBase(BaseModel):
    itinerary_item_id: int
    traveler_id: Optional[int] = None
    estimated_cost: float

class BookingResponse(BaseModel):
    id: int
    trip_id: int
    # Legacy migrated bookings may have NULL itinerary_item_id (pre-schema rows)
    itinerary_item_id: Optional[int] = None
    provider_id: Optional[str] = None
    # Legacy migrated bookings map the old 'type' column to booking_type
    booking_type: Optional[str] = None
    status: str
    confirmation_code: Optional[str] = None
    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    # Legacy migrated bookings map the old 'cost' column to estimated_cost
    estimated_cost: Optional[float] = None
    currency: Optional[str] = None
    source_type: Optional[str] = None

    model_config = {"from_attributes": True}

class PreparationTask(BaseModel):
    id: str
    title: str
    status: str # PENDING, DONE
    type: str # BOOKING, ACTION, SYSTEM
    
class TripReadiness(BaseModel):
    booking_completion: int # 0-100
    required_confirmations: str # e.g. "4 / 5"
    preparation: str # e.g. "3 / 6"
    status: str # READY or ACTION REQUIRED
    tasks: List[PreparationTask]
