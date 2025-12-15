"""
Authentication middleware.

This middleware handles API key authentication via headers.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from persona.api.config import APIConfig


class AuthMiddleware(BaseHTTPMiddleware):
    """
    API key authentication middleware.

    Validates X-API-Key header for protected endpoints.
    """

    def __init__(self, app, config: APIConfig):
        """
        Initialise authentication middleware.

        Args:
            app: FastAPI application.
            config: API configuration.
        """
        super().__init__(app)
        self.config = config

        # Endpoints that don't require authentication
        self.public_paths = {
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and verify authentication.

        Args:
            request: HTTP request.
            call_next: Next middleware/handler.

        Returns:
            HTTP response.
        """
        # Skip auth for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Skip auth if not enabled
        if not self.config.is_auth_required():
            return await call_next(request)

        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "authentication_required",
                    "message": "API key required. Provide X-API-Key header.",
                },
            )

        # Validate API key
        if not self.config.validate_token(api_key):
            return JSONResponse(
                status_code=401,
                content={
                    "error": "invalid_api_key",
                    "message": "Invalid API key.",
                },
            )

        # Add timing
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        return response
