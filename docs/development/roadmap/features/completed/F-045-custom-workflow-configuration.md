# F-045: Custom Workflow Configuration

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-005 |
| **Milestone** | v0.5.0 |
| **Priority** | P1 |
| **Category** | Config |

## Problem Statement

Teams develop their own multi-step workflows optimised for their research methodology. A fixed set of workflows cannot meet diverse research approaches.

## Design Approach

- YAML-based workflow definitions
- Reference built-in or custom templates
- Per-step model selection
- Output chaining between steps
- Workflow sharing and versioning

### Custom Workflow Schema

```yaml
# ~/.persona/workflows/research-grade.yaml
id: research-grade
name: Research-Grade Persona Generation
description: Academic-quality personas with full evidence
steps:
  - name: extract
    template: custom/deep-extract.j2
    model: claude-opus-4-5-20251101
    output: themes

  - name: synthesise
    template: custom/evidence-synthesis.j2
    model: claude-opus-4-5-20251101
    input: themes
    output: draft_personas

  - name: validate
    template: builtin/validate-personas
    model: claude-sonnet-4-5-20250929
    input: draft_personas
    output: personas
```

## Implementation Tasks

- [ ] Design workflow configuration schema
- [ ] Create WorkflowLoader for custom YAML
- [ ] Implement step chaining logic
- [ ] Support template references (builtin/, custom/)
- [ ] Create `persona workflow create` command
- [ ] Add `persona workflow list` command
- [ ] Add `persona workflow run` command
- [ ] Validate workflow before execution
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Custom workflows execute correctly
- [ ] Steps chain outputs properly
- [ ] Per-step models respected
- [ ] Invalid workflows rejected
- [ ] Test coverage ≥ 80%

## Dependencies

- F-019: Multi-step workflows (v0.2.0)
- F-003: Prompt templating

---

## Related Documentation

- [Milestone v0.5.0](../../milestones/v0.5.0.md)
- [Configuration Reference](../../../reference/configuration-reference.md)

