"""
Authentication routes.
"""

from fastapi import APIRouter, HTTPException, status, Depends

from app.models import (
    RegisterRequest, LoginRequest, RefreshTokenRequest,
    AuthResponse, User, SuccessMessage, Error
)
from app.database import db
from app.auth import (
    create_access_token, create_refresh_token, verify_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register a new user."""
    try:
        user = db.create_user(
            username=request.username,
            email=request.email,
            password=request.password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "CONFLICT", "message": str(e)}
        )
    
    access_token, expires_in = create_access_token(user["id"])
    refresh_token = create_refresh_token(user["id"])
    
    return {
        "user": user,
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresIn": expires_in,
    }


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user."""
    user = db.get_user_by_email(request.email)
    
    if not user or not db.verify_password(user, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
        )
    
    access_token, expires_in = create_access_token(user["id"])
    refresh_token = create_refresh_token(user["id"])
    
    return {
        "user": user,
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "expiresIn": expires_in,
    }


@router.post("/logout", response_model=SuccessMessage)
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout user (revoke all tokens)."""
    db.revoke_user_tokens(current_user["id"])
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token."""
    user_id = verify_token(request.refresh_token, "refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired refresh token"}
        )
    
    # Verify token is in our store
    stored_user_id = db.get_user_id_from_refresh_token(request.refresh_token)
    if stored_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Token has been revoked"}
        )
    
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"}
        )
    
    # Revoke old token and create new ones
    db.revoke_refresh_token(request.refresh_token)
    access_token, expires_in = create_access_token(user["id"])
    new_refresh_token = create_refresh_token(user["id"])
    
    return {
        "user": user,
        "accessToken": access_token,
        "refreshToken": new_refresh_token,
        "expiresIn": expires_in,
    }
