# R-005: CLI Design Patterns

## Executive Summary

Modern Python CLI development in 2025 centres on **Typer + Rich**, providing type-safe commands with beautiful terminal output. Seven essential patterns transform scripts into professional tools: subcommands, type-safe options, environment-based config, context objects, logging, packaging, and testing. The key anti-pattern to avoid is the "God Object" monolithic command function. Persona's CLI should follow a modular structure with commands split into separate modules.

## Current State of the Art (2025)

### Industry Standards

**Typer** (built on Click, type-hint driven) is the de facto standard for new Python CLI applications:
- Automatic argument parsing from type hints
- Built-in validation and help generation
- Rich integration for beautiful output
- Subcommand support for complex CLIs

**Rich** provides:
- Progress bars and spinners
- Tables and panels
- Syntax highlighting
- Markdown rendering

### Academic Research

No significant academic research specific to CLI patterns. Best practices derive from practical experience and community consensus.

### Open Source Ecosystem

| Framework | Type Hints | Rich Integration | Popularity |
|-----------|------------|------------------|------------|
| **Typer** | Native | Built-in | Growing rapidly |
| **Click** | Via plugins | Manual | Mature, stable |
| **Cyclopts** | Native | Manual | Newer alternative |
| **argparse** | No | Manual | Legacy |

## Alternatives Analysis

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Typer + Rich** | Type-safe, beautiful output, modern | Newer than Click | **Recommended** |
| **Click + Rich** | Mature, extensive docs | More verbose | Fallback if needed |
| **Cyclopts** | Clean, modern | Less community support | Monitor |
| **argparse** | Standard library | Verbose, dated | Avoid |

## Recommendation

### Primary Approach

Implement a modular CLI using **Typer + Rich** with these seven patterns:

#### 1. Subcommand Organisation

```python
# src/persona/ui/cli/__init__.py
import typer
from .commands import generate, experiment, check

app = typer.Typer(
    name="persona",
    help="Generate realistic user personas from your data using AI",
    add_completion=False
)

app.add_typer(experiment.app, name="experiment")
app.command()(generate.run)
app.command()(check.run)
```

#### 2. Type-Safe Options

```python
# src/persona/ui/cli/commands/generate.py
from typing import Optional
from pathlib import Path
import typer

def run(
    experiment_name: str = typer.Argument(..., help="Name of the experiment to run"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override model"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show cost estimate only"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Generate personas from experiment data."""
    ...
```

#### 3. Environment-Based Config

```python
# src/persona/core/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    default_vendor: str = "openai"

    class Config:
        env_file = ".env"
        env_prefix = ""  # Use OPENAI_API_KEY directly
```

#### 4. Context Objects

```python
# src/persona/ui/cli/context.py
from dataclasses import dataclass
from typing import Optional
import typer

@dataclass
class Context:
    verbose: bool = False
    config_path: Optional[Path] = None

def get_context(ctx: typer.Context) -> Context:
    return ctx.ensure_object(Context)
```

#### 5. Rich Output

```python
# src/persona/ui/cli/output.py
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def show_cost_estimate(estimate: CostEstimate):
    table = Table(title="Cost Estimate", box=box.ROUNDED)
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Model", estimate.model)
    table.add_row("Input tokens", f"{estimate.input_tokens:,}")
    table.add_row("Estimated cost", f"${estimate.total:.4f}")
    console.print(table)

def show_progress():
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Generating personas...", total=None)
        yield progress, task
```

#### 6. Error Handling

```python
# src/persona/ui/cli/errors.py
from rich.console import Console
import typer

console = Console(stderr=True)

def handle_error(message: str, suggestion: str = None):
    console.print(f"[red]Error:[/red] {message}")
    if suggestion:
        console.print(f"[yellow]Suggestion:[/yellow] {suggestion}")
    raise typer.Exit(1)
```

#### 7. Testing

```python
# tests/unit/cli/test_generate.py
from typer.testing import CliRunner
from persona.ui.cli import app

runner = CliRunner()

def test_generate_dry_run():
    result = runner.invoke(app, ["generate", "test-experiment", "--dry-run"])
    assert result.exit_code == 0
    assert "Cost Estimate" in result.stdout
```

### Project Structure

```
src/persona/ui/cli/
├── __init__.py          # App definition, subcommand registration
├── context.py           # Shared context object
├── output.py            # Rich formatting utilities
├── errors.py            # Error handling
└── commands/
    ├── __init__.py
    ├── generate.py      # persona generate
    ├── check.py         # persona check
    └── experiment/
        ├── __init__.py  # Typer sub-app
        ├── create.py    # persona experiment create
        ├── list.py      # persona experiment list
        ├── show.py      # persona experiment show
        └── delete.py    # persona experiment delete
```

### Anti-Patterns to Avoid

1. **God Object** - Single function handling all logic
2. **Hardcoded Paths** - Use Path objects and configuration
3. **Print Statements** - Use Rich console for all output
4. **Swallowed Errors** - Always provide helpful error messages

### Rationale

1. **Type Safety** - Type hints provide IDE support and validation
2. **Modularity** - Easy to test and extend individual commands
3. **User Experience** - Rich provides beautiful, informative output
4. **Maintainability** - Clear separation of concerns

## Impact on Existing Decisions

### ADR Updates Required

**ADR-0005 (CLI Framework)** should be updated to:
- Add "Alternatives Considered" section (Click, argparse, Cyclopts)
- Document the seven patterns
- Specify project structure

### Feature Spec Updates

**F-008 (CLI Interface)** should specify:
- Command structure hierarchy
- Typer app configuration
- Error handling patterns

**F-015-F-018 (CLI commands)** should specify:
- Individual command implementations
- Rich output formats
- Testing approach

## Sources

- [7 Typer CLI Patterns](https://medium.com/@connect.hashblock/7-typer-cli-patterns-that-feel-like-real-tools-ecbe72720828)
- [Typer Best Practices (Project Rules)](https://www.projectrules.ai/rules/typer)
- [Building Modern CLI with Typer and Rich](https://www.codecentric.de/en/knowledge-hub/blog/lets-build-a-modern-cmd-tool-with-python-using-typer-and-rich)
- [Typer Official Documentation](https://typer.tiangolo.com/)
- [Rich Python Library Guide](https://arjancodes.com/blog/rich-python-library-for-interactive-cli-tools/)

---

## Related Documentation

- [ADR-0005: CLI Framework](../decisions/adrs/ADR-0005-cli-framework.md)
- [F-008: CLI Interface](../roadmap/features/completed/F-008-cli-interface.md)
- [System Design](../planning/architecture/system-design.md)
