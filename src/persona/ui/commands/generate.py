"""
Generate command for creating personas from data.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.table import Table

from persona.core.data import DataLoader
from persona.core.generation import GenerationConfig, GenerationPipeline
from persona.core.output import OutputManager
from persona.core.providers import ProviderFactory
from persona.ui.completers import complete_model, complete_provider, complete_workflow
from persona.ui.console import get_console
from persona.ui.interactive import GenerateWizard, is_interactive_supported
from persona.ui.streaming import get_progress_handler

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
    local: Annotated[
        bool,
        typer.Option(
            "--local",
            help="Use all available local models (via Ollama).",
        ),
    ] = False,
    cloud: Annotated[
        bool,
        typer.Option(
            "--cloud",
            help="Use cloud/frontier providers (default behaviour).",
        ),
    ] = False,
    all_providers: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Use all available models (local and cloud).",
        ),
    ] = False,
) -> None:
    """
    Generate personas from data files.

    Example:
        persona generate --from ./data/interviews.csv --count 3
        persona generate -i  # Interactive mode
        persona generate --from sensitive.csv --anonymise

        # Provider selection shortcuts
        persona generate --from data.csv --local  # Use all local Ollama models
        persona generate --from data.csv --cloud  # Use cloud providers (default)
        persona generate --from data.csv --all    # Use all available models

        # Specific model selection
        persona generate --from data.csv --provider ollama --model llama3:8b
        persona generate --from data.csv --provider anthropic --model claude-sonnet-4-20250514

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
            console.print(
                "[yellow]Interactive mode not supported in non-TTY environment.[/yellow]"
            )
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
            console.print(
                "Use 'persona generate --from ./data.csv' or 'persona generate -i' for interactive mode."
            )
            raise typer.Exit(1)

        # Apply defaults for non-interactive mode
        if count is None:
            count = 3
        if provider is None:
            provider = "anthropic"
        if workflow is None:
            workflow = "default"

    console = get_console()

    # Handle shortcut flags (--local, --cloud, --all)
    if local or all_providers:
        # --local or --all: use all local models
        return _handle_multi_model_generation(
            console=console,
            data_path=data_path,
            output=output,
            count=count,
            workflow=workflow,
            experiment=experiment,
            dry_run=dry_run,
            no_progress=no_progress,
            anonymise=anonymise,
            anonymise_strategy=anonymise_strategy,
            verify=verify,
            verify_models=verify_models,
            verify_threshold=verify_threshold,
            include_cloud=all_providers,
        )

    # Handle Ollama model selection when provider is ollama but no model specified
    if provider == "ollama" and not model:
        model, use_all = _handle_ollama_model_selection(
            console=console,
            all_models=False,
        )
        if model is None and not use_all:
            # User cancelled selection
            raise typer.Exit(0)
        if use_all:
            return _handle_multi_model_generation(
                console=console,
                data_path=data_path,
                output=output,
                count=count,
                workflow=workflow,
                experiment=experiment,
                dry_run=dry_run,
                no_progress=no_progress,
                anonymise=anonymise,
                anonymise_strategy=anonymise_strategy,
                verify=verify,
                verify_models=verify_models,
                verify_threshold=verify_threshold,
                include_cloud=False,
            )

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
    console.print(
        f"[green]✓[/green] Loaded {len(data)} characters ({token_count:,} tokens)"
    )

    # Anonymise if requested
    if anonymise:
        try:
            from persona.core.privacy import (
                AnonymisationStrategy,
                PIIAnonymiser,
                PIIDetector,
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

    # Save output (respect experiment directory structure)
    output_dir, save_name = _resolve_output_path(output, experiment)
    manager = OutputManager(base_dir=output_dir)

    output_path = manager.save(result, name=save_name)
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

    from persona.core.hybrid import HybridConfig, HybridPipeline

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

    # Save output (respect experiment directory structure)
    output_dir, save_name = _resolve_output_path(output, experiment)
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

    output_path = manager.save(generation_result, name=save_name)
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

    console.print(
        f"\n[bold green]Generated {result.persona_count} personas:[/bold green]"
    )

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
    console.print("\n[bold]Pipeline Statistics:[/bold]")
    console.print(f"  Drafts generated: {result.draft_count}")
    console.print(f"  Passed threshold: {result.passing_count}")
    console.print(f"  Refined by frontier: {result.refined_count}")

    # Show costs
    costs = result.cost_tracker.to_dict()
    console.print("\n[bold]Costs:[/bold]")
    console.print(f"  Local: ${costs['local']['cost']:.4f}")
    console.print(f"  Judge: ${costs['judge']['cost']:.4f}")
    console.print(f"  Frontier: ${costs['frontier']['cost']:.4f}")
    console.print(f"  [bold]Total: ${costs['total']['cost']:.4f}[/bold]")

    if costs["budget"]["max"]:
        remaining = costs["budget"]["remaining"]
        console.print(f"  Budget remaining: ${remaining:.4f}")

    console.print(f"\n[dim]Generation time: {result.generation_time:.1f}s[/dim]")


def _handle_multi_model_generation(
    console,
    data_path: Path,
    output: Optional[Path],
    count: Optional[int],
    workflow: Optional[str],
    experiment: Optional[str],
    dry_run: bool,
    no_progress: bool,
    anonymise: bool,
    anonymise_strategy: str,
    verify: bool,
    verify_models: Optional[str],
    verify_threshold: float,
    include_cloud: bool = False,
) -> None:
    """Generate personas using multiple models.

    This runs generation for each model and saves results separately.

    Args:
        include_cloud: If True, also include cloud providers (anthropic, openai, gemini).
    """
    from rich.table import Table

    from persona import __version__
    from persona.core.data import DataLoader
    from persona.core.generation import GenerationConfig, GenerationPipeline
    from persona.core.output import OutputManager
    from persona.core.providers import ProviderFactory

    console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Build list of models to use
    models_to_use = []  # List of (provider, model) tuples

    # Get local Ollama models
    try:
        ollama_provider = ProviderFactory.create("ollama")
        if ollama_provider.is_configured():
            local_models = ollama_provider.list_available_models()
            for m in local_models:
                models_to_use.append(("ollama", m))
    except Exception as e:
        console.print(f"[yellow]Warning:[/yellow] Could not get Ollama models: {e}")

    # Add cloud providers if requested
    if include_cloud:
        cloud_configs = [
            ("anthropic", "claude-sonnet-4-20250514"),
            ("openai", "gpt-4o"),
            ("gemini", "gemini-2.5-flash"),
        ]
        for provider_name, model_name in cloud_configs:
            try:
                p = ProviderFactory.create(provider_name)
                if p.is_configured():
                    models_to_use.append((provider_name, model_name))
            except Exception:
                pass  # Skip unconfigured providers

    if not models_to_use:
        console.print("[red]Error:[/red] No models available.")
        console.print("Start Ollama with: [cyan]ollama serve[/cyan]")
        if include_cloud:
            console.print("Or configure a cloud provider API key.")
        raise typer.Exit(1)

    mode_name = "All Providers" if include_cloud else "Local Models"
    console.print(f"[bold cyan]{mode_name} Generation Mode[/bold cyan]")
    model_display = [f"{p}:{m}" for p, m in models_to_use]
    console.print(
        f"Running with {len(models_to_use)} models: {', '.join(model_display)}\n"
    )

    # Resolve data path
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

    token_count = loader.count_tokens(data)
    console.print(
        f"[green]✓[/green] Loaded {len(data)} characters ({token_count:,} tokens)\n"
    )

    # Anonymise if requested
    if anonymise:
        try:
            from persona.core.privacy import (
                AnonymisationStrategy,
                PIIAnonymiser,
                PIIDetector,
            )

            anon_strategy = AnonymisationStrategy(anonymise_strategy.lower())
            detector = PIIDetector()
            anonymiser = PIIAnonymiser()

            if detector.is_available() and anonymiser.is_available():
                entities = detector.detect(data)
                if entities:
                    result = anonymiser.anonymise(data, entities, anon_strategy)
                    data = result.text
                    console.print(
                        f"[green]✓[/green] Anonymised {result.entity_count} PII entities"
                    )
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Could not anonymise: {e}")

    if dry_run:
        console.print("[yellow]Dry run - no LLM calls made.[/yellow]")
        console.print(f"Would generate with models: {', '.join(model_display)}")
        return

    # Generate with each model (respect experiment directory structure)
    results_summary = []
    output_dir, _ = _resolve_output_path(output, experiment)
    manager = OutputManager(base_dir=output_dir)

    for i, (provider_name, model_name) in enumerate(models_to_use, 1):
        model_display_name = f"{provider_name}:{model_name}"
        console.print(
            f"\n[bold]Model {i}/{len(models_to_use)}: {model_display_name}[/bold]"
        )

        config = GenerationConfig(
            data_path=data_path,
            provider=provider_name,
            model=model_name,
            count=count or 3,
            workflow=workflow or "default",
        )

        try:
            pipeline = GenerationPipeline()

            # Simple progress for multi-model mode
            if not no_progress:
                with console.status(
                    f"[cyan]Generating with {model_display_name}...", spinner="dots"
                ):
                    result = pipeline.generate(config)
            else:
                result = pipeline.generate(config)

            # Save output with model name in experiment
            safe_name = model_name.replace(":", "-").replace("/", "-")
            exp_name = f"{experiment or 'multi-model'}-{provider_name}-{safe_name}"
            output_path = manager.save(result, name=exp_name)

            results_summary.append(
                {
                    "model": model_display_name,
                    "personas": len(result.personas),
                    "tokens": result.input_tokens + result.output_tokens,
                    "path": output_path,
                    "status": "success",
                }
            )
            console.print(
                f"[green]✓[/green] Generated {len(result.personas)} personas → {output_path}"
            )

        except Exception as e:
            results_summary.append(
                {
                    "model": model_display_name,
                    "personas": 0,
                    "tokens": 0,
                    "path": None,
                    "status": f"error: {e}",
                }
            )
            console.print(f"[red]✗[/red] Failed: {e}")

    # Summary table
    console.print("\n[bold]Multi-Model Generation Summary[/bold]")
    table = Table(show_header=True)
    table.add_column("Model", style="cyan")
    table.add_column("Personas", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("Status")

    total_personas = 0
    total_tokens = 0
    for r in results_summary:
        status_style = "green" if r["status"] == "success" else "red"
        table.add_row(
            r["model"],
            str(r["personas"]),
            f"{r['tokens']:,}",
            f"[{status_style}]{r['status']}[/{status_style}]",
        )
        total_personas += r["personas"]
        total_tokens += r["tokens"]

    table.add_row("", "", "", "", end_section=True)
    table.add_row(
        "[bold]Total[/bold]",
        f"[bold]{total_personas}[/bold]",
        f"[bold]{total_tokens:,}[/bold]",
        "",
    )

    console.print(table)
    console.print(f"\n[green]✓[/green] Results saved to: {output_dir}")


def _handle_ollama_model_selection(
    console,
    all_models: bool,
) -> tuple[Optional[str], bool]:
    """Handle Ollama model selection interactively or via --all-models flag.

    Args:
        console: Console instance for output.
        all_models: Whether --all-models flag was passed.

    Returns:
        Tuple of (selected_model, all_models_flag).
        If all_models is True, returns (None, True) to indicate multi-model mode.
        If user cancels, returns (None, False).
    """
    from persona.core.providers import ProviderFactory

    # Check if Ollama is running
    try:
        ollama_provider = ProviderFactory.create("ollama")
        if not ollama_provider.is_configured():
            console.print("[red]Error:[/red] Ollama is not running.")
            console.print("Start Ollama with: [cyan]ollama serve[/cyan]")
            return None, False

        available = ollama_provider.list_available_models()
        if not available:
            console.print("[red]Error:[/red] No models found in Ollama.")
            console.print("Pull a model with: [cyan]ollama pull llama3:8b[/cyan]")
            return None, False
    except Exception as e:
        console.print(f"[red]Error connecting to Ollama:[/red] {e}")
        return None, False

    # If --all-models flag, return all models mode
    if all_models:
        console.print(f"[dim]Using all {len(available)} local models[/dim]")
        return None, True

    # Interactive model selection
    console.print(f"[bold]Available Ollama models ({len(available)}):[/bold]")

    try:
        import questionary
    except ImportError:
        # Fallback: use first model if questionary not available
        console.print("[yellow]questionary not installed, using default model[/yellow]")
        default = ollama_provider.default_model
        console.print(f"[dim]Selected: {default}[/dim]")
        return default, False

    # Build choices with model info
    choices = []
    for model_name in available:
        choices.append(questionary.Choice(title=model_name, value=model_name))

    # Add "All models" option
    choices.append(
        questionary.Choice(
            title="[All models] - Generate with each model",
            value="__all__",
        )
    )

    # Prompt for selection
    selected = questionary.select(
        "Select a model:",
        choices=choices,
        default=ollama_provider.default_model
        if ollama_provider.default_model in available
        else None,
    ).ask()

    if selected is None:
        # User cancelled (Ctrl+C)
        return None, False

    if selected == "__all__":
        console.print(f"[dim]Using all {len(available)} local models[/dim]")
        return None, True

    console.print(f"[dim]Selected: {selected}[/dim]")
    return selected, False


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


def _resolve_output_path(
    output: Optional[Path], experiment: Optional[str]
) -> tuple[Path, Optional[str]]:
    """Resolve output path, respecting experiment structure.

    When an experiment is specified and no explicit output path is given,
    outputs are saved to the experiment's outputs directory.

    Args:
        output: Explicit output path from --output flag, if any.
        experiment: Experiment name from --experiment flag, if any.

    Returns:
        Tuple of (base_dir, save_name):
        - base_dir: Directory for OutputManager
        - save_name: Name to pass to save() (None for timestamp-based)
    """
    if output:
        # Explicit output path takes precedence
        return output, None

    if experiment:
        # Use experiment's outputs directory with timestamp subfolder
        return Path("experiments") / experiment / "outputs", None

    # Default: ./outputs with experiment name or timestamp
    return Path("./outputs"), experiment


def _show_config(
    console, config: GenerationConfig, data_path: Path, token_count: int
) -> None:
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
    console.print(
        f"\n[bold green]Generated {len(result.personas)} personas:[/bold green]"
    )

    for i, persona in enumerate(result.personas, 1):
        console.print(f"  {i}. [bold]{persona.name}[/bold] ({persona.id})")

    console.print(
        f"\n[dim]Tokens used: {result.input_tokens + result.output_tokens:,} "
        f"(in: {result.input_tokens:,}, out: {result.output_tokens:,})[/dim]"
    )


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

        # Status panel
        status_text = Text()
        if result.passed:
            status_text.append("✓ PASSED", style="bold green")
        else:
            status_text.append("✗ FAILED", style="bold red")

        status_text.append(f"\nConsistency Score: {result.consistency_score:.2%}")
        status_text.append(f"\nThreshold: {result.config.consistency_threshold:.2%}")

        console.print(
            Panel(
                status_text,
                title="[bold]Verification Result[/bold]",
                border_style="green" if result.passed else "red",
            )
        )

        # Metrics summary
        console.print("\n[bold]Consistency Metrics:[/bold]")
        console.print(
            f"  Attribute Agreement: {result.metrics.attribute_agreement:.2%}"
        )
        console.print(
            f"  Semantic Consistency: {result.metrics.semantic_consistency:.2%}"
        )
        console.print(
            f"  Factual Convergence: {result.metrics.factual_convergence:.2%}"
        )

        # Attribute summary
        console.print("\n[bold]Attributes:[/bold]")
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
