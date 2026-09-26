import os
import sqlite3

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def append_to_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip() + "\n")

def replace_in_file(path, old, new):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if old not in content:
        print(f"Warning: '{old}' not found in {path}")
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# 1. Database Schema Update
print("Altering database for Booking models...")
conn = sqlite3.connect('backend/tour_ops.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    itinerary_item_id INTEGER,
    traveler_id INTEGER,
    provider_id VARCHAR,
    booking_type VARCHAR,
    status VARCHAR DEFAULT 'DRAFT',
    confirmation_code VARCHAR,
    start_datetime DATETIME,
    end_datetime DATETIME,
    location VARCHAR,
    estimated_cost FLOAT,
    currency VARCHAR DEFAULT 'USD',
    provider_reference VARCHAR,
    source_type VARCHAR DEFAULT 'DEMO',
    cancellation_policy VARCHAR,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(trip_id) REFERENCES trips(id),
    FOREIGN KEY(itinerary_item_id) REFERENCES itinerary_items(id),
    FOREIGN KEY(traveler_id) REFERENCES travelers(id)
)
''')
conn.commit()
conn.close()

# 2. Update core_models.py
replace_in_file("backend/app/models/core_models.py", 
"""class ItineraryItem(Base):""",
"""class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    itinerary_item_id = Column(Integer, ForeignKey('itinerary_items.id'))
    traveler_id = Column(Integer, ForeignKey('travelers.id'))
    provider_id = Column(String)
    booking_type = Column(String)
    status = Column(String, default="DRAFT") # DRAFT, PENDING, CONFIRMED, CANCELLED, FAILED
    confirmation_code = Column(String)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    location = Column(String)
    estimated_cost = Column(Float)
    currency = Column(String, default="USD")
    provider_reference = Column(String)
    source_type = Column(String, default="DEMO") # DEMO vs LIVE
    cancellation_policy = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class ItineraryItem(Base):""")

# 3. Create schemas/booking.py
create_file("backend/app/schemas/booking.py", """
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BookableItem(BaseModel):
    itinerary_item_id: int
    activity_type: str
    description: str
    location: str
    estimated_cost: float
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AvailabilityResponse(BaseModel):
    available: bool
    reason: Optional[str] = None
    price: Optional[float] = None
    provider_id: Optional[str] = None

class BookingBase(BaseModel):
    itinerary_item_id: int
    traveler_id: Optional[int] = None
    estimated_cost: float

class BookingResponse(BaseModel):
    id: int
    trip_id: int
    itinerary_item_id: int
    provider_id: Optional[str]
    booking_type: str
    status: str
    confirmation_code: Optional[str]
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]
    location: Optional[str]
    estimated_cost: float
    currency: str
    source_type: str

class PreparationTask(BaseModel):
    id: str
    title: str
    status: str # PENDING, DONE
    type: str # BOOKING, ACTION, SYSTEM
    
class TripReadiness(BaseModel):
    booking_completion: int # 0-100
    required_confirmations: str # e.g. "4 / 5"
    preparation: str # e.g. "3 / 6"
    status: str # READY or ACTION REQUIRED
    tasks: List[PreparationTask]
""")

# 4. Create providers/booking_provider.py
create_file("backend/app/services/booking_provider.py", """
from abc import ABC, abstractmethod
import random
import uuid

class BookingProvider(ABC):
    @abstractmethod
    def check_availability(self, item) -> dict:
        pass
        
    @abstractmethod
    def create_booking(self, item) -> dict:
        pass

class DemoBookingProvider(BookingProvider):
    def check_availability(self, item) -> dict:
        # Simulate availability check logic based on item type or cost
        is_available = random.choice([True, True, True, False]) # 75% chance available in demo
        if not is_available:
            return {
                "available": False,
                "reason": f"Selected {item.activity_type} is fully booked on these dates.",
                "price": item.estimated_cost,
                "provider_id": "DEMO_PROVIDER"
            }
        return {
            "available": True,
            "reason": None,
            "price": item.estimated_cost,
            "provider_id": "DEMO_PROVIDER"
        }
        
    def create_booking(self, item) -> dict:
        code = f"DEMO-{uuid.uuid4().hex[:6].upper()}"
        return {
            "status": "CONFIRMED",
            "confirmation_code": code,
            "provider_reference": f"REF-{code}",
            "source_type": "DEMO"
        }
""")

# 5. Create services/booking_service.py
create_file("backend/app/services/booking_service.py", """
from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, ItineraryItem, Booking
from app.schemas.booking import BookableItem, AvailabilityResponse, BookingResponse, TripReadiness, PreparationTask
from app.services.booking_provider import DemoBookingProvider

class BookingService:
    def __init__(self):
        self.provider = DemoBookingProvider()

    def get_bookable_items(self, db: Session, trip_id: int):
        itinerary = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
        if not itinerary:
            return []
        items = db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == itinerary.id).all()
        # Filter for bookable things (assuming everything but 'LEISURE' is bookable for this demo)
        return [i for i in items if i.activity_type != 'LEISURE']

    def check_availability(self, db: Session, trip_id: int, item_id: int) -> AvailabilityResponse:
        item = db.query(ItineraryItem).filter(ItineraryItem.id == item_id).first()
        if not item:
            raise Exception("Item not found")
        res = self.provider.check_availability(item)
        return AvailabilityResponse(**res)
        
    def create_booking(self, db: Session, trip_id: int, item_id: int):
        item = db.query(ItineraryItem).filter(ItineraryItem.id == item_id).first()
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not item or not trip:
            raise Exception("Item or Trip not found")
            
        # Check if already booked
        existing = db.query(Booking).filter(Booking.itinerary_item_id == item_id, Booking.status == 'CONFIRMED').first()
        if existing:
            raise Exception("Item already booked")

        # Execute Provider Abstraction
        res = self.provider.create_booking(item)
        
        booking = Booking(
            trip_id=trip_id,
            itinerary_item_id=item_id,
            traveler_id=trip.traveler_id,
            provider_id="DEMO_PROVIDER",
            booking_type=item.activity_type,
            status=res["status"],
            confirmation_code=res["confirmation_code"],
            start_datetime=item.start_time,
            end_datetime=item.end_time,
            location=item.location,
            estimated_cost=item.estimated_cost,
            source_type=res["source_type"],
            provider_reference=res["provider_reference"]
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    def get_bookings(self, db: Session, trip_id: int):
        return db.query(Booking).filter(Booking.trip_id == trip_id).all()
        
    def get_preparation_readiness(self, db: Session, trip_id: int) -> TripReadiness:
        bookable_items = self.get_bookable_items(db, trip_id)
        bookings = self.get_bookings(db, trip_id)
        
        total_req = len(bookable_items)
        confirmed = len([b for b in bookings if b.status == 'CONFIRMED'])
        
        tasks = []
        for b_item in bookable_items:
            b_match = next((x for x in bookings if x.itinerary_item_id == b_item.id), None)
            tasks.append(PreparationTask(
                id=f"book_{b_item.id}",
                title=f"Book: {b_item.description}",
                status="DONE" if b_match and b_match.status == 'CONFIRMED' else "PENDING",
                type="BOOKING"
            ))
            
        tasks.append(PreparationTask(id="sys_1", title="Check travel documents (Visa/Passport)", status="PENDING", type="ACTION"))
        tasks.append(PreparationTask(id="sys_2", title="Review packing suggestions", status="PENDING", type="ACTION"))
        
        prep_total = len(tasks)
        prep_done = len([t for t in tasks if t.status == 'DONE'])
        
        completion_pct = int((confirmed / total_req) * 100) if total_req > 0 else 100
        
        return TripReadiness(
            booking_completion=completion_pct,
            required_confirmations=f"{confirmed} / {total_req}",
            preparation=f"{prep_done} / {prep_total}",
            status="READY" if completion_pct == 100 else "ACTION REQUIRED",
            tasks=tasks
        )
""")

# 6. Add to routes.py
routes_imports = """
from app.schemas.booking import BookableItem, AvailabilityResponse, BookingResponse, TripReadiness, BookingBase
from app.services.booking_service import BookingService
booking_service = BookingService()
"""
routes_endpoints = """
@router.get("/trips/{trip_id}/bookable-items", response_model=List[BookableItem])
def get_bookable_items(trip_id: int, db: Session = Depends(get_db)):
    return booking_service.get_bookable_items(db, trip_id)

@router.post("/trips/{trip_id}/bookings/check-availability", response_model=AvailabilityResponse)
def check_availability(trip_id: int, request: BookingBase, db: Session = Depends(get_db)):
    return booking_service.check_availability(db, trip_id, request.itinerary_item_id)

@router.post("/trips/{trip_id}/bookings", response_model=BookingResponse)
def create_booking(trip_id: int, request: BookingBase, db: Session = Depends(get_db)):
    try:
        return booking_service.create_booking(db, trip_id, request.itinerary_item_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trips/{trip_id}/bookings", response_model=List[BookingResponse])
def get_bookings(trip_id: int, db: Session = Depends(get_db)):
    return booking_service.get_bookings(db, trip_id)

@router.get("/trips/{trip_id}/preparation", response_model=TripReadiness)
def get_preparation(trip_id: int, db: Session = Depends(get_db)):
    return booking_service.get_preparation_readiness(db, trip_id)
"""

replace_in_file("backend/app/api/routes.py", 
                "from app.schemas.budget import OptimizeRequest", 
                "from app.schemas.budget import OptimizeRequest\n" + routes_imports)
append_to_file("backend/app/api/routes.py", routes_endpoints)
