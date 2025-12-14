"""
Command-line interface for Persona.

This module provides the main CLI entry point using Typer.
"""

import os
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.ui.commands import experiment_app, generate_app
from persona.ui.console import get_console as _get_console

app = typer.Typer(
    name="persona",
    help="Generate realistic user personas from your data using AI.",
    no_args_is_help=True,
    add_completion=False,
)

# Add subcommand groups
app.add_typer(generate_app, name="generate")
app.add_typer(experiment_app, name="experiment")

# Global state for console options (used by callbacks)
_no_color: bool = False
_quiet: bool = False


def get_console():
    """Get console with current global settings."""
    return _get_console(no_color=_no_color, quiet=_quiet)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from persona import __version__
        console = get_console()
        console.print(f"Persona {__version__}")
        raise typer.Exit()


def no_color_callback(value: bool) -> None:
    """Set no-color mode globally."""
    global _no_color
    # Always reset first (for test isolation), then set if True
    _no_color = bool(value)


def quiet_callback(value: bool) -> None:
    """Set quiet mode globally."""
    global _quiet
    # Always reset first (for test isolation), then set if True
    _quiet = bool(value)


def _reset_globals() -> None:
    """Reset global state (for testing)."""
    global _no_color, _quiet
    _no_color = False
    _quiet = False


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = None,
    no_color: Annotated[
        Optional[bool],
        typer.Option(
            "--no-color",
            callback=no_color_callback,
            is_eager=True,
            help="Disable colour output.",
        ),
    ] = None,
    quiet: Annotated[
        Optional[bool],
        typer.Option(
            "--quiet", "-q",
            callback=quiet_callback,
            is_eager=True,
            help="Minimal output (errors and results only).",
        ),
    ] = None,
) -> None:
    """Generate realistic user personas from your data using AI."""
    # Note: Global state is set by eager callbacks before this runs
    pass


