"""
Pydantic models/schemas for the Pac-Man API.
Based on OpenAPI specification.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from enum import Enum


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


# ============================================
# Enums
# ============================================
class GameStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class GameResult(str, Enum):
    WON = "won"
    LOST = "lost"


class LeaderboardPeriod(str, Enum):
    ALL_TIME = "all_time"
    MONTHLY = "monthly"
    WEEKLY = "weekly"
    DAILY = "daily"


# ============================================
# Request Models
# ============================================
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=20)
    avatar_url: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    refresh_token: str = Field(..., alias="refreshToken")


class EndGameRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    final_score: int = Field(..., ge=0, alias="finalScore")
    result: GameResult
    dots_collected: Optional[int] = Field(None, ge=0, alias="dotsCollected")
    power_dots_collected: Optional[int] = Field(None, ge=0, alias="powerDotsCollected")
    ghosts_eaten: Optional[int] = Field(None, ge=0, alias="ghostsEaten")
    lives_remaining: Optional[int] = Field(None, ge=0, le=3, alias="livesRemaining")
    duration: Optional[int] = Field(None, ge=0)


# ============================================
# Response Models
# ============================================
class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    username: str
    email: EmailStr
    avatar_url: Optional[str] = None
    high_score: int = 0
    games_played: int = 0
    created_at: datetime
    updated_at: datetime


class PublicUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    username: str
    avatar_url: Optional[str] = None
    high_score: int = 0
    games_played: int = 0


class AuthResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    user: User
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    expires_in: int = Field(..., alias="expiresIn")


class UserStats(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    user_id: str = Field(..., alias="userId")
    games_played: int = Field(..., alias="gamesPlayed")
    games_won: int = Field(..., alias="gamesWon")
    games_lost: int = Field(..., alias="gamesLost")
    win_rate: float = Field(..., alias="winRate")
    high_score: int = Field(..., alias="highScore")
    average_score: float = Field(..., alias="averageScore")
    total_dots_collected: int = Field(..., alias="totalDotsCollected")
    total_ghosts_eaten: int = Field(..., alias="totalGhostsEaten")
    total_play_time: int = Field(..., alias="totalPlayTime")


class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    rank: int
    user: PublicUser
    score: int
    achieved_at: datetime = Field(..., alias="achievedAt")


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]
    total: int
    period: LeaderboardPeriod


class UserRank(BaseModel):
    rank: Optional[int] = None
    score: int
    percentile: float
    period: str


class GameSession(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str
    user_id: str = Field(..., alias="userId")
    status: GameStatus
    started_at: datetime = Field(..., alias="startedAt")
    ended_at: Optional[datetime] = Field(None, alias="endedAt")
    final_score: Optional[int] = Field(None, alias="finalScore")
    result: Optional[GameResult] = None


class GameResultResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    game: GameSession
    is_high_score: bool = Field(..., alias="isHighScore")
    previous_high_score: Optional[int] = Field(None, alias="previousHighScore")
    new_rank: Optional[int] = Field(None, alias="newRank")


class GameHistoryResponse(BaseModel):
    games: list[GameSession]
    total: int


class SuccessMessage(BaseModel):
    message: str


class Error(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
