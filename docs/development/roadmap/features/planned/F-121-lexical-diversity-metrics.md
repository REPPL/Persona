# F-121: Lexical Diversity Metrics

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-007 |
| **Milestone** | v1.7.0 |
| **Priority** | P2 |
| **Category** | Quality |
| **Status** | Planned |

## Problem Statement

LLM-generated text can exhibit repetitive vocabulary and formulaic phrasing, reducing persona authenticity. Without lexical diversity metrics, users cannot quantify vocabulary richness or detect "template-like" outputs. Research shows length-controlled diversity measurement is critical for accurate assessment.

## Research Foundation

### Academic Sources

- **McCarthy & Jarvis (2010)**: MTLD metric with demonstrated stability across text lengths
- **Covington & McFall (2010)**: MATTR as most stable diversity index
- **Dang et al. (Feb 2025)**: MTLD segmentation methodology updates
- **Deshpande et al. (Jul 2025)**: Length control requirements for synthetic pipelines

### Key Findings

- MTLD and MATTR are most stable metrics, less susceptible to text length influence
- Type-Token Ratio (TTR) is simple but biased by text length
- Surface metrics must be complemented by embedding-based semantic diversity
- Persona detail increases diversity only in large models

### Metrics Comparison

| Metric | Description | Length Bias | Stability |
|--------|-------------|-------------|-----------|
| **TTR** | Unique words / Total words | High | Low |
| **MATTR** | Moving-average TTR | Low | High |
| **MTLD** | Average words maintaining TTR threshold | Low | High |
| **Hapax Ratio** | Words appearing once / Total | Medium | Medium |

## Design Approach

### Architecture

```
Persona Text
     │
     ▼
┌────────────────┐
│ Text Extractor │  ← Combine all text fields
└───────┬────────┘
        │
   ┌────┴────┬────────┐
   │         │        │
   ▼         ▼        ▼
  TTR      MATTR    MTLD
   │         │        │
   └────┬────┴────────┘
        │
        ▼
┌────────────────┐
│ Diversity Score│  ← Weighted combination
└───────┬────────┘
        │
        ▼
  DiversityReport
```

### Python API

```python
from persona.core.quality.diversity import (
    LexicalDiversityAnalyser,
    DiversityConfig,
)

# Configure analysis
config = DiversityConfig(
    metrics=["ttr", "mattr", "mtld"],
    mattr_window=50,  # Window size for MATTR
    mtld_threshold=0.72,  # TTR threshold for MTLD segmentation
    include_hapax=True,
    min_tokens=50,  # Minimum tokens for reliable analysis
)

# Create analyser
analyser = LexicalDiversityAnalyser(config)

# Analyse single persona
report = analyser.analyse(persona)
print(f"TTR: {report.ttr:.3f}")
print(f"MATTR: {report.mattr:.3f}")
print(f"MTLD: {report.mtld:.1f}")
print(f"Hapax ratio: {report.hapax_ratio:.3f}")
print(f"Overall diversity: {report.overall_score:.3f}")

# Batch analysis with comparison
batch_report = analyser.analyse_batch(personas)
print(f"Mean MTLD: {batch_report.mean_mtld:.1f}")
print(f"Diversity variance: {batch_report.variance:.3f}")
```

### CLI Interface

```bash
# Analyse lexical diversity
persona diversity output/personas.json

# Specific metrics
persona diversity output/ --metrics mtld,mattr

# Batch comparison
persona diversity output/ --compare --format table

# Set quality threshold
persona diversity output/ --min-mtld 50 --warn-below

# Export detailed report
persona diversity output/ --report diversity-report.md
```

### Quality Thresholds

| MTLD Score | Interpretation |
|------------|----------------|
| < 30 | Poor - highly repetitive |
| 30-50 | Below average |
| 50-70 | Average |
| 70-100 | Good |
| > 100 | Excellent - rich vocabulary |

## Implementation Tasks

- [ ] Create diversity module structure (`persona/core/quality/diversity/`)
- [ ] Implement TTR calculation
- [ ] Implement MATTR with configurable window size
- [ ] Implement MTLD with forward/backward averaging (McCarthy & Jarvis 2010)
- [ ] Add hapax legomena counting
- [ ] Create text extraction from persona fields
- [ ] Implement DiversityReport model
- [ ] Add batch analysis with statistics
- [ ] Add `persona diversity` CLI command
- [ ] Integrate with QualityScorer as optional dimension
- [ ] Write unit tests with known-diversity texts
- [ ] Add documentation with interpretation guide

## Success Criteria

- [ ] MTLD calculation matches reference implementation
- [ ] MATTR stable across varying text lengths
- [ ] Batch analysis provides meaningful comparisons
- [ ] CLI output clear and actionable
- [ ] Integration with quality scoring framework
- [ ] Test coverage ≥ 85%
- [ ] Performance < 100ms per persona

## Dependencies

- F-106: Quality Metrics Scoring (integration point)
- `lexical-diversity` PyPI package (reference, may reimplement)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Short text unreliable metrics | Medium | Medium | Minimum token threshold, warnings |
| Language-specific tokenisation | Medium | Low | Use spaCy tokeniser, document limitations |
| Metric interpretation confusion | Medium | Low | Clear documentation, thresholds |

---

## Related Documentation

- [Milestone v1.7.0](../../milestones/v1.7.0.md)
- [F-106: Quality Metrics Scoring](../completed/F-106-quality-metrics.md)
- [Quality Metrics Reference](../../../../reference/quality-metrics.md)

---

**Status**: Planned
