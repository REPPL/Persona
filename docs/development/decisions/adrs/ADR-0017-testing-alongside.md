# ADR-0017: Testing Alongside Implementation

## Status

Accepted

## Context

Testing can be:
- Deferred to later phases
- Written alongside implementation
- Test-driven (TDD)

## Decision

Test alongside implementation:
- Tests written with each feature
- Not deferred to later phases
- Minimum 80% coverage target
- Integration tests for workflows

## Consequences

**Positive:**
- Bugs caught early
- Confidence in changes
- Regression protection
- Documentation through tests

**Negative:**
- Slower initial development
- Test maintenance burden
- Coverage requirements

---

## Related Documentation

- [Implementation Workflow](../../process/workflow.md)
- [PersonaZero Analysis](../../lineage/personazero-analysis.md)
