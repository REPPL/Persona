"""
CLI commands for plugin management.

This module provides commands for listing, inspecting, and managing plugins.
"""

import json
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from persona.core.plugins import (
    PluginInfo,
    PluginType,
    get_plugin_manager,
)

plugin_app = typer.Typer(
    name="plugin",
    help="Manage Persona plugins (formatters, loaders, providers, validators).",
    no_args_is_help=True,
)

console = Console()


def _get_type_colour(plugin_type: PluginType) -> str:
    """Get colour for plugin type."""
    colours = {
        PluginType.FORMATTER: "cyan",
        PluginType.LOADER: "green",
        PluginType.PROVIDER: "yellow",
        PluginType.VALIDATOR: "magenta",
        PluginType.WORKFLOW: "blue",
    }
    return colours.get(plugin_type, "white")


def _get_status_badge(info: PluginInfo) -> Text:
    """Get status badge for plugin."""
    if not info.enabled:
        return Text("disabled", style="dim red")
    if info.builtin:
        return Text("builtin", style="dim green")
    if info.entry_point:
        return Text("external", style="dim blue")
    return Text("custom", style="dim yellow")


@plugin_app.command("list")
def list_plugins(
    plugin_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by plugin type (formatter, loader, provider, validator)",
    ),
    builtin_only: bool = typer.Option(
        False,
        "--builtin",
        "-b",
        help="Show only built-in plugins",
    ),
    external_only: bool = typer.Option(
        False,
        "--external",
        "-e",
        help="Show only external plugins",
    ),
    output: str = typer.Option(
        "rich",
        "--output",
        "-o",
        help="Output format: rich, json",
    ),
) -> None:
    """List all registered plugins."""
    manager = get_plugin_manager()

    # Parse plugin type filter
    type_filter: PluginType | None = None
    if plugin_type:
        try:
            type_filter = PluginType(plugin_type.lower())
        except ValueError:
            valid_types = ", ".join(t.value for t in PluginType)
            console.print(
                f"[red]Invalid plugin type: {plugin_type}[/red]\n"
                f"Valid types: {valid_types}"
            )
            raise typer.Exit(code=1)

    # Get plugins
    plugins = manager.list_plugins(
        plugin_type=type_filter,
        builtin_only=builtin_only,
        external_only=external_only,
    )

    if output == "json":
        data = [p.to_dict() for p in plugins]
        console.print(json.dumps(data, indent=2))
        return

    if not plugins:
        console.print("[yellow]No plugins found matching criteria.[/yellow]")
        return

    # Create table
    table = Table(
        title="Registered Plugins",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="white")
    table.add_column("Description")
    table.add_column("Version", justify="right")
    table.add_column("Status", justify="center")

    for info in plugins:
        type_colour = _get_type_colour(info.plugin_type)
        status = _get_status_badge(info)

        table.add_row(
            info.name,
            Text(info.plugin_type.value, style=type_colour),
            info.description[:50] + "..."
            if len(info.description) > 50
            else info.description,
            info.version,
            status,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(plugins)} plugins[/dim]")


@plugin_app.command("info")
def plugin_info(
    name: str = typer.Argument(..., help="Plugin name"),
    plugin_type: str = typer.Option(
        ...,
        "--type",
        "-t",
        help="Plugin type (formatter, loader, provider, validator)",
    ),
    output: str = typer.Option(
        "rich",
        "--output",
        "-o",
        help="Output format: rich, json",
    ),
) -> None:
    """Show detailed information about a plugin."""
    manager = get_plugin_manager()

    try:
        ptype = PluginType(plugin_type.lower())
    except ValueError:
        valid_types = ", ".join(t.value for t in PluginType)
        console.print(
            f"[red]Invalid plugin type: {plugin_type}[/red]\n"
            f"Valid types: {valid_types}"
        )
        raise typer.Exit(code=1)

    if not manager.has_plugin(ptype, name):
        console.print(f"[red]Plugin '{name}' of type '{plugin_type}' not found.[/red]")
        raise typer.Exit(code=1)

    info = manager.get_plugin_info(ptype, name)

    if output == "json":
        console.print(json.dumps(info.to_dict(), indent=2))
        return

    # Rich output
    type_colour = _get_type_colour(info.plugin_type)

    content = [
        f"[bold]Name:[/bold] {info.name}",
        f"[bold]Type:[/bold] [{type_colour}]{info.plugin_type.value}[/{type_colour}]",
        f"[bold]Description:[/bold] {info.description}",
        f"[bold]Version:[/bold] {info.version}",
        f"[bold]Author:[/bold] {info.author or 'Unknown'}",
        f"[bold]Status:[/bold] {'Enabled' if info.enabled else 'Disabled'}",
        f"[bold]Built-in:[/bold] {'Yes' if info.builtin else 'No'}",
    ]

    if info.entry_point:
        content.append(f"[bold]Entry Point:[/bold] {info.entry_point}")

    if info.metadata:
        content.append(f"[bold]Metadata:[/bold] {json.dumps(info.metadata, indent=2)}")

    panel = Panel(
        "\n".join(content),
        title=f"Plugin: {info.name}",
        border_style=type_colour,
    )
    console.print(panel)


