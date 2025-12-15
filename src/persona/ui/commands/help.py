"""
Help system for Persona CLI (F-082).

Provides topic-based help, interactive help browser, and rich help output.
"""

from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

help_app = typer.Typer(
    name="help",
    help="Get help on Persona commands and topics.",
    invoke_without_command=True,
)

# Help topic content
HELP_TOPICS: dict[str, dict[str, str]] = {
    "quickstart": {
        "title": "Getting Started with Persona",
        "content": """
# Quickstart Guide

Persona generates realistic user personas from your data using AI.

## Installation

```bash
pip install persona
```

## Quick Setup

1. **Set up an API key** (at least one required):
   ```bash
   export ANTHROPIC_API_KEY=your-key  # Claude
   export OPENAI_API_KEY=your-key     # GPT
   export GOOGLE_API_KEY=your-key     # Gemini
   ```

2. **Check your setup**:
   ```bash
   persona check
   ```

3. **Estimate costs before generating**:
   ```bash
   persona cost --from ./data.csv --count 3
   ```

4. **Generate your first personas**:
   ```bash
   persona generate --from ./data.csv --count 3
   ```

## What's Next?

- `persona help configuration` - Configure defaults
- `persona help providers` - Provider setup details
- `persona help generation` - Generation options
""",
    },
    "configuration": {
        "title": "Configuring Persona",
        "content": """
# Configuration Guide

Persona uses layered configuration with these sources (highest to lowest priority):

1. **Environment variables** (`PERSONA_*`)
2. **Experiment config** (`experiment.yaml`)
3. **Project config** (`.persona/config.yaml`)
4. **Global config** (`~/.persona/config.yaml`)
5. **Built-in defaults**

## Managing Configuration

```bash
# Initialise global config
persona config init

# View effective configuration
persona config show

# Get a specific value
persona config get defaults.provider

# Set a value
persona config set defaults.model gpt-4o

# Reset to defaults
persona config reset

# Show config file locations
persona config path
```

## Configuration File Format

```yaml
# ~/.persona/config.yaml
defaults:
  provider: anthropic
  model: claude-sonnet-4-20250514
  count: 3
  complexity: moderate
  detail_level: standard

budgets:
  per_run: 5.00
  daily: 25.00
  monthly: 100.00

output:
  format: json
  include_readme: true
  timestamp_folders: true

logging:
  level: info
  format: console
```

## Environment Variables

Override any config value with `PERSONA_<PATH>`:

```bash
export PERSONA_DEFAULTS_PROVIDER=openai
export PERSONA_DEFAULTS_COUNT=5
export PERSONA_BUDGETS_PER_RUN=10.00
```
""",
    },
    "providers": {
        "title": "LLM Provider Setup",
        "content": """
# Provider Setup

Persona supports multiple LLM providers. You need at least one configured.

## Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY=your-key
```

Available models:
- `claude-opus-4-20250514` - Most capable, highest cost
- `claude-sonnet-4-20250514` - Balanced (default)
- `claude-haiku-3-5-20241022` - Fast and economical

## OpenAI (GPT)

```bash
export OPENAI_API_KEY=your-key
```

Available models:
- `gpt-4.1` - Latest flagship model
- `gpt-4o` - Optimised multimodal (default)
- `gpt-4o-mini` - Cost-effective

## Google (Gemini)

```bash
export GOOGLE_API_KEY=your-key
```

Available models:
- `gemini-2.5-pro` - Most capable
- `gemini-2.0-flash` - Fast and economical (default)
- `gemini-2.0-flash-lite` - Ultra-fast

## Checking Provider Status

```bash
# See which providers are configured
persona check

# List all available models with pricing
persona models

# Filter by provider
persona models --provider anthropic
```

## Selecting a Provider

```bash
# Use --provider flag
persona generate --from data.csv --provider openai

# Or set default in config
persona config set defaults.provider openai
```
""",
    },
    "experiments": {
        "title": "Managing Experiments",
        "content": """
# Experiment Management

Experiments help you organise and track persona generation runs.

## Creating Experiments

```bash
# Create a new experiment
persona experiment create "my-project"

# Create with description
persona experiment create "user-research" --description "Q4 user research study"
```

## Listing Experiments

```bash
# List all experiments
persona experiment list

# Output as JSON for scripting
persona experiment list --json
```

## Viewing Experiment Details

```bash
# Show experiment configuration
persona experiment show my-project
```

## Project Initialisation

```bash
# Create project structure
persona init ./my-project

# Creates:
#   experiments/
#   data/
#   templates/
#   persona.yaml
```

## Experiment Configuration

Each experiment has its own `experiment.yaml`:

```yaml
name: user-research
description: Q4 user research study
created: 2024-01-15T10:00:00Z

defaults:
  provider: anthropic
  count: 5
  complexity: detailed

data:
  source: ./interviews.csv
  format: csv
```
""",
    },
    "generation": {
        "title": "Generating Personas",
        "content": """
# Generating Personas

The `generate` command creates personas from your data.

## Basic Usage

```bash
# Generate from a single file
persona generate --from ./data.csv

# Specify number of personas
persona generate --from ./data.csv --count 5

# Use specific provider/model
persona generate --from ./data.csv --provider openai --model gpt-4o
```

## Complexity Levels

Control how detailed the personas are:

| Level | Description |
|-------|-------------|
| `simple` | Basic demographics, minimal detail |
| `moderate` | Balanced detail (default) |
| `complex` | Rich backgrounds, detailed attributes |

```bash
persona generate --from data.csv --complexity complex
```

## Detail Levels

Control the amount of descriptive text:

| Level | Description |
|-------|-------------|
| `minimal` | Bullet points, key facts only |
| `standard` | Short paragraphs (default) |
| `detailed` | Full narratives, examples |

```bash
persona generate --from data.csv --detail detailed
```

## Data Sources

Supported formats:
- CSV files (`.csv`)
- JSON files (`.json`)
- Text files (`.txt`)
- Directories (processes all supported files)

```bash
# From CSV
persona generate --from ./interviews.csv

# From directory
persona generate --from ./data/
```

## Output Options

```bash
# Specify output directory
persona generate --from data.csv --output ./personas/

# Output as JSON (for piping)
persona generate --from data.csv --json
```
""",
    },
    "output": {
        "title": "Output Formats and Options",
        "content": """
# Output Formats

Persona supports multiple output formats for different use cases.

## JSON Output

Machine-readable format for integration:

```bash
# Any command with --json flag
persona check --json
persona cost --json
persona models --json
persona generate --from data.csv --json
```

## Verbosity Levels

Control output detail:

```bash
# Quiet - errors and results only
persona -q generate --from data.csv

# Normal - progress and key info (default)
persona generate --from data.csv

# Verbose - timing, provider details
persona -v generate --from data.csv

# Debug - full API calls, raw responses
persona -vv generate --from data.csv
```

## Colour Output

```bash
# Disable colour (or set NO_COLOR=1)
persona --no-color check
```

## File Output

Generated personas are saved to:
- `./experiments/<experiment>/personas/` by default
- Custom location with `--output`

Each persona includes:
- `persona-N.json` - Structured data
- `persona-N.md` - Human-readable markdown
- `README.md` - Generation summary (if enabled)
""",
    },
    "costs": {
        "title": "Understanding Costs",
        "content": """
# Understanding Costs

Persona helps you understand and control API costs.

## Estimating Before Generation

```bash
# Estimate from data file
persona cost --from ./data.csv --count 5

# Estimate with known token count
persona cost --tokens 10000 --count 3

# For specific model
persona cost --from data.csv --model claude-opus-4-20250514
```

## Comparing Models

```bash
# Compare all models (sorted by cost)
persona cost --tokens 5000

# Compare within a provider
persona cost --tokens 5000 --provider anthropic
```

## Understanding the Estimate

Cost is based on:
- **Input tokens**: Your data + system prompts
- **Output tokens**: Generated persona content

The estimate shows:
- Input cost (data processing)
- Output cost (generation)
- Total estimated cost

## Budget Limits

Set budget limits in configuration:

```yaml
# ~/.persona/config.yaml
budgets:
  per_run: 5.00    # Max per generation
  daily: 25.00     # Daily limit
  monthly: 100.00  # Monthly limit
```

## Model Pricing

View current pricing:

```bash
persona models
```

Prices shown as $/M (dollars per million tokens).
""",
    },
    "troubleshoot": {
        "title": "Troubleshooting Common Issues",
        "content": """
# Troubleshooting Guide

## "No providers configured"

**Problem**: Persona can't find any API keys.

**Solution**:
```bash
# Check current status
persona check

# Set at least one API key
export ANTHROPIC_API_KEY=your-key
# or
export OPENAI_API_KEY=your-key
# or
export GOOGLE_API_KEY=your-key
```

## "Invalid API key" or Authentication Errors

**Problem**: API key is set but not valid.

**Solution**:
1. Verify the key is correct (no extra spaces)
2. Check the key hasn't expired
3. Ensure you have API access (not just web chat access)

## "Rate limit exceeded"

**Problem**: Too many API requests.

**Solution**:
- Wait and retry
- Use a different provider
- Check your API plan's rate limits

## "Model not found"

**Problem**: Specified model doesn't exist.

**Solution**:
```bash
# List available models
persona models

# Use a valid model name
persona generate --from data.csv --model claude-sonnet-4-20250514
```

## "File not found" or Data Loading Errors

**Problem**: Can't read input data.

**Solution**:
- Check file path is correct
- Ensure file exists and is readable
- Verify file format is supported (csv, json, txt)

## "Budget limit exceeded"

**Problem**: Generation cost exceeds your budget limit.

**Solution**:
```bash
# Check current limits
persona config get budgets

# Increase limit
persona config set budgets.per_run 10.00

# Or use fewer personas/simpler model
persona cost --from data.csv --count 3
```

## Getting More Help

- GitHub Issues: https://github.com/REPPL/Persona/issues
- Documentation: https://github.com/REPPL/Persona/docs
""",
    },
}


