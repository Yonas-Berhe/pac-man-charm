"""
Tests for game endpoints.
"""

import pytest


class TestStartGame:
    """Tests for POST /games."""

    @pytest.mark.asyncio
    async def test_start_game_success(self, client, auth_headers):
        """Test starting a new game."""
        response = await client.post("/api/v1/games", headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_start_game_no_auth(self, client):
        """Test starting game without authentication."""
        response = await client.post("/api/v1/games")
        assert response.status_code == 401


class TestGetGameHistory:
    """Tests for GET /games."""

    @pytest.mark.asyncio
    async def test_get_history_success(self, client, auth_headers):
        """Test getting game history."""
        response = await client.get("/api/v1/games", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "games" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_history_no_auth(self, client):
        """Test getting history without authentication."""
        response = await client.get("/api/v1/games")
        assert response.status_code == 401


class TestGetGame:
    """Tests for GET /games/{game_id}."""

    @pytest.mark.asyncio
    async def test_get_game_success(self, client, auth_headers):
        """Test getting a specific game."""
        # Start a game first
        start_response = await client.post("/api/v1/games", headers=auth_headers)
        game_id = start_response.json()["id"]
        
        response = await client.get(f"/api/v1/games/{game_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == game_id

    @pytest.mark.asyncio
    async def test_get_game_not_found(self, client, auth_headers):
        """Test getting non-existent game."""
        response = await client.get("/api/v1/games/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_game_forbidden(self, client, auth_headers):
        """Test getting another user's game."""
        # Start a game as first user
        start_response = await client.post("/api/v1/games", headers=auth_headers)
        game_id = start_response.json()["id"]
        
        # Register second user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "otheruser",
                "email": "other@example.com",
                "password": "password123"
            }
        )
        other_token = register_response.json()["accessToken"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        response = await client.get(f"/api/v1/games/{game_id}", headers=other_headers)
        assert response.status_code == 403


class TestEndGame:
    """Tests for POST /games/{game_id}/end."""

    @pytest.mark.asyncio
    async def test_end_game_success(self, client, auth_headers):
        """Test ending a game."""
        # Start a game first
        start_response = await client.post("/api/v1/games", headers=auth_headers)
        game_id = start_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/games/{game_id}/end",
            json={
                "finalScore": 1000,
                "result": "won",
                "dotsCollected": 50,
                "ghostsEaten": 4
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["game"]["finalScore"] == 1000
        assert data["game"]["result"] == "won"
        assert "isHighScore" in data

    @pytest.mark.asyncio
    async def test_end_game_not_found(self, client, auth_headers):
        """Test ending non-existent game."""
        response = await client.post(
            "/api/v1/games/nonexistent-id/end",
            json={"finalScore": 1000, "result": "won"},
            headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_end_game_already_ended(self, client, auth_headers):
        """Test ending an already ended game."""
        # Start and end a game
        start_response = await client.post("/api/v1/games", headers=auth_headers)
        game_id = start_response.json()["id"]
        
        await client.post(
            f"/api/v1/games/{game_id}/end",
            json={"finalScore": 1000, "result": "won"},
            headers=auth_headers
        )
        
        # Try to end again
        response = await client.post(
            f"/api/v1/games/{game_id}/end",
            json={"finalScore": 2000, "result": "lost"},
            headers=auth_headers
        )
        assert response.status_code == 400
