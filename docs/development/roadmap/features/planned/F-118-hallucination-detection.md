# F-118: Hallucination Detection

## Overview

| Attribute | Value |
|-----------|-------|
| **Research** | R-014 |
| **Milestone** | v1.6.0 |
| **Priority** | P2 |
| **Category** | Quality |

## Problem Statement

Expert surveys rate hallucination as the highest concern (M = 5.94/7) for GenAI personas. Current evidence linking in Persona is manual - users must explicitly specify which source data supports each persona attribute.

Without automatic hallucination detection:
- Unsupported claims in personas go undetected
- Faithfulness to source data cannot be quantified
- Users cannot trust generated personas for critical decisions

**Research Finding:** Li et al. (2025) shows "persona-based LLM simulations show systematic biases leading to significant deviations from real-world outcomes."

## Design Approach

Implement automatic claim extraction and faithfulness scoring using RAGAS-style methodology, with optional HHEM classifier for fast, free hallucination detection.

### Detection Pipeline

```
Generated Persona → Claim Extraction → Source Matching → Faithfulness Score
       ↓                   ↓                 ↓                   ↓
   "Marketing      "Occupation is      Find mentions      SUPPORTED /
    Manager"        Marketing Manager"  in interviews     UNSUPPORTED
```

### Python API

```python
from persona.core.quality.faithfulness import FaithfulnessValidator

# Create validator
validator = FaithfulnessValidator(
    embedding_model="text-embedding-3-small",
    similarity_threshold=0.7
)

# Validate persona against source
result = validator.validate(
    persona=persona,
    source_data=source_text
)

# FaithfulnessResult(
#     faithfulness_score=0.85,      # 85% of claims supported
#     total_claims=12,
#     supported_claims=10,
#     unsupported_claims=2,
#     hallucination_rate=0.167,
#     claim_details=[
#         ClaimResult(claim="Age 34", status="SUPPORTED", confidence=0.92),
#         ClaimResult(claim="Works at TechCorp", status="UNSUPPORTED", confidence=0.23),
#         ...
#     ]
# )

# Use HHEM classifier (fast, free, local)
from persona.core.quality.faithfulness import HHEMClassifier

hhem = HHEMClassifier()
is_hallucinated = hhem.classify(
    claim="User prefers email communication",
    context="Interview transcript: 'I hate checking emails'"
)
# True (hallucination detected)
```

### CLI Integration

```bash
# Run faithfulness validation
persona validate personas.json --faithfulness --source research_data.csv

# Show detailed claim analysis
persona validate personas.json --faithfulness --source data.csv --verbose

# Use fast HHEM classifier
persona validate personas.json --faithfulness --source data.csv --hhem

# Export hallucination report
persona validate personas.json --faithfulness --source data.csv --report hallucinations.md

# Set custom threshold
persona validate personas.json --faithfulness --source data.csv --threshold 0.8
```

### Claim Extraction

Automatically extract verifiable claims from persona attributes:

| Persona Field | Extracted Claims |
|---------------|------------------|
| `name: "Sarah Chen"` | "Person is named Sarah Chen" |
| `age: 34` | "Person is 34 years old" |
| `occupation: "Marketing Manager"` | "Occupation is Marketing Manager" |
| `goals: ["Increase team efficiency"]` | "Goal: Increase team efficiency" |
| `quote: "I need quick solutions"` | "Person said: I need quick solutions" |

### Claim Verification Levels

| Level | Threshold | Meaning |
|-------|-----------|---------|
| **STRONG** | > 0.8 | Direct quote or explicit mention |
| **MODERATE** | 0.6 - 0.8 | Paraphrased or inferred |
| **WEAK** | 0.4 - 0.6 | Loosely related |
| **UNSUPPORTED** | < 0.4 | No evidence found |

### Faithfulness Formula

```
Faithfulness = (STRONG + MODERATE) / Total Claims
Hallucination Rate = UNSUPPORTED / Total Claims
```

### HHEM Integration

[Vectara HHEM-2.1-Open](https://huggingface.co/vectara/hallucination_evaluation_model) is a free, small T5-based classifier trained specifically for hallucination detection:

- **Model size**: ~300MB
- **Inference**: CPU-friendly, < 100ms per claim
- **Accuracy**: Competitive with LLM-based methods
- **Cost**: Free (runs locally)

## Implementation Tasks

- [ ] Create `src/persona/core/quality/faithfulness/__init__.py`
- [ ] Create `src/persona/core/quality/faithfulness/extractor.py` with `ClaimExtractor`
- [ ] Create `src/persona/core/quality/faithfulness/matcher.py` with embedding matching
- [ ] Create `src/persona/core/quality/faithfulness/validator.py` with `FaithfulnessValidator`
- [ ] Create `src/persona/core/quality/faithfulness/hhem.py` with `HHEMClassifier`
- [ ] Implement claim extraction from persona fields
- [ ] Implement embedding-based source matching
- [ ] Implement faithfulness score calculation
- [ ] Add HHEM model integration (optional dependency)
- [ ] Create `persona validate --faithfulness` CLI command
- [ ] Add `--hhem` flag for fast classification
- [ ] Add `--threshold` for configurable sensitivity
- [ ] Generate hallucination reports (Markdown, JSON)
- [ ] Write unit tests for claim extraction
- [ ] Write unit tests for faithfulness scoring
- [ ] Write integration tests with real embeddings
- [ ] Document interpretation of faithfulness scores

## Success Criteria

- [ ] Automatic extraction of verifiable claims from persona attributes
- [ ] Faithfulness score = (supported claims) / (total claims)
- [ ] Claims matched to source data with confidence scores
- [ ] Hallucination rate reported per persona
- [ ] HHEM classifier provides fast local alternative
- [ ] Unit test coverage >= 90%
- [ ] Integration with existing validation framework

## Dependencies

- F-106: Quality Metrics Scoring (existing framework)
- F-024: Evidence Linking (existing evidence infrastructure)
- Optional: `transformers` for HHEM classifier

## Non-Goals

- Fixing hallucinations automatically (detection only)
- Real-time hallucination prevention during generation
- Multi-document source verification (single source file for v1.6.0)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Claim extraction misses nuanced attributes | Start with structured fields, iterate |
| Embedding similarity gives false positives | Tunable threshold, human review option |
| HHEM model requires download | Graceful fallback to embedding-only |
| Large source files slow matching | Chunk source data, batch embeddings |

---

## Related Documentation

- [R-014: Shin et al. Gap Analysis](../../../research/R-014-shin-et-al-gap-analysis.md)
- [R-008: Persona Validation Methodology](../../../research/R-008-persona-validation-methodology.md)
- [F-024: Evidence Linking](../completed/F-024-evidence-linking.md)
- [F-106: Quality Metrics Scoring](../completed/F-106-quality-metrics.md)
- [RAGAS Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)
- [Vectara HHEM-2.1-Open](https://huggingface.co/vectara/hallucination_evaluation_model)
