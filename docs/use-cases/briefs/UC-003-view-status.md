# UC-003: View System Status

## Summary

User checks system health and configuration status.

## User Story

As a user, I want to verify my installation is working correctly, so that I can troubleshoot issues before running generation.

## Trigger

CLI command: `persona check`

## Priority

P1 (Important)

## Milestone

v0.1.0

## Status

✅ **Implemented** (v1.7.5)

## Preconditions

- Persona is installed

## Success Criteria

- [x] Shows configured providers and their status
- [x] Validates API key availability (without exposing keys)
- [x] Shows available models per provider
- [x] Indicates any configuration issues
- [x] Clear pass/fail output
- [x] Suggestions for resolving issues

## Derives Features

| ID | Feature | Category |
|----|---------|----------|
| F-015 | CLI core commands | CLI |
| F-016 | Interactive Rich UI | CLI |
| F-017 | System check command | CLI |
| F-018 | Context-aware help | CLI |

## Related Use Cases

- [UC-001: Generate Personas](UC-001-generate-personas.md)
- [UC-002: Manage Experiments](UC-002-manage-experiments.md)

---

## Related Documentation

- [Feature Specifications](../../development/roadmap/features/)
- [v0.1.0 Milestone](../../development/roadmap/milestones/v0.1.0.md)
