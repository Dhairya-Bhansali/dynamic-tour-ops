from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
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
