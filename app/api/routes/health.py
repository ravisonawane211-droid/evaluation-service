"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter

from app.schemas.health_response import HealthResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="Basic health check",
    description="Returns basic health status of the service.",
)
async def health_check() -> HealthResponse:
    """
    Perform a health check for the service.
    Returns:
        HealthResponse: A response object containing the health status and current timestamp.
            - status: A string indicating the service is "healthy"
            - timestamp: The current datetime when the check was performed
    Raises:
        None
    Example:
        >>> response = await health_check()
        >>> print(response.status)
        'healthy'
    """

    logger.debug("Health check requested")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )