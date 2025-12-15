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
    hybrid: Annotated[
        bool,
        typer.Option(
            "--hybrid",
            help="Use hybrid local/frontier pipeline for cost-efficient generation.",
        ),
    ] = False,
    local_model: Annotated[
        Optional[str],
        typer.Option(
            "--local-model",
            help="Local model for hybrid mode (default: qwen2.5:7b).",
        ),
    ] = None,
    frontier_provider: Annotated[
        Optional[str],
        typer.Option(
            "--frontier-provider",
            help="Frontier provider for hybrid refinement (anthropic, openai, gemini).",
        ),
    ] = None,
    frontier_model: Annotated[
        Optional[str],
        typer.Option(
            "--frontier-model",
            help="Frontier model for hybrid refinement.",
        ),
    ] = None,
    quality_threshold: Annotated[
        float,
        typer.Option(
            "--quality-threshold",
            help="Minimum quality score to skip frontier refinement (0.0-1.0).",
        ),
    ] = 0.7,
    max_cost: Annotated[
        Optional[float],
        typer.Option(
            "--max-cost",
            help="Maximum budget in USD for hybrid generation.",
        ),
    ] = None,
    no_frontier: Annotated[
        bool,
        typer.Option(
            "--no-frontier",
            help="Use local-only mode in hybrid pipeline (no frontier refinement).",
        ),
    ] = False,
    verify: Annotated[
        bool,
        typer.Option(
            "--verify",
            help="Run multi-model verification after generation.",
        ),
    ] = False,
    verify_models: Annotated[
        Optional[str],
        typer.Option(
            "--verify-models",
            help="Comma-separated models for verification (default: claude,gpt-4o,gemini).",
        ),
    ] = None,
    verify_threshold: Annotated[
        float,
        typer.Option(
            "--verify-threshold",
            help="Consistency threshold for verification (0-1, default: 0.7).",
        ),
    ] = 0.7,
) -> None:
    """
    Generate personas from data files.

    Example:
        persona generate --from ./data/interviews.csv --count 3
        persona generate -i  # Interactive mode
        persona generate --from sensitive.csv --anonymise
        persona generate --from data.csv --anonymise --anonymise-strategy replace

        # Hybrid mode examples
        persona generate --from data.csv --hybrid --count 10
        persona generate --from data.csv --hybrid --no-frontier  # Local-only
        persona generate --from data.csv --hybrid --frontier-provider anthropic --max-cost 5.0
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

    # Handle hybrid mode
    if hybrid:
        return _handle_hybrid_generation(
            console=console,
            data=data,
            count=count or 3,
            local_model=local_model,
            frontier_provider=frontier_provider if not no_frontier else None,
            frontier_model=frontier_model,
            quality_threshold=quality_threshold,
            max_cost=max_cost,
            output=output,
            experiment=experiment,
            dry_run=dry_run,
        )

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

    # Run verification if requested
    if verify:
        _run_verification(
            console=console,
            data=data,
            count=count,
            verify_models=verify_models,
            verify_threshold=verify_threshold,
            no_progress=no_progress,
        )


def _handle_hybrid_generation(
    console,
    data: str,
    count: int,
    local_model: Optional[str],
    frontier_provider: Optional[str],
    frontier_model: Optional[str],
    quality_threshold: float,
    max_cost: Optional[float],
    output: Optional[Path],
    experiment: Optional[str],
    dry_run: bool,
) -> None:
    """Handle hybrid pipeline generation."""
    import asyncio
    from persona.core.hybrid import HybridPipeline, HybridConfig

    console.print("\n[bold cyan]Hybrid Pipeline Mode[/bold cyan]")

    # Build hybrid configuration
    try:
        config = HybridConfig(
            local_model=local_model or "qwen2.5:7b",
            frontier_provider=frontier_provider,
            frontier_model=frontier_model,
            quality_threshold=quality_threshold,
            max_cost=max_cost,
        )
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid configuration: {e}")
        raise typer.Exit(1)

    # Show hybrid configuration
    _show_hybrid_config(console, config, count)

    if dry_run:
        console.print("\n[yellow]Dry run - no LLM call made.[/yellow]")
        return

    # Create pipeline
    pipeline = HybridPipeline(config)

    # Generate personas
    console.print("\n[dim]Starting hybrid generation...[/dim]")
    try:
        # Run async generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(pipeline.generate(data, count))
        loop.close()
    except Exception as e:
        console.print(f"[red]Error during generation:[/red] {e}")
        raise typer.Exit(1)

    # Show results
    _show_hybrid_result(console, result)

    # Save output
    output_dir = output or Path("./outputs")
    from persona.core.output import OutputManager

    manager = OutputManager(base_dir=output_dir)

    # Convert hybrid result to format compatible with OutputManager
    # We need to adapt the personas to the expected format
    from persona.core.generation import PersonaData

    personas = []
    for p in result.personas:
        persona = PersonaData(
            id=p.get("id", "unknown"),
            name=p.get("name", "Unknown"),
            raw_data=p,
        )
        personas.append(persona)

    # Create a minimal result object for saving
    from persona.core.generation import GenerationResult

    generation_result = GenerationResult(
        personas=personas,
        input_tokens=result.total_tokens // 2,  # Rough estimate
        output_tokens=result.total_tokens // 2,
        config=None,
    )

    output_path = manager.save(generation_result, name=experiment)
    console.print(f"\n[green]✓[/green] Saved to: {output_path}")


def _show_hybrid_config(console, config: "HybridConfig", count: int) -> None:
    """Display hybrid configuration."""
    from rich.table import Table

    table = Table(title="Hybrid Configuration", show_header=False)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    table.add_row("Pipeline mode", "Hybrid" if config.is_hybrid_mode else "Local-only")
    table.add_row("Persona count", str(count))
    table.add_row("Local model", config.local_model)

    if config.is_hybrid_mode:
        table.add_row("Frontier provider", config.frontier_provider or "None")
        table.add_row("Frontier model", config.frontier_model or "None")
        table.add_row("Quality threshold", f"{config.quality_threshold:.2f}")

    if config.max_cost:
        table.add_row("Max cost", f"${config.max_cost:.2f}")

    console.print(table)


def _show_hybrid_result(console, result: "HybridResult") -> None:
    """Display hybrid generation result."""
    from rich.table import Table

    console.print(f"\n[bold green]Generated {result.persona_count} personas:[/bold green]")

    # Show persona list
    for i, persona in enumerate(result.personas[:10], 1):  # Show first 10
        name = persona.get("name", "Unknown")
        persona_id = persona.get("id", "unknown")
        is_refined = persona.get("_refined", False)
        status = "[yellow]refined[/yellow]" if is_refined else "[green]draft[/green]"
        console.print(f"  {i}. [bold]{name}[/bold] ({persona_id}) {status}")

    if result.persona_count > 10:
        console.print(f"  ... and {result.persona_count - 10} more")

    # Show statistics
    console.print(f"\n[bold]Pipeline Statistics:[/bold]")
    console.print(f"  Drafts generated: {result.draft_count}")
    console.print(f"  Passed threshold: {result.passing_count}")
    console.print(f"  Refined by frontier: {result.refined_count}")

    # Show costs
    costs = result.cost_tracker.to_dict()
    console.print(f"\n[bold]Costs:[/bold]")
    console.print(f"  Local: ${costs['local']['cost']:.4f}")
    console.print(f"  Judge: ${costs['judge']['cost']:.4f}")
    console.print(f"  Frontier: ${costs['frontier']['cost']:.4f}")
    console.print(f"  [bold]Total: ${costs['total']['cost']:.4f}[/bold]")

    if costs["budget"]["max"]:
        remaining = costs["budget"]["remaining"]
        console.print(f"  Budget remaining: ${remaining:.4f}")

    console.print(f"\n[dim]Generation time: {result.generation_time:.1f}s[/dim]")


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


def _run_verification(
    console,
    data: str,
    count: int,
    verify_models: Optional[str],
    verify_threshold: float,
    no_progress: bool,
) -> None:
    """Run multi-model verification after generation."""
    import asyncio
    from persona.core.quality.verification import (
        MultiModelVerifier,
        VerificationConfig,
    )

    console.print("\n[bold cyan]Running Multi-Model Verification[/bold cyan]")

    # Parse models
    if verify_models:
        model_list = [m.strip() for m in verify_models.split(",")]
    else:
        # Default verification models
        model_list = ["claude-sonnet-4-20250514", "gpt-4o", "gemini-2.0-flash"]

    console.print(f"[dim]Comparing outputs from: {', '.join(model_list)}[/dim]\n")

    # Create verification config
    config = VerificationConfig(
        models=model_list,
        samples_per_model=1,
        voting_strategy="majority",
        consistency_threshold=verify_threshold,
        parallel=True,
    )

    # Create verifier
    verifier = MultiModelVerifier(config)

    # Run verification
    try:
        if not no_progress:
            with console.status("[bold cyan]Verifying consistency...", spinner="dots"):
                result = asyncio.run(verifier.verify(data, count=count))
        else:
            result = asyncio.run(verifier.verify(data, count=count))

        # Display results
        from rich.panel import Panel
        from rich.text import Text
        from rich.table import Table

        # Status panel
        status_text = Text()
        if result.passed:
            status_text.append("✓ PASSED", style="bold green")
        else:
            status_text.append("✗ FAILED", style="bold red")

        status_text.append(f"\nConsistency Score: {result.consistency_score:.2%}")
        status_text.append(f"\nThreshold: {result.config.consistency_threshold:.2%}")

        console.print(Panel(
            status_text,
            title="[bold]Verification Result[/bold]",
            border_style="green" if result.passed else "red",
        ))

        # Metrics summary
        console.print("\n[bold]Consistency Metrics:[/bold]")
        console.print(f"  Attribute Agreement: {result.metrics.attribute_agreement:.2%}")
        console.print(f"  Semantic Consistency: {result.metrics.semantic_consistency:.2%}")
        console.print(f"  Factual Convergence: {result.metrics.factual_convergence:.2%}")

        # Attribute summary
        console.print(f"\n[bold]Attributes:[/bold]")
        console.print(f"  Agreed: {len(result.agreed_attributes)}")
        console.print(f"  Disputed: {len(result.disputed_attributes)}")

        if not result.passed:
            console.print("\n[yellow]Warning:[/yellow] Verification failed. Consider:")
            console.print("  - Reviewing disputed attributes")
            console.print("  - Adjusting the consistency threshold")
            console.print("  - Using more specific prompts")

    except Exception as e:
        console.print(f"\n[red]Verification error:[/red] {e}")
        console.print("[yellow]Generation succeeded, but verification failed.[/yellow]")
