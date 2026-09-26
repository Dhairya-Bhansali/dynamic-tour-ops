import pytest
from app.services.ingestion.amadeus import AmadeusConnector
from app.services.ingestion.open_meteo import OpenMeteoConnector

def test_amadeus_demo_data():
    connector = AmadeusConnector(db=None, env="DEMO")
    data = connector.get_demo_data("flight-offers", {"originLocationCode": "JFK", "destinationLocationCode": "LHR"})
    assert "data" in data
    assert len(data["data"]) > 0
    assert "price" in data["data"][0]

def test_open_meteo_demo_data():
    connector = OpenMeteoConnector(db=None, env="DEMO")
    data = connector.get_demo_data("forecast", {"latitude": 40.71, "longitude": -74.00})
    assert "daily" in data
    assert len(data["daily"]["temperature_2m_max"]) > 0
