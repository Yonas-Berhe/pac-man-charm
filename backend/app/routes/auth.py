"""
Authentication routes.
Updated for async SQLAlchemy.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    RegisterRequest, LoginRequest, RefreshTokenRequest,
    AuthResponse, SuccessMessage
)
from app.db.connection import get_db
from app.db.repository import UserRepository, TokenRepository
from app.db.models import User
from app.auth import (
    create_access_token, create_refresh_token, verify_token, get_current_user
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user."""
    user_repo = UserRepository(db)
    token_repo = TokenRepository(db)
    
    # Check if email or username exists
    if await user_repo.email_exists(request.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CONFLICT", "message": "Email already exists"}
        )
    
    if await user_repo.username_exists(request.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CONFLICT", "message": "Username already exists"}
        )
    
    user = await user_repo.create(
        username=request.username,
        email=request.email,
        password=request.password
    )
    
    access_token, expires_in = create_access_token(user.id)
    refresh_token, refresh_expires = create_refresh_token(user.id)
    
    # Store refresh token
    await token_repo.store(refresh_token, user.id, refresh_expires)
    
    return {
        "user": user.to_dict(),
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresIn": expires_in,
    }


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login user."""
    user_repo = UserRepository(db)
    token_repo = TokenRepository(db)
    
    user = await user_repo.get_by_email(request.email)
    
    if not user or not user_repo.verify_password(user, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
        )
    
    access_token, expires_in = create_access_token(user.id)
    refresh_token, refresh_expires = create_refresh_token(user.id)
    
    # Store refresh token
    await token_repo.store(refresh_token, user.id, refresh_expires)
    
    return {
        "user": user.to_dict(),
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresIn": expires_in,
    }


@router.post("/logout", response_model=SuccessMessage)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user (revoke all tokens)."""
    token_repo = TokenRepository(db)
    await token_repo.revoke_user_tokens(current_user.id)
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token."""
    user_id = verify_token(request.refresh_token, "refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired refresh token"}
        )
    
    token_repo = TokenRepository(db)
    user_repo = UserRepository(db)
    
    # Verify token is in our store
    stored_user_id = await token_repo.get_user_id(request.refresh_token)
    if stored_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Token has been revoked"}
        )
    
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    # Revoke old token and create new ones
    await token_repo.revoke(request.refresh_token)
    access_token, expires_in = create_access_token(user.id)
    new_refresh_token, refresh_expires = create_refresh_token(user.id)
    
    # Store new refresh token
    await token_repo.store(new_refresh_token, user.id, refresh_expires)
    
    return {
        "user": user.to_dict(),
        "accessToken": access_token,
        "refreshToken": new_refresh_token,
        "expiresIn": expires_in,
    }
