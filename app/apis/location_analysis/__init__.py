from fastapi import APIRouter, Query, HTTPException, Path
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
import random
from datetime import datetime, timedelta

router = APIRouter()

# Models for location analysis
class LocationType(str, Enum):
    URBAN = "urban"
    SUBURBAN = "suburban"
    RURAL = "rural"
    DOWNTOWN = "downtown"
    SHOPPING_MALL = "shopping_mall"
    BUSINESS_DISTRICT = "business_district"
    RESIDENTIAL = "residential"
    MIXED_USE = "mixed_use"
    TRANSIT_HUB = "transit_hub"
    CAMPUS = "campus"

class DemographicMetric(str, Enum):
    POPULATION = "population"
    INCOME = "income"
    AGE_DISTRIBUTION = "age_distribution"
    EDUCATION = "education"
    HOUSEHOLD_SIZE = "household_size"
    EMPLOYMENT = "employment"
    CONSUMER_SPENDING = "consumer_spending"

class CompetitorType(str, Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    POTENTIAL = "potential"

class FootTrafficPattern(BaseModel):
    hour: int
    weekday: int  # 0-6 (Monday-Sunday)
    volume: int
    description: str

class Location(BaseModel):
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    type: LocationType
    active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    description: Optional[str] = None
    score: Optional[int] = None

class LocationScore(BaseModel):
    category: str
    score: int
    weight: float
    description: str

class LocationScoreDetails(BaseModel):
    overall: int
    foot_traffic: int
    restaurant_density: int
    income_level: int
    competition: int
    accessibility: int
    parking: int
    public_transport: int
    visibility: int
    detailed_scores: List[LocationScore]

class DemographicData(BaseModel):
    location_id: str
    metric: DemographicMetric
    value: Any
    radius_miles: float
    timestamp: datetime
    source: str

class Competitor(BaseModel):
    id: str
    name: str
    type: CompetitorType
    distance_miles: float
    address: str
    latitude: float
    longitude: float
    rating: Optional[float] = None
    price_level: Optional[int] = None
    categories: List[str]
    estimated_revenue: Optional[float] = None

class LocationInsight(BaseModel):
    id: str
    location_id: str
    title: str
    description: str
    category: str
    severity: str  # "positive", "neutral", "warning", "critical"
    created_at: datetime

# Sample data for the endpoints
sample_locations = [
    Location(
        id="loc-001",
        name="Downtown Main St.",
        address="123 Main St, San Francisco, CA",
        latitude=37.7749,
        longitude=-122.4194,
        type=LocationType.DOWNTOWN,
        created_at=datetime.now() - timedelta(days=30),
        updated_at=datetime.now() - timedelta(days=5),
        description="Prime downtown location with high foot traffic",
        score=86
    ),
    Location(
        id="loc-002",
        name="Suburban Plaza",
        address="456 Plaza Ave, San Jose, CA",
        latitude=37.3382,
        longitude=-121.8863,
        type=LocationType.SUBURBAN,
        created_at=datetime.now() - timedelta(days=20),
        updated_at=datetime.now() - timedelta(days=2),
        description="Shopping center with family-friendly demographics",
        score=72
    ),
    Location(
        id="loc-003",
        name="University District",
        address="789 College Blvd, Berkeley, CA",
        latitude=37.8715,
        longitude=-122.2730,
        type=LocationType.CAMPUS,
        created_at=datetime.now() - timedelta(days=15),
        updated_at=None,
        description="Near major university with student population",
        score=81
    ),
]

sample_scores = LocationScoreDetails(
    overall=86,
    foot_traffic=92,
    restaurant_density=75,
    income_level=88,
    competition=64,
    accessibility=95,
    parking=70,
    public_transport=85,
    visibility=80,
    detailed_scores=[
        LocationScore(
            category="Foot Traffic",
            score=92,
            weight=0.25,
            description="High volume of pedestrians throughout the day"
        ),
        LocationScore(
            category="Income Level",
            score=88,
            weight=0.2,
            description="Area median income is 33% above city average"
        ),
        LocationScore(
            category="Competition",
            score=64,
            weight=0.15,
            description="12 similar restaurants within 1 mile radius"
        ),
        LocationScore(
            category="Accessibility",
            score=95,
            weight=0.1,
            description="Easily accessible by car and public transportation"
        ),
        LocationScore(
            category="Visibility",
            score=80,
            weight=0.1,
            description="Good storefront visibility from main street"
        ),
    ]
)

sample_insights = [
    LocationInsight(
        id="ins-001",
        location_id="loc-001",
        title="High Foot Traffic",
        description="This location sees an estimated 1,200+ pedestrians daily during peak hours.",
        category="Traffic",
        severity="positive",
        created_at=datetime.now() - timedelta(days=5)
    ),
    LocationInsight(
        id="ins-002",
        location_id="loc-001",
        title="Strong Income Demographics",
        description="Median household income in this area is 33% above the city average.",
        category="Demographics",
        severity="positive",
        created_at=datetime.now() - timedelta(days=5)
    ),
    LocationInsight(
        id="ins-003",
        location_id="loc-001",
        title="Moderate Competition",
        description="12 similar restaurants within a 1-mile radius, but only 3 direct competitors.",
        category="Competition",
        severity="neutral",
        created_at=datetime.now() - timedelta(days=5)
    ),
    LocationInsight(
        id="ins-004",
        location_id="loc-001",
        title="Peak Time Alert",
        description="Traffic peaks between 11:30am-1:30pm and 5:30pm-7:30pm on weekdays.",
        category="Operations",
        severity="warning",
        created_at=datetime.now() - timedelta(days=5)
    )
]

sample_competitors = [
    Competitor(
        id="comp-001",
        name="Pasta Palace",
        type=CompetitorType.DIRECT,
        distance_miles=0.3,
        address="156 Main St, San Francisco, CA",
        latitude=37.7751,
        longitude=-122.4190,
        rating=4.2,
        price_level=3,
        categories=["Italian", "Pasta", "Wine Bar"],
        estimated_revenue=1200000
    ),
    Competitor(
        id="comp-002",
        name="Taco Time",
        type=CompetitorType.INDIRECT,
        distance_miles=0.5,
        address="200 Market St, San Francisco, CA",
        latitude=37.7757,
        longitude=-122.4183,
        rating=4.5,
        price_level=2,
        categories=["Mexican", "Tacos", "Fast Casual"],
        estimated_revenue=900000
    ),
    Competitor(
        id="comp-003",
        name="Burger Barn",
        type=CompetitorType.INDIRECT,
        distance_miles=0.7,
        address="350 Mission St, San Francisco, CA",
        latitude=37.7760,
        longitude=-122.4175,
        rating=3.8,
        price_level=2,
        categories=["American", "Burgers", "Fast Food"],
        estimated_revenue=1500000
    ),
]

# Generate sample foot traffic data
def generate_foot_traffic():
    patterns = []
    for day in range(7):  # 0-6 for Monday-Sunday
        for hour in range(24):
            # Create realistic patterns with peaks during lunch and dinner
            volume = 20  # Base level
            
            # Weekday patterns
            if day < 5:  # Monday-Friday
                if 11 <= hour <= 13:  # Lunch peak
                    volume = random.randint(150, 250)
                elif 17 <= hour <= 20:  # Dinner peak
                    volume = random.randint(180, 300)
                elif 7 <= hour <= 10:  # Breakfast
                    volume = random.randint(50, 100)
                elif 14 <= hour <= 16:  # Afternoon
                    volume = random.randint(40, 80)
                elif 21 <= hour <= 23:  # Late evening
                    volume = random.randint(30, 90)
                elif hour < 6:  # Early morning
                    volume = random.randint(5, 15)
            # Weekend patterns
            else:
                if 9 <= hour <= 14:  # Brunch/lunch peak
                    volume = random.randint(200, 350)
                elif 17 <= hour <= 21:  # Dinner peak (longer on weekends)
                    volume = random.randint(220, 380)
                elif 14 <= hour <= 16:  # Afternoon
                    volume = random.randint(100, 150)
                elif 22 <= hour <= 23:  # Late night
                    volume = random.randint(80, 120)
                elif hour < 8:  # Early morning
                    volume = random.randint(5, 20)
            
            # Create description based on volume
            if volume < 30:
                description = "Very Low"
            elif volume < 80:
                description = "Low"
            elif volume < 150:
                description = "Moderate"
            elif volume < 250:
                description = "High"
            else:
                description = "Very High"
                
            patterns.append(FootTrafficPattern(
                hour=hour,
                weekday=day,
                volume=volume,
                description=description
            ))
    return patterns

sample_foot_traffic = generate_foot_traffic()

# API Routes
@router.get("/", response_model=List[Location])
async def get_locations(
    q: Optional[str] = None,
    type: Optional[LocationType] = None,
    active: Optional[bool] = True,
    limit: int = Query(10, ge=1, le=100)
):
    """Get a list of locations with optional filtering"""
    filtered = sample_locations
    
    if q:
        filtered = [loc for loc in filtered if q.lower() in loc.name.lower() or q.lower() in loc.address.lower()]
    
    if type:
        filtered = [loc for loc in filtered if loc.type == type]
        
    if active is not None:
        filtered = [loc for loc in filtered if loc.active == active]
        
    return filtered[:limit]

@router.get("/{location_id}", response_model=Location)
async def get_location(location_id: str = Path(..., title="The ID of the location to retrieve")):
    """Get detailed information about a specific location"""
    location = next((loc for loc in sample_locations if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.get("/{location_id}/scores", response_model=LocationScoreDetails)
async def get_location_scores(location_id: str = Path(..., title="The ID of the location to retrieve scores for")):
    """Get detailed score breakdown for a location"""
    # Here we're just returning the same sample scores for any location
    # In a real app, you'd look up the specific location's scores
    location = next((loc for loc in sample_locations if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return sample_scores

@router.get("/{location_id}/foot-traffic", response_model=List[FootTrafficPattern])
async def get_location_foot_traffic(
    location_id: str = Path(..., title="The ID of the location to retrieve foot traffic for"),
    day: Optional[int] = Query(None, ge=0, le=6, description="Filter by day of week (0=Monday, 6=Sunday)"),
    min_hour: Optional[int] = Query(None, ge=0, le=23, description="Filter by minimum hour"),
    max_hour: Optional[int] = Query(None, ge=0, le=23, description="Filter by maximum hour")
):
    """Get foot traffic patterns for a location with optional time filtering"""
    location = next((loc for loc in sample_locations if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    filtered = sample_foot_traffic
    
    if day is not None:
        filtered = [pattern for pattern in filtered if pattern.weekday == day]
        
    if min_hour is not None:
        filtered = [pattern for pattern in filtered if pattern.hour >= min_hour]
        
    if max_hour is not None:
        filtered = [pattern for pattern in filtered if pattern.hour <= max_hour]
        
    return filtered

@router.get("/{location_id}/competitors", response_model=List[Competitor])
async def get_location_competitors(
    location_id: str = Path(..., title="The ID of the location to retrieve competitors for"),
    type: Optional[CompetitorType] = None,
    max_distance: Optional[float] = Query(None, gt=0, description="Maximum distance in miles"),
    limit: int = Query(10, ge=1, le=50)
):
    """Get competitors near a specified location with optional filtering"""
    location = next((loc for loc in sample_locations if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    filtered = sample_competitors
    
    if type:
        filtered = [comp for comp in filtered if comp.type == type]
        
    if max_distance:
        filtered = [comp for comp in filtered if comp.distance_miles <= max_distance]
        
    return filtered[:limit]

@router.get("/{location_id}/insights", response_model=List[LocationInsight])
async def get_location_insights(
    location_id: str = Path(..., title="The ID of the location to retrieve insights for"),
    category: Optional[str] = None,
    severity: Optional[str] = None
):
    """Get analytical insights for a location with optional filtering"""
    location = next((loc for loc in sample_locations if loc.id == location_id), None)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    filtered = [insight for insight in sample_insights if insight.location_id == location_id]
    
    if category:
        filtered = [insight for insight in filtered if insight.category.lower() == category.lower()]
        
    if severity:
        filtered = [insight for insight in filtered if insight.severity.lower() == severity.lower()]
        
    return filtered 