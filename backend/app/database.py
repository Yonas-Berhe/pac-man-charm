"""
Mock database for development.
Will be replaced with a real database later.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4
from passlib.hash import pbkdf2_sha256

from app.models import GameStatus, GameResult


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class MockDatabase:
    """In-memory mock database."""
    
    def __init__(self):
        self.users: dict[str, dict] = {}
        self.games: dict[str, dict] = {}
        self.refresh_tokens: dict[str, str] = {}  # token -> user_id
        
        # Create a demo user
        self._create_demo_user()
    
    def _create_demo_user(self):
        """Create a demo user for testing."""
        demo_id = str(uuid4())
        now = utc_now()
        self.users[demo_id] = {
            "id": demo_id,
            "username": "demo_player",
            "email": "demo@example.com",
            "password_hash": pbkdf2_sha256.hash("demo1234"),
            "avatar_url": None,
            "high_score": 5000,
            "games_played": 10,
            "games_won": 3,
            "games_lost": 7,
            "total_dots_collected": 500,
            "total_ghosts_eaten": 25,
            "total_play_time": 1800,
            "created_at": now,
            "updated_at": now,
        }
    
    # ============================================
    # User Operations
    # ============================================
    def create_user(self, username: str, email: str, password: str) -> dict:
        """Create a new user."""
        # Check if email or username exists
        for user in self.users.values():
            if user["email"] == email:
                raise ValueError("Email already exists")
            if user["username"] == username:
                raise ValueError("Username already exists")
        
        user_id = str(uuid4())
        now = utc_now()
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "password_hash": pbkdf2_sha256.hash(password),
            "avatar_url": None,
            "high_score": 0,
            "games_played": 0,
            "games_won": 0,
            "games_lost": 0,
            "total_dots_collected": 0,
            "total_ghosts_eaten": 0,
            "total_play_time": 0,
            "created_at": now,
            "updated_at": now,
        }
        self.users[user_id] = user
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        for user in self.users.values():
            if user["email"] == email:
                return user
        return None
    
    def verify_password(self, user: dict, password: str) -> bool:
        """Verify user password."""
        return pbkdf2_sha256.verify(password, user["password_hash"])
    
    def update_user(self, user_id: str, **kwargs) -> Optional[dict]:
        """Update user fields."""
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        for key, value in kwargs.items():
            if key in user and value is not None:
                user[key] = value
        user["updated_at"] = utc_now()
        return user
    
    # ============================================
    # Token Operations
    # ============================================
    def store_refresh_token(self, token: str, user_id: str):
        """Store a refresh token."""
        self.refresh_tokens[token] = user_id
    
    def get_user_id_from_refresh_token(self, token: str) -> Optional[str]:
        """Get user ID from refresh token."""
        return self.refresh_tokens.get(token)
    
    def revoke_refresh_token(self, token: str):
        """Revoke a refresh token."""
        self.refresh_tokens.pop(token, None)
    
    def revoke_user_tokens(self, user_id: str):
        """Revoke all refresh tokens for a user."""
        to_remove = [t for t, uid in self.refresh_tokens.items() if uid == user_id]
        for token in to_remove:
            del self.refresh_tokens[token]
    
    # ============================================
    # Game Operations
    # ============================================
    def create_game(self, user_id: str) -> dict:
        """Create a new game session."""
        game_id = str(uuid4())
        now = utc_now()
        game = {
            "id": game_id,
            "user_id": user_id,
            "status": GameStatus.ACTIVE,
            "started_at": now,
            "ended_at": None,
            "final_score": None,
            "result": None,
            "dots_collected": 0,
            "power_dots_collected": 0,
            "ghosts_eaten": 0,
            "lives_remaining": 3,
            "duration": 0,
        }
        self.games[game_id] = game
        return game
    
    def get_game(self, game_id: str) -> Optional[dict]:
        """Get game by ID."""
        return self.games.get(game_id)
    
    def end_game(self, game_id: str, final_score: int, result: GameResult, **stats) -> Optional[dict]:
        """End a game session."""
        game = self.games.get(game_id)
        if not game:
            return None
        
        game["status"] = GameStatus.COMPLETED
        game["ended_at"] = utc_now()
        game["final_score"] = final_score
        game["result"] = result
        
        for key, value in stats.items():
            if key in game and value is not None:
                game[key] = value
        
        # Update user stats
        user = self.users.get(game["user_id"])
        if user:
            user["games_played"] += 1
            if result == GameResult.WON:
                user["games_won"] += 1
            else:
                user["games_lost"] += 1
            
            if final_score > user["high_score"]:
                user["high_score"] = final_score
            
            user["total_dots_collected"] += stats.get("dots_collected") or 0
            user["total_ghosts_eaten"] += stats.get("ghosts_eaten") or 0
            user["total_play_time"] += stats.get("duration") or 0
            user["updated_at"] = utc_now()
        
        return game
    
    def get_user_games(self, user_id: str, limit: int = 10, offset: int = 0) -> tuple[list[dict], int]:
        """Get user's game history."""
        user_games = [g for g in self.games.values() if g["user_id"] == user_id]
        user_games.sort(key=lambda x: x["started_at"], reverse=True)
        total = len(user_games)
        return user_games[offset:offset + limit], total
    
    # ============================================
    # Leaderboard Operations
    # ============================================
    def get_leaderboard(self, period: str = "all_time", limit: int = 10, offset: int = 0) -> tuple[list[dict], int]:
        """Get leaderboard entries."""
        # Filter by period
        now = utc_now()
        if period == "daily":
            cutoff = now - timedelta(days=1)
        elif period == "weekly":
            cutoff = now - timedelta(weeks=1)
        elif period == "monthly":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = None
        
        # Get all completed games
        games = [g for g in self.games.values() 
                 if g["status"] == GameStatus.COMPLETED and g["final_score"] is not None]
        
        if cutoff:
            games = [g for g in games if g["ended_at"] and g["ended_at"] > cutoff]
        
        # Get best score per user
        user_best: dict[str, dict] = {}
        for game in games:
            user_id = game["user_id"]
            if user_id not in user_best or game["final_score"] > user_best[user_id]["final_score"]:
                user_best[user_id] = game
        
        # Sort by score
        sorted_entries = sorted(user_best.values(), key=lambda x: x["final_score"], reverse=True)
        total = len(sorted_entries)
        
        # Build leaderboard entries
        entries = []
        for i, game in enumerate(sorted_entries[offset:offset + limit], start=offset + 1):
            user = self.users.get(game["user_id"])
            if user:
                entries.append({
                    "rank": i,
                    "user": user,
                    "score": game["final_score"],
                    "achieved_at": game["ended_at"],
                })
        
        return entries, total
    
    def get_user_rank(self, user_id: str, period: str = "all_time") -> dict:
        """Get user's rank on leaderboard."""
        entries, total = self.get_leaderboard(period, limit=1000, offset=0)
        
        user = self.users.get(user_id)
        if not user:
            return {"rank": None, "score": 0, "percentile": 0, "period": period}
        
        for entry in entries:
            if entry["user"]["id"] == user_id:
                percentile = ((total - entry["rank"] + 1) / total) * 100 if total > 0 else 0
                return {
                    "rank": entry["rank"],
                    "score": entry["score"],
                    "percentile": round(percentile, 2),
                    "period": period,
                }
        
        return {
            "rank": None,
            "score": user["high_score"],
            "percentile": 0,
            "period": period,
        }
    
    def get_user_stats(self, user_id: str) -> Optional[dict]:
        """Get user statistics."""
        user = self.users.get(user_id)
        if not user:
            return None
        
        games_played = user["games_played"]
        win_rate = (user["games_won"] / games_played * 100) if games_played > 0 else 0
        
        # Calculate average score
        user_games = [g for g in self.games.values() 
                      if g["user_id"] == user_id and g["final_score"] is not None]
        total_score = sum(g["final_score"] for g in user_games)
        avg_score = total_score / len(user_games) if user_games else 0
        
        return {
            "user_id": user_id,
            "games_played": games_played,
            "games_won": user["games_won"],
            "games_lost": user["games_lost"],
            "win_rate": round(win_rate, 2),
            "high_score": user["high_score"],
            "average_score": round(avg_score, 2),
            "total_dots_collected": user["total_dots_collected"],
            "total_ghosts_eaten": user["total_ghosts_eaten"],
            "total_play_time": user["total_play_time"],
        }


# Global database instance
db = MockDatabase()
