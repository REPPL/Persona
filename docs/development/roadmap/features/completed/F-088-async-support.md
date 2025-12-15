# F-088: Async Support

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-007 |
| **Milestone** | v1.1.0 |
| **Priority** | P1 |
| **Category** | Core |
| **Status** | Completed |

## Problem Statement

LLM API calls are I/O-bound operations that can take seconds to complete. Synchronous-only APIs block the event loop, preventing efficient batch processing and integration with async applications (FastAPI, etc.).

## Design Approach

- Async versions of all core methods
- Use httpx.AsyncClient for HTTP
- Support parallel generation
- Progress callbacks for async operations
- Concurrency utilities for rate limiting

### Async Interface

```python
import asyncio
from persona.core.generation import GenerationPipeline, GenerationConfig

async def generate_personas():
    pipeline = GenerationPipeline()

    # Single async generation
    config = GenerationConfig(
        data_path="./interviews.csv",
        count=3,
        provider="anthropic",
    )
    result = await pipeline.generate_async(config)

    # Parallel batch generation
    configs = [config1, config2, config3]
    results = await pipeline.generate_batch_async(
        configs,
        max_concurrent=2,
    )

asyncio.run(generate_personas())
```

## Implementation Tasks

- [x] Create async utilities module with concurrency control
- [x] Add async methods to provider base class
- [x] Implement async support in OpenAI provider
- [x] Implement async support in Anthropic provider
- [x] Implement async support in Gemini provider
- [x] Add async data loading methods
- [x] Create async generation pipeline
- [x] Write async unit tests for utilities
- [x] Write async unit tests for providers
- [x] Add async dependency (aiofiles)

## Success Criteria

- [x] All providers have async methods
- [x] Async generation pipeline implemented
- [x] Data loading supports async
- [x] Concurrency utilities available
- [x] Test coverage ≥ 80%
- [x] Backward compatible with sync code

## Implementation Notes

### Architecture

The async implementation follows these patterns:

1. **Provider Layer**: Each provider has `generate_async()` method using `httpx.AsyncClient`
2. **Pipeline Layer**: `GenerationPipeline.generate_async()` orchestrates async operations
3. **Data Layer**: `DataLoader.load_path_async()` loads files concurrently
4. **SDK Layer**: `AsyncPersonaGenerator` already existed, now uses native async methods

### Concurrency Utilities

Created `persona.core.async_utils` with:
- `AsyncRateLimiter`: Semaphore-based rate limiting
- `retry_async`: Exponential backoff retry logic
- `async_timeout`: Timeout decorator
- `gather_with_concurrency`: Concurrent task execution with limits
- `AsyncBatchProcessor`: Batch processing with progress tracking
- `AsyncProgressTracker`: Progress monitoring

### Backward Compatibility

All async methods are additions - existing sync methods remain unchanged. The base provider class provides a fallback async implementation that runs sync methods in a thread pool.

### Files Modified

- `src/persona/core/async_utils.py` (new)
- `src/persona/core/providers/base.py`
- `src/persona/core/providers/openai.py`
- `src/persona/core/providers/anthropic.py`
- `src/persona/core/providers/gemini.py`
- `src/persona/core/data/loader.py`
- `src/persona/core/generation/pipeline.py`
- `pyproject.toml`

### Tests Added

- `tests/unit/core/test_async_utils.py` (15 tests)
- `tests/unit/core/providers/test_async_providers.py` (9 tests)

## Dependencies

- aiofiles ≥ 24.1.0 (optional)

---

## Related Documentation

- [Milestone v1.1.0](../../milestones/v1.1.0.md)
- [API Reference](../../../../reference/api.md)

---

**Status**: Completed
