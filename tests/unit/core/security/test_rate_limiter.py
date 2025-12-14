"""Tests for rate limiting (F-057)."""

import asyncio
import time
import pytest

from persona.core.security.rate_limiter import (
    RateLimiter,
    SyncRateLimiter,
    RateLimitConfig,
    RateLimitExceeded,
    DEFAULT_RATE_LIMITS,
)


class TestRateLimitConfig:
    """Tests for RateLimitConfig."""

    def test_default_values(self):
        """Default configuration values."""
        config = RateLimitConfig()
        assert config.requests_per_minute == 60
        assert config.tokens_per_minute == 100000
        assert config.concurrent_requests == 5

    def test_requests_per_second(self):
        """Calculates requests per second."""
        config = RateLimitConfig(requests_per_minute=120)
        assert config.requests_per_second() == 2.0

    def test_tokens_per_second(self):
        """Calculates tokens per second."""
        config = RateLimitConfig(tokens_per_minute=60000)
        assert config.tokens_per_second() == 1000.0


class TestDefaultRateLimits:
    """Tests for default rate limits."""

    def test_anthropic_limits(self):
        """Anthropic has default limits."""
        assert "anthropic" in DEFAULT_RATE_LIMITS
        config = DEFAULT_RATE_LIMITS["anthropic"]
        assert config.requests_per_minute > 0

    def test_openai_limits(self):
        """OpenAI has default limits."""
        assert "openai" in DEFAULT_RATE_LIMITS

    def test_gemini_limits(self):
        """Gemini has default limits."""
        assert "gemini" in DEFAULT_RATE_LIMITS


class TestRateLimiter:
    """Tests for async RateLimiter."""

    @pytest.mark.asyncio
    async def test_acquire_success(self):
        """Acquires token successfully."""
        limiter = RateLimiter()
        wait_time = await limiter.acquire("anthropic")
        assert wait_time >= 0

    @pytest.mark.asyncio
    async def test_acquire_multiple(self):
        """Acquires multiple tokens."""
        limiter = RateLimiter()
        limiter.configure("test", RateLimitConfig(requests_per_minute=1000))

        for _ in range(5):
            await limiter.acquire("test")

        status = limiter.get_status("test")
        assert status["total_requests"] == 5

    @pytest.mark.asyncio
    async def test_release(self):
        """Releases request slot."""
        limiter = RateLimiter()
        await limiter.acquire("anthropic")
        limiter.release("anthropic")

        status = limiter.get_status("anthropic")
        assert status["pending_requests"] == 0

    @pytest.mark.asyncio
    async def test_record_tokens(self):
        """Records token usage."""
        limiter = RateLimiter()
        await limiter.acquire("anthropic")
        limiter.record_tokens("anthropic", 1500)

        status = limiter.get_status("anthropic")
        assert status["total_tokens_used"] == 1500

    @pytest.mark.asyncio
    async def test_rate_limit_response(self):
        """Handles rate limit response."""
        limiter = RateLimiter()
        limiter.record_rate_limit_response("anthropic", retry_after=5.0)

        state = limiter._get_state("anthropic")
        assert state.backoff_delay == 5.0

    def test_configure(self):
        """Configures provider limits."""
        limiter = RateLimiter()
        limiter.configure(
            "custom",
            RateLimitConfig(requests_per_minute=30),
        )

        config = limiter.get_config("custom")
        assert config.requests_per_minute == 30

    def test_get_status(self):
        """Gets rate limit status."""
        limiter = RateLimiter()
        status = limiter.get_status("anthropic")

        assert "provider" in status
        assert "available_tokens" in status
        assert "requests_per_minute" in status

    def test_reset(self):
        """Resets rate limit state."""
        limiter = RateLimiter()
        limiter._get_state("test")  # Create state
        limiter.reset("test")

        assert "test" not in limiter._state

    def test_reset_all(self):
        """Resets all rate limit state."""
        limiter = RateLimiter()
        limiter._get_state("test1")
        limiter._get_state("test2")
        limiter.reset()

        assert len(limiter._state) == 0

    @pytest.mark.asyncio
    async def test_timeout_exceeded(self):
        """Raises exception on timeout."""
        limiter = RateLimiter()
        limiter.configure(
            "slow",
            RateLimitConfig(
                requests_per_minute=1,
                concurrent_requests=1,
            ),
        )

        # Exhaust the token
        await limiter.acquire("slow")

        # Next request should timeout quickly
        with pytest.raises(RateLimitExceeded):
            await limiter.acquire("slow", timeout=0.01)


class TestSyncRateLimiter:
    """Tests for synchronous RateLimiter."""

    def test_acquire_success(self):
        """Acquires token successfully."""
        limiter = SyncRateLimiter()
        wait_time = limiter.acquire("anthropic")
        assert wait_time >= 0

    def test_acquire_multiple(self):
        """Acquires multiple tokens."""
        limiter = SyncRateLimiter()
        limiter._configs["test"] = RateLimitConfig(requests_per_minute=1000)

        for _ in range(3):
            limiter.acquire("test")

        status = limiter.get_status("test")
        assert status["total_requests"] == 3

    def test_get_status(self):
        """Gets rate limit status."""
        limiter = SyncRateLimiter()
        status = limiter.get_status("anthropic")

        assert "provider" in status
        assert "available_tokens" in status

    def test_timeout_exceeded(self):
        """Raises exception on timeout."""
        limiter = SyncRateLimiter()
        limiter._configs["slow"] = RateLimitConfig(requests_per_minute=1)

        # Exhaust the token
        limiter.acquire("slow")

        # Next request should timeout quickly
        with pytest.raises(RateLimitExceeded):
            limiter.acquire("slow", timeout=0.01)


class TestRateLimitExceeded:
    """Tests for RateLimitExceeded exception."""

    def test_exception_attributes(self):
        """Exception has required attributes."""
        exc = RateLimitExceeded(
            "Rate limit exceeded",
            provider="anthropic",
            retry_after=30.0,
        )

        assert exc.provider == "anthropic"
        assert exc.retry_after == 30.0
        assert "Rate limit exceeded" in str(exc)
