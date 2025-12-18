"""
Vendor management CLI commands.

Commands for listing, adding, testing, and removing custom LLM vendors.
"""

from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.ui.console import get_console

vendor_app = typer.Typer(
    name="vendor",
    help="Manage custom LLM vendors.",
    no_args_is_help=True,
)


@vendor_app.command("list")
def list_vendors(
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
    configured_only: Annotated[
        bool,
        typer.Option(
            "--configured",
            help="Only show configured vendors.",
        ),
    ] = False,
) -> None:
    """
    List available vendors (built-in and custom).

    Example:
        persona vendor list
        persona vendor list --configured
    """
    import json

    from persona.core.config import VendorLoader
    from persona.core.providers import ProviderFactory

    console = get_console()
    loader = VendorLoader()

    # Get all providers
    builtin = ProviderFactory.list_builtin_providers()
    custom = loader.list_vendors()

    if json_output:
        result = {
            "command": "vendor list",
            "success": True,
            "data": {
                "builtin": builtin,
                "custom": [],
            },
        }

        for vendor_id in custom:
            try:
                config = loader.load(vendor_id)
                vendor_info = {
                    "id": config.id,
                    "name": config.name,
                    "api_base": config.api_base,
                    "configured": config.is_configured(),
                    "models": config.models,
                }
                if not configured_only or vendor_info["configured"]:
                    result["data"]["custom"].append(vendor_info)
            except Exception as e:
                result["data"]["custom"].append(
                    {
                        "id": vendor_id,
                        "error": str(e),
                    }
                )

        print(json.dumps(result, indent=2))
        return

    # Rich output
    console.print(
        Panel.fit(
            "[bold]Available Vendors[/bold]",
            border_style="cyan",
        )
    )

    # Built-in providers
    console.print("\n[bold]Built-in Providers:[/bold]")
    for name in builtin:
        try:
            provider = ProviderFactory.create(name)
            if provider.is_configured():
                console.print(f"  [green]✓[/green] {name} (configured)")
            else:
                console.print(f"  [yellow]○[/yellow] {name}")
        except Exception:
            console.print(f"  [red]✗[/red] {name} (error)")

    # Custom vendors
    console.print("\n[bold]Custom Vendors:[/bold]")
    if not custom:
        console.print("  [dim]No custom vendors configured.[/dim]")
        console.print("  [dim]Run 'persona vendor add' to add one.[/dim]")
    else:
        for vendor_id in custom:
            try:
                config = loader.load(vendor_id)
                if configured_only and not config.is_configured():
                    continue
                if config.is_configured():
                    console.print(f"  [green]✓[/green] {vendor_id}: {config.name}")
                else:
                    console.print(f"  [yellow]○[/yellow] {vendor_id}: {config.name}")
            except Exception as e:
                console.print(f"  [red]✗[/red] {vendor_id}: {e}")


