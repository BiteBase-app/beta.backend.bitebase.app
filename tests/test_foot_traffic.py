import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.apis.foot_traffic import DateRangeEnum

@pytest.mark.parametrize("date_range", [
    DateRangeEnum.day,
    DateRangeEnum.week,
    DateRangeEnum.month,
    DateRangeEnum.year
])
def test_get_foot_traffic_data(client: TestClient, date_range: DateRangeEnum):
    """Test the foot traffic data endpoint with different date ranges."""
    response = client.get(f"/foot_traffic/?date_range={date_range}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert f"Foot traffic data for {date_range}" in data["message"]
    assert "data" in data
    assert "summary" in data["data"]
    assert "hourlyData" in data["data"]
    assert "dailyData" in data["data"]
    assert "visitorTypes" in data["data"]
    assert "conversionRates" in data["data"]

def test_get_traffic_summary(client: TestClient):
    """Test the traffic summary endpoint."""
    response = client.get("/foot_traffic/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Traffic summary" in data["message"]
    assert "data" in data
    assert "totalVisitors" in data["data"]
    assert "averageDaily" in data["data"]
    assert "peakHour" in data["data"]
    assert "peakDay" in data["data"]
    assert "changePercentage" in data["data"]

def test_get_hourly_traffic(client: TestClient):
    """Test the hourly traffic endpoint."""
    response = client.get("/foot_traffic/hourly")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Hourly traffic data" in data["message"]
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    assert "hour" in data["data"][0]
    assert "visitors" in data["data"][0]
    assert "percentage" in data["data"][0]

def test_get_daily_traffic(client: TestClient):
    """Test the daily traffic endpoint."""
    response = client.get("/foot_traffic/daily")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Daily traffic data" in data["message"]
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    assert "day" in data["data"][0]
    assert "visitors" in data["data"][0]
    assert "percentage" in data["data"][0]

def test_get_visitor_types(client: TestClient):
    """Test the visitor types endpoint."""
    response = client.get("/foot_traffic/visitor-types")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Visitor type data" in data["message"]
    assert "data" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    assert "type" in data["data"][0]
    assert "percentage" in data["data"][0]

def test_get_conversion_rates(client: TestClient):
    """Test the conversion rates endpoint."""
    response = client.get("/foot_traffic/conversion-rates")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Conversion rate data" in data["message"]
    assert "data" in data
    assert "visitorToCustomer" in data["data"]
    assert "customerToRepeat" in data["data"]

def test_get_heatmap_data(client: TestClient):
    """Test the heatmap data endpoint."""
    response = client.get("/foot_traffic/heatmap")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Heatmap data retrieved successfully" in data["message"]
    assert "data" in data
    assert "highTrafficAreas" in data["data"]
    assert "lowTrafficAreas" in data["data"]
    assert "optimizationTips" in data["data"]
    assert isinstance(data["data"]["highTrafficAreas"], list)
    assert isinstance(data["data"]["lowTrafficAreas"], list)
    assert isinstance(data["data"]["optimizationTips"], list)

@patch("app.apis.foot_traffic.log_error")
def test_error_handling(mock_log_error, client: TestClient):
    """Test error handling in the foot traffic API."""
    # This test would be more comprehensive with a real error scenario
    # For now, we're just checking that the endpoints don't raise exceptions
    endpoints = [
        "/foot_traffic/",
        "/foot_traffic/summary",
        "/foot_traffic/hourly",
        "/foot_traffic/daily",
        "/foot_traffic/visitor-types",
        "/foot_traffic/conversion-rates",
        "/foot_traffic/heatmap"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code in [200, 401, 403, 404]  # Valid status codes
        
    # Verify log_error was not called
    mock_log_error.assert_not_called()
