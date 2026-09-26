from sqlalchemy.orm import Session
from app.models.core_models import Trip, Traveler
from app.schemas.trip import TripCreate
from app.models.enums import TripStatus

class TripService:
    @staticmethod
    def create_trip(db: Session, trip_in: TripCreate):
        # AI Deterministic Validation logic hook would go here
        db_trip = Trip(
            title=trip_in.title,
            traveler_id=trip_in.traveler_id,
            budget=trip_in.budget,
            start_date=trip_in.start_date,
            end_date=trip_in.end_date,
            destinations=trip_in.destinations,
            status=TripStatus.DRAFT
        )
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        return db_trip
        
    @staticmethod
    def get_trip(db: Session, trip_id: int):
        return db.query(Trip).filter(Trip.id == trip_id).first()
        
    @staticmethod
    def get_all_trips(db: Session):
        return db.query(Trip).all()
