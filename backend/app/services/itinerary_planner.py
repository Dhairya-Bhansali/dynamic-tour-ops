from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, ItineraryItem, Experience, Destination
from app.services.itinerary_validator import ItineraryValidator
from datetime import datetime, timedelta
import random

class ItineraryPlanner:
    @staticmethod
    def generate_itinerary(db: Session, trip_id: int):
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise Exception("Trip not found")
        
        prefs = trip.preferences or {}
        duration = prefs.get("duration", 3)
        budget = prefs.get("budget", 5000)
        selected_exp_ids = prefs.get("selected_experiences", [])
        
        # Determine existing version
        existing_versions = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).count()
        new_version_num = existing_versions + 1
        
        new_itinerary = Itinerary(trip_id=trip_id, version=new_version_num, is_active=True)
        db.add(new_itinerary)
        db.flush()
        
        # Deactivate old versions
        db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.id != new_itinerary.id).update({"is_active": False})
        
        start_date = datetime.strptime(prefs.get("start_date", datetime.utcnow().strftime("%Y-%m-%d")), "%Y-%m-%d")
        
        # Deterministic Fallback logic: schedule selected experiences
        experiences = db.query(Experience).filter(Experience.id.in_(selected_exp_ids)).all() if selected_exp_ids else []
        
        items_payload = []
        current_exp_idx = 0
        
        for day in range(1, duration + 1):
            current_date = start_date + timedelta(days=day-1)
            
            # Morning Activity
            items_payload.append({
                "day_number": day,
                "day_date": current_date,
                "start_time": current_date + timedelta(hours=9),
                "end_time": current_date + timedelta(hours=11),
                "activity_type": "BREAKFAST",
                "description": "Local breakfast near hotel",
                "location": "City Center",
                "estimated_cost": 25.0,
                "ai_reasoning": "Fits your 'Relaxed' pace and 'Food' interest.",
                "confidence_score": 0.95
            })
            
            # Main Activity (Experiences)
            if current_exp_idx < len(experiences):
                exp = experiences[current_exp_idx]
                items_payload.append({
                    "day_number": day,
                    "day_date": current_date,
                    "start_time": current_date + timedelta(hours=12),
                    "end_time": current_date + timedelta(hours=12 + exp.duration),
                    "activity_type": "EXPERIENCE",
                    "description": exp.name,
                    "location": exp.location,
                    "estimated_cost": exp.price_estimate,
                    "ai_reasoning": f"You explicitly selected this experience. Fits category '{exp.category}'.",
                    "confidence_score": 1.0
                })
                current_exp_idx += 1
            else:
                items_payload.append({
                    "day_number": day,
                    "day_date": current_date,
                    "start_time": current_date + timedelta(hours=14),
                    "end_time": current_date + timedelta(hours=17),
                    "activity_type": "EXPLORATION",
                    "description": "Guided walking tour and sightseeing",
                    "location": "Historic District",
                    "estimated_cost": 50.0,
                    "ai_reasoning": "Highly rated cultural exploration based on your DNA.",
                    "confidence_score": 0.88
                })
                
        # Validate deterministic plan
        validation_res = ItineraryValidator.validate_plan(items_payload, budget)
        
        # Save to DB
        db_items = []
        for item in items_payload:
            it = ItineraryItem(
                itinerary_id=new_itinerary.id,
                **item
            )
            db.add(it)
            db_items.append(it)
            
        db.commit()
        db.refresh(new_itinerary)
        
        return new_itinerary, validation_res
