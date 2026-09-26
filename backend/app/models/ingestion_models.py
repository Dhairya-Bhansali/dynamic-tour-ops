from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, index=True)
    data_type = Column(String, index=True) # flights, weather, places, routes, hotels, activities
    environment = Column(String) # LIVE, TEST, DEMO
    status = Column(String, default="ACTIVE")
    last_success_at = Column(DateTime)
    last_failure_at = Column(DateTime)
    last_error = Column(String)
    records_ingested = Column(Integer, default=0)
    enabled = Column(Boolean, default=True)

class RawProviderResponse(Base):
    __tablename__ = "raw_provider_responses"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String, index=True)
    endpoint = Column(String)
    request_hash = Column(String, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    status_code = Column(Integer)
    payload = Column(JSON)
    success = Column(Boolean)
    error_info = Column(String)

class FlightOffer(Base):
    __tablename__ = "flight_offers"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)
    external_id = Column(String, index=True)
    origin = Column(String, index=True)
    destination = Column(String, index=True)
    departure_time = Column(DateTime)
    arrival_time = Column(DateTime)
    duration = Column(Integer) # minutes
    stops = Column(Integer)
    airline = Column(String)
    base_price = Column(Float)
    taxes = Column(Float)
    total_price = Column(Float)
    currency = Column(String, default="USD")
    cancellation_policy = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    valid_until = Column(DateTime)

class HotelOffer(Base):
    __tablename__ = "hotel_offers"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)
    external_id = Column(String, index=True)
    hotel_name = Column(String)
    location = Column(String)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    room_type = Column(String)
    nightly_price = Column(Float)
    total_price = Column(Float)
    currency = Column(String, default="USD")
    cancellation_policy = Column(String)
    rating = Column(Float)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    valid_until = Column(DateTime)

class ActivityOffer(Base):
    __tablename__ = "activity_offers"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)
    external_id = Column(String, index=True)
    name = Column(String)
    location = Column(String)
    category = Column(String)
    duration = Column(Integer)
    price = Column(Float)
    currency = Column(String, default="USD")
    fetched_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    valid_until = Column(DateTime)

class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    date = Column(DateTime, index=True)
    temperature = Column(Float)
    precipitation_probability = Column(Float)
    precipitation = Column(Float)
    wind_speed = Column(Float)
    visibility = Column(Float)
    weather_code = Column(String)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    valid_until = Column(DateTime)

class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)
    external_id = Column(String, index=True)
    name = Column(String)
    type = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    rating = Column(Float)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Route(Base):
    __tablename__ = "routes"
    id = Column(Integer, primary_key=True, index=True)
    provider = Column(String)
    origin_lat = Column(Float)
    origin_lng = Column(Float)
    dest_lat = Column(Float)
    dest_lng = Column(Float)
    distance_km = Column(Float)
    duration_minutes = Column(Float)
    geometry = Column(JSON) # e.g. polyline or GeoJSON
    fetched_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    valid_until = Column(DateTime)
