# F-119: Bias & Stereotype Detection

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-007 |
| **Milestone** | v1.7.0 |
| **Priority** | P1 |
| **Category** | Quality |
| **Status** | Complete |

## Problem Statement

LLM-generated personas can perpetuate harmful stereotypes, particularly for intersectional demographic groups. Research shows GPT-3.5 and GPT-4 produce higher rates of racial stereotypes than human-written portrayals. Without bias detection, users may unknowingly deploy stereotypical personas that reinforce discrimination.

## Research Foundation

### Academic Sources

- **Marked Personas (ACL 2023)**: Prompt-based method measuring stereotypes without lexicons
- **StereoSet & CrowS-Pairs**: Benchmark datasets for stereotype detection
- **HolisticBias**: 600 descriptor terms across 13 demographic axes
- **HONEST Framework**: Multi-language stereotype recognition in completions

### Key Findings

- Stereotype detection is an emerging NLP field with significant societal implications
- Lexicon-based approaches have shortcomings; embedding-based methods more robust
- Intersectional analysis (race + gender + age) reveals compounded biases
- Early monitoring can prevent bias escalation into hate speech

## Design Approach

### Detection Methods

| Method | Description | Trade-offs |
|--------|-------------|------------|
| **Lexicon-based** | Match against stereotype word lists | Fast, interpretable, but limited coverage |
| **Embedding-based** | WEAT scores on vector representations | More nuanced, requires embeddings |
| **LLM-as-Judge** | Prompt LLM to identify stereotypes | Most flexible, but slower and costly |

### Architecture

```
Persona → BiasDetector → BiasReport
              │
    ┌─────────┼─────────┐
    │         │         │
Lexicon   Embedding   LLM-Judge
Matcher   Analyser    Evaluator
    │         │         │
    └─────────┴─────────┘
              │
       Aggregated Score
```

### Bias Categories

| Category | Description | Detection Method |
|----------|-------------|------------------|
| **Gender** | Role assumptions, trait stereotypes | Lexicon + embedding |
| **Racial/Ethnic** | Cultural stereotypes, appearance bias | Embedding + LLM |
| **Age** | Generational assumptions | Lexicon |
| **Professional** | Occupation-trait correlations | Lexicon + LLM |
| **Intersectional** | Compounded biases across categories | LLM-as-Judge |

### Python API

```python
from persona.core.quality.bias import BiasDetector, BiasConfig

# Configure detection
config = BiasConfig(
    methods=["lexicon", "embedding"],
    categories=["gender", "racial", "age", "professional"],
    threshold=0.3,  # Flag if bias score > 0.3
    lexicon="holisticbias",  # or "stereoset", "custom"
)

# Create detector
detector = BiasDetector(config)

# Analyse persona
report = detector.analyse(persona)

# Check results
print(f"Overall bias score: {report.overall_score}")
for finding in report.findings:
    print(f"  {finding.category}: {finding.description}")
    print(f"    Evidence: {finding.evidence}")
    print(f"    Severity: {finding.severity}")
```

### CLI Interface

```bash
# Check single persona for bias
persona bias check output/personas.json

# Batch analysis with specific categories
persona bias check output/ --categories gender,racial --threshold 0.4

# Generate detailed report
persona bias report output/personas.json --format markdown --output bias-report.md

# Use specific detection method
persona bias check output/ --method embedding --model all-MiniLM-L6-v2
```

## Implementation Tasks

- [ ] Create bias detection module structure (`persona/core/quality/bias/`)
- [ ] Implement lexicon-based detector with HolisticBias vocabulary
- [ ] Implement embedding-based detector using sentence-transformers
- [ ] Add LLM-as-Judge bias evaluator extending PersonaJudge
- [ ] Create BiasReport model with findings and severity levels
- [ ] Implement intersectional analysis combining multiple categories
- [ ] Add `persona bias check` CLI command
- [ ] Add `persona bias report` CLI command
- [ ] Create bias lexicon data files (bundled or downloadable)
- [ ] Write unit tests for each detection method
- [ ] Write integration tests for full pipeline
- [ ] Add documentation with examples

## Success Criteria

- [ ] Lexicon-based detection identifies common stereotypes
- [ ] Embedding-based detection catches subtle biases
- [ ] LLM-as-Judge provides interpretable explanations
- [ ] Intersectional analysis available for compound biases
- [ ] CLI commands functional with clear output
- [ ] Test coverage ≥ 85%
- [ ] False positive rate < 15% on benchmark data

## Dependencies

- F-106: Quality Metrics Scoring (foundation)
- F-114: LLM-as-Judge Evaluation (for LLM method)
- `sentence-transformers` (for embedding method)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| False positives on legitimate content | Medium | Medium | Configurable thresholds, human review option |
| Lexicon incompleteness | Medium | Low | Multiple lexicon sources, user-extensible |
| Cultural context sensitivity | High | Medium | Document limitations, regional lexicons |
| Performance on large batches | Low | Low | Batch processing, caching |

---

## Related Documentation

- [Milestone v1.7.0](../../milestones/v1.7.0.md)
- [F-114: LLM-as-Judge Evaluation](../completed/F-114-llm-as-judge-evaluation.md)
- [Quality Metrics Reference](../../../../reference/quality-metrics.md)

---

**Status**: Complete
