"""
Game routes.
Updated for async SQLAlchemy.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    GameSession, EndGameRequest, GameResultResponse, GameHistoryResponse
)
from app.db.connection import get_db
from app.db.repository import UserRepository, GameRepository
from app.db.models import User, Game
from app.models import GameStatus, GameResult
from app.auth import get_current_user


router = APIRouter(prefix="/games", tags=["Games"])


@router.post("", response_model=GameSession, status_code=status.HTTP_201_CREATED)
async def start_game(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new game session."""
    game_repo = GameRepository(db)
    game = await game_repo.create(current_user.id)
    
    return game.to_dict()


@router.get("", response_model=GameHistoryResponse)
async def get_game_history(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's game history."""
    game_repo = GameRepository(db)
    games, total = await game_repo.get_user_games(current_user.id, limit, offset)
    
    return {
        "games": [g.to_dict() for g in games],
        "total": total,
    }


@router.get("/{game_id}", response_model=GameSession)
async def get_game_session(
    game_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific game session."""
    game_repo = GameRepository(db)
    game = await game_repo.get_by_id(game_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Game not found"}
        )
    
    if game.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Not your game"}
        )
    
    return game.to_dict()


@router.post("/{game_id}/end", response_model=GameResultResponse)
async def end_game(
    game_id: str,
    request: EndGameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """End a game session and submit results."""
    game_repo = GameRepository(db)
    game = await game_repo.get_by_id(game_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": "Game not found"}
        )
    
    if game.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "Not your game"}
        )
    
    if game.status != GameStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": "Game already ended"}
        )
    
    previous_high_score = current_user.high_score
    
    # End the game
    game = await game_repo.end_game(
        game=game,
        user=current_user,
        final_score=request.final_score,
        result=request.result,
        dots_collected=request.dots_collected,
        power_dots_collected=request.power_dots_collected,
        ghosts_eaten=request.ghosts_eaten,
        lives_remaining=request.lives_remaining,
        duration=request.duration,
    )
    
    is_high_score = request.final_score > previous_high_score
    
    return {
        "game": game.to_dict(),
        "isHighScore": is_high_score,
        "previousHighScore": previous_high_score if is_high_score else None,
        "newRank": None,  # TODO: Calculate rank
    }
