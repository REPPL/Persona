# UC-004: Compare Persona Variations

## Summary

User compares personas generated with different settings to choose the best representation.

## User Story

As a researcher, I want to compare personas generated with different settings, so I can choose the best representation for my needs.

## Trigger

CLI command: `persona compare <id1> <id2>`

## Priority

P1 (Important)

## Milestone

v0.3.0

## Preconditions

- Persona is installed and configured
- At least two personas have been generated
- Personas to compare exist in the system

## Success Criteria

- [ ] User can compare two personas side-by-side
- [ ] Attribute-level diff highlighting shows differences
- [ ] Similarity score calculated and displayed
- [ ] Comparison report can be exported
- [ ] Works across experiments and models

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-021 | Persona Comparison | Analysis |

## Related Use Cases

- [UC-001: Generate Personas](UC-001-generate-personas.md)
- [UC-005: Validate Personas](UC-005-validate-personas.md)

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.3.0 Milestone](../../development/roadmap/milestones/v0.3.0.md)
