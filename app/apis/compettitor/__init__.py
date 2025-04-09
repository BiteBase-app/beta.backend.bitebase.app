from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/competitors", tags=["competitors"])

class Competitor(BaseModel):
    id: str
    name: str
    location: str
    category: str
    rating: float
    priceRange: str
    distance: str
    lastUpdated: str

class CompetitorDetail(BaseModel):
    id: str
    name: str
    location: str
    category: str
    rating: float
    priceRange: str
    distance: str
    lastUpdated: str
    description: str
    website: str
    phoneNumber: str
    openingHours: Dict[str, str]
    popularItems: List[Dict[str, Any]]
    reviews: List[Dict[str, Any]]
    priceComparison: Dict[str, Any]

# Sample data
COMPETITORS = [
    {
        "id": "1",
        "name": "Tasty Bites Cafe",
        "location": "123 Main St, Downtown",
        "category": "Cafe",
        "rating": 4.5,
        "priceRange": "$$",
        "distance": "0.5 miles",
        "lastUpdated": "2025-04-01",
        "description": "A cozy cafe offering a variety of breakfast and lunch options with a focus on fresh, locally-sourced ingredients.",
        "website": "https://tastybites.example.com",
        "phoneNumber": "(555) 123-4567",
        "openingHours": {
            "Monday": "7:00 AM - 8:00 PM",
            "Tuesday": "7:00 AM - 8:00 PM",
            "Wednesday": "7:00 AM - 8:00 PM",
            "Thursday": "7:00 AM - 8:00 PM",
            "Friday": "7:00 AM - 9:00 PM",
            "Saturday": "8:00 AM - 9:00 PM",
            "Sunday": "8:00 AM - 6:00 PM"
        },
        "popularItems": [
            {"name": "Avocado Toast", "price": "$12.99", "popularity": 95},
            {"name": "Breakfast Burrito", "price": "$10.99", "popularity": 88},
            {"name": "Cappuccino", "price": "$4.50", "popularity": 92}
        ],
        "reviews": [
            {"author": "John D.", "rating": 5, "comment": "Best breakfast in town!", "date": "2025-03-15"},
            {"author": "Sarah M.", "rating": 4, "comment": "Great food but a bit pricey.", "date": "2025-03-20"},
            {"author": "Mike T.", "rating": 5, "comment": "Amazing coffee and friendly staff.", "date": "2025-03-25"}
        ],
        "priceComparison": {
            "averageMealPrice": "$15.99",
            "comparedToYou": "-5%",
            "comparedToArea": "+10%"
        }
    },
    {
        "id": "2",
        "name": "Gourmet Delight",
        "location": "456 Oak Ave, Westside",
        "category": "Fine Dining",
        "rating": 4.8,
        "priceRange": "$$$",
        "distance": "1.2 miles",
        "lastUpdated": "2025-03-28",
        "description": "An upscale restaurant specializing in contemporary American cuisine with a focus on seasonal ingredients and artistic presentation.",
        "website": "https://gourmetdelight.example.com",
        "phoneNumber": "(555) 987-6543",
        "openingHours": {
            "Monday": "Closed",
            "Tuesday": "5:00 PM - 10:00 PM",
            "Wednesday": "5:00 PM - 10:00 PM",
            "Thursday": "5:00 PM - 10:00 PM",
            "Friday": "5:00 PM - 11:00 PM",
            "Saturday": "5:00 PM - 11:00 PM",
            "Sunday": "5:00 PM - 9:00 PM"
        },
        "popularItems": [
            {"name": "Filet Mignon", "price": "$42.99", "popularity": 96},
            {"name": "Seared Scallops", "price": "$36.99", "popularity": 90},
            {"name": "Truffle Risotto", "price": "$28.99", "popularity": 88}
        ],
        "reviews": [
            {"author": "Emily R.", "rating": 5, "comment": "Exceptional dining experience!", "date": "2025-03-10"},
            {"author": "David L.", "rating": 5, "comment": "Worth every penny. The service is impeccable.", "date": "2025-03-18"},
            {"author": "Lisa K.", "rating": 4, "comment": "Beautiful ambiance and delicious food.", "date": "2025-03-22"}
        ],
        "priceComparison": {
            "averageMealPrice": "$38.99",
            "comparedToYou": "+25%",
            "comparedToArea": "+15%"
        }
    },
    {
        "id": "3",
        "name": "Quick Bites",
        "location": "789 Pine St, Northside",
        "category": "Fast Food",
        "rating": 3.9,
        "priceRange": "$",
        "distance": "0.8 miles",
        "lastUpdated": "2025-04-02",
        "description": "A fast-casual restaurant offering quick, affordable meals with a focus on burgers, sandwiches, and salads.",
        "website": "https://quickbites.example.com",
        "phoneNumber": "(555) 456-7890",
        "openingHours": {
            "Monday": "10:00 AM - 10:00 PM",
            "Tuesday": "10:00 AM - 10:00 PM",
            "Wednesday": "10:00 AM - 10:00 PM",
            "Thursday": "10:00 AM - 10:00 PM",
            "Friday": "10:00 AM - 12:00 AM",
            "Saturday": "10:00 AM - 12:00 AM",
            "Sunday": "11:00 AM - 9:00 PM"
        },
        "popularItems": [
            {"name": "Classic Burger", "price": "$7.99", "popularity": 94},
            {"name": "Chicken Sandwich", "price": "$6.99", "popularity": 89},
            {"name": "Caesar Salad", "price": "$5.99", "popularity": 82}
        ],
        "reviews": [
            {"author": "Tom B.", "rating": 4, "comment": "Great value for money!", "date": "2025-03-28"},
            {"author": "Amy W.", "rating": 3, "comment": "Food is good but service can be slow.", "date": "2025-04-01"},
            {"author": "Chris P.", "rating": 4, "comment": "Perfect for a quick lunch.", "date": "2025-04-02"}
        ],
        "priceComparison": {
            "averageMealPrice": "$8.99",
            "comparedToYou": "-30%",
            "comparedToArea": "-15%"
        }
    },
    {
        "id": "4",
        "name": "Spice Kingdom",
        "location": "321 Maple Rd, Eastside",
        "category": "Ethnic",
        "rating": 4.3,
        "priceRange": "$$",
        "distance": "1.5 miles",
        "lastUpdated": "2025-03-30",
        "description": "An authentic Indian restaurant offering a wide variety of traditional dishes with a modern twist.",
        "website": "https://spicekingdom.example.com",
        "phoneNumber": "(555) 789-0123",
        "openingHours": {
            "Monday": "11:00 AM - 9:30 PM",
            "Tuesday": "11:00 AM - 9:30 PM",
            "Wednesday": "11:00 AM - 9:30 PM",
            "Thursday": "11:00 AM - 9:30 PM",
            "Friday": "11:00 AM - 10:30 PM",
            "Saturday": "11:00 AM - 10:30 PM",
            "Sunday": "12:00 PM - 9:00 PM"
        },
        "popularItems": [
            {"name": "Butter Chicken", "price": "$16.99", "popularity": 97},
            {"name": "Vegetable Biryani", "price": "$14.99", "popularity": 90},
            {"name": "Garlic Naan", "price": "$3.99", "popularity": 95}
        ],
        "reviews": [
            {"author": "Rachel G.", "rating": 5, "comment": "Most authentic Indian food in the city!", "date": "2025-03-15"},
            {"author": "Mark H.", "rating": 4, "comment": "Delicious food with generous portions.", "date": "2025-03-25"},
            {"author": "Sophia L.", "rating": 4, "comment": "Great flavors and friendly staff.", "date": "2025-03-30"}
        ],
        "priceComparison": {
            "averageMealPrice": "$18.99",
            "comparedToYou": "-8%",
            "comparedToArea": "+5%"
        }
    },
    {
        "id": "5",
        "name": "Fresh & Healthy",
        "location": "654 Cedar Ln, Southside",
        "category": "Health Food",
        "rating": 4.6,
        "priceRange": "$$",
        "distance": "0.7 miles",
        "lastUpdated": "2025-04-03",
        "description": "A health-focused restaurant offering nutritious meals, smoothies, and juices made with organic ingredients.",
        "website": "https://freshandhealthy.example.com",
        "phoneNumber": "(555) 321-6547",
        "openingHours": {
            "Monday": "7:00 AM - 8:00 PM",
            "Tuesday": "7:00 AM - 8:00 PM",
            "Wednesday": "7:00 AM - 8:00 PM",
            "Thursday": "7:00 AM - 8:00 PM",
            "Friday": "7:00 AM - 8:00 PM",
            "Saturday": "8:00 AM - 7:00 PM",
            "Sunday": "8:00 AM - 6:00 PM"
        },
        "popularItems": [
            {"name": "Acai Bowl", "price": "$11.99", "popularity": 93},
            {"name": "Green Smoothie", "price": "$7.99", "popularity": 91},
            {"name": "Quinoa Salad", "price": "$13.99", "popularity": 88}
        ],
        "reviews": [
            {"author": "Jessica T.", "rating": 5, "comment": "Best healthy options in town!", "date": "2025-03-20"},
            {"author": "Brian K.", "rating": 4, "comment": "Fresh ingredients and tasty meals.", "date": "2025-03-28"},
            {"author": "Olivia M.", "rating": 5, "comment": "Love their smoothies and bowls!", "date": "2025-04-02"}
        ],
        "priceComparison": {
            "averageMealPrice": "$13.99",
            "comparedToYou": "-12%",
            "comparedToArea": "+8%"
        }
    }
]

