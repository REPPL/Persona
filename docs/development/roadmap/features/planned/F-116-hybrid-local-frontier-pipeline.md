# F-116: Hybrid Local/Frontier Pipeline

## Overview

| Attribute | Value |
|-----------|-------|
| **Research** | R-013 |
| **Milestone** | v1.5.0 |
| **Priority** | P3 |
| **Category** | Optimisation |

## Problem Statement

Users face a trade-off between cost, privacy, and quality:

| Approach | Cost | Privacy | Quality |
|----------|------|---------|---------|
| **Frontier Only** | High ($0.15-0.50/persona) | Low (data sent to cloud) | Excellent (95%+) |
| **Local Only** | Free | High (data stays local) | Good (85-90% for 70B) |

Neither extreme is optimal for many use cases. A hybrid approach can achieve:
- **90%+ quality** of frontier models
- **50%+ cost reduction** vs frontier-only
- **Privacy protection** for sensitive input data

## Design Approach

- Orchestrate local and frontier models in a pipeline
- Generate drafts locally, refine best candidates with frontier
- Use local LLM-as-judge for quality filtering
- Cost-aware routing based on budget constraints
- Configurable quality/cost trade-offs

### Hybrid Pipeline Architecture

```
Input Data → PII Anonymisation → Local Draft Generation → Local Quality Filter
                                         ↓                        ↓
                                    N×2 Drafts              Top N Candidates
                                                                  ↓
                                                    [Optional] Frontier Refinement
                                                                  ↓
                                                          Final Personas
```

### Python API

```python
from persona.core.hybrid import HybridPipeline, HybridConfig

# Create hybrid pipeline
pipeline = HybridPipeline(
    local_provider="ollama",
    local_model="qwen2.5:72b",
    frontier_provider="anthropic",
    frontier_model="claude-sonnet-4-5-20250929"
)

# Generate with hybrid approach
result = pipeline.generate(
    data_path="research.csv",
    count=5,
    config=HybridConfig(
        draft_multiplier=2,      # Generate 2x candidates locally
        quality_threshold=0.75,  # Minimum quality for frontier refinement
        use_frontier=True,       # Enable frontier refinement
        max_frontier_cost=5.00,  # Budget cap in USD
    )
)

# Local-only mode (privacy-first)
result = pipeline.generate(
    data_path="sensitive.csv",
    count=5,
    config=HybridConfig(use_frontier=False)
)

# Cost-optimised mode
result = pipeline.generate(
    data_path="research.csv",
    count=100,
    config=HybridConfig(
        draft_multiplier=3,
        quality_threshold=0.85,  # Only refine best candidates
        max_frontier_cost=10.00, # Strict budget
    )
)
```

### CLI Integration

```bash
# Generate with hybrid pipeline (default settings)
persona generate --input research.csv --hybrid

# Local drafts, frontier refinement
persona generate --input research.csv --hybrid --local-model qwen2.5:72b --frontier anthropic

# Privacy mode (local only, no frontier)
persona generate --input sensitive.csv --hybrid --no-frontier

# Budget-constrained
persona generate --input research.csv --hybrid --max-cost 5.00

# Quality-focused (more drafts, stricter filtering)
persona generate --input research.csv --hybrid --draft-multiplier 3 --quality-threshold 0.85
```

### Pipeline Stages

#### Stage 1: Data Preparation
- Load input data
- Optionally anonymise PII (if `--anonymise` flag)
- Prepare prompt templates

#### Stage 2: Local Draft Generation
- Generate `count × draft_multiplier` draft personas
- Use local model (Ollama)
- Fast, cost-free generation

#### Stage 3: Quality Filtering
- Evaluate all drafts with local LLM-as-judge
- Score on coherence, realism, usefulness
- Select top `count` candidates above threshold

#### Stage 4: Frontier Refinement (Optional)
- Send top candidates to frontier model
- Request enhancement and polish
- Respect budget constraints

#### Stage 5: Final Output
- Combine refined personas
- Calculate total cost
- Report quality metrics

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `draft_multiplier` | int | 2 | Drafts per final persona |
| `quality_threshold` | float | 0.75 | Minimum quality for refinement |
| `use_frontier` | bool | True | Enable frontier refinement |
| `max_frontier_cost` | float | None | Budget cap (USD) |
| `local_provider` | str | "ollama" | Local model provider |
| `local_model` | str | auto | Local model (auto-detect) |
| `frontier_provider` | str | "anthropic" | Frontier provider |
| `frontier_model` | str | default | Frontier model |

### Cost Estimation

```python
# Estimate cost before generation
estimate = pipeline.estimate_cost(
    data_path="research.csv",
    count=10,
    config=HybridConfig(
        draft_multiplier=2,
        quality_threshold=0.75,
    )
)
# CostEstimate(
#     local_cost=0.00,
#     frontier_cost=1.50,  # Estimated based on typical refinement
#     total_cost=1.50,
#     frontier_calls=10,
# )
```

## Implementation Tasks

- [ ] Create `src/persona/core/hybrid/__init__.py`
- [ ] Create `src/persona/core/hybrid/pipeline.py` with `HybridPipeline`
- [ ] Create `src/persona/core/hybrid/config.py` with `HybridConfig`
- [ ] Implement draft generation stage
- [ ] Implement quality filtering stage
- [ ] Implement frontier refinement stage
- [ ] Integrate with F-107 (Ollama), F-108 (PII), F-109 (Judge)
- [ ] Add cost tracking and budget enforcement
- [ ] Add cost estimation
- [ ] Create `--hybrid` CLI flag
- [ ] Add hybrid configuration options to CLI
- [ ] Write unit tests for each stage
- [ ] Write integration tests for full pipeline
- [ ] Document cost/quality trade-offs
- [ ] Add examples for common use cases

## Success Criteria

- [ ] `persona generate --hybrid` produces frontier-quality personas
- [ ] Cost reduction of 50%+ vs frontier-only for bulk generation
- [ ] Quality within 5% of frontier-only approach
- [ ] Budget constraints respected
- [ ] Privacy mode works (local-only)
- [ ] Unit test coverage >= 90%

## Dependencies

- F-107: Native Ollama Provider
- F-108: PII Detection & Anonymisation (optional integration)
- F-109: LLM-as-Judge Persona Evaluation

## Example Cost Comparison

| Approach | 10 Personas | 100 Personas | Quality |
|----------|-------------|--------------|---------|
| **Frontier Only** | $2.00 | $20.00 | 95% |
| **Hybrid (2x drafts)** | $1.00 | $10.00 | 93% |
| **Hybrid (3x drafts, 0.85 threshold)** | $0.60 | $6.00 | 91% |
| **Local Only (70B)** | $0.00 | $0.00 | 88% |

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Quality degradation | Configurable threshold, conservative defaults |
| Unexpected costs | Budget cap, cost estimation before run |
| Local model unavailable | Fall back to frontier-only with warning |
| Slow pipeline | Progress feedback, parallel local generation |

---

## Related Documentation

- [R-013: Local Model Assessment](../../research/R-013-local-model-assessment.md)
- [F-107: Native Ollama Provider](F-107-native-ollama-provider.md)
- [F-109: LLM-as-Judge Persona Evaluation](F-109-llm-as-judge-evaluation.md)
