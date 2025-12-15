"""
Generate command for creating personas from data.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.data import DataLoader
from persona.core.generation import GenerationPipeline, GenerationConfig
from persona.core.output import OutputManager
from persona.core.providers import ProviderFactory
from persona.ui.console import get_console
from persona.ui.interactive import GenerateWizard, is_interactive_supported
from persona.ui.completers import complete_provider, complete_model, complete_workflow
from persona.ui.streaming import StreamingOutput, get_progress_handler

generate_app = typer.Typer(
    name="generate",
    help="Generate personas from data files.",
)


@generate_app.callback(invoke_without_command=True)
def generate(
    ctx: typer.Context,
    data_path: Annotated[
        Optional[Path],
        typer.Option(
            "--from",
            "-f",
            help="Path to data file, directory, or experiment name.",
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output directory for generated personas.",
        ),
    ] = None,
    count: Annotated[
        Optional[int],
        typer.Option(
            "--count",
            "-n",
            help="Number of personas to generate.",
        ),
    ] = None,
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="LLM provider to use (anthropic, openai, gemini).",
            autocompletion=complete_provider,
        ),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help="Model to use (defaults to provider's default).",
            autocompletion=complete_model,
        ),
    ] = None,
    workflow: Annotated[
        Optional[str],
        typer.Option(
            "--workflow",
            "-w",
            help="Workflow to use (default, research, quick).",
            autocompletion=complete_workflow,
        ),
    ] = None,
    experiment: Annotated[
        Optional[str],
        typer.Option(
            "--experiment",
            "-e",
            help="Experiment name to save results under.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Preview generation without calling LLM.",
        ),
    ] = False,
    no_progress: Annotated[
        bool,
        typer.Option(
            "--no-progress",
            help="Disable progress bar and streaming output.",
        ),
    ] = False,
    anonymise: Annotated[
        bool,
        typer.Option(
            "--anonymise",
            help="Anonymise PII in data before generation.",
        ),
    ] = False,
    anonymise_strategy: Annotated[
        str,
        typer.Option(
            "--anonymise-strategy",
            help="Anonymisation strategy: redact, replace, hash (default: redact).",
        ),
    ] = "redact",
) -> None:
    """
    Generate personas from data files.

    Example:
        persona generate --from ./data/interviews.csv --count 3
        persona generate -i  # Interactive mode
        persona generate --from sensitive.csv --anonymise
        persona generate --from data.csv --anonymise --anonymise-strategy replace
    """
    if ctx.invoked_subcommand is not None:
        return

    # Check for interactive mode
    from persona.ui.cli import is_interactive
    if is_interactive():
        if not is_interactive_supported():
            console = get_console()
            console.print("[yellow]Interactive mode not supported in non-TTY environment.[/yellow]")
            console.print("Use explicit flags instead.")
            raise typer.Exit(1)

        wizard = GenerateWizard()
        result = wizard.run(
            data_path=data_path,
            provider=provider,
            model=model,
            count=count,
            workflow=workflow,
        )
        if result is None:
            raise typer.Exit(0)

        # Use wizard results
        data_path = result["data_path"]
        provider = result["provider"]
        model = result["model"]
        count = result["count"]
        workflow = result["workflow"]
    else:
        # Non-interactive mode - require data_path
        if data_path is None:
            console = get_console()
            console.print("[red]Error:[/red] --from is required.")
            console.print("Use 'persona generate --from ./data.csv' or 'persona generate -i' for interactive mode.")
            raise typer.Exit(1)

        # Apply defaults for non-interactive mode
        if count is None:
            count = 3
        if provider is None:
            provider = "anthropic"
        if workflow is None:
            workflow = "default"

    console = get_console()

    from persona import __version__
    console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Resolve data path (supports experiment names)
    try:
        resolved_path = _resolve_data_path(data_path)
        if resolved_path != data_path:
            console.print(f"[dim]Resolved '{data_path}' → {resolved_path}[/dim]")
        data_path = resolved_path
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Load data
    console.print(f"[bold]Loading data from:[/bold] {data_path}")
    loader = DataLoader()

    try:
        data, _files = loader.load_path(data_path)
    except Exception as e:
        console.print(f"[red]Error loading data:[/red] {e}")
        raise typer.Exit(1)

    # Show data summary
    token_count = loader.count_tokens(data)
    console.print(f"[green]✓[/green] Loaded {len(data)} characters ({token_count:,} tokens)")

    # Anonymise if requested
    if anonymise:
        try:
            from persona.core.privacy import (
                PIIDetector,
                PIIAnonymiser,
                AnonymisationStrategy,
            )
        except ImportError:
            console.print(
                "[red]Error:[/red] Privacy module not installed.\n"
                "Install with: [cyan]pip install persona[privacy][/cyan]\n"
                "Then run: [cyan]python -m spacy download en_core_web_lg[/cyan]"
            )
            raise typer.Exit(1)

        console.print("[dim]Anonymising PII...[/dim]")

        # Validate strategy
        try:
            anon_strategy = AnonymisationStrategy(anonymise_strategy.lower())
        except ValueError:
            console.print(
                f"[red]Error:[/red] Invalid strategy '{anonymise_strategy}'. "
                "Choose from: redact, replace, hash"
            )
            raise typer.Exit(1)

        # Detect and anonymise
        try:
            detector = PIIDetector()
            if not detector.is_available():
                error = detector.get_import_error()
                console.print(
                    f"[red]Error:[/red] PII detection not available.\n"
                    f"Install with: [cyan]pip install persona[privacy][/cyan]\n"
                    f"Original error: {error}"
                )
                raise typer.Exit(1)

            anonymiser = PIIAnonymiser()
            if not anonymiser.is_available():
                error = anonymiser.get_import_error()
                console.print(
                    f"[red]Error:[/red] PII anonymisation not available.\n"
                    f"Install with: [cyan]pip install persona[privacy][/cyan]\n"
                    f"Original error: {error}"
                )
                raise typer.Exit(1)

            entities = detector.detect(data)
            if entities:
                result = anonymiser.anonymise(data, entities, anon_strategy)
                data = result.text
                console.print(
                    f"[green]✓[/green] Anonymised {result.entity_count} PII "
                    f"entities ({', '.join(sorted(result.entity_types))})"
                )
            else:
                console.print("[green]✓[/green] No PII detected")
        except Exception as e:
            console.print(f"[red]Error anonymising data:[/red] {e}")
            raise typer.Exit(1)

    # Configure generation (before provider check for dry_run)
    config = GenerationConfig(
        data_path=data_path,
        provider=provider,
        model=model,
        count=count,
        workflow=workflow,
    )

    # Show configuration
    _show_config(console, config, data_path, token_count)

    if dry_run:
        console.print("\n[yellow]Dry run - no LLM call made.[/yellow]")
        return

    # Create provider (only needed for actual generation)
    try:
        llm_provider = ProviderFactory.create(provider)
        if not llm_provider.is_configured():
            console.print(f"[red]Error:[/red] {provider} is not configured.")
            console.print(f"Set the {_get_api_key_env(provider)} environment variable.")
            raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Update config with actual model
    config = GenerationConfig(
        data_path=data_path,
        provider=provider,
        model=model or llm_provider.default_model,
        count=count,
        workflow=workflow,
    )

    # Generate personas with streaming output
    progress_handler = get_progress_handler(
        console=console._console if hasattr(console, "_console") else console,
        show_progress=not no_progress,
    )

    progress_callback = progress_handler.start(
        total=config.count,
        provider=config.provider,
        model=config.model or llm_provider.default_model,
    )

    try:
        pipeline = GenerationPipeline()
        pipeline.set_progress_callback(progress_callback)
        result = pipeline.generate(config)
        progress_handler.finish(
            personas=result.personas,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
        )
    except Exception as e:
        progress_handler.error(str(e))
        raise typer.Exit(1)

    # Save output
    output_dir = output or Path("./outputs")
    manager = OutputManager(base_dir=output_dir)

    output_path = manager.save(result, name=experiment)
    console.print(f"[green]✓[/green] Saved to: {output_path}")

    # Show summary
    _show_result_summary(console, result)


def _get_api_key_env(provider: str) -> str:
    """Get the environment variable name for a provider's API key."""
    env_vars = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "google": "GOOGLE_API_KEY",
    }
    return env_vars.get(provider.lower(), f"{provider.upper()}_API_KEY")


