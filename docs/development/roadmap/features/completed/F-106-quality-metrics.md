# F-106: Quality Metrics

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-005 |
| **Milestone** | v1.1.0 |
| **Priority** | P1 |
| **Category** | Core |

## Problem Statement

Generated personas vary in quality. Without objective measurement, users cannot:
- Identify low-quality outputs that need regeneration
- Compare quality across experiments or models
- Set quality gates for production use
- Track quality trends over time

## Design Approach

Multi-dimensional quality scoring system evaluating personas on:

1. **Completeness** (25%) - Field population and depth
2. **Consistency** (20%) - Internal coherence
3. **Evidence Strength** (25%) - Link to source data
4. **Distinctiveness** (15%) - Uniqueness vs other personas
5. **Realism** (15%) - Plausibility as a real person

### Quality Score Model

```python
@dataclass
class QualityScore:
    persona_id: str
    persona_name: str
    overall_score: float  # 0-100
    level: QualityLevel   # EXCELLENT/GOOD/ACCEPTABLE/POOR/FAILING
    dimensions: dict[str, DimensionScore]
```

### Quality Levels

| Level | Score Range | Meaning |
|-------|-------------|---------|
| Excellent | 90-100 | Production-ready |
| Good | 75-89 | Minor issues only |
| Acceptable | 60-74 | Usable with caveats |
| Poor | 40-59 | Needs regeneration |
| Failing | 0-39 | Unusable |

### CLI Integration

```bash
# Score personas
persona score ./outputs/20250101_120000/
persona score ./personas.json --min-score 70

# Output formats
persona score ./outputs/ --output json
persona score ./outputs/ --output markdown --save report.md

# Configuration presets
persona score ./outputs/ --strict   # Higher thresholds
persona score ./outputs/ --lenient  # Lower thresholds
```

## Implementation

### Module Structure

```
src/persona/core/quality/
├── __init__.py
├── scorer.py           # QualityScorer orchestrator
├── models.py           # QualityScore, DimensionScore, QualityLevel
├── config.py           # QualityConfig with weights
└── metrics/
    ├── completeness.py   # Field population scoring
    ├── consistency.py    # Internal coherence checks
    ├── evidence.py       # Evidence strength scoring
    ├── distinctiveness.py # Uniqueness vs other personas
    └── realism.py        # Plausibility checks
```

### Metric Details

**Completeness** evaluates:
- Required fields present (id, name)
- Expected fields populated (demographics, goals, pain_points, behaviours, quotes)
- Field depth (list lengths meet minimums)
- Field richness (content detail level)

**Consistency** evaluates:
- Demographic-goal alignment (no age-goal mismatches)
- Behaviour-pain coherence (no contradictions)
- Quote alignment with persona traits
- Internal list uniqueness (no duplicates)

**Evidence Strength** evaluates:
- Coverage percentage of attributes with evidence
- Strength distribution (strong vs weak evidence)
- Source diversity (multiple sources used)

**Distinctiveness** evaluates:
- Maximum similarity to any other persona
- Average similarity to all others
- Unique attribute count

**Realism** evaluates:
- Name plausibility (not generic placeholders)
- Demographic coherence (sensible combinations)
- Quote authenticity (sounds like real speech)
- Goal specificity (not overly generic)

## Success Criteria

- [x] Calculate quality score (0-100) for each persona
- [x] Provide breakdown by dimension
- [x] CLI command `persona score` functional
- [x] JSON and Markdown output formats
- [x] Configurable thresholds (strict/lenient)
- [x] Batch scoring with cross-comparison
- [x] Unit tests (35 tests, 100% pass)

## Dependencies

- F-004: Persona generation (source of personas to score)
- F-005: Evidence linking (for evidence strength metric)
- F-049: Persona comparison (for distinctiveness metric)

---

## Related Documentation

- [Milestone: v1.1.0](../../milestones/v1.1.0.md)
- [Manual Tests: Quality Metrics](../../../../../tests/manual/quality_metrics_test_script.md)

---

**Status**: Complete
