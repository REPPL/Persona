# R-010: MVP Architecture Pattern

Research into Model-View-Presenter (MVP) architecture pattern for Persona's codebase organisation.

## Executive Summary

Model-View-Presenter (MVP) is a UI architectural pattern that provides clean separation of concerns between business logic (Model), presentation (View), and coordination (Presenter). PersonaZero successfully employed this pattern. Analysis of Persona's existing architecture shows it already embodies MVP principles through its planned structure, making a formal ADR unnecessary.

**Key Finding:** Persona's existing separation between `persona/core/` (Model), `persona/cli/` (View), and command handlers (Presenter) already follows MVP principles.

**Recommendation:** Document MVP pattern in system-design.md as a design guideline rather than creating a formal ADR. The pattern is an implementation detail, not an architectural decision requiring formal tracking.

---

## Current State of the Art

### MVP Pattern Fundamentals

Model-View-Presenter (MVP) is a UI architectural pattern derived from MVC:

| Component | Responsibility | In Persona Context |
|-----------|---------------|-------------------|
| **Model** | Business logic, data | LLM providers, data loaders, persona generation |
| **View** | UI presentation | CLI output (Rich), file writing |
| **Presenter** | Coordination | Command handlers, workflow orchestration |

**Key Principle**: The View is passive - it knows nothing about the Model. All logic flows through the Presenter.

### Benefits for CLI Applications

From Python app development best practices:

> "MVP allows for different user interfaces to be used with the same underlying functionality. For example, if we wanted to switch from a graphical user interface to a command-line interface, we could do so without affecting the underlying functionality."

**For Persona:**
- Same generation logic usable from CLI, Python API, or future web UI
- Easier testing (mock the View, test Presenter logic)
- Clear boundaries for contributors

### Clean Architecture for LLM Applications

Anthropic's guidance on building agents emphasises:

> "The most successful implementations use simple, composable patterns rather than complex frameworks."

**LLM-Specific Patterns:**
1. **ReWOO**: Separate Planner, Worker, Solver
2. **ReAct**: Interleaved reasoning and actions
3. **Plan-and-Execute**: Planning before implementation

These patterns complement MVP by defining how the Model component orchestrates LLM calls.

### PersonaZero's MVP Implementation

PersonaZero documented its MVP implementation:

> "The system employs the MVP pattern to separate concerns with Models handling business logic, Views managing UI implementations, and Presenters managing shared presentation logic."

**File Structure:**
```
src/
├── models/           # Business logic
│   ├── llm_provider.py
│   ├── data_loader.py
│   └── persona_generator.py
├── views/            # UI implementations
│   ├── cli_view.py
│   └── file_view.py
├── presenters/       # Coordination
│   └── generation_presenter.py
└── persona_automation.py  # Entry point
```

---

## Persona's Current Architecture

### Existing Structure

Persona's planned architecture (from system-design.md and ADRs) already embodies separation of concerns:

```
persona/
├── core/             # Model layer
│   ├── data/         # Data loading and normalisation
│   ├── llm/          # LLM provider abstraction
│   ├── generation/   # Persona generation logic
│   └── templates/    # Prompt templates
├── cli/              # View + Presenter layer
│   ├── commands/     # CLI commands (presenters)
│   ├── views/        # Rich output formatting (views)
│   └── app.py        # Typer application
└── utils/            # Shared utilities
```

### Component Mapping

| Layer | Existing Pattern | MVP Equivalent |
|-------|-----------------|----------------|
| `persona/core/` | Data loaders, LLM abstraction, generation | Model |
| `persona/cli/commands/` | Typer commands, workflow orchestration | Presenter |
| `persona/cli/views/` | Rich console output, formatters | View |
| Templates | Jinja2 prompts | Shared by Model |

### Gap Analysis

**Current State:**
- ✓ Core business logic in `persona/core/`
- ✓ CLI structure in `persona/cli/`
- ✓ Clear separation planned in ADRs

**Improvement Opportunity:**
- Separate Presenter from View more explicitly in CLI layer
- Enable testing of command logic without Rich UI
- Allow Python API to reuse Presenter

---

## Recommendation

### No ADR Required

**Rationale:**
1. MVP is an implementation pattern, not a new feature decision
2. Existing ADR-0002 (Provider Abstraction) and ADR-0003 (Experiment-Centric) already establish separation of concerns
3. The pattern can be documented in `docs/development/planning/architecture/` without an ADR
4. Implementation details don't warrant architectural decision record

### Document in System Design

Update `docs/development/planning/architecture/system-design.md` to include:

```markdown
## Architecture Pattern: MVP

Persona follows the Model-View-Presenter (MVP) pattern:

### Model Layer (`persona/core/`)
- Data loading and normalisation
- LLM provider abstraction
- Persona generation logic
- Prompt template management

### Presenter Layer (`persona/cli/commands/`)
- Command handlers that orchestrate workflows
- Input validation and parameter processing
- Error handling and user feedback coordination

### View Layer (`persona/cli/views/`)
- Rich console output formatting
- File writing and output organisation
- Progress indicators and status displays

### Benefits
- Testable: Mock Views to test Presenter logic
- Extensible: Add new UIs without changing core logic
- Maintainable: Clear boundaries for contributors
```

### Implementation Guidelines

When implementing new features:

1. **Model Changes**: Add to `persona/core/`
   - Pure business logic
   - No Rich/Typer imports
   - Fully testable with unit tests

2. **Presenter Changes**: Add to `persona/cli/commands/`
   - Orchestration logic
   - Import from core, not from views
   - Can be tested with mock views

3. **View Changes**: Add to `persona/cli/views/`
   - Output formatting only
   - Rich-specific code
   - Minimal logic

---

## Sources

### Pattern Documentation

- Python MVP Documentation. https://python-app-dev.readthedocs.io/en/stable/internals/mvp/
- Mantid Project MVP Design. https://developer.mantidproject.org/MVPDesign.html
- Clean Architecture by Uncle Bob. https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- MVP Pattern Overview. https://en.wikipedia.org/wiki/Model–view–presenter

### LLM Architecture

- Anthropic: Building Effective Agents. https://www.anthropic.com/research/building-effective-agents

---

## Related Documentation

- [System Design](../planning/architecture/system-design.md)
- [ADR-0002: Provider Abstraction](../decisions/adrs/ADR-0002-provider-abstraction.md)
- [ADR-0003: Experiment-Centric Architecture](../decisions/adrs/ADR-0003-experiment-centric-architecture.md)

