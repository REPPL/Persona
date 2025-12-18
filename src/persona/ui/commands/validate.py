"""
Validate command for checking persona quality.
"""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.validation import PersonaValidator, ValidationLevel
from persona.ui.console import get_console

validate_app = typer.Typer(
    name="validate",
    help="Validate generated personas for quality and consistency.",
)


@validate_app.callback(invoke_without_command=True)
def validate(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file or output directory.",
            exists=True,
        ),
    ],
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            help="Treat warnings as errors.",
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
    Validate personas for quality and consistency.

    Checks personas against built-in rules for completeness,
    uniqueness, and quality standards.

    Example:
        persona validate ./outputs/20250101_120000/
        persona validate ./personas.json --strict
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    from persona import __version__

    if not json_output:
        console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Load personas
    try:
        personas = _load_personas(persona_path)
    except Exception as e:
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "validate",
                        "success": False,
                        "error": str(e),
                    },
                    indent=2,
                )
            )
        else:
            console.print(f"[red]Error loading personas:[/red] {e}")
        raise typer.Exit(1)

    if not personas:
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "validate",
                        "success": False,
                        "error": "No personas found",
                    },
                    indent=2,
                )
            )
        else:
            console.print("[yellow]No personas found to validate.[/yellow]")
        raise typer.Exit(1)

    # Validate
    validator = PersonaValidator(strict=strict)
    results = validator.validate_batch(personas)

    # Calculate summary
    total = len(results)
    passed = sum(1 for r in results if r.is_valid)
    failed = total - passed
    total_errors = sum(len(r.errors) for r in results)
    total_warnings = sum(len(r.warnings) for r in results)
    avg_score = sum(r.score for r in results) / total if total > 0 else 0

    if json_output:
        # JSON output mode
        output = {
            "command": "validate",
            "version": __version__,
            "success": failed == 0,
            "data": {
                "total_personas": total,
                "passed": passed,
                "failed": failed,
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "average_score": round(avg_score, 1),
                "strict_mode": strict,
                "results": [r.to_dict() for r in results],
            },
        }
        print(json.dumps(output, indent=2))
        if failed > 0:
            raise typer.Exit(1)
        return

    # Rich output mode
    console.print(
        Panel.fit(
            f"[bold]Persona Validation[/bold]\n{persona_path}",
            border_style="blue",
        )
    )

    # Summary
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value")

    summary_table.add_row("Personas", str(total))
    summary_table.add_row(
        "Passed", f"[green]{passed}[/green]" if passed == total else str(passed)
    )
    summary_table.add_row(
        "Failed", f"[red]{failed}[/red]" if failed > 0 else str(failed)
    )
    summary_table.add_row(
        "Errors",
        f"[red]{total_errors}[/red]" if total_errors > 0 else str(total_errors),
    )
    summary_table.add_row(
        "Warnings",
        f"[yellow]{total_warnings}[/yellow]"
        if total_warnings > 0
        else str(total_warnings),
    )
    summary_table.add_row("Average score", f"{avg_score:.0f}/100")
    summary_table.add_row("Strict mode", "Yes" if strict else "No")

    console.print(summary_table)
    console.print()

    # Results table
    results_table = Table(title="Validation Results")
    results_table.add_column("Persona", style="cyan")
    results_table.add_column("Score", justify="right")
    results_table.add_column("Status")
    results_table.add_column("Issues")

    for result in results:
        # Find persona name
        persona_name = "Unknown"
        for p in personas:
            if p.id == result.persona_id:
                persona_name = p.name or p.id
                break

        # Status
        if result.is_valid:
            status = "[green]✓ Pass[/green]"
        else:
            status = "[red]✗ Fail[/red]"

        # Score colour
        if result.score >= 80:
            score_str = f"[green]{result.score}[/green]"
        elif result.score >= 60:
            score_str = f"[yellow]{result.score}[/yellow]"
        else:
            score_str = f"[red]{result.score}[/red]"

        # Issues summary
        issues_parts = []
        if result.errors:
            issues_parts.append(f"[red]{len(result.errors)} error(s)[/red]")
        if result.warnings:
            issues_parts.append(f"[yellow]{len(result.warnings)} warning(s)[/yellow]")
        issues_str = ", ".join(issues_parts) if issues_parts else "[green]None[/green]"

        results_table.add_row(
            persona_name[:30],
            score_str,
            status,
            issues_str,
        )

    console.print(results_table)

    # Show detailed issues for failed personas
    failed_results = [r for r in results if not r.is_valid or r.errors]
    if failed_results:
        console.print("\n[bold]Issues by Persona:[/bold]")

        for result in failed_results:
            persona_name = "Unknown"
            for p in personas:
                if p.id == result.persona_id:
                    persona_name = p.name or p.id
                    break

            console.print(f"\n[cyan]{persona_name}[/cyan] ({result.persona_id}):")

            for issue in result.issues:
                if issue.level == ValidationLevel.ERROR:
                    console.print(f"  [red]✗[/red] {issue.message}")
                elif issue.level == ValidationLevel.WARNING:
                    console.print(f"  [yellow]⚠[/yellow] {issue.message}")
                else:
                    console.print(f"  [blue]ℹ[/blue] {issue.message}")

    # Final status
    if failed > 0:
        console.print(
            f"\n[red]Validation failed: {failed} persona(s) have issues.[/red]"
        )
        raise typer.Exit(1)
    elif total_warnings > 0:
        console.print(
            f"\n[yellow]Validation passed with {total_warnings} warning(s).[/yellow]"
        )
    else:
        console.print("\n[green]All personas passed validation.[/green]")


def _load_personas(path: Path):
    """Load personas from a file or directory."""
    from persona.core.generation.parser import Persona

    if path.is_file():
        # Load from JSON file
        with open(path) as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, list):
            return [Persona.from_dict(p) for p in data]
        elif isinstance(data, dict):
            if "personas" in data:
                return [Persona.from_dict(p) for p in data["personas"]]
            else:
                return [Persona.from_dict(data)]
    else:
        # Load from output directory
        personas = []

        # Look for personas.json
        personas_file = path / "personas.json"
        if personas_file.exists():
            with open(personas_file) as f:
                data = json.load(f)
            if isinstance(data, list):
                return [Persona.from_dict(p) for p in data]
            elif "personas" in data:
                return [Persona.from_dict(p) for p in data["personas"]]

        # Look for individual persona files
        for json_file in path.glob("persona_*.json"):
            with open(json_file) as f:
                data = json.load(f)
            personas.append(Persona.from_dict(data))

        return personas
