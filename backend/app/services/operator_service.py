from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.core_models import Trip, Traveler, Itinerary, ItineraryItem, Booking
from app.schemas.operator import OperatorDashboardMetrics, TourSummary, TourDetail, VendorItem, Alert
from sqlalchemy import func

class OperatorService:
    @staticmethod
    def get_dashboard_metrics(db: Session) -> OperatorDashboardMetrics:
        active = db.query(Trip).filter(Trip.status == 'ACTIVE').count()
        upcoming = db.query(Trip).filter(Trip.status == 'UPCOMING').count()
        travelers = db.query(Traveler).count()
        confirmed_bookings = db.query(Booking).filter(Booking.status == 'CONFIRMED').count()
        attention = db.query(Trip).filter(Trip.status == 'ATTENTION_REQUIRED').count()
        
        return OperatorDashboardMetrics(
            active_tours=active,
            upcoming_tours=upcoming,
            total_travelers=travelers,
            confirmed_bookings=confirmed_bookings,
            attention_required=attention
        )
        
    @staticmethod
    def get_tours(db: Session, status_filter: str = "ALL") -> list[TourSummary]:
        query = db.query(Trip)
        if status_filter != "ALL":
            query = query.filter(Trip.status == status_filter)
            
        trips = query.all()
        summaries = []
        
        for trip in trips:
            traveler = db.query(Traveler).filter(Traveler.id == trip.traveler_id).first()
            itin = db.query(Itinerary).filter(Itinerary.trip_id == trip.id, Itinerary.is_active == True).first()
            
            dest = trip.preferences.get("destination", "Unknown") if trip.preferences else "Unknown"
            
            book_str = "0/0"
            next_act = None
            attn = (trip.status == 'ATTENTION_REQUIRED')
            
            if itin:
                items = db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == itin.id).all()
                bookings = db.query(Booking).filter(Booking.trip_id == trip.id).all()
                bookable_count = len([i for i in items if i.activity_type != 'LEISURE'])
                conf_count = len([b for b in bookings if b.status == 'CONFIRMED'])
                book_str = f"{conf_count}/{bookable_count}"
                
                # mock next activity
                future_items = [i for i in items if i.start_time and i.start_time > datetime.utcnow()]
                if future_items:
                    future_items.sort(key=lambda x: x.start_time)
                    next_act = f"{future_items[0].description} - {future_items[0].start_time.strftime('%H:%M')}"
                elif items:
                    next_act = f"{items[0].description} - TBD"
                    
                if bookable_count > 0 and conf_count < bookable_count and trip.status in ['UPCOMING', 'ACTIVE']:
                    attn = True
            
            summaries.append(TourSummary(
                trip_id=trip.id,
                traveler_name=traveler.name if traveler else "Unknown",
                destination=dest,
                start_date=trip.start_date,
                end_date=trip.end_date,
                status="ATTENTION_REQUIRED" if attn else trip.status,
                booking_completion=book_str,
                coordinator=trip.coordinator or "Unassigned",
                attention_state=attn,
                next_scheduled_activity=next_act
            ))
            
        return summaries

    @staticmethod
    def get_alerts(db: Session) -> list[Alert]:
        alerts = []
        tours = OperatorService.get_tours(db)
        for t in tours:
            if t.attention_state:
                alerts.append(Alert(
                    id=f"ALT-{t.trip_id}",
                    severity="CRITICAL" if t.status == 'ACTIVE' else "WARNING",
                    trip_id=t.trip_id,
                    traveler_name=t.traveler_name,
                    affected_item="Missing Bookings",
                    reason="Not all required bookings are confirmed.",
                    timestamp=datetime.utcnow(),
                    recommended_action="Review and confirm pending bookings."
                ))
        return alerts

    @staticmethod
    def get_tour_detail(db: Session, trip_id: int) -> TourDetail:
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise Exception("Trip not found")
            
        traveler = db.query(Traveler).filter(Traveler.id == trip.traveler_id).first()
        itin = db.query(Itinerary).filter(Itinerary.trip_id == trip.id, Itinerary.is_active == True).first()
        
        timeline = []
        vendors = []
        book_str = "0/0"
        readiness = "ACTION REQUIRED"
        
        if itin:
            items = db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == itin.id).all()
            bookings = db.query(Booking).filter(Booking.trip_id == trip.id).all()
            
            bookable_count = len([i for i in items if i.activity_type != 'LEISURE'])
            conf_count = len([b for b in bookings if b.status == 'CONFIRMED'])
            book_str = f"{conf_count}/{bookable_count}"
            readiness = "READY" if (bookable_count > 0 and conf_count == bookable_count) else "ACTION REQUIRED"
            
            for item in items:
                b_match = next((b for b in bookings if b.itinerary_item_id == item.id), None)
                op_status = b_match.status if b_match else "UNBOOKED"
                
                timeline.append({
                    "id": item.id,
                    "date": item.day_date.isoformat() if item.day_date else None,
                    "start": item.start_time.isoformat() if item.start_time else None,
                    "end": item.end_time.isoformat() if item.end_time else None,
                    "activity": item.description,
                    "location": item.location,
                    "booking_status": op_status,
                    "provider": b_match.provider_id if b_match else None,
                    "cost": item.estimated_cost,
                    "dependencies": [],
                    "operational_status": "UPCOMING"
                })
                
                if b_match:
                    vendors.append(VendorItem(
                        id=b_match.id,
                        service_type=item.activity_type,
                        name=b_match.provider_id or "Demo Vendor",
                        status=b_match.status,
                        scheduled_time=item.start_time,
                        location=item.location,
                        cost=b_match.estimated_cost or 0
                    ))
                    
        return TourDetail(
            trip_id=trip.id,
            traveler_name=traveler.name if traveler else "Unknown",
            destination=trip.preferences.get("destination", "Unknown") if trip.preferences else "Unknown",
            start_date=trip.start_date,
            end_date=trip.end_date,
            budget=trip.preferences.get("budget", 0) if trip.preferences else 0,
            current_itinerary_version=itin.version if itin else 0,
            booking_completion=book_str,
            readiness=readiness,
            coordinator=trip.coordinator or "Unassigned",
            timeline=timeline,
            vendors=vendors
        )
