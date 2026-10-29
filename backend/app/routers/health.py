"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get(
    "/api/health",
    summary="Service health check",
    response_model=dict,
)
async def health_check() -> dict:
    """Check if the service is running and healthy.

    Returns:
        Dictionary with service status and version.
    """
    return {
        "status": "healthy",
        "service": "RepoLens",
        "version": "1.0.0",
    }
