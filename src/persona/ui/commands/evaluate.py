"""
LLM-based persona evaluation command.

Provides the 'persona evaluate' command for evaluating personas
using LLM judges.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.evaluation import (
    PersonaJudge,
    EvaluationCriteria,
    DEFAULT_CRITERIA,
)
from persona.ui.console import get_console

evaluate_app = typer.Typer(
    name="evaluate",
    help="Evaluate personas using LLM judges.",
)


@evaluate_app.callback(invoke_without_command=True)
def evaluate(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file.",
            exists=True,
        ),
    ],
    judge: Annotated[
        str,
        typer.Option(
            "--judge",
            "-j",
            help="Judge provider to use (ollama, anthropic, openai, gemini).",
        ),
    ] = "ollama",
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help="Model to use for evaluation (default: provider's default).",
        ),
    ] = None,
    criteria: Annotated[
        Optional[str],
        typer.Option(
            "--criteria",
            "-c",
            help="Comma-separated criteria (coherence,realism,usefulness,distinctiveness,completeness,specificity).",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            help="Show detailed reasoning for each criterion.",
        ),
    ] = False,
    output_format: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output format: rich, json.",
        ),
    ] = "rich",
    save_to: Annotated[
        Optional[Path],
        typer.Option(
            "--save",
            help="Save results to file.",
        ),
    ] = None,
) -> None:
    """
    Evaluate personas using LLM judges.

    Uses local or cloud LLMs to assess persona quality across
    multiple criteria including coherence, realism, usefulness,
    distinctiveness, completeness, and specificity.

    Example:
        persona evaluate personas.json --judge ollama
        persona evaluate personas.json --judge ollama --model qwen2.5:72b
        persona evaluate personas.json --judge ollama --criteria coherence,realism
        persona evaluate personas.json --judge ollama --verbose
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    from persona import __version__

    # Parse criteria
    selected_criteria = _parse_criteria(criteria) if criteria else DEFAULT_CRITERIA

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
            console.print("[yellow]No personas found to evaluate.[/yellow]")
        raise typer.Exit(1)

    # Create judge
    try:
        persona_judge = PersonaJudge(provider=judge, model=model)
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": f"Failed to create judge: {e}"}, indent=2))
        else:
            console.print(f"[red]Error creating judge:[/red] {e}")
        raise typer.Exit(1)

    # Evaluate
    try:
        if output_format != "json":
            console.print(f"[dim]Persona {__version__}[/dim]\n")
            console.print(f"[bold]Evaluating {len(personas)} persona(s)...[/bold]")
            console.print(f"[dim]Judge: {judge} ({persona_judge.model})[/dim]\n")

        # Check if we need batch evaluation
        requires_batch = any(c.requires_batch for c in selected_criteria)

        if requires_batch or len(personas) > 1:
            result = persona_judge.evaluate_batch(personas, selected_criteria)
        else:
            single_result = persona_judge.evaluate(personas[0], selected_criteria)
            # Convert to batch result for consistent output
            from persona.core.evaluation import BatchEvaluationResult

            average_by_criterion = {
                criterion: single_result.get_score(criterion)
                for criterion in selected_criteria
                if single_result.get_score(criterion) is not None
            }

            result = BatchEvaluationResult(
                results=[single_result],
                average_overall=single_result.overall_score,
                average_by_criterion=average_by_criterion,
                model=single_result.model,
                provider=single_result.provider,
            )

    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error during evaluation:[/red] {e}")
        raise typer.Exit(1)

    # Output results
    if output_format == "json":
        output = {
            "command": "evaluate",
            "version": __version__,
            "success": True,
            "data": result.to_dict(),
        }
        output_text = json.dumps(output, indent=2)
        print(output_text)
        if save_to:
            save_to.write_text(output_text)
    else:
        _display_rich_output(console, result, selected_criteria, verbose)
        if save_to:
            save_to.write_text(json.dumps(result.to_dict(), indent=2))


