from typing import Dict, List, Optional
import random
from app.services.ingestion.base import BaseConnector

class OpenMeteoConnector(BaseConnector):
    provider_name = "OpenMeteo"
    base_url = "https://api.open-meteo.com"

    def get_demo_data(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        return {
            "latitude": params.get("latitude", 0),
            "longitude": params.get("longitude", 0),
            "daily": {
                "time": ["2023-10-01", "2023-10-02"],
                "temperature_2m_max": [random.uniform(15, 30), random.uniform(15, 30)],
                "precipitation_probability_max": [random.uniform(0, 100), random.uniform(0, 100)],
                "weathercode": [1, 2]
            }
        }

    def fetch_weather(self, lat: float, lng: float, date: str) -> Dict:
        # NOTE: For historical/forecast, open-meteo takes date ranges. We'll simplify to fetching forecast.
        endpoint = "/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lng,
            "daily": "temperature_2m_max,precipitation_probability_max,weathercode",
            "timezone": "auto"
        }
        # In real life we'd filter by date after fetching or pass start/end date
        data = self.fetch(endpoint, params)
        return data
