import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def append_to_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip() + "\n")

def replace_in_file(path, old, new):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if old not in content:
        print(f"Warning: '{old}' not found in {path}")
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# 1. Update core_models.py
replace_in_file("backend/app/models/core_models.py",
                "is_active = Column(Boolean, default=True)",
                "is_active = Column(Boolean, default=True)\n    generation_method = Column(String, default='DEMO FALLBACK')")

# 2. Update schemas/itinerary.py
replace_in_file("backend/app/schemas/itinerary.py",
                "is_active: bool",
                "is_active: bool\n    generation_method: str = 'DEMO FALLBACK'")

# 3. Rewrite itinerary_planner.py completely
planner_code = """
import os
import json
from sqlalchemy.orm import Session
from app.models.core_models import Trip, Itinerary, ItineraryItem, Experience, Destination
from app.services.itinerary_validator import ItineraryValidator
from app.schemas.itinerary import ItineraryItemBase
from datetime import datetime, timedelta
import random

try:
    import openai
    # Assuming API key is set in environment or passed somehow.
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    HAS_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    HAS_OPENAI = False

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

        if HAS_OPENAI:
            try:
                items_payload = ItineraryPlanner._generate_with_llm(trip, prefs, experiences, start_date)
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
    def _generate_with_llm(trip, prefs, experiences, start_date):
        # Build context
        context = {
            "duration": prefs.get("duration", 3),
            "budget": prefs.get("budget", 5000),
            "interests": prefs.get("interests", []),
            "travel_style": prefs.get("travel_style", ""),
            "selected_experiences": [{"name": e.name, "category": e.category, "price": e.price_estimate, "duration": e.duration} for e in experiences]
        }
        
        prompt = f\"\"\"
You are an expert AI travel planner. Create a day-by-day itinerary based on the following context:
{json.dumps(context, indent=2)}

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
        \"\"\"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        raw_items = json.loads(content)
        
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
"""
create_file("backend/app/services/itinerary_planner.py", planner_code)

# 4. Fix frontend PlanPage to show the truth
replace_in_file("frontend/src/app/(traveler)/trips/[id]/plan/page.tsx",
                'const genSteps = [\n    "Understanding your Travel DNA...",\n    "Finding candidate experiences...",\n    "Optimizing schedule and pacing...",\n    "Checking travel times & constraints...",\n    "Validating deterministic rules..."\n  ];',
                'const genSteps = [\n    "Understanding your preferences...",\n    "Finding candidate experiences...",\n    "Building itinerary...",\n    "Validating schedule constraints...",\n    "Checking budget bounds...",\n    "Finalizing version..."\n  ];')

replace_in_file("frontend/src/app/(traveler)/trips/[id]/plan/page.tsx",
                '<Badge variant="outline" className="mb-4 bg-primary/10 border-primary/20 text-primary">\n                AI Planner Engine\n              </Badge>',
                '<Badge variant="outline" className={`mb-4 border-primary/20 ${itinerary?.generation_method === "AI GENERATED" ? "bg-green-500/10 text-green-500 border-green-500/20" : "bg-primary/10 text-primary"}`}>\n                {itinerary?.generation_method || "AI Planner Engine"}\n              </Badge>')

print("Backend and Frontend files updated for Prompt 5.1.")
