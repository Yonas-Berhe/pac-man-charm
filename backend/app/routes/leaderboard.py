"""
Leaderboard routes.
"""

from fastapi import APIRouter, Query, Depends

from app.models import LeaderboardResponse, LeaderboardPeriod, UserRank
from app.database import db
from app.auth import get_current_user


router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    period: LeaderboardPeriod = Query(LeaderboardPeriod.ALL_TIME)
):
    """Get global leaderboard."""
    entries, total = db.get_leaderboard(period.value, limit, offset)
    
    formatted_entries = []
    for entry in entries:
        formatted_entries.append({
            "rank": entry["rank"],
            "user": {
                "id": entry["user"]["id"],
                "username": entry["user"]["username"],
                "avatar_url": entry["user"].get("avatar_url"),
                "high_score": entry["user"]["high_score"],
                "games_played": entry["user"]["games_played"],
            },
            "score": entry["score"],
            "achievedAt": entry["achieved_at"],
        })
    
    return {
        "entries": formatted_entries,
        "total": total,
        "period": period,
    }


@router.get("/me", response_model=UserRank)
async def get_my_rank(
    period: LeaderboardPeriod = Query(LeaderboardPeriod.ALL_TIME),
    current_user: dict = Depends(get_current_user)
):
    """Get current user's rank."""
    rank_info = db.get_user_rank(current_user["id"], period.value)
    return rank_info
