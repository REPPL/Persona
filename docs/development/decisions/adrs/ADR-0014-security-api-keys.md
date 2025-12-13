# ADR-0014: Security-First API Key Handling

## Status

Accepted

## Context

API keys are sensitive:
- Must never be exposed in logs
- Must never be in output files
- Must never be in error messages
- Must support rotation

## Decision

Security-first API key handling (v0.6.0):
- Keys from environment variables only
- Automatic masking in all output
- Pattern detection for accidental exposure
- Key rotation on authentication failure

## Consequences

**Positive:**
- Keys never exposed
- Automatic protection
- Rotation handles temporary issues
- Security best practices

**Negative:**
- More complex key management
- Environment variable dependency
- Masking may obscure debugging

---

## Related Documentation

- [v0.6.0 Milestone](../../roadmap/milestones/v0.6.0.md)
