# ADR-0004: Jinja2 Prompt Templating

## Status

Accepted

## Context

Persona generation requires:
- Customisable prompts
- Variable injection (data, persona count)
- Reusable template components
- No coding for customisation

## Decision

Use Jinja2 for prompt templating:
- Industry-standard templating
- Rich syntax (loops, conditionals, filters)
- Template inheritance for composition
- YAML workflow definitions reference templates

## Consequences

**Positive:**
- Powerful customisation without code
- Familiar to Python developers
- Template inheritance for DRY
- Well-documented, mature library

**Negative:**
- Learning curve for complex templates
- Debugging can be challenging

## Alternatives Considered

### Banks Library
**Description:** LLM-focused prompt language built on Jinja2, with metadata and versioning.
**Pros:** First-class prompt versioning, LLM-specific features.
**Cons:** Additional dependency, smaller community.
**Why Not Chosen:** Native Jinja2 sufficient for v0.1.0; consider Banks for v0.5.0+.

### LangChain PromptTemplate
**Description:** Prompt templating integrated with LangChain framework.
**Pros:** Integrated with broader LangChain ecosystem.
**Cons:** Heavy dependency, framework lock-in.
**Why Not Chosen:** We don't use LangChain; pure Jinja2 preferred.

### Python f-strings
**Description:** Native Python string formatting.
**Pros:** No dependencies, simple syntax.
**Cons:** No template inheritance, no reusable components, embedded in code.
**Why Not Chosen:** Doesn't support external prompt storage or complex templating.

### String.Template
**Description:** Python standard library templating.
**Pros:** No dependencies.
**Cons:** Very limited syntax, no conditionals or loops.
**Why Not Chosen:** Insufficient for persona generation prompts.

## Research Reference

See [R-007: Prompt Templating](../../research/R-007-prompt-templating.md) for comprehensive analysis.

---

## Related Documentation

- [F-003: Prompt Templating](../../roadmap/features/planned/F-003-prompt-templating.md)
