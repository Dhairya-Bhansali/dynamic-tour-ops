from typing import Dict, List, Optional
import random
from app.services.ingestion.base import BaseConnector

class OSRMConnector(BaseConnector):
    provider_name = "OSRM"
    base_url = "http://router.project-osrm.org"

    def get_demo_data(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        return {
            "routes": [
                {
                    "distance": random.uniform(10000, 500000), # meters
                    "duration": random.uniform(3600, 14400), # seconds
                    "geometry": "mock_polyline"
                }
            ]
        }

    def fetch_route(self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> Dict:
        # OSRM format: /route/v1/driving/{lon},{lat};{lon},{lat}
        endpoint = f"/route/v1/driving/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        params = {
            "overview": "simplified"
        }
        data = self.fetch(endpoint, params)
        return data
