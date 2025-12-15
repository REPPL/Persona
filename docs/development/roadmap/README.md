# Roadmap Dashboard

Feature-centric roadmap for Persona development.

## Current Status

| Milestone | Theme | Features | Status |
|-----------|-------|----------|--------|
| v0.1.0 | Foundation | 21 | ✅ Complete |
| v0.2.0 | Validation & Data | 6 | ✅ Complete |
| v0.3.0 | Analysis & Variation | 5 | ✅ Complete |
| v0.4.0 | Advanced Output | 7 | ✅ Complete |
| v0.5.0 | Extensibility | 8 | ✅ Complete |
| v0.6.0 | Security | 9 | ✅ Complete |
| v0.7.0 | Batch Processing | 9 | ✅ Complete |
| v0.8.0 | Multi-Model | 7 | ✅ Complete |
| v0.9.0 | Logging | 6 | ✅ Complete |
| v1.0.0 | Production | 17 | 📋 Planned |
| v1.1.0 | API & Integrations | 4 | 📋 Planned |
| v1.2.0 | TUI Dashboard | 6 | 🔮 Future |

**Total: 76 complete features, 27 planned features**

## Roadmap Structure

```
roadmap/
├── README.md                 ← You are here
├── features/                 # Feature specifications
│   ├── active/               # Currently implementing
│   ├── planned/              # Queued for future
│   └── completed/            # Done
└── milestones/               # Release planning
    └── v0.X.0.md             # One file per version
```

## Feature-Centric Approach

Features are the primary unit of work. Versions/milestones are bundles of features shipped together.

- **Features** = discrete pieces of value (the work)
- **Milestones** = bundles of features shipped together (the delivery)

Status is tracked by folder location:
- `features/active/` → 🔄 In Progress
- `features/planned/` → 📋 Planned
- `features/completed/` → ✅ Done

---

## User Interface Layer

Multiple interfaces planned, with terminal-first approach:

| Interface | Framework | Version | Status |
|-----------|-----------|---------|--------|
| CLI | Typer + Rich | v0.1.0 | ✅ Complete |
| Interactive CLI | questionary | v1.0.0 | 📋 Planned |
| REST API | FastAPI | v1.1.0 | 📋 Planned |
| TUI Dashboard | Textual | v1.2.0 | 📋 Planned |
| WebUI | TBD | Future | ⏸️ Deferred |

**Strategy:**
- **CLI** — Primary interface for all functionality (complete)
- **Interactive CLI** — Arrow-key prompts and form-based configuration
- **REST API** — HTTP access for integrations and automation
- **TUI Dashboard** — Full-screen terminal monitoring (after CLI maturity)
- **WebUI** — Browser interface (not prioritised, TUI first)

---

## Related Documentation

- [Features Index](features/)
- [Milestones](milestones/)
- [Use Cases](../../use-cases/)