@plugin_app.command("summary")
def plugin_summary(
    output: str = typer.Option(
        "rich",
        "--output",
        "-o",
        help="Output format: rich, json",
    ),
) -> None:
    """Show summary of all registered plugins."""
    manager = get_plugin_manager()
    summary = manager.get_summary()

    if output == "json":
        console.print(json.dumps(summary, indent=2))
        return

    # Overview panel
    overview = (
        f"[bold]Total Plugins:[/bold] {summary['total']}\n"
        f"[bold]Enabled:[/bold] [green]{summary['enabled']}[/green]\n"
        f"[bold]Disabled:[/bold] [red]{summary['disabled']}[/red]\n"
        f"[bold]Built-in:[/bold] {summary['builtin']}\n"
        f"[bold]External:[/bold] {summary['external']}"
    )
    console.print(Panel(overview, title="Plugin Summary", border_style="blue"))

    # By type table
    table = Table(
        title="Plugins by Type",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Type", style="cyan")
    table.add_column("Total", justify="right")
    table.add_column("Enabled", justify="right", style="green")
    table.add_column("Built-in", justify="right")
    table.add_column("External", justify="right", style="blue")

    for type_name, type_summary in summary["by_type"].items():
        table.add_row(
            type_name,
            str(type_summary["total"]),
            str(type_summary["enabled"]),
            str(type_summary["builtin"]),
            str(type_summary["external"]),
        )

    console.print(table)


@plugin_app.command("check")
def check_plugins(
    plugin_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Check only plugins of this type",
    ),
) -> None:
    """Verify all plugins can be loaded correctly."""
    manager = get_plugin_manager()

    type_filter: PluginType | None = None
    if plugin_type:
        try:
            type_filter = PluginType(plugin_type.lower())
        except ValueError:
            valid_types = ", ".join(t.value for t in PluginType)
            console.print(
                f"[red]Invalid plugin type: {plugin_type}[/red]\n"
                f"Valid types: {valid_types}"
            )
            raise typer.Exit(code=1)

    plugins = manager.list_plugins(plugin_type=type_filter, enabled_only=True)

    if not plugins:
        console.print("[yellow]No plugins to check.[/yellow]")
        return

    console.print(f"[bold]Checking {len(plugins)} plugins...[/bold]\n")

    errors = []
    for info in plugins:
        try:
            # Try to instantiate the plugin
            manager.get_plugin(info.plugin_type, info.name)
            console.print(f"  [green]✓[/green] {info.name} ({info.plugin_type.value})")
        except Exception as e:
            errors.append((info, str(e)))
            console.print(f"  [red]✗[/red] {info.name} ({info.plugin_type.value}): {e}")

    console.print()
    if errors:
        console.print(f"[red]{len(errors)} plugins failed to load.[/red]")
        raise typer.Exit(code=1)
    else:
        console.print(f"[green]All {len(plugins)} plugins loaded successfully.[/green]")


@plugin_app.command("reload")
def reload_plugins() -> None:
    """Reload all plugin registries."""
    manager = get_plugin_manager()

    console.print("[bold]Reloading plugins...[/bold]")
    manager.reload_all()

    summary = manager.get_summary()
    console.print(f"[green]Reloaded {summary['total']} plugins.[/green]")
