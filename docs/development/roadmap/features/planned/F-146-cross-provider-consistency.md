# F-146: Cross-Provider Consistency Report

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-146 |
| **Title** | Cross-Provider Consistency Report |
| **Priority** | P0 (Critical) |
| **Category** | Quality |
| **Milestone** | [v1.14.0](../../milestones/v1.14.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-142 (Response Caching Layer) |

---

## Problem Statement

Different LLM providers produce different persona outputs for the same input. Without systematic comparison, users cannot:
- Understand provider-specific tendencies
- Choose optimal providers for their use case
- Identify provider-induced biases
- Validate generation consistency

---

## Design Approach

Generate personas using multiple providers from identical inputs, then compare and report on consistency.

---

## Key Capabilities

### 1. Multi-Provider Generation

Generate personas with multiple providers simultaneously.

```bash
# Compare across providers
persona quality providers --compare --from data/

# Specific providers
persona quality providers --compare \
  --providers anthropic,openai,ollama \
  --from data/
```

### 2. Consistency Analysis

Analyse semantic and structural consistency.

```python
class ConsistencyAnalyser:
    def analyse(
        self,
        personas: dict[str, Persona]  # provider -> persona
    ) -> ConsistencyReport:
        return ConsistencyReport(
            semantic_similarity=self._compute_semantic_matrix(personas),
            structural_alignment=self._compute_structural_alignment(personas),
            field_consistency=self._analyse_field_consistency(personas),
            bias_indicators=self._detect_provider_biases(personas)
        )
```

### 3. Consistency Report

Generate detailed comparison reports.

```bash
# Generate report
persona quality providers --report --output comparison.md
```

**Output:**
```markdown
# Provider Consistency Report

## Summary

| Provider | Semantic Sim | Structural | Bias Score |
|----------|--------------|------------|------------|
| anthropic | 0.92 (ref) | 95% | 0.12 |
| openai | 0.89 | 92% | 0.15 |
| ollama | 0.78 | 88% | 0.21 |

## Semantic Similarity Matrix

| | anthropic | openai | ollama |
|---|-----------|--------|--------|
| anthropic | 1.00 | 0.89 | 0.78 |
| openai | 0.89 | 1.00 | 0.82 |
| ollama | 0.78 | 0.82 | 1.00 |

## Field Analysis

### Demographics
- Age: High consistency (σ = 1.2 years)
- Location: Medium consistency (70% exact match)
- Occupation: Low consistency (different terminology)

### Behaviours
- anthropic: More detailed, longer descriptions
- openai: Concise, action-oriented
- ollama: Variable quality

## Recommendations

Based on this analysis:
- **High fidelity**: Use anthropic
- **Cost-effective**: Use ollama for drafts, anthropic for final
- **Balanced**: Use openai
```

### 4. Provider Selection Guide

Recommend providers based on requirements.

```bash
persona quality providers --recommend \
  --priority quality \
  --budget 10.00
```

---

## CLI Commands

```bash
# Multi-provider comparison
persona quality providers --compare [--from PATH] [--providers LIST]

# Generate report
persona quality providers --report [--output FILE] [--format md|json|html]

# Provider recommendation
persona quality providers --recommend [--priority quality|cost|speed]

# Single provider benchmark
persona quality providers --benchmark --provider NAME
```

---

## Success Criteria

- [ ] Multi-provider generation works simultaneously
- [ ] Semantic similarity matrix accurately reflects differences
- [ ] Structural alignment percentage calculated correctly
- [ ] Provider-specific biases identified
- [ ] Reports exportable in multiple formats
- [ ] Provider recommendations based on use case
- [ ] Test coverage >= 85%

---

## Related Documentation

- [v1.14.0 Milestone](../../milestones/v1.14.0.md)
- [R-024: Cross-Provider Consistency Analysis](../../../research/R-024-cross-provider-consistency.md)
- [F-142: Response Caching Layer](F-142-response-caching-layer.md)

---

**Status**: Planned
