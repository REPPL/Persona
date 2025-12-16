"""
Project management CLI commands.

Provides commands for creating, listing, and managing Persona projects
using the registry-based project management system.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.ui.console import get_console

project_app = typer.Typer(
    name="project",
    help="Manage Persona projects.",
    invoke_without_command=True,
)


@project_app.callback(invoke_without_command=True)
def project_callback(ctx: typer.Context) -> None:
    """
    Manage Persona projects.

    Projects can be created, registered, and referenced by name from
    anywhere on the filesystem.

    Example:
        persona project list
        persona project create my-research
        persona project show my-research
    """
    if ctx.invoked_subcommand is None:
        # Show help if no subcommand
        ctx.get_help()


@project_app.command("list")
def list_projects(
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output as JSON.",
        ),
    ] = False,
) -> None:
    """
    List all registered projects.

    Shows projects from the global registry with their paths and status.

    Example:
        persona project list
        persona project list --json
    """
    import json

    from persona.core.project import list_registered_projects

    console = get_console()
    projects = list_registered_projects()

    if json_output:
        data = [
            {"name": name, "path": str(path), "exists": path.exists()}
            for name, path in projects
        ]
        print(json.dumps(data, indent=2))
        return

    if not projects:
        console.print("[yellow]No projects registered.[/yellow]")
        console.print("\nCreate a project with:")
        console.print("  persona project create my-research")
        console.print("\nOr register an existing project:")
        console.print("  persona project register my-project /path/to/project")
        return

    console.print(Panel.fit(
        "[bold]Registered Projects[/bold]",
        border_style="cyan",
    ))

    table = Table(show_header=True, header_style="bold")
    table.add_column("Name", style="cyan")
    table.add_column("Path")
    table.add_column("Status")

    for name, path in projects:
        status = "[green]✓[/green]" if path.exists() else "[red]missing[/red]"
        table.add_row(name, str(path), status)

    console.print(table)


@project_app.command("create")
def create_project_cmd(
    name: Annotated[
        str,
        typer.Argument(help="Name for the new project."),
    ],
    path: Annotated[
        Optional[Path],
        typer.Option(
            "--path", "-p",
            help="Directory to create project in. Defaults to current directory.",
        ),
    ] = None,
    template: Annotated[
        str,
        typer.Option(
            "--template", "-t",
            help="Project template (basic or research).",
        ),
    ] = "basic",
    description: Annotated[
        Optional[str],
        typer.Option(
            "--description", "-d",
            help="Project description.",
        ),
    ] = None,
    no_register: Annotated[
        bool,
        typer.Option(
            "--no-register",
            help="Don't register project in global registry.",
        ),
    ] = False,
) -> None:
    """
    Create a new project.

    Creates a project directory with the specified template structure
    and registers it in the global registry.

    Templates:
    - basic: Minimal structure (data/, output/)
    - research: Full structure with config/, templates/ directories

    Example:
        persona project create my-research
        persona project create my-study --template research
        persona project create demo --path ./projects --description "Demo project"
    """
    from persona.core.project import create_project

    console = get_console()
    target_path = path or Path.cwd()

    try:
        manager = create_project(
            name=name,
            path=target_path,
            template=template,
            description=description,
            register=not no_register,
        )

        project_path = target_path / name
        console.print(f"[green]✓[/green] Created project: {project_path}")

        if not no_register:
            console.print(f"[green]✓[/green] Registered in global registry")

        console.print("\n[bold]Next steps:[/bold]")
        console.print(f"  1. Add data files to {project_path}/data/")
        console.print(f"  2. Run: persona generate --from {name}")

    except FileExistsError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@project_app.command("register")
def register_project(
    name: Annotated[
        str,
        typer.Argument(help="Name to register the project as."),
    ],
    path: Annotated[
        Path,
        typer.Argument(help="Path to existing project directory."),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f",
            help="Update path if project already registered.",
        ),
    ] = False,
) -> None:
    """
    Register an existing project in the global registry.

    Allows referencing the project by name from anywhere.

    Example:
        persona project register my-research ./my-research
        persona project register demo /path/to/demo-project
    """
    from persona.core.project import get_registry_manager

    console = get_console()
    registry = get_registry_manager()

    # Validate path exists
    if not path.exists():
        console.print(f"[red]Error:[/red] Path does not exist: {path}")
        raise typer.Exit(1)

    # Check for project file
    has_project_file = (path / "project.yaml").exists() or (path / "persona.yaml").exists()
    if not has_project_file:
        console.print(f"[yellow]Warning:[/yellow] No project.yaml found in {path}")
        console.print("This directory may not be a valid Persona project.")
        if not typer.confirm("Register anyway?"):
            raise typer.Exit(0)

    try:
        if force and registry.project_exists(name):
            registry.update_project_path(name, path.resolve())
            console.print(f"[green]✓[/green] Updated project '{name}': {path.resolve()}")
        else:
            registry.register_project(name, path.resolve())
            console.print(f"[green]✓[/green] Registered project '{name}': {path.resolve()}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("Use --force to update the path.")
        raise typer.Exit(1)


@project_app.command("unregister")
def unregister_project(
    name: Annotated[
        str,
        typer.Argument(help="Name of project to unregister."),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f",
            help="Skip confirmation.",
        ),
    ] = False,
) -> None:
    """
    Remove a project from the global registry.

    This does not delete the project files, only removes the registry entry.

    Example:
        persona project unregister my-research
    """
    from persona.core.project import get_registry_manager

    console = get_console()
    registry = get_registry_manager()

    if not registry.project_exists(name):
        console.print(f"[yellow]Project '{name}' is not registered.[/yellow]")
        raise typer.Exit(0)

    if not force:
        if not typer.confirm(f"Unregister project '{name}'?"):
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    registry.unregister_project(name)
    console.print(f"[green]✓[/green] Unregistered project '{name}'")
    console.print("[dim]Project files were not deleted.[/dim]")


@project_app.command("show")
def show_project(
    name: Annotated[
        Optional[str],
        typer.Argument(help="Project name or path. Uses current directory if not specified."),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output as JSON.",
        ),
    ] = False,
) -> None:
    """
    Show project details.

    Displays project metadata, data sources, and configuration.

    Example:
        persona project show
        persona project show my-research
        persona project show --json
    """
    import json

    from persona.core.project import resolve_project

    console = get_console()

    ctx = resolve_project(name)
    if ctx is None:
        if name:
            console.print(f"[red]Error:[/red] Project '{name}' not found.")
        else:
            console.print("[yellow]No project found in current directory.[/yellow]")
        raise typer.Exit(1)

    project = ctx.project

    if json_output:
        print(json.dumps(project.to_yaml_dict(), indent=2, default=str))
        return

    console.print(Panel.fit(
        f"[bold]{project.name}[/bold]",
        border_style="cyan",
    ))

    if project.description:
        console.print(f"\n{project.description}")

    console.print(f"\n[bold]Path:[/bold] {ctx.project_path}")
    console.print(f"[bold]Template:[/bold] {project.template.value}")
    console.print(f"[bold]Created:[/bold] {project.created_at.strftime('%Y-%m-%d %H:%M')}")

    console.print("\n[bold]Defaults:[/bold]")
    console.print(f"  provider: {project.defaults.provider}")
    console.print(f"  model: {project.defaults.model or '[dim]provider default[/dim]'}")
    console.print(f"  count: {project.defaults.count}")
    console.print(f"  workflow: {project.defaults.workflow}")

    if project.data_sources:
        console.print("\n[bold]Data Sources:[/bold]")
        for ds in project.data_sources:
            path = ds.get_absolute_path(ctx.project_path)
            status = "[green]✓[/green]" if path.exists() else "[red]missing[/red]"
            console.print(f"  {ds.name}: {ds.path} {status}")
    else:
        console.print("\n[dim]No data sources registered.[/dim]")
        console.print("Add data sources with: persona project add-source")


@project_app.command("add-source")
def add_data_source(
    name: Annotated[
        str,
        typer.Argument(help="Name for the data source."),
    ],
    path: Annotated[
        str,
        typer.Argument(help="Relative path to data file from project root."),
    ],
    project: Annotated[
        Optional[str],
        typer.Option(
            "--project", "-p",
            help="Project to add source to. Uses current directory if not specified.",
        ),
    ] = None,
    source_type: Annotated[
        str,
        typer.Option(
            "--type", "-t",
            help="Data type (qualitative, quantitative, mixed, raw).",
        ),
    ] = "raw",
    description: Annotated[
        Optional[str],
        typer.Option(
            "--description", "-d",
            help="Description of the data source.",
        ),
    ] = None,
) -> None:
    """
    Add a data source to a project.

    Data sources allow referencing specific data files by name.

    Example:
        persona project add-source interviews data/interviews.csv
        persona project add-source survey data/survey.json --type quantitative
    """
    from persona.core.project import load_project, resolve_project

    console = get_console()

    # Resolve project
    ctx = resolve_project(project)
    if ctx is None:
        if project:
            console.print(f"[red]Error:[/red] Project '{project}' not found.")
        else:
            console.print("[yellow]No project found in current directory.[/yellow]")
        raise typer.Exit(1)

    # Load project manager
    manager = load_project(ctx.project_path)

    try:
        ds = manager.add_data_source(
            name=name,
            path=path,
            source_type=source_type,
            description=description,
        )
        console.print(f"[green]✓[/green] Added data source '{name}': {path}")

        # Check if file exists
        abs_path = ds.get_absolute_path(ctx.project_path)
        if not abs_path.exists():
            console.print(f"[yellow]Warning:[/yellow] File does not exist: {abs_path}")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@project_app.command("remove-source")
def remove_data_source(
    name: Annotated[
        str,
        typer.Argument(help="Name of data source to remove."),
    ],
    project: Annotated[
        Optional[str],
        typer.Option(
            "--project", "-p",
            help="Project to remove source from. Uses current directory if not specified.",
        ),
    ] = None,
) -> None:
    """
    Remove a data source from a project.

    Example:
        persona project remove-source interviews
    """
    from persona.core.project import load_project, resolve_project

    console = get_console()

    # Resolve project
    ctx = resolve_project(project)
    if ctx is None:
        if project:
            console.print(f"[red]Error:[/red] Project '{project}' not found.")
        else:
            console.print("[yellow]No project found in current directory.[/yellow]")
        raise typer.Exit(1)

    # Load project manager
    manager = load_project(ctx.project_path)

    if manager.remove_data_source(name):
        console.print(f"[green]✓[/green] Removed data source '{name}'")
    else:
        console.print(f"[yellow]Data source '{name}' not found.[/yellow]")


@project_app.command("init-registry")
def init_registry(
    force: Annotated[
        bool,
        typer.Option(
            "--force", "-f",
            help="Overwrite existing registry.",
        ),
    ] = False,
) -> None:
    """
    Initialise the project registry.

    Creates the global registry file for project management.

    Example:
        persona project init-registry
    """
    from persona.core.project import get_registry_manager

    console = get_console()
    registry = get_registry_manager()

    try:
        path = registry.init_registry(force=force)
        console.print(f"[green]✓[/green] Created registry: {path}")
    except FileExistsError as e:
        console.print(f"[yellow]Registry already exists:[/yellow] {e}")
        console.print("Use --force to reinitialise.")
        raise typer.Exit(1)


@project_app.command("defaults")
def show_or_set_defaults(
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            help="Set default provider.",
        ),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            help="Set default model.",
        ),
    ] = None,
    count: Annotated[
        Optional[int],
        typer.Option(
            "--count",
            help="Set default persona count.",
        ),
    ] = None,
) -> None:
    """
    Show or set global defaults.

    Without options, shows current defaults. With options, updates them.

    Example:
        persona project defaults
        persona project defaults --provider openai
        persona project defaults --count 5
    """
    from persona.core.project import get_registry_manager

    console = get_console()
    registry = get_registry_manager()

    # If any option provided, set values
    if any([provider, model, count]):
        registry.set_defaults(provider=provider, model=model, count=count)
        console.print("[green]✓[/green] Updated global defaults")

    # Show current defaults
    defaults = registry.get_defaults()
    console.print("\n[bold]Global Defaults:[/bold]")
    console.print(f"  provider: {defaults.provider}")
    console.print(f"  model: {defaults.model or '[dim]provider default[/dim]'}")
    console.print(f"  count: {defaults.count}")
