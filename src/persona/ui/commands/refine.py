"""
Refine command for iteratively improving personas.
"""

from pathlib import Path
from typing import Annotated, Optional
import json

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.refinement import PersonaRefiner
from persona.ui.console import get_console

refine_app = typer.Typer(
    name="refine",
    help="Interactively refine personas with natural language instructions.",
)


@refine_app.callback(invoke_without_command=True)
def refine(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file.",
            exists=True,
        ),
    ],
    instruction: Annotated[
        Optional[str],
        typer.Option(
            "--instruction",
            "-i",
            help="Refinement instruction to apply.",
        ),
    ] = None,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output path for refined persona (overwrites source if not specified).",
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
    Refine personas with natural language instructions.

    Apply modifications like "add a goal about efficiency" or
    "make more technical" to iteratively improve personas.

    Example:
        persona refine ./persona.json --instruction "Add goal: improve efficiency"
        persona refine ./persona.json -i "Make more technical" -o ./refined.json
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    from persona import __version__

    if not json_output:
        console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Load persona
    try:
        persona = _load_persona(persona_path)
    except Exception as e:
        if json_output:
            print(json.dumps({
                "command": "refine",
                "success": False,
                "error": str(e),
            }, indent=2))
        else:
            console.print(f"[red]Error loading persona:[/red] {e}")
        raise typer.Exit(1)

    if persona is None:
        if json_output:
            print(json.dumps({
                "command": "refine",
                "success": False,
                "error": "No persona found",
            }, indent=2))
        else:
            console.print("[yellow]No persona found to refine.[/yellow]")
        raise typer.Exit(1)

    if instruction is None:
        # No instruction provided - show current state and available templates
        if json_output:
            print(json.dumps({
                "command": "refine",
                "success": True,
                "data": {
                    "persona": persona.to_dict() if hasattr(persona, "to_dict") else {"id": persona.id, "name": persona.name},
                    "message": "No instruction provided. Use --instruction to refine.",
                },
            }, indent=2))
        else:
            console.print(Panel.fit(
                f"[bold]Persona Refinement[/bold]\n{persona.name} ({persona.id})",
                border_style="blue",
            ))
            console.print("\n[yellow]No instruction provided.[/yellow]")
            console.print("Use [cyan]--instruction[/cyan] to apply a refinement.\n")
            _show_persona_summary(console, persona)
            _show_instruction_examples(console)
        return

    # Apply refinement
    refiner = PersonaRefiner()
    session = refiner.create_session(persona)
    result = refiner.refine(session, instruction)

    if not result.success:
        if json_output:
            print(json.dumps({
                "command": "refine",
                "success": False,
                "error": result.error,
            }, indent=2))
        else:
            console.print(f"[red]Refinement failed:[/red] {result.error}")
        raise typer.Exit(1)

    # Save refined persona
    output_path = output or persona_path
    try:
        _save_persona(result.persona, output_path)
    except Exception as e:
        if json_output:
            print(json.dumps({
                "command": "refine",
                "success": False,
                "error": f"Failed to save: {e}",
            }, indent=2))
        else:
            console.print(f"[red]Failed to save:[/red] {e}")
        raise typer.Exit(1)

    if json_output:
        print(json.dumps({
            "command": "refine",
            "version": __version__,
            "success": True,
            "data": {
                "changes": result.changes,
                "version": result.version,
                "output_path": str(output_path),
                "persona": result.persona.to_dict() if hasattr(result.persona, "to_dict") else None,
            },
        }, indent=2))
        return

    # Rich output
    console.print(Panel.fit(
        f"[bold]Persona Refined[/bold]\n{persona.name} ({persona.id})",
        border_style="green",
    ))

    console.print(f"\n[bold]Instruction:[/bold] {instruction}")
    console.print(f"[bold]Version:[/bold] {result.version}")

    if result.changes:
        console.print("\n[bold]Changes applied:[/bold]")
        for change in result.changes:
            console.print(f"  [green]•[/green] {change}")

    console.print(f"\n[green]✓[/green] Saved to: {output_path}")


