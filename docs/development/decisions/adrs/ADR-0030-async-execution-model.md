# ADR-0030: Async Execution Model

## Status

Planned

## Context

Persona v1.0.0 introduced async generation (F-088) but the async execution model was not formally documented. As the application grows with more concurrent operations (batch processing, parallel provider calls, background tasks), a clear async architecture is needed.

Key concerns:
- Event loop management across CLI, API, and library contexts
- Proper resource cleanup (connections, file handles)
- Cancellation handling for long-running operations
- Concurrency limits to prevent resource exhaustion
- Debugging async code paths

## Decision

Adopt a **structured concurrency model** with explicit lifecycle management for all async operations.

### Core Principles

1. **Single Event Loop Ownership** - One owner creates and manages the event loop
2. **Structured Lifetimes** - All tasks have explicit parent-child relationships
3. **Graceful Cancellation** - All operations support cancellation with cleanup
4. **Bounded Concurrency** - Semaphores prevent resource exhaustion

### Event Loop Management

```python
class AsyncRuntime:
    """Manages the async runtime for Persona."""

    _instance: ClassVar["AsyncRuntime | None"] = None
    _loop: asyncio.AbstractEventLoop | None = None

    @classmethod
    def get(cls) -> "AsyncRuntime":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def run(self, coro: Coroutine[Any, Any, T]) -> T:
        """Run a coroutine in the managed event loop."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)

        try:
            return self._loop.run_until_complete(coro)
        finally:
            self._cleanup_pending_tasks()

    def _cleanup_pending_tasks(self) -> None:
        """Cancel and cleanup any pending tasks."""
        pending = asyncio.all_tasks(self._loop)
        for task in pending:
            task.cancel()
        self._loop.run_until_complete(
            asyncio.gather(*pending, return_exceptions=True)
        )
```

### Task Groups (Structured Concurrency)

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def task_group(name: str):
    """Create a task group with automatic cleanup."""
    tasks: list[asyncio.Task] = []

    class TaskGroup:
        def create_task(self, coro: Coroutine) -> asyncio.Task:
            task = asyncio.create_task(coro)
            tasks.append(task)
            return task

    try:
        yield TaskGroup()
        # Wait for all tasks
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        # Cancel all tasks on cancellation
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
    except Exception:
        # Cancel remaining on error
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
```

### Concurrency Control

```python
class ConcurrencyController:
    """Control concurrent operations with semaphores."""

    def __init__(self, limits: dict[str, int]):
        self.semaphores = {
            name: asyncio.Semaphore(limit)
            for name, limit in limits.items()
        }

    @asynccontextmanager
    async def acquire(self, resource: str):
        """Acquire a slot for the named resource."""
        semaphore = self.semaphores.get(resource)
        if semaphore is None:
            yield
            return

        async with semaphore:
            yield

# Usage
controller = ConcurrencyController({
    "api_calls": 10,
    "file_operations": 5,
    "provider_anthropic": 5,
    "provider_openai": 10,
})

async def generate_persona(data: str) -> Persona:
    async with controller.acquire("api_calls"):
        async with controller.acquire("provider_anthropic"):
            return await provider.generate(data)
```

### Cancellation Handling

```python
class CancellableOperation:
    """Base class for operations that support cancellation."""

    def __init__(self):
        self._cancelled = False
        self._cleanup_handlers: list[Callable] = []

    def cancel(self) -> None:
        self._cancelled = True

    def on_cleanup(self, handler: Callable) -> None:
        self._cleanup_handlers.append(handler)

    async def run(self) -> T:
        try:
            return await self._execute()
        except asyncio.CancelledError:
            await self._cleanup()
            raise
        finally:
            await self._cleanup()

    async def _cleanup(self) -> None:
        for handler in self._cleanup_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception:
                pass  # Log but don't raise during cleanup
```

### Context Propagation

```python
from contextvars import ContextVar

# Context variables for async operations
current_experiment: ContextVar[str | None] = ContextVar("experiment", default=None)
current_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)

def with_context(**kwargs):
    """Decorator to set context for async operation."""
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kw):
            tokens = []
            for key, value in kwargs.items():
                var = globals().get(f"current_{key}")
                if var:
                    tokens.append((var, var.set(value)))
            try:
                return await fn(*args, **kw)
            finally:
                for var, token in tokens:
                    var.reset(token)
        return wrapper
    return decorator
```

## Consequences

**Positive:**
- Clear ownership model for event loops
- Automatic cleanup of resources
- Bounded concurrency prevents exhaustion
- Cancellation propagates correctly
- Context available in async operations

**Negative:**
- Requires discipline to use task groups
- Additional complexity vs fire-and-forget
- Context propagation has overhead

## Alternatives Considered

### asyncio.run() Everywhere

**Description:** Use `asyncio.run()` at each entry point.

**Pros:** Simple, standard.

**Cons:** Creates/destroys event loop repeatedly, can't share state.

**Why Not Chosen:** Inefficient for CLI with multiple commands.

### Trio Instead of asyncio

**Description:** Use Trio for structured concurrency.

**Pros:** Better cancellation, stricter model.

**Cons:** Not in standard library, ecosystem compatibility.

**Why Not Chosen:** asyncio is standard, Trio adds dependency.

### Global Event Loop

**Description:** Single global event loop.

**Pros:** Simple access, shared state.

**Cons:** Hard to test, cleanup issues, thread safety.

**Why Not Chosen:** Runtime management is more explicit.

## Research Reference

See [R-025: Batch Processing Optimisation](../../research/R-025-batch-processing-optimisation.md) for concurrent processing patterns.

---

## Related Documentation

- [R-025: Batch Processing Optimisation](../../research/R-025-batch-processing-optimisation.md)
- [F-088: Async Generation](../../roadmap/features/completed/F-088-async-generation.md)
- [ADR-0029: Error Handling Strategy](ADR-0029-error-handling-strategy.md)

---

**Status**: Planned
