# F-065: Persona Count Estimation from Data

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-003 |
| **Milestone** | v0.7.0 |
| **Priority** | P2 |
| **Category** | Cost |

## Problem Statement

Users often don't know how many personas their data can support. Too few personas underutilise data; too many create thin, overlapping personas. An estimation feature helps users make informed decisions.

## Design Approach

- Analyse data volume and diversity
- Estimate optimal persona count range
- Consider data richness heuristics
- Factor in model capabilities
- Provide confidence intervals

### Estimation Algorithm

```python
def estimate_persona_count(data: DataSource, model: Model) -> CountEstimate:
    """Estimate optimal persona count."""

    # Heuristics
    tokens = count_tokens(data)
    unique_themes = extract_themes(data)  # Simple keyword clustering
    data_sources = len(data.files)

    # Base estimate: ~5000-10000 tokens per rich persona
    token_based = tokens // 7500

    # Theme-based: one persona per major theme cluster
    theme_based = len(unique_themes)

    # Source-based: can't have more personas than sources
    source_ceiling = data_sources

    return CountEstimate(
        recommended=min(token_based, theme_based),
        range=(max(2, token_based - 2), min(token_based + 2, source_ceiling)),
        confidence=calculate_confidence(tokens, unique_themes),
        reasoning="Based on data volume and theme diversity"
    )
```

### CLI Output

```
📊 Persona Count Estimation

Data Analysis:
  - Files: 12
  - Total tokens: 85,420
  - Identified themes: 5

Recommendation: 4-6 personas

Reasoning:
  Your data contains rich information across ~5 distinct themes.
  With 85K tokens, each persona can be well-supported with
  ~14-21K tokens of backing data.

  Generating more than 6 personas may result in thin personas
  with overlapping characteristics.
```

## Implementation Tasks

- [ ] Create PersonaEstimator class
- [ ] Implement token-based estimation
- [ ] Add simple theme extraction
- [ ] Calculate confidence levels
- [ ] Generate reasoning explanations
- [ ] Create `persona estimate` command
- [ ] Add to cost estimation flow
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Estimation within reasonable range
- [ ] Clear reasoning provided
- [ ] Confidence levels meaningful
- [ ] Integrates with cost estimation
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Multi-format data loading
- F-007: Cost estimation
- F-063: Token count tracking

---

## Related Documentation

- [Milestone v0.7.0](../../milestones/v0.7.0.md)
- [F-007: Cost Estimation](F-007-cost-estimation.md)

