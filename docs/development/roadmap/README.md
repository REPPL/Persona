# Roadmap Dashboard

Feature-centric roadmap for Persona development.

## Current Status

| Milestone | Theme | Features | Status |
|-----------|-------|----------|--------|
| v0.1.0 | Foundation | 20 | ✅ Complete |
| v0.2.0 | Validation & Data | 6 | ✅ Complete |
| v0.3.0 | Analysis & Variation | 5 | ✅ Complete |
| v0.4.0 | Advanced Output | 7 | ✅ Complete |
| v0.5.0 | Extensibility | 8 | ✅ Complete |
| v0.6.0 | Security | 10 | ✅ Complete |
| v0.7.0 | Batch Processing | 9 | ✅ Complete |
| v0.8.0 | Multi-Model | 7 | ✅ Complete |
| v0.9.0 | Logging | 6 | ✅ Complete |
| v1.0.0 | Production | 14 | ✅ Complete |
| v1.1.0 | Quality & API | 6 | ✅ Complete |
| v1.2.0 | Extensibility & TUI | 7 | ✅ Complete |
| v1.3.0 | Local Model Foundation | 2 | ✅ Complete |
| v1.4.0 | Quality & Data Generation | 2 | ✅ Complete |
| v1.5.0 | Hybrid Pipeline | 1 | ✅ Complete |
| v1.6.0 | Academic Validation | 2 | 📋 Planned |
| v1.7.0 | Research Compliance | 5 | 📋 Planned |

**Total: 110 complete features, 7 planned features**

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
| Interactive CLI | questionary | v1.0.0 | ✅ Complete |
| Quality Metrics | Built-in | v1.1.0 | ✅ Complete |
| Plugin System | Entry Points | v1.2.0 | ✅ Complete |
| REST API | FastAPI | v1.1.0 | ✅ Complete |
| TUI Dashboard | Textual | v1.2.0 | ✅ Complete |
| WebUI | TBD | Future | ⏸️ Deferred |

**Strategy:**
- **CLI** — Primary interface for all functionality (complete)
- **Interactive CLI** — Arrow-key prompts and form-based configuration (complete)
- **Quality Metrics** — Persona quality scoring and analysis (complete)
- **Plugin System** — Entry point-based extension architecture (complete)
- **REST API** — HTTP access for integrations and automation (complete)
- **TUI Dashboard** — Full-screen terminal monitoring (complete)
- **WebUI** — Browser interface (not prioritised, TUI first)

---

## Related Documentation

- [Features Index](features/)
- [Milestones](milestones/)
- [Use Cases](../../use-cases/)
