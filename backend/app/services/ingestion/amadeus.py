import os
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
from app.services.ingestion.base import BaseConnector

class AmadeusConnector(BaseConnector):
    provider_name = "Amadeus"
    base_url = "https://test.api.amadeus.com" # Test API URL for now

    def __init__(self, db, env: str = "DEMO"):
        super().__init__(db, env)
        self.client_id = os.getenv("AMADEUS_CLIENT_ID")
        self.client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
        self._access_token = None
        self._token_expires_at = 0

    def _get_access_token(self) -> str:
        if self.env == "DEMO":
            return "demo_token"

        if not self.client_id or not self.client_secret:
            raise ValueError("Amadeus credentials are not configured.")

        # Check if token is still valid (with a 30 sec buffer)
        if self._access_token and time.time() < self._token_expires_at - 30:
            return self._access_token

        # Fetch new token
        endpoint = "/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            response = self.client.post(endpoint, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            self._access_token = token_data["access_token"]
            self._token_expires_at = time.time() + token_data.get("expires_in", 1799)
            return self._access_token
        except Exception as e:
            raise RuntimeError(f"Amadeus OAuth failed: {str(e)}")

    def get_demo_data(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Provide realistic mock data for flights and hotels."""
        if "flight-offers" in endpoint:
            origin = params.get("originLocationCode", "JFK")
            destination = params.get("destinationLocationCode", "LHR")
            return {
                "data": [
                    {
                        "id": f"demo_flight_{hash(origin + destination) % 10000}",
                        "itineraries": [{"duration": "PT7H30M", "segments": [{"numberOfStops": 0, "carrierCode": "BA"}]}],
                        "price": {"total": str(random.uniform(300, 1500)), "currency": "USD"},
                        "validatingAirlineCodes": ["BA"]
                    }
                ]
            }
        elif "hotel-offers" in endpoint:
            return {
                "data": [
                    {
                        "hotel": {"hotelId": f"demo_hotel_{random.randint(100,999)}", "name": "Grand Demo Hotel", "rating": "4"},
                        "offers": [{"price": {"total": str(random.uniform(100, 500)), "currency": "USD"}, "policies": {"cancellations": [{"description": "Free cancellation"}]}}]
                    }
                ]
            }
        return {"data": []}

    def fetch_flight_offers(self, origin: str, destination: str, date: str) -> List[Dict]:
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"} if token != "demo_token" else None
        endpoint = "/v2/shopping/flight-offers"
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": date,
            "adults": 1,
            "max": 5
        }
        data = self.fetch(endpoint, params, headers=headers)
        return data.get("data", [])

    def fetch_hotel_offers(self, location: str, check_in: str, check_out: str) -> List[Dict]:
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"} if token != "demo_token" else None
        endpoint = "/v3/shopping/hotel-offers"
        params = {
            "cityCode": location,
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "adults": 1,
            "bestRateOnly": "true"
        }
        data = self.fetch(endpoint, params, headers=headers)
        return data.get("data", [])
