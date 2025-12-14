"""
Workflow management CLI commands.

Commands for listing, creating, and managing custom workflows.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.ui.console import get_console

workflow_app = typer.Typer(
    name="workflow",
    help="Manage custom workflows.",
    no_args_is_help=True,
)


@workflow_app.command("list")
def list_workflows(
    source: Annotated[
        Optional[str],
        typer.Option(
            "--source", "-s",
            help="Filter by source (builtin, user, project).",
        ),
    ] = None,
    tag: Annotated[
        Optional[str],
        typer.Option(
            "--tag", "-t",
            help="Filter by tag.",
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
    List available workflows.

    Example:
        persona workflow list
        persona workflow list --source builtin
        persona workflow list --tag healthcare
    """
    import json

    from persona.core.config import CustomWorkflowLoader

    console = get_console()
    loader = CustomWorkflowLoader()

    if json_output:
        result = {
            "command": "workflow list",
            "success": True,
            "data": {
                "workflows": [],
            },
        }

        for workflow_id in loader.list_workflows(source=source, tag=tag):
            try:
                info = loader.get_info(workflow_id)
                result["data"]["workflows"].append({
                    "id": info.id,
                    "name": info.name,
                    "source": info.source,
                    "description": info.description,
                    "step_count": info.step_count,
                    "tags": info.tags,
                })
            except Exception as e:
                result["data"]["workflows"].append({
                    "id": workflow_id,
                    "error": str(e),
                })

        print(json.dumps(result, indent=2))
        return

    # Rich output
    console.print(Panel.fit(
        "[bold]Available Workflows[/bold]",
        border_style="cyan",
    ))

    workflows = loader.list_workflows(source=source, tag=tag)

    if not workflows:
        console.print("\n[dim]No workflows found.[/dim]")
        if not source:
            console.print("[dim]Run 'persona workflow create' to create one.[/dim]")
        return

    # Group by source
    by_source: dict[str, list] = {"builtin": [], "user": [], "project": []}

    for workflow_id in workflows:
        try:
            info = loader.get_info(workflow_id)
            by_source[info.source].append(info)
        except Exception:
            continue

    for source_name, source_workflows in by_source.items():
        if not source_workflows:
            continue

        source_label = {
            "builtin": "Built-in Workflows",
            "user": "User Workflows (~/.persona/workflows/)",
            "project": "Project Workflows (.persona/workflows/)",
        }.get(source_name, source_name)

        console.print(f"\n[bold]{source_label}:[/bold]")

        for info in source_workflows:
            tags_str = ", ".join(info.tags) if info.tags else ""
            console.print(f"  • {info.id}")
            console.print(f"    [dim]{info.name}[/dim]")
            if info.description:
                desc = info.description[:60] + "..." if len(info.description) > 60 else info.description
                console.print(f"    [dim]{desc}[/dim]")
            console.print(f"    [cyan]Steps: {info.step_count}[/cyan]")
            if tags_str:
                console.print(f"    [cyan]Tags: {tags_str}[/cyan]")


