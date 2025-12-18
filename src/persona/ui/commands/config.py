"""
Configuration management CLI commands.
"""

from typing import Annotated, Optional

import typer
from rich.panel import Panel

from persona.ui.console import get_console
from persona.ui.interactive import ConfigWizard, is_interactive_supported

config_app = typer.Typer(
    name="config",
    help="Manage Persona configuration.",
    invoke_without_command=True,
)


@config_app.callback(invoke_without_command=True)
def config_callback(ctx: typer.Context) -> None:
    """
    Manage Persona configuration.

    Use 'persona config -i' for interactive configuration wizard.

    Example:
        persona config -i
        persona config show
    """
    # Check if running interactively with no subcommand
    from persona.ui.cli import is_interactive

    if ctx.invoked_subcommand is None:
        if is_interactive():
            if not is_interactive_supported():
                console = get_console()
                console.print(
                    "[yellow]Interactive mode not supported in non-TTY environment.[/yellow]"
                )
                raise typer.Exit(1)

            wizard = ConfigWizard()
            result = wizard.run()
            if result is None:
                raise typer.Exit(0)

            # Apply the configuration
            from persona.core.config.global_config import get_config_manager

            console = get_console()
            manager = get_config_manager()

            section = result.pop("section")
            for key, value in result.items():
                path = f"{section}.{key}"
                try:
                    manager.set_value(path, value, user_level=True)
                    console.print(f"[green]✓[/green] Set {path} = {value}")
                except Exception as e:
                    console.print(f"[red]Error setting {path}:[/red] {e}")

            console.print("\n[green]Configuration saved![/green]")
        else:
            # Show help if no subcommand and not interactive
            ctx.get_help()
            raise typer.Exit(0)


@config_app.command("init")
def init_config(
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing configuration.",
        ),
    ] = False,
) -> None:
    """
    Initialise global configuration file.

    Creates ~/.persona/config.yaml with default settings.

    Example:
        persona config init
        persona config init --force
    """
    from persona.core.config.global_config import get_config_manager

    console = get_console()
    manager = get_config_manager()

    try:
        path = manager.init_global(force=force)
        console.print(f"[green]✓[/green] Created configuration: {path}")
        console.print("\nEdit this file to customise your defaults.")
    except FileExistsError as e:
        console.print(f"[yellow]Configuration already exists:[/yellow] {e}")
        console.print("Use --force to overwrite.")
        raise typer.Exit(1)


@config_app.command("show")
def show_config(
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output as JSON.",
        ),
    ] = False,
    source: Annotated[
        bool,
        typer.Option(
            "--source",
            "-s",
            help="Show configuration sources.",
        ),
    ] = False,
) -> None:
    """
    Show effective configuration.

    Displays the merged configuration from all layers.

    Example:
        persona config show
        persona config show --json
    """
    import json

    from persona.core.config.global_config import (
        get_config_manager,
        get_global_config_path,
        get_project_config_path,
    )

    console = get_console()
    manager = get_config_manager()
    config = manager.load()

    if json_output:
        print(json.dumps(config.model_dump(mode="json"), indent=2))
        return

    console.print(
        Panel.fit(
            "[bold]Effective Configuration[/bold]",
            border_style="cyan",
        )
    )

    if source:
        console.print("\n[bold]Configuration Sources:[/bold]")
        global_path = get_global_config_path()
        project_path = get_project_config_path()

        console.print(
            f"  Global:  {global_path} {'[green]✓[/green]' if global_path.exists() else '[dim]not found[/dim]'}"
        )
        if project_path:
            console.print(f"  Project: {project_path} [green]✓[/green]")
        else:
            console.print("  Project: [dim]not found[/dim]")
        console.print()

    # Show config sections
    console.print("\n[bold]Defaults:[/bold]")
    console.print(f"  provider: {config.defaults.provider}")
    console.print(f"  model: {config.defaults.model or '[dim]provider default[/dim]'}")
    console.print(f"  complexity: {config.defaults.complexity}")
    console.print(f"  detail_level: {config.defaults.detail_level}")
    console.print(f"  workflow: {config.defaults.workflow}")
    console.print(f"  count: {config.defaults.count}")

    console.print("\n[bold]Budgets:[/bold]")
    console.print(f"  per_run: {config.budgets.per_run or '[dim]not set[/dim]'}")
    console.print(f"  daily: {config.budgets.daily or '[dim]not set[/dim]'}")
    console.print(f"  monthly: {config.budgets.monthly or '[dim]not set[/dim]'}")

    console.print("\n[bold]Output:[/bold]")
    console.print(f"  format: {config.output.format}")
    console.print(f"  include_readme: {config.output.include_readme}")
    console.print(f"  timestamp_folders: {config.output.timestamp_folders}")

    console.print("\n[bold]Logging:[/bold]")
    console.print(f"  level: {config.logging.level}")
    console.print(f"  format: {config.logging.format}")
    console.print(f"  file: {config.logging.file or '[dim]not set[/dim]'}")


