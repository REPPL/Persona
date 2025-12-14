# Use Case Briefs

This directory contains detailed use case specifications.

## Format

Each use case brief follows a standard template:

```markdown
# UC-XXX: [Title]

## Summary
[One-line description]

## User Story
As a [role], I want to [action], so that [benefit].

## Trigger
[What initiates this use case - typically a CLI command]

## Priority
[P0 | P1 | P2]

## Milestone
[Target version]

## Preconditions
- [What must be true before this use case can be executed]

## Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]

## Derives Features
- [F-XXX: Feature Name]

## Related Use Cases
- [UC-XXX: Related Use Case]
```

## Briefs in This Directory

### v0.1.0 - Foundation

| Brief | Use Case | Status |
|-------|----------|--------|
| [UC-001](UC-001-generate-personas.md) | Generate Personas | Planned |
| [UC-002](UC-002-manage-experiments.md) | Manage Experiments | Planned |
| [UC-003](UC-003-view-status.md) | View Status | Planned |
| [UC-008](UC-008-demo-mode.md) | Demo Without Real Data | Planned |

### v0.2.0 - Validation

| Brief | Use Case | Status |
|-------|----------|--------|
| [UC-005](UC-005-validate-personas.md) | Validate Generated Personas | Planned |
| [UC-009](UC-009-empathy-mapping.md) | Generate from Empathy Mapping | Planned |

### v0.3.0+ - Advanced

| Brief | Use Case | Status |
|-------|----------|--------|
| [UC-004](UC-004-compare-variations.md) | Compare Persona Variations | Planned |
| [UC-006](UC-006-large-datasets.md) | Process Large Datasets | Planned |
| [UC-007](UC-007-custom-format.md) | Customise Persona Format | Planned |

---

## Related Documentation

- [Use Cases Index](../README.md)
- [Feature Specifications](../../development/roadmap/features/)
