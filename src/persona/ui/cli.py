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

from persona.ui.commands import (
    experiment_app,
    generate_app,
    vendor_app,
    model_app,
    template_app,
    workflow_app,
    preview_app,
    validate_app,
    compare_app,
    export_app,
    cluster_app,
    refine_app,
    config_app,
    help_app,
    quality_app,
    plugin_app,
    script_app,
    dashboard_app,
    serve_app,
)
from persona.ui.console import get_console as _get_console

app = typer.Typer(
    name="persona",
    help="Generate realistic user personas from your data using AI.",
    no_args_is_help=True,
    add_completion=True,  # Enable shell completions (F-095)
)

# Add subcommand groups - User-facing commands
app.add_typer(generate_app, name="generate")
app.add_typer(serve_app, name="serve")
app.add_typer(dashboard_app, name="dashboard")
app.add_typer(preview_app, name="preview")
app.add_typer(validate_app, name="validate")
app.add_typer(compare_app, name="compare")
app.add_typer(export_app, name="export")
app.add_typer(cluster_app, name="cluster")
app.add_typer(refine_app, name="refine")
app.add_typer(experiment_app, name="experiment")
app.add_typer(config_app, name="config")
app.add_typer(help_app, name="help")
app.add_typer(quality_app, name="score")
app.add_typer(script_app, name="script")

# Add subcommand groups - Advanced/Admin commands (hidden by default)
app.add_typer(vendor_app, name="vendor", hidden=True)
app.add_typer(model_app, name="model", hidden=True)
app.add_typer(template_app, name="template", hidden=True)
app.add_typer(workflow_app, name="workflow", hidden=True)
app.add_typer(plugin_app, name="plugin")

# Global state for console options (used by callbacks)
_no_color: bool = False
_quiet: bool = False
_verbosity: int = 1  # 0=quiet, 1=normal, 2=verbose, 3=debug
_interactive: bool = False


def get_console():
    """Get console with current global settings."""
    return _get_console(no_color=_no_color, quiet=_quiet, verbosity=_verbosity)


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
    global _quiet, _verbosity
    # Always reset first (for test isolation), then set if True
    _quiet = bool(value)
    if _quiet:
        _verbosity = 0


def verbose_callback(value: int) -> None:
    """Set verbosity level globally.

    Can be called multiple times (-v -v) to increase verbosity.
    """
    global _verbosity
    if value:
        _verbosity = min(value + 1, 3)  # +1 because normal is 1, cap at 3 (debug)


def interactive_callback(value: bool) -> None:
    """Set interactive mode globally."""
    global _interactive
    _interactive = bool(value)


def _reset_globals() -> None:
    """Reset global state (for testing)."""
    global _no_color, _quiet, _verbosity, _interactive
    _no_color = False
    _quiet = False
    _verbosity = 1
    _interactive = False


