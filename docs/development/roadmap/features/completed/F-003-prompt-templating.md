# F-003: Prompt Templating

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v0.1.0 |
| **Priority** | P0 |
| **Category** | Prompts |

## Problem Statement

Persona generation requires flexible prompts that can be customised for different use cases. Users need control over prompt content without coding.

## Design Approach

- Jinja2 template engine
- YAML-based workflow definitions
- Variable injection (user_data, number_of_personas)
- Default templates for common scenarios

## Implementation Tasks

- [ ] Create PromptTemplate class
- [ ] Implement Jinja2 rendering
- [ ] Define workflow schema
- [ ] Create default workflow templates:
  - [ ] Basic single-step
  - [ ] Research-oriented
- [ ] Add template validation
- [ ] Write unit tests

## Success Criteria

- [ ] Templates render with variable injection
- [ ] Workflows load from YAML
- [ ] Invalid templates rejected with clear errors
- [ ] At least 2 default workflows available
- [ ] Test coverage ≥ 80%

## Dependencies

- Jinja2 for templating
- PyYAML for configuration

---

## Related Documentation

- [UC-001: Generate Personas](../../../../use-cases/briefs/UC-001-generate-personas.md)
- [ADR-0004: Jinja2 Templating](../../../decisions/adrs/ADR-0004-jinja2-templating.md)
