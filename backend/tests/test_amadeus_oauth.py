import pytest
from unittest.mock import patch, MagicMock
from app.services.ingestion.amadeus import AmadeusConnector
from app.services.ingestion.service import IngestionService
from app.models.ingestion_models import FlightOffer, HotelOffer, DataSource
import os

@pytest.fixture
def mock_db():
    db = MagicMock()
    return db

@patch.dict(os.environ, {"AMADEUS_CLIENT_ID": "test_id", "AMADEUS_CLIENT_SECRET": "test_secret"})
def test_amadeus_oauth_success(mock_db):
    connector = AmadeusConnector(mock_db, env="LIVE")
    with patch.object(connector.client, 'post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "valid_token", "expires_in": 1800}
        mock_post.return_value = mock_response

        token = connector._get_access_token()
        assert token == "valid_token"
        assert connector._access_token == "valid_token"

@patch.dict(os.environ, {"AMADEUS_CLIENT_ID": "", "AMADEUS_CLIENT_SECRET": ""})
def test_amadeus_oauth_missing_credentials(mock_db):
    connector = AmadeusConnector(mock_db, env="LIVE")
    with pytest.raises(ValueError, match="Amadeus credentials are not configured"):
        connector._get_access_token()

@patch.dict(os.environ, {"AMADEUS_CLIENT_ID": "test_id", "AMADEUS_CLIENT_SECRET": "test_secret"})
def test_amadeus_fetch_flight_offers(mock_db):
    connector = AmadeusConnector(mock_db, env="LIVE")
    with patch.object(connector, '_get_access_token', return_value="test_token"):
        with patch.object(connector, 'fetch', return_value={"data": [{"id": "1", "price": {"total": "100.0"}}]}) as mock_fetch:
            offers = connector.fetch_flight_offers("JFK", "LHR", "2023-12-01")
            assert len(offers) == 1
            assert offers[0]["id"] == "1"
            mock_fetch.assert_called_once()
            args, kwargs = mock_fetch.call_args
            assert kwargs["headers"] == {"Authorization": "Bearer test_token"}

@patch.dict(os.environ, {"AMADEUS_CLIENT_ID": "test_id", "AMADEUS_CLIENT_SECRET": "test_secret"})
def test_amadeus_fetch_hotel_offers(mock_db):
    connector = AmadeusConnector(mock_db, env="LIVE")
    with patch.object(connector, '_get_access_token', return_value="test_token"):
        with patch.object(connector, 'fetch', return_value={"data": [{"hotel": {"hotelId": "H1"}}]}) as mock_fetch:
            offers = connector.fetch_hotel_offers("LON", "2023-12-01", "2023-12-05")
            assert len(offers) == 1
            assert offers[0]["hotel"]["hotelId"] == "H1"
            mock_fetch.assert_called_once()
            args, kwargs = mock_fetch.call_args
            assert kwargs["headers"] == {"Authorization": "Bearer test_token"}
