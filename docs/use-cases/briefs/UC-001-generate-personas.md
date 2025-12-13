# UC-001: Generate Personas from Data

## Summary

User generates realistic personas from qualitative research data using LLM analysis.

## User Story

As a UX researcher, I want to transform my interview/survey data into detailed personas, so that I can better understand and communicate user needs.

## Trigger

CLI command: `persona generate --from <source>`

## Priority

P0 (Critical)

## Milestone

v0.1.0

## Preconditions

- Persona is installed and configured
- API key for at least one LLM provider configured
- Data file/folder exists at specified path
- Supported format (CSV, JSON, TXT, Markdown, YAML)

## Success Criteria

- [ ] User can generate personas from a single file
- [ ] User can generate personas from an experiment folder
- [ ] Cost estimation shown before generation proceeds
- [ ] Progress feedback shown during generation
- [ ] Output includes structured personas (JSON + Markdown)
- [ ] Generation metadata saved with output

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-001 | Multi-format data loading | Data |
| F-002 | Data format normalisation | Data |
| F-003 | Multi-provider LLM support | LLM |
| F-004 | Provider interface abstraction | LLM |
| F-005 | Reusable prompt templates | Prompts |
| F-006 | Single-step workflow | Workflow |
| F-007 | Basic persona extraction | Generation |
| F-008 | Structured JSON output | Output |
| F-009 | Timestamped output folders | Output |
| F-013 | Cost estimation before generation | Cost |
| F-014 | Model-specific pricing | Cost |

## Related Use Cases

- [UC-002: Manage Experiments](UC-002-manage-experiments.md)
- [UC-003: View Status](UC-003-view-status.md)

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.1.0 Milestone](../../development/roadmap/milestones/v0.1.0.md)
