"""
Experiment management commands.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.config.registry import ExperimentRegistry, get_registry
from persona.core.experiments import (
    ExperimentEditor,
    ExperimentManager,
    RunHistory,
    RunHistoryManager,
)
from persona.ui.console import get_console

experiment_app = typer.Typer(
    name="experiment",
    help="Manage experiments.",
)


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

    console = get_console()
    try:
        exp = manager.create(
            name=name,
            description=description or "",
            provider=provider,
            count=count,
        )
        console.print(f"[green]✓[/green] Created experiment: [bold]{exp.name}[/bold]")
        console.print(f"  Path: {exp.path}")
        console.print("\nNext steps:")
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
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    List all experiments.

    Example:
        persona experiment list
        persona experiment list --json
    """
    import json

    console = get_console()
    manager = _get_manager(base_dir)
    experiments = manager.list_experiments()

    if json_output:
        result = {
            "command": "experiment list",
            "success": True,
            "data": {
                "experiments": [],
            },
        }
        for exp_name in experiments:
            try:
                exp = manager.load(exp_name)
                outputs = exp.list_outputs()
                result["data"]["experiments"].append(
                    {
                        "name": exp_name,
                        "description": exp.config.description or "",
                        "provider": exp.config.provider,
                        "model": exp.config.model,
                        "count": exp.config.count,
                        "outputs_count": len(outputs),
                    }
                )
            except Exception as e:
                result["data"]["experiments"].append(
                    {
                        "name": exp_name,
                        "error": str(e),
                    }
                )
        print(json.dumps(result, indent=2))
        return

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
    console = get_console()
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
    console = get_console()
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


def _parse_set_value(value_str: str) -> tuple[str, str]:
    """Parse a --set value like 'field=value' into (field, value)."""
    if "=" not in value_str:
        raise ValueError(f"Invalid format: {value_str}. Use 'field=value'")
    field, value = value_str.split("=", 1)
    return field.strip(), value.strip()


