import pytest
from fastapi.testclient import TestClient

def test_test_endpoint(client: TestClient):
    """Test the test endpoint."""
    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "environment" in data
    assert "firebase_configured" in data
    assert "routes_loaded" in data
    assert "api_version" in data

def test_health_endpoint(client: TestClient):
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
