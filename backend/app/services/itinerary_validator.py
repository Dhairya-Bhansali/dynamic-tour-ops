from typing import List

class ItineraryValidator:
    @staticmethod
    def validate_plan(items: List[dict], trip_budget: float) -> dict:
        errors = []
        warnings = []
        
        # 1. Budget check
        total_cost = sum(item.get('estimated_cost', 0) for item in items)
        if total_cost > trip_budget * 1.2:
            errors.append(f"Itinerary cost (${total_cost}) significantly exceeds budget (${trip_budget}).")
        elif total_cost > trip_budget:
            warnings.append(f"Itinerary cost (${total_cost}) slightly exceeds budget (${trip_budget}).")
            
        # 2. Time conflict check (basic)
        # Assuming items are sorted by start_time
        for i in range(len(items) - 1):
            if items[i].get('end_time') and items[i+1].get('start_time'):
                if items[i]['end_time'] > items[i+1]['start_time']:
                    errors.append(f"Time conflict detected between '{items[i]['description']}' and '{items[i+1]['description']}'.")
                    
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
