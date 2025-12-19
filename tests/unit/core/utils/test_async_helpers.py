"""
Tests for async helper utilities (F-132, F-135).
"""

import asyncio

import pytest

from persona.core.utils.async_helpers import is_async_context, run_sync, to_thread


class TestRunSync:
    """Tests for run_sync utility."""

    def test_runs_async_function_from_sync_context(self):
        """Test running async function from sync context."""

        async def async_add(a: int, b: int) -> int:
            return a + b

        result = run_sync(async_add, 2, 3)
        assert result == 5

    def test_runs_async_function_with_kwargs(self):
        """Test running async function with keyword arguments."""

        async def async_greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        result = run_sync(async_greet, "World", greeting="Hi")
        assert result == "Hi, World!"

    def test_raises_in_async_context(self):
        """Test that run_sync raises when called from async context."""

        async def async_func() -> int:
            return 42

        async def test_wrapper():
            with pytest.raises(RuntimeError, match="Cannot call run_sync"):
                run_sync(async_func)

        asyncio.run(test_wrapper())

    def test_propagates_exceptions(self):
        """Test that exceptions from async function are propagated."""

        async def async_error():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            run_sync(async_error)

    def test_with_awaited_result(self):
        """Test with async function that awaits other coroutines."""

        async def inner() -> int:
            await asyncio.sleep(0.01)
            return 10

        async def outer() -> int:
            value = await inner()
            return value * 2

        result = run_sync(outer)
        assert result == 20


class TestIsAsyncContext:
    """Tests for is_async_context utility."""

    def test_returns_false_in_sync_context(self):
        """Test that is_async_context returns False in sync context."""
        assert is_async_context() is False

    def test_returns_true_in_async_context(self):
        """Test that is_async_context returns True in async context."""

        async def check():
            return is_async_context()

        result = asyncio.run(check())
        assert result is True


class TestToThread:
    """Tests for to_thread utility."""

    @pytest.mark.asyncio
    async def test_runs_blocking_function(self):
        """Test running blocking function in thread pool."""

        def blocking_add(a: int, b: int) -> int:
            return a + b

        result = await to_thread(blocking_add, 5, 7)
        assert result == 12

    @pytest.mark.asyncio
    async def test_runs_with_kwargs(self):
        """Test running blocking function with keyword arguments."""

        def blocking_greet(name: str, prefix: str = "Hello") -> str:
            return f"{prefix}, {name}!"

        result = await to_thread(blocking_greet, "Test", prefix="Hi")
        assert result == "Hi, Test!"

    @pytest.mark.asyncio
    async def test_propagates_exceptions(self):
        """Test that exceptions from blocking function are propagated."""

        def blocking_error():
            raise ValueError("Blocking error")

        with pytest.raises(ValueError, match="Blocking error"):
            await to_thread(blocking_error)

    @pytest.mark.asyncio
    async def test_allows_concurrent_execution(self):
        """Test that multiple calls can run concurrently."""
        import time

        def slow_function(value: int) -> int:
            time.sleep(0.05)
            return value * 2

        start = time.monotonic()
        results = await asyncio.gather(
            to_thread(slow_function, 1),
            to_thread(slow_function, 2),
            to_thread(slow_function, 3),
        )
        elapsed = time.monotonic() - start

        assert results == [2, 4, 6]
        # Should complete faster than sequential execution (0.15s)
        # Allow some buffer for overhead
        assert elapsed < 0.12


class TestImports:
    """Tests for module imports."""

    def test_can_import_from_utils(self):
        """Test that helpers are exported from utils package."""
        from persona.core.utils import is_async_context, run_sync, to_thread

        assert run_sync is not None
        assert is_async_context is not None
        assert to_thread is not None
