import re

class ScopeGuard:
    # Allowed categories
    ALLOWED_CATEGORIES = [
        "TRAVEL", "ITINERARY", "DESTINATION", "FLIGHT", "HOTEL", 
        "ACTIVITY", "TRANSPORT", "WEATHER_TRAVEL", "BUDGET", 
        "COST_OPTIMIZATION", "DISRUPTION", "REOPTIMIZATION", 
        "BOOKING", "LIVE_TRIP", "OPERATOR", "PROJECT", "TECHNICAL_PROJECT"
    ]
    
    # Simple deterministic classification using keywords
    TRAVEL_KEYWORDS = [
        "trip", "travel", "itinerary", "destination", "flight", "hotel", 
        "activity", "transport", "weather", "budget", "cost", "optimize",
        "disruption", "book", "live", "operator", "tour", "vacation", 
        "holiday", "save", "price", "delay", "cancel", "schedule", "plan",
        "kyoto", "bali", "paris", "tokyo", "recommend"
    ]
    
    PROJECT_KEYWORDS = [
        "project", "architecture", "ingestion", "pipeline", "optimizer",
        "engine", "amadeus", "open-meteo", "osrm", "freshness",
        "canonical", "fallback", "demo", "test", "live",
        "control tower", "explain", "how does", "why did"
    ]
    
    IRRELEVANT_PATTERNS = [
        r"capital of\b", r"\bmath\b", r"\d+\s*[\+\-\*[Xx]/]\s*\d+", r"cricket", 
        r"football", r"joke", r"photosynthesis", r"meaning of life", 
        r"generic", r"python game", r"write a.*script", r"write me a.*"
    ]

    @classmethod
    def classify(cls, message: str) -> str:
        msg_lower = message.lower()
        
        # Immediate rejection of known irrelevant patterns
        for pattern in cls.IRRELEVANT_PATTERNS:
            if re.search(pattern, msg_lower):
                return "IRRELEVANT"
                
        # Check for travel/project relevance
        is_relevant = False
        
        for kw in cls.TRAVEL_KEYWORDS:
            if kw in msg_lower:
                is_relevant = True
                break
                
        if not is_relevant:
            for kw in cls.PROJECT_KEYWORDS:
                if kw in msg_lower:
                    is_relevant = True
                    break
        
        if not is_relevant:
            return "IRRELEVANT"
            
        return "RELEVANT" # We can just map to RELEVANT for the gate

    @classmethod
    def check_relevance(cls, message: str) -> bool:
        category = cls.classify(message)
        return category != "IRRELEVANT"
        
    @classmethod
    def get_rejection_message(cls) -> str:
        return "I’m focused on travel planning, trip optimization, tour operations, and questions about this project. Please ask a relevant travel or project-related question."
