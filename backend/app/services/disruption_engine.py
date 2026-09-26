import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, ItineraryItem, Disruption, AlternativePlan
from app.models.enums import DisruptionStatus
from app.services.budget_optimizer import BudgetOptimizerService
from app.schemas.budget import OptimizeRequest

DISRUPTION_THRESHOLDS = {
    "flight_price_percent": 0.05,
    "hotel_price_percent": 0.05,
    "route_delay_minutes": 30,
    "weather_risk": "HIGH"
}

class DisruptionEngine:

    @staticmethod
    def simulate_disruption(db: Session, trip_id: int, disruption_type: str):
        active_itin = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
        if not active_itin:
            raise ValueError("No active itinerary found.")
        
        items = db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == active_itin.id).all()
        
        target_item = None
        if disruption_type in ["PRICE_CHANGE", "FLIGHT_CHANGE", "FLIGHT_UNAVAILABLE"]:
            target_item = next((i for i in items if i.activity_type and "flight" in i.activity_type.lower()), None)
        elif disruption_type == "HOTEL_UNAVAILABLE":
            target_item = next((i for i in items if i.activity_type and "hotel" in i.activity_type.lower()), None)
        elif disruption_type == "WEATHER_RISK":
            target_item = next((i for i in items if i.activity_type and "activity" in i.activity_type.lower()), None)
            
        if not target_item and items:
            target_item = items[0]
            
        if not target_item:
            raise ValueError("No matching itinerary items found for disruption.")

        cost_impact = 0
        title = ""
        desc = ""
        prev_val = str(target_item.estimated_cost)
        curr_val = ""
        severity = "MEDIUM"

        if disruption_type == "PRICE_CHANGE":
            increase = 4500
            cost_impact = increase
            curr_val = str((target_item.estimated_cost or 0) + increase)
            title = "Flight price increased"
            desc = f"Your {target_item.description} price increased by ₹{increase}."
            severity = "HIGH"
        elif disruption_type == "HOTEL_UNAVAILABLE":
            curr_val = "Unavailable"
            title = "Hotel fully booked"
            desc = f"{target_item.description} is no longer available for your dates."
            severity = "HIGH"
        elif disruption_type == "WEATHER_RISK":
            curr_val = "High Precipitation"
            prev_val = "Clear"
            title = "Weather condition alert"
            desc = "Heavy precipitation is expected which may affect this outdoor activity."
            severity = "LOW"
        else:
            curr_val = "Delayed"
            title = "Route Delay"
            desc = f"{target_item.description} route significantly delayed."
            
        impact_summary = {
            "cost_impact": cost_impact,
            "affected_items": [target_item.id],
            "projected_cost": sum(i.estimated_cost or 0 for i in items) + cost_impact
        }
        
        impact_radius = {
            "downstream_affected": [i.id for i in items if i.day_number >= target_item.day_number and i.id != target_item.id]
        }

        d = Disruption(
            trip_id=trip_id,
            itinerary_version_id=active_itin.id,
            disruption_type=disruption_type,
            severity=severity,
            title=title,
            description=desc,
            source="DEMO SIMULATION",
            source_record_id=str(uuid.uuid4()),
            previous_value=prev_val,
            current_value=curr_val,
            status=DisruptionStatus.DETECTED,
            impact_summary=impact_summary,
            impact_radius=impact_radius,
            confidence="HIGH",
            requires_approval=True
        )
        db.add(d)
        db.commit()
        db.refresh(d)
        return d
        
    @staticmethod
    def analyze_and_generate_alternatives(db: Session, disruption_id: int):
        disruption = db.query(Disruption).filter(Disruption.id == disruption_id).first()
        if not disruption:
            raise ValueError("Disruption not found.")
            
        disruption.status = DisruptionStatus.ANALYZING
        db.commit()
        
        # Determine constraints based on disruption type.
        trip = db.query(Trip).filter(Trip.id == disruption.trip_id).first()
        target_budget = trip.budget or sum(i.estimated_cost or 0 for i in disruption.itinerary_version.items)
        
        # Use Budget Optimizer to generate candidates
        req = OptimizeRequest(target_budget=target_budget, strategies=["BALANCED", "PRESERVE_EXPERIENCES"])
        opt_response = BudgetOptimizerService.generate_scenarios(db, disruption.trip_id, req)
        
        # Create AlternativePlans
        for scen in opt_response.scenarios:
            alt = AlternativePlan(
                disruption_id=disruption.id,
                confidence_score=scen.preference_score,
                changes=[c.model_dump(mode='json') for c in scen.changed_components],
                cost_difference=scen.savings * -1 if scen.savings > 0 else abs(scen.savings),
                preference_match=scen.preference_score,
                travel_time_difference=0,
                reason=f"{scen.name}: {len(scen.changed_components)} components updated.",
                items=scen.items
            )
            db.add(alt)
            
        disruption.status = DisruptionStatus.ALTERNATIVES_READY
        db.commit()
        
        return disruption

    @staticmethod
    def approve_alternative(db: Session, disruption_id: int, alternative_id: int):
        disruption = db.query(Disruption).filter(Disruption.id == disruption_id).first()
        alt = db.query(AlternativePlan).filter(AlternativePlan.id == alternative_id).first()
        
        if not disruption or not alt:
            raise ValueError("Disruption or alternative not found.")
            
        new_items = alt.items
            
        # Apply Scenario
        new_itin = BudgetOptimizerService.apply_scenario(db, disruption.trip_id, {"scenario_items": new_items, "scenario_id": str(alt.id)})
        
        disruption.status = DisruptionStatus.APPROVED
        alt.is_approved = True
        db.commit()
        return new_itin
        
    @staticmethod
    def reject_disruption(db: Session, disruption_id: int):
        disruption = db.query(Disruption).filter(Disruption.id == disruption_id).first()
        disruption.status = DisruptionStatus.REJECTED
        db.commit()
        return disruption
