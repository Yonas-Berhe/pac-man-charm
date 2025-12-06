"""
Game routes.
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends

from app.models import (
    GameSession, GameHistoryResponse, GameResultResponse,
    EndGameRequest, GameStatus
)
from app.database import db
from app.auth import get_current_user


router = APIRouter(prefix="/games", tags=["Games"])


@router.post("", response_model=GameSession, status_code=status.HTTP_201_CREATED)
async def start_game(current_user: dict = Depends(get_current_user)):
    """Start a new game session."""
    game = db.create_game(current_user["id"])
    return {
        "id": game["id"],
        "userId": game["user_id"],
        "status": game["status"],
        "startedAt": game["started_at"],
        "endedAt": game["ended_at"],
        "finalScore": game["final_score"],
        "result": game["result"],
    }


@router.get("", response_model=GameHistoryResponse)
async def get_game_history(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get user's game history."""
    games, total = db.get_user_games(current_user["id"], limit, offset)
    
    formatted_games = []
    for game in games:
        formatted_games.append({
            "id": game["id"],
            "userId": game["user_id"],
            "status": game["status"],
            "startedAt": game["started_at"],
            "endedAt": game["ended_at"],
            "finalScore": game["final_score"],
            "result": game["result"],
        })
    
    return {"games": formatted_games, "total": total}


@router.get("/{game_id}", response_model=GameSession)
async def get_game_session(
    game_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get game session details."""
    game = db.get_game(game_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GAME_NOT_FOUND", "message": "Game not found"}
        )
    
    if game["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "You don't have access to this game"}
        )
    
    return {
        "id": game["id"],
        "userId": game["user_id"],
        "status": game["status"],
        "startedAt": game["started_at"],
        "endedAt": game["ended_at"],
        "finalScore": game["final_score"],
        "result": game["result"],
    }


@router.post("/{game_id}/end", response_model=GameResultResponse)
async def end_game(
    game_id: str,
    request: EndGameRequest,
    current_user: dict = Depends(get_current_user)
):
    """End a game session and submit score."""
    game = db.get_game(game_id)
    
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "GAME_NOT_FOUND", "message": "Game not found"}
        )
    
    if game["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "You don't have access to this game"}
        )
    
    if game["status"] != GameStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_STATE", "message": "Game is not active"}
        )
    
    previous_high_score = current_user["high_score"]
    
    updated_game = db.end_game(
        game_id,
        final_score=request.final_score,
        result=request.result,
        dots_collected=request.dots_collected,
        power_dots_collected=request.power_dots_collected,
        ghosts_eaten=request.ghosts_eaten,
        lives_remaining=request.lives_remaining,
        duration=request.duration,
    )
    
    # Check if new high score
    updated_user = db.get_user_by_id(current_user["id"])
    is_high_score = updated_user["high_score"] > previous_high_score
    
    # Get new rank if high score
    new_rank = None
    if is_high_score:
        rank_info = db.get_user_rank(current_user["id"])
        new_rank = rank_info.get("rank")
    
    return {
        "game": {
            "id": updated_game["id"],
            "userId": updated_game["user_id"],
            "status": updated_game["status"],
            "startedAt": updated_game["started_at"],
            "endedAt": updated_game["ended_at"],
            "finalScore": updated_game["final_score"],
            "result": updated_game["result"],
        },
        "isHighScore": is_high_score,
        "previousHighScore": previous_high_score if is_high_score else None,
        "newRank": new_rank,
    }
