# F-117: Academic Validation Metrics

## Overview

| Attribute | Value |
|-----------|-------|
| **Research** | R-014 |
| **Milestone** | v1.6.0 |
| **Priority** | P1 |
| **Category** | Quality |

## Problem Statement

Persona's documentation (R-008, ADR-0019) references academic evaluation metrics from Shin et al. (DIS 2024) that are not implemented in the codebase:

- **ROUGE-L** - Lexical overlap with source data (longest common subsequence)
- **BERTScore** - Semantic similarity via contextual embeddings
- **GPT-similarity** - High-dimensional embedding distance
- **G-eval** - Chain-of-thought GPT-4 validity scoring

Additionally, the Persona Perception Scale (PPS) - a validated 28-item survey instrument - is referenced but not implemented.

Without these metrics, Persona cannot:
- Make direct comparisons with academic research
- Claim standards-compliant validation
- Enable reproducible benchmarking

**Research Finding:** Shin et al. (DIS 2024) found "By every similarity metric, LLM-summarizing reached statistically higher scores than the other workflows (p < 0.01)."

## Design Approach

Implement Shin et al. four metrics plus PPS survey generation as an extension to the existing quality metrics system.

### Metric Pipeline

```
Persona + Source Data → Academic Metrics Engine
                              ↓
                        ROUGE-L | BERTScore | GPT-similarity | G-eval
                              ↓
                        AcademicValidationReport
```

### Python API

```python
from persona.core.quality.academic import AcademicValidator

# Create validator
validator = AcademicValidator(
    embedding_model="text-embedding-3-small",  # For GPT-similarity
    bert_model="distilbert-base-uncased",       # For BERTScore
)

# Validate persona against source
result = validator.validate(
    persona=persona,
    source_data=source_text,
    metrics=["rouge_l", "bertscore", "gpt_similarity", "geval"]
)

# AcademicValidationResult(
#     rouge_l=0.72,
#     bertscore=0.85,
#     gpt_similarity=0.81,
#     geval=0.78,
#     overall=0.79
# )

# Generate PPS survey
from persona.core.quality.pps import PersonaPerceptionSurvey

survey = PersonaPerceptionSurvey.generate(persona)
survey.export_markdown("pps_survey.md")
survey.export_json("pps_survey.json")
```

### CLI Integration

```bash
# Run academic validation
persona validate personas.json --academic --source research_data.csv

# Run specific metrics
persona validate personas.json --academic --metrics rouge_l,bertscore

# Generate PPS survey
persona validate personas.json --pps-survey --output pps_survey.md

# Full academic report
persona validate personas.json --academic --source data.csv --report academic_report.md
```

### Metric Specifications

| Metric | Method | Range | Library |
|--------|--------|-------|---------|
| **ROUGE-L** | Longest common subsequence | 0.0 - 1.0 | `rouge-score` |
| **BERTScore** | distilbert-base-uncased cosine | 0.0 - 1.0 | `bert-score` |
| **GPT-similarity** | text-embedding-3-small cosine | 0.0 - 1.0 | `openai` |
| **G-eval** | GPT-4 CoT validity scoring | 0.0 - 1.0 | PersonaJudge |

### Persona Perception Scale (PPS)

| Dimension | Items | Sample Statement |
|-----------|-------|------------------|
| **Credibility** | 4-5 | "The persona seems realistic" |
| **Consistency** | 4-5 | "The quotes match other information shown" |
| **Completeness** | 4-5 | "The persona profile is not missing vital information" |
| **Clarity** | 4-5 | "The persona is easy to understand" |
| **Empathy** | 4-5 | "I can relate to this persona" |
| **Willingness to Use** | 4-5 | "I would like to know more about this persona" |

Survey uses 7-point Likert scale (1 = Strongly Disagree, 7 = Strongly Agree).

## Implementation Tasks

- [ ] Add `rouge-score` and `bert-score` to `pyproject.toml` dependencies
- [ ] Create `src/persona/core/quality/academic/__init__.py`
- [ ] Create `src/persona/core/quality/academic/metrics.py` with metric classes
- [ ] Implement `RougeL` metric class
- [ ] Implement `BertScore` metric class
- [ ] Implement `GptSimilarity` metric class
- [ ] Implement `GEval` metric class (extending PersonaJudge with CoT)
- [ ] Create `AcademicValidator` orchestrator class
- [ ] Create `src/persona/core/quality/pps/__init__.py`
- [ ] Create `PersonaPerceptionSurvey` class
- [ ] Implement PPS 28-item survey template
- [ ] Add survey export (Markdown, JSON, CSV)
- [ ] Create `persona validate --academic` CLI command
- [ ] Create `persona validate --pps-survey` CLI command
- [ ] Write unit tests for each metric
- [ ] Write integration tests with real embeddings
- [ ] Document metric interpretation and benchmarks

## Success Criteria

- [ ] `persona validate --academic` runs all four Shin et al. metrics
- [ ] ROUGE-L score correlates with source data lexically
- [ ] BERTScore achieves > 0.8 for high-quality personas
- [ ] G-eval uses chain-of-thought evaluation
- [ ] PPS survey template can be exported for human validation
- [ ] Unit test coverage >= 90%
- [ ] Integration with existing F-106 QualityScorer

## Dependencies

- F-106: Quality Metrics Scoring (existing framework)
- F-114: LLM-as-Judge Evaluation (PersonaJudge infrastructure)
- External: `rouge-score`, `bert-score` PyPI packages

## Non-Goals

- Automated human study recruitment (PPS is template generation only)
- Real-time metric calculation (batch processing acceptable)
- Multi-language support (English-only for v1.6.0)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| BERTScore slow for large batches | Batch processing, progress feedback |
| GPT-similarity requires API key | Optional metric, graceful degradation |
| G-eval expensive | Cache results, low temperature for consistency |
| PPS requires human respondents | Clear documentation on survey usage |

---

## Related Documentation

- [R-014: Shin et al. Gap Analysis](../../../research/R-014-shin-et-al-gap-analysis.md)
- [R-008: Persona Validation Methodology](../../../research/R-008-persona-validation-methodology.md)
- [F-106: Quality Metrics Scoring](../completed/F-106-quality-metrics.md)
- [F-114: LLM-as-Judge Evaluation](../completed/F-114-llm-as-judge-evaluation.md)
- [Shin et al. DIS 2024](https://dl.acm.org/doi/10.1145/3643834.3660729)
- [Persona Perception Scale](https://www.sciencedirect.com/science/article/abs/pii/S1071581920300392)
