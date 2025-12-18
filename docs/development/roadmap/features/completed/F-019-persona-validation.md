# F-019: Persona Validation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-005 |
| **Milestone** | v0.2.0 |
| **Priority** | P1 |
| **Category** | Validation |

## Problem Statement

Academic research (Shin et al. DIS 2024, Li et al. arXiv 2503.16527) shows LLM-generated personas have systematic biases and may include hallucinated attributes not grounded in source data. Expert surveys rate hallucination as the highest concern (M = 5.94/7) for GenAI personas. Users need a way to validate that generated personas accurately reflect their research data before using them for decision-making.

## Design Approach

### Three-Layer Validation Architecture

**Layer 1: Attribute-Level Validation (Per-Claim)**
- Extract claims from each persona attribute
- Match to source data using embedding similarity
- Score: Strong (>0.8), Moderate (0.6-0.8), Weak (0.4-0.6), Unsupported (<0.4)

**Layer 2: Persona-Level Validation (Aggregate)**
- Coverage score: % of attributes with evidence
- Faithfulness score: Weighted claim verification
- Hallucination rate: % of unsupported claims

**Layer 3: Perceptual Validation (Optional)**
- Persona Perception Scale survey template generation
- Six dimensions: Credibility, Consistency, Completeness, Clarity, Empathy, Willingness to Use
- For stakeholder acceptance testing

### Validation Metrics

Based on Shin et al. DIS 2024 research:

| Metric | Method | Use Case |
|--------|--------|----------|
| **Evidence Coverage** | Count attributes with source links | Quick quality check |
| **Embedding Similarity** | text-embedding-3-small cosine | Attribute-to-source matching |
| **Faithfulness Score** | Aggregate claim verification | Hallucination detection |
| **G-eval Score** | GPT-4 validity rating (optional) | Information accuracy |

### Validation Levels

| Level | Speed | Cost | Use Case |
|-------|-------|------|----------|
| **Quick** | <5s | Free | Coverage score only |
| **Standard** | <30s | Low | Embedding similarity + coverage |
| **Comprehensive** | <2min | Medium | Full metrics + G-eval |

### Output Structure

```
outputs/{timestamp}/validation/
├── persona-001/
│   ├── validation_report.md    # Human-readable report
│   ├── validation_scores.json  # Machine-readable scores
│   ├── evidence_map.json       # Attribute → Source mapping
│   └── gaps.json               # Unsupported claims
└── summary.json                # Aggregate scores
```

## Implementation Tasks

- [ ] Create claim extractor for persona attributes
- [ ] Implement embedding-based source matching
- [ ] Build source data indexing with chunking
- [ ] Implement four-tier evidence strength scoring
- [ ] Calculate coverage, faithfulness, and hallucination metrics
- [ ] Create `persona validate <id>` CLI command
- [ ] Add `--level` flag (quick/standard/comprehensive)
- [ ] Generate validation report (Markdown)
- [ ] Generate machine-readable JSON output
- [ ] Add evidence citations with file and line numbers
- [ ] Optional: Implement G-eval with GPT-4
- [ ] Optional: Generate PPS survey template
- [ ] Write unit tests for scoring logic
- [ ] Add integration tests with sample data

## Success Criteria

- [ ] Coverage score correlates with actual evidence presence
- [ ] Faithfulness score detects injected hallucinations with >90% recall
- [ ] Attribute-source mapping accurate to file and line number
- [ ] Quick validation completes in <5s
- [ ] Standard validation completes in <30s
- [ ] Reports suitable for stakeholder review (non-technical)
- [ ] Configurable thresholds with sensible defaults
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Data loading for source access
- F-004: Persona generation
- Embedding model for similarity matching (text-embedding-3-small)
- ADR-0019: Persona Validation Methodology

---

## Related Documentation

- [R-008: Persona Validation Methodology](../../../research/R-008-persona-validation-methodology.md)
- [UC-005: Validate Personas](../../../../use-cases/briefs/UC-005-validate-personas.md)
- [F-024: Evidence Linking](F-024-evidence-linking.md)
- [ADR-0019: Persona Validation Methodology](../../../decisions/adrs/ADR-0019-persona-validation-methodology.md)
