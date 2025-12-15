# F-071: Multi-Model Cost Estimation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-008 |
| **Milestone** | v0.8.0 |
| **Priority** | P1 |
| **Category** | Cost |

## Problem Statement

When using multiple models, cost estimation becomes complex. Users need accurate projections that account for different model pricing, execution modes, and potential retries.

## Design Approach

- Calculate costs per model
- Factor in execution mode overhead
- Show cost breakdown
- Compare single vs. multi-model costs
- Support budget constraints

### Cost Breakdown

```
💰 Multi-Model Cost Estimation

Configuration:
  Models: claude-sonnet-4-5, gpt-5, gemini-3.0-pro
  Mode: parallel
  Data: 45,000 tokens

Per-Model Estimates:
  ┌────────────────────────────────────────────────┐
  │ Model                 │ Input  │ Output │ Cost │
  ├───────────────────────┼────────┼────────┼──────┤
  │ claude-sonnet-4-5     │ 45K    │ ~8K    │ $0.26│
  │ gpt-5-20250807        │ 45K    │ ~8K    │ $0.69│
  │ gemini-3.0-pro        │ 45K    │ ~8K    │ $0.10│
  └───────────────────────┴────────┴────────┴──────┘

  Subtotal:                                   $1.05

Mode Overhead (consensus):
  - Clustering step:      +$0.05
  - Merge generation:     +$0.08
                                             ──────
Total Estimated Cost:                         $1.18

Comparison:
  Single model (claude-sonnet-4-5): $0.26
  Multi-model overhead: +$0.92 (+354%)

Budget Status: ✓ Within $5.00 limit
```

## Implementation Tasks

- [ ] Extend CostEstimator for multi-model
- [ ] Calculate per-model costs
- [ ] Add execution mode overhead
- [ ] Generate cost breakdown display
- [ ] Add comparison vs. single-model
- [ ] Implement budget constraint checking
- [ ] Update cost confirmation dialog
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Per-model costs accurate
- [ ] Mode overhead calculated
- [ ] Clear cost breakdown
- [ ] Budget checking works
- [ ] Test coverage ≥ 80%

## Dependencies

- F-007: Cost estimation
- F-066: Multi-model persona generation
- F-067: Execution modes

---

## Related Documentation

- [Milestone v0.8.0](../../milestones/v0.8.0.md)
- [F-007: Cost Estimation](F-007-cost-estimation.md)
- [Model Cards](../../../../reference/model-cards.md)

