# F-088: Async Support

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-007 |
| **Milestone** | v0.5.0 |
| **Priority** | P1 |
| **Category** | SDK |

## Problem Statement

LLM API calls are I/O-bound operations that can take seconds to complete. Synchronous-only APIs block the event loop, preventing efficient batch processing and integration with async applications (FastAPI, etc.).

## Design Approach

- Async versions of all SDK methods
- Use httpx for async HTTP
- Support parallel generation
- Progress callbacks for async operations
- Graceful cancellation

### Async Interface

```python
import asyncio
from persona import AsyncPersonaGenerator, Experiment

async def generate_personas():
    exp = await Experiment.acreate(name="my-experiment", ...)

    generator = AsyncPersonaGenerator(experiment=exp)

    # Single generation
    result = await generator.agenerate(config)

    # Parallel generation (multiple experiments)
    tasks = [
        generator.agenerate(config1),
        generator.agenerate(config2),
        generator.agenerate(config3),
    ]
    results = await asyncio.gather(*tasks)

    # With progress callback
    async def on_progress(step, total):
        print(f"Progress: {step}/{total}")

    result = await generator.agenerate(
        config,
        progress_callback=on_progress
    )

asyncio.run(generate_personas())
```

## Implementation Tasks

- [ ] Create async variants of SDK classes
- [ ] Use httpx.AsyncClient for HTTP
- [ ] Implement parallel generation
- [ ] Add progress callback support
- [ ] Implement cancellation tokens
- [ ] Add timeout handling
- [ ] Write async unit tests
- [ ] Write async integration tests
- [ ] Update SDK tutorial with async examples

## Success Criteria

- [ ] All SDK methods have async variants
- [ ] Parallel generation works correctly
- [ ] Progress callbacks fire correctly
- [ ] Cancellation works cleanly
- [ ] Test coverage ≥ 90%

## Dependencies

- F-087: Python SDK

---

## Related Documentation

- [Milestone v0.5.0](../../milestones/v0.5.0.md)
- [F-087: Python SDK](F-087-python-sdk.md)

