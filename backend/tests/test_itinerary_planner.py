import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from app.services.itinerary_planner import ItineraryPlanner
from app.models.core_models import Trip, Experience

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockMessage(content)

class MockResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

@pytest.fixture
def mock_trip():
    t = MagicMock()
    t.id = 1
    t.destination_id = 1
    t.preferences = {"duration": 1, "budget": 1000, "interests": ["culture"], "travel_style": "relaxed"}
    return t

@pytest.fixture
def mock_sparse_trip():
    t = MagicMock()
    t.id = 2
    t.destination_id = 1
    t.preferences = {"duration": 1, "budget": 1000, "interests": [], "travel_style": "", "selected_experiences": []}
    return t

@pytest.fixture
def db_session():
    db = MagicMock()
    # mock existing version count
    db.query().filter().count.return_value = 0
    return db

def get_mock_destination():
    d = MagicMock()
    d.name = "Test Destination"
    return d

def test_full_preferences_ai_generated(db_session, mock_trip):
    client_mock = MagicMock()
    # Valid JSON
    valid_json = '[{"day_number": 1, "start_time": "2026-09-26T09:00:00", "end_time": "2026-09-26T11:00:00", "activity_type": "culture", "description": "Test", "location": "Test", "estimated_cost": 50, "ai_reasoning": "test", "confidence_score": 0.9}]'
    client_mock.chat.completions.create.return_value = MockResponse(valid_json)
    
    with patch('app.services.itinerary_planner.get_openrouter_client', return_value=(client_mock, 'test-model')):
        db_session.query().filter().first.side_effect = [mock_trip, get_mock_destination()]
        itinerary, _ = ItineraryPlanner.generate_itinerary(db_session, 1)
        assert itinerary.generation_method == "AI GENERATED"
        assert client_mock.chat.completions.create.call_count == 1

def test_empty_interests_and_experiences(db_session, mock_sparse_trip):
    client_mock = MagicMock()
    valid_json = '[{"day_number": 1, "start_time": "2026-09-26T09:00:00", "end_time": "2026-09-26T11:00:00", "activity_type": "culture", "description": "Test", "location": "Test", "estimated_cost": 50, "ai_reasoning": "test", "confidence_score": 0.9}]'
    client_mock.chat.completions.create.return_value = MockResponse(valid_json)
    
    with patch('app.services.itinerary_planner.get_openrouter_client', return_value=(client_mock, 'test-model')):
        db_session.query().filter().first.side_effect = [mock_sparse_trip, get_mock_destination()]
        itinerary, _ = ItineraryPlanner.generate_itinerary(db_session, 2)
        assert itinerary.generation_method == "AI GENERATED"
        
        # Check prompt normalization
        call_args = client_mock.chat.completions.create.call_args[1]
        prompt = call_args["messages"][1]["content"]
        assert "balanced general travel interests" in prompt

def test_markdown_json_extraction(db_session, mock_trip):
    client_mock = MagicMock()
    markdown_json = "Here is your plan:\n```json\n" + '[{"day_number": 1, "start_time": "2026-09-26T09:00:00", "end_time": "2026-09-26T11:00:00", "activity_type": "culture", "description": "Test", "location": "Test", "estimated_cost": 50, "ai_reasoning": "test", "confidence_score": 0.9}]' + "\n```\nEnjoy!"
    client_mock.chat.completions.create.return_value = MockResponse(markdown_json)
    
    with patch('app.services.itinerary_planner.get_openrouter_client', return_value=(client_mock, 'test-model')):
        db_session.query().filter().first.side_effect = [mock_trip, get_mock_destination()]
        itinerary, _ = ItineraryPlanner.generate_itinerary(db_session, 1)
        assert itinerary.generation_method == "AI GENERATED"

def test_conversational_retry_success(db_session, mock_trip):
    client_mock = MagicMock()
    # First call returns conversational, second returns JSON
    valid_json = '[{"day_number": 1, "start_time": "2026-09-26T09:00:00", "end_time": "2026-09-26T11:00:00", "activity_type": "culture", "description": "Test", "location": "Test", "estimated_cost": 50, "ai_reasoning": "test", "confidence_score": 0.9}]'
    client_mock.chat.completions.create.side_effect = [MockResponse("I need more info"), MockResponse(valid_json)]
    
    with patch('app.services.itinerary_planner.get_openrouter_client', return_value=(client_mock, 'test-model')):
        db_session.query().filter().first.side_effect = [mock_trip, get_mock_destination()]
        itinerary, _ = ItineraryPlanner.generate_itinerary(db_session, 1)
        assert itinerary.generation_method == "AI GENERATED"
        assert client_mock.chat.completions.create.call_count == 2

def test_conversational_retry_failure_fallback(db_session, mock_trip):
    client_mock = MagicMock()
    # Both calls return conversational
    client_mock.chat.completions.create.side_effect = [MockResponse("I need more info"), MockResponse("Still need info")]
    
    with patch('app.services.itinerary_planner.get_openrouter_client', return_value=(client_mock, 'test-model')):
        db_session.query().filter().first.side_effect = [mock_trip, MagicMock(name="Destination")]
        itinerary, _ = ItineraryPlanner.generate_itinerary(db_session, 1)
        assert itinerary.generation_method == "DEMO FALLBACK"

def test_openrouter_unavailable_fallback(db_session, mock_trip):
    # client is None
    with patch('app.services.itinerary_planner.get_openrouter_client', return_value=(None, None)):
        db_session.query().filter().first.side_effect = [mock_trip, MagicMock(name="Destination")]
        itinerary, _ = ItineraryPlanner.generate_itinerary(db_session, 1)
        assert itinerary.generation_method == "DEMO FALLBACK"
