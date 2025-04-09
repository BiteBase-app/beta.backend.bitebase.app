import os
import pytest
from fastapi.testclient import TestClient

# Set environment to test
os.environ["ENVIRONMENT"] = "test"

# Import app after setting environment
from main import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_firebase_token():
    """Return a mock Firebase token for testing."""
    return "mock_firebase_token"

@pytest.fixture
def mock_user():
    """Return a mock user for testing."""
    return {
        "sub": "test_user_id",
        "user_id": "test_user_id",
        "name": "Test User",
        "email": "test@example.com",
        "picture": "https://example.com/test.jpg"
    }
