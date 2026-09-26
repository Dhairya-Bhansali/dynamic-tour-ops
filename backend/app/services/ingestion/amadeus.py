from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random
from app.services.ingestion.base import BaseConnector

class AmadeusConnector(BaseConnector):
    provider_name = "Amadeus"
    base_url = "https://test.api.amadeus.com" # Test API URL for now

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
        endpoint = "/v2/shopping/flight-offers"
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": date,
            "adults": 1,
            "max": 5
        }
        data = self.fetch(endpoint, params)
        return data.get("data", [])

    def fetch_hotel_offers(self, location: str, check_in: str, check_out: str) -> List[Dict]:
        endpoint = "/v3/shopping/hotel-offers"
        # Mock mapping location to city code
        params = {
            "cityCode": location,
            "checkInDate": check_in,
            "checkOutDate": check_out,
            "adults": 1,
            "bestRateOnly": "true"
        }
        data = self.fetch(endpoint, params)
        return data.get("data", [])
