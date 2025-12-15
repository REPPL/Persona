# F-017: Single-Step Workflow

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v0.1.0 |
| **Priority** | P1 |
| **Category** | Workflow |

## Problem Statement

The v0.1.0 release requires a working persona generation pipeline. Before implementing multi-step workflows (v0.2.0), a single-step workflow provides the foundation: load data → send to LLM → produce personas.

## Design Approach

- Single LLM call per generation
- All data sent in one prompt
- Direct mapping to output
- Foundation for future multi-step architecture
- Clear extension points for workflow complexity

## Implementation Tasks

- [ ] Define single-step workflow interface
- [ ] Implement data aggregation for single prompt
- [ ] Create generation orchestrator
- [ ] Handle response parsing
- [ ] Map output to persona structure
- [ ] Add error handling for LLM failures
- [ ] Implement retry logic
- [ ] Write integration tests

## Success Criteria

- [ ] End-to-end generation works
- [ ] Reasonable data sizes processed successfully
- [ ] LLM errors handled gracefully
- [ ] Output matches expected schema
- [ ] Architecture supports future multi-step extension
- [ ] Test coverage ≥ 80%

## Workflow Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Load Data  │ ──▶ │  LLM Call    │ ──▶ │  Output     │
│  (F-001)    │     │  (F-002)     │     │  (F-005)    │
└─────────────┘     └──────────────┘     └─────────────┘
```

## Limitations (Addressed in v0.2.0)

- No intermediate processing steps
- No parallel persona generation
- Single LLM call may hit context limits
- No iterative refinement

## Dependencies

- F-001: Data loading
- F-002: LLM provider abstraction
- F-004: Persona generation pipeline
- F-005: Output formatting

---

## Related Documentation

- [F-004: Persona Generation Pipeline](F-004-persona-generation.md)
- [ADR-0011: Multi-Step Workflow](../../../../decisions/adrs/ADR-0011-multi-step-workflow.md)
- [v0.2.0 Milestone](../../milestones/v0.2.0.md) (multi-step workflows)

