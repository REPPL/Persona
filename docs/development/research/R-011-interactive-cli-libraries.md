# R-011: Interactive CLI Libraries

Research into Python libraries for interactive command-line interfaces with arrow-key navigation, form input, and autocomplete.

## Executive Summary

Persona's CLI needs interactive capabilities beyond basic argument parsing for guided workflows, configuration editing, and model selection. This research evaluates the current state of the art in Python interactive CLI libraries (December 2025).

**Key Finding:** questionary is built on top of prompt_toolkit, providing the same underlying capabilities with a simpler API better suited to our needs.

**Recommendation:** Use **questionary** for interactive prompts (ADR-0022). Reserve Textual for future dashboard/monitoring features.

---

## Current State of the Art (December 2025)

### Library Landscape

| Library | GitHub Stars | Latest Version | Best For | Complexity |
|---------|--------------|----------------|----------|------------|
| **[prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)** | 10.1k | 3.0.52 (Aug 2025) | Advanced REPL, full-screen apps | High |
| **[questionary](https://github.com/tmbo/questionary)** | 1.9k | 2.1.1 (Aug 2025) | Simple prompts, selections | Low |
| **[Textual](https://github.com/Textualize/textual)** | 26k+ | 0.87+ (2025) | Full TUI applications | Medium-High |
| **[inquirer3](https://github.com/magmax/python-inquirer)** | 0.5k | 3.x | Inquirer.js port | Low |
| **[bullet](https://github.com/bchao1/bullet)** | 3.6k | 2.2.0 | Simple menus | Very Low |

### Detailed Analysis

#### prompt_toolkit

**Repository:** https://github.com/prompt-toolkit/python-prompt-toolkit

**Overview:** Pure Python readline replacement powering ptpython, IPython, AWS CLI v2, and questionary itself.

**Features:**
- Multi-line editing with syntax highlighting
- Emacs and Vi key bindings
- Auto-suggestions (fish shell style)
- Mouse support
- Bracketed paste
- Full-screen layouts
- Completion systems (fuzzy, word, path)
- Custom key bindings

**Dependencies:** Only Pygments and wcwidth

**Example:**
```python
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

model_completer = WordCompleter(['claude-sonnet-4', 'gpt-4o', 'gemini-1.5-pro'])
result = prompt('Select model: ', completer=model_completer)
```

**Assessment:**
- **Pros:** Maximum flexibility, powers major tools, actively maintained
- **Cons:** Verbose for simple prompts, steep learning curve
- **Use Case:** Building REPL, custom shells, full-screen applications

#### questionary

**Repository:** https://github.com/tmbo/questionary

**Overview:** High-level interactive prompts built on prompt_toolkit. Used by ~18.5k projects.

**Features:**
- 8 prompt types: text, password, file path, confirmation, select, raw_select, checkbox, autocomplete
- Fluent API: `questionary.select(...).ask()`
- Form support for multi-field input
- Validation and transformation
- Keyboard shortcuts (1-9 for quick selection)
- Style customisation

**Dependencies:** prompt_toolkit (which brings Pygments, wcwidth)

**Example:**
```python
import questionary

# Arrow-key selection
model = questionary.select(
    "Select model:",
    choices=[
        questionary.Choice("Claude Sonnet 4 (recommended)", "claude-sonnet-4"),
        questionary.Choice("GPT-4o", "gpt-4o"),
        questionary.Choice("Gemini 1.5 Pro", "gemini-1.5-pro"),
    ],
    use_shortcuts=True,
).ask()

# Multi-field form
config = questionary.form(
    provider=questionary.select("Provider:", ["anthropic", "openai", "gemini"]),
    count=questionary.text("Persona count:", default="3"),
    format=questionary.select("Output format:", ["json", "markdown", "yaml"]),
).ask()

# File path with validation
data_file = questionary.path(
    "Data file:",
    validate=lambda p: Path(p).exists() or "File not found",
).ask()

# Checkbox (multi-select)
features = questionary.checkbox(
    "Enable features:",
    choices=["validation", "reasoning", "streaming"],
).ask()
```

**Assessment:**
- **Pros:** Simple API, right abstraction level, active maintenance
- **Cons:** Additional dependency, not for full-screen apps
- **Use Case:** Interactive wizards, configuration, selection menus

#### Textual

**Repository:** https://github.com/Textualize/textual

**Overview:** Modern TUI framework from the creators of Rich. CSS-like styling, reactive design.

**Features:**
- Full-screen applications
- Widget system (buttons, inputs, tables, trees)
- CSS-like styling with hot reload
- Async-first design
- Mouse support
- Built-in testing framework

**Dependencies:** Rich, typing_extensions

**Example:**
```python
from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer, DataTable

class PersonaApp(App):
    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Name", "Role")
        table.add_row("001", "Alex", "Developer")
```

**Assessment:**
- **Pros:** Beautiful UI, modern architecture, excellent docs
- **Cons:** Overkill for simple prompts, different paradigm
- **Use Case:** Dashboards, monitoring tools, complex TUIs

#### inquirer3

**Repository:** https://github.com/magmax/python-inquirer

**Overview:** Python port of the popular Inquirer.js library.

**Features:**
- Similar API to JavaScript version
- Basic prompt types (text, select, checkbox, confirm)
- Theme support

**Dependencies:** blessed, readchar

**Assessment:**
- **Pros:** Familiar to JavaScript developers
- **Cons:** Less actively maintained than questionary, fewer features
- **Use Case:** Simple prompts, JavaScript developer preference

#### bullet

**Repository:** https://github.com/bchao1/bullet

**Overview:** Minimal interactive prompts with arrow-key navigation.

**Features:**
- Basic select menus
- Checkbox prompts
- Minimal dependencies

**Assessment:**
- **Pros:** Very lightweight, simple
- **Cons:** Limited features, less maintained
- **Use Case:** Extremely simple menus only

---

## Comparison Matrix

| Criteria | prompt_toolkit | questionary | Textual | inquirer3 |
|----------|---------------|-------------|---------|-----------|
| **Arrow-key selection** | Via custom code | Built-in | Via widgets | Built-in |
| **Form input** | Via custom code | Built-in | Via widgets | Limited |
| **Autocomplete** | Built-in | Built-in | Via widgets | Limited |
| **Learning curve** | Steep | Low | Medium | Low |
| **Maintenance** | Excellent | Good | Excellent | Fair |
| **Rich compatibility** | Good | Good | Native | Unknown |
| **Dependency weight** | Light | Light (via pt) | Medium | Light |

---

## Gap Analysis: Persona Needs

**Current State:**
- Typer for CLI parsing (ADR-0005)
- Rich for output formatting
- No interactive prompt capability

**Requirements:**
1. **Model selection** - Arrow-key menu for provider/model choice
2. **Configuration editing** - Multi-field form input
3. **Batch selection** - Checkbox for file/operation selection
4. **File path input** - Autocomplete for data files
5. **Confirmation prompts** - Yes/no for destructive operations

**Gap Assessment:**

| Requirement | prompt_toolkit | questionary | Textual |
|-------------|---------------|-------------|---------|
| Model selection | Custom code | `select()` | Widget |
| Config forms | Custom code | `form()` | Widgets |
| Batch selection | Custom code | `checkbox()` | Widget |
| Path autocomplete | Built-in | `path()` | Custom |
| Confirmation | Custom code | `confirm()` | Dialog |

**Finding:** questionary provides the exact abstractions needed with minimal code.

---

## Recommendation

### Primary: questionary for Interactive Prompts

**Rationale:**
1. **Right abstraction level** - We need prompts, not full-screen apps
2. **Built on prompt_toolkit** - Same reliable foundation as AWS CLI v2
3. **Simple API** - Reduces code complexity
4. **Form support** - Multi-field configuration in single call
5. **Active maintenance** - v2.1.1 released August 2025
6. **Rich compatibility** - Works alongside our existing Rich output

### Secondary: Textual for Future Dashboard

**Rationale:**
1. Reserve for v1.2.0+ monitoring/dashboard features
2. Overkill for current interactive needs
3. Different paradigm (full-screen vs inline)

### Integration Pattern

```python
# src/persona/cli/interactive.py

import questionary
from rich.console import Console

console = Console()

def interactive_generate():
    """Interactive persona generation wizard."""
    # Provider selection
    provider = questionary.select(
        "Select LLM provider:",
        choices=[
            questionary.Choice("Anthropic (Claude)", "anthropic"),
            questionary.Choice("OpenAI (GPT)", "openai"),
            questionary.Choice("Google (Gemini)", "gemini"),
        ],
    ).ask()

    # Model selection based on provider
    models = get_models_for_provider(provider)
    model = questionary.select(
        "Select model:",
        choices=[questionary.Choice(m.display_name, m.id) for m in models],
    ).ask()

    # Configuration form
    config = questionary.form(
        count=questionary.text("Number of personas:", default="3"),
        format=questionary.select("Output format:", ["json", "markdown", "yaml"]),
        reasoning=questionary.confirm("Capture reasoning?", default=True),
    ).ask()

    # File selection with autocomplete
    data_path = questionary.path(
        "Data file or directory:",
        validate=lambda p: Path(p).exists() or "Path not found",
    ).ask()

    # Confirmation
    if questionary.confirm(f"Generate {config['count']} personas?").ask():
        # Proceed with generation
        ...
```

---

## Impact on Existing Decisions

### ADR-0005: Typer + Rich CLI Framework

**Extension:** Add questionary as third component of CLI stack.

```
CLI Stack:
├── Typer       - Command parsing, --help, validation
├── Rich        - Output formatting, progress, tables
└── questionary - Interactive prompts, wizards (NEW)
```

### New ADR-0022: Interactive CLI Library Selection

Documents the decision to use questionary (see ADR-0022).

### New Features

| Feature | Description | Milestone |
|---------|-------------|-----------|
| F-092 | `--interactive` / `-i` global flag | v1.0.0 |
| F-093 | TUI configuration editor | v1.0.0 |
| F-094 | Streaming output display | v1.0.0 |
| F-095 | Shell completions | v1.0.0 |

---

## Sources

### Libraries

- prompt_toolkit. https://github.com/prompt-toolkit/python-prompt-toolkit
- questionary. https://github.com/tmbo/questionary
- Textual. https://github.com/Textualize/textual
- inquirer3. https://github.com/magmax/python-inquirer
- bullet. https://github.com/bchao1/bullet

### Documentation

- prompt_toolkit docs. https://python-prompt-toolkit.readthedocs.io/
- questionary docs. https://questionary.readthedocs.io/
- Textual docs. https://textual.textualize.io/

---

## Related Documentation

- [ADR-0005: Typer + Rich CLI Framework](../decisions/adrs/ADR-0005-cli-framework.md)
- [ADR-0022: Interactive CLI Library Selection](../decisions/adrs/ADR-0022-interactive-cli-library.md)
- [F-092: Interactive Mode Flag](../roadmap/features/planned/F-092-interactive-mode.md)
- [F-016: Interactive Rich UI](../roadmap/features/completed/F-016-interactive-rich-ui.md)
