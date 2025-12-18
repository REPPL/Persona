"""
API configuration.

This module provides configuration for the FastAPI application.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class APIConfig(BaseSettings):
    """
    API server configuration.

    Configuration is loaded from environment variables with PERSONA_API_ prefix.

    Example:
        export PERSONA_API_HOST=0.0.0.0
        export PERSONA_API_PORT=8000
        export PERSONA_API_AUTH_ENABLED=true
        export PERSONA_API_AUTH_TOKEN=secret123
    """

    # Server settings
    host: str = Field(default="127.0.0.1", description="Server host")
    port: int = Field(default=8000, ge=1024, le=65535, description="Server port")
    workers: int = Field(default=1, ge=1, description="Number of worker processes")
    reload: bool = Field(default=False, description="Enable auto-reload in development")

    # API settings
    title: str = Field(default="Persona API", description="API title")
    version: str = Field(default="1.0.0", description="API version")
    description: str = Field(
        default="Generate realistic user personas from your data using AI",
        description="API description",
    )
    docs_url: Optional[str] = Field(default="/docs", description="OpenAPI docs URL")
    redoc_url: Optional[str] = Field(default="/redoc", description="ReDoc URL")

    # Authentication
    auth_enabled: bool = Field(default=False, description="Enable API authentication")
    auth_token: Optional[str] = Field(
        default=None, description="API authentication token"
    )

    # Rate limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(
        default=100, ge=1, description="Max requests per window"
    )
    rate_limit_window: int = Field(
        default=60, ge=1, description="Rate limit window (seconds)"
    )

    # CORS
    cors_enabled: bool = Field(default=True, description="Enable CORS")
    cors_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")

    # Webhooks
    webhook_timeout: int = Field(
        default=30, ge=1, le=300, description="Webhook timeout (seconds)"
    )
    webhook_max_retries: int = Field(
        default=3, ge=0, le=10, description="Webhook retry attempts"
    )
    webhook_retry_delay: float = Field(
        default=1.0, ge=0.1, description="Initial retry delay (seconds)"
    )

    class Config:
        """Pydantic configuration."""

        env_prefix = "PERSONA_API_"
        case_sensitive = False

    @classmethod
    def from_env(cls) -> "APIConfig":
        """
        Load configuration from environment variables.

        Returns:
            APIConfig loaded from environment.
        """
        return cls()

    def is_auth_required(self) -> bool:
        """Check if authentication is required."""
        return self.auth_enabled and self.auth_token is not None

    def validate_token(self, token: str) -> bool:
        """
        Validate API token.

        Args:
            token: Token to validate.

        Returns:
            True if token is valid.
        """
        if not self.is_auth_required():
            return True
        return self.auth_token == token
