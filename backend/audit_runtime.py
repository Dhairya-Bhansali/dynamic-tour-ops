import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.ingestion.open_meteo import OpenMeteoConnector
from app.services.ingestion.osm import OSRMConnector
from app.services.ingestion.amadeus import AmadeusConnector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def audit():
    print("--- ENV CHECK ---")
    openai_key = os.getenv("OPENAI_API_KEY")
    amadeus_id = os.getenv("AMADEUS_CLIENT_ID")
    amadeus_secret = os.getenv("AMADEUS_CLIENT_SECRET")
    
    print(f"OPENAI_API_KEY: {'PRESENT' if openai_key else 'MISSING'}")
    print(f"AMADEUS_CLIENT_ID: {'PRESENT' if amadeus_id else 'MISSING'}")
    print(f"AMADEUS_CLIENT_SECRET: {'PRESENT' if amadeus_secret else 'MISSING'}")
    
    print("\n--- EXTERNAL CONNECTIVITY ---")
    
    engine = create_engine("sqlite:///tour_ops.db")
    Session = sessionmaker(bind=engine)
    db = Session()
    
    # Open-Meteo LIVE test
    try:
        om = OpenMeteoConnector(db, env="LIVE")
        om_res = om.fetch_weather(52.52, 13.41, "today")
        if om_res and "daily" in om_res:
            print("OPEN_METEO: SUCCESS")
        else:
            print("OPEN_METEO: FAILED (Malformed)")
    except Exception as e:
        print(f"OPEN_METEO: FAILED ({e})")
        
    # OSRM LIVE test
    try:
        osrm = OSRMConnector(db, env="LIVE")
        osrm_res = osrm.fetch_route(52.51, 13.43, 52.52, 13.41)
        if osrm_res and "routes" in osrm_res:
            print("OSRM: SUCCESS")
        else:
            print("OSRM: FAILED (Malformed)")
    except Exception as e:
        print(f"OSRM: FAILED ({e})")
        
    # Amadeus LIVE test
    if amadeus_id and amadeus_secret:
        try:
            am = AmadeusConnector(db, env="LIVE")
            # Minimal flight test
            flight = am.fetch_flight_offers("JFK", "LHR", "2026-12-01")
            print(f"AMADEUS FLIGHT: SUCCESS (Found {len(flight)} records)")
        except Exception as e:
            print(f"AMADEUS FLIGHT: FAILED ({e})")
    else:
        print("AMADEUS FLIGHT: NOT EXECUTED (Missing Credentials)")

    # OpenRouter LIVE test
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        try:
            import openai
            from app.services.scope_guard import ScopeGuard
            
            # Test 1: Allowed Question
            q1 = "Plan a 5-day Kyoto trip under $5000."
            if not ScopeGuard.check_relevance(q1):
                print("OPENROUTER TEST 1: FAILED (Rejected allowed question)")
            else:
                client = openai.OpenAI(
                    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                    api_key=openrouter_key
                )
                model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": 'Return a JSON object with exactly: {"status": "ok"}'}],
                    max_tokens=50
                )
                print(f"OPENROUTER: SUCCESS ({model}, {resp.choices[0].message.content.strip()})")
                
            # Test 2: Project Question
            q2 = "Explain how the cost optimization engine works."
            if not ScopeGuard.check_relevance(q2):
                print("OPENROUTER TEST 2: FAILED (Rejected project question)")
            else:
                print("OPENROUTER TEST 2: SUCCESS (Allowed project question)")
                
            # Test 3: Unrelated Question
            q3 = "What is the capital of India?"
            if ScopeGuard.check_relevance(q3):
                print("OPENROUTER TEST 3: FAILED (Allowed unrelated question)")
            else:
                print("OPENROUTER TEST 3: SUCCESS (Rejected unrelated question)")

        except Exception as e:
            print(f"OPENROUTER: FAILED ({e})")
    else:
        print("OPENROUTER: NOT EXECUTED (Missing Credentials)")

if __name__ == "__main__":
    audit()
