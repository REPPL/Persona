"""
HTTP base provider with connection pooling.

This module provides a base class for HTTP-based LLM providers
with connection pooling for improved performance.
"""

import asyncio
from typing import Any

import httpx

from persona.core.providers.base import LLMProvider, LLMResponse


class HTTPProvider(LLMProvider):
    """
    Base provider with HTTP connection pooling.

    Provides a shared httpx client with connection pooling for
    improved performance in batch operations. Both sync and async
    clients are lazily initialised and reused across requests.

    Configuration options:
        timeout: Request timeout in seconds (default: 120.0)
        max_connections: Maximum concurrent connections (default: 10)
        max_keepalive_connections: Keep-alive connections (default: 5)

    Example:
        class MyProvider(HTTPProvider):
            def generate(self, prompt, **kwargs):
                client = self.get_sync_client()
                response = client.post(self.API_URL, json=payload)
                return self._parse_response(response)

            async def generate_async(self, prompt, **kwargs):
                client = await self.get_async_client()
                response = await client.post(self.API_URL, json=payload)
                return self._parse_response(response)
    """

    # Default connection pool settings
    DEFAULT_TIMEOUT = 120.0
    DEFAULT_MAX_CONNECTIONS = 10
    DEFAULT_MAX_KEEPALIVE = 5

    # Class-level clients for connection pooling
    # Using class variables ensures all instances share the same pools
    _sync_client: httpx.Client | None = None
    _async_client: httpx.AsyncClient | None = None
    _lock: asyncio.Lock | None = None

    def __init__(
        self,
        timeout: float | None = None,
        max_connections: int | None = None,
        max_keepalive_connections: int | None = None,
    ) -> None:
        """
        Initialise the HTTP provider.

        Args:
            timeout: Request timeout in seconds.
            max_connections: Maximum concurrent connections.
            max_keepalive_connections: Maximum keep-alive connections.
        """
        self._timeout = timeout or self.DEFAULT_TIMEOUT
        self._max_connections = max_connections or self.DEFAULT_MAX_CONNECTIONS
        self._max_keepalive = max_keepalive_connections or self.DEFAULT_MAX_KEEPALIVE

    @classmethod
    def _get_timeout(cls, timeout: float | None = None) -> httpx.Timeout:
        """Get timeout configuration."""
        t = timeout or cls.DEFAULT_TIMEOUT
        return httpx.Timeout(t, connect=10.0)

    @classmethod
    def _get_limits(
        cls,
        max_connections: int | None = None,
        max_keepalive: int | None = None,
    ) -> httpx.Limits:
        """Get connection pool limits."""
        return httpx.Limits(
            max_connections=max_connections or cls.DEFAULT_MAX_CONNECTIONS,
            max_keepalive_connections=max_keepalive or cls.DEFAULT_MAX_KEEPALIVE,
        )

    def get_sync_client(self) -> httpx.Client:
        """
        Get or create the synchronous HTTP client.

        Returns a shared client instance for connection pooling.
        The client is created on first use and reused for all requests.

        Returns:
            Shared httpx.Client instance.
        """
        if HTTPProvider._sync_client is None or HTTPProvider._sync_client.is_closed:
            HTTPProvider._sync_client = httpx.Client(
                timeout=self._get_timeout(self._timeout),
                limits=self._get_limits(self._max_connections, self._max_keepalive),
            )
        return HTTPProvider._sync_client

    async def get_async_client(self) -> httpx.AsyncClient:
        """
        Get or create the asynchronous HTTP client.

        Returns a shared client instance for connection pooling.
        The client is created on first use and reused for all requests.
        Uses a lock to ensure thread-safe initialisation.

        Returns:
            Shared httpx.AsyncClient instance.
        """
        # Lazy initialise the lock
        if HTTPProvider._lock is None:
            HTTPProvider._lock = asyncio.Lock()

        async with HTTPProvider._lock:
            if (
                HTTPProvider._async_client is None
                or HTTPProvider._async_client.is_closed
            ):
                HTTPProvider._async_client = httpx.AsyncClient(
                    timeout=self._get_timeout(self._timeout),
                    limits=self._get_limits(self._max_connections, self._max_keepalive),
                )
        return HTTPProvider._async_client

    @classmethod
    def cleanup_sync(cls) -> None:
        """
        Close the synchronous HTTP client.

        Should be called during application shutdown to release resources.
        """
        if cls._sync_client is not None and not cls._sync_client.is_closed:
            cls._sync_client.close()
            cls._sync_client = None

    @classmethod
    async def cleanup_async(cls) -> None:
        """
        Close the asynchronous HTTP client.

        Should be called during application shutdown to release resources.
        """
        if cls._async_client is not None and not cls._async_client.is_closed:
            await cls._async_client.aclose()
            cls._async_client = None

    @classmethod
    async def cleanup(cls) -> None:
        """
        Close all HTTP clients.

        Convenience method that closes both sync and async clients.
        """
        cls.cleanup_sync()
        await cls.cleanup_async()

    # Abstract methods from LLMProvider that subclasses must implement
    @property
    def name(self) -> str:
        raise NotImplementedError("Subclasses must implement name")

    @property
    def default_model(self) -> str:
        raise NotImplementedError("Subclasses must implement default_model")

    @property
    def available_models(self) -> list[str]:
        raise NotImplementedError("Subclasses must implement available_models")

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        raise NotImplementedError("Subclasses must implement generate")

    def is_configured(self) -> bool:
        raise NotImplementedError("Subclasses must implement is_configured")
