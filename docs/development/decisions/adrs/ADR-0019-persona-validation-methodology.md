# ADR-0019: Persona Validation Methodology

## Status

Accepted

## Context

Academic research (Shin et al. DIS 2024, Li et al. arXiv 2503.16527) demonstrates that LLM-generated personas suffer from systematic biases and hallucinations. Expert surveys rate hallucination as the highest concern (M = 5.94/7) for GenAI personas. Users need robust validation to trust personas for decision-making.

Persona aims to be research-grade software where every output is auditable. Without systematic validation, personas may contain claims unsupported by source data, undermining their value for research and design decisions.

## Decision

Implement multi-layer persona validation with the following methodology:

### 1. Claim Extraction
- Parse each persona attribute as a verifiable claim
- Handle compound claims (split into atomic units)
- Preserve attribute context for matching

### 2. Evidence Matching
- Use embedding similarity (text-embedding-3-small default)
- Match claims to source data chunks
- Return top-k matches with similarity scores
- Configurable similarity threshold (default: 0.7)

### 3. Scoring

```python
# Per-attribute scoring
def score_attribute(claim: str, sources: List[str]) -> EvidenceScore:
    embeddings = embed([claim] + sources)
    similarities = cosine_similarity(embeddings[0], embeddings[1:])
    max_sim = max(similarities)

    if max_sim > 0.8:
        return EvidenceScore.STRONG
    elif max_sim > 0.6:
        return EvidenceScore.MODERATE
    elif max_sim > 0.4:
        return EvidenceScore.WEAK
    else:
        return EvidenceScore.UNSUPPORTED

# Aggregate scoring
coverage = count(score != UNSUPPORTED) / total_attributes
faithfulness = mean([similarity for score, similarity in scored_attributes])
hallucination_rate = count(score == UNSUPPORTED) / total_attributes
```

### 4. Threshold Configuration

```yaml
validation:
  embedding_model: "text-embedding-3-small"
  similarity_threshold: 0.7
  coverage_minimum: 0.80
  faithfulness_minimum: 0.75
  max_hallucination_rate: 0.15
```

### 5. Report Generation
- Markdown for human review
- JSON for programmatic access
- Optional: Persona Perception Scale survey template

## Consequences

**Positive:**
- Research-grade validation for persona quality
- Quantifiable trust metrics for stakeholders
- Hallucination detection before personas used in decisions
- Alignment with academic best practices (RAGAS, Shin et al., PPS)
- Evidence linking provides auditability

**Negative:**
- Requires embedding model API calls (additional cost)
- Validation time adds to workflow
- False positives possible (semantic similarity ≠ factual support)
- Threshold calibration may need domain tuning

## Alternatives Considered

### LLM-as-Judge Only (G-eval)
- Pro: Leverages LLM reasoning
- Con: More expensive, potentially circular (LLM validates LLM)
- Decision: Use as optional enhancement, not primary method

### Exact String Matching
- Pro: Simple, fast, no API calls
- Con: Misses paraphrases, too strict
- Decision: Rejected

### Human-Only Validation (PPS)
- Pro: Gold standard for perception
- Con: Doesn't scale, slow
- Decision: Optional add-on for stakeholder validation

---

## Related Documentation

- [R-008: Persona Validation Methodology](../../research/R-008-persona-validation-methodology.md)
- [F-019: Persona Validation](../../roadmap/features/completed/F-019-persona-validation.md)
- [ADR-0011: Multi-Step Workflow](ADR-0011-multi-step-workflow.md)
- [Persona Schema Reference](../../../reference/persona-schema.md)
