from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.db.session import engine
from app.db.base import Base
# Import all models to ensure they are registered with Base
from app.models import core_models

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
def health_check():
    return {"status": "ok", "version": "1.0.0"}
