"""
Rate limiting utilities (F-057).

Provides token bucket rate limiting, per-provider rate tracking,
and request queueing.
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        provider: str | None = None,
        retry_after: float | None = None,
    ):
        super().__init__(message)
        self.provider = provider
        self.retry_after = retry_after


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_minute: int = 60
    tokens_per_minute: int = 100000
    concurrent_requests: int = 5
    initial_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0

    def requests_per_second(self) -> float:
        """Calculate requests per second."""
        return self.requests_per_minute / 60.0

    def tokens_per_second(self) -> float:
        """Calculate tokens per second."""
        return self.tokens_per_minute / 60.0


# Default rate limits by provider
DEFAULT_RATE_LIMITS: dict[str, RateLimitConfig] = {
    "anthropic": RateLimitConfig(
        requests_per_minute=60,
        tokens_per_minute=100000,
        concurrent_requests=5,
    ),
    "openai": RateLimitConfig(
        requests_per_minute=60,
        tokens_per_minute=150000,
        concurrent_requests=10,
    ),
    "gemini": RateLimitConfig(
        requests_per_minute=60,
        tokens_per_minute=120000,
        concurrent_requests=5,
    ),
}


@dataclass
class RateLimitState:
    """Current state of rate limiting for a provider."""

    tokens: float
    last_update: float
    pending_requests: int = 0
    total_requests: int = 0
    total_tokens_used: int = 0
    last_request_time: float | None = None
    backoff_delay: float = 0.0


class RateLimiter:
    """
    Token bucket rate limiter for API requests.

    Implements the token bucket algorithm to manage request rates,
    with support for concurrent request limiting and exponential backoff.

    Example:
        >>> limiter = RateLimiter()
        >>> await limiter.acquire("anthropic")  # Waits if needed
        >>> # Make API request...
        >>> limiter.record_tokens("anthropic", 1500)  # Track token usage
    """

    def __init__(self, configs: dict[str, RateLimitConfig] | None = None):
        """
        Initialise the rate limiter.

        Args:
            configs: Provider-specific rate limit configurations.
        """
        self._configs = configs or DEFAULT_RATE_LIMITS.copy()
        self._state: dict[str, RateLimitState] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._semaphores: dict[str, asyncio.Semaphore] = {}

    def configure(self, provider: str, config: RateLimitConfig) -> None:
        """
        Configure rate limits for a provider.

        Args:
            provider: Provider name.
            config: Rate limit configuration.
        """
        self._configs[provider] = config
        # Reset state for this provider
        if provider in self._state:
            del self._state[provider]

    def get_config(self, provider: str) -> RateLimitConfig:
        """
        Get rate limit configuration for a provider.

        Args:
            provider: Provider name.

        Returns:
            Rate limit configuration.
        """
        return self._configs.get(provider, RateLimitConfig())

    def _get_state(self, provider: str) -> RateLimitState:
        """Get or create state for a provider."""
        if provider not in self._state:
            config = self.get_config(provider)
            self._state[provider] = RateLimitState(
                tokens=config.requests_per_minute,  # Start with full bucket
                last_update=time.monotonic(),
            )
        return self._state[provider]

    def _get_lock(self, provider: str) -> asyncio.Lock:
        """Get or create lock for a provider."""
        if provider not in self._locks:
            self._locks[provider] = asyncio.Lock()
        return self._locks[provider]

    def _get_semaphore(self, provider: str) -> asyncio.Semaphore:
        """Get or create semaphore for concurrent request limiting."""
        if provider not in self._semaphores:
            config = self.get_config(provider)
            self._semaphores[provider] = asyncio.Semaphore(config.concurrent_requests)
        return self._semaphores[provider]

    def _refill_tokens(self, provider: str) -> None:
        """Refill tokens based on elapsed time."""
        state = self._get_state(provider)
        config = self.get_config(provider)

        now = time.monotonic()
        elapsed = now - state.last_update
        state.last_update = now

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * config.requests_per_second()
        state.tokens = min(
            state.tokens + tokens_to_add,
            config.requests_per_minute,  # Bucket capacity
        )

    async def acquire(
        self,
        provider: str,
        tokens: int = 1,
        timeout: float | None = None,
    ) -> float:
        """
        Acquire permission to make a request.

        Waits until tokens are available, respecting rate limits.

        Args:
            provider: Provider name.
            tokens: Number of tokens to acquire.
            timeout: Maximum time to wait (None for no limit).

        Returns:
            Time waited in seconds.

        Raises:
            RateLimitExceeded: If timeout exceeded.
        """
        start_time = time.monotonic()
        lock = self._get_lock(provider)
        semaphore = self._get_semaphore(provider)

        # Wait for concurrent request slot
        try:
            await asyncio.wait_for(semaphore.acquire(), timeout=timeout)
        except asyncio.TimeoutError:
            raise RateLimitExceeded(
                f"Timeout waiting for request slot for {provider}",
                provider=provider,
            )

        try:
            async with lock:
                while True:
                    self._refill_tokens(provider)
                    state = self._get_state(provider)

                    # Check if we need to wait due to backoff
                    if state.backoff_delay > 0:
                        wait_time = state.backoff_delay
                        state.backoff_delay = 0  # Reset after waiting
                        await asyncio.sleep(wait_time)
                        continue

                    # Check if tokens available
                    if state.tokens >= tokens:
                        state.tokens -= tokens
                        state.pending_requests += 1
                        state.total_requests += 1
                        state.last_request_time = time.monotonic()
                        break

                    # Calculate wait time
                    config = self.get_config(provider)
                    tokens_needed = tokens - state.tokens
                    wait_time = tokens_needed / config.requests_per_second()

                    # Check timeout
                    elapsed = time.monotonic() - start_time
                    if timeout and elapsed + wait_time > timeout:
                        semaphore.release()
                        raise RateLimitExceeded(
                            f"Rate limit would exceed timeout for {provider}",
                            provider=provider,
                            retry_after=wait_time,
                        )

                    await asyncio.sleep(min(wait_time, 1.0))  # Wait in chunks

            return time.monotonic() - start_time

        except Exception:
            semaphore.release()
            raise

    def release(self, provider: str) -> None:
        """
        Release a request slot after completion.

        Args:
            provider: Provider name.
        """
        semaphore = self._get_semaphore(provider)
        state = self._get_state(provider)
        state.pending_requests = max(0, state.pending_requests - 1)
        try:
            semaphore.release()
        except ValueError:
            pass  # Already released

    def record_tokens(self, provider: str, tokens_used: int) -> None:
        """
        Record token usage for a provider.

        Args:
            provider: Provider name.
            tokens_used: Number of tokens used.
        """
        state = self._get_state(provider)
        state.total_tokens_used += tokens_used

    def record_rate_limit_response(
        self,
        provider: str,
        retry_after: float | None = None,
    ) -> None:
        """
        Record a 429 rate limit response.

        Sets backoff delay for next request.

        Args:
            provider: Provider name.
            retry_after: Retry-After header value in seconds.
        """
        state = self._get_state(provider)
        config = self.get_config(provider)

        if retry_after:
            state.backoff_delay = retry_after
        else:
            # Use exponential backoff
            current_delay = state.backoff_delay or config.initial_delay
            state.backoff_delay = min(
                current_delay * config.backoff_multiplier,
                config.max_delay,
            )

    def get_status(self, provider: str) -> dict[str, Any]:
        """
        Get current rate limit status for a provider.

        Args:
            provider: Provider name.

        Returns:
            Dictionary with status information.
        """
        self._refill_tokens(provider)
        state = self._get_state(provider)
        config = self.get_config(provider)

        return {
            "provider": provider,
            "available_tokens": state.tokens,
            "max_tokens": config.requests_per_minute,
            "pending_requests": state.pending_requests,
            "max_concurrent": config.concurrent_requests,
            "total_requests": state.total_requests,
            "total_tokens_used": state.total_tokens_used,
            "requests_per_minute": config.requests_per_minute,
            "tokens_per_minute": config.tokens_per_minute,
        }

    def reset(self, provider: str | None = None) -> None:
        """
        Reset rate limit state.

        Args:
            provider: Provider to reset, or None for all.
        """
        if provider:
            if provider in self._state:
                del self._state[provider]
        else:
            self._state.clear()


class SyncRateLimiter:
    """
    Synchronous rate limiter for non-async contexts.

    Example:
        >>> limiter = SyncRateLimiter()
        >>> wait_time = limiter.acquire("anthropic")
        >>> # Make API request...
        >>> limiter.release("anthropic")
    """

    def __init__(self, configs: dict[str, RateLimitConfig] | None = None):
        """Initialise the synchronous rate limiter."""
        self._configs = configs or DEFAULT_RATE_LIMITS.copy()
        self._state: dict[str, RateLimitState] = {}
        import threading
        self._locks: dict[str, threading.Lock] = {}

    def get_config(self, provider: str) -> RateLimitConfig:
        """Get rate limit configuration for a provider."""
        return self._configs.get(provider, RateLimitConfig())

    def _get_state(self, provider: str) -> RateLimitState:
        """Get or create state for a provider."""
        if provider not in self._state:
            config = self.get_config(provider)
            self._state[provider] = RateLimitState(
                tokens=config.requests_per_minute,
                last_update=time.monotonic(),
            )
        return self._state[provider]

    def _get_lock(self, provider: str):
        """Get or create lock for a provider."""
        import threading
        if provider not in self._locks:
            self._locks[provider] = threading.Lock()
        return self._locks[provider]

    def _refill_tokens(self, provider: str) -> None:
        """Refill tokens based on elapsed time."""
        state = self._get_state(provider)
        config = self.get_config(provider)

        now = time.monotonic()
        elapsed = now - state.last_update
        state.last_update = now

        tokens_to_add = elapsed * config.requests_per_second()
        state.tokens = min(
            state.tokens + tokens_to_add,
            config.requests_per_minute,
        )

    def acquire(
        self,
        provider: str,
        tokens: int = 1,
        timeout: float | None = None,
    ) -> float:
        """
        Acquire permission to make a request (blocking).

        Args:
            provider: Provider name.
            tokens: Number of tokens to acquire.
            timeout: Maximum time to wait.

        Returns:
            Time waited in seconds.
        """
        start_time = time.monotonic()
        lock = self._get_lock(provider)

        with lock:
            while True:
                self._refill_tokens(provider)
                state = self._get_state(provider)

                if state.tokens >= tokens:
                    state.tokens -= tokens
                    state.total_requests += 1
                    state.last_request_time = time.monotonic()
                    return time.monotonic() - start_time

                # Calculate wait time
                config = self.get_config(provider)
                tokens_needed = tokens - state.tokens
                wait_time = tokens_needed / config.requests_per_second()

                # Check timeout
                elapsed = time.monotonic() - start_time
                if timeout and elapsed + wait_time > timeout:
                    raise RateLimitExceeded(
                        f"Rate limit would exceed timeout for {provider}",
                        provider=provider,
                        retry_after=wait_time,
                    )

                time.sleep(min(wait_time, 1.0))

    def release(self, provider: str) -> None:
        """Release a request slot (no-op for sync limiter)."""
        pass

    def get_status(self, provider: str) -> dict[str, Any]:
        """Get current rate limit status."""
        self._refill_tokens(provider)
        state = self._get_state(provider)
        config = self.get_config(provider)

        return {
            "provider": provider,
            "available_tokens": state.tokens,
            "max_tokens": config.requests_per_minute,
            "total_requests": state.total_requests,
        }
