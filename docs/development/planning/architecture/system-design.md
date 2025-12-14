# System Design

High-level architecture for Persona.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │       CLI       │  │       TUI       │  │      WebUI      │  │
│  │    (Typer)      │  │   (Textual)     │  │   (Future)      │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼────────────────────┼────────────────────┼───────────┘
            │                    │                    │
            └──────────────────┬─┴────────────────────┘
                               │
┌──────────────────────────────┼───────────────────────────────────┐
│                         Core Layer                               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    PersonaAutomation                        │ │
│  │  (Orchestrates data loading, LLM calls, output generation)  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                               │                                  │
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
┌──────────────────────────────┼───────────────────────────────────┐
│                      Configuration Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │   Vendors    │  │    Models    │  │      Workflows         │  │
│  │   (YAML)     │  │   (YAML)     │  │       (YAML)           │  │
│  └──────────────┘  └──────────────┘  └────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### User Interface Layer
- **CLI** - Primary interface using Typer + Rich
- **TUI** - Terminal UI for interactive exploration (v1.0.0)
- **WebUI** - Web interface (future)

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

## Architecture Pattern: MVP

Persona follows the Model-View-Presenter (MVP) pattern for clean separation of concerns:

### Model Layer (`persona/core/`)

Business logic with no UI dependencies:

- **Data Loading** - Load and normalise from CSV, JSON, Markdown, etc.
- **LLM Abstraction** - Provider-agnostic LLM interface
- **Generation Logic** - Persona synthesis algorithms
- **Template Management** - Jinja2 prompt templates

### Presenter Layer (`persona/cli/commands/`)

Coordination and workflow orchestration:

- **Command Handlers** - Orchestrate workflows for each CLI command
- **Input Validation** - Parameter processing and validation
- **Error Handling** - User feedback coordination

### View Layer (`persona/cli/views/`)

UI presentation with no business logic:

- **Rich Output** - Console formatting and tables
- **File Writing** - Output organisation and file creation
- **Progress Indicators** - Status displays and spinners

### MVP Benefits

| Benefit | Description |
|---------|-------------|
| **Testable** | Mock Views to test Presenter logic in isolation |
| **Extensible** | Add new UIs (TUI, WebUI) without changing core logic |
| **Maintainable** | Clear boundaries for contributors |
| **Reusable** | Python API can reuse Model and Presenter |

### Implementation Guidelines

When implementing new features:

1. **Model Changes**: Add to `persona/core/`
   - Pure business logic, no Rich/Typer imports
   - Fully testable with unit tests

2. **Presenter Changes**: Add to `persona/cli/commands/`
   - Import from core, not from views
   - Can be tested with mock views

3. **View Changes**: Add to `persona/cli/views/`
   - Output formatting only
   - Rich-specific code, minimal logic

See [R-010: MVP Architecture](../../research/R-010-mvp-architecture.md) for detailed research.

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
