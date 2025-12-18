"""
API request models.

This module defines Pydantic models for API requests.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """
    Request model for persona generation.

    Example:
        {
            "data": "./interviews.csv",
            "count": 3,
            "provider": "anthropic",
            "model": "claude-sonnet-4-5-20250929",
            "config": {
                "complexity": "moderate",
                "detail_level": "standard"
            },
            "webhook_url": "https://example.com/webhook"
        }
    """

    data: str = Field(..., description="Path or URL to data source")
    count: Optional[int] = Field(
        default=3, ge=1, le=20, description="Number of personas to generate"
    )
    provider: Optional[str] = Field(
        default=None, description="LLM provider (anthropic, openai, gemini)"
    )
    model: Optional[str] = Field(default=None, description="Model identifier")
    config: Optional[dict[str, Any]] = Field(
        default=None, description="Generation configuration"
    )
    webhook_url: Optional[str] = Field(
        default=None, description="URL for completion webhook"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "data": "./interviews.csv",
                "count": 3,
                "provider": "anthropic",
                "model": "claude-sonnet-4-5-20250929",
                "config": {
                    "complexity": "moderate",
                    "detail_level": "standard",
                },
                "webhook_url": "https://example.com/webhook",
            }
        }


class QualityScoreRequest(BaseModel):
    """
    Request model for quality scoring.

    Example:
        {
            "persona_id": "persona-abc123",
            "experiment_id": "exp-def456"
        }
    """

    persona_id: Optional[str] = Field(default=None, description="Persona ID to score")
    experiment_id: Optional[str] = Field(
        default=None, description="Experiment ID to score"
    )
    data: Optional[dict[str, Any]] = Field(
        default=None, description="Raw persona data to score"
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "persona_id": "persona-abc123",
                "experiment_id": "exp-def456",
            }
        }


class WebhookRegisterRequest(BaseModel):
    """
    Request model for webhook registration.

    Example:
        {
            "url": "https://example.com/webhook",
            "events": ["generation.completed", "generation.failed"],
            "secret": "webhook-secret-123"
        }
    """

    url: str = Field(..., description="Webhook URL")
    events: list[str] = Field(
        default=["generation.completed", "generation.failed"],
        description="Events to subscribe to",
    )
    secret: Optional[str] = Field(default=None, description="Secret for HMAC signature")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "url": "https://example.com/webhook",
                "events": ["generation.completed", "generation.failed"],
                "secret": "webhook-secret-123",
            }
        }
