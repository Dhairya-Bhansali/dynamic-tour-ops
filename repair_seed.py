import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.core_models import Base, User, Traveler, Trip, Destination, Itinerary, ItineraryItem, Booking
from datetime import datetime, timedelta

def verify_and_repair_seed_data():
    engine = create_engine("sqlite:///backend/tour_ops.db")
    Session = sessionmaker(bind=engine)
    db = Session()

    # 1. Ensure User & Traveler
    user = db.query(User).filter_by(email="rahul.sharma@example.com").first()
    if not user:
        user = User(email="rahul.sharma@example.com", full_name="Rahul Sharma", role="TRAVELER")
        db.add(user)
        db.commit()

    traveler = db.query(Traveler).filter_by(user_id=user.id).first()
    if not traveler:
        traveler = Traveler(user_id=user.id, preferences="{}")
        db.add(traveler)
        db.commit()

    # 2. Ensure Destination
    dest = db.query(Destination).filter_by(name="Kyoto").first()
    if not dest:
        dest = Destination(name="Kyoto", country="Japan", description="Cultural capital",
                           latitude=35.0116, longitude=135.7681)
        db.add(dest)
        db.commit()

    # 3. Ensure Trip
    trip = db.query(Trip).filter_by(traveler_id=traveler.id, destination_id=dest.id).first()
    if not trip:
        trip = Trip(traveler_id=traveler.id, destination_id=dest.id, 
                    start_date=datetime.utcnow() + timedelta(days=2),
                    end_date=datetime.utcnow() + timedelta(days=7),
                    status="ACTIVE",
                    budget_tier="PREMIUM",
                    coordinator="System")
        db.add(trip)
        db.commit()

    # 4. Ensure Itinerary & Items
    itin = db.query(Itinerary).filter_by(trip_id=trip.id, is_active=True).first()
    if not itin:
        itin = Itinerary(trip_id=trip.id, total_estimated_cost=1500, version=1, is_active=True, ai_reasoning="Good fit")
        db.add(itin)
        db.commit()
        
        # Items
        item1 = ItineraryItem(itinerary_id=itin.id, day_number=1, start_time=datetime.utcnow(), 
                              description="Hotel Check-in", location="Grand Kyoto Hotel",
                              estimated_cost=500)
        item2 = ItineraryItem(itinerary_id=itin.id, day_number=2, start_time=datetime.utcnow() + timedelta(hours=2), 
                              description="Kyoto Tea Ceremony", location="Gion",
                              estimated_cost=200)
        db.add_all([item1, item2])
        db.commit()

    # 5. Ensure Bookings
    bookings = db.query(Booking).filter_by(trip_id=trip.id).all()
    if not bookings:
        b1 = Booking(trip_id=trip.id, booking_type="HOTEL", provider="DemoProvider", status="CONFIRMED", cost=500, currency="USD")
        b2 = Booking(trip_id=trip.id, booking_type="ACTIVITY", provider="DemoProvider", status="PENDING", cost=200, currency="USD")
        db.add_all([b1, b2])
        db.commit()
        
    print(f"Demo trip ID: {trip.id}")
    print("Seed data repaired successfully.")

if __name__ == "__main__":
    verify_and_repair_seed_data()
