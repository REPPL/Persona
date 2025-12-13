# ADR-0013: Formatter Registry Pattern

## Status

Accepted

## Context

Different users need different output formats:
- JSON for developers
- Markdown for documentation
- CSV for spreadsheets
- LaTeX for academic papers

## Decision

Use formatter registry pattern (v0.4.0):
- Base formatter interface
- Registry for format types
- Pluggable custom formatters
- Configuration-driven selection

## Consequences

**Positive:**
- Easy to add new formats
- User-extensible
- Consistent interface
- Configuration-driven

**Negative:**
- More complex architecture
- Must maintain multiple formatters

---

## Related Documentation

- [v0.4.0 Milestone](../../roadmap/milestones/v0.4.0.md)
