from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.db.session import engine
from app.db.base import Base
# Import all models to ensure they are registered with Base
from app.models import core_models
from app.models import ingestion_models

# Create tables for demo
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NexTour API", description="Dynamic Tour Operations Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        return {"status": "ok", "version": "1.0.0", "database": "connected"}
    except Exception as e:
        return {"status": "error", "version": "1.0.0", "database": "disconnected", "error": str(e)}
