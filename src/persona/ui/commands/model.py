"""
Model management CLI commands.

Commands for listing, adding, and removing custom model configurations.
"""

from decimal import Decimal
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.ui.console import get_console

model_app = typer.Typer(
    name="model",
    help="Manage custom model configurations.",
    no_args_is_help=True,
)


@model_app.command("list")
def list_models(
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="Filter by provider.",
        ),
    ] = None,
    custom_only: Annotated[
        bool,
        typer.Option(
            "--custom",
            help="Only show custom models.",
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    List available models (built-in and custom).

    Example:
        persona model list
        persona model list --provider openai
        persona model list --custom
    """
    import json

    from persona.core.config import ModelLoader, get_builtin_models

    console = get_console()
    loader = ModelLoader()

    if json_output:
        result = {
            "command": "model list",
            "success": True,
            "data": {
                "builtin": {} if custom_only else get_builtin_models(),
                "custom": [],
            },
        }

        for model_id in loader.list_models(provider=provider):
            try:
                config = loader.load(model_id)
                result["data"]["custom"].append(
                    {
                        "id": config.id,
                        "name": config.name,
                        "provider": config.provider,
                        "context_window": config.context_window,
                        "max_output": config.max_output,
                        "pricing": {
                            "input": float(config.pricing.input),
                            "output": float(config.pricing.output),
                        },
                    }
                )
            except Exception as e:
                result["data"]["custom"].append(
                    {
                        "id": model_id,
                        "error": str(e),
                    }
                )

        print(json.dumps(result, indent=2))
        return

    # Rich output
    console.print(
        Panel.fit(
            "[bold]Available Models[/bold]",
            border_style="cyan",
        )
    )

    # Built-in models
    if not custom_only:
        builtin = get_builtin_models()

        if provider:
            builtin = {k: v for k, v in builtin.items() if k == provider}

        console.print("\n[bold]Built-in Models:[/bold]")
        for provider_name, models in sorted(builtin.items()):
            console.print(f"\n  [cyan]{provider_name}[/cyan]:")
            for model in models:
                console.print(f"    • {model}")

    # Custom models
    console.print("\n[bold]Custom Models:[/bold]")
    custom_models = loader.list_models(provider=provider)

    if not custom_models:
        console.print("  [dim]No custom models configured.[/dim]")
        console.print("  [dim]Run 'persona model add' to add one.[/dim]")
    else:
        for model_id in custom_models:
            try:
                config = loader.load(model_id)
                console.print(f"  • {config.id} ({config.provider})")
                console.print(f"    [dim]{config.name}[/dim]")
            except Exception as e:
                console.print(f"  [red]✗[/red] {model_id}: {e}")


@model_app.command("show")
def show_model(
    model_id: Annotated[
        str,
        typer.Argument(help="Model ID to show."),
    ],
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    Show details for a model.

    Example:
        persona model show my-finetuned-gpt4
    """
    import json

    from persona.core.config import ModelLoader

    console = get_console()
    loader = ModelLoader()

    try:
        config = loader.load(model_id)
    except FileNotFoundError as e:
        if json_output:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if json_output:
        result = {
            "command": "model show",
            "success": True,
            "data": config.model_dump(mode="json"),
        }
        print(json.dumps(result, indent=2))
        return

    # Rich output
    console.print(
        Panel.fit(
            f"[bold]{config.name}[/bold] ({config.id})",
            border_style="cyan",
        )
    )

    table = Table(show_header=False, box=None)
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("ID", config.id)
    table.add_row("Name", config.name)
    table.add_row("Provider", config.provider)
    if config.base_model:
        table.add_row("Base Model", config.base_model)
    if config.deployment_id:
        table.add_row("Deployment ID", config.deployment_id)
    table.add_row("Context Window", f"{config.context_window:,} tokens")
    table.add_row("Max Output", f"{config.max_output:,} tokens")
    table.add_row("Input Price", f"${config.pricing.input}/M tokens")
    table.add_row("Output Price", f"${config.pricing.output}/M tokens")

    if config.description:
        table.add_row("Description", config.description)

    console.print(table)

    # Capabilities
    console.print("\n[bold]Capabilities:[/bold]")
    caps = config.capabilities
    console.print(
        f"  Structured output: {'[green]✓[/green]' if caps.structured_output else '[red]✗[/red]'}"
    )
    console.print(f"  Vision: {'[green]✓[/green]' if caps.vision else '[red]✗[/red]'}")
    console.print(
        f"  Function calling: {'[green]✓[/green]' if caps.function_calling else '[red]✗[/red]'}"
    )
    console.print(
        f"  Streaming: {'[green]✓[/green]' if caps.streaming else '[red]✗[/red]'}"
    )


@model_app.command("add")
def add_model(
    model_id: Annotated[
        str,
        typer.Argument(help="Unique model ID."),
    ],
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Human-readable name."),
    ],
    provider: Annotated[
        str,
        typer.Option("--provider", "-p", help="Provider ID."),
    ],
    context_window: Annotated[
        int,
        typer.Option("--context", help="Context window size in tokens."),
    ] = 128000,
    max_output: Annotated[
        int,
        typer.Option("--max-output", help="Maximum output tokens."),
    ] = 4096,
    input_price: Annotated[
        float,
        typer.Option("--input-price", help="Price per 1M input tokens."),
    ] = 0.0,
    output_price: Annotated[
        float,
        typer.Option("--output-price", help="Price per 1M output tokens."),
    ] = 0.0,
    base_model: Annotated[
        Optional[str],
        typer.Option("--base-model", help="Base model ID for inheritance."),
    ] = None,
    deployment_id: Annotated[
        Optional[str],
        typer.Option("--deployment-id", help="Deployment ID (for Azure etc.)."),
    ] = None,
    project_level: Annotated[
        bool,
        typer.Option(
            "--project", help="Save to project directory instead of user directory."
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing model."),
    ] = False,
) -> None:
    """
    Add a custom model configuration.

    Example:
        persona model add my-finetuned-gpt4 \\
            --name "Fine-tuned GPT-4" \\
            --provider azure-openai \\
            --context 128000 \\
            --max-output 8192 \\
            --input-price 5.00 \\
            --output-price 15.00 \\
            --deployment-id my-deployment
    """
    from persona.core.config import ModelConfig, ModelLoader, ModelPricing

    console = get_console()
    loader = ModelLoader()

    # Check if exists
    if loader.exists(model_id) and not force:
        console.print(f"[red]Error:[/red] Model '{model_id}' already exists.")
        console.print("Use --force to overwrite.")
        raise typer.Exit(1)

    # Create config
    try:
        config = ModelConfig(
            id=model_id,
            name=name,
            provider=provider,
            base_model=base_model,
            context_window=context_window,
            max_output=max_output,
            deployment_id=deployment_id,
            pricing=ModelPricing(
                input=Decimal(str(input_price)),
                output=Decimal(str(output_price)),
            ),
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid configuration: {e}")
        raise typer.Exit(1)

    # Save
    path = loader.save(config, user_level=not project_level)

    console.print(f"[green]✓[/green] Model '{model_id}' added.")
    console.print(f"  Config saved to: {path}")


@model_app.command("remove")
def remove_model(
    model_id: Annotated[
        str,
        typer.Argument(help="Model ID to remove."),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation."),
    ] = False,
) -> None:
    """
    Remove a custom model configuration.

    Example:
        persona model remove my-finetuned-gpt4
    """
    from persona.core.config import ModelLoader

    console = get_console()
    loader = ModelLoader()

    if not loader.exists(model_id):
        console.print(f"[red]Error:[/red] Model '{model_id}' not found.")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Remove model '{model_id}'?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    if loader.delete(model_id):
        console.print(f"[green]✓[/green] Model '{model_id}' removed.")
    else:
        console.print("[red]Error:[/red] Failed to remove model.")
        raise typer.Exit(1)


@model_app.command("pricing")
def show_pricing(
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="Filter by provider.",
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
    Show pricing for all models.

    Example:
        persona model pricing
        persona model pricing --provider anthropic
    """
    import json

    from persona.core.config import ModelLoader
    from persona.core.cost import PricingData

    console = get_console()
    loader = ModelLoader()

    all_pricing = []

    # Get built-in pricing
    for pricing in PricingData.list_models(provider=provider):
        all_pricing.append(
            {
                "model": pricing.model,
                "provider": pricing.provider,
                "input": float(pricing.input_price),
                "output": float(pricing.output_price),
                "source": "builtin",
            }
        )

    # Get custom model pricing
    for model_id in loader.list_models(provider=provider):
        try:
            config = loader.load(model_id)
            all_pricing.append(
                {
                    "model": config.id,
                    "provider": config.provider,
                    "input": float(config.pricing.input),
                    "output": float(config.pricing.output),
                    "source": "custom",
                }
            )
        except Exception:
            continue

    # Sort by input price
    all_pricing.sort(key=lambda x: x["input"])

    if json_output:
        print(json.dumps({"pricing": all_pricing}, indent=2))
        return

    # Rich output
    table = Table(title="Model Pricing (per 1M tokens)")
    table.add_column("Model", style="cyan")
    table.add_column("Provider")
    table.add_column("Input", justify="right")
    table.add_column("Output", justify="right")
    table.add_column("Source")

    for p in all_pricing:
        table.add_row(
            p["model"],
            p["provider"],
            f"${p['input']:.2f}",
            f"${p['output']:.2f}",
            p["source"],
        )

    console.print(table)


@model_app.command("discover")
def discover_models(
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="Filter by provider.",
        ),
    ] = None,
    refresh: Annotated[
        bool,
        typer.Option(
            "--refresh",
            "-r",
            help="Force refresh of cached results.",
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    Discover available models from vendors.

    Example:
        persona model discover
        persona model discover --provider openai
    """
    import json

    from persona.core.discovery import ModelDiscovery, ModelStatus

    console = get_console()

    if not json_output:
        console.print(
            Panel.fit(
                "[bold]Discovering Models[/bold]",
                border_style="cyan",
            )
        )
        console.print()

    discovery = ModelDiscovery()
    results = discovery.discover_all(provider=provider, force_refresh=refresh)

    if json_output:
        output = {
            "command": "model discover",
            "success": True,
            "data": {
                "models": [],
            },
        }
        for result in results:
            output["data"]["models"].append(
                {
                    "id": result.model_id,
                    "name": result.name,
                    "status": result.status.value,
                    "provider": result.provider,
                    "source": result.source,
                    "context_window": result.context_window,
                    "deprecation_message": result.deprecation_message,
                }
            )
        print(json.dumps(output, indent=2))
        return

    # Group by provider
    by_provider: dict[str, list] = {}
    for result in results:
        if result.provider not in by_provider:
            by_provider[result.provider] = []
        by_provider[result.provider].append(result)

    for provider_name, models in sorted(by_provider.items()):
        console.print(f"\n[bold cyan]{provider_name}:[/bold cyan]")

        for result in sorted(models, key=lambda x: x.model_id):
            if result.status == ModelStatus.AVAILABLE:
                status_icon = "[green]✓[/green]"
            elif result.status == ModelStatus.DEPRECATED:
                status_icon = "[yellow]![/yellow]"
            else:
                status_icon = "[red]✗[/red]"

            context = (
                f" ({result.context_window:,} ctx)" if result.context_window else ""
            )
            source = f" [{result.source}]" if result.source != "builtin" else ""
            console.print(f"  {status_icon} {result.model_id}{context}{source}")

            if result.deprecation_message:
                console.print(f"    [yellow]{result.deprecation_message}[/yellow]")

    # Summary
    available = len([r for r in results if r.status == ModelStatus.AVAILABLE])
    deprecated = len([r for r in results if r.status == ModelStatus.DEPRECATED])
    console.print(
        f"\n[bold]Summary:[/bold] {available} available, {deprecated} deprecated"
    )


@model_app.command("check")
def check_model(
    model_id: Annotated[
        str,
        typer.Argument(help="Model ID to check."),
    ],
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="Provider hint.",
        ),
    ] = None,
) -> None:
    """
    Check if a model is available.

    Example:
        persona model check gpt-4o
        persona model check claude-3-5-sonnet-20241022 --provider anthropic
    """
    from persona.core.discovery import ModelDiscovery

    console = get_console()
    discovery = ModelDiscovery()

    is_available, message = discovery.check_model(model_id, provider)

    if is_available:
        if "Warning" in message:
            console.print(f"[yellow]{message}[/yellow]")
        else:
            console.print(f"[green]✓[/green] {message}")
    else:
        console.print(f"[red]✗[/red] {message}")
        raise typer.Exit(1)
