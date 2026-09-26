import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.api.endpoints.demo import reset_demo_data
from app.db.session import get_db

def init():
    engine = create_engine("sqlite:///tour_ops.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    from app.db.base import Base
    from app.models.core_models import Trip, Itinerary, ItineraryItem, User
    from app.models.ingestion_models import FlightOffer, HotelOffer

    Base.metadata.create_all(bind=engine)
    print("Demo DB reset (schema initialized).")

if __name__ == "__main__":
    init()
