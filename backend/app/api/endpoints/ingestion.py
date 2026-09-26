from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.services.ingestion.service import IngestionService

router = APIRouter()

@router.get("/status", response_model=List[Dict[str, Any]])
def get_ingestion_status(db: Session = Depends(get_db), env: str = Query("DEMO")):
    service = IngestionService(db, env=env)
    return service.get_data_sources_status()

@router.post("/sync/flights")
def sync_flights(
    origin: str = Query(...), 
    destination: str = Query(...), 
    date: str = Query(...),
    env: str = Query("DEMO"),
    db: Session = Depends(get_db)
):
    service = IngestionService(db, env=env)
    offers = service.sync_flights(origin, destination, date)
    return {"status": "success", "count": len(offers), "environment": env}

@router.post("/sync/weather")
def sync_weather(
    lat: float = Query(...), 
    lng: float = Query(...), 
    location_name: str = Query(...),
    env: str = Query("DEMO"),
    db: Session = Depends(get_db)
):
    service = IngestionService(db, env=env)
    weather = service.sync_weather(lat, lng, location_name)
    return {"status": "success", "environment": env, "temperature": weather.temperature}
