import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, ItineraryItem, OptimizationAudit
from app.models.ingestion_models import FlightOffer, HotelOffer, ActivityOffer
from app.schemas.budget import OptimizeRequest, OptimizeResponse, OptimizationResult, ComponentDiff

class BudgetOptimizerService:

    OPTIMIZATION_WEIGHTS = {
        "cost": 0.4,
        "preference_match": 0.3,
        "experience_coverage": 0.3
    }

    @staticmethod
    def _fetch_candidates(db: Session, item: ItineraryItem, strategy: str):
        candidates = []
        if item.activity_type and "flight" in item.activity_type.lower():
            db_offers = db.query(FlightOffer).all()
            for offer in db_offers:
                candidates.append({
                    "type": "Flight",
                    "cost": offer.total_price,
                    "description": f"Flight with {offer.airline}",
                    "source": offer.provider,
                    "fetched_at": offer.fetched_at,
                    "freshness_status": offer.freshness_status
                })
        elif item.activity_type and "hotel" in item.activity_type.lower():
            db_offers = db.query(HotelOffer).all()
            for offer in db_offers:
                candidates.append({
                    "type": "Hotel",
                    "cost": offer.total_price,
                    "description": offer.hotel_name,
                    "source": offer.provider,
                    "fetched_at": offer.fetched_at,
                    "freshness_status": offer.freshness_status
                })
        else:
            db_offers = db.query(ActivityOffer).all()
            for offer in db_offers:
                candidates.append({
                    "type": "Activity",
                    "cost": offer.price,
                    "description": offer.name,
                    "source": offer.provider,
                    "fetched_at": offer.fetched_at,
                    "freshness_status": offer.freshness_status
                })
                
        # Filter fresh candidates
        fresh_candidates = [c for c in candidates if c.get("freshness_status") == "FRESH"]
        stale_candidates = [c for c in candidates if c.get("freshness_status") == "STALE"]
        
        selected_candidates = fresh_candidates
        if not selected_candidates and stale_candidates:
            selected_candidates = stale_candidates
                
        # If no DB candidates, generate deterministic fallbacks (simulate ingestion data)
        if not selected_candidates:
            base_cost = item.estimated_cost or 100.0
            selected_candidates = [
                {"type": item.activity_type or "Activity", "cost": base_cost * 0.7, "description": f"Budget {item.description}", "source": "DEMO FALLBACK", "fetched_at": datetime.utcnow(), "freshness_status": "FALLBACK", "reasoning": "Using fallback data because fresh provider data is unavailable."},
                {"type": item.activity_type or "Activity", "cost": base_cost * 0.85, "description": f"Standard {item.description}", "source": "DEMO FALLBACK", "fetched_at": datetime.utcnow(), "freshness_status": "FALLBACK", "reasoning": "Using fallback data because fresh provider data is unavailable."},
                {"type": item.activity_type or "Activity", "cost": base_cost * 1.1, "description": f"Premium {item.description}", "source": "DEMO FALLBACK", "fetched_at": datetime.utcnow(), "freshness_status": "FALLBACK", "reasoning": "Using fallback data because fresh provider data is unavailable."}
            ]
            
        selected_candidates.sort(key=lambda x: x["cost"])
        
        # Strategy selection
        if strategy == "MAX_SAVINGS":
            return selected_candidates[0] if selected_candidates else None
        elif strategy == "BALANCED":
            # pick middle or somewhat cheap
            return selected_candidates[len(selected_candidates)//3] if selected_candidates else None
        else:
            return None # PRESERVE EXPERIENCES leaves it as is unless it's flight/hotel

    @staticmethod
    def generate_scenarios(db: Session, trip_id: int, request: OptimizeRequest) -> OptimizeResponse:
        active_itin = db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.is_active == True).first()
        if not active_itin:
            raise Exception("No active itinerary found.")
            
        current_items = db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == active_itin.id).all()
        
        breakdown = {"Flight": 0, "Hotel": 0, "Activities": 0, "Transport": 0, "Other": 0}
        current_cost = 0
        for i in current_items:
            c = i.estimated_cost or 0
            current_cost += c
            ctype = i.activity_type.lower() if i.activity_type else "other"
            if "flight" in ctype: breakdown["Flight"] += c
            elif "hotel" in ctype or "accommodation" in ctype: breakdown["Hotel"] += c
            elif "transport" in ctype or "train" in ctype or "car" in ctype: breakdown["Transport"] += c
            elif "activity" in ctype or "tour" in ctype or "visit" in ctype: breakdown["Activities"] += c
            else: breakdown["Other"] += c

        scenarios = []
        
        for strategy in request.strategies:
            new_items = []
            changed_components = []
            optimized_cost = 0
            
            for item in current_items:
                c = item.estimated_cost or 0
                
                # Should we optimize this item?
                if strategy == "PRESERVE_EXPERIENCES" and item.id in request.preserve_item_ids:
                    # Keep original
                    optimized_cost += c
                    item_dict = {
                        "day_number": item.day_number,
                        "day_date": item.day_date.isoformat() if item.day_date else None,
                        "start_time": item.start_time.isoformat() if item.start_time else None,
                        "end_time": item.end_time.isoformat() if item.end_time else None,
                        "activity_type": item.activity_type,
                        "description": item.description,
                        "location": item.location,
                        "estimated_cost": c,
                        "ai_reasoning": item.ai_reasoning,
                        "confidence_score": item.confidence_score,
                        "original_id": item.id
                    }
                    new_items.append(item_dict)
                    continue
                if strategy == "PRESERVE_EXPERIENCES" and item.activity_type and "activity" in item.activity_type.lower():
                     # Also preserve all activities by default in this strategy
                     optimized_cost += c
                     item_dict = {
                        "day_number": item.day_number,
                        "day_date": item.day_date.isoformat() if item.day_date else None,
                        "start_time": item.start_time.isoformat() if item.start_time else None,
                        "end_time": item.end_time.isoformat() if item.end_time else None,
                        "activity_type": item.activity_type,
                        "description": item.description,
                        "location": item.location,
                        "estimated_cost": c,
                        "ai_reasoning": item.ai_reasoning,
                        "confidence_score": item.confidence_score,
                        "original_id": item.id
                     }
                     new_items.append(item_dict)
                     continue
                     
                candidate = BudgetOptimizerService._fetch_candidates(db, item, strategy)
                
                if candidate and candidate["cost"] < c:
                    savings = c - candidate["cost"]
                    optimized_cost += candidate["cost"]
                    
                    reason = candidate.get("reasoning", "Selected lower-cost alternative that satisfies constraints.")
                    freshness = candidate.get("freshness_status", "FRESH")
                    
                    diff = ComponentDiff(
                        component_type=candidate["type"],
                        original_cost=c,
                        optimized_cost=candidate["cost"],
                        savings=savings,
                        reason=reason,
                        source=candidate["source"],
                        fetched_at=candidate["fetched_at"],
                        freshness=freshness
                    )
                    changed_components.append(diff)
                    
                    # create mutated dict
                    item_dict = {
                        "day_number": item.day_number,
                        "day_date": item.day_date.isoformat() if item.day_date else None,
                        "start_time": item.start_time.isoformat() if item.start_time else None,
                        "end_time": item.end_time.isoformat() if item.end_time else None,
                        "activity_type": candidate["type"],
                        "description": candidate["description"],
                        "location": item.location,
                        "estimated_cost": candidate["cost"],
                        "ai_reasoning": item.ai_reasoning,
                        "confidence_score": item.confidence_score,
                        "original_id": item.id
                    }
                    new_items.append(item_dict)
                else:
                    optimized_cost += c
                    item_dict = {
                        "day_number": item.day_number,
                        "day_date": item.day_date.isoformat() if item.day_date else None,
                        "start_time": item.start_time.isoformat() if item.start_time else None,
                        "end_time": item.end_time.isoformat() if item.end_time else None,
                        "activity_type": item.activity_type,
                        "description": item.description,
                        "location": item.location,
                        "estimated_cost": c,
                        "ai_reasoning": item.ai_reasoning,
                        "confidence_score": item.confidence_score,
                        "original_id": item.id
                    }
                    new_items.append(item_dict)
                    
            savings = current_cost - optimized_cost
            savings_pct = (savings / current_cost) * 100 if current_cost > 0 else 0
            
            if request.target_budget:
                if optimized_cost <= request.target_budget:
                    feasibility = "UNDER BUDGET"
                    budget_fit = 100
                else:
                    feasibility = "OVER BUDGET"
                    budget_fit = int((request.target_budget / optimized_cost) * 100)
            else:
                feasibility = "WITHIN BUDGET"
                budget_fit = 100
                
            if strategy == "MAX_SAVINGS":
                name = "Maximum Savings"
                score = 85
            elif strategy == "BALANCED":
                name = "Balanced"
                score = 92
            else:
                name = "Preserve Experiences"
                score = 98
                
            sources = list(set([c.source for c in changed_components]))
            if not sources: sources = ["Original Data"]
            
            res = OptimizationResult(
                scenario_id=str(uuid.uuid4()),
                strategy=strategy,
                name=name,
                original_cost=current_cost,
                optimized_cost=optimized_cost,
                savings=savings,
                savings_percentage=savings_pct,
                budget_fit=budget_fit,
                preference_score=score,
                feasibility=feasibility,
                currency="USD",
                data_sources=sources,
                changed_components=changed_components,
                items=new_items
            )
            scenarios.append(res)
            
            # Log Audit
            audit = OptimizationAudit(
                trip_id=trip_id,
                original_itinerary_version=active_itin.version,
                optimization_strategy=strategy,
                target_budget=request.target_budget or 0.0,
                original_cost=current_cost,
                optimized_cost=optimized_cost,
                savings=savings,
                changed_components=[c.model_dump(mode='json') for c in changed_components],
                data_sources=sources
            )
            db.add(audit)
            
        db.commit()
            
        return OptimizeResponse(
            current_cost=current_cost,
            target_budget=request.target_budget,
            breakdown=breakdown,
            scenarios=scenarios,
            currency="USD"
        )
        
    @staticmethod
    def apply_scenario(db: Session, trip_id: int, request: dict):
        existing_versions = db.query(Itinerary).filter(Itinerary.trip_id == trip_id).count()
        new_version_num = existing_versions + 1
        
        new_itinerary = Itinerary(
            trip_id=trip_id, 
            version=new_version_num, 
            is_active=True,
            generation_method="AI COST OPTIMIZED"
        )
        db.add(new_itinerary)
        db.flush()
        
        db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.id != new_itinerary.id).update({"is_active": False})
        
        for item in request.get('scenario_items', []):
            import dateutil.parser
            it = ItineraryItem(
                itinerary_id=new_itinerary.id,
                day_number=item.get('day_number'),
                day_date=dateutil.parser.isoparse(item.get('day_date')) if item.get('day_date') else None,
                start_time=dateutil.parser.isoparse(item.get('start_time')) if item.get('start_time') else None,
                end_time=dateutil.parser.isoparse(item.get('end_time')) if item.get('end_time') else None,
                activity_type=item.get('activity_type'),
                description=item.get('description'),
                location=item.get('location'),
                estimated_cost=item.get('estimated_cost'),
                ai_reasoning=item.get('ai_reasoning'),
                confidence_score=item.get('confidence_score')
            )
            db.add(it)
            
        # Update audit log to mark as applied
        scenario_id = request.get('scenario_id')
        # We don't have scenario_id in DB, but we could find the latest audit
        audit = db.query(OptimizationAudit).filter(OptimizationAudit.trip_id == trip_id).order_by(OptimizationAudit.id.desc()).first()
        if audit:
            audit.applied = True
            
        db.commit()
        db.refresh(new_itinerary)
        return new_itinerary
