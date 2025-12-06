"""
Tests for health endpoint.
"""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health endpoint returns OK status."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
