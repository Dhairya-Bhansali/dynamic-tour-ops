from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.services.ingestion.service import IngestionService
from app.models.ingestion_models import IngestionRun, DataSource

router = APIRouter()

@router.get("/health", response_model=Dict[str, Any])
def get_ingestion_health(db: Session = Depends(get_db), env: str = Query("DEMO")):
    service = IngestionService(db, env=env)
    sources = service.get_data_sources_status()
    
    healthy = len([s for s in sources if s["status"] == "HEALTHY"])
    degraded = len([s for s in sources if s["status"] in ["DEGRADED", "STALE", "ERROR"]])
    
    # Calculate fresh/stale records globally if we want, or just sum it from sources
    # Actually, we didn't populate fresh_records count deeply, but we can do a simple sum.
    # For now, let's just return what we have
    return {
        "providers_healthy": healthy,
        "providers_degraded": degraded,
        "sources": sources
    }

@router.get("/sources", response_model=List[Dict[str, Any]])
def get_ingestion_sources(db: Session = Depends(get_db), env: str = Query("DEMO")):
    service = IngestionService(db, env=env)
    return service.get_data_sources_status()

@router.get("/runs", response_model=List[Dict[str, Any]])
def get_ingestion_runs(db: Session = Depends(get_db), limit: int = 100):
    runs = db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit).all()
    return [
        {
            "run_id": r.run_id,
            "provider": r.provider,
            "dataset_type": r.dataset_type,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "duration": r.duration,
            "status": r.status,
            "records_received": r.records_received,
            "records_inserted": r.records_inserted,
            "records_updated": r.records_updated,
            "records_rejected": r.records_rejected,
            "error_message": r.error_message
        } for r in runs
    ]

@router.get("/runs/{run_id}", response_model=Dict[str, Any])
def get_ingestion_run(run_id: str, db: Session = Depends(get_db)):
    r = db.query(IngestionRun).filter(IngestionRun.run_id == run_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "run_id": r.run_id,
        "provider": r.provider,
        "dataset_type": r.dataset_type,
        "started_at": r.started_at.isoformat() if r.started_at else None,
        "completed_at": r.completed_at.isoformat() if r.completed_at else None,
        "duration": r.duration,
        "status": r.status,
        "records_received": r.records_received,
        "records_inserted": r.records_inserted,
        "records_updated": r.records_updated,
        "records_rejected": r.records_rejected,
        "error_message": r.error_message
    }

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

@router.post("/sync/hotels")
def sync_hotels(
    location: str = Query(...), 
    check_in: str = Query(...), 
    check_out: str = Query(...),
    env: str = Query("DEMO"),
    db: Session = Depends(get_db)
):
    service = IngestionService(db, env=env)
    offers = service.sync_hotels(location, check_in, check_out)
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
