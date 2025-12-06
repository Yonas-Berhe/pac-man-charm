"""
Tests for user endpoints.
"""

import pytest


class TestGetCurrentUser:
    """Tests for GET /users/me."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client, auth_headers):
        """Test getting current user profile."""
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "test_user"
        assert data["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401


class TestUpdateCurrentUser:
    """Tests for PATCH /users/me."""

    @pytest.mark.asyncio
    async def test_update_username(self, client, auth_headers):
        """Test updating username."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"username": "newusername"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["username"] == "newusername"

    @pytest.mark.asyncio
    async def test_update_avatar(self, client, auth_headers):
        """Test updating avatar URL."""
        response = await client.patch(
            "/api/v1/users/me",
            json={"avatar_url": "https://example.com/avatar.png"},
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["avatar_url"] == "https://example.com/avatar.png"

    @pytest.mark.asyncio
    async def test_update_duplicate_username(self, client, auth_headers):
        """Test updating to existing username."""
        # Register another user first
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "existing_user",
                "email": "existing@example.com",
                "password": "password123"
            }
        )
        
        response = await client.patch(
            "/api/v1/users/me",
            json={"username": "existing_user"},
            headers=auth_headers
        )
        assert response.status_code == 409


class TestGetUserById:
    """Tests for GET /users/{user_id}."""

    @pytest.mark.asyncio
    async def test_get_user_success(self, client, auth_headers):
        """Test getting user by ID."""
        # Get current user ID
        me_response = await client.get("/api/v1/users/me", headers=auth_headers)
        user_id = me_response.json()["id"]
        
        response = await client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["username"] == "test_user"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client):
        """Test getting non-existent user."""
        response = await client.get("/api/v1/users/nonexistent-id")
        assert response.status_code == 404


class TestGetUserStats:
    """Tests for GET /users/{user_id}/stats."""

    @pytest.mark.asyncio
    async def test_get_stats_success(self, client, auth_headers):
        """Test getting user stats."""
        me_response = await client.get("/api/v1/users/me", headers=auth_headers)
        user_id = me_response.json()["id"]
        
        response = await client.get(f"/api/v1/users/{user_id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert "gamesPlayed" in data
        assert "highScore" in data
        assert "winRate" in data

    @pytest.mark.asyncio
    async def test_get_stats_not_found(self, client):
        """Test getting stats for non-existent user."""
        response = await client.get("/api/v1/users/nonexistent-id/stats")
        assert response.status_code == 404
