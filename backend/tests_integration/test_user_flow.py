"""
Integration test: Full user flow from registration to gameplay.
Tests the complete lifecycle with real SQLite database.
"""

import pytest


@pytest.mark.asyncio
class TestUserGameFlow:
    """
    End-to-end test of user registration, login, gameplay, and leaderboard.
    Uses a persistent SQLite database to verify data integrity.
    """

    @pytest.mark.asyncio
    async def test_complete_user_journey(self, client):
        """Test complete user flow: register -> play games -> check leaderboard."""
        
        # 1. Register a new user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "integration_player",
                "email": "integration@test.com",
                "password": "securepass123"
            }
        )
        assert register_response.status_code == 201
        register_data = register_response.json()
        user_id = register_data["user"]["id"]
        access_token = register_data["accessToken"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Verify initial state (snake_case from to_dict())
        assert register_data["user"]["high_score"] == 0
        assert register_data["user"]["games_played"] == 0
        
        # 2. Check user profile
        me_response = await client.get("/api/v1/users/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "integration_player"
        
        # 3. Start first game
        game1_start = await client.post("/api/v1/games", headers=headers)
        assert game1_start.status_code == 201
        game1_id = game1_start.json()["id"]
        assert game1_start.json()["status"] == "active"
        
        # 4. End first game with a win
        game1_end = await client.post(
            f"/api/v1/games/{game1_id}/end",
            json={
                "finalScore": 5000,
                "result": "won",
                "dotsCollected": 150,
                "ghostsEaten": 8,
                "duration": 180
            },
            headers=headers
        )
        assert game1_end.status_code == 200
        assert game1_end.json()["isHighScore"] == True
        assert game1_end.json()["game"]["finalScore"] == 5000
        
        # 5. Start and complete second game (higher score)
        game2_start = await client.post("/api/v1/games", headers=headers)
        game2_id = game2_start.json()["id"]
        
        game2_end = await client.post(
            f"/api/v1/games/{game2_id}/end",
            json={
                "finalScore": 8000,
                "result": "won",
                "dotsCollected": 200,
                "ghostsEaten": 12,
                "duration": 240
            },
            headers=headers
        )
        assert game2_end.status_code == 200
        assert game2_end.json()["isHighScore"] == True
        assert game2_end.json()["previousHighScore"] == 5000
        
        # 6. Check game history
        history_response = await client.get("/api/v1/games", headers=headers)
        assert history_response.status_code == 200
        games = history_response.json()["games"]
        assert len(games) == 2
        assert history_response.json()["total"] == 2
        
        # 7. Check user stats
        stats_response = await client.get(f"/api/v1/users/{user_id}/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["gamesPlayed"] == 2
        assert stats["gamesWon"] == 2
        assert stats["highScore"] == 8000
        assert stats["totalDotsCollected"] == 350
        assert stats["totalGhostsEaten"] == 20
        
        # 8. Check leaderboard
        leaderboard_response = await client.get("/api/v1/leaderboard")
        assert leaderboard_response.status_code == 200
        entries = leaderboard_response.json()["entries"]
        assert len(entries) >= 1
        assert entries[0]["score"] == 8000
        
        # 9. Check user's rank
        rank_response = await client.get("/api/v1/leaderboard/me", headers=headers)
        assert rank_response.status_code == 200
        assert rank_response.json()["rank"] == 1
        assert rank_response.json()["score"] == 8000

    @pytest.mark.asyncio
    async def test_multiple_users_leaderboard(self, client):
        """Test leaderboard with multiple users competing."""
        
        users = []
        scores = [3000, 7000, 1000, 9000, 5000]
        
        # Register users and play games
        for i, score in enumerate(scores):
            # Register
            reg = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": f"player_{i}",
                    "email": f"player{i}@test.com",
                    "password": "password123"
                }
            )
            assert reg.status_code == 201
            token = reg.json()["accessToken"]
            headers = {"Authorization": f"Bearer {token}"}
            users.append({"headers": headers, "score": score})
            
            # Start and end game
            game = await client.post("/api/v1/games", headers=headers)
            game_id = game.json()["id"]
            
            await client.post(
                f"/api/v1/games/{game_id}/end",
                json={"finalScore": score, "result": "won"},
                headers=headers
            )
        
        # Check leaderboard - should be sorted by score
        lb = await client.get("/api/v1/leaderboard?limit=10")
        assert lb.status_code == 200
        entries = lb.json()["entries"]
        
        # Verify ranking order (highest first)
        scores_in_order = [e["score"] for e in entries]
        assert scores_in_order == sorted(scores_in_order, reverse=True)

    @pytest.mark.asyncio
    async def test_login_persists_data(self, client):
        """Test that user data persists across login sessions."""
        
        # Register and play
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "persist_user",
                "email": "persist@test.com",
                "password": "password123"
            }
        )
        token1 = reg.json()["accessToken"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        # Play a game
        game = await client.post("/api/v1/games", headers=headers1)
        game_id = game.json()["id"]
        await client.post(
            f"/api/v1/games/{game_id}/end",
            json={"finalScore": 4500, "result": "won"},
            headers=headers1
        )
        
        # Logout
        await client.post("/api/v1/auth/logout", headers=headers1)
        
        # Login again
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": "persist@test.com", "password": "password123"}
        )
        assert login.status_code == 200
        token2 = login.json()["accessToken"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        # Verify data persists (snake_case from to_dict())
        me = await client.get("/api/v1/users/me", headers=headers2)
        assert me.json()["high_score"] == 4500
        assert me.json()["games_played"] == 1
        
        history = await client.get("/api/v1/games", headers=headers2)
        assert history.json()["total"] == 1
