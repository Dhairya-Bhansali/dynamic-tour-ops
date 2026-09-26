from abc import ABC, abstractmethod
import random
import uuid

class BookingProvider(ABC):
    @abstractmethod
    def check_availability(self, item) -> dict:
        pass
        
    @abstractmethod
    def create_booking(self, item) -> dict:
        pass

class DemoBookingProvider(BookingProvider):
    def check_availability(self, item) -> dict:
        # Simulate availability check logic based on item type or cost
        is_available = random.choice([True, True, True, False]) # 75% chance available in demo
        if not is_available:
            return {
                "available": False,
                "reason": f"Selected {item.activity_type} is fully booked on these dates.",
                "price": item.estimated_cost,
                "provider_id": "DEMO_PROVIDER"
            }
        return {
            "available": True,
            "reason": None,
            "price": item.estimated_cost,
            "provider_id": "DEMO_PROVIDER"
        }
        
    def create_booking(self, item) -> dict:
        code = f"DEMO-{uuid.uuid4().hex[:6].upper()}"
        return {
            "status": "CONFIRMED",
            "confirmation_code": code,
            "provider_reference": f"REF-{code}",
            "source_type": "DEMO"
        }