@workflow_app.command("show")
def show_workflow(
    workflow_id: Annotated[
        str,
        typer.Argument(help="Workflow ID to show."),
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
    Show details for a workflow.

    Example:
        persona workflow show default
        persona workflow show research --json
    """
    import json

    from persona.core.config import CustomWorkflowLoader

    console = get_console()
    loader = CustomWorkflowLoader()

    try:
        config = loader.load(workflow_id)
        info = loader.get_info(workflow_id)
    except FileNotFoundError as e:
        if json_output:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if json_output:
        result = {
            "command": "workflow show",
            "success": True,
            "data": config.model_dump(mode="json"),
        }
        result["data"]["source"] = info.source
        if info.path:
            result["data"]["path"] = str(info.path)
        print(json.dumps(result, indent=2))
        return

    # Rich output
    console.print(Panel.fit(
        f"[bold]{config.name}[/bold] ({config.id})",
        border_style="cyan",
    ))

    table = Table(show_header=False, box=None)
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("ID", config.id)
    table.add_row("Name", config.name)
    table.add_row("Source", info.source)
    if info.path:
        table.add_row("Path", str(info.path))
    if config.description:
        table.add_row("Description", config.description)
    if config.author:
        table.add_row("Author", config.author)
    table.add_row("Version", config.version)
    if config.tags:
        table.add_row("Tags", ", ".join(config.tags))
    table.add_row("Provider", config.provider)
    if config.model:
        table.add_row("Model", config.model)
    table.add_row("Temperature", str(config.temperature))
    table.add_row("Max Tokens", f"{config.max_tokens:,}")

    console.print(table)

    # Steps
    console.print("\n[bold]Steps:[/bold]")
    for i, step in enumerate(config.steps, 1):
        console.print(f"\n  [cyan]{i}. {step.name}[/cyan]")
        console.print(f"     Template: {step.template}")
        if step.model:
            console.print(f"     Model: {step.model}")
        if step.input:
            console.print(f"     Input: {step.input}")
        if step.output:
            console.print(f"     Output: {step.output}")

    # Variables
    if config.variables:
        console.print("\n[bold]Default Variables:[/bold]")
        for key, value in config.variables.items():
            console.print(f"  • {key}: {value}")


@workflow_app.command("create")
def create_workflow(
    workflow_id: Annotated[
        str,
        typer.Argument(help="Unique workflow ID."),
    ],
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Human-readable name."),
    ],
    description: Annotated[
        str,
        typer.Option("--description", "-d", help="Workflow description."),
    ] = "",
    template: Annotated[
        str,
        typer.Option("--template", "-t", help="Template to use (default: builtin/default)."),
    ] = "builtin/default",
    provider: Annotated[
        str,
        typer.Option("--provider", "-p", help="Default provider."),
    ] = "anthropic",
    tags: Annotated[
        Optional[str],
        typer.Option("--tags", help="Comma-separated tags."),
    ] = None,
    project_level: Annotated[
        bool,
        typer.Option("--project", help="Save to project directory."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing workflow."),
    ] = False,
) -> None:
    """
    Create a new custom workflow.

    Example:
        persona workflow create my-workflow --name "My Workflow"
        persona workflow create healthcare-v2 --name "Healthcare v2" --template builtin/healthcare
    """
    from persona.core.config import WorkflowConfig, WorkflowStep, CustomWorkflowLoader

    console = get_console()
    loader = CustomWorkflowLoader()

    # Check if exists
    if loader.exists(workflow_id) and not force:
        info = loader.get_info(workflow_id)
        if info.source != "builtin":
            console.print(f"[red]Error:[/red] Workflow '{workflow_id}' already exists.")
            console.print("Use --force to overwrite.")
            raise typer.Exit(1)

    # Prepare tags list
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Create config
    try:
        config = WorkflowConfig(
            id=workflow_id,
            name=name,
            description=description,
            provider=provider,
            tags=tag_list,
            steps=[
                WorkflowStep(
                    name="generate",
                    template=template,
                    output="personas",
                ),
            ],
            variables={
                "complexity": "moderate",
                "detail_level": "standard",
                "include_reasoning": False,
            },
        )
    except Exception as e:
        console.print(f"[red]Error:[/red] Invalid configuration: {e}")
        raise typer.Exit(1)

    # Save
    try:
        path = loader.save(config, user_level=not project_level, overwrite=force)
        console.print(f"[green]✓[/green] Workflow '{workflow_id}' created.")
        console.print(f"  Saved to: {path}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@workflow_app.command("validate")
def validate_workflow(
    workflow_id: Annotated[
        str,
        typer.Argument(help="Workflow ID to validate."),
    ],
) -> None:
    """
    Validate a workflow configuration.

    Example:
        persona workflow validate my-workflow
    """
    from persona.core.config import CustomWorkflowLoader

    console = get_console()
    loader = CustomWorkflowLoader()

    console.print(f"[bold]Validating workflow:[/bold] {workflow_id}")
    console.print()

    is_valid, errors = loader.validate_workflow(workflow_id)

    if is_valid:
        console.print("[green]✓ Workflow validation passed[/green]")

        # Show summary
        try:
            config = loader.load(workflow_id)
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(f"  Steps: {len(config.steps)}")
            console.print(f"  Provider: {config.provider}")
            if config.model:
                console.print(f"  Model: {config.model}")
        except Exception:
            pass
    else:
        console.print("[red]✗ Workflow validation failed[/red]")
        for error in errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)


@workflow_app.command("remove")
def remove_workflow(
    workflow_id: Annotated[
        str,
        typer.Argument(help="Workflow ID to remove."),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation."),
    ] = False,
) -> None:
    """
    Remove a custom workflow.

    Example:
        persona workflow remove my-workflow
    """
    from persona.core.config import CustomWorkflowLoader

    console = get_console()
    loader = CustomWorkflowLoader()

    if not loader.exists(workflow_id):
        console.print(f"[red]Error:[/red] Workflow '{workflow_id}' not found.")
        raise typer.Exit(1)

    try:
        info = loader.get_info(workflow_id)
        if info.source == "builtin":
            console.print(f"[red]Error:[/red] Cannot remove built-in workflow.")
            raise typer.Exit(1)
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Workflow '{workflow_id}' not found.")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Remove workflow '{workflow_id}'?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    if loader.delete(workflow_id):
        console.print(f"[green]✓[/green] Workflow '{workflow_id}' removed.")
    else:
        console.print(f"[red]Error:[/red] Failed to remove workflow.")
        raise typer.Exit(1)
