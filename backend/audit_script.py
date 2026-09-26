import os
import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models.ingestion_models import FlightOffer, HotelOffer, ActivityOffer, WeatherForecast, DataSource, IngestionRun
from app.models.core_models import Trip, ItineraryItem
from app.db.base import Base

def audit():
    engine = create_engine("sqlite:///tour_ops.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    print("=== ENVIRONMENT VARIABLES ===")
    keys = ["OPENAI_API_KEY", "AMADEUS_CLIENT_ID", "AMADEUS_CLIENT_SECRET", "AMADEUS_API_KEY"]
    for k in keys:
        val = os.getenv(k)
        print(f"{k}: {'YES' if val else 'NO'}")

    print("\n=== DATABASE PROVENANCE ===")
    for model, name in [(FlightOffer, 'FlightOffer'), (HotelOffer, 'HotelOffer'), (ActivityOffer, 'ActivityOffer'), (WeatherForecast, 'WeatherForecast')]:
        try:
            records = session.query(model).all()
            sources = {}
            modes = {}
            for r in records:
                # get source/provider if exists
                provider = getattr(r, 'provider', None)
                if not provider:
                    provider = getattr(r, 'source', None)
                
                # try to get mode from DataSource if we can, else if it has mode
                # but models themselves have freshness_status which indicates fallback or fresh
                freshness = getattr(r, 'freshness_status', 'UNKNOWN')
                
                sources[provider] = sources.get(provider, 0) + 1
                modes[freshness] = modes.get(freshness, 0) + 1
                
            print(f"Table {name}: Total {len(records)}")
            print(f"  Providers: {sources}")
            print(f"  Freshness/Mode: {modes}")
        except Exception as e:
            print(f"Table {name} error: {e}")

    try:
        ds = session.query(DataSource).all()
        print("\n=== DATA SOURCES ===")
        for d in ds:
            print(f"Provider: {d.provider_name}, Type: {d.provider_type}, Mode: {d.mode}, Status: {d.status}")
    except Exception as e:
        print(f"DataSource error: {e}")

    try:
        runs = session.query(IngestionRun).all()
        print("\n=== INGESTION RUNS ===")
        print(f"Total runs: {len(runs)}")
        for r in runs[:5]:
            print(f"Provider: {r.provider}, Status: {r.status}, Mode: {r.mode}")
    except Exception as e:
        print(f"IngestionRun error: {e}")
        
    try:
        items = session.query(ItineraryItem).all()
        print("\n=== ITINERARY ITEMS (OPTIMIZER USAGE) ===")
        sources = {}
        for item in items:
            rs = item.ai_reasoning or ""
            if "fallback" in rs.lower():
                sources['FALLBACK'] = sources.get('FALLBACK', 0) + 1
            else:
                sources['OTHER'] = sources.get('OTHER', 0) + 1
        print(f"Sources based on reasoning: {sources}")
    except Exception as e:
        print(f"ItineraryItem error: {e}")

if __name__ == "__main__":
    audit()
