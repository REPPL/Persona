# F-078: Cost Tracking Post-Generation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-007 |
| **Milestone** | v0.9.0 |
| **Priority** | P1 |
| **Category** | Logging |

## Problem Statement

While F-007 provides cost estimation before generation, users need accurate post-generation cost tracking for budgeting, billing, and analysis.

## Design Approach

- Calculate actual costs after generation
- Compare to estimates
- Track cumulative costs
- Support budget alerts
- Generate cost reports

### Cost Tracking Data

```json
{
  "costs": {
    "estimated_before": 0.45,
    "actual": 0.42,
    "variance": -0.03,
    "variance_percent": -6.7,
    "breakdown": {
      "persona_generation": 0.38,
      "summary_generation": 0.04
    },
    "by_model": {
      "claude-sonnet-4-5-20250929": 0.42
    }
  }
}
```

### Budget Tracking

```yaml
# ~/.persona/config.yaml
budgets:
  daily: 10.00
  weekly: 50.00
  monthly: 150.00
  alerts:
    - threshold: 0.8  # 80% of budget
      action: warn
    - threshold: 1.0  # 100% of budget
      action: block
```

### Cost Report

```
💰 Cost Report

This Run:
  Estimated: $0.45
  Actual:    $0.42 (-6.7%)

Experiment Total (5 runs):
  Total cost: $2.15
  Average per run: $0.43

Budget Status (Monthly):
  Used: $45.20 / $150.00 (30.1%)
  Remaining: $104.80

  ████████░░░░░░░░░░░░░░░░░░░░░░ 30%
```

## Implementation Tasks

- [ ] Create CostTracker class
- [ ] Calculate actual costs post-run
- [ ] Compare to estimates
- [ ] Implement cumulative tracking
- [ ] Add budget configuration
- [ ] Implement budget alerts
- [ ] Generate cost reports
- [ ] Add `persona costs` command
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Actual costs calculated accurately
- [ ] Variance from estimates tracked
- [ ] Budget alerts work correctly
- [ ] Reports generated correctly
- [ ] Test coverage ≥ 80%

## Dependencies

- F-007: Cost estimation
- F-077: Token usage logging

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [F-007: Cost Estimation](F-007-cost-estimation.md)
- [ADR-0010: Cost Estimation](../../../decisions/adrs/ADR-0010-cost-estimation.md)
