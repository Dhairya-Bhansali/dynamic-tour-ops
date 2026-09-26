from sqlalchemy.orm import Session
from app.models.core_models import Traveler, Trip

class PersonalizeService:
    @staticmethod
    def get_travel_dna(db: Session, traveler_id: int):
        traveler = db.query(Traveler).filter(Traveler.id == traveler_id).first()
        return traveler

    @staticmethod
    def update_travel_dna(db: Session, traveler_id: int, dna: dict):
        traveler = db.query(Traveler).filter(Traveler.id == traveler_id).first()
        if traveler:
            traveler.preferences = dna
            db.commit()
            db.refresh(traveler)
        return traveler

    @staticmethod
    def get_trip_preferences(db: Session, trip_id: int):
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        return trip

    @staticmethod
    def update_trip_preferences(db: Session, trip_id: int, prefs: dict):
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if trip:
            trip.preferences = prefs
            db.commit()
            db.refresh(trip)
        return trip
