# F-030: Empathy Map Table Output

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-009 |
| **Milestone** | v0.2.0 |
| **Priority** | P1 |
| **Category** | Output |

## Problem Statement

The Boag empathy mapping method outputs personas in a structured table format showing all five dimensions. This is standard in UX research practice and expected by stakeholders familiar with the methodology (cf. Table 1 in Lycett et al. 2025).

## Design Approach

- Generate Markdown/HTML tables with empathy map dimensions
- Columns: Persona, Tasks, Feelings, Influences, Pain Points, Goals
- Support multiple personas in single table
- Enable export for stakeholder presentations
- Preserve source data mapping

## Implementation Tasks

- [ ] Create empathy table output formatter
- [ ] Add `--output-format empathy-table` flag
- [ ] Generate Markdown table output
- [ ] Generate HTML table output
- [ ] Support Rich table for terminal display
- [ ] Implement multi-persona table view
- [ ] Add data point mapping (which input → which cell)
- [ ] Export as standalone HTML file
- [ ] Write unit tests

## Success Criteria

- [ ] Table renders correctly in terminal
- [ ] Markdown exports display in GitHub/docs
- [ ] HTML exports suitable for presentations
- [ ] Data mapping visible on request
- [ ] Multiple personas in single table
- [ ] Test coverage ≥ 80%

## Output Format Example

| Persona | Tasks | Feelings | Influences | Pain Points | Goals |
|---------|-------|----------|------------|-------------|-------|
| Superfan Alice | Expanding collection, Engaging with community | Easy to navigate, Curation is critical | Community, Concerts | Time-consuming, Missing information | Expand and share, Safe interactions |
| Musical Bob | Experiencing music, Learning | Storytelling, Authenticity | Audio quality, Artists | VR lacks authenticity | Learn from artists |

## Dependencies

- F-029: Empathy map input format
- F-005: Output formatting
- F-004: Persona generation

## References

### Foundational Work

Boag, P. (2015). Adapting Empathy Maps for UX Design. *Boagworld*. https://boagworld.com/usability/adapting-empathy-maps-for-ux-design/

### Academic Application

Lycett, M., Cundle, M., Grasso, L., Meechao, K., & Reppel, A. (2025). Materialising Design Fictions: Exploring Music Memorabilia in a Metaverse Environment. *Information Systems Journal*, 35, 1662–1678. https://doi.org/10.1111/isj.12600 (see Table 1 for output format).

---

## Related Documentation

- [UC-009: Empathy Mapping](../../../../use-cases/briefs/UC-009-empathy-mapping.md)
- [F-029: Empathy Map Input Format](F-029-empathy-map-input-format.md)
- [F-005: Output Formatting](F-005-output-formatting.md)

