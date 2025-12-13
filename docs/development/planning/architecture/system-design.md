# System Design

High-level architecture for Persona.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │       CLI       │  │       TUI       │  │      WebUI      │  │
│  │    (Typer)      │  │   (Textual)     │  │   (Future)      │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼─────────────────────┼─────────────────────┼──────────┘
            │                     │                     │
            └──────────────────┬──┴─────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                         Core Layer                               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    PersonaAutomation                        │ │
│  │  (Orchestrates data loading, LLM calls, output generation)  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                               │                                   │
│  ┌────────────┐  ┌────────────┴────────────┐  ┌────────────────┐ │
│  │   Data     │  │       LLM Providers     │  │    Output      │ │
│  │  Loaders   │  │  ┌──────┬──────┬──────┐ │  │   Formatters   │ │
│  │            │  │  │OpenAI│Claude│Gemini│ │  │                │ │
│  └────────────┘  │  └──────┴──────┴──────┘ │  └────────────────┘ │
│                  └─────────────────────────┘                     │
│  ┌────────────┐  ┌─────────────────────────┐  ┌────────────────┐ │
│  │ Experiment │  │        Prompts          │  │     Cost       │ │
│  │  Manager   │  │       (Jinja2)          │  │   Estimator    │ │
│  └────────────┘  └─────────────────────────┘  └────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                      Configuration Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │   Vendors    │  │    Models    │  │      Workflows         │ │
│  │   (YAML)     │  │   (YAML)     │  │       (YAML)           │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### User Interface Layer
- **CLI** - Primary interface using Typer + Rich
- **TUI** - Terminal UI for interactive exploration (future)
- **WebUI** - Web interface (v1.0.0)

### Core Layer
- **PersonaAutomation** - Main orchestrator coordinating all components
- **Data Loaders** - Load and normalise data from various formats
- **LLM Providers** - Unified interface for AI providers
- **Output Formatters** - Generate JSON, Markdown, etc.
- **Experiment Manager** - Manage experiment lifecycle
- **Prompts** - Jinja2 template rendering
- **Cost Estimator** - Token counting and pricing

### Configuration Layer
- **Vendors** - API endpoints, authentication
- **Models** - Capabilities, pricing, limits
- **Workflows** - Prompt sequences, parameters

## Data Flow

```
Input Data                    Persona Output
    │                              ▲
    ▼                              │
┌─────────┐    ┌─────────┐    ┌─────────┐
│  Load   │───▶│ Process │───▶│ Format  │
│  Data   │    │  (LLM)  │    │ Output  │
└─────────┘    └─────────┘    └─────────┘
    │              │              │
    ▼              ▼              ▼
CSV, JSON,     OpenAI,        JSON,
TXT, MD...     Claude,        Markdown,
               Gemini         Tables...
```

## Key Design Decisions

| Decision | ADR | Rationale |
|----------|-----|-----------|
| Multi-provider architecture | ADR-0002 | User flexibility |
| Experiment-centric workflow | ADR-0003 | Reproducibility |
| Jinja2 templating | ADR-0004 | Powerful, familiar |
| Typer + Rich CLI | ADR-0005 | Best UX |
| YAML configuration | ADR-0006 | Human-readable |

---

## Related Documentation

- [Architecture Decisions](../../decisions/adrs/)
- [v0.1.0 Vision](../vision/v0.1-vision.md)
