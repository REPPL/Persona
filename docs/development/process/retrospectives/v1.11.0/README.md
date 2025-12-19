# v1.11.0 Retrospective

**Milestone:** Code Quality & Architecture

**Features:** F-128 through F-135 (8 refactoring features)

---

## What Went Well

### Code Consolidation (F-128)
- Eliminated ~200 lines of duplicated JSON parsing code
- Single source of truth for LLM response parsing
- Consistent error handling across all callers
- Easier to maintain and test

### Type Safety Improvements (F-131)
- TypedDict provides IDE autocompletion
- Static analysis catches type errors early
- Self-documenting code structure
- No runtime overhead

### Test Coverage (F-134)
- Hybrid stages now have 90%+ unit test coverage
- Easier to debug failures with isolated tests
- Confidence in refactoring without breaking functionality
- Clear test structure mirrors code structure

### HTTP Connection Pooling (F-129)
- ~30% reduction in API call latency for batch operations
- Reduced resource consumption
- Consistent timeout handling
- Automatic retry with backoff

---

## What Could Improve

### Refactoring Scope Creep
- Started with 5 features, expanded to 8 during implementation
- Some features could have been smaller, more focused
- Better upfront scoping would reduce mid-milestone changes

### Documentation Lag
- API reference updates happened after implementation
- Would be better to update docs alongside code changes
- Feature specs should link to API docs earlier

### Breaking Changes Communication
- Internal API changes weren't clearly marked
- Plugin authors might be affected by interface changes
- Need changelog entries for internal API changes

---

## Lessons Learned

### 1. Refactoring Requires Test Safety Net
Before changing any code, we ensured existing tests passed. This gave confidence that refactoring didn't break functionality. Lesson: Never refactor without tests.

### 2. TypedDict Has Limitations
Python's TypedDict doesn't support:
- Optional fields elegantly (requires `total=False`)
- Inheritance well
- Runtime validation

For complex structures, Pydantic models may be better. TypedDict is best for simple, fixed structures.

### 3. Connection Pooling Lifecycle is Tricky
Managing HTTP client lifecycle across:
- One-shot CLI commands
- Long-running API server
- Async context managers

Required careful design with explicit cleanup and context managers.

### 4. Deprecated API Migration is Low-Risk, High-Value
Replacing deprecated `asyncio.get_event_loop()` took minimal effort but ensures Python 3.13+ compatibility. Worth prioritising these "boring" improvements.

---

## Decisions Made

### ADR: PipelineStage as Abstract Base Class
**Decision:** Use ABC instead of Protocol for PipelineStage.

**Rationale:** ABC provides better error messages when methods aren't implemented. Protocol is better for duck typing, but stages are explicitly inherited.

### ADR: Separate async_helpers Module
**Decision:** Create dedicated module for async utilities rather than adding to existing modules.

**Rationale:** Keeps utilities discoverable and avoids circular imports between modules that need async bridging.

### ADR: Registry Pattern for Metrics
**Decision:** Use registry pattern instead of factory pattern for quality metrics.

**Rationale:** Registry allows dynamic registration at runtime, enabling plugin-based metrics. Factory requires compile-time knowledge of all metrics.

---

## Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Duplicated code | ~200 lines | 0 lines | -100% |
| Type coverage | 82% | 91% | +9% |
| Stage test coverage | 45% | 91% | +46% |
| Deprecated API calls | 4 | 0 | -100% |
| Average API latency | 1.2s | 0.85s | -29% |

---

## Technical Debt Status

### Resolved This Milestone
- [x] JSON parsing duplication
- [x] Missing stage unit tests
- [x] Deprecated asyncio usage
- [x] Hard-coded metric instantiation
- [x] Per-request HTTP clients

### Remaining Technical Debt
- [ ] Some providers still have verbose error handling
- [ ] Plugin discovery could be more efficient
- [ ] Configuration validation could be stricter

---

## Follow-Up Actions

- [ ] Monitor connection pool metrics in production
- [ ] Add TypedDict to more internal structures
- [ ] Document internal API changes for plugin authors
- [ ] Consider Pydantic migration for complex structures

---

## Related Documentation

- [v1.11.0 Devlog](../../devlogs/v1.11.0/)
- [v1.11.0 Milestone](../../roadmap/milestones/v1.11.0.md)
- [F-128: JSON Parsing](../../roadmap/features/completed/F-128-json-parsing-consolidation.md)
- [F-129: HTTP Pooling](../../roadmap/features/completed/F-129-provider-connection-pooling.md)
- [F-130: Stage Abstraction](../../roadmap/features/completed/F-130-hybrid-stage-abstraction.md)
- [F-131: TypedDict](../../roadmap/features/completed/F-131-persona-typeddict.md)
- [F-132: Event Loop](../../roadmap/features/completed/F-132-event-loop-standardisation.md)
- [F-133: Metric Registry](../../roadmap/features/completed/F-133-metric-registry-integration.md)
- [F-134: Stage Tests](../../roadmap/features/completed/F-134-hybrid-stage-tests.md)
- [F-135: asyncio Migration](../../roadmap/features/completed/F-135-asyncio-migration.md)

