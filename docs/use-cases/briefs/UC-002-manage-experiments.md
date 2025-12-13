# UC-002: Manage Experiments

## Summary

User organises persona generation work into experiments for reproducibility.

## User Story

As a researcher, I want to organise my persona generation runs into experiments, so that I can compare results and maintain reproducibility.

## Trigger

CLI commands:
- `persona create experiment`
- `persona list experiments`
- `persona show experiment <name>`
- `persona delete experiment <name>`

## Priority

P0 (Critical)

## Milestone

v0.1.0

## Preconditions

- Persona is installed

## Success Criteria

- [ ] User can create a new experiment interactively
- [ ] User can list all existing experiments
- [ ] User can view experiment details
- [ ] User can delete experiments with confirmation
- [ ] Experiment configuration persisted (YAML)
- [ ] Output organised by experiment and timestamp

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-010 | Create/list/show/delete experiments | Experiments |
| F-011 | Experiment configuration (YAML) | Experiments |
| F-012 | Experiment directory structure | Experiments |
| F-015 | CLI core commands | CLI |
| F-016 | Interactive Rich UI | CLI |

## Related Use Cases

- [UC-001: Generate Personas](UC-001-generate-personas.md)
- [UC-003: View Status](UC-003-view-status.md)

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.1.0 Milestone](../../development/roadmap/milestones/v0.1.0.md)
