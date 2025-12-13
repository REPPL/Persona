# ADR-0006: YAML-Based Configuration

## Status

Accepted

## Context

Configuration must be:
- Human-readable
- Editable without code changes
- Version controllable
- Self-documenting

## Decision

Use YAML for all configuration:
- Vendor configurations
- Model definitions
- Workflow definitions
- Experiment settings

## Consequences

**Positive:**
- Human-readable format
- Git-friendly
- Standard format, widely understood
- Comments allowed

**Negative:**
- Indentation sensitive
- Validation needed at runtime
- No executable logic

## Alternatives Considered

### JSON
**Description:** JavaScript Object Notation, widely used for configuration.
**Pros:** Native Python support, simpler parsing.
**Cons:** No comments, verbose (many quotes), poor human readability.
**Why Not Chosen:** Comments are essential for configuration documentation.

### TOML
**Description:** Tom's Obvious Minimal Language, used by pyproject.toml.
**Pros:** Simple syntax, good for flat configs.
**Cons:** Less expressive for nested structures, less common in LLM tools.
**Why Not Chosen:** YAML better suits our hierarchical configuration needs.

### Python Files
**Description:** Configuration as Python code (e.g., settings.py).
**Pros:** Executable logic, full Python expressiveness.
**Cons:** Security concerns, harder for non-developers to edit.
**Why Not Chosen:** Security risks, target users are researchers not developers.

### Environment Variables Only
**Description:** All configuration via environment variables.
**Pros:** 12-factor app pattern, secure for secrets.
**Cons:** Hard to represent complex structures, no comments.
**Why Not Chosen:** Only use for secrets (API keys); YAML for complex config.

## Implementation Note

Configuration validation via Pydantic with `extra="forbid"` ensures typos are caught at load time.

## Research Reference

See [R-006: YAML Configuration & Validation](../../research/R-006-yaml-configuration-validation.md) for comprehensive analysis.

---

## Related Documentation

- [System Design](../../planning/architecture/system-design.md)
