# Quality Metrics Reference

Technical specifications for persona quality assessment metrics in Persona.

## Overview

Persona uses a multi-dimensional quality assessment framework to evaluate generated personas. Each metric provides a score from 0.0 to 1.0, with configurable thresholds for quality gates.

---

## Metric Categories

| Category | Purpose | Metrics |
|----------|---------|---------|
| **Content Quality** | Factual accuracy and grounding | Faithfulness, Groundedness |
| **Linguistic Quality** | Language naturalness and diversity | Lexical Diversity, Coherence |
| **Faithfulness** | Semantic alignment with source | BERTScore, ROUGE-L |
| **Diversity** | Output variety across personas | MTLD, MATTR, TTR |
| **Bias Detection** | Stereotype and fairness analysis | Bias Score, Stereotype Count |

---

## Content Quality Metrics

### Groundedness Score

Measures how well persona attributes are supported by source data.

```python
from persona.core.quality import GroundednessScorer

scorer = GroundednessScorer()
result = scorer.score(
    persona=persona_output,
    source_data=input_data
)

# Returns:
# {
#     "score": 0.85,
#     "supported_claims": 17,
#     "total_claims": 20,
#     "unsupported": ["Claim about age not in source"]
# }
```

| Property | Type | Description |
|----------|------|-------------|
| `score` | `float` | Overall groundedness (0.0-1.0) |
| `supported_claims` | `int` | Claims with source evidence |
| `total_claims` | `int` | Total extracted claims |
| `unsupported` | `list[str]` | Claims lacking evidence |

**Algorithm:** Extracts verifiable claims from persona output, then matches each against source data using embedding similarity (threshold: 0.7).

### Faithfulness Score

Measures semantic alignment between persona and source using NLI-based verification.

```python
from persona.core.quality import FaithfulnessScorer

scorer = FaithfulnessScorer(model="cross-encoder/nli-deberta-v3-base")
result = scorer.score(
    persona=persona_output,
    source_data=input_data
)

# Returns:
# {
#     "score": 0.92,
#     "entailment_ratio": 0.88,
#     "contradiction_ratio": 0.04,
#     "neutral_ratio": 0.08
# }
```

| Property | Type | Description |
|----------|------|-------------|
| `score` | `float` | Overall faithfulness (0.0-1.0) |
| `entailment_ratio` | `float` | Proportion of entailed claims |
| `contradiction_ratio` | `float` | Proportion of contradictions |
| `neutral_ratio` | `float` | Proportion of neutral claims |

---

## Linguistic Quality Metrics

### Lexical Diversity (MTLD)

Measure of Textual Lexical Diversity - vocabulary richness that accounts for text length.

```python
from persona.core.quality import LexicalDiversityScorer

scorer = LexicalDiversityScorer()
result = scorer.score(text=persona_text)

# Returns:
# {
#     "mtld": 72.5,
#     "mattr": 0.78,
#     "ttr": 0.65,
#     "unique_words": 234,
#     "total_words": 360
# }
```

| Metric | Range | Interpretation |
|--------|-------|----------------|
| **MTLD** | 0-200+ | Higher = more diverse. Typical: 50-100 |
| **MATTR** | 0.0-1.0 | Moving-average TTR. Target: >0.7 |
| **TTR** | 0.0-1.0 | Type-token ratio. Varies with length |

**MTLD Algorithm:**
1. Calculate sequential TTR until it falls below 0.72
2. Record factor length, reset counter
3. MTLD = total_words / factor_count

### Coherence Score

Measures logical flow and consistency within persona narrative.

```python
from persona.core.quality import CoherenceScorer

scorer = CoherenceScorer()
result = scorer.score(persona=persona_output)

# Returns:
# {
#     "score": 0.88,
#     "sentence_coherence": 0.91,
#     "section_coherence": 0.85
# }
```

| Property | Type | Description |
|----------|------|-------------|
| `score` | `float` | Overall coherence (0.0-1.0) |
| `sentence_coherence` | `float` | Adjacent sentence similarity |
| `section_coherence` | `float` | Section-level logical flow |

---

## Semantic Similarity Metrics

### BERTScore

Contextual embedding similarity using BERT representations.

```python
from persona.core.quality import SemanticScorer

scorer = SemanticScorer(method="bertscore")
result = scorer.score(
    generated=persona_text,
    reference=source_text
)

# Returns:
# {
#     "precision": 0.87,
#     "recall": 0.82,
#     "f1": 0.845
# }
```

| Property | Type | Description |
|----------|------|-------------|
| `precision` | `float` | Generated tokens matched in reference |
| `recall` | `float` | Reference tokens matched in generated |
| `f1` | `float` | Harmonic mean of precision and recall |

**Model:** `microsoft/deberta-xlarge-mnli` (default)

### ROUGE-L

Longest common subsequence overlap for lexical similarity.

```python
from persona.core.quality import SemanticScorer

scorer = SemanticScorer(method="rouge")
result = scorer.score(
    generated=persona_text,
    reference=source_text
)

# Returns:
# {
#     "rouge_l_precision": 0.45,
#     "rouge_l_recall": 0.52,
#     "rouge_l_f1": 0.48
# }
```

**Note:** ROUGE-L scores are typically lower than BERTScore for persona generation since personas transform rather than reproduce source text.

