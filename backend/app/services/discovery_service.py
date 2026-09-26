from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.core_models import Destination, Experience

class DiscoveryService:
    @staticmethod
    def get_destinations(db: Session, search: str = None, style: str = None):
        query = db.query(Destination)
        if search:
            query = query.filter(
                or_(
                    Destination.name.ilike(f"%{search}%"),
                    Destination.country.ilike(f"%{search}%")
                )
            )
        if style:
            # Simple fallback search within JSON text
            query = query.filter(Destination.travel_styles.cast(str).ilike(f"%{style}%"))
        return query.all()

    @staticmethod
    def get_destination(db: Session, dest_id: int):
        return db.query(Destination).filter(Destination.id == dest_id).first()

    @staticmethod
    def get_experiences(db: Session, category: str = None, dest_id: int = None, search: str = None):
        query = db.query(Experience)
        if search:
            query = query.filter(Experience.name.ilike(f"%{search}%"))
        if category:
            query = query.filter(Experience.category == category)
        if dest_id:
            query = query.filter(Experience.destination_id == dest_id)
        return query.all()

    @staticmethod
    def get_experience(db: Session, exp_id: int):
        return db.query(Experience).filter(Experience.id == exp_id).first()
