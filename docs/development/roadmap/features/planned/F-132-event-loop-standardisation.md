# F-132: Event Loop Management Standardisation

**Milestone:** v1.11.0 - Code Quality & Architecture

**Category:** Async

**Priority:** Medium

---

## Problem Statement

Inconsistent async/sync patterns across modules:
- Different sync wrapper implementations
- Bug in `HybridPipeline.generate_sync()` returns Task, not result
- Mixing deprecated `asyncio.get_event_loop()` with modern patterns
- Duplicate code between `generate()` and `generate_async()` methods

Affected files:
- `src/persona/core/generation/pipeline.py` (lines 231-304)
- `src/persona/core/hybrid/pipeline.py` (lines 216-247)

---

## Solution

Standardise on async-first with proper sync wrappers:

```python
def generate_sync(self, *args, **kwargs) -> list[Persona]:
    """Synchronous wrapper for async generation."""
    try:
        loop = asyncio.get_running_loop()
        raise RuntimeError(
            "Cannot call generate_sync() from async context. "
            "Use await generate() instead."
        )
    except RuntimeError:
        return asyncio.run(self.generate(*args, **kwargs))
```

---

## Implementation Tasks

- [ ] Audit all sync/async wrapper implementations
- [ ] Create `src/persona/core/utils/async_helpers.py`
- [ ] Implement `run_sync()` utility with proper detection
- [ ] Fix bug in HybridPipeline.generate_sync() (returns Task, not result)
- [ ] Update all pipelines to use consistent pattern
- [ ] Document async usage patterns
- [ ] Replace deprecated `asyncio.get_event_loop()` calls

---

## Success Criteria

- [ ] All sync wrappers use consistent pattern
- [ ] Bug in HybridPipeline.generate_sync() fixed
- [ ] Clear error messages when mixing sync/async incorrectly
- [ ] Documentation explains when to use each pattern

---

## Dependencies

None

---

## Related Documentation

- [v1.11.0 Milestone](../../milestones/v1.11.0.md)
- [F-088 Async Support](../completed/F-088-async-support.md)

---

**Status**: Planned
