import pytest
from app.services.scope_guard import ScopeGuard
from unittest.mock import patch, MagicMock

def test_scope_guard_allowed():
    assert ScopeGuard.check_relevance("Plan a 5-day Kyoto trip under $5000.") == True
    assert ScopeGuard.check_relevance("Why did my trip cost increase?") == True
    assert ScopeGuard.check_relevance("Optimize my itinerary while preserving food experiences.") == True
    assert ScopeGuard.check_relevance("What happens if my flight is delayed?") == True
    assert ScopeGuard.check_relevance("Explain the cost optimization engine.") == True
    assert ScopeGuard.check_relevance("Why was my hotel changed?") == True
    assert ScopeGuard.check_relevance("How does real-time data ingestion work?") == True

def test_scope_guard_rejected():
    assert ScopeGuard.check_relevance("What is the capital of India?") == False
    assert ScopeGuard.check_relevance("What is 25 * 37?") == False
    assert ScopeGuard.check_relevance("Who won yesterday's cricket match?") == False
    assert ScopeGuard.check_relevance("Write me a Python game.") == False
    assert ScopeGuard.check_relevance("Tell me a joke.") == False
    assert ScopeGuard.check_relevance("Explain photosynthesis.") == False
    assert ScopeGuard.check_relevance("What is the meaning of life?") == False
    assert ScopeGuard.check_relevance("Write a generic college essay.") == False

@patch('app.services.openrouter_client.openai.OpenAI')
def test_openrouter_success(mock_openai):
    from app.services.live_trip_service import LiveTripService
    
    # Mock environment variables
    import os
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        # Mock client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Your flight is delayed."
        mock_client.chat.completions.create.return_value = mock_response

        # Mock db
        db = MagicMock()
        
        # Test LiveTripService integration
        with patch('app.services.live_trip_service.LiveTripService.get_live_status') as mock_status:
            mock_status.return_value.status_label = "ACTIVE"
            mock_status.return_value.day_label = "Day 1"
            mock_status.return_value.timeline = []

            response = LiveTripService.handle_assistant_request(db, 1, "Why did my flight change?")
            assert "[AI GENERATED]" in response.response
            assert "Your flight is delayed." in response.response

@patch('app.services.openrouter_client.openai.OpenAI')
def test_openrouter_missing_key(mock_openai):
    from app.services.live_trip_service import LiveTripService
    import os
    with patch.dict(os.environ, clear=True):
        db = MagicMock()
        with patch('app.services.live_trip_service.LiveTripService.get_live_status') as mock_status:
            mock_status.return_value.status_label = "ACTIVE"
            mock_status.return_value.day_label = "Day 1"
            mock_status.return_value.timeline = []

            response = LiveTripService.handle_assistant_request(db, 1, "Why did my flight change?")
            assert "[DEMO FALLBACK]" in response.response

def test_openrouter_scope_rejection():
    from app.services.live_trip_service import LiveTripService
    db = MagicMock()
    response = LiveTripService.handle_assistant_request(db, 1, "What is the capital of India?")
    assert "[SCOPE REJECTED]" in response.response
    assert "I’m focused on travel planning" in response.response