@router.get("/")
async def get_competitors() -> List[Competitor]:
    """
    Get all competitors
    """
    return COMPETITORS

@router.get("/{competitor_id}")
async def get_competitor(competitor_id: str) -> CompetitorDetail:
    """
    Get a competitor by ID
    """
    for competitor in COMPETITORS:
        if competitor["id"] == competitor_id:
            return competitor
    
    raise HTTPException(status_code=404, detail="Competitor not found")

@router.get("/categories")
async def get_categories() -> List[str]:
    """
    Get all unique competitor categories
    """
    categories = set()
    for competitor in COMPETITORS:
        categories.add(competitor["category"])
    
    return sorted(list(categories))

class CompetitorCreate(BaseModel):
    name: str
    location: str
    category: str
    rating: float
    priceRange: str
    distance: str
    description: str
    website: str
    phoneNumber: str

@router.post("/")
async def create_competitor(competitor: CompetitorCreate) -> Competitor:
    """
    Create a new competitor
    """
    # In a real implementation, this would add to a database
    # For now, we'll just return a mock response
    
    new_id = str(len(COMPETITORS) + 1)
    
    new_competitor = {
        "id": new_id,
        "name": competitor.name,
        "location": competitor.location,
        "category": competitor.category,
        "rating": competitor.rating,
        "priceRange": competitor.priceRange,
        "distance": competitor.distance,
        "lastUpdated": "2025-04-05",
        "description": competitor.description,
        "website": competitor.website,
        "phoneNumber": competitor.phoneNumber,
        "openingHours": {
            "Monday": "9:00 AM - 9:00 PM",
            "Tuesday": "9:00 AM - 9:00 PM",
            "Wednesday": "9:00 AM - 9:00 PM",
            "Thursday": "9:00 AM - 9:00 PM",
            "Friday": "9:00 AM - 10:00 PM",
            "Saturday": "10:00 AM - 10:00 PM",
            "Sunday": "10:00 AM - 8:00 PM"
        },
        "popularItems": [],
        "reviews": [],
        "priceComparison": {
            "averageMealPrice": "$0.00",
            "comparedToYou": "0%",
            "comparedToArea": "0%"
        }
    }
    
    # In a real implementation, we would add this to the database
    # COMPETITORS.append(new_competitor)
    
    return new_competitor
