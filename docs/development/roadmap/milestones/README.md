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
| [v1.1.0](v1.1.0.md) | Quality & API | 6 | v1.0.0 | ✅ Complete |
| [v1.2.0](v1.2.0.md) | Extensibility & TUI | 7 | v1.0.0 | ✅ Complete |
| [v1.3.0](v1.3.0.md) | Local Model Foundation | 2 | v1.2.0 | ✅ Complete |
| [v1.4.0](v1.4.0.md) | Quality & Data Generation | 2 | v1.3.0 | ✅ Complete |
| [v1.5.0](v1.5.0.md) | Hybrid Pipeline | 1 | v1.4.0 | ✅ Complete |
| [v1.6.0](v1.6.0.md) | Academic Validation | 2 | v1.5.0 | ✅ Complete |
| [v1.7.0](v1.7.0.md) | Research Compliance | 5 | v1.6.0 | ✅ Complete |
| [v1.8.0](v1.8.0.md) | Technical Debt | 0 | v1.7.0 | ✅ Complete |
| [v1.9.0](v1.9.0.md) | Experiment Infrastructure | 2 | v1.8.0 | ✅ Complete |

**Total: 119 complete features, 1 active feature (F-091)**

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
    v1.1.0 (Quality & API) ✅
        │
        ↓
    v1.2.0 (Extensibility & TUI) ✅
        │
        ↓
    v1.3.0 (Local Model Foundation) ✅
        │
        ↓
    v1.4.0 (Quality & Data Generation) ✅
        │
        ↓
    v1.5.0 (Hybrid Pipeline) ✅
        │
        ↓
    v1.6.0 (Academic Validation) ✅
        │
        ↓
    v1.7.0 (Research Compliance) ✅
        │
        ↓
    v1.8.0 (Technical Debt) ✅
        │
        ↓
    v1.9.0 (Experiment Infrastructure) ✅
```

## User Interface Roadmap

Terminal-first approach, with WebUI deferred until TUI is mature:

```
v0.1.0  ──────  CLI (Typer + Rich) ✅
                Primary command-line interface

v1.0.0  ──────  Interactive CLI (questionary)
                Arrow-key prompts, form-based config

v1.1.0  ──────  Quality Metrics + REST API (FastAPI)
                Quality scoring and HTTP access for integrations

v1.2.0  ──────  Plugin System + TUI Dashboard (Textual) ✅
                Extensible plugins and full-screen terminal monitoring

v1.3.0  ──────  Local Model Foundation ✅
                Native Ollama provider + PII detection

v1.4.0  ──────  Quality & Data Generation ✅
                LLM-as-judge evaluation + Synthetic data

v1.5.0  ──────  Hybrid Pipeline ✅
                Local/frontier cost-optimised generation

v1.6.0  ──────  Academic Validation ✅
                Shin et al. DIS 2024 metrics + Hallucination detection

v1.7.0  ──────  Research Compliance ✅
                Bias detection + Audit trails + Lexical diversity

v1.8.0  ──────  Technical Debt
                Refactoring + Code quality + Deprecation fixes

v1.9.0  ──────  Experiment Infrastructure
                Project management + Data lineage
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
