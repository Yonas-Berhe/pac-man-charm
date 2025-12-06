"""
Tests for user endpoints.
"""

import pytest


class TestGetCurrentUser:
    """Tests for GET /api/v1/users/me."""

    def test_get_current_user_success(self, client, auth_headers):
        """Test getting current user profile."""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "test_user"
        assert data["email"] == "test@example.com"

    def test_get_current_user_no_auth(self, client):
        """Test getting current user without auth."""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401


class TestUpdateCurrentUser:
    """Tests for PATCH /api/v1/users/me."""

    def test_update_username(self, client, auth_headers):
        """Test updating username."""
        response = client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"username": "updated_user"}
        )
        assert response.status_code == 200
        assert response.json()["username"] == "updated_user"

    def test_update_avatar(self, client, auth_headers):
        """Test updating avatar URL."""
        response = client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"avatar_url": "https://example.com/avatar.png"}
        )
        assert response.status_code == 200
        assert response.json()["avatar_url"] == "https://example.com/avatar.png"

    def test_update_duplicate_username(self, client, auth_headers):
        """Test updating to existing username."""
        response = client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"username": "demo_player"}  # Already exists
        )
        assert response.status_code == 400


class TestGetUserById:
    """Tests for GET /api/v1/users/{user_id}."""

    def test_get_user_success(self, client, auth_headers):
        """Test getting user by ID."""
        # First get current user to get ID
        me_response = client.get("/api/v1/users/me", headers=auth_headers)
        user_id = me_response.json()["id"]

        # Get user by ID (public endpoint)
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["username"] == "test_user"
        # Should not include email (public profile)
        assert "email" not in response.json()

    def test_get_user_not_found(self, client):
        """Test getting non-existent user."""
        response = client.get("/api/v1/users/nonexistent-id")
        assert response.status_code == 404


class TestGetUserStats:
    """Tests for GET /api/v1/users/{user_id}/stats."""

    def test_get_stats_success(self, client, demo_auth_headers):
        """Test getting user stats."""
        # Get demo user ID
        me_response = client.get("/api/v1/users/me", headers=demo_auth_headers)
        user_id = me_response.json()["id"]

        response = client.get(f"/api/v1/users/{user_id}/stats")
        assert response.status_code == 200
        data = response.json()
        assert "gamesPlayed" in data
        assert "gamesWon" in data
        assert "gamesLost" in data
        assert "winRate" in data
        assert "highScore" in data

    def test_get_stats_not_found(self, client):
        """Test getting stats for non-existent user."""
        response = client.get("/api/v1/users/nonexistent-id/stats")
        assert response.status_code == 404
