"""
Command-line interface for Persona.

This module provides the main CLI entry point using Typer.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

import typer

# Lazy load Rich components for faster CLI startup
if TYPE_CHECKING:
    pass


def _get_panel():
    """Lazy load Rich Panel class."""
    from rich.panel import Panel

    return Panel


def _get_table():
    """Lazy load Rich Table class."""
    from rich.table import Table

    return Table


from persona.ui.commands import (
    academic_app,
    audit_app,
    bias_app,
    cluster_app,
    compare_app,
    config_app,
    dashboard_app,
    diversity_app,
    evaluate_app,
    experiment_app,
    export_app,
    faithfulness_app,
    fidelity_app,
    generate_app,
    help_app,
    model_app,
    plugin_app,
    preview_app,
    privacy_app,
    project_app,
    quality_app,
    refine_app,
    script_app,
    serve_app,
    synthesise_app,
    template_app,
    validate_app,
    vendor_app,
    verify_app,
    workflow_app,
)
from persona.ui.console import get_console as _get_console

app = typer.Typer(
    name="persona",
    help="Generate realistic user personas from your data using AI.",
    no_args_is_help=True,
    invoke_without_command=True,  # Allow callback to handle -i flag
    add_completion=False,  # Hide completion options from help (expert feature)
)

# =============================================================================
# Essential Commands (visible to all users)
# =============================================================================
# These are the core commands that most users will need.
app.add_typer(generate_app, name="generate")
app.add_typer(preview_app, name="preview")
app.add_typer(export_app, name="export")
app.add_typer(validate_app, name="validate")
app.add_typer(project_app, name="project")
app.add_typer(config_app, name="config")
app.add_typer(help_app, name="help")

# =============================================================================
# Advanced Commands (hidden by default, for expert users)
# =============================================================================
# Use `persona --all-commands` or `persona help advanced` to see these.
# These commands are still fully functional, just not shown in `--help`.

# Research & Analysis
app.add_typer(experiment_app, name="experiment", hidden=True)
app.add_typer(compare_app, name="compare", hidden=True)
app.add_typer(cluster_app, name="cluster", hidden=True)
app.add_typer(refine_app, name="refine", hidden=True)

# Quality & Validation
app.add_typer(quality_app, name="score", hidden=True)
app.add_typer(evaluate_app, name="evaluate", hidden=True)
app.add_typer(academic_app, name="academic", hidden=True)
app.add_typer(faithfulness_app, name="faithfulness", hidden=True)
app.add_typer(fidelity_app, name="fidelity", hidden=True)
app.add_typer(diversity_app, name="diversity", hidden=True)
app.add_typer(bias_app, name="bias", hidden=True)
app.add_typer(verify_app, name="verify", hidden=True)

# Privacy & Security
app.add_typer(privacy_app, name="privacy", hidden=True)
app.add_typer(synthesise_app, name="synthesise", hidden=True)
app.add_typer(audit_app, name="audit", hidden=True)

# Development & Deployment
app.add_typer(serve_app, name="serve", hidden=True)
app.add_typer(dashboard_app, name="dashboard", hidden=True)
app.add_typer(script_app, name="script", hidden=True)
app.add_typer(plugin_app, name="plugin", hidden=True)

# =============================================================================
# Admin Commands (hidden, for advanced configuration)
# =============================================================================
app.add_typer(vendor_app, name="vendor", hidden=True)
app.add_typer(model_app, name="model", hidden=True)
app.add_typer(template_app, name="template", hidden=True)
app.add_typer(workflow_app, name="workflow", hidden=True)

# CLI context management (replaces global state)
from persona.ui.context import (
    get_cli_context,
    get_interactive,
    get_no_color,
    get_quiet,
    get_verbosity,
    reset_cli_context,
    set_interactive,
    set_no_color,
    set_quiet,
    set_verbosity,
)


def get_console():
    """Get console with current context settings."""
    ctx = get_cli_context()
    return _get_console(no_color=ctx.no_color, quiet=ctx.quiet, verbosity=ctx.verbosity)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from persona import __version__

        console = get_console()
        console.print(f"Persona {__version__}")
        raise typer.Exit()


def no_color_callback(value: bool) -> None:
    """Set no-color mode via context."""
    set_no_color(bool(value))


def quiet_callback(value: bool) -> None:
    """Set quiet mode via context."""
    set_quiet(bool(value))


def verbose_callback(value: int) -> None:
    """Set verbosity level via context.

    Can be called multiple times (-v -v) to increase verbosity.
    """
    if value:
        set_verbosity(min(value + 1, 3))  # +1 because normal is 1, cap at 3 (debug)


def interactive_callback(value: bool) -> None:
    """Set interactive mode via context."""
    set_interactive(bool(value))


def _reset_globals() -> None:
    """Reset context state (for testing)."""
    reset_cli_context()


def is_interactive() -> bool:
    """Check if interactive mode is enabled."""
    return get_interactive()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
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
            "--quiet",
            "-q",
            callback=quiet_callback,
            is_eager=True,
            help="Minimal output (errors and results only).",
        ),
    ] = None,
    verbose: Annotated[
        int,
        typer.Option(
            "--verbose",
            "-v",
            callback=verbose_callback,
            count=True,
            is_eager=True,
            help="Increase output verbosity. Use -v for verbose, -vv for debug.",
        ),
    ] = 0,
    interactive: Annotated[
        Optional[bool],
        typer.Option(
            "--interactive",
            "-i",
            callback=interactive_callback,
            is_eager=True,
            help="Run in interactive mode with guided prompts.",
        ),
    ] = None,
    ctx: typer.Context = None,
) -> None:
    """Generate realistic user personas from your data using AI."""
    # If a subcommand was invoked, let it handle things
    if ctx and ctx.invoked_subcommand is not None:
        return

    # If interactive mode is set, launch the generate wizard
    if get_interactive():
        from pathlib import Path

        from persona.core.data import DataLoader
        from persona.core.generation import GenerationConfig, GenerationPipeline
        from persona.core.output import OutputManager
        from persona.core.providers import ProviderFactory
        from persona.ui.interactive import GenerateWizard, is_interactive_supported
        from persona.ui.streaming import get_progress_handler

        console = get_console()

        if not is_interactive_supported():
            console.print(
                "[yellow]Interactive mode not supported in non-TTY environment.[/yellow]"
            )
            raise typer.Exit(1)

        wizard = GenerateWizard()
        result = wizard.run()
        if result is None:
            raise typer.Exit(0)

        # Run generation with wizard results
        from persona import __version__

        console.print(f"[dim]Persona {__version__}[/dim]\n")

        data_path = result["data_path"]
        provider = result["provider"]
        model = result.get("model")
        count = result["count"]
        workflow = result.get("workflow", "default")

        # Load data
        console.print(f"[bold]Loading data from:[/bold] {data_path}")
        loader = DataLoader()
        try:
            data, _files = loader.load_path(data_path)
        except (FileNotFoundError, ValueError, OSError) as e:
            console.print(f"[red]Error loading data:[/red] {e}")
            raise typer.Exit(1)

        token_count = loader.count_tokens(data)
        console.print(
            f"[green]✓[/green] Loaded {len(data)} characters ({token_count:,} tokens)"
        )

        # Create provider
        try:
            llm_provider = ProviderFactory.create(provider)
            if not llm_provider.is_configured():
                console.print(f"[red]Error:[/red] {provider} is not configured.")
                raise typer.Exit(1)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

        # Configure and run generation
        config = GenerationConfig(
            data_path=data_path,
            provider=provider,
            model=model or llm_provider.default_model,
            count=count,
            workflow=workflow,
        )

        progress_handler = get_progress_handler(
            console=console._console if hasattr(console, "_console") else console,
            show_progress=True,
        )

        progress_callback = progress_handler.start(
            total=config.count,
            provider=config.provider,
            model=config.model,
        )

        try:
            pipeline = GenerationPipeline()
            pipeline.set_progress_callback(progress_callback)
            gen_result = pipeline.generate(config)
            progress_handler.finish(
                personas=gen_result.personas,
                input_tokens=gen_result.input_tokens,
                output_tokens=gen_result.output_tokens,
            )
        except (ValueError, RuntimeError, OSError) as e:
            progress_handler.error(str(e))
            raise typer.Exit(1)

        # Save output
        output_dir = Path("./outputs")
        manager = OutputManager(base_dir=output_dir)
        output_path = manager.save(gen_result)
        console.print(f"[green]✓[/green] Saved to: {output_path}")

        # Show summary
        console.print(
            f"\n[bold green]Generated {len(gen_result.personas)} personas:[/bold green]"
        )
        for i, persona in enumerate(gen_result.personas, 1):
            console.print(f"  {i}. [bold]{persona.name}[/bold] ({persona.id})")

        return

    # No command and no -i flag: this is handled by no_args_is_help=True
    # But if we get here somehow, just return
    return


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
        except (ValueError, ImportError, OSError):
            # Provider unavailable or not properly installed
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
    Panel = _get_panel()
    console.print(
        Panel.fit(
            "[bold]Persona Health Check[/bold]",
            border_style="green",
        )
    )

    # Version and installation
    console.print(f"\n[green]✓[/green] Version: {__version__}")
    console.print("[green]✓[/green] Installation: OK")

    # Provider status
    console.print("\n[bold]Provider Status:[/bold]")

    for provider_name, env_var in providers_config:
        status = provider_status[provider_name]
        if status.get("error"):
            console.print(f"  [red]✗[/red] {provider_name}: Error")
        elif status["configured"]:
            console.print(f"  [green]✓[/green] {provider_name}: Configured")
        else:
            console.print(
                f"  [yellow]○[/yellow] {provider_name}: Not configured ({env_var})"
            )

    if configured_count == 0:
        console.print("\n[yellow]Warning:[/yellow] No providers configured.")
        console.print("Set at least one API key to start generating personas:\n")
        console.print("  [bold]Option 1 - Persistent (recommended):[/bold]")
        console.print("    Add to .env file: ANTHROPIC_API_KEY=your-key\n")
        console.print("  [bold]Option 2 - Current session only:[/bold]")
        console.print("    export ANTHROPIC_API_KEY=your-key")
        console.print("    export OPENAI_API_KEY=your-key")
        console.print("    export GOOGLE_API_KEY=your-key\n")
        console.print(
            "  Run [cyan]persona help api-keys[/cyan] for detailed setup instructions."
        )
    else:
        console.print(
            f"\n[green]Ready![/green] {configured_count} provider(s) available."
        )


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
                    "input_cost": float(estimate.input_cost)
                    if estimate.pricing
                    else None,
                    "output_cost": float(estimate.output_cost)
                    if estimate.pricing
                    else None,
                    "total_cost": float(estimate.total_cost)
                    if estimate.pricing
                    else None,
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
            console.print(
                f"  Input:  {estimate.input_tokens:,} tokens @ ${float(estimate.pricing.input_price)}/M = {estimator.format_cost(estimate.input_cost)}"
            )
            console.print(
                f"  Output: {estimate.output_tokens:,} tokens @ ${float(estimate.pricing.output_price)}/M = {estimator.format_cost(estimate.output_cost)}"
            )
            console.print(
                f"  [bold]Total: {estimator.format_cost(estimate.total_cost)}[/bold]"
            )
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
                            "input_cost": float(est.input_cost)
                            if est.pricing
                            else None,
                            "output_cost": float(est.output_cost)
                            if est.pricing
                            else None,
                            "total_cost": float(est.total_cost)
                            if est.pricing
                            else None,
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
            console.print(
                "[yellow]Specify --from or --tokens for accurate estimates.[/yellow]"
            )
        console.print(f"[bold]Personas:[/bold] {count}")
        console.print()

        Table = _get_table()
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
            console.print(
                f"\n[dim]Estimates based on {input_tokens:,} input tokens + ~{estimates[0].output_tokens:,} output tokens[/dim]"
            )


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
        except (ValueError, ImportError, OSError):
            # Provider unavailable or not properly installed
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
            result["data"]["providers"][pricing.provider]["models"].append(
                {
                    "name": pricing.model,
                    "input_price": float(pricing.input_price),
                    "output_price": float(pricing.output_price),
                    "default": pricing.model
                    in [
                        "claude-sonnet-4-20250514",
                        "gpt-4o",
                        "gemini-2.0-flash",
                    ],
                }
            )

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
    name: Annotated[
        Optional[str],
        typer.Argument(
            help="Project name (creates directory with this name).",
        ),
    ] = None,
    path: Annotated[
        Optional[Path],
        typer.Option(
            "--path",
            "-p",
            help="Parent directory for project (defaults to current directory).",
        ),
    ] = None,
) -> None:
    """
    Initialise a new Persona project.

    Creates the recommended directory structure for managing
    experiments and data.

    Examples:
        persona init my-research
        persona init my-research --path ~/projects/
    """
    from persona import __version__

    console = get_console()
    console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Prompt for name if not provided
    if not name:
        import questionary

        name = questionary.text(
            "Project name:",
            validate=lambda x: len(x) > 0 or "Project name is required",
        ).ask()
        if not name:
            console.print("[red]Cancelled[/red]")
            raise typer.Exit(1)

    # Determine target directory
    parent = path or Path.cwd()
    target = (parent / name).resolve()

    console.print(f"[bold]Initialising Persona project:[/bold] {name}")
    console.print(f"[dim]Location: {target}[/dim]\n")

    # Check if directory already exists
    if target.exists():
        console.print(f"[yellow]Warning:[/yellow] Directory already exists: {target}")
        import questionary

        if not questionary.confirm("Continue anyway?", default=False).ask():
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(0)

    # Create directory structure
    dirs = [
        target / "data",
        target / "output",
        target / "templates",
    ]

    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        console.print(f"  [green]✓[/green] Created: {d.relative_to(target)}/")

    # Create project config
    config_path = target / "persona.yaml"
    if not config_path.exists():
        config_content = f"""# Persona Project: {name}
# See: https://github.com/REPPL/Persona

project:
  name: {name}

defaults:
  provider: anthropic
  count: 3
  workflow: default
  complexity: moderate
  detail_level: standard
"""
        config_path.write_text(config_content)
        console.print("  [green]✓[/green] Created: persona.yaml")

    console.print(f"\n[green]Project '{name}' initialised![/green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print(f"  1. cd {name}")
    console.print("  2. Add your data files to ./data/")
    console.print("  3. Run: persona generate --from ./data/your-file.csv")


if __name__ == "__main__":
    app()
