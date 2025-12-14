# Milestones

Release planning and milestone documentation.

## Milestone Overview

| Version | Theme | Features | Dependencies | Status |
|---------|-------|----------|--------------|--------|
| [v0.1.0](v0.1.0.md) | Foundation | 18 | None | Planned |
| [v0.2.0](v0.2.0.md) | Multi-Step Workflows | 9 | v0.1.0 | Planned |
| [v0.3.0](v0.3.0.md) | Multi-Variation | 8 | v0.2.0 | Planned |
| [v0.4.0](v0.4.0.md) | Advanced Output | 7 | v0.1.0 | Planned |
| [v0.5.0](v0.5.0.md) | Extensibility | 8 | v0.1.0 | Planned |
| [v0.6.0](v0.6.0.md) | Security | 8 | v0.1.0 | Planned |
| [v0.7.0](v0.7.0.md) | Batch Processing | 7 | v0.1.0 | Complete |
| [v0.8.0](v0.8.0.md) | Multi-Model | 7 | v0.2.0, v0.3.0 | Planned |
| [v0.9.0](v0.9.0.md) | Logging | 6 | v0.1.0 | Planned |
| [v1.0.0](v1.0.0.md) | Production | 12 | All above | Planned |
| [v1.1.0](v1.1.0.md) | API & Integrations | 4 | v1.0.0 | Planned |

**Total: 94 features across 11 milestones**

## Dependency Graph

```
v0.1.0 (Foundation)
├─→ v0.2.0 (Workflows)
│   ├─→ v0.3.0 (Variation)
│   │   └─→ v0.8.0 (Multi-Model) ←─┐
│   └────────────────────────────────┘
├─→ v0.4.0 (Output)
├─→ v0.5.0 (Extensibility)
├─→ v0.6.0 (Security)
├─→ v0.7.0 (Batch) ✓
└─→ v0.9.0 (Logging)
        │
        ↓
    v1.0.0 (Production)
        │
        ↓
    v1.1.0 (API & Integrations)
```

## Milestone Format

Each milestone document includes:
- **Goal** - What we want to achieve
- **Features** - What's included (links to feature specs)
- **Use Cases Addressed** - Which use cases this satisfies
- **Success Criteria** - How we know it's done
- **Non-Goals** - What's explicitly deferred

---

## Related Documentation

- [Features Index](../features/)
- [Roadmap Dashboard](../README.md)
