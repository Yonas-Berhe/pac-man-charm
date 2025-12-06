"""
SQLAlchemy ORM models for the Pac-Man database.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import Base
from app.models import GameStatus, GameResult


def utc_now() -> datetime:
    """Get current UTC time."""
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class User(Base):
    """User model."""
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Stats
    high_score: Mapped[int] = mapped_column(Integer, default=0)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    games_won: Mapped[int] = mapped_column(Integer, default=0)
    games_lost: Mapped[int] = mapped_column(Integer, default=0)
    total_dots_collected: Mapped[int] = mapped_column(Integer, default=0)
    total_ghosts_eaten: Mapped[int] = mapped_column(Integer, default=0)
    total_play_time: Mapped[int] = mapped_column(Integer, default=0)  # seconds
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    
    # Relationships
    games: Mapped[List["Game"]] = relationship("Game", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "high_score": self.high_score,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "games_lost": self.games_lost,
            "total_dots_collected": self.total_dots_collected,
            "total_ghosts_eaten": self.total_ghosts_eaten,
            "total_play_time": self.total_play_time,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Game(Base):
    """Game session model."""
    __tablename__ = "games"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    status: Mapped[str] = mapped_column(String(20), default=GameStatus.ACTIVE.value)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    final_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    result: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Game stats
    dots_collected: Mapped[int] = mapped_column(Integer, default=0)
    power_dots_collected: Mapped[int] = mapped_column(Integer, default=0)
    ghosts_eaten: Mapped[int] = mapped_column(Integer, default=0)
    lives_remaining: Mapped[int] = mapped_column(Integer, default=3)
    duration: Mapped[int] = mapped_column(Integer, default=0)  # seconds
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="games")

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": GameStatus(self.status) if self.status else None,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "final_score": self.final_score,
            "result": GameResult(self.result) if self.result else None,
            "dots_collected": self.dots_collected,
            "power_dots_collected": self.power_dots_collected,
            "ghosts_eaten": self.ghosts_eaten,
            "lives_remaining": self.lives_remaining,
            "duration": self.duration,
        }


class RefreshToken(Base):
    """Refresh token model."""
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    token: Mapped[str] = mapped_column(String(500), unique=True, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
