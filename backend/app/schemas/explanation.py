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
