from fastapi import APIRouter, Query, HTTPException, Path, Body
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import random

router = APIRouter()

# Models for reports
class ReportType(str, Enum):
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    ANALYTICS = "analytics"
    MARKETING = "marketing"
    HR = "hr"
    INVENTORY = "inventory"
    CUSTOM = "custom"

class ReportFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    ONCE = "once"

class ReportFormat(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "excel"
    HTML = "html"
    JSON = "json"

class ReportMetric(BaseModel):
    name: str
    value: Union[int, float, str]
    change: Optional[float] = None
    trend: Optional[str] = None
    format: Optional[str] = None

class ReportDataPoint(BaseModel):
    date: datetime
    orders: int
    revenue: float
    avg_order: float
    profit: float

class ReportTemplate(BaseModel):
    id: str
    name: str
    description: str
    type: ReportType
    category: str
    popularity: str  # "High", "Medium", "Low"
    default_settings: Dict[str, Any] = {}

class ScheduledReport(BaseModel):
    id: str
    name: str
    template_id: str
    frequency: ReportFrequency
    day: str
    recipients: List[str]
    last_sent: Optional[datetime] = None
    next_scheduled: Optional[datetime] = None
    settings: Dict[str, Any] = {}
    active: bool = True

class Report(BaseModel):
    id: str
    name: str
    description: str
    type: ReportType
    created_at: datetime
    updated_at: Optional[datetime] = None
    generated_by: str
    starred: bool = False
    metrics: Optional[List[ReportMetric]] = None
    data_points: Optional[List[ReportDataPoint]] = None
    insights: Optional[List[str]] = None
    settings: Dict[str, Any] = {}

# Sample data for reports
sample_reports = [
    Report(
        id="rep-001",
        name="Monthly Sales Performance",
        description="Comprehensive analysis of sales with trend comparison",
        type=ReportType.FINANCIAL,
        created_at=datetime.now() - timedelta(days=5),
        updated_at=datetime.now() - timedelta(days=2),
        generated_by="admin@example.com",
        starred=True,
        metrics=[
            ReportMetric(name="Total Revenue", value=24389, change=12.5, trend="up", format="currency"),
            ReportMetric(name="Average Order", value=32.80, change=3.2, trend="up", format="currency"),
            ReportMetric(name="Customer Count", value=2451, change=8.7, trend="up", format="number"),
            ReportMetric(name="Profit Margin", value=23.4, change=-1.2, trend="down", format="percentage")
        ],
        insights=[
            "Sales have increased by 12.5% compared to last month",
            "The dinner service has seen the highest growth at 18%",
            "Online orders now represent 35% of total sales",
            "Seafood dishes are showing the strongest category growth"
        ]
    ),
    Report(
        id="rep-002",
        name="Customer Traffic Analysis",
        description="Foot traffic patterns and peak hours",
        type=ReportType.ANALYTICS,
        created_at=datetime.now() - timedelta(days=8),
        updated_at=datetime.now() - timedelta(days=8),
        generated_by="admin@example.com",
        starred=True,
        metrics=[
            ReportMetric(name="Daily Average Traffic", value=450, change=5.2, trend="up", format="number"),
            ReportMetric(name="Peak Hour Traffic", value=68, change=7.1, trend="up", format="number"),
            ReportMetric(name="Weekend Increase", value=32, change=3.5, trend="up", format="percentage"),
            ReportMetric(name="Conversion Rate", value=42, change=-0.5, trend="down", format="percentage")
        ],
        insights=[
            "Peak hours are between 12-1pm and 6-8pm",
            "Saturday evening has the highest foot traffic",
            "Foot traffic increases 15% during promotional events",
            "The bar area sees 28% of total customer traffic"
        ]
    ),
    Report(
        id="rep-003",
        name="Menu Item Performance",
        description="Profitability and popularity of menu items",
        type=ReportType.OPERATIONAL,
        created_at=datetime.now() - timedelta(days=10),
        generated_by="admin@example.com",
        metrics=[
            ReportMetric(name="Top Seller", value="Signature Burger", format="text"),
            ReportMetric(name="Most Profitable Item", value="Seafood Pasta", format="text"),
            ReportMetric(name="Average Item Profit", value=8.35, change=1.2, trend="up", format="currency"),
            ReportMetric(name="Menu Item Count", value=42, change=-3, trend="down", format="number")
        ],
        insights=[
            "The top 5 items represent 40% of total sales",
            "Dessert orders have increased by 18% since menu redesign",
            "Vegetarian options are showing 25% growth compared to last quarter",
            "Items with photos on the menu sell 22% better than those without"
        ]
    ),
    Report(
        id="rep-004",
        name="Competitive Landscape",
        description="Analysis of nearby competitors and market share",
        type=ReportType.MARKETING,
        created_at=datetime.now() - timedelta(days=25),
        generated_by="admin@example.com",
        metrics=[
            ReportMetric(name="Competitor Count", value=12, format="number"),
            ReportMetric(name="Price Position", value="15% above average", format="text"),
            ReportMetric(name="Market Share", value=8.5, change=0.7, trend="up", format="percentage"),
            ReportMetric(name="Average Competitor Rating", value=4.1, format="rating")
        ],
        insights=[
            "Two new competitors opened in the last quarter",
            "Your restaurant ranks 3rd in online reviews out of 15 similar establishments",
            "Your pricing is 12% higher than the market average",
            "Your signature dishes have limited competition in the area"
        ]
    ),
    Report(
        id="rep-005",
        name="Staff Productivity Report",
        description="Performance metrics for staff and shifts",
        type=ReportType.HR,
        created_at=datetime.now() - timedelta(days=32),
        generated_by="admin@example.com",
        metrics=[
            ReportMetric(name="Sales per Staff Hour", value=75.40, change=3.1, trend="up", format="currency"),
            ReportMetric(name="Average Tables per Server", value=5.2, change=0.3, trend="up", format="number"),
            ReportMetric(name="Staff Turnover Rate", value=12, change=-5, trend="down", format="percentage"),
            ReportMetric(name="Training Hours", value=45, change=15, trend="up", format="number")
        ],
        insights=[
            "Evening shifts are 35% more productive than lunch shifts",
            "Staff with 6+ months experience serve 24% more customers per hour",
            "The new incentive program has reduced turnover by 5%",
            "Cross-training has improved kitchen efficiency by 12%"
        ]
    )
]

# Generate sample data points for a report
def generate_report_data_points(days=30):
    data_points = []
    base_date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        # Create realistic fluctuations
        current_date = base_date + timedelta(days=i)
        # More orders on weekends
        is_weekend = current_date.weekday() >= 5
        
        # Base numbers with randomness
        orders = random.randint(60, 100)
        if is_weekend:
            orders += random.randint(20, 40)
            
        # Revenue per order with some randomness
        avg_order = random.uniform(25.0, 40.0)
        revenue = orders * avg_order
        
        # Profit is typically 20-30% of revenue
        profit_margin = random.uniform(0.2, 0.3)
        profit = revenue * profit_margin
        
        data_points.append(ReportDataPoint(
            date=current_date,
            orders=orders,
            revenue=round(revenue, 2),
            avg_order=round(avg_order, 2),
            profit=round(profit, 2)
        ))
    
    return data_points

# Sample templates
sample_templates = [
    ReportTemplate(
        id="temp-001",
        name="Sales Performance Report",
        description="Daily, weekly, or monthly sales analysis",
        type=ReportType.FINANCIAL,
        category="Financial",
        popularity="High",
        default_settings={
            "include_charts": True,
            "compare_to_previous": True,
            "metrics": ["revenue", "orders", "avg_order", "profit"]
        }
    ),
    ReportTemplate(
        id="temp-002",
        name="Inventory Management",
        description="Stock levels, usage, and wastage tracking",
        type=ReportType.INVENTORY,
        category="Operations",
        popularity="Medium",
        default_settings={
            "include_charts": True,
            "highlight_low_stock": True,
            "wastage_threshold": 5
        }
    ),
    ReportTemplate(
        id="temp-003",
        name="Customer Insights",
        description="Demographics, preferences, and feedback",
        type=ReportType.MARKETING,
        category="Marketing",
        popularity="High",
        default_settings={
            "include_reviews": True,
            "sentiment_analysis": True,
            "group_by_demographics": True
        }
    ),
    ReportTemplate(
        id="temp-004",
        name="Location Performance",
        description="Foot traffic and revenue by location",
        type=ReportType.ANALYTICS,
        category="Analytics",
        popularity="Medium",
        default_settings={
            "include_maps": True,
            "traffic_heatmap": True,
            "compare_locations": True
        }
    ),
    ReportTemplate(
        id="temp-005",
        name="Staff Performance",
        description="Productivity, scheduling, and labor costs",
        type=ReportType.HR,
        category="HR",
        popularity="Low",
        default_settings={
            "include_individual_metrics": True,
            "compare_shifts": True,
            "track_overtime": True
        }
    )
]

# Sample scheduled reports
sample_schedules = [
    ScheduledReport(
        id="sched-001",
        name="Weekly Sales Summary",
        template_id="temp-001",
        frequency=ReportFrequency.WEEKLY,
        day="Monday",
        recipients=["management@example.com", "finance@example.com"],
        last_sent=datetime.now() - timedelta(days=6),
        next_scheduled=datetime.now() + timedelta(days=1),
        settings={
            "include_charts": True,
            "compare_to_previous": True,
            "format": ReportFormat.PDF
        }
    ),
    ScheduledReport(
        id="sched-002",
        name="Monthly Financial Report",
        template_id="temp-001",
        frequency=ReportFrequency.MONTHLY,
        day="1st",
        recipients=["finance@example.com", "ceo@example.com"],
        last_sent=datetime.now() - timedelta(days=14),
        next_scheduled=datetime.now() + timedelta(days=16),
        settings={
            "include_charts": True,
            "include_projections": True,
            "format": ReportFormat.EXCEL
        }
    ),
    ScheduledReport(
        id="sched-003",
        name="Daily Operations Overview",
        template_id="temp-002",
        frequency=ReportFrequency.DAILY,
        day="Every day",
        recipients=["operations@example.com"],
        last_sent=datetime.now() - timedelta(days=1),
        next_scheduled=datetime.now(),
        settings={
            "highlight_low_stock": True,
            "include_tasks": True,
            "format": ReportFormat.HTML
        }
    )
]

# Generate data points for first report
sample_reports[0].data_points = generate_report_data_points(30)

# API Routes
@router.get("/", response_model=List[Report])
async def get_reports(
    type: Optional[ReportType] = None,
    search: Optional[str] = None,
    starred: Optional[bool] = None,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """Get a list of reports with optional filtering"""
    filtered = sample_reports
    
    if type:
        filtered = [r for r in filtered if r.type == type]
        
    if search:
        filtered = [r for r in filtered if search.lower() in r.name.lower() or search.lower() in r.description.lower()]
        
    if starred is not None:
        filtered = [r for r in filtered if r.starred == starred]
        
    # Apply pagination
    paginated = filtered[skip:skip + limit]
    
    return paginated

@router.get("/{report_id}", response_model=Report)
async def get_report(report_id: str = Path(..., title="The ID of the report to retrieve")):
    """Get detailed information about a specific report"""
    report = next((r for r in sample_reports if r.id == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Ensure the report has data points
    if not report.data_points:
        report.data_points = generate_report_data_points(30)
        
    return report

@router.post("/", response_model=Report)
async def create_report(
    name: str = Body(...),
    description: str = Body(...),
    type: ReportType = Body(...),
    template_id: Optional[str] = Body(None),
    settings: Dict[str, Any] = Body({})
):
    """Create a new report"""
    # In a real app, this would generate a report based on the provided settings
    # For now, we'll just create a sample report with the provided information
    
    new_report = Report(
        id=f"rep-{len(sample_reports) + 1:03d}",
        name=name,
        description=description,
        type=type,
        created_at=datetime.now(),
        generated_by="admin@example.com",
        settings=settings
    )
    
    # If using a template, apply template settings
    if template_id:
        template = next((t for t in sample_templates if t.id == template_id), None)
        if template:
            # Apply template default settings, but user settings take precedence
            combined_settings = {**template.default_settings, **settings}
            new_report.settings = combined_settings
    
    # Generate sample data for the new report
    new_report.data_points = generate_report_data_points(30)
    
    # Add some sample metrics
    new_report.metrics = [
        ReportMetric(name="Total Revenue", value=random.uniform(15000, 30000), format="currency"),
        ReportMetric(name="Average Order", value=random.uniform(25, 40), format="currency"),
        ReportMetric(name="Customer Count", value=random.randint(1500, 3000), format="number")
    ]
    
    # Add sample insights
    new_report.insights = [
        "Sample insight 1 for your new report",
        "Sample insight 2 for your new report",
        "Sample insight 3 for your new report"
    ]
    
    # Add to our sample data (in a real app, this would be saved to a database)
    sample_reports.append(new_report)
    
    return new_report

@router.put("/{report_id}/star", response_model=Report)
async def toggle_star_report(report_id: str = Path(..., title="The ID of the report to star/unstar")):
    """Toggle the starred status of a report"""
    report = next((r for r in sample_reports if r.id == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.starred = not report.starred
    return report

@router.delete("/{report_id}", status_code=204)
async def delete_report(report_id: str = Path(..., title="The ID of the report to delete")):
    """Delete a report"""
    global sample_reports
    report = next((r for r in sample_reports if r.id == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Remove the report from our sample data
    sample_reports = [r for r in sample_reports if r.id != report_id]
    return None

@router.get("/templates/", response_model=List[ReportTemplate])
async def get_report_templates(
    type: Optional[ReportType] = None,
    search: Optional[str] = None,
    popularity: Optional[str] = None
):
    """Get a list of report templates with optional filtering"""
    filtered = sample_templates
    
    if type:
        filtered = [t for t in filtered if t.type == type]
        
    if search:
        filtered = [t for t in filtered if search.lower() in t.name.lower() or search.lower() in t.description.lower()]
        
    if popularity:
        filtered = [t for t in filtered if t.popularity.lower() == popularity.lower()]
        
    return filtered

@router.get("/templates/{template_id}", response_model=ReportTemplate)
async def get_report_template(template_id: str = Path(..., title="The ID of the template to retrieve")):
    """Get detailed information about a specific report template"""
    template = next((t for t in sample_templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.get("/scheduled/", response_model=List[ScheduledReport])
async def get_scheduled_reports(
    frequency: Optional[ReportFrequency] = None,
    active: Optional[bool] = None
):
    """Get a list of scheduled reports with optional filtering"""
    filtered = sample_schedules
    
    if frequency:
        filtered = [s for s in filtered if s.frequency == frequency]
        
    if active is not None:
        filtered = [s for s in filtered if s.active == active]
        
    return filtered

@router.get("/scheduled/{schedule_id}", response_model=ScheduledReport)
async def get_scheduled_report(schedule_id: str = Path(..., title="The ID of the scheduled report to retrieve")):
    """Get detailed information about a specific scheduled report"""
    schedule = next((s for s in sample_schedules if s.id == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="Scheduled report not found")
    return schedule

@router.post("/scheduled/", response_model=ScheduledReport)
async def create_scheduled_report(
    name: str = Body(...),
    template_id: str = Body(...),
    frequency: ReportFrequency = Body(...),
    day: str = Body(...),
    recipients: List[str] = Body(...),
    settings: Dict[str, Any] = Body({})
):
    """Create a new scheduled report"""
    # Check if the template exists
    template = next((t for t in sample_templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Calculate next scheduled date based on frequency
    next_scheduled = datetime.now()
    if frequency == ReportFrequency.DAILY:
        next_scheduled += timedelta(days=1)
    elif frequency == ReportFrequency.WEEKLY:
        next_scheduled += timedelta(days=7)
    elif frequency == ReportFrequency.MONTHLY:
        next_scheduled += timedelta(days=30)
    elif frequency == ReportFrequency.QUARTERLY:
        next_scheduled += timedelta(days=90)
    elif frequency == ReportFrequency.ANNUAL:
        next_scheduled += timedelta(days=365)
    
    # Create the new scheduled report
    new_schedule = ScheduledReport(
        id=f"sched-{len(sample_schedules) + 1:03d}",
        name=name,
        template_id=template_id,
        frequency=frequency,
        day=day,
        recipients=recipients,
        next_scheduled=next_scheduled,
        settings=settings
    )
    
    # Apply template default settings if not overridden
    for key, value in template.default_settings.items():
        if key not in settings:
            new_schedule.settings[key] = value
    
    # Add to our sample data
    sample_schedules.append(new_schedule)
    
    return new_schedule

@router.put("/scheduled/{schedule_id}/send", response_model=ScheduledReport)
async def send_scheduled_report(schedule_id: str = Path(..., title="The ID of the scheduled report to send now")):
    """Send a scheduled report immediately (simulation)"""
    schedule = next((s for s in sample_schedules if s.id == schedule_id), None)
    if not schedule:
        raise HTTPException(status_code=404, detail="Scheduled report not found")
    
    # Update the last sent time and next scheduled time
    schedule.last_sent = datetime.now()
    
    # Update next scheduled time based on frequency
    if schedule.frequency == ReportFrequency.DAILY:
        schedule.next_scheduled = datetime.now() + timedelta(days=1)
    elif schedule.frequency == ReportFrequency.WEEKLY:
        schedule.next_scheduled = datetime.now() + timedelta(days=7)
    elif schedule.frequency == ReportFrequency.MONTHLY:
        schedule.next_scheduled = datetime.now() + timedelta(days=30)
    elif schedule.frequency == ReportFrequency.QUARTERLY:
        schedule.next_scheduled = datetime.now() + timedelta(days=90)
    elif schedule.frequency == ReportFrequency.ANNUAL:
        schedule.next_scheduled = datetime.now() + timedelta(days=365)
    
    return schedule 