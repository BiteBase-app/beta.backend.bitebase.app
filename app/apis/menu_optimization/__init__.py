from fastapi import APIRouter, HTTPException, Query, Path, Depends, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/menu-optimization", tags=["menu-optimization"])

# Menu item models
class MenuItemBase(BaseModel):
    name: str
    category: str
    price: float
    cost: float
    description: Optional[str] = None
    image_url: Optional[str] = None
    ingredients: Optional[List[str]] = None
    allergens: Optional[List[str]] = None
    is_vegetarian: Optional[bool] = False
    is_vegan: Optional[bool] = False
    is_gluten_free: Optional[bool] = False

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemSales(BaseModel):
    item_id: str
    quantity: int
    revenue: float
    date: datetime

class MenuItemPerformance(BaseModel):
    id: str
    name: str
    category: str
    price: float
    cost: float
    profit_margin: float
    popularity: float
    sales_count: int
    revenue: float
    description: Optional[str] = None
    image_url: Optional[str] = None
    trend: Optional[str] = None  # "up", "down", "stable"
    recommendation: Optional[str] = None  # "keep", "remove", "price_adjust", "promote"

class MenuCategory(BaseModel):
    id: str
    name: str
    item_count: int
    average_profit_margin: float
    total_sales: int
    total_revenue: float

class MenuAnalysis(BaseModel):
    complexity_score: float
    top_performers: List[MenuItemPerformance]
    low_performers: List[MenuItemPerformance]
    categories: List[MenuCategory]
    average_profit_margin: float
    menu_performance_score: float
    recommendations: List[str]

class MenuOptimizationResult(BaseModel):
    items_to_keep: List[str]
    items_to_promote: List[str]
    items_to_adjust_price: List[str]
    items_to_remove: List[str]
    suggested_new_items: List[str]
    complexity_recommendation: str
    estimated_profit_increase: float

# Sample data for demonstration
sample_menu_items = [
    {
        "id": "1",
        "name": "Classic Burger",
        "category": "Burgers",
        "price": 12.99,
        "cost": 4.50,
        "profit_margin": 65.36,
        "popularity": 92,
        "sales_count": 342,
        "revenue": 4442.58,
        "description": "Beef patty with lettuce, tomato, cheese and our special sauce",
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?q=80&w=300",
        "trend": "up",
        "recommendation": "keep"
    },
    {
        "id": "2",
        "name": "Veggie Burger",
        "category": "Burgers",
        "price": 11.99,
        "cost": 3.75,
        "profit_margin": 68.72,
        "popularity": 76,
        "sales_count": 187,
        "revenue": 2242.13,
        "description": "Plant-based patty with lettuce, tomato, and vegan mayo",
        "image_url": "https://images.unsplash.com/photo-1520072959219-c595dc870360?q=80&w=300",
        "trend": "up",
        "recommendation": "price_adjust"
    },
    {
        "id": "3",
        "name": "Chicken Sandwich",
        "category": "Sandwiches",
        "price": 10.99,
        "cost": 3.25,
        "profit_margin": 70.43,
        "popularity": 84,
        "sales_count": 256,
        "revenue": 2813.44,
        "description": "Grilled chicken breast with avocado, bacon and honey mustard",
        "image_url": "https://images.unsplash.com/photo-1606755962773-d324e0a13086?q=80&w=300",
        "trend": "stable",
        "recommendation": "keep"
    },
    {
        "id": "4",
        "name": "Caesar Salad",
        "category": "Salads",
        "price": 8.99,
        "cost": 2.50,
        "profit_margin": 72.19,
        "popularity": 65,
        "sales_count": 145,
        "revenue": 1303.55,
        "description": "Romaine lettuce, croutons, parmesan, and Caesar dressing",
        "image_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1?q=80&w=300",
        "trend": "stable",
        "recommendation": "price_adjust"
    },
    {
        "id": "5",
        "name": "Chocolate Lava Cake",
        "category": "Desserts",
        "price": 7.99,
        "cost": 2.25,
        "profit_margin": 71.84,
        "popularity": 89,
        "sales_count": 198,
        "revenue": 1582.02,
        "description": "Warm chocolate cake with a molten center, served with vanilla ice cream",
        "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?q=80&w=300",
        "trend": "up",
        "recommendation": "keep"
    },
    {
        "id": "6",
        "name": "Fish & Chips",
        "category": "Mains",
        "price": 14.99,
        "cost": 5.75,
        "profit_margin": 61.64,
        "popularity": 45,
        "sales_count": 98,
        "revenue": 1469.02,
        "description": "Battered cod with steak fries and tartar sauce",
        "image_url": "https://images.unsplash.com/photo-1580217593608-61e702099914?q=80&w=300",
        "trend": "down",
        "recommendation": "remove"
    },
    {
        "id": "7",
        "name": "Onion Rings",
        "category": "Sides",
        "price": 4.99,
        "cost": 1.25,
        "profit_margin": 74.95,
        "popularity": 52,
        "sales_count": 124,
        "revenue": 618.76,
        "description": "Crispy battered onion rings with dipping sauce",
        "image_url": "https://images.unsplash.com/photo-1639024471283-03518883512d?q=80&w=300",
        "trend": "down",
        "recommendation": "remove"
    }
]

