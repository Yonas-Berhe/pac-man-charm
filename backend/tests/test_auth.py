"""
Tests for authentication endpoints.
"""

import pytest


class TestRegister:
    """Tests for POST /auth/register."""

    @pytest.mark.asyncio
    async def test_register_success(self, client):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user"]["username"] == "newuser"
        assert data["user"]["email"] == "newuser@example.com"
        assert "accessToken" in data
        assert "refreshToken" in data
        assert "expiresIn" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client):
        """Test registration with existing email."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user1",
                "email": "dup@example.com",
                "password": "password123"
            }
        )
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "user2",
                "email": "dup@example.com",
                "password": "password456"
            }
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client):
        """Test registration with existing username."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "dupuser",
                "email": "user1@example.com",
                "password": "password123"
            }
        )
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "dupuser",
                "email": "user2@example.com",
                "password": "password456"
            }
        )
        assert response.status_code == 409


class TestLogin:
    """Tests for POST /auth/login."""

    @pytest.mark.asyncio
    async def test_login_success(self, client):
        """Test successful login."""
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "password123"
            }
        )
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == "login@example.com"
        assert "accessToken" in data

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client):
        """Test login with non-existent email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client):
        """Test login with wrong password."""
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "wrongpass",
                "email": "wrongpass@example.com",
                "password": "correctpass"
            }
        )
        
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrongpass@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401


class TestLogout:
    """Tests for POST /auth/logout."""

    @pytest.mark.asyncio
    async def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = await client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    @pytest.mark.asyncio
    async def test_logout_no_auth(self, client):
        """Test logout without authentication."""
        response = await client.post("/api/v1/auth/logout")
        assert response.status_code == 401
