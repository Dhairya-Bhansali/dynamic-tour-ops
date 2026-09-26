from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.discovery import DestinationResponse, ExperienceResponse

from app.schemas.personalize import TravelDNABase

from app.schemas.itinerary import ItineraryResponse, ValidationResult

from app.schemas.explanation import TripExplanation

from app.schemas.budget import OptimizeRequest, OptimizeResponse, ApplyScenarioRequest
from app.schemas.booking import BookableItem, AvailabilityResponse, BookingResponse, TripReadiness, BookingBase

from app.schemas.live_trip import LiveTripStatus, AssistantRequest, AssistantResponse
from app.services.live_trip_service import LiveTripService

from app.schemas.operator import OperatorDashboardMetrics, TourSummary, TourDetail, Alert
from app.services.operator_service import OperatorService
from app.services.booking_service import BookingService
booking_service = BookingService()
from app.services.budget_optimizer import BudgetOptimizerService

from app.services.explanation_service import ExplanationService

from app.services.itinerary_planner import ItineraryPlanner
from app.schemas.personalize import TripPreferencesBase, TravelDNAResponse, TripPreferencesResponse
from app.services.personalize_service import PersonalizeService

from app.services.discovery_service import DiscoveryService
from typing import List, Optional

from app.db.session import get_db
from app.schemas.trip import TripCreate, TripResponse
from app.services.trip_service import TripService

from app.api.endpoints import ingestion

router = APIRouter()
router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])


@router.post("/trips", response_model=TripResponse)
def create_trip(trip: TripCreate, db: Session = Depends(get_db)):
    return TripService.create_trip(db, trip)

@router.get("/trips", response_model=List[TripResponse])
def get_trips(db: Session = Depends(get_db)):
    return TripService.get_all_trips(db)

