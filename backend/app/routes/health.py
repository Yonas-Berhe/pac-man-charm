"""
Health check route.
"""

from datetime import datetime, timezone
from fastapi import APIRouter

from app.models import HealthResponse


router = APIRouter(tags=["Health"])


def utc_now() -> datetime:
    """Get current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": utc_now(),
    }
