# UC-004: Compare Persona Variations

## Summary

User compares personas generated with different settings to choose the best representation.

## User Story

As a researcher, I want to compare personas generated with different settings, so I can choose the best representation for my needs.

## Trigger

CLI command: `persona compare <path>`

Where `<path>` is a directory containing persona JSON files, or a specific persona JSON file. Optional flags allow comparing specific personas within a collection using `--persona-a` and `--persona-b`.

## Priority

P1 (Important)

## Milestone

v0.3.0

## Status

✅ **Implemented** (v1.7.5)

## Preconditions

- Persona is installed and configured
- At least two personas have been generated
- Personas to compare exist in the system

## Success Criteria

- [x] User can compare two personas side-by-side
- [x] Attribute-level diff highlighting shows differences
- [x] Similarity score calculated and displayed
- [x] Comparison report can be exported
- [x] Works across experiments and models

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
