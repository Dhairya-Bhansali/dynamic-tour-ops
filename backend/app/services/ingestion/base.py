import httpx
import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.ingestion_models import RawProviderResponse, DataSource

class BaseConnector:
    """Base class for all provider connectors."""
    
    provider_name: str
    base_url: str

    def __init__(self, db: Session, env: str = "DEMO"):
        self.db = db
        self.env = env
        self.client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def fetch(self, endpoint: str, params: Optional[Dict] = None, method: str = "GET", headers: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Fetch data from the provider or use DEMO/TEST mock."""
        if self.env == "DEMO":
            return self.get_demo_data(endpoint, params)

        try:
            response = self.client.request(method, endpoint, params=params, headers=headers, **kwargs)
            response.raise_for_status()
            data = response.json()
            self._log_raw_response(endpoint, params, response.status_code, data, True, None)
            return data
        except httpx.HTTPError as e:
            error_msg = str(e)
            status_code = e.response.status_code if hasattr(e, 'response') and e.response else 500
            self._log_raw_response(endpoint, params, status_code, None, False, error_msg)
            raise e
        except Exception as e:
            self._log_raw_response(endpoint, params, 500, None, False, str(e))
            raise e

    def _log_raw_response(self, endpoint: str, params: Optional[Dict], status_code: int, 
                          payload: Any, success: bool, error_info: Optional[str]):
        """Store the raw provider response."""
        param_str = json.dumps(params, sort_keys=True) if params else ""
        request_hash_input = f"{self.provider_name}:{endpoint}:{param_str}"
        request_hash = hashlib.md5(request_hash_input.encode()).hexdigest()

        raw_record = RawProviderResponse(
            provider=self.provider_name,
            endpoint=endpoint,
            request_hash=request_hash,
            status_code=status_code,
            payload=payload,
            success=success,
            error_info=error_info
        )
        self.db.add(raw_record)
        self.db.commit()

    def get_demo_data(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Override to provide fallback demo data when LIVE is not requested or available."""
        return {}

    def fetch_flight_offers(self, origin: str, destination: str, date: str) -> List[Dict]:
        raise NotImplementedError

    def fetch_hotel_offers(self, location: str, check_in: str, check_out: str) -> List[Dict]:
        raise NotImplementedError

    def fetch_weather(self, lat: float, lng: float, date: str) -> Dict:
        raise NotImplementedError

    def fetch_route(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict:
        raise NotImplementedError

    def search_places(self, query: str, lat: float, lng: float) -> List[Dict]:
        raise NotImplementedError
