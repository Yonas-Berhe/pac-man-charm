"""
Database repository with CRUD operations.
Replaces the mock database with SQLAlchemy queries.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.hash import pbkdf2_sha256

from app.db.models import User, Game, RefreshToken, utc_now
from app.models import GameStatus, GameResult


class UserRepository:
    """User CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, username: str, email: str, password: str) -> User:
        """Create a new user."""
        user = User(
            username=username,
            email=email,
            password_hash=pbkdf2_sha256.hash(password),
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check if email exists."""
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.email == email)
        )
        return result.scalar() > 0

    async def username_exists(self, username: str) -> bool:
        """Check if username exists."""
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.username == username)
        )
        return result.scalar() > 0

    def verify_password(self, user: User, password: str) -> bool:
        """Verify user password."""
        return pbkdf2_sha256.verify(password, user.password_hash)

    async def update(self, user: User, **kwargs) -> User:
        """Update user fields."""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        user.updated_at = utc_now()
        await self.session.commit()
        await self.session.refresh(user)
        return user


class GameRepository:
    """Game CRUD operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str) -> Game:
        """Create a new game session."""
        game = Game(user_id=user_id)
        self.session.add(game)
        await self.session.commit()
        await self.session.refresh(game)
        return game

    async def get_by_id(self, game_id: str) -> Optional[Game]:
        """Get game by ID."""
        result = await self.session.execute(
            select(Game).where(Game.id == game_id)
        )
        return result.scalar_one_or_none()

    async def end_game(
        self,
        game: Game,
        user: User,
        final_score: int,
        result: GameResult,
        **stats
    ) -> Game:
        """End a game session and update user stats."""
        game.status = GameStatus.COMPLETED.value
        game.ended_at = utc_now()
        game.final_score = final_score
        game.result = result.value

        for key, value in stats.items():
            if hasattr(game, key) and value is not None:
                setattr(game, key, value)

        # Update user stats
        user.games_played += 1
        if result == GameResult.WON:
            user.games_won += 1
        else:
            user.games_lost += 1

        if final_score > user.high_score:
            user.high_score = final_score

        user.total_dots_collected += stats.get("dots_collected") or 0
        user.total_ghosts_eaten += stats.get("ghosts_eaten") or 0
        user.total_play_time += stats.get("duration") or 0
        user.updated_at = utc_now()

        await self.session.commit()
        await self.session.refresh(game)
        return game

    async def get_user_games(
        self, user_id: str, limit: int = 10, offset: int = 0
    ) -> tuple[list[Game], int]:
        """Get user's game history."""
        # Count total
        count_result = await self.session.execute(
            select(func.count()).select_from(Game).where(Game.user_id == user_id)
        )
        total = count_result.scalar() or 0

        # Get games
        result = await self.session.execute(
            select(Game)
            .where(Game.user_id == user_id)
            .order_by(Game.started_at.desc())
            .limit(limit)
            .offset(offset)
        )
        games = list(result.scalars().all())
        return games, total


class LeaderboardRepository:
    """Leaderboard operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_leaderboard(
        self, period: str = "all_time", limit: int = 10, offset: int = 0
    ) -> tuple[list[dict], int]:
        """Get leaderboard entries."""
        now = utc_now()
        
        if period == "daily":
            cutoff = now - timedelta(days=1)
        elif period == "weekly":
            cutoff = now - timedelta(weeks=1)
        elif period == "monthly":
            cutoff = now - timedelta(days=30)
        else:
            cutoff = None

        # Build query for best score per user
        query = (
            select(
                Game.user_id,
                func.max(Game.final_score).label("best_score"),
                func.max(Game.ended_at).label("achieved_at"),
            )
            .where(Game.status == GameStatus.COMPLETED.value)
            .where(Game.final_score.isnot(None))
        )

        if cutoff:
            query = query.where(Game.ended_at > cutoff)

        query = query.group_by(Game.user_id).order_by(func.max(Game.final_score).desc())

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated results
        result = await self.session.execute(query.limit(limit).offset(offset))
        rows = result.all()

        # Build entries with user data
        entries = []
        for i, row in enumerate(rows, start=offset + 1):
            user_result = await self.session.execute(
                select(User).where(User.id == row.user_id)
            )
            user = user_result.scalar_one_or_none()
            if user:
                entries.append({
                    "rank": i,
                    "user": user.to_dict(),
                    "score": row.best_score,
                    "achieved_at": row.achieved_at,
                })

        return entries, total

    async def get_user_rank(self, user_id: str, period: str = "all_time") -> dict:
        """Get user's rank on leaderboard."""
        entries, total = await self.get_leaderboard(period, limit=1000, offset=0)

        user_result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

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
            "score": user.high_score,
            "percentile": 0,
            "period": period,
        }


class TokenRepository:
    """Refresh token operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def store(self, token: str, user_id: str, expires_at: datetime) -> RefreshToken:
        """Store a refresh token."""
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.session.add(refresh_token)
        await self.session.commit()
        return refresh_token

    async def get_user_id(self, token: str) -> Optional[str]:
        """Get user ID from refresh token."""
        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.token == token)
            .where(RefreshToken.expires_at > utc_now())
        )
        refresh_token = result.scalar_one_or_none()
        return refresh_token.user_id if refresh_token else None

    async def revoke(self, token: str) -> None:
        """Revoke a refresh token."""
        await self.session.execute(
            delete(RefreshToken).where(RefreshToken.token == token)
        )
        await self.session.commit()

    async def revoke_user_tokens(self, user_id: str) -> None:
        """Revoke all refresh tokens for a user."""
        await self.session.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        await self.session.commit()


def get_user_stats(user: User, games: list[Game]) -> dict:
    """Calculate user statistics."""
    games_played = user.games_played
    win_rate = (user.games_won / games_played * 100) if games_played > 0 else 0

    completed_games = [g for g in games if g.final_score is not None]
    total_score = sum(g.final_score for g in completed_games)
    avg_score = total_score / len(completed_games) if completed_games else 0

    return {
        "user_id": user.id,
        "games_played": games_played,
        "games_won": user.games_won,
        "games_lost": user.games_lost,
        "win_rate": round(win_rate, 2),
        "high_score": user.high_score,
        "average_score": round(avg_score, 2),
        "total_dots_collected": user.total_dots_collected,
        "total_ghosts_eaten": user.total_ghosts_eaten,
        "total_play_time": user.total_play_time,
    }
