# F-019: Persona Validation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-005 |
| **Milestone** | v0.2.0 |
| **Priority** | P1 |
| **Category** | Validation |

## Problem Statement

Academic research (CHI 2024, arXiv 2503.16527) shows LLM-generated personas have systematic biases and may include hallucinated attributes not grounded in source data. Users need a way to validate that generated personas accurately reflect their research data before using them for decision-making.

## Design Approach

- Cross-reference persona attributes with source data
- Use embedding similarity to match persona claims to source quotes
- Calculate evidence coverage score (percentage of attributes backed by data)
- Identify gaps where persona makes unsupported claims
- Generate validation report with confidence scores

## Implementation Tasks

- [ ] Create validation engine with embedding-based matching
- [ ] Implement attribute extraction from personas
- [ ] Build source data indexing for efficient lookup
- [ ] Calculate coverage and confidence scores
- [ ] Implement gap analysis (unsupported claims)
- [ ] Create `persona validate <id>` CLI command
- [ ] Generate validation report (Markdown, JSON)
- [ ] Add evidence citations to report
- [ ] Write unit tests

## Success Criteria

- [ ] Coverage score accurately reflects evidence backing
- [ ] Hallucinated attributes identified with high precision
- [ ] Source citations linked to persona attributes
- [ ] Validation completes within reasonable time (<30s for typical persona)
- [ ] Report exportable for stakeholder review
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Data loading for source access
- F-004: Persona generation
- Embedding model for similarity matching
- ADR-0019: Persona Validation Methodology

---

## Related Documentation

- [UC-005: Validate Personas](../../../../use-cases/briefs/UC-005-validate-personas.md)
- [F-024: Evidence Linking](F-024-evidence-linking.md)
- [ADR-0019: Persona Validation Methodology](../../../decisions/adrs/ADR-0019-persona-validation-methodology.md)

