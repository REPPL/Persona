"""
Async helper utilities for standardised event loop management.

This module provides utilities for properly managing async/sync
boundaries, avoiding deprecated asyncio APIs.

Example:
    from persona.core.utils.async_helpers import run_sync

    # Call async function from sync context
    result = run_sync(async_function, arg1, arg2)
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


def run_sync(
    coro_func: Callable[..., Awaitable[T]],
    *args,
    **kwargs,
) -> T:
    """
    Run an async function synchronously.

    This is the preferred way to call async functions from sync contexts.
    It properly handles event loop management without using deprecated APIs.

    Args:
        coro_func: Async function to call.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        The result of the async function.

    Raises:
        RuntimeError: If called from within an async context.

    Example:
        async def fetch_data(url: str) -> dict:
            ...

        # From sync context
        result = run_sync(fetch_data, "https://example.com")
    """
    # Check if we're already in an async context
    try:
        asyncio.get_running_loop()
        raise RuntimeError(
            "Cannot call run_sync() from async context. "
            "Use 'await coro_func(...)' instead."
        )
    except RuntimeError as e:
        # If the error is about no running loop, that's what we want
        if "no running event loop" not in str(e).lower():
            raise

    # Create coroutine and run it
    coro = coro_func(*args, **kwargs)
    return asyncio.run(coro)


def is_async_context() -> bool:
    """
    Check if currently running in an async context.

    Returns:
        True if there's a running event loop.

    Example:
        if is_async_context():
            result = await async_func()
        else:
            result = run_sync(async_func)
    """
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


async def to_thread(func: Callable[..., T], *args, **kwargs) -> T:
    """
    Run a blocking function in a thread pool.

    This is the modern replacement for loop.run_in_executor().
    Available in Python 3.9+.

    Args:
        func: Blocking function to run.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.

    Returns:
        The result of the function.

    Example:
        async def main():
            # Run blocking IO in thread pool
            result = await to_thread(blocking_io_function, arg1)
    """
    # Use asyncio.to_thread if available (Python 3.9+)
    # Fall back to run_in_executor for compatibility
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: func(*args, **kwargs),
    )
