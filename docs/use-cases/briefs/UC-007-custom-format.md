# UC-007: Customise Persona Format

## Summary

User generates personas in a custom format to match team standards.

## User Story

As a UX designer, I want to generate personas in my team's standard format, so they integrate with our existing workflow.

## Trigger

CLI command: `persona generate --template <name>`

## Priority

P2 (Nice to have)

## Milestone

v0.5.0

## Status

✅ **Implemented** (v1.7.5)

## Preconditions

- Persona is installed and configured
- API key configured for LLM provider
- Data file/folder exists at specified path

## Success Criteria

- [x] User can select from template library
- [x] Custom template creation supported
- [x] Templates shareable/exportable
- [x] Domain-specific defaults available (UX, marketing, product)
- [x] Template validation before use
- [x] Preview template output before generation

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-023 | Persona Templates | Templates |

## Related Use Cases

- [UC-001: Generate Personas](UC-001-generate-personas.md)
- [UC-002: Manage Experiments](UC-002-manage-experiments.md)

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.5.0 Milestone](../../development/roadmap/milestones/v0.5.0.md)
