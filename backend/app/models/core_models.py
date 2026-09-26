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
    status = Column(Enum(TripStatus), default=TripStatus.DRAFT)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    destinations = Column(JSON)
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
    
    trip = relationship("Trip", back_populates="itineraries")
    items = relationship("ItineraryItem", back_populates="itinerary")

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
    
    itinerary = relationship("Itinerary", back_populates="items")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    type = Column(String) # HOTEL, TRANSPORT, ACTIVITY
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    cost = Column(Float)
    confirmation_code = Column(String)
    
    trip = relationship("Trip", back_populates="bookings")
    vendor = relationship("Vendor")

class Disruption(Base):
    __tablename__ = "disruptions"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    description = Column(String)
    status = Column(Enum(DisruptionStatus), default=DisruptionStatus.DETECTED)
    impact_radius = Column(JSON)
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    trip = relationship("Trip", back_populates="disruptions")
    alternatives = relationship("AlternativePlan", back_populates="disruption")

class AlternativePlan(Base):
    __tablename__ = "alternative_plans"
    id = Column(Integer, primary_key=True, index=True)
    disruption_id = Column(Integer, ForeignKey("disruptions.id"))
    confidence_score = Column(Float)
    changes = Column(JSON)
    is_approved = Column(Boolean, default=False)
    
    disruption = relationship("Disruption", back_populates="alternatives")

class Destination(Base):
    __tablename__ = "destinations"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String)
    hero_image = Column(String)
    description = Column(String)
    budget = Column(Float)
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
    duration = Column(Integer) # in hours
    price_estimate = Column(Float)
    category = Column(String) # Adventure, Culture, Food, etc.
    travel_styles = Column(JSON)
    availability_status = Column(String, default="AVAILABLE")
    description = Column(String)
    
    destination = relationship("Destination")
