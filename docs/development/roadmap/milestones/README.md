# Milestones

Release planning and milestone documentation.

## Milestone Overview

| Version | Theme | Features | Dependencies | Status |
|---------|-------|----------|--------------|--------|
| [v0.1.0](v0.1.0.md) | Foundation | 19 | None | ✅ Complete |
| [v0.2.0](v0.2.0.md) | Validation & Data | 6 | v0.1.0 | ✅ Complete |
| [v0.3.0](v0.3.0.md) | Analysis & Variation | 5 | v0.1.0 | ✅ Complete |
| [v0.4.0](v0.4.0.md) | Advanced Output | 7 | v0.1.0 | ✅ Complete |
| [v0.5.0](v0.5.0.md) | Extensibility | 8 | v0.1.0 | ✅ Complete |
| [v0.6.0](v0.6.0.md) | Security | 10 | v0.1.0 | ✅ Complete |
| [v0.7.0](v0.7.0.md) | Batch Processing | 9 | v0.1.0 | ✅ Complete |
| [v0.8.0](v0.8.0.md) | Multi-Model | 7 | v0.1.0 | ✅ Complete |
| [v0.9.0](v0.9.0.md) | Logging | 6 | v0.1.0 | ✅ Complete |
| [v1.0.0](v1.0.0.md) | Production | 12 | All above | ✅ Complete |
| [v1.1.0](v1.1.0.md) | API & Integrations | 5 | v1.0.0 | 📋 Planned |
| [v1.2.0](v1.2.0.md) | TUI Dashboard | 6 | v1.1.0 | 🔮 Future |

**Total: 92 complete features, 11 planned features**

## Dependency Graph

```
v0.1.0 (Foundation) ✅
├─→ v0.2.0 (Validation & Data) ✅
├─→ v0.3.0 (Analysis & Variation) ✅
├─→ v0.4.0 (Output) ✅
├─→ v0.5.0 (Extensibility) ✅
├─→ v0.6.0 (Security) ✅
├─→ v0.7.0 (Batch) ✅
├─→ v0.8.0 (Multi-Model) ✅
└─→ v0.9.0 (Logging) ✅
        │
        ↓
    v1.0.0 (Production) ✅
        │
        ↓
    v1.1.0 (API & Integrations) 📋
        │
        ↓
    v1.2.0 (TUI Dashboard) 🔮
        │
        ↓
    v1.3.0+ (Future)
```

## User Interface Roadmap

Terminal-first approach, with WebUI deferred until TUI is mature:

```
v0.1.0  ──────  CLI (Typer + Rich) ✅
                Primary command-line interface

v1.0.0  ──────  Interactive CLI (questionary)
                Arrow-key prompts, form-based config

v1.1.0  ──────  REST API (FastAPI)
                HTTP access for integrations

v1.2.0  ──────  TUI Dashboard (Textual)
                Full-screen terminal monitoring

v1.3.0+ ──────  WebUI (TBD)
                Browser interface (not prioritised)
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
