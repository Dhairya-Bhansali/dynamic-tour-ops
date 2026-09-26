from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.discovery import DestinationResponse, ExperienceResponse

from app.schemas.personalize import TravelDNABase, TripPreferencesBase, TravelDNAResponse, TripPreferencesResponse
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