@refine_app.command("templates")
def list_templates() -> None:
    """
    List available refinement templates.

    Example:
        persona refine templates
    """
    console = get_console()

    from persona import __version__
    console.print(f"[dim]Persona {__version__}[/dim]\n")

    refiner = PersonaRefiner()
    templates = refiner.list_templates()

    console.print("[bold]Available Refinement Templates:[/bold]\n")

    table = Table()
    table.add_column("Template", style="cyan")
    table.add_column("Description")
    table.add_column("Affects")

    for name, details in templates.items():
        table.add_row(
            name,
            details.get("description", ""),
            ", ".join(details.get("affects", [])),
        )

    console.print(table)

    console.print("\n[dim]Use natural language instructions for refinement.[/dim]")


@refine_app.command("diff")
def show_diff(
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file with history.",
            exists=True,
        ),
    ],
    version_a: Annotated[
        int,
        typer.Option(
            "--from",
            "-a",
            help="First version to compare (default: 0).",
        ),
    ] = 0,
    version_b: Annotated[
        Optional[int],
        typer.Option(
            "--to",
            "-b",
            help="Second version to compare (default: current).",
        ),
    ] = None,
) -> None:
    """
    Show differences between persona versions.

    Example:
        persona refine diff ./persona.json --from 0 --to 2
    """
    console = get_console()

    from persona import __version__
    console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Load persona
    try:
        persona = _load_persona(persona_path)
    except Exception as e:
        console.print(f"[red]Error loading persona:[/red] {e}")
        raise typer.Exit(1)

    refiner = PersonaRefiner()
    session = refiner.create_session(persona)

    # Get diff
    diff = refiner.get_diff(session, version_a, version_b)

    if "error" in diff:
        console.print(f"[red]Error:[/red] {diff['error']}")
        raise typer.Exit(1)

    if not diff:
        console.print("[green]No differences found.[/green]")
        return

    console.print(Panel.fit(
        f"[bold]Version Diff[/bold]\n"
        f"Version {version_a} → {version_b or session.version}",
        border_style="blue",
    ))

    for field, changes in diff.items():
        console.print(f"\n[cyan]{field}:[/cyan]")

        if isinstance(changes, dict):
            if "from" in changes and "to" in changes:
                console.print(f"  [red]- {changes['from']}[/red]")
                console.print(f"  [green]+ {changes['to']}[/green]")
            elif "added" in changes or "removed" in changes:
                for item in changes.get("removed", []):
                    console.print(f"  [red]- {item}[/red]")
                for item in changes.get("added", []):
                    console.print(f"  [green]+ {item}[/green]")
            else:
                for key, val in changes.items():
                    if isinstance(val, dict) and "from" in val:
                        console.print(f"  {key}: [red]{val['from']}[/red] → [green]{val['to']}[/green]")


def _show_persona_summary(console, persona) -> None:
    """Show a summary of the persona."""
    console.print("[bold]Current Persona:[/bold]")

    table = Table(show_header=False, box=None)
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("Name", persona.name or "N/A")
    table.add_row("ID", persona.id)
    table.add_row("Goals", str(len(persona.goals or [])))
    table.add_row("Pain points", str(len(persona.pain_points or [])))
    table.add_row("Behaviours", str(len(persona.behaviours or [])))

    console.print(table)


def _show_instruction_examples(console) -> None:
    """Show example refinement instructions."""
    console.print("\n[bold]Example Instructions:[/bold]")
    examples = [
        'Add goal: "Improve team collaboration"',
        'Remove last goal',
        'Add pain point: "Lacks time for learning"',
        'Rename to "Alex Developer"',
        'Make more technical',
        'Simplify the summary',
    ]
    for example in examples:
        console.print(f"  [dim]--instruction[/dim] [cyan]{example}[/cyan]")


def _load_persona(path: Path):
    """Load a single persona from a file."""
    from persona.core.generation.parser import Persona

    with open(path) as f:
        data = json.load(f)

    if isinstance(data, list):
        if data:
            return Persona.from_dict(data[0])
        return None
    elif isinstance(data, dict):
        if "personas" in data and data["personas"]:
            return Persona.from_dict(data["personas"][0])
        else:
            return Persona.from_dict(data)
    return None


def _save_persona(persona, path: Path) -> None:
    """Save a persona to a file."""
    if hasattr(persona, "to_dict"):
        data = persona.to_dict()
    else:
        data = {
            "id": persona.id,
            "name": persona.name,
            "goals": list(persona.goals or []),
            "pain_points": list(persona.pain_points or []),
            "behaviours": list(persona.behaviours or []),
            "demographics": dict(persona.demographics or {}),
        }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)
