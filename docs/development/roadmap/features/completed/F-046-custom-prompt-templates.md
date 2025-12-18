# F-046: Custom Prompt Templates

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-005 |
| **Milestone** | v0.5.0 |
| **Priority** | P1 |
| **Category** | Config |

## Problem Statement

Different research domains require different prompting approaches. Marketing personas need different prompts than healthcare or enterprise software. Users need to create and share custom templates.

## Design Approach

- User template directory (~/.persona/templates/)
- Template inheritance from built-ins
- Variable validation and documentation
- Template testing before use
- Template sharing via export/import

### Template Structure

```jinja2
{# ~/.persona/templates/healthcare-personas.j2 #}
{% extends "builtin/base-generation.j2" %}

{% block system_context %}
You are an expert healthcare UX researcher specialising in patient experience.
{% endblock %}

{% block domain_requirements %}
- Consider healthcare literacy levels
- Include accessibility requirements
- Note privacy sensitivity
{% endblock %}
```

## Implementation Tasks

- [ ] Create user template directory structure
- [ ] Implement template inheritance
- [ ] Add template variable validation
- [ ] Create `persona template create` command
- [ ] Add `persona template test` command
- [ ] Add `persona template export` command
- [ ] Add `persona template import` command
- [ ] Document template development
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Custom templates override built-ins
- [ ] Inheritance works correctly
- [ ] Variables validated before use
- [ ] Export/import enables sharing
- [ ] Test coverage ≥ 80%

## Dependencies

- F-003: Prompt templating

---

## Related Documentation

- [Milestone v0.5.0](../../milestones/v0.5.0.md)
- [Configuration Reference](../../../../reference/configuration-reference.md)
