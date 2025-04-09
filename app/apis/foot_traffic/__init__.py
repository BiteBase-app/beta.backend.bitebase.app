from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime, timedelta

router = APIRouter(prefix="/foot_traffic", tags=["foot_traffic"])

class DateRangeEnum(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"

class TrafficSummary(BaseModel):
    totalVisitors: int
    averageDaily: int
    peakHour: str
    peakDay: str
    changePercentage: str

class HourlyTraffic(BaseModel):
    hour: str
    visitors: int
    percentage: float

class DailyTraffic(BaseModel):
    day: str
    visitors: int
    percentage: float

class VisitorType(BaseModel):
    type: str
    percentage: int

class ConversionRates(BaseModel):
    visitorToCustomer: int
    customerToRepeat: int

class FootTrafficData(BaseModel):
    summary: TrafficSummary
    hourlyData: List[HourlyTraffic]
    dailyData: List[DailyTraffic]
    visitorTypes: List[VisitorType]
    conversionRates: ConversionRates

# Sample foot traffic data
FOOT_TRAFFIC_DATA = {
    "summary": {
        "totalVisitors": 4250,
        "averageDaily": 607,
        "peakHour": "6:00 PM - 7:00 PM",
        "peakDay": "Saturday",
        "changePercentage": "+8.5%"
    },
    "hourlyData": [
        {"hour": "6 AM", "visitors": 15, "percentage": 0.4},
        {"hour": "7 AM", "visitors": 45, "percentage": 1.1},
        {"hour": "8 AM", "visitors": 120, "percentage": 2.8},
        {"hour": "9 AM", "visitors": 180, "percentage": 4.2},
        {"hour": "10 AM", "visitors": 210, "percentage": 4.9},
        {"hour": "11 AM", "visitors": 320, "percentage": 7.5},
        {"hour": "12 PM", "visitors": 450, "percentage": 10.6},
        {"hour": "1 PM", "visitors": 380, "percentage": 8.9},
        {"hour": "2 PM", "visitors": 290, "percentage": 6.8},
        {"hour": "3 PM", "visitors": 240, "percentage": 5.6},
        {"hour": "4 PM", "visitors": 280, "percentage": 6.6},
        {"hour": "5 PM", "visitors": 420, "percentage": 9.9},
        {"hour": "6 PM", "visitors": 520, "percentage": 12.2},
        {"hour": "7 PM", "visitors": 480, "percentage": 11.3},
        {"hour": "8 PM", "visitors": 350, "percentage": 8.2},
        {"hour": "9 PM", "visitors": 210, "percentage": 4.9},
        {"hour": "10 PM", "visitors": 120, "percentage": 2.8},
        {"hour": "11 PM", "visitors": 60, "percentage": 1.4}
    ],
    "dailyData": [
        {"day": "Monday", "visitors": 520, "percentage": 12.2},
        {"day": "Tuesday", "visitors": 480, "percentage": 11.3},
        {"day": "Wednesday", "visitors": 510, "percentage": 12.0},
        {"day": "Thursday", "visitors": 550, "percentage": 12.9},
        {"day": "Friday", "visitors": 680, "percentage": 16.0},
        {"day": "Saturday", "visitors": 850, "percentage": 20.0},
        {"day": "Sunday", "visitors": 660, "percentage": 15.5}
    ],
    "visitorTypes": [
        {"type": "First-time", "percentage": 35},
        {"type": "Returning", "percentage": 45},
        {"type": "Regular", "percentage": 20}
    ],
    "conversionRates": {
        "visitorToCustomer": 68,
        "customerToRepeat": 42
    }
}

@router.get("/")
async def get_foot_traffic_data(date_range: DateRangeEnum = DateRangeEnum.week) -> FootTrafficData:
    """
    Get foot traffic data for the specified date range
    """
    # In a real implementation, this would filter data based on the date range
    # For now, we'll just return the sample data
    return FOOT_TRAFFIC_DATA

@router.get("/summary")
async def get_traffic_summary(date_range: DateRangeEnum = DateRangeEnum.week) -> TrafficSummary:
    """
    Get traffic summary for the specified date range
    """
    return FOOT_TRAFFIC_DATA["summary"]

@router.get("/hourly")
async def get_hourly_traffic(date_range: DateRangeEnum = DateRangeEnum.week) -> List[HourlyTraffic]:
    """
    Get hourly traffic data for the specified date range
    """
    return FOOT_TRAFFIC_DATA["hourlyData"]

@router.get("/daily")
async def get_daily_traffic(date_range: DateRangeEnum = DateRangeEnum.week) -> List[DailyTraffic]:
    """
    Get daily traffic data for the specified date range
    """
    return FOOT_TRAFFIC_DATA["dailyData"]

@router.get("/visitor-types")
async def get_visitor_types(date_range: DateRangeEnum = DateRangeEnum.week) -> List[VisitorType]:
    """
    Get visitor type distribution for the specified date range
    """
    return FOOT_TRAFFIC_DATA["visitorTypes"]

@router.get("/conversion-rates")
async def get_conversion_rates(date_range: DateRangeEnum = DateRangeEnum.week) -> ConversionRates:
    """
    Get conversion rates for the specified date range
    """
    return FOOT_TRAFFIC_DATA["conversionRates"]

class HeatmapData(BaseModel):
    highTrafficAreas: List[str]
    lowTrafficAreas: List[str]
    optimizationTips: List[str]

@router.get("/heatmap")
async def get_heatmap_data() -> HeatmapData:
    """
    Get store traffic heatmap data
    """
    return {
        "highTrafficAreas": [
            "Front entrance",
            "Main dining area",
            "Bar section"
        ],
        "lowTrafficAreas": [
            "Back corner tables",
            "Private dining room",
            "Outdoor patio (weekdays)"
        ],
        "optimizationTips": [
            "Rearrange seating in low traffic areas",
            "Add signage to highlight private dining",
            "Consider weekday patio promotions"
        ]
    }
