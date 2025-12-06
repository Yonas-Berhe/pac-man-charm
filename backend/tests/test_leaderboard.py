"""
Tests for leaderboard endpoints.
"""

import pytest


class TestGetLeaderboard:
    """Tests for GET /leaderboard."""

    @pytest.mark.asyncio
    async def test_get_leaderboard_empty(self, client):
        """Test getting empty leaderboard."""
        response = await client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert data["entries"] == []
        assert data["total"] == 0
        assert "period" in data

    @pytest.mark.asyncio
    async def test_get_leaderboard_with_games(self, client, auth_headers):
        """Test getting leaderboard with entries."""
        # Play and complete a game
        start_response = await client.post("/api/v1/games", headers=auth_headers)
        game_id = start_response.json()["id"]
        
        await client.post(
            f"/api/v1/games/{game_id}/end",
            json={"finalScore": 5000, "result": "won"},
            headers=auth_headers
        )
        
        response = await client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) == 1
        assert data["entries"][0]["score"] == 5000

    @pytest.mark.asyncio
    async def test_get_leaderboard_periods(self, client):
        """Test getting leaderboard with different periods."""
        for period in ["all_time", "monthly", "weekly", "daily"]:
            response = await client.get(f"/api/v1/leaderboard?period={period}")
            assert response.status_code == 200


class TestGetMyRank:
    """Tests for GET /leaderboard/me."""

    @pytest.mark.asyncio
    async def test_get_my_rank_no_games(self, client, auth_headers):
        """Test getting rank when user has no games."""
        response = await client.get("/api/v1/leaderboard/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["rank"] is None
        assert data["score"] == 0

    @pytest.mark.asyncio
    async def test_get_my_rank_with_game(self, client, auth_headers):
        """Test getting rank after playing a game."""
        # Play and complete a game
        start_response = await client.post("/api/v1/games", headers=auth_headers)
        game_id = start_response.json()["id"]
        
        await client.post(
            f"/api/v1/games/{game_id}/end",
            json={"finalScore": 3000, "result": "won"},
            headers=auth_headers
        )
        
        response = await client.get("/api/v1/leaderboard/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["rank"] == 1
        assert data["score"] == 3000

    @pytest.mark.asyncio
    async def test_get_my_rank_no_auth(self, client):
        """Test getting rank without authentication."""
        response = await client.get("/api/v1/leaderboard/me")
        assert response.status_code == 401
