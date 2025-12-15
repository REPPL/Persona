# F-024: Evidence Linking

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-005 |
| **Milestone** | v0.2.0 |
| **Priority** | P1 |
| **Category** | Output |

## Problem Statement

Best practice from Shin et al. (DIS 2024) shows personas should demonstrate provenance and be traceable to source data. Their human-AI workflow research found that LLMs alone miss key characteristics; personas need clear links to the evidence that supports each attribute.

## Design Approach

- Extend persona output schema with `evidence` field
- Include direct quotes for each attribute
- Record source file and location
- Support evidence strength indicators
- Enable audit trail for stakeholder review

## Implementation Tasks

- [x] Design evidence linking schema
- [x] Extend persona output format with evidence field
- [x] Modify generation prompts to extract evidence
- [x] Implement source location tracking
- [x] Add evidence strength scoring
- [x] Create evidence view in CLI output
- [x] Export evidence report for auditing
- [x] Update JSON schema documentation
- [x] Write unit tests (40 tests)

## Success Criteria

- [x] Every persona attribute has linked evidence
- [x] Source quotes accurately extracted
- [x] File/location references correct and clickable
- [x] Evidence strength reflects actual support
- [x] Audit report suitable for stakeholder review
- [x] Test coverage ≥ 80%

## Dependencies

- F-001: Data loading (source access)
- F-004: Persona generation
- F-005: Output formatting

## Implementation Notes

Implemented in v0.2.0 with:
- `EvidenceLinker` class for tracking evidence
- `Evidence` dataclass with strength scoring (STRONG, MODERATE, WEAK, INFERRED)
- `EvidenceReport` for audit trail generation
- Full test coverage in `tests/unit/core/test_evidence.py`

---

## Related Documentation

- [UC-005: Validate Personas](../../../../use-cases/briefs/UC-005-validate-personas.md)
- [F-019: Persona Validation](F-019-persona-validation.md)
- [Persona Schema Reference](../../../../../reference/persona-schema.md)

