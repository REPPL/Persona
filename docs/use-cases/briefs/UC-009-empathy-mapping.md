# UC-009: Generate Personas from Empathy Mapping Workshops

## Summary

User generates personas from co-creation workshop outputs (empathy maps with post-it notes).

## User Story

As a UX researcher, I want to generate personas from co-creation workshop outputs (empathy maps with post-it notes), so I can synthesise messy qualitative data into structured personas.

## Trigger

CLI command: `persona generate --from workshop-data.yaml --format empathy-map`

## Priority

P1 (Important)

## Milestone

v0.2.0

## Background

The Boag empathy mapping method structures user insights around five dimensions:

1. **Tasks** - Activities to complete
2. **Feelings** - Priorities about experience
3. **Influences** - People, things, places
4. **Pain Points** - What they're trying to overcome
5. **Goals** - What they're trying to achieve

This approach is validated in academic research (Lycett et al. 2025, Information Systems Journal) and is widely used in UX practice. Workshop data is inherently messy - post-it notes clustered on whiteboards, transcribed quotes, and freeform observations.

## Preconditions

- Persona is installed and configured
- API key configured for LLM provider
- Workshop data structured as YAML/JSON with empathy map categories
- Supported format: tasks, feelings, influences, pain_points, goals sections

## Input Format Example

```yaml
# Empathy map workshop data
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
      - "Access to the 'history' of items"
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

## Output Format

Structured table (following Lycett et al. 2025, Table 1):

| Persona | Tasks | Feelings | Influences | Pain Points | Goals |
|---------|-------|----------|------------|-------------|-------|
| Superfan Alice | Expanding collection... | Easy to navigate... | Community... | Time-consuming... | Expand and share... |
| Musical Bob | Experiencing music... | Storytelling... | Audio quality... | VR lacks authenticity... | Learn from artists... |

## Success Criteria

- [ ] Accepts empathy map structured YAML/JSON input
- [ ] Handles messy, freeform text within categories
- [ ] Generates distinct personas from clustered data
- [ ] Outputs in table format suitable for stakeholder presentations
- [ ] Shows which input data points map to which persona attributes
- [ ] Optional: Accept workshop photos and extract text via vision LLM

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-029 | Empathy Map Input Format | Data |
| F-030 | Empathy Map Table Output | Output |
| F-031 | Workshop Data Import | Data |

## Related Use Cases

- [UC-001: Generate Personas](UC-001-generate-personas.md)
- [UC-005: Validate Personas](UC-005-validate-personas.md)
- [UC-007: Custom Format](UC-007-custom-format.md)

## Academic Reference

Lycett, M., Cundle, M., Grasso, L., Meechao, K., & Reppel, A. (2025). Materialising Design Fictions: Exploring Music Memorabilia in a Metaverse Environment. *Information Systems Journal*, 35, 1662–1678. https://doi.org/10.1111/isj.12600

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.2.0 Milestone](../../development/roadmap/milestones/v0.2.0.md)
