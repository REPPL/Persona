"""
Lexical diversity analysis command for personas.

Provides comprehensive lexical diversity metrics including TTR, MATTR, MTLD,
and Hapax Ratio to assess vocabulary richness.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.generation.parser import Persona
from persona.core.quality.diversity import (
    DiversityConfig,
    InterpretationLevel,
    LexicalDiversityAnalyser,
)
from persona.ui.console import get_console

diversity_app = typer.Typer(
    name="diversity",
    help="Analyse lexical diversity of generated personas.",
)


@diversity_app.command(name="analyse")
def diversity(
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
            "--format", "-f",
            help="Output format: rich, json, table.",
        ),
    ] = "rich",
    save_to: Annotated[
        Optional[Path],
        typer.Option(
            "--save",
            help="Save report to file.",
        ),
    ] = None,
    window_size: Annotated[
        int,
        typer.Option(
            "--window-size",
            help="Window size for MATTR calculation.",
        ),
    ] = 50,
    min_tokens: Annotated[
        int,
        typer.Option(
            "--min-tokens",
            help="Minimum tokens required for reliable analysis.",
        ),
    ] = 50,
) -> None:
    """
    Analyse lexical diversity of personas.

    Calculates comprehensive lexical diversity metrics:
    - TTR (Type-Token Ratio): Basic unique word ratio
    - MATTR (Moving-Average TTR): Window-based stability measure
    - MTLD (Measure of Textual Lexical Diversity): Factor-based richness
    - Hapax Ratio: Proportion of words appearing exactly once

    Example:
        persona diversity analyse ./outputs/20250101_120000/
        persona diversity analyse ./personas.json --format json
        persona diversity analyse ./outputs/ --save diversity_report.json
    """
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
            console.print("[yellow]No personas found to analyse.[/yellow]")
        raise typer.Exit(1)

    # Configure analyser
    config = DiversityConfig(
        mattr_window_size=window_size,
        min_tokens=min_tokens,
    )

    # Analyse personas
    analyser = LexicalDiversityAnalyser(config=config)
    result = analyser.analyse_batch(personas)

    # Output results
    if output_format == "json":
        output = {
            "command": "diversity",
            "version": __version__,
            "success": True,
            "data": result.to_dict(),
        }
        output_text = json.dumps(output, indent=2)
        print(output_text)
        if save_to:
            save_to.write_text(output_text)
    elif output_format == "table":
        _display_table_output(console, result)
        if save_to:
            # Save JSON for table output
            save_to.write_text(json.dumps(result.to_dict(), indent=2))
    else:
        if not console.is_quiet:
            console.print(f"[dim]Persona {__version__}[/dim]\n")
        _display_rich_output(console, result)
        if save_to:
            # Save JSON for rich output
            save_to.write_text(json.dumps(result.to_dict(), indent=2))


def _display_rich_output(console, result) -> None:
    """Display results with Rich formatting."""
    console.print(Panel.fit(
        "[bold]Lexical Diversity Analysis[/bold]",
        border_style="blue",
    ))

    # Summary table
    summary = Table(show_header=False, box=None)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")
    summary.add_row("Personas analysed", str(len(result.reports)))
    summary.add_row("Average TTR", f"{result.average_ttr:.4f}")
    summary.add_row("Average MATTR", f"{result.average_mattr:.4f}")
    summary.add_row(
        "Average MTLD",
        _colour_mtld(result.average_mtld)
    )
    summary.add_row("Average Hapax Ratio", f"{result.average_hapax_ratio:.4f}")
    console.print(summary)
    console.print()

    # Distribution by interpretation
    console.print("[bold]Distribution by Interpretation Level:[/bold]")
    for level in InterpretationLevel:
        count = len(result.get_by_interpretation(level))
        if count > 0:
            level_name = level.value.replace("_", " ").title()
            bar_width = count * 2
            bar = "█" * min(bar_width, 40)
            console.print(f"  {level_name:15} {bar} ({count})")
    console.print()

    # Individual reports table
    reports_table = Table(title="Individual Diversity Scores")
    reports_table.add_column("Persona", style="cyan")
    reports_table.add_column("Tokens", justify="right")
    reports_table.add_column("Unique", justify="right")
    reports_table.add_column("TTR", justify="right")
    reports_table.add_column("MATTR", justify="right")
    reports_table.add_column("MTLD", justify="right")
    reports_table.add_column("Hapax", justify="right")
    reports_table.add_column("Level")

    for report in result.reports:
        level_colours = {
            InterpretationLevel.EXCELLENT: "green",
            InterpretationLevel.GOOD: "green",
            InterpretationLevel.AVERAGE: "yellow",
            InterpretationLevel.BELOW_AVERAGE: "red",
            InterpretationLevel.POOR: "red",
        }
        colour = level_colours.get(report.interpretation, "white")

        reports_table.add_row(
            report.persona_name[:30] if report.persona_name else report.persona_id[:30],
            str(report.total_tokens),
            str(report.unique_tokens),
            f"{report.ttr:.4f}",
            f"{report.mattr:.4f}",
            f"[{colour}]{report.mtld:.2f}[/{colour}]",
            f"{report.hapax_ratio:.4f}",
            f"[{colour}]{report.interpretation.value}[/{colour}]",
        )

    console.print(reports_table)

    # Show top tokens for low-diversity personas
    low_diversity = [
        r for r in result.reports
        if r.interpretation in (InterpretationLevel.POOR, InterpretationLevel.BELOW_AVERAGE)
    ]
    if low_diversity:
        console.print("\n[bold]Low Diversity Personas - Top Tokens:[/bold]")
        for report in low_diversity[:3]:  # Show up to 3
            name = report.persona_name or report.persona_id
            console.print(f"\n[cyan]{name}[/cyan] (MTLD: {report.mtld:.2f}):")
            top_tokens = sorted(
                report.token_frequency.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:10]
            for token, count in top_tokens:
                console.print(f"  {token}: {count}")


def _display_table_output(console, result) -> None:
    """Display results in simple table format."""
    # Summary
    console.print("SUMMARY")
    console.print(f"Personas: {len(result.reports)}")
    console.print(f"Avg TTR: {result.average_ttr:.4f}")
    console.print(f"Avg MATTR: {result.average_mattr:.4f}")
    console.print(f"Avg MTLD: {result.average_mtld:.2f}")
    console.print(f"Avg Hapax: {result.average_hapax_ratio:.4f}")
    console.print()

    # Individual scores
    console.print("INDIVIDUAL SCORES")
    console.print(
        f"{'Persona':<30} {'Tokens':>8} {'Unique':>8} {'TTR':>8} "
        f"{'MATTR':>8} {'MTLD':>8} {'Hapax':>8} {'Level':<15}"
    )
    console.print("-" * 120)

    for report in result.reports:
        name = report.persona_name[:28] if report.persona_name else report.persona_id[:28]
        console.print(
            f"{name:<30} {report.total_tokens:>8} {report.unique_tokens:>8} "
            f"{report.ttr:>8.4f} {report.mattr:>8.4f} {report.mtld:>8.2f} "
            f"{report.hapax_ratio:>8.4f} {report.interpretation.value:<15}"
        )


def _colour_mtld(mtld: float) -> str:
    """Return MTLD score with appropriate colour markup."""
    if mtld >= 100:
        return f"[green]{mtld:.2f}[/green]"
    elif mtld >= 70:
        return f"[green]{mtld:.2f}[/green]"
    elif mtld >= 50:
        return f"[yellow]{mtld:.2f}[/yellow]"
    else:
        return f"[red]{mtld:.2f}[/red]"


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
