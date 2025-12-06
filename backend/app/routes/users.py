"""
User routes.
Updated for async SQLAlchemy.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User as UserModel, PublicUser, UpdateUserRequest, UserStats
from app.db.connection import get_db
from app.db.repository import UserRepository, GameRepository, get_user_stats
from app.db.models import User
from app.auth import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserModel)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user.to_dict()


@router.patch("/me", response_model=UserModel)
async def update_current_user(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    user_repo = UserRepository(db)
    
    # Check if new username is taken
    if request.username and request.username != current_user.username:
        if await user_repo.username_exists(request.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "CONFLICT", "message": "Username already exists"}
            )
    
    updated_user = await user_repo.update(
        current_user,
        username=request.username,
        avatar_url=request.avatar_url
    )
    
    return updated_user.to_dict()


@router.get("/{user_id}", response_model=PublicUser)
async def get_user_by_id(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get public user profile."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "User not found"}
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "high_score": user.high_score,
        "games_played": user.games_played,
    }


@router.get("/{user_id}/stats", response_model=UserStats)
async def get_user_statistics(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user game statistics."""
    user_repo = UserRepository(db)
    game_repo = GameRepository(db)
    
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "User not found"}
        )
    
    games, _ = await game_repo.get_user_games(user_id, limit=1000)
    stats = get_user_stats(user, games)
    
    return stats
