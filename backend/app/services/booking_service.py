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
