# UC-006: Process Large Datasets

## Summary

User processes hundreds of interview transcripts efficiently for large-scale studies.

## User Story

As a research team lead, I want to process hundreds of interview transcripts efficiently, so I can generate personas from large-scale studies.

## Trigger

CLI command: `persona generate --batch <folder>`

## Priority

P0 (Critical)

## Milestone

v0.7.0

## Preconditions

- Persona is installed and configured
- API key configured for LLM provider
- Data folder contains multiple valid input files
- Sufficient API quota for batch processing

## Success Criteria

- [ ] Parallel processing with visual progress bar
- [ ] Combined cost estimation shown before processing
- [ ] User confirmation required before starting batch
- [ ] Resumable processing on failure
- [ ] Consolidated output with per-file attribution
- [ ] Rate limiting handled gracefully

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-020 | Batch Data Processing | Data |

## Related Use Cases

- [UC-001: Generate Personas](UC-001-generate-personas.md)
- [UC-002: Manage Experiments](UC-002-manage-experiments.md)

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.7.0 Milestone](../../development/roadmap/milestones/v0.7.0.md)
