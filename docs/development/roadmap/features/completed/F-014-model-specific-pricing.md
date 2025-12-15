# F-014: Model-Specific Pricing

## Overview

| Attribute | Value |
|-----------|-------|
| **Milestone** | v0.1.0 |
| **Priority** | P0 |
| **Category** | Cost |

## Problem Statement

Different LLM models have vastly different pricing structures. Users need accurate cost estimates that reflect the specific model they're using, including input/output token pricing, and any model-specific constraints.

## Design Approach

- YAML-based pricing configuration per model
- Support different input/output token rates
- Include pricing for all supported providers
- Version pricing data for historical accuracy
- Allow user overrides for enterprise/custom pricing

## Implementation Tasks

- [ ] Define pricing YAML schema
- [ ] Create pricing files for OpenAI models
- [ ] Create pricing files for Anthropic models
- [ ] Create pricing files for Google Gemini models
- [ ] Implement pricing lookup by model ID
- [ ] Add pricing validation (positive values, currency)
- [ ] Support user-defined pricing overrides
- [ ] Write unit tests

## Success Criteria

- [ ] All supported models have pricing data
- [ ] Pricing estimates accurate to published rates
- [ ] Easy to update when providers change pricing
- [ ] User overrides work without modifying package
- [ ] Test coverage ≥ 80%

## Pricing Schema

```yaml
# config/pricing/anthropic/claude-3-sonnet.yaml
model_id: claude-3-sonnet-20240229
provider: anthropic
pricing:
  input_per_1m_tokens: 3.00
  output_per_1m_tokens: 15.00
  currency: USD
effective_date: 2024-02-29
```

## Dependencies

- F-007: Cost estimation (uses pricing data)
- F-011: Multi-provider LLM support (model identification)

---

## Related Documentation

- [F-007: Cost Estimation](F-007-cost-estimation.md)
- [ADR-0010: Cost Estimation](../../../../decisions/adrs/ADR-0010-cost-estimation.md)
- [Model Cards](../../../../reference/model-cards.md)

