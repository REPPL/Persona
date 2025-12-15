"""
API request and response models.

This module provides Pydantic models for API requests and responses.
"""

from persona.api.models.requests import (
    GenerateRequest,
    QualityScoreRequest,
    WebhookRegisterRequest,
)
from persona.api.models.responses import (
    ErrorResponse,
    GenerateResponse,
    HealthResponse,
    JobStatusResponse,
    QualityScoreResponse,
    SuccessResponse,
    WebhookResponse,
)

__all__ = [
    # Request models
    "GenerateRequest",
    "QualityScoreRequest",
    "WebhookRegisterRequest",
    # Response models
    "ErrorResponse",
    "GenerateResponse",
    "HealthResponse",
    "JobStatusResponse",
    "QualityScoreResponse",
    "SuccessResponse",
    "WebhookResponse",
]
