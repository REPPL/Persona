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

- [ ] Design evidence linking schema (ADR-0020)
- [ ] Extend persona output format with evidence field
- [ ] Modify generation prompts to extract evidence
- [ ] Implement source location tracking
- [ ] Add evidence strength scoring
- [ ] Create evidence view in CLI output
- [ ] Export evidence report for auditing
- [ ] Update JSON schema documentation
- [ ] Write unit tests

## Success Criteria

- [ ] Every persona attribute has linked evidence
- [ ] Source quotes accurately extracted
- [ ] File/location references correct and clickable
- [ ] Evidence strength reflects actual support
- [ ] Audit report suitable for stakeholder review
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Data loading (source access)
- F-004: Persona generation
- F-005: Output formatting
- ADR-0020: Evidence Linking Schema

---

## Related Documentation

- [UC-005: Validate Personas](../../../../use-cases/briefs/UC-005-validate-personas.md)
- [F-019: Persona Validation](F-019-persona-validation.md)
- [ADR-0020: Evidence Linking Schema](../../../decisions/adrs/ADR-0020-evidence-linking-schema.md)
- [R-010: Persona Schema Reference](../../../../reference/persona-schema.md)

