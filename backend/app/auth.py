"""
JWT Authentication utilities.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import db


# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


def create_access_token(user_id: str) -> tuple[str, int]:
    """Create a new access token."""
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = utc_now() + expires_delta
    
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "access",
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, int(expires_delta.total_seconds())


def create_refresh_token(user_id: str) -> str:
    """Create a new refresh token."""
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    expire = utc_now() + expires_delta
    
    payload = {
        "sub": user_id,
        "exp": expire,
        "type": "refresh",
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    db.store_refresh_token(token, user_id)
    return token


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verify a token and return the user ID."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get the current authenticated user."""
    token = credentials.credentials
    user_id = verify_token(token, "access")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token"},
        )
    
    user = db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"},
        )
    
    return user


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """Get the current user if authenticated, otherwise None."""
    if not credentials:
        return None
    
    token = credentials.credentials
    user_id = verify_token(token, "access")
    
    if not user_id:
        return None
    
    return db.get_user_by_id(user_id)
