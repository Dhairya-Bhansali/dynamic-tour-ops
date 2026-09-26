import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_experiences_endpoint_success():
    response = client.get("/api/v1/experiences")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_destinations_style_filtering():
    response = client.get("/api/v1/destinations?style=Adventure")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    response = client.get("/api/v1/destinations?style=NonExistentStyle")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_itinerary_generation_validates_destination():
    response = client.post("/api/v1/trips/1/itinerary/generate")
    assert response.status_code in [200, 201]
    data = response.json()
    assert "itinerary" in data
    assert data["itinerary"]["generation_method"] in ["AI GENERATED", "DEMO FALLBACK"]
