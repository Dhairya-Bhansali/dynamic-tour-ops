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

# 1. Update Database for Trip Coordinator
print("Altering trips table for coordinator...")
conn = sqlite3.connect('backend/tour_ops.db')
c = conn.cursor()
try:
    c.execute("ALTER TABLE trips ADD COLUMN coordinator VARCHAR DEFAULT 'Unassigned'")
    conn.commit()
except Exception as e:
    print("Columns may already exist:", e)
conn.close()

# 2. Update core_models.py for Trip
replace_in_file("backend/app/models/core_models.py",
"""    traveler_id = Column(Integer, ForeignKey("travelers.id"))
    status = Column(Enum(TripStatus), default=TripStatus.DRAFT)
    start_date = Column(DateTime)""",
"""    traveler_id = Column(Integer, ForeignKey("travelers.id"))
    status = Column(String, default="DRAFT")
    coordinator = Column(String, default="Unassigned")
    start_date = Column(DateTime)""")

# 6. Seed Operational Data
print("Seeding operational data...")
def seed_operational_data():
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    from backend.app.models.core_models import Base, Trip, Traveler, Itinerary, ItineraryItem, Booking
    from datetime import datetime, timedelta

    engine = create_engine("sqlite:///backend/tour_ops.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Check if we already seeded operator trips
    if db.query(Trip).filter(Trip.coordinator == "Priya Sharma").first():
        db.close()
        return

    # Add a couple of travelers
    t1 = Traveler(preferences={"Culture": 90, "Food": 80})
    t2 = Traveler(preferences={"Adventure": 85, "Nature": 95})
    db.add(t1)
    db.add(t2)
    db.commit()

    # Add Trips
    now = datetime.utcnow()
    trip1 = Trip(
        traveler_id=t1.id, 
        coordinator="Priya Sharma", 
        status="ACTIVE", 
        start_date=now - timedelta(days=1), 
        end_date=now + timedelta(days=5),
        preferences={"destination": "Kyoto, Japan", "budget": 5000}
    )
    trip2 = Trip(
        traveler_id=t2.id, 
        coordinator="Raj Patel", 
        status="UPCOMING", 
        start_date=now + timedelta(days=10), 
        end_date=now + timedelta(days=17),
        preferences={"destination": "Reykjavik, Iceland", "budget": 8000}
    )
    trip3 = Trip(
        traveler_id=t1.id, 
        coordinator="Priya Sharma", 
        status="ATTENTION_REQUIRED", 
        start_date=now + timedelta(days=2), 
        end_date=now + timedelta(days=7),
        preferences={"destination": "Bali, Indonesia", "budget": 3000}
    )
    db.add_all([trip1, trip2, trip3])
    db.commit()

    # Add Itineraries & Items for Trip 1
    i1 = Itinerary(trip_id=trip1.id, version=1, is_active=True)
    db.add(i1)
    db.commit()
    item1 = ItineraryItem(itinerary_id=i1.id, description="Grand Kyoto Hotel", activity_type="HOTEL", start_time=now, location="Kyoto")
    item2 = ItineraryItem(itinerary_id=i1.id, description="Kyoto Tea Ceremony", activity_type="EXPERIENCE", start_time=now + timedelta(hours=2), location="Gion")
    db.add_all([item1, item2])
    db.commit()
    
    # Add Bookings for Trip 1
    b1 = Booking(trip_id=trip1.id, itinerary_item_id=item1.id, status="CONFIRMED", provider_id="Grand Kyoto Hotel")
    b2 = Booking(trip_id=trip1.id, itinerary_item_id=item2.id, status="PENDING", provider_id="Tea Master Senshi")
    db.add_all([b1, b2])
    db.commit()
    
    # Add Itineraries for Trip 3 (Attention Required - no bookings)
    i3 = Itinerary(trip_id=trip3.id, version=1, is_active=True)
    db.add(i3)
    db.commit()
    item3 = ItineraryItem(itinerary_id=i3.id, description="Ubud Jungle Resort", activity_type="HOTEL", start_time=now+timedelta(days=2))
    db.add(item3)
    db.commit()
    
    db.close()

seed_operational_data()
print("Operational data seeded.")
