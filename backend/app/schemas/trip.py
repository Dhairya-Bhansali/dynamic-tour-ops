from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.enums import TripStatus

class TripBase(BaseModel):
    title: str
    budget: float
    start_date: datetime
    end_date: datetime
    destinations: List[str]

class TripCreate(TripBase):
    traveler_id: int

class TripResponse(TripBase):
    id: int
    status: TripStatus
    class Config:
        from_attributes = True