def _resolve_data_path(path: Path) -> Path:
    """Resolve data path, supporting experiment names.

    Allows users to specify:
    - Direct paths: ./data/interviews.csv
    - Experiment names: my-experiment (resolves to experiments/my-experiment/data/)

    Args:
        path: The path or experiment name provided by the user.

    Returns:
        Resolved Path to the data location.

    Raises:
        FileNotFoundError: If the path cannot be resolved.
    """
    # If path exists directly, use it
    if path.exists():
        return path

    # Try as experiment name: experiments/<name>/data/
    experiment_data_path = Path("experiments") / path / "data"
    if experiment_data_path.exists():
        return experiment_data_path

    # Try in experiments/ directly: experiments/<name>
    experiment_path = Path("experiments") / path
    if experiment_path.exists():
        return experiment_path

    # Nothing found - provide helpful error message
    raise FileNotFoundError(
        f"Path not found: {path}\n"
        f"Tried:\n"
        f"  - {path}\n"
        f"  - {experiment_data_path}\n"
        f"  - {experiment_path}"
    )


def _show_config(console, config: GenerationConfig, data_path: Path, token_count: int) -> None:
    """Display generation configuration."""
    table = Table(title="Generation Configuration", show_header=False)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    table.add_row("Data source", str(data_path))
    table.add_row("Token count", f"{token_count:,}")
    table.add_row("Provider", config.provider)
    table.add_row("Model", str(config.model or "default"))
    table.add_row("Persona count", str(config.count))
    table.add_row("Workflow", config.workflow)

    console.print(table)


def _show_result_summary(console, result) -> None:
    """Display generation result summary."""
    console.print(f"\n[bold green]Generated {len(result.personas)} personas:[/bold green]")

    for i, persona in enumerate(result.personas, 1):
        console.print(f"  {i}. [bold]{persona.name}[/bold] ({persona.id})")

    console.print(f"\n[dim]Tokens used: {result.input_tokens + result.output_tokens:,} "
                  f"(in: {result.input_tokens:,}, out: {result.output_tokens:,})[/dim]")