@app.command()
def check(
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """Check Persona installation and configuration."""
    import json

    from persona import __version__
    from persona.core.providers import ProviderFactory

    console = get_console()

    providers_config = [
        ("anthropic", "ANTHROPIC_API_KEY"),
        ("openai", "OPENAI_API_KEY"),
        ("gemini", "GOOGLE_API_KEY"),
    ]

    # Gather provider status
    provider_status = {}
    configured_count = 0
    for provider_name, env_var in providers_config:
        try:
            provider = ProviderFactory.create(provider_name)
            is_configured = provider.is_configured()
            provider_status[provider_name] = {
                "configured": is_configured,
                "env_var": env_var,
            }
            if is_configured:
                configured_count += 1
        except Exception:
            provider_status[provider_name] = {
                "configured": False,
                "env_var": env_var,
                "error": True,
            }

    if json_output:
        # JSON output mode
        result = {
            "command": "check",
            "version": __version__,
            "success": True,
            "data": {
                "installation": "ok",
                "providers": provider_status,
            },
        }
        print(json.dumps(result, indent=2))
        return

    # Rich output mode
    console.print(Panel.fit(
        "[bold]Persona Health Check[/bold]",
        border_style="green",
    ))

    # Version and installation
    console.print(f"\n[green]✓[/green] Version: {__version__}")
    console.print(f"[green]✓[/green] Installation: OK")

    # Provider status
    console.print("\n[bold]Provider Status:[/bold]")

    for provider_name, env_var in providers_config:
        status = provider_status[provider_name]
        if status.get("error"):
            console.print(f"  [red]✗[/red] {provider_name}: Error")
        elif status["configured"]:
            console.print(f"  [green]✓[/green] {provider_name}: Configured")
        else:
            console.print(f"  [yellow]○[/yellow] {provider_name}: Not configured ({env_var})")

    if configured_count == 0:
        console.print("\n[yellow]Warning:[/yellow] No providers configured.")
        console.print("Set at least one API key to start generating personas:")
        console.print("  export ANTHROPIC_API_KEY=your-key")
        console.print("  export OPENAI_API_KEY=your-key")
        console.print("  export GOOGLE_API_KEY=your-key")
    else:
        console.print(f"\n[green]Ready![/green] {configured_count} provider(s) available.")


@app.command("cost")
def estimate_cost(
    data_path: Annotated[
        Optional[Path],
        typer.Option(
            "--from",
            "-f",
            help="Path to data file (for token-based estimation).",
            exists=True,
        ),
    ] = None,
    tokens: Annotated[
        Optional[int],
        typer.Option(
            "--tokens",
            "-t",
            help="Number of input tokens (if not using --from).",
        ),
    ] = None,
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-n",
            help="Number of personas to generate.",
        ),
    ] = 3,
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="Filter by provider (anthropic, openai, gemini).",
        ),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help="Specific model to estimate (shows all if not specified).",
        ),
    ] = None,
) -> None:
    """
    Estimate API costs before generating.

    Example:
        persona cost --from ./data/interviews.csv --count 5
        persona cost --tokens 10000 --model gpt-4o
    """
    from persona import __version__
    from persona.core.cost import CostEstimator, PricingData
    from persona.core.data import DataLoader

    console = get_console()
    console.print(f"[dim]Persona {__version__}[/dim]\n")

    estimator = CostEstimator()

    # Determine input tokens
    if data_path:
        loader = DataLoader()
        data = loader.load_file(data_path)
        input_tokens = loader.count_tokens(data)
        console.print(f"[bold]Data:[/bold] {data_path}")
        console.print(f"[bold]Tokens:[/bold] {input_tokens:,}")
    elif tokens:
        input_tokens = tokens
        console.print(f"[bold]Tokens:[/bold] {input_tokens:,}")
    else:
        console.print("[yellow]Specify --from or --tokens for accurate estimates.[/yellow]")
        input_tokens = 5000  # Default assumption

    console.print(f"[bold]Personas:[/bold] {count}")
    console.print()

    if model:
        # Single model estimate
        estimate = estimator.estimate(
            model=model,
            input_tokens=input_tokens,
            persona_count=count,
            provider=provider,
        )

        if estimate.pricing:
            console.print(f"[bold]{estimate.model}[/bold] ({estimate.provider})")
            console.print(f"  Input:  {estimate.input_tokens:,} tokens @ ${float(estimate.pricing.input_price)}/M = {estimator.format_cost(estimate.input_cost)}")
            console.print(f"  Output: {estimate.output_tokens:,} tokens @ ${float(estimate.pricing.output_price)}/M = {estimator.format_cost(estimate.output_cost)}")
            console.print(f"  [bold]Total: {estimator.format_cost(estimate.total_cost)}[/bold]")
        else:
            console.print(f"[yellow]Unknown model: {model}[/yellow]")
    else:
        # Compare all models
        estimates = estimator.compare_models(
            input_tokens=input_tokens,
            persona_count=count,
            provider=provider,
        )

        table = Table(title="Cost Estimates (sorted by cost)")
        table.add_column("Model", style="cyan")
        table.add_column("Provider")
        table.add_column("Est. Cost", justify="right", style="green")
        table.add_column("Input $/M", justify="right")
        table.add_column("Output $/M", justify="right")

        for est in estimates:
            if est.pricing:
                table.add_row(
                    est.model,
                    est.provider,
                    estimator.format_cost(est.total_cost),
                    f"${float(est.pricing.input_price):.2f}",
                    f"${float(est.pricing.output_price):.2f}",
                )

        console.print(table)
        console.print(f"\n[dim]Estimates based on {input_tokens:,} input tokens + ~{estimates[0].output_tokens:,} output tokens[/dim]")


@app.command()
def init(
    path: Annotated[
        Optional[Path],
        typer.Argument(
            help="Directory to initialise (defaults to current directory).",
        ),
    ] = None,
) -> None:
    """
    Initialise a new Persona project.

    Creates the recommended directory structure for managing
    experiments and data.

    Example:
        persona init ./my-project
    """
    from persona import __version__

    console = get_console()
    console.print(f"[dim]Persona {__version__}[/dim]\n")

    target = path or Path.cwd()
    target = target.resolve()

    console.print(f"[bold]Initialising Persona project in:[/bold] {target}")

    # Create directory structure
    dirs = [
        target / "experiments",
        target / "data",
        target / "templates",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        console.print(f"  [green]✓[/green] Created: {d.relative_to(target)}/")

    # Create sample config
    config_path = target / "persona.yaml"
    if not config_path.exists():
        config_content = """# Persona Configuration
# See: https://github.com/REPPL/Persona

defaults:
  provider: anthropic
  count: 3
  workflow: default
  complexity: moderate
  detail_level: standard

experiments_dir: ./experiments
data_dir: ./data
templates_dir: ./templates
"""
        config_path.write_text(config_content)
        console.print(f"  [green]✓[/green] Created: persona.yaml")

    console.print("\n[green]Project initialised![/green]")
    console.print("\nNext steps:")
    console.print("  1. Add your data files to ./data/")
    console.print("  2. Run: persona generate --from ./data/your-file.csv")


if __name__ == "__main__":
    app()
