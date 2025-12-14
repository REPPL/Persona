# ADR-0008: Structured JSON Output

## Status

Accepted

## Context

Generated personas need to be:
- Programmatically accessible
- Human readable
- Self-documenting
- Suitable for further analysis

## Decision

Output structured JSON alongside Markdown:
- JSON for programmatic access
- Markdown for human reading
- Metadata captures generation context
- Both formats always generated

## Consequences

**Positive:**
- Easy integration with other tools
- Human and machine readable
- Self-documenting metadata
- Standard format

**Negative:**
- Larger output size
- Must maintain both formats

## Alternatives Considered

### Instructor Library (Recommended Implementation)
**Description:** Pydantic-based structured output extraction for LLMs.
**Pros:** 3M+ downloads, 15+ providers, automatic retries, type-safe.
**Cons:** Additional dependency.
**Decision:** Use as implementation layer for reliable JSON extraction.

### Native Provider Structured Outputs
**Description:** Use OpenAI/Anthropic/Gemini native structured output APIs.
**Pros:** Provider-optimised, server-side enforcement.
**Cons:** Provider-specific code, varying maturity levels.
**Why Not Chosen:** Instructor provides unified interface with fallbacks.

### JSON Mode Only
**Description:** Use provider JSON mode without schema enforcement.
**Pros:** Simpler implementation.
**Cons:** No schema validation, may get invalid structures.
**Why Not Chosen:** Schema enforcement essential for reliable persona extraction.

### Manual Parsing
**Description:** Parse JSON from free-text LLM responses.
**Pros:** No special dependencies.
**Cons:** Fragile, frequent parsing failures, high maintenance.
**Why Not Chosen:** Unreliable for production use.

## Research Reference

See [R-001: Structured LLM Output](../../research/R-001-structured-llm-output.md) for comprehensive analysis.

---

## Related Documentation

- [F-005: Output Formatting](../../roadmap/features/completed/F-005-output-formatting.md)