---

## Bias Detection Metrics

### Bias Score

Multi-method bias detection combining lexicon, embedding, and LLM approaches.

```python
from persona.core.quality import BiasScorer

scorer = BiasScorer(
    methods=["lexicon", "embedding", "llm"],
    categories=["gender", "race", "age", "profession"]
)
result = scorer.score(persona=persona_output)

# Returns:
# {
#     "overall_score": 0.15,  # Lower = less bias
#     "by_category": {
#         "gender": 0.12,
#         "race": 0.08,
#         "age": 0.22,
#         "profession": 0.18
#     },
#     "flagged_terms": [
#         {"term": "young professional", "category": "age", "severity": "low"}
#     ]
# }
```

| Property | Type | Description |
|----------|------|-------------|
| `overall_score` | `float` | Combined bias score (0.0-1.0, lower = better) |
| `by_category` | `dict` | Bias score per demographic category |
| `flagged_terms` | `list` | Specific terms flagged for review |

**Methods:**
1. **Lexicon:** HolisticBias vocabulary matching (600+ terms)
2. **Embedding:** WEAT-style association tests
3. **LLM:** Chain-of-thought bias analysis

### Stereotype Detection

Specific stereotype pattern identification.

```python
from persona.core.quality import StereotypeDetector

detector = StereotypeDetector()
result = detector.detect(persona=persona_output)

# Returns:
# {
#     "stereotype_count": 2,
#     "stereotypes": [
#         {
#             "text": "As a female designer, she brings empathy...",
#             "category": "gender",
#             "pattern": "gendered_trait_attribution",
#             "severity": "medium"
#         }
#     ],
#     "clean": False
# }
```

---

## Composite Scoring

### Quality Score Aggregation

Combine multiple metrics into a single quality score.

```python
from persona.core.quality import QualityScorer

scorer = QualityScorer(
    weights={
        "groundedness": 0.25,
        "faithfulness": 0.20,
        "lexical_diversity": 0.15,
        "coherence": 0.15,
        "bias": 0.25  # Inverted: high bias = low score
    }
)

result = scorer.score(
    persona=persona_output,
    source_data=input_data
)

# Returns:
# {
#     "overall_score": 0.82,
#     "grade": "B+",
#     "metrics": {
#         "groundedness": 0.85,
#         "faithfulness": 0.88,
#         "lexical_diversity": 0.75,
#         "coherence": 0.82,
#         "bias": 0.12
#     },
#     "recommendations": [
#         "Consider increasing vocabulary diversity",
#         "Review age-related language for potential bias"
#     ]
# }
```

### Grade Thresholds

| Grade | Score Range | Interpretation |
|-------|-------------|----------------|
| A+ | 0.95-1.00 | Excellent - publication ready |
| A | 0.90-0.94 | Very good - minor refinements |
| B+ | 0.85-0.89 | Good - some improvements needed |
| B | 0.80-0.84 | Acceptable - review recommended |
| C | 0.70-0.79 | Marginal - significant issues |
| D | 0.60-0.69 | Poor - major revision needed |
| F | <0.60 | Failing - regenerate required |

---

## Configuration

### Default Configuration

```yaml
# persona.yaml
quality:
  enabled: true

  metrics:
    groundedness:
      enabled: true
      threshold: 0.70

    faithfulness:
      enabled: true
      threshold: 0.75
      model: cross-encoder/nli-deberta-v3-base

    lexical_diversity:
      enabled: true
      mtld_threshold: 50.0
      mattr_threshold: 0.70

    coherence:
      enabled: true
      threshold: 0.75

    bias:
      enabled: true
      threshold: 0.25  # Maximum acceptable bias
      categories:
        - gender
        - race
        - age
        - profession

  composite:
    weights:
      groundedness: 0.25
      faithfulness: 0.20
      lexical_diversity: 0.15
      coherence: 0.15
      bias: 0.25

    grade_thresholds:
      A+: 0.95
      A: 0.90
      B+: 0.85
      B: 0.80
      C: 0.70
      D: 0.60
```

### CLI Usage

```bash
# Score a generated persona
persona quality score output/personas.json

# Score with specific metrics
persona quality score output/personas.json --metrics groundedness,bias

# Generate quality report
persona quality report output/personas.json --format markdown

# Check quality gate (exit 1 if below threshold)
persona quality check output/personas.json --threshold 0.80
```

---

## Dependencies

Quality metrics require optional dependencies:

```bash
# Install quality metrics dependencies
pip install persona[academic]
```

This installs:
- `rouge-score>=0.1.2` - ROUGE metric
- `bert-score>=0.3.13` - BERTScore metric
- `transformers>=4.36.0` - NLI models for faithfulness
- `sentence-transformers>=2.2.0` - Embedding-based metrics

---

## Related Documentation

- [LLM-as-Judge Evaluation](../development/roadmap/features/completed/F-114-llm-as-judge-evaluation.md)
- [Quality Metrics Taxonomy Research](../development/research/R-015-quality-metrics-taxonomy.md)
- [Bias Detection Feature](../development/roadmap/features/completed/F-119-bias-stereotype-detection.md)
- [Lexical Diversity Feature](../development/roadmap/features/completed/F-121-lexical-diversity-metrics.md)

---

**Status**: Complete
