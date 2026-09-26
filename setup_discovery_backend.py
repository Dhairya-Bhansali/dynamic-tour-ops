import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

def append_to_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip() + "\n")

def replace_in_file(path, old, new):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# 1. Update core_models.py to add Destination and Experience
models_content = """
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
"""
append_to_file("backend/app/models/core_models.py", models_content)

# 2. Create schemas/discovery.py
create_file("backend/app/schemas/discovery.py", """
from pydantic import BaseModel
from typing import List, Optional, Any

class DestinationBase(BaseModel):
    name: str
    country: str
    hero_image: str
    description: str
    budget: float
    recommended_duration: int
    travel_styles: List[str]
    coordinates: Any
    is_featured: bool
    is_trending: bool

class DestinationResponse(DestinationBase):
    id: int
    class Config:
        from_attributes = True

class ExperienceBase(BaseModel):
    destination_id: int
    name: str
    image: str
    location: str
    duration: int
    price_estimate: float
    category: str
    travel_styles: List[str]
    availability_status: str
    description: str

class ExperienceResponse(ExperienceBase):
    id: int
    class Config:
        from_attributes = True
""")

# 3. Create services/discovery_service.py
create_file("backend/app/services/discovery_service.py", """
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.core_models import Destination, Experience

class DiscoveryService:
    @staticmethod
    def get_destinations(db: Session, search: str = None, style: str = None):
        query = db.query(Destination)
        if search:
            query = query.filter(
                or_(
                    Destination.name.ilike(f"%{search}%"),
                    Destination.country.ilike(f"%{search}%")
                )
            )
        if style:
            # Simple fallback search within JSON text
            query = query.filter(Destination.travel_styles.cast(str).ilike(f"%{style}%"))
        return query.all()

    @staticmethod
    def get_destination(db: Session, dest_id: int):
        return db.query(Destination).filter(Destination.id == dest_id).first()

    @staticmethod
    def get_experiences(db: Session, category: str = None, dest_id: int = None, search: str = None):
        query = db.query(Experience)
        if search:
            query = query.filter(Experience.name.ilike(f"%{search}%"))
        if category:
            query = query.filter(Experience.category == category)
        if dest_id:
            query = query.filter(Experience.destination_id == dest_id)
        return query.all()

    @staticmethod
    def get_experience(db: Session, exp_id: int):
        return db.query(Experience).filter(Experience.id == exp_id).first()
""")

# 4. Update routes.py
routes_imports = """
from app.schemas.discovery import DestinationResponse, ExperienceResponse
from app.services.discovery_service import DiscoveryService
from typing import List, Optional
"""
routes_endpoints = """
@router.get("/destinations", response_model=List[DestinationResponse])
def get_destinations(
    search: Optional[str] = None, 
    style: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    return DiscoveryService.get_destinations(db, search=search, style=style)

@router.get("/destinations/{dest_id}", response_model=DestinationResponse)
def get_destination(dest_id: int, db: Session = Depends(get_db)):
    dest = DiscoveryService.get_destination(db, dest_id)
    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")
    return dest

@router.get("/experiences", response_model=List[ExperienceResponse])
def get_experiences(
    category: Optional[str] = None,
    dest_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return DiscoveryService.get_experiences(db, category=category, dest_id=dest_id, search=search)

@router.get("/experiences/{exp_id}", response_model=ExperienceResponse)
def get_experience(exp_id: int, db: Session = Depends(get_db)):
    exp = DiscoveryService.get_experience(db, exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp
"""

replace_in_file("backend/app/api/routes.py", 
                "from typing import List", 
                routes_imports)
append_to_file("backend/app/api/routes.py", routes_endpoints)

# 5. Update seed.py
replace_in_file("backend/seed.py",
                "from app.models.core_models import User, Traveler, Operator, Vendor, Trip, Itinerary, ItineraryItem, Booking",
                "from app.models.core_models import User, Traveler, Operator, Vendor, Trip, Itinerary, ItineraryItem, Booking, Destination, Experience")