@vendor_app.command("show")
def show_vendor(
    vendor_id: Annotated[
        str,
        typer.Argument(help="Vendor ID to show."),
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
    Show details for a vendor.

    Example:
        persona vendor show azure-openai
    """
    import json

    from persona.core.config import VendorLoader

    console = get_console()
    loader = VendorLoader()

    try:
        config = loader.load(vendor_id)
    except FileNotFoundError as e:
        if json_output:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if json_output:
        result = {
            "command": "vendor show",
            "success": True,
            "data": config.model_dump(mode="json"),
        }
        result["data"]["configured"] = config.is_configured()
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
    table.add_row("API Base", config.api_base)
    if config.api_version:
        table.add_row("API Version", config.api_version)
    table.add_row("Auth Type", config.auth_type)
    if config.auth_env:
        table.add_row("Auth Env", config.auth_env)
    table.add_row("Default Model", config.default_model or "[dim]none[/dim]")
    table.add_row(
        "Models", ", ".join(config.models) if config.models else "[dim]none[/dim]"
    )
    table.add_row("Timeout", f"{config.timeout}s")
    table.add_row("Request Format", config.request_format)
    table.add_row("Response Format", config.response_format)

    if config.is_configured():
        table.add_row("Status", "[green]Configured[/green]")
    else:
        table.add_row(
            "Status", f"[yellow]Not configured[/yellow] (set {config.auth_env})"
        )

    console.print(table)


@vendor_app.command("add")
def add_vendor(
    vendor_id: Annotated[
        str,
        typer.Argument(help="Unique ID for the vendor."),
    ],
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Human-readable name."),
    ],
    api_base: Annotated[
        str,
        typer.Option("--api-base", "-u", help="API base URL."),
    ],
    api_version: Annotated[
        Optional[str],
        typer.Option("--api-version", help="API version string."),
    ] = None,
    auth_type: Annotated[
        str,
        typer.Option(
            "--auth-type", help="Authentication type (bearer, header, query, none)."
        ),
    ] = "bearer",
    auth_env: Annotated[
        Optional[str],
        typer.Option("--auth-env", help="Environment variable for API key."),
    ] = None,
    default_model: Annotated[
        Optional[str],
        typer.Option("--default-model", "-m", help="Default model to use."),
    ] = None,
    models: Annotated[
        Optional[str],
        typer.Option("--models", help="Comma-separated list of available models."),
    ] = None,
    project_level: Annotated[
        bool,
        typer.Option(
            "--project", help="Save to project directory instead of user directory."
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing vendor."),
    ] = False,
) -> None:
    """
    Add a custom vendor configuration.

    Example:
        persona vendor add azure-openai \\
            --name "Azure OpenAI" \\
            --api-base "https://my-deployment.openai.azure.com" \\
            --auth-type header \\
            --auth-env AZURE_OPENAI_API_KEY \\
            --default-model gpt-4
    """
    from persona.core.config import AuthType, VendorConfig, VendorLoader

    console = get_console()
    loader = VendorLoader()

    # Check if exists
    if loader.exists(vendor_id) and not force:
        console.print(f"[red]Error:[/red] Vendor '{vendor_id}' already exists.")
        console.print("Use --force to overwrite.")
        raise typer.Exit(1)

    # Parse models
    model_list = []
    if models:
        model_list = [m.strip() for m in models.split(",")]

    # Validate auth_type
    try:
        auth = AuthType(auth_type)
    except ValueError:
        console.print(f"[red]Error:[/red] Invalid auth type: {auth_type}")
        console.print("Valid types: bearer, header, query, none")
        raise typer.Exit(1)

    # Create config
    try:
        config = VendorConfig(
            id=vendor_id,
            name=name,
            api_base=api_base,
            api_version=api_version,
            auth_type=auth,
            auth_env=auth_env,
            default_model=default_model,
            models=model_list,
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid configuration: {e}")
        raise typer.Exit(1)

    # Save
    path = loader.save(config, user_level=not project_level)

    console.print(f"[green]✓[/green] Vendor '{vendor_id}' added.")
    console.print(f"  Config saved to: {path}")

    if auth_env and not config.is_configured():
        console.print(
            f"\n[yellow]Note:[/yellow] Set {auth_env} to configure authentication."
        )


@vendor_app.command("remove")
def remove_vendor(
    vendor_id: Annotated[
        str,
        typer.Argument(help="Vendor ID to remove."),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation."),
    ] = False,
) -> None:
    """
    Remove a custom vendor configuration.

    Example:
        persona vendor remove azure-openai
    """
    from persona.core.config import VendorLoader

    console = get_console()
    loader = VendorLoader()

    if not loader.exists(vendor_id):
        console.print(f"[red]Error:[/red] Vendor '{vendor_id}' not found.")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Remove vendor '{vendor_id}'?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    if loader.delete(vendor_id):
        console.print(f"[green]✓[/green] Vendor '{vendor_id}' removed.")
    else:
        console.print("[red]Error:[/red] Failed to remove vendor.")
        raise typer.Exit(1)


@vendor_app.command("test")
def test_vendor(
    vendor_id: Annotated[
        str,
        typer.Argument(help="Vendor ID to test."),
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
    Test connection to a vendor.

    Example:
        persona vendor test azure-openai
    """
    import json

    from persona.core.providers import ProviderFactory

    console = get_console()

    if not json_output:
        console.print(f"Testing vendor: {vendor_id}...")

    try:
        provider = ProviderFactory.create(vendor_id)
    except ValueError as e:
        if json_output:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    # Check if it's a custom provider with test_connection
    if hasattr(provider, "test_connection"):
        result = provider.test_connection()
    else:
        # Built-in provider - simple check
        result = {
            "vendor": vendor_id,
            "configured": provider.is_configured(),
            "models": provider.available_models,
        }

    if json_output:
        print(json.dumps(result, indent=2))
        return

    # Rich output
    if result.get("success") is True:
        console.print("\n[green]✓[/green] Connection successful!")
        console.print(f"  Model: {result.get('response_model', 'unknown')}")
        console.print(f"  Tokens used: {result.get('response_tokens', 'unknown')}")
    elif result.get("configured") is False:
        console.print("\n[yellow]○[/yellow] Not configured")
        if "error" in result:
            console.print(f"  {result['error']}")
    elif "error" in result:
        console.print("\n[red]✗[/red] Connection failed")
        console.print(f"  Error: {result['error']}")
    else:
        console.print("\n[green]✓[/green] Vendor configured")
        console.print(f"  Available models: {', '.join(result.get('models', []))}")


@vendor_app.command("discover")
def discover_vendors(
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
    Discover available vendors by probing endpoints.

    Example:
        persona vendor discover
        persona vendor discover --refresh
    """
    import json

    from persona.core.discovery import VendorDiscovery, VendorStatus

    console = get_console()

    if not json_output:
        console.print(
            Panel.fit(
                "[bold]Discovering Vendors[/bold]",
                border_style="cyan",
            )
        )
        console.print()

    discovery = VendorDiscovery()
    results = discovery.discover_all(force_refresh=refresh)

    if json_output:
        output = {
            "command": "vendor discover",
            "success": True,
            "data": {
                "vendors": [],
            },
        }
        for result in results:
            output["data"]["vendors"].append(
                {
                    "id": result.vendor_id,
                    "name": result.name,
                    "status": result.status.value,
                    "source": result.source,
                    "message": result.message,
                    "base_url": result.base_url,
                    "response_time_ms": result.response_time_ms,
                    "models": result.models,
                }
            )
        print(json.dumps(output, indent=2))
        return

    # Rich output - group by status
    available = [r for r in results if r.status == VendorStatus.AVAILABLE]
    not_configured = [r for r in results if r.status == VendorStatus.NOT_CONFIGURED]
    unavailable = [r for r in results if r.status == VendorStatus.UNAVAILABLE]
    errors = [r for r in results if r.status == VendorStatus.ERROR]

    if available:
        console.print("[bold green]Available:[/bold green]")
        for result in available:
            response_time = (
                f" ({result.response_time_ms:.0f}ms)" if result.response_time_ms else ""
            )
            models_info = f" - {len(result.models)} models" if result.models else ""
            console.print(
                f"  [green]✓[/green] {result.name} ({result.vendor_id}){response_time}{models_info}"
            )
            if result.message:
                console.print(f"    [dim]{result.message}[/dim]")

    if not_configured:
        console.print("\n[bold yellow]Not Configured:[/bold yellow]")
        for result in not_configured:
            console.print(f"  [yellow]○[/yellow] {result.name} ({result.vendor_id})")
            if result.message:
                console.print(f"    [dim]{result.message}[/dim]")

    if unavailable:
        console.print("\n[bold red]Unavailable:[/bold red]")
        for result in unavailable:
            console.print(f"  [red]✗[/red] {result.name} ({result.vendor_id})")
            if result.message:
                console.print(f"    [dim]{result.message}[/dim]")

    if errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for result in errors:
            console.print(f"  [red]✗[/red] {result.name} ({result.vendor_id})")
            if result.message:
                console.print(f"    [dim]{result.message}[/dim]")

    # Summary
    console.print(
        f"\n[bold]Summary:[/bold] {len(available)} available, {len(not_configured)} not configured, {len(unavailable)} unavailable"
    )
