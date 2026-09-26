import json
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.core_models import Trip, Itinerary, ItineraryItem, Booking
from app.schemas.live_trip import LiveTripStatus, TimelineEvent, NextAction, LiveAlert, AssistantResponse
from app.services.operator_service import OperatorService

import openai
import os

class LiveTripService:
    @staticmethod
    def get_live_status(db: Session, trip_id: int) -> LiveTripStatus:
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise Exception("Trip not found")
            
        itin = db.query(Itinerary).filter(Itinerary.trip_id == trip.id, Itinerary.is_active == True).first()
        items = []
        if itin:
            items = db.query(ItineraryItem).filter(ItineraryItem.itinerary_id == itin.id).all()
            
        now = datetime.utcnow()
        
        # Calculate status_label and day_label
        status_label = trip.status
        day_label = ""
        
        if trip.start_date and trip.end_date:
            if now < trip.start_date:
                days_until = (trip.start_date - now).days
                status_label = "UPCOMING"
                day_label = f"Starts in {days_until} day(s)"
            elif now > trip.end_date:
                status_label = "COMPLETED"
                day_label = "Trip ended"
            else:
                status_label = "ACTIVE"
                day_number = (now - trip.start_date).days + 1
                total_days = (trip.end_date - trip.start_date).days + 1
                day_label = f"Day {day_number} of {total_days}"
        else:
            day_label = "Dates TBD"
            
        # Timeline
        timeline = []
        next_action = None
        
        # sort items by start_time
        sorted_items = [i for i in items if i.start_time]
        sorted_items.sort(key=lambda x: x.start_time)
        
        if sorted_items:
            # Fake logic for demo: pick first item as NOW, second as NEXT, third as LATER
            # In real life, filter by 'now'
            now_idx = 0
            if len(sorted_items) > 0:
                timeline.append(TimelineEvent(
                    id=sorted_items[0].id,
                    time_label="NOW",
                    time=sorted_items[0].start_time,
                    title=sorted_items[0].description,
                    location=sorted_items[0].location or "TBD",
                    status="ACTIVE"
                ))
            if len(sorted_items) > 1:
                timeline.append(TimelineEvent(
                    id=sorted_items[1].id,
                    time_label="NEXT",
                    time=sorted_items[1].start_time,
                    title=sorted_items[1].description,
                    location=sorted_items[1].location or "TBD",
                    status="UPCOMING"
                ))
                # Generate next action based on NEXT item
                next_action = NextAction(
                    title="Upcoming Activity",
                    description=f"Your next activity is {sorted_items[1].description} at {sorted_items[1].start_time.strftime('%H:%M')}. *Estimated travel time: 20 mins*",
                    action_type="TRAVEL"
                )
            if len(sorted_items) > 2:
                for i in range(2, min(5, len(sorted_items))):
                    timeline.append(TimelineEvent(
                        id=sorted_items[i].id,
                        time_label="LATER",
                        time=sorted_items[i].start_time,
                        title=sorted_items[i].description,
                        location=sorted_items[i].location or "TBD",
                        status="UPCOMING"
                    ))
        
        # Alerts
        alerts = []
        bookings = db.query(Booking).filter(Booking.trip_id == trip.id).all()
        pending = [b for b in bookings if b.status != 'CONFIRMED']
        if pending:
            alerts.append(LiveAlert(
                id="ALERT-B",
                severity="WARNING",
                message=f"{len(pending)} bookings are pending or incomplete."
            ))
            
        # Summaries
        conf_count = len([b for b in bookings if b.status == 'CONFIRMED'])
        book_sum = f"{conf_count}/{len(bookings) if bookings else 0} Confirmed"
        
        return LiveTripStatus(
            trip_id=trip.id,
            status_label=status_label,
            day_label=day_label,
            timeline=timeline,
            next_action=next_action,
            alerts=alerts,
            bookings_summary=book_sum,
            prep_summary="0/3 Complete" # Placeholder
        )

    @staticmethod
    def handle_assistant_request(db: Session, trip_id: int, message: str) -> AssistantResponse:
        from app.services.scope_guard import ScopeGuard
        from app.services.openrouter_client import get_openrouter_client, get_system_prompt
        import json

        # 1. Scope Guard Check
        if not ScopeGuard.check_relevance(message):
            return AssistantResponse(
                response=f"**[SCOPE REJECTED]**\n{ScopeGuard.get_rejection_message()}",
                intent_detected="IRRELEVANT",
                data_used={}
            )

        client, model = get_openrouter_client()
        intent = "UNKNOWN"
        msg_lower = message.lower()
        
        if "next" in msg_lower or "after" in msg_lower:
            intent = "GET_NEXT_ACTIVITY"
        elif "today" in msg_lower:
            intent = "GET_TODAY"
        elif "booking" in msg_lower:
            intent = "GET_BOOKINGS"
        elif "status" in msg_lower or "active" in msg_lower:
            intent = "GET_TRIP_STATUS"
        elif "prep" in msg_lower or "ready" in msg_lower:
            intent = "GET_PREPARATION"
            
        # Get Deterministic Backend Result
        trip_status = LiveTripService.get_live_status(db, trip_id)
        
        data_used = {}
        if intent == "GET_NEXT_ACTIVITY":
            next_event = next((e for e in trip_status.timeline if e.time_label == "NEXT"), None)
            data_used = {"next_activity": next_event.dict() if next_event else None}
        elif intent == "GET_TODAY":
            data_used = {"timeline": [e.dict() for e in trip_status.timeline]}
        elif intent == "GET_TRIP_STATUS":
            data_used = {"status": trip_status.status_label, "day": trip_status.day_label}
        else:
            data_used = {"raw_status": "Available"}

        if client:
            try:
                system_prompt = get_system_prompt()
                context_str = json.dumps(data_used, indent=2)
                
                prompt = f"""
Context from backend for this trip:
{context_str}

User question: {message}

Please answer the user's question concisely using the context provided. Do not invent any facts, prices, or itinerary details outside the context.
"""
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300
                )
                response_text = response.choices[0].message.content.strip()
                final_response = f"**[AI GENERATED]**\nIntent: {intent}\n\n**[AI EXPLANATION]**\n{response_text}"
                return AssistantResponse(
                    response=final_response,
                    intent_detected=intent,
                    data_used=data_used
                )
            except Exception as e:
                print(f"OpenRouter LLM failed: {e}. Falling back to deterministic.")
                # Fall through to fallback
        
        # Fallback formulation
        response_text = ""
        if intent == "GET_NEXT_ACTIVITY":
            evt = data_used.get("next_activity")
            if evt:
                response_text = f"Your next planned activity is {evt['title']} at {evt['location']}. Please check your estimated travel time to ensure you arrive on time."
            else:
                response_text = "You have no upcoming activities scheduled."
        elif intent == "GET_TODAY":
            response_text = "Here is your timeline for today: " + ", ".join([f"{e['title']} ({e['time_label']})" for e in data_used['timeline']])
        elif intent == "GET_TRIP_STATUS":
            response_text = f"Your trip is currently {data_used['status']}. {data_used['day']}."
        else:
            response_text = "I'm your live trip assistant. I can tell you about your next activity, today's schedule, or your trip status."

        final_response = f"**[DEMO FALLBACK]**\nIntent: {intent}\n\n**[ASSISTANT EXPLANATION]**\n{response_text}"
        
        return AssistantResponse(
            response=final_response,
            intent_detected=intent,
            data_used=data_used
        )