@experiment_app.command("edit")
def edit(
    name: Annotated[
        str,
        typer.Argument(help="Experiment name."),
    ],
    set_values: Annotated[
        Optional[list[str]],
        typer.Option(
            "--set",
            "-s",
            help="Set field value (format: field=value). Can be repeated.",
        ),
    ] = None,
    add_source: Annotated[
        Optional[list[Path]],
        typer.Option(
            "--add-source",
            help="Add data source file. Can be repeated.",
        ),
    ] = None,
    remove_source: Annotated[
        Optional[list[str]],
        typer.Option(
            "--remove-source",
            help="Remove data source by name. Can be repeated.",
        ),
    ] = None,
    rollback: Annotated[
        int,
        typer.Option(
            "--rollback",
            help="Rollback N recent edits.",
        ),
    ] = 0,
    clear_history: Annotated[
        bool,
        typer.Option(
            "--clear-history",
            help="Clear edit history.",
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
    Edit experiment configuration.

    Examples:
        # Set a single field
        persona experiment edit my-research --set count=5

        # Set nested field
        persona experiment edit my-research --set generation.model=gpt-4o

        # Set multiple fields
        persona experiment edit my-research --set count=5 --set provider=openai

        # Add data sources
        persona experiment edit my-research --add-source ./data.csv

        # Remove data source
        persona experiment edit my-research --remove-source old-data.csv

        # Rollback last edit
        persona experiment edit my-research --rollback 1

        # Clear edit history
        persona experiment edit my-research --clear-history
    """
    console = get_console()
    manager = _get_manager(base_dir)
    editor = ExperimentEditor(manager)

    # Check experiment exists
    if not manager.exists(name):
        console.print(f"[red]Error:[/red] Experiment not found: {name}")
        raise typer.Exit(1)

    changes_made = False

    # Handle clear history
    if clear_history:
        editor.clear_history(name)
        console.print(f"[green]✓[/green] Cleared edit history for: {name}")
        changes_made = True

    # Handle rollback
    if rollback > 0:
        try:
            config = editor.rollback(name, rollback)
            if config:
                console.print(f"[green]✓[/green] Rolled back {rollback} edit(s)")
                changes_made = True
            else:
                console.print("[yellow]Nothing to rollback.[/yellow]")
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    # Handle set values
    if set_values:
        for set_value in set_values:
            try:
                field, value = _parse_set_value(set_value)
                config = editor.set_field(name, field, value)
                console.print(f"[green]✓[/green] Set {field} = {value}")
                changes_made = True
            except ValueError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

    # Handle add sources
    if add_source:
        for source in add_source:
            try:
                dest = editor.add_source(name, source)
                console.print(f"[green]✓[/green] Added source: {source.name}")
                changes_made = True
            except (FileNotFoundError, ValueError) as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

    # Handle remove sources
    if remove_source:
        for source in remove_source:
            try:
                editor.remove_source(name, source)
                console.print(f"[green]✓[/green] Removed source: {source}")
                changes_made = True
            except FileNotFoundError as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

    # If no changes requested, show current config
    if not changes_made:
        exp = manager.load(name)
        sources = editor.list_sources(name)
        history = editor.get_history(name)

        console.print(
            Panel.fit(
                f"[bold]Edit Experiment: {name}[/bold]",
                border_style="cyan",
            )
        )

        console.print("\n[bold]Current Configuration:[/bold]")
        console.print(f"  provider: {exp.config.provider}")
        console.print(f"  model: {exp.config.model or 'default'}")
        console.print(f"  workflow: {exp.config.workflow}")
        console.print(f"  count: {exp.config.count}")
        console.print(f"  complexity: {exp.config.complexity}")
        console.print(f"  detail_level: {exp.config.detail_level}")

        console.print(f"\n[bold]Data Sources ({len(sources)}):[/bold]")
        if sources:
            for source in sources:
                console.print(f"  • {source}")
        else:
            console.print("  [dim]No data sources.[/dim]")

        console.print(f"\n[bold]Edit History ({len(history)} entries):[/bold]")
        if history:
            for entry in history[-5:]:  # Show last 5
                console.print(
                    f"  • [{entry.timestamp.strftime('%Y-%m-%d %H:%M')}] "
                    f"{entry.action}: {entry.field}"
                )
            if len(history) > 5:
                console.print(f"  [dim]...and {len(history) - 5} more[/dim]")
        else:
            console.print("  [dim]No edit history.[/dim]")

        console.print("\n[bold]Usage:[/bold]")
        console.print("  persona experiment edit my-experiment --set count=5")
        console.print("  persona experiment edit my-experiment --add-source data.csv")


@experiment_app.command("sources")
def list_sources(
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
    List data sources for an experiment.

    Example:
        persona experiment sources my-research
    """
    console = get_console()
    manager = _get_manager(base_dir)
    editor = ExperimentEditor(manager)

    if not manager.exists(name):
        console.print(f"[red]Error:[/red] Experiment not found: {name}")
        raise typer.Exit(1)

    sources = editor.list_sources(name)

    if not sources:
        console.print("[yellow]No data sources found.[/yellow]")
        console.print(
            f"Add sources with: persona experiment edit {name} --add-source <file>"
        )
        return

    console.print(f"[bold]Data Sources for {name}:[/bold]")
    for source in sources:
        console.print(f"  • {source}")


@experiment_app.command("history")
def history(
    name: Annotated[
        str,
        typer.Argument(help="Experiment name."),
    ],
    last: Annotated[
        Optional[int],
        typer.Option(
            "--last",
            "-n",
            help="Show only the last N runs.",
        ),
    ] = None,
    diff: Annotated[
        Optional[str],
        typer.Option(
            "--diff",
            help="Compare two runs (format: 'id1,id2').",
        ),
    ] = None,
    stats: Annotated[
        bool,
        typer.Option(
            "--stats",
            "-s",
            help="Show aggregate statistics.",
        ),
    ] = False,
    status_filter: Annotated[
        Optional[str],
        typer.Option(
            "--status",
            help="Filter by status (completed, failed).",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
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
    Show run history for an experiment.

    Examples:
        # Show all runs
        persona experiment history my-research

        # Show last 5 runs
        persona experiment history my-research --last 5

        # Show statistics
        persona experiment history my-research --stats

        # Compare two runs
        persona experiment history my-research --diff "1,3"

        # Filter by status
        persona experiment history my-research --status completed
    """
    import json as json_module

    console = get_console()
    manager = _get_manager(base_dir)
    run_history = RunHistory(manager)

    if not manager.exists(name):
        if json_output:
            print(json_module.dumps({"error": f"Experiment not found: {name}"}))
        else:
            console.print(f"[red]Error:[/red] Experiment not found: {name}")
        raise typer.Exit(1)

    # Handle diff
    if diff:
        try:
            parts = diff.split(",")
            if len(parts) != 2:
                raise ValueError("Invalid format")
            id1, id2 = int(parts[0].strip()), int(parts[1].strip())

            diff_result = run_history.diff_runs(name, id1, id2)

            if json_output:
                print(json_module.dumps(diff_result, indent=2))
            else:
                console.print(
                    Panel.fit(
                        f"[bold]Run Comparison: #{id1} vs #{id2}[/bold]",
                        border_style="cyan",
                    )
                )

                if diff_result["differences"]:
                    console.print("\n[bold]Differences:[/bold]")
                    for field, vals in diff_result["differences"].items():
                        console.print(f"  {field}: {vals['run_1']} → {vals['run_2']}")
                else:
                    console.print("\n[dim]No differences found.[/dim]")

                console.print("\n[bold]Delta:[/bold]")
                for field, delta in diff_result["delta"].items():
                    if delta != 0:
                        sign = "+" if delta > 0 else ""
                        if field == "cost":
                            console.print(f"  {field}: {sign}${delta:.4f}")
                        else:
                            console.print(f"  {field}: {sign}{delta}")
            return

        except ValueError as e:
            if json_output:
                print(json_module.dumps({"error": str(e)}))
            else:
                console.print(f"[red]Error:[/red] {e}")
                console.print("Use format: --diff '1,3' to compare runs #1 and #3")
            raise typer.Exit(1)

    # Handle stats
    if stats:
        statistics = run_history.get_statistics(name)

        if json_output:
            print(json_module.dumps(statistics.to_dict(), indent=2))
        else:
            console.print(
                Panel.fit(
                    f"[bold]Statistics for {name}[/bold]",
                    border_style="cyan",
                )
            )

            console.print("\n[bold]Runs:[/bold]")
            console.print(f"  Total: {statistics.total_runs}")
            console.print(f"  Completed: {statistics.completed_runs}")
            console.print(f"  Failed: {statistics.failed_runs}")

            console.print("\n[bold]Output:[/bold]")
            console.print(f"  Total personas: {statistics.total_personas}")
            console.print(f"  Avg per run: {statistics.avg_personas_per_run:.1f}")

            console.print("\n[bold]Cost:[/bold]")
            console.print(f"  Total: ${statistics.total_cost:.4f}")
            console.print(f"  Avg per run: ${statistics.avg_cost_per_run:.4f}")

            console.print("\n[bold]Tokens:[/bold]")
            console.print(f"  Input: {statistics.total_input_tokens:,}")
            console.print(f"  Output: {statistics.total_output_tokens:,}")

            if statistics.models_used:
                console.print(
                    f"\n[bold]Models used:[/bold] {', '.join(statistics.models_used)}"
                )
            if statistics.providers_used:
                console.print(
                    f"[bold]Providers used:[/bold] {', '.join(statistics.providers_used)}"
                )
        return

    # Default: show run history
    runs = run_history.get_runs(name, last=last, status=status_filter)

    if json_output:
        output = {
            "experiment": name,
            "runs": [r.to_dict() for r in runs],
        }
        print(json_module.dumps(output, indent=2))
        return

    if not runs:
        console.print(f"[yellow]No runs found for experiment: {name}[/yellow]")
        return

    console.print(
        Panel.fit(
            f"[bold]Run History for {name}[/bold]",
            border_style="cyan",
        )
    )

    table = Table()
    table.add_column("Run", style="cyan", justify="right")
    table.add_column("Timestamp")
    table.add_column("Model")
    table.add_column("Personas", justify="right")
    table.add_column("Cost", justify="right")
    table.add_column("Status")

    for run in runs:
        status_icon = (
            "[green]✓[/green]" if run.status == "completed" else "[red]✗[/red]"
        )
        table.add_row(
            f"#{run.run_id}",
            run.timestamp.strftime("%Y-%m-%d %H:%M"),
            run.model,
            str(run.persona_count),
            f"${run.cost:.4f}",
            status_icon,
        )

    console.print(table)

    # Summary
    stats = run_history.get_statistics(name)
    console.print(
        f"\n[bold]Total:[/bold] {stats.total_runs} runs, "
        f"{stats.total_personas} personas, ${stats.total_cost:.2f}"
    )


@experiment_app.command("record-run")
def record_run(
    name: Annotated[
        str,
        typer.Argument(help="Experiment name."),
    ],
    model: Annotated[
        str,
        typer.Option("--model", "-m", help="Model used."),
    ],
    provider: Annotated[
        str,
        typer.Option("--provider", "-p", help="Provider used."),
    ],
    personas: Annotated[
        int,
        typer.Option("--personas", "-n", help="Number of personas."),
    ] = 0,
    cost: Annotated[
        float,
        typer.Option("--cost", help="Cost in USD."),
    ] = 0.0,
    status: Annotated[
        str,
        typer.Option("--status", help="Run status."),
    ] = "completed",
    output_dir: Annotated[
        Optional[str],
        typer.Option("--output-dir", help="Output directory path."),
    ] = None,
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
    Record a generation run in history.

    This command is typically called automatically by the generate command,
    but can be used manually to record external runs.

    Example:
        persona experiment record-run my-research \\
            --model gpt-4o --provider openai \\
            --personas 3 --cost 0.45
    """
    console = get_console()
    manager = _get_manager(base_dir)
    run_history = RunHistory(manager)

    if not manager.exists(name):
        console.print(f"[red]Error:[/red] Experiment not found: {name}")
        raise typer.Exit(1)

    run = run_history.record_run(
        name=name,
        model=model,
        provider=provider,
        persona_count=personas,
        cost=cost,
        status=status,
        output_dir=output_dir or "",
    )

    console.print(f"[green]✓[/green] Recorded run #{run.run_id} for {name}")


@experiment_app.command("clear-history")
def clear_run_history(
    name: Annotated[
        str,
        typer.Argument(help="Experiment name."),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Skip confirmation.",
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
    Clear run history for an experiment.

    Example:
        persona experiment clear-history my-research --force
    """
    console = get_console()
    manager = _get_manager(base_dir)
    run_history = RunHistory(manager)

    if not manager.exists(name):
        console.print(f"[red]Error:[/red] Experiment not found: {name}")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(
            f"Clear all run history for '{name}'?",
            default=False,
        )
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(0)

    run_history.clear_history(name)
    console.print(f"[green]✓[/green] Cleared run history for {name}")


@experiment_app.command("runs")
def runs(
    name: Annotated[
        str,
        typer.Argument(help="Experiment name."),
    ],
    last: Annotated[
        Optional[int],
        typer.Option(
            "--last",
            "-n",
            help="Show only the last N runs.",
        ),
    ] = None,
    status_filter: Annotated[
        Optional[str],
        typer.Option(
            "--status",
            help="Filter by status (success, failed, partial, running).",
        ),
    ] = None,
    provider_filter: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            help="Filter by provider.",
        ),
    ] = None,
    model_filter: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            help="Filter by model.",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
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
    Show tracked generation runs for an experiment.

    Displays runs recorded in the experiment's history.json file,
    which is automatically updated when using --experiment flag.

    Examples:
        # Show all runs
        persona experiment runs my-research

        # Show last 5 runs
        persona experiment runs my-research --last 5

        # Filter by status
        persona experiment runs my-research --status success

        # Filter by provider
        persona experiment runs my-research --provider anthropic

        # JSON output
        persona experiment runs my-research --json
    """
    import json as json_module

    console = get_console()

    # Determine experiment path
    experiment_base = base_dir or Path("./experiments")
    experiment_path = experiment_base / name

    if not experiment_path.exists():
        if json_output:
            print(json_module.dumps({"error": f"Experiment not found: {name}"}))
        else:
            console.print(f"[red]Error:[/red] Experiment not found: {name}")
        raise typer.Exit(1)

    history_manager = RunHistoryManager(experiment_path, name)
    run_list = history_manager.list_runs(
        status=status_filter,
        provider=provider_filter,
        model=model_filter,
        limit=last,
    )

    if json_output:
        result = {
            "command": "experiment runs",
            "success": True,
            "data": {
                "experiment": name,
                "runs": [r.model_dump(mode="json") for r in run_list],
                "total": len(run_list),
            },
        }
        print(json_module.dumps(result, indent=2, default=str))
        return

    if not run_list:
        console.print(f"[yellow]No runs recorded for experiment: {name}[/yellow]")
        console.print(
            "\n[dim]Tip: Runs are automatically recorded when using "
            "[cyan]--experiment {name}[/cyan] flag with generate command.[/dim]"
        )
        return

    # Display runs table
    table = Table(title=f"Runs for '{name}'")
    table.add_column("ID", style="cyan")
    table.add_column("Date", style="dim")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Personas", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("Status")

    for run in run_list:
        status_icon = {
            "success": "[green]✓[/green]",
            "failed": "[red]✗[/red]",
            "partial": "[yellow]~[/yellow]",
            "running": "[blue]⟳[/blue]",
        }.get(run.status, run.status)

        date_str = run.started_at.strftime("%Y-%m-%d %H:%M") if run.started_at else "-"

        table.add_row(
            run.run_id,
            date_str,
            run.provider,
            run.model,
            str(run.persona_count),
            str(run.tokens.total),
            status_icon,
        )

    console.print(table)

    # Summary
    total_personas = sum(r.persona_count for r in run_list)
    total_tokens = sum(r.tokens.total for r in run_list)
    success_count = sum(1 for r in run_list if r.status == "success")

    console.print(
        f"\n[bold]Summary:[/bold] {len(run_list)} runs, "
        f"{success_count} successful, {total_personas} personas, {total_tokens:,} tokens"
    )


@experiment_app.command("register")
def register(
    name: Annotated[
        str,
        typer.Argument(help="Name to register the experiment under."),
    ],
    path: Annotated[
        Path,
        typer.Argument(help="Path to the experiment directory."),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing registration.",
        ),
    ] = False,
) -> None:
    """
    Register an external experiment in the global registry.

    Allows experiments outside ./experiments/ to be referenced by name.
    Registered experiments are stored in ~/.config/persona/experiments.yaml

    Examples:
        # Register an experiment
        persona experiment register client-study /projects/client/personas

        # Overwrite existing registration
        persona experiment register client-study /new/path --force
    """
    console = get_console()
    registry = get_registry()

    try:
        registry.register(name, path, force=force)
        resolved_path = Path(path).resolve()
        console.print(f"[green]✓[/green] Registered experiment: [bold]{name}[/bold]")
        console.print(f"  Path: {resolved_path}")
        console.print(f"\nYou can now use:")
        console.print(f"  persona generate --from {name} --experiment {name}")
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print(f"\nUse [cyan]--force[/cyan] to overwrite.")
        raise typer.Exit(1)


@experiment_app.command("unregister")
def unregister(
    name: Annotated[
        str,
        typer.Argument(help="Name of the experiment to unregister."),
    ],
) -> None:
    """
    Remove an experiment from the global registry.

    Note: This only removes the registry entry, not the actual files.

    Example:
        persona experiment unregister client-study
    """
    console = get_console()
    registry = get_registry()

    if registry.unregister(name):
        console.print(f"[green]✓[/green] Unregistered experiment: {name}")
        console.print("[dim]Note: The experiment files were not deleted.[/dim]")
    else:
        console.print(f"[yellow]Warning:[/yellow] Experiment not found in registry: {name}")


@experiment_app.command("registry")
def list_registry(
    validate: Annotated[
        bool,
        typer.Option(
            "--validate",
            "-v",
            help="Check if registered paths still exist.",
        ),
    ] = False,
    cleanup: Annotated[
        bool,
        typer.Option(
            "--cleanup",
            help="Remove invalid registrations.",
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
    List all globally registered experiments.

    Shows experiments registered with 'persona experiment register'.

    Examples:
        # List all registered experiments
        persona experiment registry

        # Validate paths exist
        persona experiment registry --validate

        # Remove invalid entries
        persona experiment registry --cleanup
    """
    import json

    console = get_console()
    registry = get_registry()

    # Handle cleanup
    if cleanup:
        removed = registry.cleanup()
        if removed:
            console.print(f"[green]✓[/green] Removed {len(removed)} invalid registration(s):")
            for name in removed:
                console.print(f"  • {name}")
        else:
            console.print("[dim]No invalid registrations found.[/dim]")
        return

    experiments = registry.list_experiments()

    if json_output:
        result = {
            "command": "experiment registry",
            "success": True,
            "data": {
                "config_path": str(registry.config_path),
                "experiments": [
                    {"name": name, "path": str(path)}
                    for name, path in experiments
                ],
            },
        }

        if validate:
            errors = registry.validate()
            result["data"]["errors"] = [
                {"name": name, "error": error}
                for name, error in errors
            ]

        print(json.dumps(result, indent=2))
        return

    if not experiments:
        console.print("[yellow]No experiments registered.[/yellow]")
        console.print("\nRegister experiments with:")
        console.print("  persona experiment register <name> <path>")
        return

    console.print(
        Panel.fit(
            "[bold]Global Experiment Registry[/bold]",
            border_style="cyan",
        )
    )
    console.print(f"[dim]Config: {registry.config_path}[/dim]\n")

    table = Table()
    table.add_column("Name", style="cyan")
    table.add_column("Path")
    if validate:
        table.add_column("Status")

    errors_dict = {}
    if validate:
        errors = registry.validate()
        errors_dict = dict(errors)

    for name, path in experiments:
        if validate:
            if name in errors_dict:
                status = f"[red]✗ {errors_dict[name]}[/red]"
            else:
                status = "[green]✓ Valid[/green]"
            table.add_row(name, str(path), status)
        else:
            table.add_row(name, str(path))

    console.print(table)

    if validate and errors_dict:
        console.print(
            f"\n[yellow]Found {len(errors_dict)} invalid registration(s).[/yellow]"
        )
        console.print("Run with [cyan]--cleanup[/cyan] to remove them.")
