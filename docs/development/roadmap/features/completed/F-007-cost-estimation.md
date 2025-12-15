# F-007: Cost Estimation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v0.1.0 |
| **Priority** | P1 |
| **Category** | Cost |

## Problem Statement

Users need to understand cost implications before running generation, especially when processing large datasets.

## Design Approach

- Token counting for input data
- Model pricing database (YAML)
- Pre-generation cost estimate display
- Post-generation actual cost recording

## Implementation Tasks

- [ ] Create CostEstimator class
- [ ] Implement token counting (tiktoken)
- [ ] Add model pricing config (YAML)
- [ ] Display cost estimate before generation
- [ ] Track actual costs post-generation
- [ ] Add to metadata.json
- [ ] Write unit tests

## Success Criteria

- [ ] Accurate token count (within 5%)
- [ ] Cost estimate shown before generation
- [ ] Actual cost recorded in metadata
- [ ] Support for all three providers' pricing
- [ ] Test coverage ≥ 80%

## Pricing Configuration

```yaml
# config/models/openai/gpt-4.yaml
pricing:
  input_per_1k: 0.03
  output_per_1k: 0.06
  currency: USD
```

---

## Related Documentation

- [UC-001: Generate Personas](../../../../use-cases/briefs/UC-001-generate-personas.md)
- [ADR-0010: Cost Estimation](../../../../decisions/adrs/ADR-0010-cost-estimation.md)
