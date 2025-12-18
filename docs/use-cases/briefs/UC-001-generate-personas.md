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

## Status

✅ **Implemented** (v1.7.5)

## Preconditions

- Persona is installed and configured
- API key for at least one LLM provider configured
- Data file/folder exists at specified path
- Supported format (CSV, JSON, TXT, Markdown, YAML)

## Success Criteria

- [x] User can generate personas from a single file
- [x] User can generate personas from an experiment folder
- [x] Cost estimation shown before generation proceeds
- [x] Progress feedback shown during generation
- [x] Output includes structured personas (JSON + Markdown)
- [x] Generation metadata saved with output

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-001 | Multi-format data loading | Data |
| F-002 | LLM provider abstraction | LLM |
| F-003 | Prompt templating (Jinja2) | Prompts |
| F-004 | Persona generation pipeline | Generation |
| F-005 | Output formatting | Output |
| F-007 | Cost estimation | Cost |
| F-010 | Data format normalisation | Data |
| F-011 | Multi-provider LLM support | LLM |
| F-013 | Timestamped output folders | Output |
| F-014 | Model-specific pricing | Cost |
| F-017 | Single-step workflow | Workflow |

## Related Use Cases

- [UC-002: Manage Experiments](UC-002-manage-experiments.md)
- [UC-003: View Status](UC-003-view-status.md)

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.1.0 Milestone](../../development/roadmap/milestones/v0.1.0.md)
