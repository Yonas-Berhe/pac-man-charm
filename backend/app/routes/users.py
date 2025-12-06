"""
User routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends

from app.models import User, PublicUser, UpdateUserRequest, UserStats
from app.database import db
from app.auth import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=User)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.patch("/me", response_model=User)
async def update_current_user_profile(
    request: UpdateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile."""
    update_data = {}
    if request.username is not None:
        # Check if username is taken
        for user in db.users.values():
            if user["username"] == request.username and user["id"] != current_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"code": "USERNAME_TAKEN", "message": "Username is already taken"}
                )
        update_data["username"] = request.username
    
    if request.avatar_url is not None:
        update_data["avatar_url"] = request.avatar_url
    
    updated_user = db.update_user(current_user["id"], **update_data)
    return updated_user


@router.get("/{user_id}", response_model=PublicUser)
async def get_user_by_id(user_id: str):
    """Get user by ID (public profile)."""
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    return user


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: str):
    """Get user game statistics."""
    stats = db.get_user_stats(user_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    return {
        "userId": stats["user_id"],
        "gamesPlayed": stats["games_played"],
        "gamesWon": stats["games_won"],
        "gamesLost": stats["games_lost"],
        "winRate": stats["win_rate"],
        "highScore": stats["high_score"],
        "averageScore": stats["average_score"],
        "totalDotsCollected": stats["total_dots_collected"],
        "totalGhostsEaten": stats["total_ghosts_eaten"],
        "totalPlayTime": stats["total_play_time"],
    }
