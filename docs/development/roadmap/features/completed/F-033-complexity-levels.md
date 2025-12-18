# F-033: Complexity Levels

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-005 |
| **Milestone** | v0.3.0 |
| **Priority** | P1 |
| **Category** | Variation |

## Problem Statement

Different use cases require different levels of persona detail. A quick prototype may need simple personas, whilst stakeholder presentations need comprehensive detail. Users need the ability to specify complexity levels to match their needs.

## Design Approach

- Three complexity levels: simple, moderate, complex
- Each level defines different output requirements
- Configurable via CLI and experiment config
- Affects prompt templates and validation

### Complexity Definitions

| Level | Attributes | Goals/Pain Points | Evidence | Use Case |
|-------|------------|-------------------|----------|----------|
| Simple | Demographics only | 2-3 each | None | Rapid prototyping |
| Moderate | Demographics + behaviours | 4-6 each | Optional | Standard use |
| Complex | Full schema | 7-10 each | Required | Research-grade |

## Implementation Tasks

- [ ] Define complexity level enum (simple, moderate, complex)
- [ ] Create complexity-specific prompt templates
- [ ] Implement schema validation per complexity level
- [ ] Add `--complexity` CLI flag
- [ ] Add complexity to experiment config
- [ ] Update cost estimation for complexity levels
- [ ] Write unit tests for each level
- [ ] Write integration tests

## Success Criteria

- [ ] All three levels produce valid personas
- [ ] Simple personas generated 50% faster than complex
- [ ] Complex personas include full evidence linking
- [ ] CLI flag works correctly
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation pipeline
- F-024: Evidence linking (for complex level)

---

## Related Documentation

- [Milestone v0.3.0](../../milestones/v0.3.0.md)
- [F-034: Detail Levels](F-034-detail-levels.md)
- [F-035: Variation Combinations](F-035-variation-combinations.md)
