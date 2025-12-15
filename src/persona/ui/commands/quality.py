"""
Quality scoring command for personas.

Provides comprehensive quality assessment across multiple dimensions.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.generation.parser import Persona
from persona.core.quality import QualityScorer, QualityConfig, QualityLevel
from persona.ui.console import get_console

quality_app = typer.Typer(
    name="score",
    help="Calculate quality scores for generated personas.",
)


@quality_app.callback(invoke_without_command=True)
def score(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file or output directory.",
            exists=True,
        ),
    ],
    output_format: Annotated[
        str,
        typer.Option(
            "--output", "-o",
            help="Output format: rich, json, markdown.",
        ),
    ] = "rich",
    save_to: Annotated[
        Optional[Path],
        typer.Option(
            "--save",
            help="Save report to file.",
        ),
    ] = None,
    minimum_score: Annotated[
        Optional[int],
        typer.Option(
            "--min-score",
            help="Exit with error if any score below this threshold.",
        ),
    ] = None,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            help="Use strict thresholds (higher quality requirements).",
        ),
    ] = False,
    lenient: Annotated[
        bool,
        typer.Option(
            "--lenient",
            help="Use lenient thresholds (lower quality requirements).",
        ),
    ] = False,
) -> None:
    """
    Calculate quality scores for personas.

    Evaluates personas across five dimensions:
    - Completeness: Field population and depth
    - Consistency: Internal coherence
    - Evidence Strength: Link to source data
    - Distinctiveness: Uniqueness vs other personas
    - Realism: Plausibility as a real person

    Example:
        persona score ./outputs/20250101_120000/
        persona score ./personas.json --min-score 70
        persona score ./outputs/ --output json --save report.json
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    from persona import __version__

    # Load personas
    try:
        personas = _load_personas(persona_path)
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error loading personas:[/red] {e}")
        raise typer.Exit(1)

    if not personas:
        if output_format == "json":
            print(json.dumps({"success": False, "error": "No personas found"}, indent=2))
        else:
            console.print("[yellow]No personas found to score.[/yellow]")
        raise typer.Exit(1)

    # Select configuration
    if strict and lenient:
        console.print("[red]Cannot use both --strict and --lenient[/red]")
        raise typer.Exit(1)
    elif strict:
        config = QualityConfig.strict()
    elif lenient:
        config = QualityConfig.lenient()
    else:
        config = QualityConfig()

    # Score personas
    scorer = QualityScorer(config=config)
    result = scorer.score_batch(personas)

    # Output results
    if output_format == "json":
        output = {
            "command": "score",
            "version": __version__,
            "success": True,
            "data": result.to_dict(),
        }
        output_text = json.dumps(output, indent=2)
        print(output_text)
        if save_to:
            save_to.write_text(output_text)
    elif output_format == "markdown":
        report = _generate_markdown_report(result, personas)
        print(report)
        if save_to:
            save_to.write_text(report)
    else:
        if not console._quiet:
            console.print(f"[dim]Persona {__version__}[/dim]\n")
        _display_rich_output(console, result, personas)
        if save_to:
            # Save JSON for rich output
            save_to.write_text(json.dumps(result.to_dict(), indent=2))

    # Check minimum score threshold
    if minimum_score is not None:
        failing = [s for s in result.scores if s.overall_score < minimum_score]
        if failing:
            if output_format != "json":
                console.print(
                    f"\n[red]Error:[/red] {len(failing)} persona(s) "
                    f"below minimum score of {minimum_score}"
                )
            raise typer.Exit(1)