def is_interactive() -> bool:
    """Check if interactive mode is enabled."""
    return _interactive


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
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose", "-v",
            callback=verbose_callback,
            count=True,
            is_eager=True,
            help="Increase output verbosity. Use -v for verbose, -vv for debug.",
        ),
    ] = 0,
    interactive: Annotated[
        Optional[bool],
        typer.Option(
            "--interactive", "-i",
            callback=interactive_callback,
            is_eager=True,
            help="Run in interactive mode with guided prompts.",
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
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    Estimate API costs before generating.

    Example:
        persona cost --from ./data/interviews.csv --count 5
        persona cost --tokens 10000 --model gpt-4o
    """
    import json

    from persona import __version__
    from persona.core.cost import CostEstimator
    from persona.core.data import DataLoader

    console = get_console()
    estimator = CostEstimator()

    # Determine input tokens
    if data_path:
        loader = DataLoader()
        data, _files = loader.load_path(data_path)
        input_tokens = loader.count_tokens(data)
    elif tokens:
        input_tokens = tokens
    else:
        input_tokens = 5000  # Default assumption

    if model:
        # Single model estimate
        estimate = estimator.estimate(
            model=model,
            input_tokens=input_tokens,
            persona_count=count,
            provider=provider,
        )

        if json_output:
            result = {
                "command": "cost",
                "version": __version__,
                "success": estimate.pricing is not None,
                "data": {
                    "input_tokens": estimate.input_tokens,
                    "output_tokens": estimate.output_tokens,
                    "persona_count": count,
                    "model": estimate.model,
                    "provider": estimate.provider,
                    "input_cost": float(estimate.input_cost) if estimate.pricing else None,
                    "output_cost": float(estimate.output_cost) if estimate.pricing else None,
                    "total_cost": float(estimate.total_cost) if estimate.pricing else None,
                },
            }
            print(json.dumps(result, indent=2))
            return

        # Rich output
        console.print(f"[dim]Persona {__version__}[/dim]\n")
        if data_path:
            console.print(f"[bold]Data:[/bold] {data_path}")
        console.print(f"[bold]Tokens:[/bold] {input_tokens:,}")
        console.print(f"[bold]Personas:[/bold] {count}")
        console.print()

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

        if json_output:
            result = {
                "command": "cost",
                "version": __version__,
                "success": True,
                "data": {
                    "input_tokens": input_tokens,
                    "persona_count": count,
                    "estimates": [
                        {
                            "model": est.model,
                            "provider": est.provider,
                            "input_tokens": est.input_tokens,
                            "output_tokens": est.output_tokens,
                            "input_cost": float(est.input_cost) if est.pricing else None,
                            "output_cost": float(est.output_cost) if est.pricing else None,
                            "total_cost": float(est.total_cost) if est.pricing else None,
                        }
                        for est in estimates
                        if est.pricing
                    ],
                },
            }
            print(json.dumps(result, indent=2))
            return

        # Rich output
        console.print(f"[dim]Persona {__version__}[/dim]\n")
        if data_path:
            console.print(f"[bold]Data:[/bold] {data_path}")
            console.print(f"[bold]Tokens:[/bold] {input_tokens:,}")
        elif tokens:
            console.print(f"[bold]Tokens:[/bold] {input_tokens:,}")
        else:
            console.print("[yellow]Specify --from or --tokens for accurate estimates.[/yellow]")
        console.print(f"[bold]Personas:[/bold] {count}")
        console.print()

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
        if estimates:
            console.print(f"\n[dim]Estimates based on {input_tokens:,} input tokens + ~{estimates[0].output_tokens:,} output tokens[/dim]")


@app.command("models")
def list_models(
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="Filter by provider (anthropic, openai, gemini).",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    List available models with pricing information.

    Example:
        persona models
        persona models --provider anthropic
        persona models --json
    """
    import json

    from persona import __version__
    from persona.core.cost import PricingData
    from persona.core.providers import ProviderFactory

    console = get_console()

    # Get all pricing data
    all_pricing = list(PricingData.list_models(provider=provider))

    # Check which providers are configured
    configured_providers = set()
    for p_name in ["anthropic", "openai", "gemini"]:
        try:
            prov = ProviderFactory.create(p_name)
            if prov.is_configured():
                configured_providers.add(p_name)
        except Exception:
            pass

    if json_output:
        result = {
            "command": "models",
            "version": __version__,
            "success": True,
            "data": {
                "providers": {},
            },
        }

        # Group by provider
        for pricing in all_pricing:
            if pricing.provider not in result["data"]["providers"]:
                result["data"]["providers"][pricing.provider] = {
                    "configured": pricing.provider in configured_providers,
                    "models": [],
                }
            result["data"]["providers"][pricing.provider]["models"].append({
                "name": pricing.model,
                "input_price": float(pricing.input_price),
                "output_price": float(pricing.output_price),
                "default": pricing.model in [
                    "claude-sonnet-4-20250514",
                    "gpt-4o",
                    "gemini-2.0-flash",
                ],
            })

        print(json.dumps(result, indent=2))
        return

    # Rich output
    console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Group by provider
    by_provider: dict[str, list] = {}
    for pricing in all_pricing:
        if pricing.provider not in by_provider:
            by_provider[pricing.provider] = []
        by_provider[pricing.provider].append(pricing)

    for provider_name, models in sorted(by_provider.items()):
        # Provider header with configured status
        configured = provider_name in configured_providers
        status = "[green]✓[/green]" if configured else "○"
        console.print(f"\n[bold]{provider_name}[/bold] {status}")

        # Sort models by input price
        models.sort(key=lambda x: float(x.input_price))

        for pricing in models:
            # Check if default
            is_default = pricing.model in [
                "claude-sonnet-4-20250514",
                "gpt-4o",
                "gemini-2.0-flash",
            ]
            default_marker = " [cyan]✓ default[/cyan]" if is_default else ""

            console.print(
                f"  {pricing.model:30} "
                f"${float(pricing.input_price):>6.2f}/${float(pricing.output_price):>6.2f} per M tokens"
                f"{default_marker}"
            )

    # Legend
    console.print()
    console.print("[dim]Legend: Input/Output price per million tokens[/dim]")
    console.print("[dim]✓ = configured provider, ○ = not configured[/dim]")


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
