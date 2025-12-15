# F-069: Confidence Scoring

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-007 |
| **Milestone** | v0.8.0 |
| **Priority** | P1 |
| **Category** | Analysis |

## Problem Statement

Not all persona attributes are equally well-supported by source data. Users need to understand which characteristics are strongly evidenced vs. inferred, to make informed decisions about persona reliability.

## Design Approach

- Score confidence for each persona attribute
- Use three levels: high, medium, low
- Base confidence on evidence strength
- Aggregate to persona-level confidence
- Display confidence in output

### Confidence Levels

| Level | Description | Evidence |
|-------|-------------|----------|
| **High** | Strongly supported | Multiple explicit mentions |
| **Medium** | Reasonably supported | Single mention or strong inference |
| **Low** | Inferred/extrapolated | Pattern-based inference only |

### Confidence Calculation

```python
@dataclass
class AttributeConfidence:
    attribute: str
    value: str
    confidence: Literal["high", "medium", "low"]
    evidence_count: int
    evidence_sources: list[str]
    reasoning: str
```

### Output Format

```json
{
  "persona": {
    "name": "Jordan",
    "attributes": {
      "role": {
        "value": "Senior Developer",
        "confidence": "high",
        "evidence_count": 5,
        "reasoning": "Explicitly stated in 3 sources, implied in 2"
      },
      "frustration": {
        "value": "Documentation gaps",
        "confidence": "medium",
        "evidence_count": 2,
        "reasoning": "Mentioned directly in 1 source, context in 1"
      },
      "preferred_learning": {
        "value": "Video tutorials",
        "confidence": "low",
        "evidence_count": 0,
        "reasoning": "Inferred from age group patterns"
      }
    },
    "overall_confidence": "medium"
  }
}
```

## Implementation Tasks

- [ ] Create ConfidenceScorer class
- [ ] Implement evidence tracking
- [ ] Add confidence level thresholds
- [ ] Calculate attribute-level confidence
- [ ] Aggregate to persona-level
- [ ] Include reasoning in output
- [ ] Add confidence to all output formats
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Confidence levels accurate
- [ ] Evidence sources tracked
- [ ] Clear reasoning provided
- [ ] Confidence in all output formats
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation pipeline
- F-003: Prompt templating (for evidence tracking)

---

## Related Documentation

- [Milestone v0.8.0](../../milestones/v0.8.0.md)
- [Persona Schema](../../../reference/persona-schema.md)

