from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, OptimizationAudit, Disruption, ItineraryItem
from app.models.enums import DisruptionStatus
from datetime import datetime

class CostExplanationService:
    @staticmethod
    def get_cost_explanation(db: Session, trip_id: int):
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise ValueError("Trip not found")

        active_itin = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
        active_items = db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == active_itin.id).all() if active_itin else []
        
        current_total = sum(i.estimated_cost or 0 for i in active_items)

        # Get the latest optimization audit
        audit = db.query(OptimizationAudit).filter(OptimizationAudit.trip_id == trip_id).order_by(OptimizationAudit.id.desc()).first()
        
        # Get active disruption (to calculate unmanaged cost)
        disruption = db.query(Disruption).filter(Disruption.trip_id == trip_id, Disruption.status.in_([DisruptionStatus.DETECTED, DisruptionStatus.ANALYZING, DisruptionStatus.ALTERNATIVES_READY])).order_by(Disruption.id.desc()).first()

        target_budget = trip.budget or (audit.target_budget if audit else current_total)
        original_total = audit.original_cost if audit else current_total
        optimized_total = audit.optimized_cost if audit else current_total
        savings = audit.savings if audit else 0
        budget_delta = current_total - target_budget
        
        components = []
        reasons = []
        sources = audit.data_sources if audit else ["Original Data"]

        if audit and audit.changed_components:
            for c in audit.changed_components:
                # Synthesize a deterministic reason
                ctype = c.get('component_type', 'Component').upper()
                reason_text = ""
                cost_diff = c.get('original_cost', 0) - c.get('optimized_cost', 0)
                if cost_diff > 0:
                    reason_text = f"{ctype} cost decreased because the optimizer selected a lower-cost alternative."
                elif cost_diff < 0:
                    reason_text = f"{ctype} cost increased due to price updates or disruption impacts."
                else:
                    reason_text = f"{ctype} was preserved to match your preferences."

                components.append({
                    "component_type": ctype,
                    "original_cost": c.get('original_cost', 0),
                    "optimized_cost": c.get('optimized_cost', 0),
                    "savings": c.get('savings', 0),
                    "reason": reason_text,
                    "source": c.get('source', 'Unknown'),
                    "freshness": c.get('freshness', 'Unknown')
                })
                reasons.append(f"{ctype}: {reason_text}")

        # If there is a disruption, calculate unmanaged cost
        projected_unmanaged_cost = current_total
        avoided_cost = 0
        if disruption and disruption.impact_summary:
            cost_impact = disruption.impact_summary.get('cost_impact', 0)
            projected_unmanaged_cost = current_total + cost_impact
            
            # If we had an optimized total for this disruption
            if audit:
                avoided_cost = projected_unmanaged_cost - optimized_total

        return {
            "trip_id": trip_id,
            "itinerary_version_id": active_itin.id if active_itin else None,
            "original_total": original_total,
            "current_total": current_total,
            "projected_unmanaged_cost": projected_unmanaged_cost,
            "optimized_total": optimized_total,
            "target_budget": target_budget,
            "savings": savings,
            "avoided_cost": avoided_cost,
            "budget_delta": budget_delta,
            "currency": "USD",
            "optimization_strategy": audit.optimization_strategy if audit else "NONE",
            "preference_preservation": ["Culture: Preserved", "Pace: Preserved"] if audit and audit.optimization_strategy == "PRESERVE_EXPERIENCES" else ["Cost: Minimized"],
            "components": components,
            "reasons": reasons,
            "data_sources": sources,
            "generated_at": datetime.utcnow().isoformat()
        }

    @staticmethod
    def get_operator_cost_control(db: Session):
        trips = db.query(Trip).all()
        disruptions = db.query(Disruption).filter(Disruption.status.in_([DisruptionStatus.DETECTED, DisruptionStatus.ANALYZING, DisruptionStatus.ALTERNATIVES_READY])).all()
        
        at_risk = []
        total_potential_impact = 0
        total_avoided_cost = 0
        
        for d in disruptions:
            impact = d.impact_summary.get('cost_impact', 0) if d.impact_summary else 0
            total_potential_impact += impact
            
            trip = next((t for t in trips if t.id == d.trip_id), None)
            if not trip: continue
            
            # Get latest audit for avoided cost
            audit = db.query(OptimizationAudit).filter(OptimizationAudit.trip_id == trip.id).order_by(OptimizationAudit.id.desc()).first()
            
            current_cost = sum(i.estimated_cost or 0 for i in trip.itineraries[-1].items) if trip.itineraries else 0
            opt_cost = audit.optimized_cost if audit else current_cost
            avoided = (current_cost + impact) - opt_cost if audit else 0
            total_avoided_cost += avoided
            
            at_risk.append({
                "trip_id": trip.id,
                "traveler_name": "Traveler " + str(trip.traveler_id),
                "destination": trip.destinations[0] if trip.destinations else "Unknown",
                "current_cost": current_cost,
                "potential_impact": impact,
                "optimized_cost": opt_cost,
                "potential_avoided_cost": avoided,
                "status": d.status.value,
                "action_required": "ACTION REQUIRED"
            })

        return {
            "active_trips": len(trips),
            "at_risk_trips": len(at_risk),
            "active_disruptions": len(disruptions),
            "potential_cost_impact": total_potential_impact,
            "potential_avoided_cost": total_avoided_cost,
            "trips_requiring_approval": len([d for d in disruptions if d.status == DisruptionStatus.ALTERNATIVES_READY]),
            "cost_at_risk": at_risk
        }
