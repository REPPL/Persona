"""
Lexical diversity analysis command for personas.

Provides comprehensive lexical diversity metrics including TTR, MATTR, MTLD,
and Hapax Ratio to assess vocabulary richness.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.table import Table

from persona.core.quality.diversity import (
    DiversityConfig,
    InterpretationLevel,
    LexicalDiversityAnalyser,
)
from persona.ui.commands.quality_base import (
    QualityOutputFormatter,
    colour_score,
    create_panel,
    create_summary_table,
    display_version_header,
    handle_error,
    load_personas,
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
            "--format",
            "-f",
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
    formatter = QualityOutputFormatter(console, output_format, save_to)

    # Load personas
    try:
        personas = load_personas(persona_path)
    except Exception as e:
        handle_error(console, "Error loading personas", output_format, e)

    if not personas:
        handle_error(console, "Error", output_format, "No personas found to analyse")

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
        formatter.output_json(result.to_dict(), "diversity")
    elif output_format == "table":
        _display_table_output(console, result)
        formatter.save_data(result.to_dict())
    else:
        display_version_header(console, console.is_quiet)
        _display_rich_output(console, result)
        formatter.save_data(result.to_dict())


def _display_rich_output(console, result) -> None:
    """Display results with Rich formatting."""
    console.print(create_panel("[bold]Lexical Diversity Analysis[/bold]", border_style="blue"))

    # Summary table
    summary = create_summary_table([
        ("Personas analysed", str(len(result.reports))),
        ("Average TTR", f"{result.average_ttr:.4f}"),
        ("Average MATTR", f"{result.average_mattr:.4f}"),
        ("Average MTLD", _colour_mtld(result.average_mtld)),
        ("Average Hapax Ratio", f"{result.average_hapax_ratio:.4f}"),
    ])
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
        r
        for r in result.reports
        if r.interpretation
        in (InterpretationLevel.POOR, InterpretationLevel.BELOW_AVERAGE)
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
        name = (
            report.persona_name[:28] if report.persona_name else report.persona_id[:28]
        )
        console.print(
            f"{name:<30} {report.total_tokens:>8} {report.unique_tokens:>8} "
            f"{report.ttr:>8.4f} {report.mattr:>8.4f} {report.mtld:>8.2f} "
            f"{report.hapax_ratio:>8.4f} {report.interpretation.value:<15}"
        )


def _colour_mtld(mtld: float) -> str:
    """Return MTLD score with appropriate colour markup."""
    if mtld >= 70:
        return f"[green]{mtld:.2f}[/green]"
    elif mtld >= 50:
        return f"[yellow]{mtld:.2f}[/yellow]"
    else:
        return f"[red]{mtld:.2f}[/red]"
