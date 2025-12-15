"""
Rate limiting middleware.

This middleware provides simple in-memory rate limiting based on IP address.
"""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from persona.api.config import APIConfig


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.

    Tracks requests per IP address within a time window.
    """

    def __init__(self, app, config: APIConfig):
        """
        Initialise rate limiting middleware.

        Args:
            app: FastAPI application.
            config: API configuration.
        """
        super().__init__(app)
        self.config = config
        self.requests: defaultdict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and enforce rate limits.

        Args:
            request: HTTP request.
            call_next: Next middleware/handler.

        Returns:
            HTTP response.
        """
        # Skip rate limiting if disabled
        if not self.config.rate_limit_enabled:
            return await call_next(request)

        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"

        # Current timestamp
        now = time.time()

        # Remove old requests outside the window
        window_start = now - self.config.rate_limit_window
        self.requests[client_ip] = [
            timestamp
            for timestamp in self.requests[client_ip]
            if timestamp > window_start
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.config.rate_limit_requests:
            # Calculate retry-after
            oldest_request = min(self.requests[client_ip])
            retry_after = int(oldest_request + self.config.rate_limit_window - now) + 1

            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.config.rate_limit_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(oldest_request + self.config.rate_limit_window)),
                },
            )

        # Record this request
        self.requests[client_ip].append(now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self.config.rate_limit_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.config.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(now + self.config.rate_limit_window))

        return response
