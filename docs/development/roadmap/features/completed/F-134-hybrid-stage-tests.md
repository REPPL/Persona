# F-134: Hybrid Stage Unit Tests

**Milestone:** v1.11.0 - Code Quality & Architecture

**Category:** Testing

**Priority:** High

---

## Problem Statement

Hybrid pipeline stages are only tested indirectly through integration tests:
- `src/persona/core/hybrid/stages/draft.py` - No dedicated test file
- `src/persona/core/hybrid/stages/filter.py` - No dedicated test file
- `src/persona/core/hybrid/stages/refine.py` - No dedicated test file

These modules contain complex logic:
- Batch processing
- Evaluation scoring
- Budget tracking
- Error handling

---

## Solution

Create dedicated unit tests for each stage with mocked dependencies.

---

## Implementation Tasks

- [ ] Create `tests/unit/core/hybrid/stages/__init__.py`
- [ ] Create `tests/unit/core/hybrid/stages/test_draft.py`
- [ ] Create `tests/unit/core/hybrid/stages/test_filter.py`
- [ ] Create `tests/unit/core/hybrid/stages/test_refine.py`
- [ ] Mock ProviderFactory, CostTracker, PersonaJudge
- [ ] Test error handling scenarios
- [ ] Test batch processing edge cases
- [ ] Achieve 85%+ coverage on stages

---

## Test Coverage Requirements

### Draft Stage
- [ ] Basic persona generation
- [ ] Batch size handling
- [ ] Provider error recovery
- [ ] JSON parsing failures
- [ ] Empty input handling

### Filter Stage
- [ ] Quality threshold filtering
- [ ] Evaluation scoring integration
- [ ] Pass/fail persona separation
- [ ] Edge cases (all pass, all fail)

### Refine Stage
- [ ] Budget tracking
- [ ] Refinement quality improvement
- [ ] Max iterations limit
- [ ] Cost overflow protection

---

## Success Criteria

- [ ] Each stage has dedicated test file
- [ ] Coverage ≥ 85% on hybrid stages
- [ ] All edge cases documented and tested
- [ ] No regression in existing tests

---

## Dependencies

- F-130 (Hybrid Stage Abstraction) - tests should target new interface

---

## Related Documentation

- [v1.11.0 Milestone](../../milestones/v1.11.0.md)
- [F-116 Hybrid Pipeline](../completed/F-116-hybrid-local-frontier-pipeline.md)

---

**Status**: Planned
