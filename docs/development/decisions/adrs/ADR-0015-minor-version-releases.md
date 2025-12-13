# ADR-0015: Minor Version Releases Only

## Status

Accepted

## Context

Version tagging options:
- Alpha/beta pre-releases (v0.1.0-alpha.1)
- Minor version only (v0.1.0, v0.2.0)
- Continuous deployment

## Decision

Use minor version releases only:
- No alpha/beta pre-release tags
- v0.1.0-planning is the only exception
- Each milestone = minor version
- Bug fixes use patch versions

## Consequences

**Positive:**
- Simpler version history
- Clear milestone boundaries
- Less tag clutter
- Easier to communicate

**Negative:**
- No early feedback period
- Must be confident at release
- Bugs fixed in patch releases

---

## Related Documentation

- [Implementation Workflow](../../process/workflow.md)
