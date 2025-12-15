"""
API response models.

This module defines Pydantic models for API responses.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """
    Generic success response.

    Example:
        {
            "success": true,
            "message": "Operation completed successfully"
        }
    """

    success: bool = Field(default=True, description="Operation success status")
    message: str = Field(..., description="Success message")


class ErrorResponse(BaseModel):
    """
    Generic error response.

    Example:
        {
            "success": false,
            "error": "invalid_input",
            "message": "Invalid data source path",
            "details": {"field": "data"}
        }
    """

    success: bool = Field(default=False, description="Operation success status")
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict[str, Any]] = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """
    Health check response.

    Example:
        {
            "status": "healthy",
            "version": "1.1.0",
            "timestamp": "2025-12-15T10:30:00Z"
        }
    """

    status: str = Field(..., description="Health status (healthy, unhealthy)")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current server time")


class GenerateResponse(BaseModel):
    """
    Generation job response.

    Example:
        {
            "job_id": "job-abc123",
            "status": "pending",
            "message": "Generation job created",
            "status_url": "/api/v1/generate/job-abc123"
        }
    """

    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status (pending, running, completed, failed)")
    message: str = Field(..., description="Status message")
    status_url: str = Field(..., description="URL to check job status")


class JobStatusResponse(BaseModel):
    """
    Job status response.

    Example:
        {
            "job_id": "job-abc123",
            "status": "completed",
            "progress": 100,
            "created_at": "2025-12-15T10:30:00Z",
            "completed_at": "2025-12-15T10:35:00Z",
            "result": {
                "personas": [...],
                "experiment_id": "exp-def456"
            }
        }
    """

    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Job status")
    progress: Optional[int] = Field(default=None, ge=0, le=100, description="Progress percentage")
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(default=None, description="Job start time")
    completed_at: Optional[datetime] = Field(default=None, description="Job completion time")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    result: Optional[dict[str, Any]] = Field(default=None, description="Job result data")


class QualityScoreResponse(BaseModel):
    """
    Quality score response.

    Example:
        {
            "persona_id": "persona-abc123",
            "score": 0.85,
            "metrics": {
                "completeness": 0.9,
                "consistency": 0.8,
                "realism": 0.85
            }
        }
    """

    persona_id: Optional[str] = Field(default=None, description="Persona identifier")
    score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score")
    metrics: dict[str, float] = Field(..., description="Individual quality metrics")


class WebhookResponse(BaseModel):
    """
    Webhook registration response.

    Example:
        {
            "webhook_id": "webhook-abc123",
            "url": "https://example.com/webhook",
            "events": ["generation.completed"],
            "created_at": "2025-12-15T10:30:00Z"
        }
    """

    webhook_id: str = Field(..., description="Webhook identifier")
    url: str = Field(..., description="Webhook URL")
    events: list[str] = Field(..., description="Subscribed events")
    created_at: datetime = Field(..., description="Registration time")
