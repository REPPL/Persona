# F-066: Multi-Model Persona Generation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-008 |
| **Milestone** | v0.8.0 |
| **Priority** | P1 |
| **Category** | Generation |

## Problem Statement

Different LLMs have different strengths. Some users want to compare outputs across models, combine insights from multiple models, or use ensemble approaches for higher quality results.

## Design Approach

- Specify multiple models for generation
- Support same-provider and cross-provider
- Configure execution strategy per model
- Combine or compare outputs
- Track per-model costs

### CLI Interface

```bash
# Multiple models from same provider
persona generate --from data.csv \
    --model claude-sonnet-4-5-20250929 \
    --model claude-opus-4-5-20251101

# Cross-provider generation
persona generate --from data.csv \
    --model anthropic:claude-sonnet-4-5-20250929 \
    --model openai:gpt-5-20250807 \
    --model google:gemini-3.0-pro
```

### Configuration

```yaml
# experiment.yaml
generation:
  models:
    - provider: anthropic
      model: claude-sonnet-4-5-20250929
      weight: 1.0

    - provider: openai
      model: gpt-5-20250807
      weight: 1.0

  execution:
    mode: parallel  # parallel, sequential, consensus
    timeout: 300
```

## Implementation Tasks

- [ ] Create MultiModelGenerator class
- [ ] Support multiple model specification
- [ ] Implement model list parsing
- [ ] Add per-model configuration
- [ ] Track per-model metrics
- [ ] Store multi-model metadata
- [ ] Update CLI for multi-model input
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Multiple models generate successfully
- [ ] Cross-provider works correctly
- [ ] Per-model tracking accurate
- [ ] Output organised by model
- [ ] Test coverage ≥ 80%

## Dependencies

- F-002: LLM provider abstraction
- F-004: Persona generation pipeline

---

## Related Documentation

- [Milestone v0.8.0](../../milestones/v0.8.0.md)
- [ADR-0002: Multi-Provider Architecture](../../decisions/adrs/ADR-0002-multi-provider-architecture.md)

