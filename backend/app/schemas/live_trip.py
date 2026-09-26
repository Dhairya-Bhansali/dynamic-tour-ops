from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class TimelineEvent(BaseModel):
    id: int
    time_label: str # NOW, NEXT, LATER
    time: Optional[datetime]
    title: str
    location: str
    status: str

class NextAction(BaseModel):
    title: str
    description: str
    action_type: str

class LiveAlert(BaseModel):
    id: str
    severity: str
    message: str

class LiveTripStatus(BaseModel):
    trip_id: int
    status_label: str
    day_label: str
    timeline: List[TimelineEvent]
    next_action: Optional[NextAction]
    alerts: List[LiveAlert]
    bookings_summary: str
    prep_summary: str

class AssistantRequest(BaseModel):
    message: str

class AssistantResponse(BaseModel):
    response: str
    intent_detected: str
    data_used: Dict[str, Any]
