"""
Pytest configuration and fixtures.
"""

import pytest
from fastapi.testclient import TestClient

from main import app
from app.database import MockDatabase, db


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """Reset database before each test."""
    # Clear all data
    db.users.clear()
    db.games.clear()
    db.refresh_tokens.clear()
    # Recreate demo user
    db._create_demo_user()
    yield


@pytest.fixture
def auth_headers(client):
    """Get authentication headers for a new test user."""
    # Register a test user
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "test_user",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 201
    token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def demo_auth_headers(client):
    """Get authentication headers for the demo user."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "demo@example.com",
            "password": "demo1234"
        }
    )
    assert response.status_code == 200
    token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}