def _display_rich_output(
    console,
    result,
    criteria: list[EvaluationCriteria],
    verbose: bool,
) -> None:
    """Display results with Rich formatting."""
    console.print(Panel.fit(
        "[bold]LLM-Based Persona Evaluation[/bold]",
        border_style="blue",
    ))

    # Summary table
    summary = Table(show_header=False, box=None)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")
    summary.add_row("Personas evaluated", str(len(result.results)))
    summary.add_row("Average score", _colour_score(result.average_overall))
    summary.add_row("Model", f"{result.provider}/{result.model}")
    console.print(summary)
    console.print()

    # Criterion averages
    console.print("[bold]Average by Criterion:[/bold]")
    for criterion in criteria:
        avg = result.average_by_criterion.get(criterion, 0.0)
        bar_width = int(avg * 20)  # 0-20 chars
        bar = "[green]" + "█" * bar_width + "[/green]" + "░" * (20 - bar_width)
        criterion_display = criterion.value.replace("_", " ").title()
        console.print(f"  {criterion_display:20} {bar} {avg:.2f}")
    console.print()

    # Individual scores table
    scores_table = Table(title="Individual Scores")
    scores_table.add_column("Persona", style="cyan")
    scores_table.add_column("Overall", justify="right")

    # Add column for each criterion
    for criterion in criteria:
        short_name = criterion.value[:4].title()
        scores_table.add_column(short_name, justify="right")

    for eval_result in result.results:
        name = eval_result.persona_name or eval_result.persona_id
        overall_colour = _get_score_colour(eval_result.overall_score)

        row = [
            name[:30] if name else eval_result.persona_id[:30],
            f"[{overall_colour}]{eval_result.overall_score:.2f}[/{overall_colour}]",
        ]

        for criterion in criteria:
            score = eval_result.get_score(criterion)
            if score is not None:
                colour = _get_score_colour(score)
                row.append(f"[{colour}]{score:.2f}[/{colour}]")
            else:
                row.append("-")

        scores_table.add_row(*row)

    console.print(scores_table)

    # Show detailed reasoning if verbose
    if verbose:
        console.print("\n[bold]Detailed Reasoning:[/bold]\n")
        for eval_result in result.results:
            name = eval_result.persona_name or eval_result.persona_id
            console.print(f"[bold cyan]{name}[/bold cyan] (Overall: {eval_result.overall_score:.2f})")
            console.print()

            for criterion in criteria:
                reasoning = eval_result.get_reasoning(criterion)
                score = eval_result.get_score(criterion)
                if reasoning and score is not None:
                    colour = _get_score_colour(score)
                    criterion_display = criterion.value.replace("_", " ").title()
                    console.print(f"  [bold]{criterion_display}:[/bold] [{colour}]{score:.2f}[/{colour}]")
                    console.print(f"  {reasoning}")
                    console.print()


def _colour_score(score: float) -> str:
    """Return score with appropriate colour markup."""
    colour = _get_score_colour(score)
    return f"[{colour}]{score:.2f}[/{colour}]"


def _get_score_colour(score: float) -> str:
    """Get colour for a score."""
    if score >= 0.9:
        return "green"
    elif score >= 0.7:
        return "green"
    elif score >= 0.5:
        return "yellow"
    elif score >= 0.3:
        return "red"
    else:
        return "red"


def _parse_criteria(criteria_str: str) -> list[EvaluationCriteria]:
    """
    Parse comma-separated criteria string.

    Args:
        criteria_str: Comma-separated criteria names.

    Returns:
        List of EvaluationCriteria.

    Raises:
        ValueError: If any criterion is invalid.
    """
    criteria_names = [c.strip().lower() for c in criteria_str.split(",")]
    parsed = []

    for name in criteria_names:
        try:
            criterion = EvaluationCriteria(name)
            parsed.append(criterion)
        except ValueError:
            valid = ", ".join(c.value for c in EvaluationCriteria)
            raise ValueError(
                f"Invalid criterion: '{name}'. Valid criteria: {valid}"
            )

    return parsed


def _load_personas(path: Path) -> list[dict]:
    """Load personas from a JSON file."""
    with open(path) as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, list):
        personas = data
    elif isinstance(data, dict):
        if "personas" in data:
            personas = data["personas"]
        else:
            personas = [data]
    else:
        raise ValueError("Invalid JSON format: expected object or array")

    # Convert Persona objects to dicts if needed
    result = []
    for p in personas:
        if isinstance(p, dict):
            result.append(p)
        else:
            # Try to convert to dict
            if hasattr(p, "to_dict"):
                result.append(p.to_dict())
            elif hasattr(p, "__dict__"):
                result.append(p.__dict__)
            else:
                raise ValueError(f"Cannot convert persona to dict: {type(p)}")

    return result