@router.get("/trips/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = TripService.get_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@router.get("/destinations", response_model=List[DestinationResponse])
def get_destinations(
    search: Optional[str] = None, 
    style: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    return DiscoveryService.get_destinations(db, search=search, style=style)

@router.get("/destinations/{dest_id}", response_model=DestinationResponse)
def get_destination(dest_id: int, db: Session = Depends(get_db)):
    dest = DiscoveryService.get_destination(db, dest_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return dest

@router.get("/experiences", response_model=List[ExperienceResponse])
def get_experiences(
    category: Optional[str] = None,
    dest_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return DiscoveryService.get_experiences(db, category=category, dest_id=dest_id, search=search)

@router.get("/experiences/{exp_id}", response_model=ExperienceResponse)
def get_experience(exp_id: int, db: Session = Depends(get_db)):
    exp = DiscoveryService.get_experience(db, exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp

@router.get("/travel-dna/{traveler_id}", response_model=TravelDNAResponse)
def get_travel_dna(traveler_id: int, db: Session = Depends(get_db)):
    traveler = PersonalizeService.get_travel_dna(db, traveler_id)
    if not traveler:
        raise HTTPException(status_code=404, detail="Traveler not found")
    return TravelDNAResponse(traveler_id=traveler.id, preferences=traveler.preferences)

@router.put("/travel-dna/{traveler_id}", response_model=TravelDNAResponse)
def update_travel_dna(traveler_id: int, payload: TravelDNABase, db: Session = Depends(get_db)):
    traveler = PersonalizeService.update_travel_dna(db, traveler_id, payload.model_dump()["dimensions"])
    if not traveler:
        raise HTTPException(status_code=404, detail="Traveler not found")
    return TravelDNAResponse(traveler_id=traveler.id, preferences=traveler.preferences)

@router.get("/trips/{trip_id}/preferences", response_model=TripPreferencesResponse)
def get_trip_preferences(trip_id: int, db: Session = Depends(get_db)):
    trip = PersonalizeService.get_trip_preferences(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripPreferencesResponse(trip_id=trip.id, preferences=trip.preferences)

@router.put("/trips/{trip_id}/preferences", response_model=TripPreferencesResponse)
def update_trip_preferences(trip_id: int, payload: TripPreferencesBase, db: Session = Depends(get_db)):
    trip = PersonalizeService.update_trip_preferences(db, trip_id, payload.model_dump())
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripPreferencesResponse(trip_id=trip.id, preferences=trip.preferences)

@router.post("/trips/{trip_id}/itinerary/generate")
def generate_itinerary(trip_id: int, db: Session = Depends(get_db)):
    try:
        itinerary, validation = ItineraryPlanner.generate_itinerary(db, trip_id)
        return {
            "itinerary": ItineraryResponse.from_orm(itinerary),
            "validation": validation
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trips/{trip_id}/itinerary", response_model=ItineraryResponse)
def get_active_itinerary(trip_id: int, db: Session = Depends(get_db)):
    itinerary = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Active itinerary not found")
    return itinerary

@router.get("/trips/{trip_id}/itinerary/versions", response_model=List[ItineraryResponse])
def get_itinerary_versions(trip_id: int, db: Session = Depends(get_db)):
    itineraries = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).order_by(Itinerary.version.desc()).all()
    return itineraries

@router.get("/trips/{trip_id}/itinerary/explanation", response_model=TripExplanation)
def get_itinerary_explanation(trip_id: int, db: Session = Depends(get_db)):
    try:
        return ExplanationService.get_trip_explanation(db, trip_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trips/{trip_id}/budget/optimize", response_model=OptimizeResponse)
def optimize_budget(trip_id: int, request: OptimizeRequest, db: Session = Depends(get_db)):
    try:
        return BudgetOptimizerService.generate_scenarios(db, trip_id, request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/trips/{trip_id}/itinerary/apply-scenario")
def apply_scenario(trip_id: int, request: ApplyScenarioRequest, db: Session = Depends(get_db)):
    try:
        it = BudgetOptimizerService.apply_scenario(db, trip_id, request.dict())
        return {"status": "success", "itinerary_id": it.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trips/{trip_id}/bookable-items", response_model=List[BookableItem])
def get_bookable_items(trip_id: int, db: Session = Depends(get_db)):
    return booking_service.get_bookable_items(db, trip_id)

@router.post("/trips/{trip_id}/bookings/check-availability", response_model=AvailabilityResponse)
def check_availability(trip_id: int, request: BookingBase, db: Session = Depends(get_db)):
    return booking_service.check_availability(db, trip_id, request.itinerary_item_id)

@router.post("/trips/{trip_id}/bookings", response_model=BookingResponse)
def create_booking(trip_id: int, request: BookingBase, db: Session = Depends(get_db)):
    try:
        return booking_service.create_booking(db, trip_id, request.itinerary_item_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trips/{trip_id}/bookings", response_model=List[BookingResponse])
def get_bookings(trip_id: int, db: Session = Depends(get_db)):
    return booking_service.get_bookings(db, trip_id)

@router.get("/trips/{trip_id}/preparation", response_model=TripReadiness)
def get_preparation(trip_id: int, db: Session = Depends(get_db)):
    return booking_service.get_preparation_readiness(db, trip_id)

@router.get("/operator/dashboard", response_model=OperatorDashboardMetrics)
def get_operator_dashboard(db: Session = Depends(get_db)):
    return OperatorService.get_dashboard_metrics(db)

@router.get("/operator/tours", response_model=List[TourSummary])
def get_operator_tours(status_filter: str = "ALL", db: Session = Depends(get_db)):
    return OperatorService.get_tours(db, status_filter)

@router.get("/operator/tours/{trip_id}", response_model=TourDetail)
def get_operator_tour_detail(trip_id: int, db: Session = Depends(get_db)):
    try:
        return OperatorService.get_tour_detail(db, trip_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/operator/alerts", response_model=List[Alert])
def get_operator_alerts(db: Session = Depends(get_db)):
    return OperatorService.get_alerts(db)

@router.get("/trips/{trip_id}/live", response_model=LiveTripStatus)
def get_live_trip_status(trip_id: int, db: Session = Depends(get_db)):
    try:
        return LiveTripService.get_live_status(db, trip_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/trips/{trip_id}/assistant", response_model=AssistantResponse)
def handle_live_trip_assistant(trip_id: int, request: AssistantRequest, db: Session = Depends(get_db)):
    try:
        return LiveTripService.handle_assistant_request(db, trip_id, request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.services.disruption_engine import DisruptionEngine

@router.post("/trips/{trip_id}/disruptions/simulate")
def simulate_disruption(trip_id: int, disruption_type: str, db: Session = Depends(get_db)):
    try:
        d = DisruptionEngine.simulate_disruption(db, trip_id, disruption_type)
        return {"status": "success", "disruption_id": d.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/trips/{trip_id}/disruptions")
def get_disruptions(trip_id: int, db: Session = Depends(get_db)):
    from app.models.core_models import Disruption
    disruptions = db.query(Disruption).filter(Disruption.trip_id == trip_id).order_by(Disruption.id.desc()).all()
    # Simple dict return to avoid needing a Pydantic model for now
    return [{"id": d.id, "type": d.disruption_type, "severity": d.severity, "title": d.title, "description": d.description, "status": d.status, "impact": d.impact_summary, "confidence": d.confidence} for d in disruptions]

@router.post("/disruptions/{disruption_id}/analyze")
def analyze_disruption(disruption_id: int, db: Session = Depends(get_db)):
    try:
        DisruptionEngine.analyze_and_generate_alternatives(db, disruption_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/disruptions/{disruption_id}/alternatives")
def get_disruption_alternatives(disruption_id: int, db: Session = Depends(get_db)):
    from app.models.core_models import AlternativePlan
    alts = db.query(AlternativePlan).filter(AlternativePlan.disruption_id == disruption_id).all()
    return [{"id": a.id, "confidence_score": a.confidence_score, "changes": a.changes, "cost_difference": a.cost_difference, "preference_match": a.preference_match, "reason": a.reason, "is_approved": a.is_approved} for a in alts]

@router.post("/disruptions/{disruption_id}/approve/{alternative_id}")
def approve_disruption_alternative(disruption_id: int, alternative_id: int, db: Session = Depends(get_db)):
    try:
        new_itin = DisruptionEngine.approve_alternative(db, disruption_id, alternative_id)
        return {"status": "success", "new_itinerary_id": new_itin.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
@router.post("/disruptions/{disruption_id}/reject")
def reject_disruption(disruption_id: int, db: Session = Depends(get_db)):
    try:
        DisruptionEngine.reject_disruption(db, disruption_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/operator/disruptions")
def get_all_disruptions(db: Session = Depends(get_db)):
    from app.models.core_models import Disruption, Trip
    disruptions = db.query(Disruption).order_by(Disruption.id.desc()).all()
    res = []
    for d in disruptions:
        trip = db.query(Trip).filter(Trip.id == d.trip_id).first()
        res.append({
            "id": d.id,
            "trip_id": d.trip_id,
            "traveler": trip.id if trip else "Unknown",
            "type": d.disruption_type,
            "severity": d.severity,
            "title": d.title,
            "status": d.status,
            "impact": d.impact_summary
        })
    return res

from app.services.cost_explanation_service import CostExplanationService

@router.get("/trips/{trip_id}/cost-explanation")
def get_cost_explanation(trip_id: int, db: Session = Depends(get_db)):
    try:
        return CostExplanationService.get_cost_explanation(db, trip_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/operator/cost-control")
def get_operator_cost_control(db: Session = Depends(get_db)):
    try:
        return CostExplanationService.get_operator_cost_control(db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