@config_app.command("get")
def get_config_value(
    path: Annotated[
        str,
        typer.Argument(help="Configuration path (e.g., 'defaults.provider')."),
    ],
) -> None:
    """
    Get a configuration value.

    Example:
        persona config get defaults.provider
        persona config get budgets.daily
    """
    from persona.core.config.global_config import get_config_manager

    console = get_console()
    manager = get_config_manager()

    try:
        value = manager.get_value(path)
        if value is None:
            console.print("[dim]not set[/dim]")
        else:
            console.print(str(value))
    except KeyError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@config_app.command("set")
def set_config_value(
    path: Annotated[
        str,
        typer.Argument(help="Configuration path (e.g., 'defaults.provider')."),
    ],
    value: Annotated[
        str,
        typer.Argument(help="Value to set."),
    ],
    project: Annotated[
        bool,
        typer.Option(
            "--project",
            "-p",
            help="Set in project config instead of global config.",
        ),
    ] = False,
) -> None:
    """
    Set a configuration value.

    Example:
        persona config set defaults.provider openai
        persona config set defaults.count 5
        persona config set budgets.daily 25.00
    """
    from persona.core.config.global_config import get_config_manager

    console = get_console()
    manager = get_config_manager()

    # Type conversion for known numeric fields
    parsed_value: str | int | float = value
    if path.endswith(".count"):
        parsed_value = int(value)
    elif path.startswith("budgets."):
        parsed_value = float(value)

    try:
        config_path = manager.set_value(path, parsed_value, user_level=not project)
        console.print(f"[green]✓[/green] Set {path} = {value}")
        console.print(f"  [dim]Saved to: {config_path}[/dim]")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@config_app.command("reset")
def reset_config(
    project: Annotated[
        bool,
        typer.Option(
            "--project",
            "-p",
            help="Reset project config instead of global config.",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Skip confirmation.",
        ),
    ] = False,
) -> None:
    """
    Reset configuration to defaults.

    Example:
        persona config reset
        persona config reset --project
    """
    from persona.core.config.global_config import get_config_manager

    console = get_console()
    manager = get_config_manager()

    config_type = "project" if project else "global"

    if not force:
        confirm = typer.confirm(f"Reset {config_type} configuration to defaults?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    path = manager.reset(user_level=not project)
    if path:
        console.print(f"[green]✓[/green] Removed configuration: {path}")
    else:
        console.print(f"[yellow]No {config_type} configuration found.[/yellow]")


@config_app.command("path")
def show_paths() -> None:
    """
    Show configuration file paths.

    Example:
        persona config path
    """
    from persona.core.config.global_config import (
        get_global_config_path,
        get_project_config_path,
    )

    console = get_console()

    global_path = get_global_config_path()
    project_path = get_project_config_path()

    console.print("[bold]Configuration Paths:[/bold]")
    console.print("\n  Global config:")
    console.print(f"    {global_path}")
    console.print(
        f"    {'[green]exists[/green]' if global_path.exists() else '[dim]not created[/dim]'}"
    )

    console.print("\n  Project config:")
    if project_path:
        console.print(f"    {project_path}")
        console.print("    [green]exists[/green]")
    else:
        console.print("    [dim]not found (search from cwd to root)[/dim]")


@config_app.command("edit")
def edit_config(
    section: Annotated[
        Optional[str],
        typer.Argument(
            help="Configuration section to edit (defaults, budgets, output, logging).",
        ),
    ] = None,
    project: Annotated[
        bool,
        typer.Option(
            "--project",
            "-p",
            help="Edit project config instead of global config.",
        ),
    ] = False,
) -> None:
    """
    Open interactive configuration editor.

    Edit all configuration options in a form-based interface.

    Example:
        persona config edit
        persona config edit defaults
        persona config edit --project
    """
    from persona.ui.interactive import ConfigEditor, is_interactive_supported

    console = get_console()

    if not is_interactive_supported():
        console.print(
            "[yellow]Interactive mode not supported in non-TTY environment.[/yellow]"
        )
        console.print(
            "Use 'persona config set <path> <value>' for non-interactive configuration."
        )
        raise typer.Exit(1)

    editor = ConfigEditor(console=console, project_level=project)
    result = editor.run(section=section)

    if result is None:
        raise typer.Exit(0)

    # Apply changes
    from persona.core.config.global_config import get_config_manager

    manager = get_config_manager()

    changes_made = False
    for key, value in result.items():
        if value is not None:
            try:
                manager.set_value(key, value, user_level=not project)
                console.print(f"[green]✓[/green] Set {key} = {value}")
                changes_made = True
            except Exception as e:
                console.print(f"[red]Error setting {key}:[/red] {e}")

    if changes_made:
        console.print("\n[green]Configuration saved![/green]")
    else:
        console.print("[yellow]No changes made.[/yellow]")
