"""
Experiment management commands.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from persona.core.experiments import ExperimentManager

experiment_app = typer.Typer(
    name="experiment",
    help="Manage experiments.",
)

# Constrain output width for cleaner display
console = Console(width=min(100, Console().width))


def _get_manager(base_dir: Optional[Path] = None) -> ExperimentManager:
    """Get experiment manager with optional custom base directory."""
    return ExperimentManager(base_dir=base_dir or Path("./experiments"))


@experiment_app.command("create")
def create(
    name: Annotated[
        str,
        typer.Argument(help="Name for the experiment."),
    ],
    description: Annotated[
        Optional[str],
        typer.Option(
            "--description",
            "-d",
            help="Description of the experiment.",
        ),
    ] = None,
    provider: Annotated[
        str,
        typer.Option(
            "--provider",
            "-p",
            help="Default LLM provider.",
        ),
    ] = "anthropic",
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-n",
            help="Default persona count.",
        ),
    ] = 3,
    base_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--base-dir",
            "-b",
            help="Base directory for experiments.",
        ),
    ] = None,
) -> None:
    """
    Create a new experiment.

    Example:
        persona experiment create my-research -d "User research study"
    """
    manager = _get_manager(base_dir)

    try:
        exp = manager.create(
            name=name,
            description=description or "",
            provider=provider,
            count=count,
        )
        console.print(f"[green]✓[/green] Created experiment: [bold]{exp.name}[/bold]")
        console.print(f"  Path: {exp.path}")
        console.print(f"\nNext steps:")
        console.print(f"  1. Add data files to: {exp.data_dir}")
        console.print(f"  2. Run: persona generate --experiment {exp.name}")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@experiment_app.command("list")
def list_experiments(
    base_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--base-dir",
            "-b",
            help="Base directory for experiments.",
        ),
    ] = None,
) -> None:
    """
    List all experiments.

    Example:
        persona experiment list
    """
    manager = _get_manager(base_dir)
    experiments = manager.list_experiments()

    if not experiments:
        console.print("[yellow]No experiments found.[/yellow]")
        console.print("Create one with: persona experiment create <name>")
        return

    table = Table(title="Experiments")
    table.add_column("Name", style="cyan")
    table.add_column("Description")
    table.add_column("Provider")
    table.add_column("Outputs")

    for exp_name in experiments:
        try:
            exp = manager.load(exp_name)
            outputs = exp.list_outputs()
            table.add_row(
                exp_name,
                exp.config.description or "-",
                exp.config.provider,
                str(len(outputs)),
            )
        except Exception:
            table.add_row(exp_name, "[red]Error loading[/red]", "-", "-")

    console.print(table)


@experiment_app.command("show")
def show(
    name: Annotated[
        str,
        typer.Argument(help="Experiment name."),
    ],
    base_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--base-dir",
            "-b",
            help="Base directory for experiments.",
        ),
    ] = None,
) -> None:
    """
    Show experiment details.

    Example:
        persona experiment show my-research
    """
    manager = _get_manager(base_dir)

    try:
        exp = manager.load(name)
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Experiment not found: {name}")
        raise typer.Exit(1)

    # Show configuration
    panel_content = f"""[bold]Name:[/bold] {exp.name}
[bold]Path:[/bold] {exp.path}
[bold]Description:[/bold] {exp.config.description or '-'}

[bold]Configuration:[/bold]
  Provider: {exp.config.provider}
  Model: {exp.config.model or 'Default'}
  Workflow: {exp.config.workflow}
  Persona Count: {exp.config.count}
  Complexity: {exp.config.complexity}
  Detail Level: {exp.config.detail_level}"""

    console.print(Panel(panel_content, title=f"Experiment: {exp.name}"))

    # Show outputs
    outputs = exp.list_outputs()
    if outputs:
        console.print(f"\n[bold]Outputs ({len(outputs)}):[/bold]")
        for output in outputs:
            console.print(f"  • {output.name}")
    else:
        console.print("\n[dim]No outputs yet.[/dim]")


@experiment_app.command("delete")
def delete(
    name: Annotated[
        str,
        typer.Argument(help="Experiment name."),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Skip confirmation prompt.",
        ),
    ] = False,
    base_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--base-dir",
            "-b",
            help="Base directory for experiments.",
        ),
    ] = None,
) -> None:
    """
    Delete an experiment.

    Example:
        persona experiment delete my-research --force
    """
    manager = _get_manager(base_dir)

    if not manager.exists(name):
        console.print(f"[red]Error:[/red] Experiment not found: {name}")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(
            f"Delete experiment '{name}' and all its data?",
            default=False,
        )
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    try:
        manager.delete(name, confirm=True)
        console.print(f"[green]✓[/green] Deleted experiment: {name}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
