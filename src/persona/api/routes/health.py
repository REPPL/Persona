"""
Health check endpoint.

This module provides health check functionality.
"""

from datetime import datetime

from fastapi import APIRouter

from persona import __version__
from persona.api.dependencies import ConfigDep
from persona.api.models.responses import HealthResponse

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(config: ConfigDep) -> HealthResponse:
    """
    Health check endpoint.

    Returns server health status and version information.

    Returns:
        HealthResponse with status, version, and timestamp.
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(),
    )