seed_data_injection = """
    # Discovery Data
    if not db.query(Destination).first():
        d1 = Destination(
            name="Kyoto", country="Japan",
            hero_image="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?q=80&w=2070&auto=format&fit=crop",
            description="Experience the tranquil beauty of ancient temples, traditional tea houses, and sublime gardens.",
            budget=2500, recommended_duration=5, travel_styles=["Culture", "Spiritual", "Relaxation"],
            coordinates={"lat": 35.0116, "lng": 135.7681}, is_featured=True, is_trending=True
        )
        d2 = Destination(
            name="Santorini", country="Greece",
            hero_image="https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?q=80&w=1935&auto=format&fit=crop",
            description="Famous for its stunning sunsets, white-washed buildings, and crystal-clear Aegean waters.",
            budget=3500, recommended_duration=7, travel_styles=["Romantic", "Luxury", "Relaxation"],
            coordinates={"lat": 36.3932, "lng": 25.4615}, is_featured=True, is_trending=False
        )
        d3 = Destination(
            name="Patagonia", country="Chile",
            hero_image="https://images.unsplash.com/photo-1578637387939-43c525550085?q=80&w=2070&auto=format&fit=crop",
            description="A dramatic landscape of jagged peaks, immense glaciers, and pristine lakes at the edge of the world.",
            budget=4000, recommended_duration=10, travel_styles=["Adventure", "Nature"],
            coordinates={"lat": -51.7236, "lng": -72.5087}, is_featured=False, is_trending=True
        )
        d4 = Destination(
            name="Bali", country="Indonesia",
            hero_image="https://images.unsplash.com/photo-1537996194471-e657df975ab4?q=80&w=2138&auto=format&fit=crop",
            description="An island paradise blending vibrant culture, lush rice terraces, and beautiful beaches.",
            budget=1500, recommended_duration=8, travel_styles=["Culture", "Nature", "Spiritual"],
            coordinates={"lat": -8.4095, "lng": 115.1889}, is_featured=True, is_trending=True
        )
        db.add_all([d1, d2, d3, d4])
        db.commit()

        # Experiences
        e1 = Experience(
            destination_id=d1.id, name="Private Tea Ceremony",
            image="https://images.unsplash.com/photo-1542281286-9e0a16bb7366?q=80&w=2069&auto=format&fit=crop",
            location="Higashiyama District, Kyoto", duration=2, price_estimate=150,
            category="Culture", travel_styles=["Culture", "Spiritual"],
            description="A mindful and authentic matcha tea ceremony led by a zen master in a 300-year-old traditional machiya."
        )
        e2 = Experience(
            destination_id=d3.id, name="Glacier Trekking",
            image="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=2070&auto=format&fit=crop",
            location="Torres del Paine", duration=8, price_estimate=300,
            category="Adventure", travel_styles=["Adventure", "Nature"],
            description="Strap on crampons and explore the mesmerizing ice caves and crevasses of the Grey Glacier."
        )
        e3 = Experience(
            destination_id=d2.id, name="Catamaran Sunset Cruise",
            image="https://images.unsplash.com/photo-1544321272-97b411d957fc?q=80&w=2070&auto=format&fit=crop",
            location="Oia, Santorini", duration=4, price_estimate=250,
            category="Luxury", travel_styles=["Romantic", "Luxury"],
            description="Sail the caldera on a luxury catamaran, complete with a Greek feast and open bar as the sun dips below the horizon."
        )
        e4 = Experience(
            destination_id=d4.id, name="Ubud Rice Terraces Cycling",
            image="https://images.unsplash.com/photo-1560930773-16a73c9db60b?q=80&w=2070&auto=format&fit=crop",
            location="Ubud, Bali", duration=5, price_estimate=80,
            category="Adventure", travel_styles=["Adventure", "Nature"],
            description="Downhill cycling through lush ancient rice terraces and authentic Balinese villages."
        )
        db.add_all([e1, e2, e3, e4])
        db.commit()
"""
replace_in_file("backend/seed.py", 
                "print(\"Seed data injected successfully!\")", 
                seed_data_injection + "\n    print(\"Seed data injected successfully!\")")