def get_topic_list() -> list[tuple[str, str]]:
    """Get list of (topic_name, title) tuples."""
    return [(name, info["title"]) for name, info in HELP_TOPICS.items()]


def get_topic_content(topic: str) -> Optional[str]:
    """Get markdown content for a topic."""
    if topic in HELP_TOPICS:
        return HELP_TOPICS[topic]["content"]
    return None


def get_topic_title(topic: str) -> Optional[str]:
    """Get title for a topic."""
    if topic in HELP_TOPICS:
        return HELP_TOPICS[topic]["title"]
    return None


@help_app.callback(invoke_without_command=True)
def help_main(
    ctx: typer.Context,
    topic: Annotated[
        Optional[str],
        typer.Argument(
            help="Help topic to display (use 'topics' to list all).",
        ),
    ] = None,
) -> None:
    """
    Get help on Persona commands and topics.

    Use 'persona help topics' to see available topics, or
    'persona help <topic>' for specific help.

    Examples:
        persona help                 Show this overview
        persona help topics          List all help topics
        persona help quickstart      Getting started guide
        persona help providers       Provider setup help
    """
    console = Console()

    # If a subcommand is being invoked, let it handle things
    if ctx.invoked_subcommand is not None:
        return

    if topic is None:
        # Show overview
        _show_overview(console)
    elif topic.lower() == "topics":
        # List all topics
        _show_topics(console)
    else:
        # Show specific topic
        _show_topic(console, topic.lower())


