"""
Request logging middleware.

This middleware logs all HTTP requests and responses.
"""

import logging
import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Request/response logging middleware.

    Logs HTTP method, path, status code, and processing time.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: HTTP request.
            call_next: Next middleware/handler.

        Returns:
            HTTP response.
        """
        # Start timing
        start_time = time.time()

        # Log request
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"{request.method} {request.url.path} - Client: {client_ip}")

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"{request.method} {request.url.path} - ERROR: {str(e)} - {process_time:.3f}s"
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"{request.method} {request.url.path} - Status: {response.status_code} - {process_time:.3f}s"
        )

        # Add timing header
        response.headers["X-Process-Time"] = f"{process_time:.3f}"

        return response
