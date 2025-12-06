"""
Integration test: Authentication flows.
Tests token lifecycle, refresh, and logout with real database.
"""

import pytest


@pytest.mark.asyncio
class TestAuthenticationFlow:
    """Test authentication mechanisms with persistent storage."""

    @pytest.mark.asyncio
    async def test_token_refresh_flow(self, client):
        """Test access token refresh using refresh token."""
        
        # Register
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "refresh_user",
                "email": "refresh@test.com",
                "password": "password123"
            }
        )
        assert reg.status_code == 201
        original_access = reg.json()["accessToken"]
        refresh_token = reg.json()["refreshToken"]
        
        # Use refresh token to get new access token
        refresh_response = await client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_access = refresh_response.json()["accessToken"]
        new_refresh = refresh_response.json()["refreshToken"]
        
        # Tokens should be different
        assert new_access != original_access
        assert new_refresh != refresh_token
        
        # New access token should work
        me = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {new_access}"}
        )
        assert me.status_code == 200
        assert me.json()["username"] == "refresh_user"
        
        # Old refresh token should be revoked
        old_refresh = await client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": refresh_token}
        )
        assert old_refresh.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_revokes_tokens(self, client):
        """Test that logout properly revokes all tokens."""
        
        # Register
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "logout_user",
                "email": "logout@test.com",
                "password": "password123"
            }
        )
        access_token = reg.json()["accessToken"]
        refresh_token = reg.json()["refreshToken"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Logout
        logout = await client.post("/api/v1/auth/logout", headers=headers)
        assert logout.status_code == 200
        
        # Refresh token should no longer work
        refresh = await client.post(
            "/api/v1/auth/refresh",
            json={"refreshToken": refresh_token}
        )
        assert refresh.status_code == 401

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, client):
        """Test multiple login sessions for same user."""
        
        # Register
        await client.post(
            "/api/v1/auth/register",
            json={
                "username": "multi_session",
                "email": "multi@test.com",
                "password": "password123"
            }
        )
        
        # Login twice (simulating two devices)
        login1 = await client.post(
            "/api/v1/auth/login",
            json={"email": "multi@test.com", "password": "password123"}
        )
        login2 = await client.post(
            "/api/v1/auth/login",
            json={"email": "multi@test.com", "password": "password123"}
        )
        
        token1 = login1.json()["accessToken"]
        token2 = login2.json()["accessToken"]
        
        # Both sessions should work
        me1 = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token1}"}
        )
        me2 = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert me1.status_code == 200
        assert me2.status_code == 200
