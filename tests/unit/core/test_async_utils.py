"""
Tests for async utilities module.
"""

import asyncio
import time

import pytest
from persona.core.async_utils import (
    AsyncBatchProcessor,
    AsyncProgressTracker,
    AsyncRateLimiter,
    async_timeout,
    gather_with_concurrency,
    retry_async,
)


@pytest.mark.asyncio
class TestAsyncRateLimiter:
    """Test AsyncRateLimiter functionality."""

    async def test_rate_limiter_limits_concurrency(self):
        """Test that rate limiter limits concurrent operations."""
        limiter = AsyncRateLimiter(max_concurrent=2)
        active = 0
        max_active = 0

        async def task():
            nonlocal active, max_active
            async with limiter:
                active += 1
                max_active = max(max_active, active)
                await asyncio.sleep(0.1)
                active -= 1

        await asyncio.gather(*[task() for _ in range(10)])
        assert max_active == 2

    async def test_rate_limiter_enforces_delay(self):
        """Test that rate limiter enforces minimum delay."""
        limiter = AsyncRateLimiter(max_concurrent=1, min_delay=0.1)
        times = []

        async def task():
            async with limiter:
                times.append(time.monotonic())

        await asyncio.gather(*[task() for _ in range(3)])

        # Check delays between operations
        for i in range(1, len(times)):
            delay = times[i] - times[i - 1]
            assert delay >= 0.09  # Allow small tolerance


@pytest.mark.asyncio
class TestRetryAsync:
    """Test retry_async functionality."""

    async def test_retry_succeeds_on_first_attempt(self):
        """Test retry succeeds when function works first time."""
        call_count = 0

        async def succeeds():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await retry_async(succeeds, max_retries=3)
        assert result == "success"
        assert call_count == 1

    async def test_retry_succeeds_after_failures(self):
        """Test retry succeeds after some failures."""
        call_count = 0

        async def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("fail")
            return "success"

        result = await retry_async(fails_twice, max_retries=3, base_delay=0.01)
        assert result == "success"
        assert call_count == 3

    async def test_retry_raises_after_max_retries(self):
        """Test retry raises exception after max retries."""
        call_count = 0

        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")

        with pytest.raises(ValueError):
            await retry_async(always_fails, max_retries=2, base_delay=0.01)

        assert call_count == 3  # Initial + 2 retries

    async def test_retry_respects_exception_filter(self):
        """Test retry only catches specified exceptions."""
        call_count = 0

        async def raises_runtime_error():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("fail")

        with pytest.raises(RuntimeError):
            await retry_async(
                raises_runtime_error,
                max_retries=2,
                base_delay=0.01,
                exceptions=(ValueError,),  # Only catch ValueError
            )

        assert call_count == 1  # No retries for RuntimeError


@pytest.mark.asyncio
class TestAsyncTimeout:
    """Test async_timeout decorator."""

    async def test_timeout_passes_when_within_limit(self):
        """Test timeout allows function to complete within limit."""

        @async_timeout(1.0)
        async def fast_operation():
            await asyncio.sleep(0.1)
            return "done"

        result = await fast_operation()
        assert result == "done"

    async def test_timeout_raises_when_exceeded(self):
        """Test timeout raises TimeoutError when exceeded."""

        @async_timeout(0.1)
        async def slow_operation():
            await asyncio.sleep(1.0)
            return "done"

        with pytest.raises(asyncio.TimeoutError):
            await slow_operation()


@pytest.mark.asyncio
class TestGatherWithConcurrency:
    """Test gather_with_concurrency functionality."""

    async def test_gathers_all_results(self):
        """Test that all tasks complete and return results."""

        async def task(value):
            await asyncio.sleep(0.01)
            return value * 2

        tasks = [task(i) for i in range(10)]
        results = await gather_with_concurrency(3, *tasks)

        assert len(results) == 10
        assert results == [i * 2 for i in range(10)]

    async def test_limits_concurrency(self):
        """Test that concurrency is limited."""
        active = 0
        max_active = 0

        async def task():
            nonlocal active, max_active
            active += 1
            max_active = max(max_active, active)
            await asyncio.sleep(0.1)
            active -= 1
            return "done"

        tasks = [task() for _ in range(10)]
        await gather_with_concurrency(3, *tasks)

        assert max_active == 3


@pytest.mark.asyncio
class TestAsyncBatchProcessor:
    """Test AsyncBatchProcessor functionality."""

    async def test_processes_all_items(self):
        """Test that all items are processed."""
        processor = AsyncBatchProcessor(batch_size=3, max_concurrent=2)
        items = list(range(10))

        async def process(item):
            return item * 2

        results = await processor.process(items, process)

        assert len(results) == 10
        assert results == [i * 2 for i in range(10)]

    async def test_calls_progress_callback(self):
        """Test that progress callback is called."""
        processor = AsyncBatchProcessor(batch_size=2, max_concurrent=1)
        items = list(range(5))
        progress_calls = []

        async def process(item):
            return item

        async def progress_callback(completed, total):
            progress_calls.append((completed, total))

        await processor.process(items, process, progress_callback)

        assert len(progress_calls) > 0
        assert progress_calls[-1] == (5, 5)  # Final call


@pytest.mark.asyncio
class TestAsyncProgressTracker:
    """Test AsyncProgressTracker functionality."""

    async def test_tracks_progress(self):
        """Test that progress is tracked correctly."""
        tracker = AsyncProgressTracker(total=10)

        for _ in range(5):
            await tracker.update(1)

        assert tracker.completed == 5
        assert tracker.total == 10
        assert tracker.percentage == 50.0

    async def test_calls_callbacks(self):
        """Test that callbacks are called on update."""
        tracker = AsyncProgressTracker(total=10)
        calls = []

        async def callback(completed, total):
            calls.append((completed, total))

        tracker.add_callback(callback)

        await tracker.update(3)
        await tracker.update(2)

        assert len(calls) == 2
        assert calls[0] == (3, 10)
        assert calls[1] == (5, 10)

    async def test_reset_clears_progress(self):
        """Test that reset clears progress."""
        tracker = AsyncProgressTracker(total=10)

        await tracker.update(5)
        assert tracker.completed == 5

        await tracker.reset()
        assert tracker.completed == 0
