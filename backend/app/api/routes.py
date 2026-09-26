from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.discovery import DestinationResponse, ExperienceResponse

from app.schemas.personalize import TravelDNABase

from app.schemas.itinerary import ItineraryResponse, ValidationResult

from app.schemas.explanation import TripExplanation

from app.schemas.budget import OptimizeRequest, OptimizeResponse, ApplyScenarioRequest
from app.services.budget_optimizer import BudgetOptimizerService

from app.services.explanation_service import ExplanationService

from app.services.itinerary_planner import ItineraryPlanner
from app.schemas.personalize import TripPreferencesBase, TravelDNAResponse, TripPreferencesResponse
from app.services.personalize_service import PersonalizeService

from app.services.discovery_service import DiscoveryService
from typing import List, Optional

from app.db.session import get_db
from app.schemas.trip import TripCreate, TripResponse
from app.services.trip_service import TripService

router = APIRouter()

@router.post("/trips", response_model=TripResponse)
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    return TripService.create_trip(db, trip)

@router.get("/trips", response_model=List[TripResponse])
def get_trips(db: Session = Depends(get_db)):
    return TripService.get_all_trips(db)

@router.get("/trips/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = TripService.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.get("/destinations", response_model=List[DestinationResponse])
def get_destinations(
    search: Optional[str] = None, 
    style: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    return DiscoveryService.get_destinations(db, search=search, style=style)

@router.get("/destinations/{dest_id}", response_model=DestinationResponse)
def get_destination(dest_id: int, db: Session = Depends(get_db)):
    dest = DiscoveryService.get_destination(db, dest_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return dest

@router.get("/experiences", response_model=List[ExperienceResponse])
def get_experiences(
    category: Optional[str] = None,
    dest_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return DiscoveryService.get_experiences(db, category=category, dest_id=dest_id, search=search)

@router.get("/experiences/{exp_id}", response_model=ExperienceResponse)
def get_experience(exp_id: int, db: Session = Depends(get_db)):
    exp = DiscoveryService.get_experience(db, exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp

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

@router.get("/trips/{trip_id}/itinerary/explanation", response_model=TripExplanation)
def get_itinerary_explanation(trip_id: int, db: Session = Depends(get_db)):
    try:
        return ExplanationService.get_trip_explanation(db, trip_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trips/{trip_id}/budget/optimize", response_model=OptimizeResponse)
def optimize_budget(trip_id: int, request: OptimizeRequest, db: Session = Depends(get_db)):
    try:
        return BudgetOptimizerService.generate_scenarios(db, trip_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trips/{trip_id}/itinerary/apply-scenario")
def apply_scenario(trip_id: int, request: ApplyScenarioRequest, db: Session = Depends(get_db)):
    try:
        it = BudgetOptimizerService.apply_scenario(db, trip_id, request.dict())
        return {"status": "success", "itinerary_id": it.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
