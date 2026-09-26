from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.base import Base
from app.db.session import engine
from app.models.core_models import Trip, Itinerary, ItineraryItem, User, Disruption, AlternativePlan, OptimizationAudit
from app.models.ingestion_models import DataSource, IngestionRun, FlightOffer, HotelOffer, ActivityOffer, WeatherForecast, Place, Route
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/reset")
def reset_demo_data(db: Session = Depends(get_db)):
    """Reset the database to the deterministic demo scenario."""
    # We want this to be safe, so we only clear data if we're explicitly running the reset.
    # To be extremely safe, we could just delete all data and recreate the schema.
    
    # 1. Clear all data
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    now = datetime.utcnow()
    
    # 2. Create Demo User
    demo_user = User(name="Demo Traveler", email="traveler@nex-tour.demo", password_hash="demo_hash")
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    # 3. Create Demo Trip
    trip = Trip(
        user_id=demo_user.id,
        destination="Kyoto",
        budget=60000,
        currency="INR",
        start_date=now + timedelta(days=30),
        end_date=now + timedelta(days=35),
        travel_style="Relaxed",
        interests="Culture, Food",
        status="PLANNING"
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    
    # 4. Create Initial Itinerary
    itin = Itinerary(
        trip_id=trip.id,
        version=1,
        is_active=True,
        total_estimated_cost=65000 # Slightly above target budget 60000
    )
    db.add(itin)
    db.commit()
    db.refresh(itin)
    
    # 5. Add Demo Items
    items = [
        ItineraryItem(
            itinerary_id=itin.id, day_number=1, day_date=trip.start_date, start_time=trip.start_date,
            end_time=trip.start_date + timedelta(hours=6), activity_type="flight", description="Flight to Kyoto (KIX)",
            location="KIX Airport", estimated_cost=35000, ai_reasoning="Direct flight selected for a relaxed start.", confidence_score=0.9
        ),
        ItineraryItem(
            itinerary_id=itin.id, day_number=1, day_date=trip.start_date, start_time=trip.start_date + timedelta(hours=7),
            end_time=trip.start_date + timedelta(hours=8), activity_type="transport", description="Airport Transfer",
            location="Kyoto Station", estimated_cost=2000, ai_reasoning="Standard rail transfer.", confidence_score=0.9
        ),
        ItineraryItem(
            itinerary_id=itin.id, day_number=1, day_date=trip.start_date, start_time=trip.start_date + timedelta(hours=9),
            end_time=trip.start_date + timedelta(hours=24), activity_type="hotel", description="Luxury Ryokan",
            location="Higashiyama", estimated_cost=20000, ai_reasoning="Premium stay matching culture preference.", confidence_score=0.8
        ),
        ItineraryItem(
            itinerary_id=itin.id, day_number=2, day_date=trip.start_date + timedelta(days=1), start_time=trip.start_date + timedelta(days=1, hours=10),
            end_time=trip.start_date + timedelta(days=1, hours=14), activity_type="activity", description="Guided Temple Tour",
            location="Kinkaku-ji", estimated_cost=5000, ai_reasoning="Highly rated cultural experience.", confidence_score=0.95
        ),
        ItineraryItem(
            itinerary_id=itin.id, day_number=2, day_date=trip.start_date + timedelta(days=1), start_time=trip.start_date + timedelta(days=1, hours=19),
            end_time=trip.start_date + timedelta(days=1, hours=21), activity_type="dining", description="Omakase Sushi Dinner",
            location="Gion", estimated_cost=3000, ai_reasoning="Fulfills foodie preference.", confidence_score=0.9
        )
    ]
    db.add_all(items)
    db.commit()
    
    # 6. Seed mock provider data for optimizer
    # Flight fallback
    f_offer = FlightOffer(
        provider="Amadeus",
        external_id="flight_demo_opt",
        origin="DEL",
        destination="KIX",
        total_price=28000,
        currency="INR",
        fetched_at=now,
        valid_from=now,
        valid_until=now + timedelta(hours=2),
        freshness_status="FRESH",
        airline="ANA"
    )
    # Hotel fallback
    h_offer = HotelOffer(
        provider="Amadeus",
        external_id="hotel_demo_opt",
        hotel_name="Boutique Ryokan",
        location="Kyoto",
        total_price=15000,
        currency="INR",
        fetched_at=now,
        valid_from=now,
        valid_until=now + timedelta(hours=2),
        freshness_status="FRESH"
    )
    db.add_all([f_offer, h_offer])
    db.commit()
    
    return {"status": "success", "message": "Demo data reset successfully", "trip_id": trip.id}
