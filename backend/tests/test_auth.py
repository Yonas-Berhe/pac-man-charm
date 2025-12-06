"""
Tests for authentication endpoints.
"""

import pytest


class TestRegister:
    """Tests for POST /api/v1/auth/register."""

    def test_register_success(self, client):
        """Test successful registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "new_user",
                "email": "new@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["user"]["username"] == "new_user"
        assert data["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self, client):
        """Test registration with existing email."""
        # First registration
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "user1",
                "email": "same@example.com",
                "password": "password123"
            }
        )
        # Second registration with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "same@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 409

    def test_register_duplicate_username(self, client):
        """Test registration with existing username."""
        # First registration
        client.post(
            "/api/v1/auth/register",
            json={
                "username": "same_user",
                "email": "first@example.com",
                "password": "password123"
            }
        )
        # Second registration with same username
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "same_user",
                "email": "second@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        """Test registration with invalid email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "new_user",
                "email": "not-an-email",
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_register_short_password(self, client):
        """Test registration with short password."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "new_user",
                "email": "new@example.com",
                "password": "short"
            }
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    def test_login_success(self, client):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo@example.com",
                "password": "demo1234"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data
        assert data["user"]["username"] == "demo_player"

    def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401

    def test_login_invalid_password(self, client):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401


class TestLogout:
    """Tests for POST /api/v1/auth/logout."""

    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    def test_logout_no_auth(self, client):
        """Test logout without authentication."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401


class TestRefreshToken:
    """Tests for POST /api/v1/auth/refresh."""

    def test_refresh_success(self, client):
        """Test successful token refresh."""
        # First login to get refresh token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "demo@example.com",
                "password": "demo1234"
            }
        )
        refresh_token = login_response.json()["refreshToken"]

        # Use refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert "refreshToken" in data

    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": "invalid-token"}
        )
        assert response.status_code == 401
