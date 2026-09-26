from datetime import datetime, timedelta
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.core_models import User, Traveler, Operator, Vendor, Trip, Itinerary, ItineraryItem, Booking, Destination, Experience
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

    
    # Discovery Data
    if not db.query(Destination).first():
        d1 = Destination(
            name="Kyoto", country="Japan",
            hero_image="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=2070&auto=format&fit=crop",
            description="Experience the tranquil beauty of ancient temples, traditional tea houses, and sublime gardens.",
            budget=2500, recommended_duration=5, travel_styles=["Culture", "Spiritual", "Relaxation"],
            coordinates={"lat": 35.0116, "lng": 135.7681}, is_featured=True, is_trending=True
        )
        d2 = Destination(
            name="Santorini", country="Greece",
            hero_image="https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?q=80&w=1935&auto=format&fit=crop",
            description="Famous for its stunning sunsets, white-washed buildings, and crystal-clear Aegean waters.",
            budget=3500, recommended_duration=7, travel_styles=["Romantic", "Luxury", "Relaxation"],
            coordinates={"lat": 36.3932, "lng": 25.4615}, is_featured=True, is_trending=False
        )
        d3 = Destination(
            name="Patagonia", country="Chile",
            hero_image="https://images.unsplash.com/photo-1578637387939-43c525550085?q=80&w=2070&auto=format&fit=crop",
            description="A dramatic landscape of jagged peaks, immense glaciers, and pristine lakes at the edge of the world.",
            budget=4000, recommended_duration=10, travel_styles=["Adventure", "Nature"],
            coordinates={"lat": -51.7236, "lng": -72.5087}, is_featured=False, is_trending=True
        )
        d4 = Destination(
            name="Bali", country="Indonesia",
            hero_image="https://images.unsplash.com/photo-1537996194471-e657df975ab4?q=80&w=2138&auto=format&fit=crop",
            description="An island paradise blending vibrant culture, lush rice terraces, and beautiful beaches.",
            budget=1500, recommended_duration=8, travel_styles=["Culture", "Nature", "Spiritual"],
            coordinates={"lat": -8.4095, "lng": 115.1889}, is_featured=True, is_trending=True
        )
        db.add_all([d1, d2, d3, d4])
        db.commit()

        # Experiences
        e1 = Experience(
            destination_id=d1.id, name="Private Tea Ceremony",
            image="https://images.unsplash.com/photo-1542281286-9e0a16bb7366?q=80&w=2069&auto=format&fit=crop",
            location="Higashiyama District, Kyoto", duration=2, price_estimate=150,
            category="Culture", travel_styles=["Culture", "Spiritual"],
            description="A mindful and authentic matcha tea ceremony led by a zen master in a 300-year-old traditional machiya."
        )
        e2 = Experience(
            destination_id=d3.id, name="Glacier Trekking",
            image="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=2070&auto=format&fit=crop",
            location="Torres del Paine", duration=8, price_estimate=300,
            category="Adventure", travel_styles=["Adventure", "Nature"],
            description="Strap on crampons and explore the mesmerizing ice caves and crevasses of the Grey Glacier."
        )
        e3 = Experience(
            destination_id=d2.id, name="Catamaran Sunset Cruise",
            image="https://images.unsplash.com/photo-1544321272-97b411d957fc?q=80&w=2070&auto=format&fit=crop",
            location="Oia, Santorini", duration=4, price_estimate=250,
            category="Luxury", travel_styles=["Romantic", "Luxury"],
            description="Sail the caldera on a luxury catamaran, complete with a Greek feast and open bar as the sun dips below the horizon."
        )
        e4 = Experience(
            destination_id=d4.id, name="Ubud Rice Terraces Cycling",
            image="https://images.unsplash.com/photo-1560930773-16a73c9db60b?q=80&w=2070&auto=format&fit=crop",
            location="Ubud, Bali", duration=5, price_estimate=80,
            category="Adventure", travel_styles=["Adventure", "Nature"],
            description="Downhill cycling through lush ancient rice terraces and authentic Balinese villages."
        )
        db.add_all([e1, e2, e3, e4])
        db.commit()

    print("Seed data injected successfully!")

if __name__ == "__main__":
    seed_db()
