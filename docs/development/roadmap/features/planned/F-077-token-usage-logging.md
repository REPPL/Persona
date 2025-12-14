# F-077: Token Usage Logging

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-007 |
| **Milestone** | v0.9.0 |
| **Priority** | P1 |
| **Category** | Logging |

## Problem Statement

Detailed token usage logs enable cost analysis, optimisation, and debugging. Users need to understand where tokens are consumed across the generation process.

## Design Approach

- Log token usage per LLM call
- Track by workflow step
- Aggregate across runs
- Export for analysis
- Integrate with cost tracking

### Token Log Format

```json
{
  "timestamp": "2025-12-14T10:30:15Z",
  "event": "llm_call",
  "run_id": "run-def456",
  "step": "persona_generation",
  "model": "claude-sonnet-4-5-20250929",
  "tokens": {
    "input": 42000,
    "output": 7500,
    "total": 49500
  },
  "prompt_breakdown": {
    "system": 2100,
    "data": 38000,
    "instructions": 1900
  },
  "cost_usd": 0.24
}
```

### Aggregation Report

```
Token Usage Report
══════════════════════════════════════════

By Step:
  ┌─────────────────────────┬────────┬────────┬───────┐
  │ Step                    │ Input  │ Output │ Cost  │
  ├─────────────────────────┼────────┼────────┼───────┤
  │ Data processing         │ 0      │ 0      │ $0.00 │
  │ Persona generation      │ 42,000 │ 7,500  │ $0.24 │
  │ Summary generation      │ 3,200  │ 1,250  │ $0.02 │
  └─────────────────────────┴────────┴────────┴───────┘
  Total:                      45,200   8,750    $0.26

By Prompt Component:
  System prompt:     2,100 tokens (4.6%)
  Data context:     38,000 tokens (84.1%)
  Instructions:      1,900 tokens (4.2%)
  Output:            8,750 tokens (19.4%)

Efficiency Metrics:
  Output/Input ratio: 19.4%
  Cost per persona: $0.09
```

## Implementation Tasks

- [ ] Create TokenUsageLogger class
- [ ] Log per-call token usage
- [ ] Track prompt breakdown
- [ ] Implement aggregation
- [ ] Generate usage reports
- [ ] Add CSV export
- [ ] Integrate with F-063
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All LLM calls logged
- [ ] Breakdown by component
- [ ] Aggregation accurate
- [ ] Reports generated correctly
- [ ] Test coverage ≥ 80%

## Dependencies

- F-063: Token count tracking
- F-073: Experiment logger

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [F-063: Token Count Tracking](F-063-token-count-tracking.md)

