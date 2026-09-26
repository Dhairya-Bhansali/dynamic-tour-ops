from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Alert(BaseModel):
    id: str
    severity: str # WARNING, CRITICAL
    trip_id: int
    traveler_name: str
    affected_item: str
    reason: str
    timestamp: datetime
    recommended_action: str

class OperatorDashboardMetrics(BaseModel):
    active_tours: int
    upcoming_tours: int
    total_travelers: int
    confirmed_bookings: int
    attention_required: int

class TourSummary(BaseModel):
    trip_id: int
    traveler_name: str
    destination: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    status: str
    booking_completion: str
    coordinator: str
    attention_state: bool
    next_scheduled_activity: Optional[str]

class VendorItem(BaseModel):
    id: int
    service_type: str
    name: str
    status: str
    scheduled_time: Optional[datetime]
    location: str
    cost: float

class TourDetail(BaseModel):
    trip_id: int
    traveler_name: str
    destination: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget: float
    current_itinerary_version: int
    booking_completion: str
    readiness: str
    coordinator: str
    timeline: List[dict]
    vendors: List[VendorItem]
