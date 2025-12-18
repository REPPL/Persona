# F-029: Empathy Map Input Format

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-009 |
| **Milestone** | v0.2.0 |
| **Priority** | P1 |
| **Category** | Data |

## Problem Statement

The Boag empathy mapping method (used in co-creation workshops) produces messy, unstructured data (post-it notes, whiteboard captures). Current data loaders assume structured input. Research (Lycett et al. 2025, ISJ) validates this approach for persona development.

## Design Approach

- Support empathy map structured YAML/JSON input
- Five dimensions: Tasks, Feelings, Influences, Pain Points, Goals
- Handle freeform text within categories
- Support multiple participant types
- Validate empathy map structure

## Implementation Tasks

- [ ] Design empathy map schema (YAML/JSON)
- [ ] Create EmpathyMapLoader class
- [ ] Implement validation for required dimensions
- [ ] Handle messy/freeform text entries
- [ ] Support participant type grouping
- [ ] Add `--format empathy-map` flag
- [ ] Create sample empathy map templates
- [ ] Document input format with examples
- [ ] Write unit tests

## Success Criteria

- [ ] Valid empathy maps load correctly
- [ ] Missing dimensions produce clear errors
- [ ] Freeform text preserved without loss
- [ ] Multiple participant types supported
- [ ] Schema documentation complete
- [ ] Test coverage ≥ 80%

## Input Format Example

```yaml
participants: 22
method: "co-creation workshop with interviews"
data:
  - participant_type: "music_fan"
    tasks:
      - "Expanding and exhibiting collection(s)"
      - "Engaging with community"
    feelings:
      - "Easy to navigate"
      - "Curation is critical"
    influences:
      - "Community (artists, other superfans)"
      - "Concerts (organiser & venues)"
    pain_points:
      - "Collecting becomes increasingly time-consuming"
      - "Inaccurate/missing information"
    goals:
      - "Expand and share collection"
      - "Safe interactions with others"
```

## Dependencies

- F-001: Data loading (base classes)
- F-004: Persona generation

## References

### Foundational Work

Boag, P. (2015). Adapting Empathy Maps for UX Design. *Boagworld*. https://boagworld.com/usability/adapting-empathy-maps-for-ux-design/

### Academic Application

Lycett, M., Cundle, M., Grasso, L., Meechao, K., & Reppel, A. (2025). Materialising Design Fictions: Exploring Music Memorabilia in a Metaverse Environment. *Information Systems Journal*, 35, 1662–1678. https://doi.org/10.1111/isj.12600

---

## Related Documentation

- [UC-009: Empathy Mapping](../../../../use-cases/briefs/UC-009-empathy-mapping.md)
- [F-030: Empathy Map Table Output](F-030-empathy-map-table-output.md)
- [F-001: Data Loading](F-001-data-loading.md)
