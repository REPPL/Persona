# ADR-0011: Multi-Step Workflow Orchestration

## Status

Accepted

## Context

Complex persona generation benefits from:
- Separation of concerns (extract, consolidate, validate)
- Intermediate inspection points
- Per-step model optimisation
- Research transparency

## Decision

Support multi-step workflows (v0.2.0):
- Each step defined separately
- Output chaining between steps
- Intermediate results saved
- Per-step model selection

## Consequences

**Positive:**
- Research-grade transparency
- Debugging intermediate steps
- Optimised model selection
- Alignment with Shin et al. methodology

**Negative:**
- More complex implementation
- Higher total costs (multiple calls)
- Longer execution time

---

## Related Documentation

- [v0.2.0 Milestone](../../roadmap/milestones/v0.2.0.md)
