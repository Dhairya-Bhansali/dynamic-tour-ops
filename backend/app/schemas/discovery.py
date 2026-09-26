from pydantic import BaseModel
from typing import List, Optional, Any

class DestinationBase(BaseModel):
    name: str
    country: str
    hero_image: str
    description: str
    budget: float
    recommended_duration: int
    travel_styles: List[str]
    coordinates: Any
    is_featured: bool
    is_trending: bool

class DestinationResponse(DestinationBase):
    id: int
    class Config:
        from_attributes = True

class ExperienceBase(BaseModel):
    destination_id: int
    name: str
    image: str
    location: str
    duration: int
    price_estimate: float
    category: str
    travel_styles: List[str]
    availability_status: str
    description: str

class ExperienceResponse(ExperienceBase):
    id: int
    class Config:
        from_attributes = True