def _display_rich_output(console, result, personas) -> None:
    """Display results with Rich formatting."""
    console.print(Panel.fit(
        "[bold]Persona Quality Scores[/bold]",
        border_style="blue",
    ))

    # Summary table
    summary = Table(show_header=False, box=None)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")
    summary.add_row("Personas scored", str(len(result.scores)))
    summary.add_row(
        "Average score",
        _colour_score(result.average_score)
    )
    summary.add_row("Passing", f"[green]{result.passing_count}[/green]")
    summary.add_row(
        "Failing",
        f"[red]{result.failing_count}[/red]" if result.failing_count > 0 else "0"
    )
    console.print(summary)
    console.print()

    # Dimension averages
    console.print("[bold]Average by Dimension:[/bold]")
    for dim, avg in result.average_by_dimension.items():
        bar_width = int(avg / 5)  # 0-20 chars
        bar = "[green]" + "█" * bar_width + "[/green]" + "░" * (20 - bar_width)
        dim_display = dim.replace("_", " ").title()
        console.print(f"  {dim_display:20} {bar} {avg:.1f}")
    console.print()

    # Individual scores table
    scores_table = Table(title="Individual Scores")
    scores_table.add_column("Persona", style="cyan")
    scores_table.add_column("Overall", justify="right")
    scores_table.add_column("Level")
    scores_table.add_column("Comp", justify="right")
    scores_table.add_column("Cons", justify="right")
    scores_table.add_column("Evid", justify="right")
    scores_table.add_column("Dist", justify="right")
    scores_table.add_column("Real", justify="right")

    for score in result.scores:
        level_colours = {
            QualityLevel.EXCELLENT: "green",
            QualityLevel.GOOD: "green",
            QualityLevel.ACCEPTABLE: "yellow",
            QualityLevel.POOR: "red",
            QualityLevel.FAILING: "red",
        }
        colour = level_colours.get(score.level, "white")

        scores_table.add_row(
            score.persona_name[:25] if score.persona_name else score.persona_id[:25],
            f"[{colour}]{score.overall_score:.0f}[/{colour}]",
            f"[{colour}]{score.level.value}[/{colour}]",
            f"{score.dimensions['completeness'].score:.0f}",
            f"{score.dimensions['consistency'].score:.0f}",
            f"{score.dimensions['evidence_strength'].score:.0f}",
            f"{score.dimensions['distinctiveness'].score:.0f}",
            f"{score.dimensions['realism'].score:.0f}",
        )

    console.print(scores_table)

    # Show issues for low-scoring personas
    low_scores = [s for s in result.scores if s.overall_score < 70]
    if low_scores:
        console.print("\n[bold]Issues for Low-Scoring Personas:[/bold]")
        for score in low_scores:
            name = score.persona_name or score.persona_id
            console.print(f"\n[cyan]{name}[/cyan] ({score.overall_score:.0f}):")
            for dim_name, dim in score.dimensions.items():
                if dim.issues:
                    dim_display = dim_name.replace("_", " ").title()
                    for issue in dim.issues[:3]:  # Limit to 3 issues per dimension
                        console.print(f"  [yellow]•[/yellow] [{dim_display}] {issue}")


def _generate_markdown_report(result, personas) -> str:
    """Generate a Markdown report."""
    lines = [
        "# Persona Quality Report",
        "",
        "## Summary",
        "",
        f"- **Personas scored:** {len(result.scores)}",
        f"- **Average score:** {result.average_score:.1f}/100",
        f"- **Passing:** {result.passing_count}",
        f"- **Failing:** {result.failing_count}",
        "",
        "## Average by Dimension",
        "",
        "| Dimension | Score |",
        "|-----------|-------|",
    ]

    for dim, avg in result.average_by_dimension.items():
        dim_display = dim.replace("_", " ").title()
        lines.append(f"| {dim_display} | {avg:.1f} |")

    lines.extend([
        "",
        "## Individual Scores",
        "",
        "| Persona | Overall | Level | Comp | Cons | Evid | Dist | Real |",
        "|---------|---------|-------|------|------|------|------|------|",
    ])

    for score in result.scores:
        name = score.persona_name or score.persona_id
        lines.append(
            f"| {name[:20]} | {score.overall_score:.0f} | {score.level.value} | "
            f"{score.dimensions['completeness'].score:.0f} | "
            f"{score.dimensions['consistency'].score:.0f} | "
            f"{score.dimensions['evidence_strength'].score:.0f} | "
            f"{score.dimensions['distinctiveness'].score:.0f} | "
            f"{score.dimensions['realism'].score:.0f} |"
        )

    # Issues section
    low_scores = [s for s in result.scores if s.overall_score < 70]
    if low_scores:
        lines.extend([
            "",
            "## Issues",
            "",
        ])
        for score in low_scores:
            name = score.persona_name or score.persona_id
            lines.append(f"### {name} ({score.overall_score:.0f})")
            lines.append("")
            for dim_name, dim in score.dimensions.items():
                if dim.issues:
                    dim_display = dim_name.replace("_", " ").title()
                    for issue in dim.issues:
                        lines.append(f"- **{dim_display}:** {issue}")
            lines.append("")

    return "\n".join(lines)


def _colour_score(score: float) -> str:
    """Return score with appropriate colour markup."""
    if score >= 90:
        return f"[green]{score:.1f}/100[/green]"
    elif score >= 75:
        return f"[green]{score:.1f}/100[/green]"
    elif score >= 60:
        return f"[yellow]{score:.1f}/100[/yellow]"
    else:
        return f"[red]{score:.1f}/100[/red]"


def _load_personas(path: Path) -> list[Persona]:
    """Load personas from a file or directory."""
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

    return []
