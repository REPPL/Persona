# UC-005: Validate Generated Personas

## Summary

User validates that generated personas accurately reflect source data.

## User Story

As a researcher, I want to validate that generated personas accurately reflect my source data, so I can trust them for decision-making.

## Trigger

CLI command: `persona validate <id>`

## Priority

P1 (Important)

## Milestone

v0.2.0

## Preconditions

- Persona is installed and configured
- At least one persona has been generated
- Source data used for generation is accessible

## Success Criteria

- [ ] Evidence coverage score calculated (% of persona attributes backed by data)
- [ ] Gap analysis identifies unsupported claims
- [ ] Source citations linked to persona attributes
- [ ] Validation report exportable (JSON, Markdown)
- [ ] Hallucinated content flagged for review

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-019 | Persona Validation | Validation |
| F-024 | Evidence Linking | Output |

## Related Use Cases

- [UC-001: Generate Personas](UC-001-generate-personas.md)
- [UC-004: Compare Variations](UC-004-compare-variations.md)

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.2.0 Milestone](../../development/roadmap/milestones/v0.2.0.md)
