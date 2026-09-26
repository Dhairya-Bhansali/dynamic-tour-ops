from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.ingestion_models import DataSource

class FreshnessEngine:
    """Centralized freshness evaluation rules."""
    
    THRESHOLDS = {
        "flights": timedelta(minutes=30),
        "hotels": timedelta(minutes=120),
        "weather": timedelta(minutes=60),
        "places": timedelta(days=7),
        "routes": timedelta(days=1),
        "activities": timedelta(hours=24)
    }

    @classmethod
    def get_threshold(cls, data_type: str) -> timedelta:
        return cls.THRESHOLDS.get(data_type, timedelta(hours=24))

    @classmethod
    def evaluate_freshness(cls, data_type: str, fetched_at: datetime, now: Optional[datetime] = None) -> str:
        if not now:
            now = datetime.utcnow()
        threshold = cls.get_threshold(data_type)
        if (now - fetched_at) > threshold:
            return "STALE"
        return "FRESH"

    @classmethod
    def update_datasource_health(cls, db: Session, ds: DataSource, error: Optional[str] = None):
        """Deterministically evaluates and updates a DataSource's health status."""
        now = datetime.utcnow()
        if not ds.enabled:
            ds.status = "DISABLED"
            return
            
        if error or ds.error_count > 0:
            ds.status = "ERROR"
            if error:
                ds.error_count += 1
                # ds.last_error = error
                # ds.last_failure_at = now
            return

        if not ds.last_successful_sync:
            ds.status = "DEGRADED"
            return
            
        # Check staleness
        threshold = cls.get_threshold(ds.provider_type)
        if (now - ds.last_successful_sync) > threshold:
            ds.status = "STALE"
            ds.freshness_status = "STALE"
        else:
            ds.status = "HEALTHY"
            ds.freshness_status = "FRESH"
