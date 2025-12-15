"""
API route handlers.

This module provides route handlers for all API endpoints.
"""

from persona.api.routes.generate import router as generate_router
from persona.api.routes.health import router as health_router
from persona.api.routes.webhooks import router as webhooks_router

__all__ = ["generate_router", "health_router", "webhooks_router"]
