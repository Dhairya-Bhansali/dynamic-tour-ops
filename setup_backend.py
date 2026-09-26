import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# core/config.py
create_file("backend/app/core/config.py", """
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "NexTour API"
    # Use SQLite for demo purposes to avoid requiring a running Postgres server during review,
    # but the architecture supports Postgres (just change this URL).
    DATABASE_URL: str = "sqlite:///./tour_ops.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        case_sensitive = True

settings = Settings()
""")

# db/session.py
create_file("backend/app/db/session.py", """
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configure engine for SQLite (fallback) or Postgres
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

# db/base.py
create_file("backend/app/db/base.py", """
from sqlalchemy.orm import declarative_base
Base = declarative_base()
""")

# models/enums.py
create_file("backend/app/models/enums.py", """
import enum

class TripStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PLANNING = "PLANNING"
    READY = "READY"
    BOOKED = "BOOKED"
    PREPARING = "PREPARING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    MODIFIED = "MODIFIED"

class DisruptionStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    ANALYZING = "ANALYZING"
    ALTERNATIVES_READY = "ALTERNATIVES_READY"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    RESOLVED = "RESOLVED"
""")

# models/core_models.py (combining them for simplicity)
create_file("backend/app/models/core_models.py", """
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.enums import TripStatus, BookingStatus, DisruptionStatus

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String) # TRAVELER or OPERATOR

class Traveler(Base):
    __tablename__ = "travelers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preferences = Column(JSON) # Travel DNA
    user = relationship("User")
    trips = relationship("Trip", back_populates="traveler")

class Operator(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String)
    user = relationship("User")

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String) # HOTEL, TRANSPORT, ACTIVITY

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    traveler_id = Column(Integer, ForeignKey("travelers.id"))
    status = Column(Enum(TripStatus), default=TripStatus.DRAFT)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    destinations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    traveler = relationship("Traveler", back_populates="trips")
    itineraries = relationship("Itinerary", back_populates="trip")
    bookings = relationship("Booking", back_populates="trip")
    disruptions = relationship("Disruption", back_populates="trip")

class Itinerary(Base):
    __tablename__ = "itineraries"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    trip = relationship("Trip", back_populates="itineraries")
    items = relationship("ItineraryItem", back_populates="itinerary")

class ItineraryItem(Base):
    __tablename__ = "itinerary_items"
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"))
    day_number = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    activity_type = Column(String)
    description = Column(String)
    location = Column(String)
    
    itinerary = relationship("Itinerary", back_populates="items")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    type = Column(String) # HOTEL, TRANSPORT, ACTIVITY
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    cost = Column(Float)
    confirmation_code = Column(String)
    
    trip = relationship("Trip", back_populates="bookings")
    vendor = relationship("Vendor")

class Disruption(Base):
    __tablename__ = "disruptions"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    description = Column(String)
    status = Column(Enum(DisruptionStatus), default=DisruptionStatus.DETECTED)
    impact_radius = Column(JSON)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    trip = relationship("Trip", back_populates="disruptions")
    alternatives = relationship("AlternativePlan", back_populates="disruption")

class AlternativePlan(Base):
    __tablename__ = "alternative_plans"
    id = Column(Integer, primary_key=True, index=True)
    disruption_id = Column(Integer, ForeignKey("disruptions.id"))
    confidence_score = Column(Float)
    changes = Column(JSON)
    is_approved = Column(Boolean, default=False)
    
    disruption = relationship("Disruption", back_populates="alternatives")
""")

# schemas/trip.py
create_file("backend/app/schemas/trip.py", """
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.enums import TripStatus

class TripBase(BaseModel):
    title: str
    budget: float
    start_date: datetime
    end_date: datetime
    destinations: List[str]

class TripCreate(TripBase):
    traveler_id: int

class TripResponse(TripBase):
    id: int
    status: TripStatus
    class Config:
        from_attributes = True
""")

# services/trip_service.py
create_file("backend/app/services/trip_service.py", """
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
""")

# api/routes.py
create_file("backend/app/api/routes.py", """
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
""")

# main.py
create_file("backend/app/main.py", """
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.db.session import engine
from app.db.base import Base
# Import all models to ensure they are registered with Base
from app.models import core_models

# Create tables for demo
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NexTour API", description="Dynamic Tour Operations Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
""")

# seed.py
create_file("backend/seed.py", """
from datetime import datetime, timedelta
from app.db.session import SessionLocal
from app.models.core_models import User, Traveler, Operator, Vendor, Trip, Itinerary, ItineraryItem, Booking
from app.models.enums import TripStatus, BookingStatus

def seed_db():
    db = SessionLocal()
    
    # 1. Clear existing data (optional, but good for idempotent seeds)
    # Since we're using SQLite for demo, it just inserts. To keep it simple, we won't delete if we assume empty DB.
    if db.query(User).first():
        print("Database already seeded!")
        return

    # 2. Create Users
    u1 = User(email="traveler1@example.com", full_name="Alice Smith", role="TRAVELER")
    u2 = User(email="operator1@example.com", full_name="Bob Operator", role="OPERATOR")
    db.add_all([u1, u2])
    db.commit()

    # 3. Create Profiles
    t1 = Traveler(user_id=u1.id, preferences={"vibe": "Adventure", "budget_level": "Premium"})
    o1 = Operator(user_id=u2.id, department="Disruption Management")
    db.add_all([t1, o1])
    db.commit()

    # 4. Create Vendors
    v1 = Vendor(name="Grand Tokyo Hotel", type="HOTEL")
    v2 = Vendor(name="Japan Airlines", type="TRANSPORT")
    db.add_all([v1, v2])
    db.commit()

    # 5. Create a Trip
    trip1 = Trip(
        title="Tokyo Adventure",
        traveler_id=t1.id,
        status=TripStatus.BOOKED,
        start_date=datetime.utcnow() + timedelta(days=10),
        end_date=datetime.utcnow() + timedelta(days=17),
        budget=4500.0,
        destinations=["Tokyo, Japan"]
    )
    db.add(trip1)
    db.commit()

    # 6. Create Itinerary
    itin = Itinerary(trip_id=trip1.id, version=1, is_active=True)
    db.add(itin)
    db.commit()

    # 7. Create Itinerary Items
    i1 = ItineraryItem(
        itinerary_id=itin.id,
        day_number=1,
        start_time=trip1.start_date,
        end_time=trip1.start_date + timedelta(hours=3),
        activity_type="FLIGHT",
        description="JAL Flight 123",
        location="JFK to NRT"
    )
    db.add(i1)

    # 8. Create Bookings
    b1 = Booking(
        trip_id=trip1.id,
        vendor_id=v1.id,
        type="HOTEL",
        status=BookingStatus.CONFIRMED,
        cost=1200.0,
        confirmation_code="HTL-98765"
    )
    db.add(b1)
    db.commit()

    print("Seed data injected successfully!")

if __name__ == "__main__":
    seed_db()
""")
