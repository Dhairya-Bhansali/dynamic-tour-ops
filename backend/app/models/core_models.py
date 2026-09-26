from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.enums import TripStatus, BookingStatus, DisruptionStatus

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    role = Column(String) # TRAVELER or OPERATOR

class Traveler(Base):
    __tablename__ = "travelers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    preferences = Column(JSON) # Travel DNA
    user = relationship("User")
    trips = relationship("Trip", back_populates="traveler")

class Operator(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    department = Column(String)
    user = relationship("User")

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String) # HOTEL, TRANSPORT, ACTIVITY

class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    traveler_id = Column(Integer, ForeignKey("travelers.id"))
    status = Column(String, default="DRAFT")
    coordinator = Column(String, default="Unassigned")
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    preferences = Column(JSON) # Trip-level personalization data
    destinations = Column(JSON)
    destination_id = Column(Integer, ForeignKey("destinations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    traveler = relationship("Traveler", back_populates="trips")
    itineraries = relationship("Itinerary", back_populates="trip")
    bookings = relationship("Booking", back_populates="trip")
    disruptions = relationship("Disruption", back_populates="trip")

class Itinerary(Base):
    __tablename__ = "itineraries"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    generation_method = Column(String, default='DEMO FALLBACK')
    generation_method = Column(String, default='DEMO FALLBACK')
    
    trip = relationship("Trip", back_populates="itineraries")
    items = relationship("ItineraryItem", back_populates="itinerary")

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey('trips.id'), nullable=False)
    itinerary_item_id = Column(Integer, ForeignKey('itinerary_items.id'))
    traveler_id = Column(Integer, ForeignKey('travelers.id'))
    provider_id = Column(String)
    booking_type = Column(String)
    status = Column(String, default="DRAFT") # DRAFT, PENDING, CONFIRMED, CANCELLED, FAILED
    confirmation_code = Column(String)
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    location = Column(String)
    estimated_cost = Column(Float)
    currency = Column(String, default="USD")
    provider_reference = Column(String)
    source_type = Column(String, default="DEMO") # DEMO vs LIVE
    cancellation_policy = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    trip = relationship("Trip", back_populates="bookings")
    
class ItineraryItem(Base):
    __tablename__ = "itinerary_items"
    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"))
    day_number = Column(Integer)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    activity_type = Column(String)
    description = Column(String)
    location = Column(String)
    estimated_cost = Column(Float)
    ai_reasoning = Column(String)
    confidence_score = Column(Float)
    day_date = Column(DateTime)
    
    itinerary = relationship("Itinerary", back_populates="items")


class Disruption(Base):
    __tablename__ = "disruptions"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    itinerary_version_id = Column(Integer, ForeignKey("itineraries.id"), nullable=True)
    disruption_type = Column(String) # PRICE_CHANGE, FLIGHT_CHANGE, WEATHER_RISK, etc.
    severity = Column(String) # HIGH, MEDIUM, LOW
    title = Column(String)
    description = Column(String)
    source = Column(String)
    source_record_id = Column(String)
    previous_value = Column(String)
    current_value = Column(String)
    status = Column(Enum(DisruptionStatus), default=DisruptionStatus.DETECTED)
    impact_summary = Column(JSON) # e.g. {"cost_impact": 4500, "affected_items": [1,2]}
    impact_radius = Column(JSON) # e.g. {"downstream_affected": [3]}
    confidence = Column(String) # HIGH, MEDIUM, LOW
    requires_approval = Column(Boolean, default=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    trip = relationship("Trip", back_populates="disruptions")
    itinerary_version = relationship("Itinerary")
    alternatives = relationship("AlternativePlan", back_populates="disruption")

class AlternativePlan(Base):
    __tablename__ = "alternative_plans"
    id = Column(Integer, primary_key=True, index=True)
    disruption_id = Column(Integer, ForeignKey("disruptions.id"))
    confidence_score = Column(Float)
    changes = Column(JSON)
    is_approved = Column(Boolean, default=False)
    cost_difference = Column(Float, default=0.0)
    preference_match = Column(Float, default=0.0)
    travel_time_difference = Column(Integer, default=0)
    reason = Column(String)
    items = Column(JSON)
    
    disruption = relationship("Disruption", back_populates="alternatives")

class Destination(Base):
    __tablename__ = "destinations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String)
    hero_image = Column(String)
    description = Column(String)
    budget = Column(Float)
    preferences = Column(JSON) # Trip-level personalization data
    recommended_duration = Column(Integer) # in days
    travel_styles = Column(JSON) # e.g., ["Adventure", "Luxury"]
    coordinates = Column(JSON) # {"lat": 0.0, "lng": 0.0}
    is_featured = Column(Boolean, default=False)
    is_trending = Column(Boolean, default=False)

class Experience(Base):
    __tablename__ = "experiences"
    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"))
    name = Column(String, index=True)
    image = Column(String)
    location = Column(String)
    estimated_cost = Column(Float)
    ai_reasoning = Column(String)
    confidence_score = Column(Float)
    day_date = Column(DateTime)
    duration = Column(Integer) # in hours
    price_estimate = Column(Float)
    category = Column(String) # Adventure, Culture, Food, etc.
    travel_styles = Column(JSON)
    availability_status = Column(String, default="AVAILABLE")
    description = Column(String)
    
    destination = relationship("Destination")

class OptimizationAudit(Base):
    __tablename__ = "optimization_audits"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    original_itinerary_version = Column(Integer)
    optimization_strategy = Column(String)
    target_budget = Column(Float)
    original_cost = Column(Float)
    optimized_cost = Column(Float)
    savings = Column(Float)
    changed_components = Column(JSON)
    data_sources = Column(JSON)
    applied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

