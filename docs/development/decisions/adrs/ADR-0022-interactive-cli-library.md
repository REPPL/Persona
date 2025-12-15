# ADR-0022: Interactive CLI Library Selection

## Status

Accepted

## Context

Persona's CLI (built with Typer + Rich per ADR-0005) needs interactive capabilities beyond basic argument parsing:

- **Model/provider selection** with arrow-key navigation
- **Configuration editing** with form-based input
- **Multi-select operations** for batch processing
- **Guided workflow wizards** for complex tasks
- **File path autocomplete** for data input

The current CLI handles non-interactive use well, but interactive mode (`-i` flag) requires additional tooling.

## Decision

Use **questionary** for interactive CLI prompts.

### Rationale

1. **Right abstraction level** - questionary provides high-level prompt components (select, checkbox, text, confirm) that match our needs
2. **Built on prompt_toolkit** - Uses the same foundation as IPython and AWS CLI v2, ensuring reliability
3. **Fluent API** - Clean, readable code: `questionary.select(...).ask()`
4. **Active maintenance** - v2.1.1 released August 2025
5. **Low learning curve** - Familiar pattern for Python developers
6. **Rich compatibility** - Works alongside Rich output formatting

### Example Usage

```python
import questionary

# Model selection with arrow keys
model = questionary.select(
    "Select model:",
    choices=[
        questionary.Choice("Claude Sonnet 4 (recommended)", "claude-sonnet-4-20250514"),
        questionary.Choice("GPT-4o", "gpt-4o"),
        questionary.Choice("Gemini 1.5 Pro", "gemini-1.5-pro"),
    ],
    use_shortcuts=True,
).ask()

# Configuration form
answers = questionary.form(
    provider=questionary.select("Provider:", ["anthropic", "openai", "gemini"]),
    count=questionary.text("Persona count:", default="3"),
    output=questionary.select("Output format:", ["json", "markdown", "yaml"]),
).ask()

# File path with autocomplete
data_file = questionary.path(
    "Data file:",
    validate=lambda p: Path(p).exists() or "File not found",
).ask()
```

## Consequences

**Positive:**

- Consistent with Typer + Rich ecosystem
- Arrow-key navigation for all selection prompts
- Form-based input for multi-field configuration
- Built-in validation support
- Autocomplete for file paths
- Keyboard shortcuts (1-9 for quick selection)

**Negative:**

- Additional dependency (~100KB)
- Not suitable for full TUI dashboards (use Textual for that)
- Requires TTY (won't work in non-interactive pipes)

## Alternatives Considered

### prompt_toolkit (directly)

**Description:** Low-level terminal toolkit powering questionary, ptpython, and IPython.

**Pros:** Maximum flexibility, full control over rendering, supports full-screen applications.

**Cons:** Verbose for simple prompts, steeper learning curve, requires more boilerplate.

**Why Not Chosen:** Too low-level for our needs. questionary provides the right abstractions built on top of prompt_toolkit.

### Textual

**Description:** Modern TUI framework from the creators of Rich.

**Pros:** Beautiful full-screen applications, reactive design, CSS-like styling.

**Cons:** Overkill for simple prompts, different paradigm (full-screen vs inline).

**Why Not Chosen:** Reserved for future dashboard/monitoring features. Simple prompts don't need full TUI framework.

### inquirer3

**Description:** Python port of Inquirer.js.

**Pros:** Familiar to JavaScript developers.

**Cons:** Less actively maintained than questionary, similar feature set.

**Why Not Chosen:** questionary has more GitHub stars, more dependents, and clearer maintenance.

### Rich Prompt

**Description:** Built-in prompt in Rich library.

**Pros:** No additional dependency, consistent styling.

**Cons:** Basic text input only, no arrow-key selection, no multi-select.

**Why Not Chosen:** Insufficient for interactive workflows requiring selection menus.

## Research Reference

See [R-011: Interactive CLI Libraries](../../research/R-011-interactive-cli-libraries.md) for comprehensive analysis.

---

## Related Documentation

- [ADR-0005: Typer + Rich CLI Framework](./ADR-0005-cli-framework.md)
- [F-092: Interactive Mode Flag](../../roadmap/features/completed/F-092-interactive-mode.md)
- [F-093: TUI Configuration Editor](../../roadmap/features/completed/F-093-tui-config-editor.md)
- [R-011: Interactive CLI Libraries](../../research/R-011-interactive-cli-libraries.md)

---

**Status**: Accepted
