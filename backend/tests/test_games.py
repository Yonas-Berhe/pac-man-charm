"""
Tests for game endpoints.
"""

import pytest


class TestStartGame:
    """Tests for POST /api/v1/games."""

    def test_start_game_success(self, client, auth_headers):
        """Test starting a new game."""
        response = client.post("/api/v1/games", headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "active"
        assert data["finalScore"] is None

    def test_start_game_no_auth(self, client):
        """Test starting game without authentication."""
        response = client.post("/api/v1/games")
        assert response.status_code == 401


class TestGetGameHistory:
    """Tests for GET /api/v1/games."""

    def test_get_history_empty(self, client, auth_headers):
        """Test getting empty game history."""
        response = client.get("/api/v1/games", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["games"] == []
        assert data["total"] == 0

    def test_get_history_with_games(self, client, auth_headers):
        """Test getting game history with games."""
        # Create a game
        client.post("/api/v1/games", headers=auth_headers)

        response = client.get("/api/v1/games", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["games"]) == 1
        assert data["total"] == 1

    def test_get_history_pagination(self, client, auth_headers):
        """Test game history pagination."""
        # Create multiple games
        for _ in range(5):
            client.post("/api/v1/games", headers=auth_headers)

        # Get with limit
        response = client.get("/api/v1/games?limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["games"]) == 2
        assert data["total"] == 5


class TestGetGameSession:
    """Tests for GET /api/v1/games/{game_id}."""

    def test_get_game_success(self, client, auth_headers):
        """Test getting game session details."""
        # Create a game
        create_response = client.post("/api/v1/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        response = client.get(f"/api/v1/games/{game_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == game_id

    def test_get_game_not_found(self, client, auth_headers):
        """Test getting non-existent game."""
        response = client.get("/api/v1/games/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404

    def test_get_game_forbidden(self, client, auth_headers, demo_auth_headers):
        """Test accessing another user's game."""
        # Create game with auth_headers
        create_response = client.post("/api/v1/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        # Try to access with demo_auth_headers
        response = client.get(f"/api/v1/games/{game_id}", headers=demo_auth_headers)
        assert response.status_code == 403


class TestEndGame:
    """Tests for POST /api/v1/games/{game_id}/end."""

    def test_end_game_success(self, client, auth_headers):
        """Test ending a game successfully."""
        # Create a game
        create_response = client.post("/api/v1/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        # End the game
        response = client.post(
            f"/api/v1/games/{game_id}/end",
            headers=auth_headers,
            json={
                "finalScore": 1500,
                "result": "won",
                "dotsCollected": 150,
                "powerDotsCollected": 4,
                "ghostsEaten": 8,
                "livesRemaining": 2,
                "duration": 180
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["game"]["finalScore"] == 1500
        assert data["game"]["result"] == "won"
        assert data["game"]["status"] == "completed"
        assert data["isHighScore"] == True  # First game, so it's a high score

    def test_end_game_lost(self, client, auth_headers):
        """Test ending a game with lost result."""
        create_response = client.post("/api/v1/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        response = client.post(
            f"/api/v1/games/{game_id}/end",
            headers=auth_headers,
            json={
                "finalScore": 500,
                "result": "lost",
                "livesRemaining": 0
            }
        )
        assert response.status_code == 200
        assert response.json()["game"]["result"] == "lost"

    def test_end_game_not_found(self, client, auth_headers):
        """Test ending non-existent game."""
        response = client.post(
            "/api/v1/games/nonexistent-id/end",
            headers=auth_headers,
            json={"finalScore": 1000, "result": "won"}
        )
        assert response.status_code == 404

    def test_end_game_already_ended(self, client, auth_headers):
        """Test ending an already ended game."""
        # Create and end a game
        create_response = client.post("/api/v1/games", headers=auth_headers)
        game_id = create_response.json()["id"]

        client.post(
            f"/api/v1/games/{game_id}/end",
            headers=auth_headers,
            json={"finalScore": 1000, "result": "won"}
        )

        # Try to end again
        response = client.post(
            f"/api/v1/games/{game_id}/end",
            headers=auth_headers,
            json={"finalScore": 2000, "result": "won"}
        )
        assert response.status_code == 400

    def test_end_game_updates_high_score(self, client, auth_headers):
        """Test that ending game updates user's high score."""
        # First game
        game1 = client.post("/api/v1/games", headers=auth_headers).json()
        client.post(
            f"/api/v1/games/{game1['id']}/end",
            headers=auth_headers,
            json={"finalScore": 1000, "result": "won"}
        )

        # Check high score
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        assert me["high_score"] == 1000

        # Second game with higher score
        game2 = client.post("/api/v1/games", headers=auth_headers).json()
        response = client.post(
            f"/api/v1/games/{game2['id']}/end",
            headers=auth_headers,
            json={"finalScore": 2000, "result": "won"}
        )
        assert response.json()["isHighScore"] == True

        # Check updated high score
        me = client.get("/api/v1/users/me", headers=auth_headers).json()
        assert me["high_score"] == 2000


class TestHealthCheck:
    """Tests for GET /api/v1/health."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
