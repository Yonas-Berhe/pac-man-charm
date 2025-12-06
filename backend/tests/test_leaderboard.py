"""
Tests for leaderboard endpoints.
"""

import pytest


class TestGetLeaderboard:
    """Tests for GET /api/v1/leaderboard."""

    def test_get_leaderboard_empty(self, client):
        """Test getting empty leaderboard."""
        response = client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert data["entries"] == []
        assert data["total"] == 0

    def test_get_leaderboard_with_games(self, client, auth_headers):
        """Test getting leaderboard with completed games."""
        # Start and end a game
        start_response = client.post("/api/v1/games", headers=auth_headers)
        game_id = start_response.json()["id"]

        client.post(
            f"/api/v1/games/{game_id}/end",
            headers=auth_headers,
            json={
                "finalScore": 1000,
                "result": "won",
                "dotsCollected": 100,
                "ghostsEaten": 5,
                "duration": 120
            }
        )

        # Get leaderboard
        response = client.get("/api/v1/leaderboard")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["entries"]) >= 1

    def test_get_leaderboard_with_limit(self, client):
        """Test getting leaderboard with limit."""
        response = client.get("/api/v1/leaderboard?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["entries"]) <= 5

    def test_get_leaderboard_by_period(self, client):
        """Test getting leaderboard by period."""
        for period in ["all_time", "monthly", "weekly", "daily"]:
            response = client.get(f"/api/v1/leaderboard?period={period}")
            assert response.status_code == 200
            assert response.json()["period"] == period


class TestGetMyRank:
    """Tests for GET /api/v1/leaderboard/me."""

    def test_get_my_rank_no_games(self, client, auth_headers):
        """Test getting rank with no completed games."""
        response = client.get("/api/v1/leaderboard/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["rank"] is None
        assert data["score"] == 0

    def test_get_my_rank_with_game(self, client, auth_headers):
        """Test getting rank after completing a game."""
        # Start and end a game
        start_response = client.post("/api/v1/games", headers=auth_headers)
        game_id = start_response.json()["id"]

        client.post(
            f"/api/v1/games/{game_id}/end",
            headers=auth_headers,
            json={
                "finalScore": 5000,
                "result": "won"
            }
        )

        response = client.get("/api/v1/leaderboard/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 5000

    def test_get_my_rank_no_auth(self, client):
        """Test getting rank without authentication."""
        response = client.get("/api/v1/leaderboard/me")
        assert response.status_code == 401
