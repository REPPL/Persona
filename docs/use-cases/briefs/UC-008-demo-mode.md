# UC-008: Demo Without Real Data

## Summary

User tries Persona without providing real data to evaluate the tool.

## User Story

As a new user, I want to try Persona without providing my own data, so I can evaluate the tool before committing.

## Trigger

CLI command: `persona demo`

## Priority

P2 (Nice to have)

## Milestone

v0.1.0

## Status

✅ **Implemented** (v1.7.5)

## Preconditions

- Persona is installed
- API key configured for at least one LLM provider

## Success Criteria

- [x] Generates synthetic interview data automatically
- [x] Runs full generation pipeline with sample data
- [x] Shows example output in terminal
- [x] Explains each step as it progresses
- [x] Displays cost incurred for demo run
- [x] Cleanup option for demo data

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-028 | Synthetic Data Generation | Demo |

## Related Use Cases

- [UC-001: Generate Personas](UC-001-generate-personas.md)
- [UC-003: View Status](UC-003-view-status.md)

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.1.0 Milestone](../../development/roadmap/milestones/v0.1.0.md)
