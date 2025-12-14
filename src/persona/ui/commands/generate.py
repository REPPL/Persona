"""
Generate command for creating personas from data.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from persona.core.data import DataLoader
from persona.core.generation import GenerationPipeline, GenerationConfig
from persona.core.output import OutputManager
from persona.core.providers import ProviderFactory

generate_app = typer.Typer(
    name="generate",
    help="Generate personas from data files.",
)

console = Console()


@generate_app.callback(invoke_without_command=True)
def generate(
    ctx: typer.Context,
    data_path: Annotated[
        Path,
        typer.Option(
            "--from",
            "-f",
            help="Path to data file or directory.",
            exists=True,
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output directory for generated personas.",
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
        str,
        typer.Option(
            "--provider",
            "-p",
            help="LLM provider to use (anthropic, openai, gemini).",
        ),
    ] = "anthropic",
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help="Model to use (defaults to provider's default).",
        ),
    ] = None,
    workflow: Annotated[
        str,
        typer.Option(
            "--workflow",
            "-w",
            help="Workflow to use (default, research, quick).",
        ),
    ] = "default",
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
) -> None:
    """
    Generate personas from data files.

    Example:
        persona generate --from ./data/interviews.csv --count 3
    """
    if ctx.invoked_subcommand is not None:
        return

    # Load data
    console.print(f"[bold]Loading data from:[/bold] {data_path}")
    loader = DataLoader()

    try:
        if data_path.is_dir():
            data = loader.load_directory(data_path)
        else:
            data = loader.load_file(data_path)
    except Exception as e:
        console.print(f"[red]Error loading data:[/red] {e}")
        raise typer.Exit(1)

    # Show data summary
    token_count = loader.count_tokens(data)
    console.print(f"[green]✓[/green] Loaded {len(data)} characters ({token_count:,} tokens)")

    # Configure generation (before provider check for dry_run)
    config = GenerationConfig(
        data_path=data_path,
        provider=provider,
        model=model,
        count=count,
        workflow=workflow,
    )

    # Show configuration
    _show_config(config, data_path, token_count)

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

    # Generate personas
    console.print("\n[bold]Generating personas...[/bold]")

    try:
        pipeline = GenerationPipeline(llm_provider)
        result = pipeline.generate(
            data=data,
            config=config,
            source_files=[data_path] if data_path.is_file() else list(data_path.glob("*")),
        )
    except Exception as e:
        console.print(f"[red]Error during generation:[/red] {e}")
        raise typer.Exit(1)

    # Save output
    output_dir = output or Path("./outputs")
    manager = OutputManager(base_dir=output_dir)

    output_path = manager.save(result, name=experiment)
    console.print(f"[green]✓[/green] Saved to: {output_path}")

    # Show summary
    _show_result_summary(result)


def _get_api_key_env(provider: str) -> str:
    """Get the environment variable name for a provider's API key."""
    env_vars = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "gemini": "GOOGLE_API_KEY",
        "google": "GOOGLE_API_KEY",
    }
    return env_vars.get(provider.lower(), f"{provider.upper()}_API_KEY")


def _show_config(config: GenerationConfig, data_path: Path, token_count: int) -> None:
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


def _show_result_summary(result) -> None:
    """Display generation result summary."""
    console.print(f"\n[bold green]Generated {len(result.personas)} personas:[/bold green]")

    for i, persona in enumerate(result.personas, 1):
        console.print(f"  {i}. [bold]{persona.name}[/bold] ({persona.id})")

    console.print(f"\n[dim]Tokens used: {result.input_tokens + result.output_tokens:,} "
                  f"(in: {result.input_tokens:,}, out: {result.output_tokens:,})[/dim]")
