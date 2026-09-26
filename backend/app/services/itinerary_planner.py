import os
import json
from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, ItineraryItem, Experience, Destination
from app.services.itinerary_validator import ItineraryValidator
from app.schemas.itinerary import ItineraryItemBase
from datetime import datetime, timedelta
import random

from app.services.openrouter_client import get_openrouter_client

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
        
        start_date_str = prefs.get("start_date", datetime.utcnow().strftime("%Y-%m-%d"))
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        
        experiences = db.query(Experience).filter(Experience.id.in_(selected_exp_ids)).all() if selected_exp_ids else []
        
        items_payload = []
        generation_method = "DEMO FALLBACK"

        destination = db.query(Destination).filter(Destination.id == trip.destination_id).first()
        destination_name = destination.name if destination else "the destination"

        client, model = get_openrouter_client()
        if client:
            try:
                items_payload = ItineraryPlanner._generate_with_llm(client, model, trip, prefs, experiences, start_date, destination_name)
                generation_method = "AI GENERATED"
            except Exception as e:
                print(f"LLM generation failed: {e}. Falling back to deterministic planner.")
                items_payload = ItineraryPlanner._generate_deterministic(duration, experiences, start_date)
        else:
            items_payload = ItineraryPlanner._generate_deterministic(duration, experiences, start_date)
            
        # Validate deterministic plan
        validation_res = ItineraryValidator.validate_plan(items_payload, budget)
        
        # We save even if it has warnings, but maybe in a real app we'd reject errors. 
        # For hackathon, we persist and show errors in UI.
        new_itinerary = Itinerary(
            trip_id=trip_id, 
            version=new_version_num, 
            is_active=True,
            generation_method=generation_method
        )
        db.add(new_itinerary)
        db.flush()
        
        # Deactivate old versions
        db.query(Itinerary).filter(Itinerary.trip_id == trip_id, Itinerary.id != new_itinerary.id).update({"is_active": False})
        
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

    @staticmethod
    def _generate_with_llm(client, model, trip, prefs, experiences, start_date, destination_name="the destination"):
        from app.services.openrouter_client import get_system_prompt
        import re
        
        # 1. Normalize sparse inputs
        interests = prefs.get("interests", [])
        if not interests:
            interests = ["balanced general travel interests"]
            
        travel_style = prefs.get("travel_style", "")
        if not travel_style:
            travel_style = "balanced"
            
        selected_experiences = [{"name": e.name, "category": e.category, "price": e.price_estimate, "duration": e.duration} for e in experiences]
        if not selected_experiences:
            selected_experiences = ["representative destination experiences"]
            
        # Build context
        context = {
            "destination": destination_name,
            "duration": prefs.get("duration", 3),
            "budget": prefs.get("budget", 5000),
            "interests": interests,
            "travel_style": travel_style,
            "selected_experiences": selected_experiences
        }
        
        system_prompt = get_system_prompt()
        prompt = f"""
You are an expert AI travel planner. Create a day-by-day itinerary based on the following context:
{json.dumps(context, indent=2)}

CRITICAL INSTRUCTIONS:
- The traveler may not have specified all preferences. If optional preferences are empty or generic (like "balanced"), choose sensible defaults appropriate for {destination_name}.
- Do not ask the user for more information. Generate the itinerary using the available information.
- Always generate the requested itinerary.
- Never respond with a clarification question or an apology.
- Never say that more information is required.
- Return ONLY valid JSON matching the expected itinerary schema.
- Do not invent live availability, live prices, bookings, weather, or provider data.
- Clearly distinguish recommendations from verified provider data.

You MUST output ONLY valid JSON matching this schema exactly (a list of objects):
[
  {{
    "day_number": int,
    "start_time": "YYYY-MM-DDTHH:MM:SS", (ensure dates start at {start_date.strftime("%Y-%m-%d")})
    "end_time": "YYYY-MM-DDTHH:MM:SS",
    "activity_type": str,
    "description": str,
    "location": str,
    "estimated_cost": float,
    "ai_reasoning": str,
    "confidence_score": float (0.0 to 1.0)
  }}
]
Include the selected experiences in your plan logically. Make sure times do not overlap.
"""

        def extract_and_parse_json(text):
            # Safe structured-response extraction layer
            text = text.strip()
            # Try to find JSON block using regex if markdown fences are used
            match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
            if match:
                text = match.group(1).strip()
            else:
                # Try to find first [ and last ]
                start = text.find('[')
                end = text.rfind(']')
                if start != -1 and end != -1:
                    text = text[start:end+1]
            return json.loads(text)

        # First attempt
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=15000
        )
        
        content = response.choices[0].message.content
        
        try:
            raw_items = extract_and_parse_json(content)
        except Exception as e:
            # Retry exactly once
            retry_prompt = "Return ONLY the JSON object matching the required schema. Do not include explanations or conversational text."
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": content},
                    {"role": "user", "content": retry_prompt}
                ],
                temperature=0.7,
                max_tokens=15000
            )
            content = response.choices[0].message.content
            raw_items = extract_and_parse_json(content)

        # Validate through Pydantic
        validated_items = []
        for raw in raw_items:
            # We add day_date based on start_time
            dt = datetime.fromisoformat(raw["start_time"].replace("Z", ""))
            raw["day_date"] = dt
            raw["start_time"] = dt
            raw["end_time"] = datetime.fromisoformat(raw["end_time"].replace("Z", ""))
            validated = ItineraryItemBase(**raw)
            validated_items.append(validated.model_dump())
            
        return validated_items

    @staticmethod
    def _generate_deterministic(duration, experiences, start_date):
        items_payload = []
        current_exp_idx = 0
        for day in range(1, duration + 1):
            current_date = start_date + timedelta(days=day-1)
            
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
        return items_payload
