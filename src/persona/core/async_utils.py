"""
Async utilities for concurrent operations.

This module provides utilities for async operations including
semaphore-based rate limiting, retry logic, and batch processing.
"""

import asyncio
import functools
import time
from typing import Any, Awaitable, Callable, TypeVar

T = TypeVar("T")


class AsyncRateLimiter:
    """
    Semaphore-based rate limiter for async operations.

    Limits the number of concurrent operations and enforces
    a minimum delay between operations.

    Example:
        limiter = AsyncRateLimiter(max_concurrent=3, min_delay=0.5)

        async with limiter:
            result = await expensive_operation()
    """

    def __init__(
        self,
        max_concurrent: int = 5,
        min_delay: float = 0.0,
    ) -> None:
        """
        Initialise the rate limiter.

        Args:
            max_concurrent: Maximum number of concurrent operations.
            min_delay: Minimum delay in seconds between operations.
        """
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._min_delay = min_delay
        self._last_call: float = 0.0
        self._delay_lock = asyncio.Lock()

    async def __aenter__(self) -> "AsyncRateLimiter":
        """Acquire semaphore and enforce delay."""
        await self._semaphore.acquire()

        # Enforce minimum delay
        if self._min_delay > 0:
            async with self._delay_lock:
                now = time.monotonic()
                elapsed = now - self._last_call
                if elapsed < self._min_delay:
                    await asyncio.sleep(self._min_delay - elapsed)
                self._last_call = time.monotonic()

        return self

    async def __aexit__(self, *args: Any) -> None:
        """Release semaphore."""
        self._semaphore.release()


async def retry_async(
    func: Callable[..., Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """
    Retry an async function with exponential backoff.

    Args:
        func: Async function to retry.
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds.
        max_delay: Maximum delay in seconds.
        exponential: Whether to use exponential backoff.
        exceptions: Tuple of exceptions to catch and retry.

    Returns:
        Result of the function call.

    Raises:
        The last exception if all retries fail.

    Example:
        async def api_call():
            return await client.request()

        result = await retry_async(api_call, max_retries=3)
    """
    last_exception: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e

            # Don't wait after the last attempt
            if attempt == max_retries:
                break

            # Calculate delay
            if exponential:
                delay = min(base_delay * (2**attempt), max_delay)
            else:
                delay = base_delay

            await asyncio.sleep(delay)

    # All retries failed
    if last_exception:
        raise last_exception

    raise RuntimeError("retry_async failed without exception")


def async_timeout(seconds: float) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Decorator to add timeout to async functions.

    Args:
        seconds: Timeout in seconds.

    Returns:
        Decorated async function.

    Example:
        @async_timeout(30.0)
        async def long_operation():
            await asyncio.sleep(100)
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=seconds,
            )
        return wrapper
    return decorator


async def gather_with_concurrency(
    max_concurrent: int,
    *tasks: Awaitable[T],
) -> list[T]:
    """
    Run multiple async tasks with concurrency limit.

    Similar to asyncio.gather() but limits concurrent execution.

    Args:
        max_concurrent: Maximum number of concurrent tasks.
        *tasks: Async tasks to execute.

    Returns:
        List of results in the same order as tasks.

    Example:
        results = await gather_with_concurrency(
            3,
            fetch_url(url1),
            fetch_url(url2),
            fetch_url(url3),
            fetch_url(url4),
        )
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def run_with_semaphore(task: Awaitable[T]) -> T:
        async with semaphore:
            return await task

    return await asyncio.gather(*[run_with_semaphore(task) for task in tasks])


class AsyncBatchProcessor:
    """
    Process items in batches with concurrency control.

    Useful for processing large lists of items without overwhelming
    the system or API rate limits.

    Example:
        processor = AsyncBatchProcessor(
            batch_size=10,
            max_concurrent=3,
        )

        async def process_item(item):
            return await api_call(item)

        results = await processor.process(items, process_item)
    """

    def __init__(
        self,
        batch_size: int = 10,
        max_concurrent: int = 5,
        min_delay: float = 0.0,
    ) -> None:
        """
        Initialise the batch processor.

        Args:
            batch_size: Number of items per batch.
            max_concurrent: Maximum concurrent operations within a batch.
            min_delay: Minimum delay between batches.
        """
        self._batch_size = batch_size
        self._max_concurrent = max_concurrent
        self._min_delay = min_delay

    async def process(
        self,
        items: list[Any],
        process_func: Callable[[Any], Awaitable[T]],
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> list[T]:
        """
        Process items in batches.

        Args:
            items: List of items to process.
            process_func: Async function to process each item.
            progress_callback: Optional callback(completed, total).

        Returns:
            List of results in the same order as items.

        Example:
            async def process(item):
                return await transform(item)

            results = await processor.process(items, process)
        """
        results: list[T] = []
        total = len(items)

        # Process in batches
        for i in range(0, len(items), self._batch_size):
            batch = items[i : i + self._batch_size]

            # Process batch with concurrency control
            batch_results = await gather_with_concurrency(
                self._max_concurrent,
                *[process_func(item) for item in batch],
            )

            results.extend(batch_results)

            # Report progress
            if progress_callback:
                await progress_callback(len(results), total)

            # Delay between batches
            if self._min_delay > 0 and i + self._batch_size < len(items):
                await asyncio.sleep(self._min_delay)

        return results


class AsyncProgressTracker:
    """
    Track progress of async operations.

    Provides a simple way to track and report progress for
    concurrent async operations.

    Example:
        tracker = AsyncProgressTracker(total=100)

        async def work(item):
            result = await process(item)
            await tracker.update(1)
            return result

        results = await asyncio.gather(*[work(item) for item in items])
        print(f"Progress: {tracker.percentage:.1f}%")
    """

    def __init__(self, total: int) -> None:
        """
        Initialise the progress tracker.

        Args:
            total: Total number of items to process.
        """
        self._total = total
        self._completed = 0
        self._lock = asyncio.Lock()
        self._callbacks: list[Callable[[int, int], Awaitable[None]]] = []

    @property
    def completed(self) -> int:
        """Return number of completed items."""
        return self._completed

    @property
    def total(self) -> int:
        """Return total number of items."""
        return self._total

    @property
    def percentage(self) -> float:
        """Return completion percentage (0-100)."""
        if self._total == 0:
            return 100.0
        return (self._completed / self._total) * 100.0

    async def update(self, count: int = 1) -> None:
        """
        Update progress counter.

        Args:
            count: Number of items completed.
        """
        async with self._lock:
            self._completed += count

            # Call callbacks
            for callback in self._callbacks:
                await callback(self._completed, self._total)

    def add_callback(
        self,
        callback: Callable[[int, int], Awaitable[None]],
    ) -> None:
        """
        Add a progress callback.

        The callback receives (completed, total).

        Args:
            callback: Async callback function.
        """
        self._callbacks.append(callback)

    async def reset(self) -> None:
        """Reset progress counter."""
        async with self._lock:
            self._completed = 0
