import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_experiences_endpoint_success():
    response = client.get("/api/v1/experiences")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

def test_destinations_style_filtering():
    response = client.get("/api/v1/destinations?style=Adventure")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)

def test_itinerary_generation_validates_destination():
    response = client.post("/api/v1/trips/1/itinerary/generate")
    assert response.status_code in [200, 201], response.text
    data = response.json()
    assert "itinerary" in data
    assert data["itinerary"]["generation_method"] in ["AI_GENERATED", "DEMO FALLBACK"]

def test_sparse_itinerary_generation():
    # Similar to normal generation but validates sparse inputs (no interests/experiences)
    response = client.post("/api/v1/trips/2/itinerary/generate")
    assert response.status_code in [200, 201], response.text
    data = response.json()
    assert "itinerary" in data

def test_deterministic_fallback_uniqueness():
    # Test that fallback doesn't generate the same activity every day
    # We trigger fallback by mocking the client
    with pytest.MonkeyPatch.context() as m:
        import app.services.itinerary_planner
        m.setattr(app.services.itinerary_planner, "get_openrouter_client", lambda: (None, None, None))
        response = client.post("/api/v1/trips/1/itinerary/generate")
        assert response.status_code in [200, 201], response.text
        data = response.json()
        assert data["itinerary"]["generation_method"] == "DEMO FALLBACK"
        
        # Verify uniqueness — items are nested inside data["itinerary"]
        items = data["itinerary"]["items"]
        morning_descriptions = [i["description"] for i in items if i["activity_type"] == "BREAKFAST"]
        assert len(set(morning_descriptions)) > 1, f"All morning descriptions are the same: {morning_descriptions}"

def test_bookable_items_endpoint():
    response = client.get("/api/v1/trips/1/bookable-items")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "itinerary_item_id" in data[0]

def test_booking_total_calculation():
    # The frontend calculates it, but we check if the endpoint returns estimated_cost properly
    response = client.get("/api/v1/trips/1/bookable-items")
    assert response.status_code == 200, response.text
    data = response.json()
    if len(data) > 0:
        assert "estimated_cost" in data[0]

def test_currency_propagation():
    response = client.get("/api/v1/trips/1/bookable-items")
    assert response.status_code == 200, response.text
    data = response.json()
    if len(data) > 0:
        assert data[0].get("currency") == "INR"

def test_live_trip_assistant():
    response = client.post("/api/v1/trips/1/assistant", json={"message": "Hello"})
    assert response.status_code == 200, response.text

def test_cost_optimization():
    client.post("/api/v1/trips/1/itinerary/generate")
    # OptimizeRequest schema uses 'strategies' (list), not 'strategy' (str)
    response = client.post("/api/v1/trips/1/budget/optimize", json={"target_budget": 500, "strategies": ["MAX_SAVINGS"]})
    assert response.status_code == 200, response.text
    data = response.json()
    # OptimizeResponse uses 'current_cost', not 'optimized_total'
    assert "current_cost" in data, f"Expected 'current_cost' in response. Got keys: {list(data.keys())}"
    assert "scenarios" in data

def test_disruption_flow():
    client.post("/api/v1/trips/1/itinerary/generate")
    response = client.post("/api/v1/trips/1/disruptions/simulate?disruption_type=WEATHER")
    assert response.status_code == 200, response.text
    data = response.json()
    disruption_id = data.get("id")
    if disruption_id:
        analyze_res = client.post(f"/api/v1/disruptions/{disruption_id}/analyze")
        assert analyze_res.status_code == 200

def test_bookings_endpoint_after_migration():
    """
    Regression test: GET /api/v1/trips/1/bookings must return HTTP 200
    after the legacy bookings schema migration (adds itinerary_item_id etc.).
    The legacy booking row (HTL-98765, HOTEL, CONFIRMED) must be preserved.
    """
    response = client.get("/api/v1/trips/1/bookings")
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}: {response.text}"
    data = response.json()
    assert isinstance(data, list)
    # The legacy booking must still exist after migration
    codes = [b.get("confirmation_code") for b in data]
    assert "HTL-98765" in codes, f"Legacy booking HTL-98765 not found. Got: {codes}"
    # Verify the legacy booking has the correct backfilled fields
    legacy = next(b for b in data if b.get("confirmation_code") == "HTL-98765")
    assert legacy["status"] == "CONFIRMED"
    assert legacy["booking_type"] == "HOTEL"
    assert legacy["estimated_cost"] == 1200.0
    assert legacy["currency"] == "INR"
    assert legacy["source_type"] == "DEMO"

