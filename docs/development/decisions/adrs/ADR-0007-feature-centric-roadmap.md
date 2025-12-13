# ADR-0007: Feature-Centric Roadmap

## Status

Accepted

## Context

Version-centric roadmaps cause:
- File explosion (16+ files per version series)
- Duplicate content across versions
- Maintenance burden
- Feature specifications coupled to release schedule

## Decision

Use feature-centric roadmaps:
- Features are primary unit of work
- Versions are bundles of features
- Status tracked by folder location
- Features stable even when schedules change

```
roadmap/
├── features/
│   ├── active/
│   ├── planned/
│   └── completed/
└── milestones/
    └── v0.X.md
```

## Consequences

**Positive:**
- Features stable across schedule changes
- No file explosion
- Clear single source of truth
- Milestone docs reference, not duplicate

**Negative:**
- Different from traditional roadmaps
- Requires folder moves for status changes

---

## Related Documentation

- [Roadmap Dashboard](../../roadmap/README.md)
- [Features Index](../../roadmap/features/)
