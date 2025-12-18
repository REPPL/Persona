"""
Compare command for analysing persona similarities and differences.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.comparison import PersonaComparator
from persona.ui.console import get_console

compare_app = typer.Typer(
    name="compare",
    help="Compare personas to identify similarities and differences.",
)


@compare_app.callback(invoke_without_command=True)
def compare(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file or output directory.",
            exists=True,
        ),
    ],
    persona_id_a: Annotated[
        Optional[str],
        typer.Option(
            "--persona-a",
            "-a",
            help="ID of first persona to compare (compares all if not specified).",
        ),
    ] = None,
    persona_id_b: Annotated[
        Optional[str],
        typer.Option(
            "--persona-b",
            "-b",
            help="ID of second persona to compare.",
        ),
    ] = None,
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            "-t",
            help="Similarity threshold for duplicate detection (0-100).",
        ),
    ] = 70.0,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    Compare personas to identify similarities and differences.

    Can compare two specific personas or find similar pairs across
    all personas in a collection.

    Example:
        persona compare ./outputs/20250101_120000/
        persona compare ./personas.json --persona-a id1 --persona-b id2
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
                        "command": "compare",
                        "success": False,
                        "error": str(e),
                    },
                    indent=2,
                )
            )
        else:
            console.print(f"[red]Error loading personas:[/red] {e}")
        raise typer.Exit(1)

    if len(personas) < 2:
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "compare",
                        "success": False,
                        "error": "Need at least 2 personas to compare",
                    },
                    indent=2,
                )
            )
        else:
            console.print("[yellow]Need at least 2 personas to compare.[/yellow]")
        raise typer.Exit(1)

    comparator = PersonaComparator()

    # Specific comparison or all pairs
    if persona_id_a and persona_id_b:
        # Compare two specific personas
        persona_a = next((p for p in personas if p.id == persona_id_a), None)
        persona_b = next((p for p in personas if p.id == persona_id_b), None)

        if not persona_a:
            msg = f"Persona not found: {persona_id_a}"
            if json_output:
                print(
                    json.dumps(
                        {"command": "compare", "success": False, "error": msg}, indent=2
                    )
                )
            else:
                console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)

        if not persona_b:
            msg = f"Persona not found: {persona_id_b}"
            if json_output:
                print(
                    json.dumps(
                        {"command": "compare", "success": False, "error": msg}, indent=2
                    )
                )
            else:
                console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)

        result = comparator.compare(persona_a, persona_b)

        if json_output:
            print(
                json.dumps(
                    {
                        "command": "compare",
                        "version": __version__,
                        "success": True,
                        "data": result.to_dict(),
                    },
                    indent=2,
                )
            )
            return

        # Rich output for single comparison
        _display_single_comparison(console, persona_a, persona_b, result)

    else:
        # Compare all pairs
        results = comparator.compare_all(personas)

        # Find duplicates
        duplicates = [r for r in results if r.similarity.overall >= threshold]

        if json_output:
            print(
                json.dumps(
                    {
                        "command": "compare",
                        "version": __version__,
                        "success": True,
                        "data": {
                            "total_personas": len(personas),
                            "comparisons": len(results),
                            "threshold": threshold,
                            "similar_pairs": len(duplicates),
                            "comparisons_data": [r.to_dict() for r in results],
                        },
                    },
                    indent=2,
                )
            )
            return

        # Rich output for all comparisons
        _display_all_comparisons(console, personas, results, duplicates, threshold)


def _display_single_comparison(console, persona_a, persona_b, result) -> None:
    """Display comparison between two personas."""
    console.print(
        Panel.fit(
            f"[bold]Persona Comparison[/bold]\n"
            f"{persona_a.name} vs {persona_b.name}",
            border_style="blue",
        )
    )

    # Similarity scores
    sim = result.similarity
    console.print("\n[bold]Similarity Scores:[/bold]")

    scores_table = Table(show_header=False, box=None)
    scores_table.add_column("Dimension", style="cyan")
    scores_table.add_column("Score", justify="right")

    scores_table.add_row("Overall", _format_score(sim.overall))
    scores_table.add_row("Goals", _format_score(sim.goals))
    scores_table.add_row("Pain points", _format_score(sim.pain_points))
    scores_table.add_row("Demographics", _format_score(sim.demographics))
    scores_table.add_row("Behaviours", _format_score(sim.behaviours))

    console.print(scores_table)

    # Shared goals
    if result.shared_goals:
        console.print("\n[bold]Shared Goals:[/bold]")
        for goal in result.shared_goals:
            console.print(f"  [green]•[/green] {goal}")

    # Unique goals
    if result.unique_goals_a or result.unique_goals_b:
        console.print("\n[bold]Unique Goals:[/bold]")
        if result.unique_goals_a:
            console.print(f"\n  [cyan]{persona_a.name}:[/cyan]")
            for goal in result.unique_goals_a:
                console.print(f"    • {goal}")
        if result.unique_goals_b:
            console.print(f"\n  [cyan]{persona_b.name}:[/cyan]")
            for goal in result.unique_goals_b:
                console.print(f"    • {goal}")

    # Shared pain points
    if result.shared_pain_points:
        console.print("\n[bold]Shared Pain Points:[/bold]")
        for pain in result.shared_pain_points:
            console.print(f"  [green]•[/green] {pain}")

    # Demographic differences
    if result.demographic_differences:
        console.print("\n[bold]Demographic Differences:[/bold]")
        for diff in result.demographic_differences:
            console.print(
                f"  [cyan]{diff.field}:[/cyan] " f"{diff.persona_a} → {diff.persona_b}"
            )

    # Summary
    if result.is_similar:
        console.print(
            f"\n[yellow]These personas are similar ({sim.overall:.0f}%).[/yellow]"
        )
        console.print("Consider consolidating or differentiating them.")
    else:
        console.print(
            f"\n[green]These personas are distinct ({sim.overall:.0f}% similarity).[/green]"
        )


def _display_all_comparisons(console, personas, results, duplicates, threshold) -> None:
    """Display all pairwise comparisons."""
    console.print(
        Panel.fit(
            f"[bold]Persona Comparison[/bold]\n" f"Analysing {len(personas)} personas",
            border_style="blue",
        )
    )

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Total personas: {len(personas)}")
    console.print(f"  Comparisons: {len(results)}")
    console.print(f"  Similar pairs (>{threshold}%): {len(duplicates)}")

    # Similar pairs table
    if duplicates:
        console.print(f"\n[yellow]Similar Pairs (>{threshold}% similarity):[/yellow]")

        similar_table = Table()
        similar_table.add_column("Persona A", style="cyan")
        similar_table.add_column("Persona B", style="cyan")
        similar_table.add_column("Similarity", justify="right")
        similar_table.add_column("Relationship")

        for result in sorted(
            duplicates, key=lambda r: r.similarity.overall, reverse=True
        ):
            name_a = next(
                (p.name for p in personas if p.id == result.persona_a_id),
                result.persona_a_id,
            )
            name_b = next(
                (p.name for p in personas if p.id == result.persona_b_id),
                result.persona_b_id,
            )

            sim = result.similarity.overall
            if sim >= 90:
                relationship = "[red]Potential duplicate[/red]"
            elif sim >= 80:
                relationship = "[yellow]Very similar[/yellow]"
            else:
                relationship = "Similar"

            similar_table.add_row(
                name_a[:25],
                name_b[:25],
                _format_score(sim),
                relationship,
            )

        console.print(similar_table)

    # All comparisons (abbreviated)
    console.print("\n[bold]All Comparisons:[/bold]")

    all_table = Table()
    all_table.add_column("Persona A", style="cyan")
    all_table.add_column("Persona B", style="cyan")
    all_table.add_column("Overall", justify="right")
    all_table.add_column("Goals", justify="right")
    all_table.add_column("Pain Pts", justify="right")

    # Sort by similarity
    sorted_results = sorted(results, key=lambda r: r.similarity.overall, reverse=True)

    for result in sorted_results[:20]:  # Limit to top 20
        name_a = next(
            (p.name for p in personas if p.id == result.persona_a_id),
            result.persona_a_id,
        )
        name_b = next(
            (p.name for p in personas if p.id == result.persona_b_id),
            result.persona_b_id,
        )

        all_table.add_row(
            name_a[:20],
            name_b[:20],
            _format_score(result.similarity.overall),
            _format_score(result.similarity.goals),
            _format_score(result.similarity.pain_points),
        )

    console.print(all_table)

    if len(results) > 20:
        console.print(f"[dim]... and {len(results) - 20} more comparisons[/dim]")

    # Recommendations
    if duplicates:
        console.print(
            f"\n[yellow]Recommendation:[/yellow] Review {len(duplicates)} similar pair(s) for potential consolidation."
        )
    else:
        console.print("\n[green]All personas appear distinct.[/green]")


def _format_score(score: float) -> str:
    """Format a similarity score with colour."""
    if score >= 80:
        return f"[red]{score:.0f}%[/red]"
    elif score >= 60:
        return f"[yellow]{score:.0f}%[/yellow]"
    else:
        return f"[green]{score:.0f}%[/green]"


def _load_personas(path: Path):
    """Load personas from a file or directory."""
    from persona.core.generation.parser import Persona

    if path.is_file():
        with open(path) as f:
            data = json.load(f)

        if isinstance(data, list):
            return [Persona.from_dict(p) for p in data]
        elif isinstance(data, dict):
            if "personas" in data:
                return [Persona.from_dict(p) for p in data["personas"]]
            else:
                return [Persona.from_dict(data)]
    else:
        personas = []

        personas_file = path / "personas.json"
        if personas_file.exists():
            with open(personas_file) as f:
                data = json.load(f)
            if isinstance(data, list):
                return [Persona.from_dict(p) for p in data]
            elif "personas" in data:
                return [Persona.from_dict(p) for p in data["personas"]]

        for json_file in path.glob("persona_*.json"):
            with open(json_file) as f:
                data = json.load(f)
            personas.append(Persona.from_dict(data))

        return personas