def _show_overview(console: Console) -> None:
    """Display help overview."""
    from persona import __version__

    console.print(f"[dim]Persona {__version__}[/dim]\n")

    console.print(Panel(
        "[bold]Persona Help System[/bold]\n\n"
        "Generate realistic user personas from your data using AI.",
        border_style="blue",
    ))

    console.print("\n[bold]Quick Commands:[/bold]")
    console.print("  persona check          Check installation status")
    console.print("  persona cost           Estimate generation costs")
    console.print("  persona generate       Generate personas from data")
    console.print("  persona models         List available models")

    console.print("\n[bold]Help Topics:[/bold]")
    console.print("  persona help topics       List all help topics")
    console.print("  persona help quickstart   Getting started guide")
    console.print("  persona help providers    Provider setup")
    console.print("  persona help costs        Understanding costs")

    console.print("\n[bold]Command Help:[/bold]")
    console.print("  persona --help            All commands")
    console.print("  persona <command> --help  Command-specific help")

    console.print("\n[dim]Documentation: https://github.com/REPPL/Persona[/dim]")


def _show_topics(console: Console) -> None:
    """Display list of help topics."""
    from persona import __version__

    console.print(f"[dim]Persona {__version__}[/dim]\n")

    console.print("[bold]Available Help Topics:[/bold]\n")

    table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
    table.add_column("Topic", style="cyan")
    table.add_column("Description")

    for topic_name, title in get_topic_list():
        table.add_row(topic_name, title)

    console.print(table)

    console.print("\n[dim]Use 'persona help <topic>' for detailed help.[/dim]")


def _show_topic(console: Console, topic: str) -> None:
    """Display a specific help topic."""
    from persona import __version__

    content = get_topic_content(topic)
    title = get_topic_title(topic)

    if content is None:
        console.print(f"[red]Unknown help topic: {topic}[/red]")
        console.print("\nAvailable topics:")
        for topic_name, topic_title in get_topic_list():
            console.print(f"  {topic_name:15} {topic_title}")
        raise typer.Exit(1)

    console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Render markdown
    md = Markdown(content)
    console.print(md)

    console.print("\n[dim]Use 'persona help topics' to see all topics.[/dim]")


@help_app.command("topics")
def list_topics() -> None:
    """List all available help topics."""
    console = Console()
    _show_topics(console)
