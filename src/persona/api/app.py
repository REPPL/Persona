"""
FastAPI application factory.

This module creates and configures the FastAPI application.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from persona import __version__
from persona.api.config import APIConfig
from persona.api.middleware.logging import LoggingMiddleware
from persona.api.middleware.rate_limit import RateLimitMiddleware
from persona.api.routes import generate_router, health_router, webhooks_router
from persona.api.services.generation import GenerationService
from persona.api.services.webhook import WebhookManager

logger = logging.getLogger(__name__)


def create_app(config: APIConfig | None = None) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        config: API configuration. If None, loads from environment.

    Returns:
        Configured FastAPI application.
    """
    # Load config
    if config is None:
        config = APIConfig.from_env()

    # Create FastAPI app
    app = FastAPI(
        title=config.title,
        version=__version__,
        description=config.description,
        docs_url=config.docs_url,
        redoc_url=config.redoc_url,
    )

    # Store config in app state
    app.state.config = config

    # Initialise services
    generation_service = GenerationService()
    webhook_manager = WebhookManager(config)

    # Link services
    generation_service.set_webhook_manager(webhook_manager)

    # Store services in app state
    app.state.generation_service = generation_service
    app.state.webhook_manager = webhook_manager

    # Add middleware
    if config.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware, config=config)

    # Include routers
    app.include_router(health_router)
    app.include_router(generate_router)
    app.include_router(webhooks_router)

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "name": config.title,
            "version": __version__,
            "docs": config.docs_url,
            "health": "/api/v1/health",
        }

    logger.info(f"FastAPI application created (version: {__version__})")

    return app


# Default app instance for uvicorn
app = create_app()
