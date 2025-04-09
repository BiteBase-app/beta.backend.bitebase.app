from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    data: Dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
    status: str = "success"

class User(BaseModel):
    """User model representing a system user"""
    id: str
    email: str
    name: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None

class Restaurant(BaseModel):
    """Restaurant model representing a restaurant business"""
    id: str
    name: str
    location: str
    cuisine_type: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    rating: Optional[float] = None
    price_range: Optional[str] = None
    image_url: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    contact: Optional[Dict[str, Any]] = None
    hours: Optional[Dict[str, List[str]]] = None
    tags: List[str] = Field(default_factory=list)

class AnalyticsData(BaseModel):
    """Model for restaurant analytics data points"""
    id: str
    restaurant_id: str
    metric_type: str  # e.g., 'foot_traffic', 'sales', 'reviews'
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)