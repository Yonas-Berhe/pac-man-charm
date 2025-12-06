"""
Leaderboard routes.
Updated for async SQLAlchemy.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LeaderboardResponse, LeaderboardPeriod, UserRank
from app.db.connection import get_db
from app.db.repository import LeaderboardRepository
from app.db.models import User
from app.auth import get_current_user


router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    period: LeaderboardPeriod = Query(LeaderboardPeriod.ALL_TIME),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get leaderboard rankings."""
    leaderboard_repo = LeaderboardRepository(db)
    entries, total = await leaderboard_repo.get_leaderboard(
        period=period.value,
        limit=limit,
        offset=offset
    )
    
    return {
        "entries": entries,
        "total": total,
        "period": period,
    }


@router.get("/me", response_model=UserRank)
async def get_my_rank(
    period: LeaderboardPeriod = Query(LeaderboardPeriod.ALL_TIME),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's rank on the leaderboard."""
    leaderboard_repo = LeaderboardRepository(db)
    rank_info = await leaderboard_repo.get_user_rank(current_user.id, period.value)
    
    return rank_info
