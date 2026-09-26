from datetime import datetime, timedelta
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.core_models import User, Traveler, Operator, Vendor, Trip, Itinerary, ItineraryItem, Booking
from app.models.enums import TripStatus, BookingStatus

def seed_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
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
