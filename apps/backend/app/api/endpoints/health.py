"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def health_check():
    """
    Health check endpoint.
    Returns the current status of the API.
    """
    return {
        "status": "healthy",
        "service": "StraRun API",
        "version": "0.1.0",
    }