sample_categories = [
    {
        "id": "1",
        "name": "Burgers",
        "item_count": 2,
        "average_profit_margin": 67.04,
        "total_sales": 529,
        "total_revenue": 6684.71
    },
    {
        "id": "2",
        "name": "Sandwiches",
        "item_count": 1,
        "average_profit_margin": 70.43,
        "total_sales": 256,
        "total_revenue": 2813.44
    },
    {
        "id": "3",
        "name": "Salads",
        "item_count": 1,
        "average_profit_margin": 72.19,
        "total_sales": 145,
        "total_revenue": 1303.55
    },
    {
        "id": "4",
        "name": "Mains",
        "item_count": 1,
        "average_profit_margin": 61.64,
        "total_sales": 98,
        "total_revenue": 1469.02
    },
    {
        "id": "5",
        "name": "Sides",
        "item_count": 1,
        "average_profit_margin": 74.95,
        "total_sales": 124,
        "total_revenue": 618.76
    },
    {
        "id": "6",
        "name": "Desserts",
        "item_count": 1,
        "average_profit_margin": 71.84,
        "total_sales": 198,
        "total_revenue": 1582.02
    }
]

sample_analysis = {
    "complexity_score": 6.5,
    "top_performers": [item for item in sample_menu_items if item["recommendation"] == "keep"],
    "low_performers": [item for item in sample_menu_items if item["recommendation"] == "remove"],
    "categories": sample_categories,
    "average_profit_margin": 67.4,
    "menu_performance_score": 78,
    "recommendations": [
        "Consider removing low-performing items like Fish & Chips and Onion Rings",
        "Increase price of Veggie Burger slightly to increase profit margin",
        "Consider adding a signature burger to capitalize on burger category performance",
        "Maintain a menu complexity score between 5-7 for optimal kitchen efficiency"
    ]
}

sample_optimization = {
    "items_to_keep": ["Classic Burger", "Chicken Sandwich", "Chocolate Lava Cake"],
    "items_to_promote": ["Classic Burger", "Chocolate Lava Cake"],
    "items_to_adjust_price": ["Veggie Burger", "Caesar Salad"],
    "items_to_remove": ["Fish & Chips", "Onion Rings"],
    "suggested_new_items": ["Signature Burger", "Loaded Fries", "Grilled Vegetable Salad"],
    "complexity_recommendation": "Your menu complexity score of 6.5 is in the optimal range (5-7)",
    "estimated_profit_increase": 12.5
}

@router.get("/menu-items", response_model=List[MenuItemPerformance])
async def get_menu_items(
    restaurant_id: Optional[str] = Query(None, description="Restaurant ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: Optional[str] = Query("popularity", description="Sort by field (popularity, profit_margin, sales_count, revenue)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)")
):
    """
    Get the list of menu items with performance data.
    """
    items = sample_menu_items
    
    # Filter by category if provided
    if category:
        items = [item for item in items if item["category"].lower() == category.lower()]
    
    # Sort items
    reverse = sort_order.lower() == "desc"
    if sort_by in ["popularity", "profit_margin", "sales_count", "revenue"]:
        items = sorted(items, key=lambda x: x[sort_by], reverse=reverse)
    
    return items

@router.get("/menu-items/{item_id}", response_model=MenuItemPerformance)
async def get_menu_item(
    item_id: str = Path(..., description="Menu item ID")
):
    """
    Get detailed information about a specific menu item.
    """
    item = next((item for item in sample_menu_items if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail=f"Menu item with ID {item_id} not found")
    
    return item

@router.get("/categories", response_model=List[MenuCategory])
async def get_menu_categories(
    restaurant_id: Optional[str] = Query(None, description="Restaurant ID"),
    sort_by: Optional[str] = Query("total_revenue", description="Sort by field (total_revenue, average_profit_margin, total_sales)"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)")
):
    """
    Get menu categories with performance data.
    """
    categories = sample_categories
    
    # Sort categories
    reverse = sort_order.lower() == "desc"
    if sort_by in ["total_revenue", "average_profit_margin", "total_sales", "item_count"]:
        categories = sorted(categories, key=lambda x: x[sort_by], reverse=reverse)
    
    return categories

@router.get("/analysis", response_model=MenuAnalysis)
async def get_menu_analysis(
    restaurant_id: Optional[str] = Query(None, description="Restaurant ID"),
    time_period: Optional[str] = Query("last_month", description="Time period for analysis (last_week, last_month, last_quarter, last_year)")
):
    """
    Get comprehensive menu analysis with performance metrics and recommendations.
    """
    return sample_analysis

@router.get("/optimization", response_model=MenuOptimizationResult)
async def get_menu_optimization(
    restaurant_id: Optional[str] = Query(None, description="Restaurant ID"),
    target: Optional[str] = Query("balanced", description="Optimization target (profit, popularity, balanced)")
):
    """
    Get menu optimization recommendations based on performance data.
    """
    return sample_optimization

@router.post("/simulate", response_model=MenuOptimizationResult)
async def simulate_menu_changes(
    restaurant_id: str,
    items_to_remove: List[str],
    items_to_add: List[MenuItemCreate],
    price_adjustments: dict
):
    """
    Simulate the impact of menu changes (adding/removing items, price adjustments).
    """
    # In a real implementation, this would calculate the projected impact
    # For demo purposes, returning the sample optimization
    return sample_optimization 