"""
Academic validation command for personas.

Provides research-grade validation using ROUGE-L, BERTScore,
GPT embedding similarity, and G-eval metrics.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.generation.parser import Persona
from persona.ui.console import get_console

academic_app = typer.Typer(
    name="academic",
    help="Validate personas using academic research metrics.",
)


@academic_app.callback(invoke_without_command=True)
def academic(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file or output directory.",
            exists=True,
        ),
    ],
    source_path: Annotated[
        Optional[Path],
        typer.Option(
            "--source", "-s",
            help="Path to source data file for comparison.",
            exists=True,
        ),
    ] = None,
    rouge: Annotated[
        bool,
        typer.Option(
            "--rouge",
            help="Compute ROUGE-L scores (surface text overlap).",
        ),
    ] = False,
    bertscore: Annotated[
        bool,
        typer.Option(
            "--bertscore",
            help="Compute BERTScore (contextual embedding similarity).",
        ),
    ] = False,
    gpt_similarity: Annotated[
        bool,
        typer.Option(
            "--gpt-similarity",
            help="Compute GPT embedding similarity.",
        ),
    ] = False,
    geval: Annotated[
        bool,
        typer.Option(
            "--geval",
            help="Compute G-eval scores (LLM-based assessment).",
        ),
    ] = False,
    all_metrics: Annotated[
        bool,
        typer.Option(
            "--all",
            help="Compute all available metrics.",
        ),
    ] = False,
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
        Optional[float],
        typer.Option(
            "--min-score",
            help="Exit with error if overall score below threshold (0-1).",
        ),
    ] = None,
    geval_provider: Annotated[
        str,
        typer.Option(
            "--geval-provider",
            help="LLM provider for G-eval (anthropic, openai, ollama).",
        ),
    ] = "ollama",
    embedding_provider: Annotated[
        str,
        typer.Option(
            "--embedding-provider",
            help="Embedding provider for GPT similarity (openai).",
        ),
    ] = "openai",
) -> None:
    """
    Validate personas using academic research metrics.

    Provides research-grade validation for persona quality assessment:
    - ROUGE-L: Surface-level text similarity (lexical overlap)
    - BERTScore: Semantic similarity using contextual embeddings
    - GPT Similarity: High-level semantic similarity using embeddings
    - G-eval: LLM-based multi-dimensional quality assessment

    Example:
        persona academic ./personas.json --source ./data.txt --all
        persona academic ./output/ --rouge --bertscore --min-score 0.6
        persona academic ./personas.json --geval --geval-provider anthropic
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    from persona import __version__
    from persona.core.quality.academic import AcademicValidator

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
            console.print("[yellow]No personas found to validate.[/yellow]")
        raise typer.Exit(1)

    # Load source data if provided
    source_data = None
    if source_path:
        try:
            source_data = source_path.read_text(encoding="utf-8")
        except Exception as e:
            if output_format == "json":
                print(json.dumps({"success": False, "error": f"Failed to load source: {e}"}, indent=2))
            else:
                console.print(f"[red]Error loading source data:[/red] {e}")
            raise typer.Exit(1)

    # Determine which metrics to compute
    metrics = []
    if all_metrics:
        metrics = ["rouge_l", "bertscore", "gpt_similarity", "geval"]
    else:
        if rouge:
            metrics.append("rouge_l")
        if bertscore:
            metrics.append("bertscore")
        if gpt_similarity:
            metrics.append("gpt_similarity")
        if geval:
            metrics.append("geval")

    # Default to G-eval only if no metrics specified
    if not metrics:
        metrics = ["geval"]
        if output_format == "rich" and not console._quiet:
            console.print("[dim]No metrics specified, defaulting to G-eval[/dim]")

    # Check source requirement
    requires_source = {"rouge_l", "bertscore", "gpt_similarity"}
    if requires_source & set(metrics) and not source_data:
        msg = f"Metrics {requires_source & set(metrics)} require --source data file"
        if output_format == "json":
            print(json.dumps({"success": False, "error": msg}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {msg}")
        raise typer.Exit(1)

    # Create validator
    try:
        validator = AcademicValidator(
            geval_provider=geval_provider,
            embedding_provider=embedding_provider,
        )
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": f"Failed to initialise validator: {e}"}, indent=2))
        else:
            console.print(f"[red]Error initialising validator:[/red] {e}")
        raise typer.Exit(1)

    # Validate personas
    try:
        result = validator.validate_batch(personas, source_data, metrics)
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Validation error:[/red] {e}")
        raise typer.Exit(1)

    # Output results
    if output_format == "json":
        output = {
            "command": "academic",
            "version": __version__,
            "success": True,
            "data": {
                "metrics_used": metrics,
                "persona_count": len(result.reports),
                "averages": {
                    "rouge_l": result.average_rouge_l,
                    "bertscore": result.average_bertscore,
                    "gpt_similarity": result.average_gpt_similarity,
                    "geval": result.average_geval,
                    "overall": result.overall_average,
                },
                "reports": [_report_to_dict(r) for r in result.reports],
            },
        }
        output_text = json.dumps(output, indent=2)
        print(output_text)
        if save_to:
            save_to.write_text(output_text)
    elif output_format == "markdown":
        report = _generate_markdown_report(result, metrics)
        print(report)
        if save_to:
            save_to.write_text(report)
    else:
        if not console._quiet:
            console.print(f"[dim]Persona {__version__}[/dim]\n")
        _display_rich_output(console, result, metrics)
        if save_to:
            save_to.write_text(json.dumps({
                "averages": {
                    "rouge_l": result.average_rouge_l,
                    "bertscore": result.average_bertscore,
                    "gpt_similarity": result.average_gpt_similarity,
                    "geval": result.average_geval,
                    "overall": result.overall_average,
                },
                "reports": [_report_to_dict(r) for r in result.reports],
            }, indent=2))

    # Check minimum score threshold
    if minimum_score is not None:
        if result.overall_average is not None and result.overall_average < minimum_score:
            if output_format != "json":
                console.print(
                    f"\n[red]Error:[/red] Overall score {result.overall_average:.2f} "
                    f"below minimum threshold {minimum_score}"
                )
            raise typer.Exit(1)


def _display_rich_output(console, result, metrics: list[str]) -> None:
    """Display results with Rich formatting."""
    console.print(Panel.fit(
        "[bold]Academic Validation Report[/bold]",
        border_style="blue",
    ))

    # Summary table
    summary = Table(show_header=False, box=None)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")
    summary.add_row("Personas validated", str(len(result.reports)))
    summary.add_row("Metrics used", ", ".join(metrics))

    if result.overall_average is not None:
        summary.add_row("Overall average", _colour_score(result.overall_average))

    console.print(summary)
    console.print()

    # Metric averages
    console.print("[bold]Average by Metric:[/bold]")

    if result.average_rouge_l is not None:
        _print_score_bar(console, "ROUGE-L", result.average_rouge_l)
    if result.average_bertscore is not None:
        _print_score_bar(console, "BERTScore", result.average_bertscore)
    if result.average_gpt_similarity is not None:
        _print_score_bar(console, "GPT Similarity", result.average_gpt_similarity)
    if result.average_geval is not None:
        _print_score_bar(console, "G-eval", result.average_geval)

    console.print()

    # Individual scores table
    scores_table = Table(title="Individual Scores")
    scores_table.add_column("Persona", style="cyan")

    if "rouge_l" in metrics:
        scores_table.add_column("ROUGE-L", justify="right")
    if "bertscore" in metrics:
        scores_table.add_column("BERT", justify="right")
    if "gpt_similarity" in metrics:
        scores_table.add_column("GPT-Sim", justify="right")
    if "geval" in metrics:
        scores_table.add_column("G-eval", justify="right")

    scores_table.add_column("Overall", justify="right")

    for report in result.reports:
        row = [report.persona_name or report.persona_id[:20]]

        if "rouge_l" in metrics:
            if report.rouge_l:
                row.append(f"{report.rouge_l.fmeasure:.3f}")
            else:
                row.append("-")

        if "bertscore" in metrics:
            if report.bertscore:
                row.append(f"{report.bertscore.f1:.3f}")
            else:
                row.append("-")

        if "gpt_similarity" in metrics:
            if report.gpt_similarity:
                row.append(f"{report.gpt_similarity.similarity:.3f}")
            else:
                row.append("-")

        if "geval" in metrics:
            if report.geval:
                row.append(f"{report.geval.overall:.3f}")
            else:
                row.append("-")

        row.append(_colour_score(report.overall_score) if report.overall_score else "-")
        scores_table.add_row(*row)

    console.print(scores_table)

    # Show G-eval details if available
    if "geval" in metrics:
        geval_reports = [r for r in result.reports if r.geval]
        if geval_reports:
            console.print("\n[bold]G-eval Dimension Details:[/bold]")
            geval_table = Table()
            geval_table.add_column("Persona", style="cyan")
            geval_table.add_column("Coherence", justify="right")
            geval_table.add_column("Relevance", justify="right")
            geval_table.add_column("Fluency", justify="right")
            geval_table.add_column("Consistency", justify="right")

            for report in geval_reports:
                if report.geval:
                    geval_table.add_row(
                        report.persona_name or report.persona_id[:20],
                        f"{report.geval.coherence:.2f}",
                        f"{report.geval.relevance:.2f}",
                        f"{report.geval.fluency:.2f}",
                        f"{report.geval.consistency:.2f}",
                    )

            console.print(geval_table)


def _print_score_bar(console, name: str, score: float) -> None:
    """Print a score with visual bar."""
    bar_width = int(score * 20)  # 0-20 chars for 0-1 score
    bar = "[green]" + "█" * bar_width + "[/green]" + "░" * (20 - bar_width)
    console.print(f"  {name:20} {bar} {score:.3f}")


def _generate_markdown_report(result, metrics: list[str]) -> str:
    """Generate a Markdown report."""
    lines = [
        "# Academic Validation Report",
        "",
        "## Summary",
        "",
        f"- **Personas validated:** {len(result.reports)}",
        f"- **Metrics used:** {', '.join(metrics)}",
    ]

    if result.overall_average is not None:
        lines.append(f"- **Overall average:** {result.overall_average:.3f}")

    lines.extend([
        "",
        "## Average by Metric",
        "",
        "| Metric | Score |",
        "|--------|-------|",
    ])

    if result.average_rouge_l is not None:
        lines.append(f"| ROUGE-L | {result.average_rouge_l:.3f} |")
    if result.average_bertscore is not None:
        lines.append(f"| BERTScore | {result.average_bertscore:.3f} |")
    if result.average_gpt_similarity is not None:
        lines.append(f"| GPT Similarity | {result.average_gpt_similarity:.3f} |")
    if result.average_geval is not None:
        lines.append(f"| G-eval | {result.average_geval:.3f} |")

    lines.extend([
        "",
        "## Individual Scores",
        "",
    ])

    # Build header
    header = "| Persona |"
    separator = "|---------|"
    if "rouge_l" in metrics:
        header += " ROUGE-L |"
        separator += "---------|"
    if "bertscore" in metrics:
        header += " BERT |"
        separator += "------|"
    if "gpt_similarity" in metrics:
        header += " GPT-Sim |"
        separator += "---------|"
    if "geval" in metrics:
        header += " G-eval |"
        separator += "--------|"
    header += " Overall |"
    separator += "---------|"

    lines.append(header)
    lines.append(separator)

    for report in result.reports:
        row = f"| {(report.persona_name or report.persona_id)[:20]} |"

        if "rouge_l" in metrics:
            row += f" {report.rouge_l.fmeasure:.3f} |" if report.rouge_l else " - |"
        if "bertscore" in metrics:
            row += f" {report.bertscore.f1:.3f} |" if report.bertscore else " - |"
        if "gpt_similarity" in metrics:
            row += f" {report.gpt_similarity.similarity:.3f} |" if report.gpt_similarity else " - |"
        if "geval" in metrics:
            row += f" {report.geval.overall:.3f} |" if report.geval else " - |"

        row += f" {report.overall_score:.3f} |" if report.overall_score else " - |"
        lines.append(row)

    return "\n".join(lines)


def _colour_score(score: float) -> str:
    """Return score with appropriate colour markup."""
    if score >= 0.8:
        return f"[green]{score:.3f}[/green]"
    elif score >= 0.6:
        return f"[yellow]{score:.3f}[/yellow]"
    else:
        return f"[red]{score:.3f}[/red]"


def _report_to_dict(report) -> dict:
    """Convert an AcademicValidationReport to a dictionary."""
    return {
        "persona_id": report.persona_id,
        "persona_name": report.persona_name,
        "overall_score": report.overall_score,
        "metrics_used": report.metrics_used,
        "rouge_l": {
            "precision": report.rouge_l.precision,
            "recall": report.rouge_l.recall,
            "fmeasure": report.rouge_l.fmeasure,
        } if report.rouge_l else None,
        "bertscore": {
            "precision": report.bertscore.precision,
            "recall": report.bertscore.recall,
            "f1": report.bertscore.f1,
            "model": report.bertscore.model,
        } if report.bertscore else None,
        "gpt_similarity": {
            "similarity": report.gpt_similarity.similarity,
            "embedding_model": report.gpt_similarity.embedding_model,
        } if report.gpt_similarity else None,
        "geval": {
            "coherence": report.geval.coherence,
            "relevance": report.geval.relevance,
            "fluency": report.geval.fluency,
            "consistency": report.geval.consistency,
            "overall": report.geval.overall,
            "model": report.geval.model,
            "reasoning": report.geval.reasoning,
        } if report.geval else None,
    }


def _load_personas(path: Path) -> list[Persona]:
    """Load personas from a file or directory."""
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

    return []
