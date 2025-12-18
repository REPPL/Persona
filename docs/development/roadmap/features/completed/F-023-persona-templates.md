# F-023: Persona Templates

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-007 |
| **Milestone** | v0.5.0 |
| **Priority** | P2 |
| **Category** | Templates |

## Problem Statement

PersonaCraft research shows domain-specific templates improve persona quality. UX personas differ from marketing personas, which differ from academic research personas. Teams need to generate personas in their standard format.

## Design Approach

- Three-layer template hierarchy (system, user, experiment)
- Presets for common domains (UX, marketing, academic, product)
- Template creation wizard for custom formats
- Template sharing/export functionality
- Preview output before generation

## Implementation Tasks

- [ ] Design template schema and format
- [ ] Create system templates for common domains:
  - [ ] UX research template
  - [ ] Marketing persona template
  - [ ] Academic research template
  - [ ] Product development template
- [ ] Build template selection CLI (`--template <name>`)
- [ ] Implement template creation wizard
- [ ] Add template validation
- [ ] Create template preview command
- [ ] Implement template export/import
- [ ] Store user templates in config directory
- [ ] Write unit tests

## Success Criteria

- [ ] Domain templates produce appropriate output
- [ ] Custom templates work identically to system templates
- [ ] Templates shareable between users
- [ ] Preview accurately shows final format
- [ ] Template validation catches errors before generation
- [ ] Test coverage ≥ 80%

## Dependencies

- F-003: Prompt templating (Jinja2)
- F-004: Persona generation
- F-005: Output formatting

---

## Related Documentation

- [UC-007: Customise Persona Format](../../../../use-cases/briefs/UC-007-custom-format.md)
- [F-003: Prompt Templating](F-003-prompt-templating.md)
- [R-008: Template-Driven Architecture](../../../../explanation/template-architecture.md)
