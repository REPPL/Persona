# ADR-0009: Timestamped Output Organisation

## Status

Accepted

## Context

Users run multiple generation sessions and need:
- Clear organisation
- Non-destructive runs
- Easy comparison
- Historical records

## Decision

Use timestamped output folders:
- Format: `YYYYMMDD_HHMMSS`
- Never overwrite previous outputs
- Self-documenting folder names
- Metadata links to source data

## Consequences

**Positive:**
- Never lose previous work
- Clear chronological order
- Easy to compare runs
- Simple cleanup

**Negative:**
- Disk space accumulates
- User must manage old outputs

---

## Related Documentation

- [F-005: Output Formatting](../../roadmap/features/planned/F-005-output-formatting.md)
