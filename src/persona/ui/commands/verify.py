"""
Verify command for multi-model verification of persona generation.
"""

import asyncio
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from persona.core.quality.verification import (
    MultiModelVerifier,
    VerificationConfig,
)
from persona.ui.console import get_console

verify_app = typer.Typer(
    name="verify",
    help="Verify persona generation across multiple models.",
)


@verify_app.callback(invoke_without_command=True)
def verify(
    ctx: typer.Context,
    data_path: Annotated[
        Path,
        typer.Argument(
            help="Path to data file or directory for verification.",
            exists=True,
        ),
    ],
    models: Annotated[
        Optional[str],
        typer.Option(
            "--models",
            "-m",
            help="Comma-separated list of models to verify across.",
        ),
    ] = None,
    samples: Annotated[
        int,
        typer.Option(
            "--samples",
            "-s",
            help="Number of samples to generate per model.",
        ),
    ] = 3,
    strategy: Annotated[
        str,
        typer.Option(
            "--strategy",
            help="Voting strategy (majority, unanimous, weighted).",
        ),
    ] = "majority",
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            "-t",
            help="Consistency threshold for passing (0-1).",
        ),
    ] = 0.7,
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-n",
            help="Number of personas to generate.",
        ),
    ] = 3,
    self_consistency: Annotated[
        bool,
        typer.Option(
            "--self-consistency",
            help="Check self-consistency of a single model.",
        ),
    ] = False,
    report: Annotated[
        Optional[Path],
        typer.Option(
            "--report",
            "-r",
            help="Path to save verification report (markdown).",
        ),
    ] = None,
    sequential: Annotated[
        bool,
        typer.Option(
            "--sequential",
            help="Run models sequentially instead of in parallel.",
        ),
    ] = False,
    no_progress: Annotated[
        bool,
        typer.Option(
            "--no-progress",
            help="Disable progress indicators.",
        ),
    ] = False,
) -> None:
    """
    Verify persona generation across multiple models.

    Detects model-specific artifacts and hallucinations by comparing
    outputs from different LLM providers.

    Examples:

        # Verify across multiple models
        persona verify data.txt --models claude-sonnet-4,gpt-4o,gemini-2.0-flash

        # Self-consistency check
        persona verify data.txt --self-consistency --models claude-sonnet-4 --samples 5

        # Save detailed report
        persona verify data.txt --models claude-sonnet-4,gpt-4o --report report.md
    """
    console = get_console()

    # Parse models
    if models:
        model_list = [m.strip() for m in models.split(",")]
    else:
        # Default models
        model_list = ["claude-sonnet-4-20250514", "gpt-4o", "gemini-2.0-flash"]

    # Create configuration
    config = VerificationConfig(
        models=model_list,
        samples_per_model=samples,
        voting_strategy=strategy,
        consistency_threshold=threshold,
        parallel=not sequential,
    )

    # Display configuration
    if not no_progress:
        console.print("\n[bold cyan]Verification Configuration[/bold cyan]")
        config_table = Table(show_header=False, box=None, padding=(0, 2))
        config_table.add_column("Setting", style="bold")
        config_table.add_column("Value")
        config_table.add_row("Data Path", str(data_path))
        config_table.add_row("Models", ", ".join(model_list))
        config_table.add_row("Samples per Model", str(samples))
        config_table.add_row("Voting Strategy", strategy)
        config_table.add_row("Threshold", f"{threshold:.1%}")
        config_table.add_row(
            "Mode", "Self-Consistency" if self_consistency else "Cross-Model"
        )
        config_table.add_row("Execution", "Sequential" if sequential else "Parallel")
        console.print(config_table)
        console.print()

    # Create verifier
    verifier = MultiModelVerifier(config)

    # Run verification
    try:
        if not no_progress:
            with console.status("[bold cyan]Running verification...", spinner="dots"):
                if self_consistency:
                    result = asyncio.run(
                        verifier.verify_self_consistency(
                            data_path,
                            model=model_list[0],
                            samples=samples,
                        )
                    )
                else:
                    result = asyncio.run(verifier.verify(data_path, count=count))
        else:
            if self_consistency:
                result = asyncio.run(
                    verifier.verify_self_consistency(
                        data_path,
                        model=model_list[0],
                        samples=samples,
                    )
                )
            else:
                result = asyncio.run(verifier.verify(data_path, count=count))

        # Display results
        _display_results(console, result, no_progress)

        # Save report if requested
        if report:
            report_content = result.to_markdown()
            report.write_text(report_content)
            console.print(f"\n[green]✓[/green] Report saved to {report}")

        # Exit with appropriate code
        if result.passed:
            raise typer.Exit(0)
        else:
            raise typer.Exit(1)

    except KeyboardInterrupt:
        console.print("\n[yellow]Verification cancelled[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _display_results(console, result, quiet: bool = False) -> None:
    """Display verification results."""
    # Status panel
    status_text = Text()
    if result.passed:
        status_text.append("✓ PASSED", style="bold green")
    else:
        status_text.append("✗ FAILED", style="bold red")

    status_text.append(f"\nConsistency Score: {result.consistency_score:.2%}")
    status_text.append(f"\nThreshold: {result.config.consistency_threshold:.2%}")

    console.print(
        Panel(
            status_text,
            title="[bold]Verification Result[/bold]",
            border_style="green" if result.passed else "red",
        )
    )

    if not quiet:
        # Metrics table
        console.print("\n[bold cyan]Consistency Metrics[/bold cyan]")
        metrics_table = Table(show_header=True, box=None, padding=(0, 2))
        metrics_table.add_column("Metric", style="bold")
        metrics_table.add_column("Score", justify="right")
        metrics_table.add_column("Bar", width=30)

        metrics = [
            ("Attribute Agreement", result.metrics.attribute_agreement),
            ("Semantic Consistency", result.metrics.semantic_consistency),
            ("Factual Convergence", result.metrics.factual_convergence),
        ]

        for name, score in metrics:
            bar = _create_progress_bar(score)
            metrics_table.add_row(name, f"{score:.2%}", bar)

        console.print(metrics_table)

        # Attributes
        console.print("\n[bold cyan]Attribute Analysis[/bold cyan]")
        attr_table = Table(show_header=True, box=None, padding=(0, 2))
        attr_table.add_column("Category", style="bold")
        attr_table.add_column("Count", justify="right")
        attr_table.add_column("Attributes")

        agreed = ", ".join(result.agreed_attributes[:5])
        if len(result.agreed_attributes) > 5:
            agreed += f" (+{len(result.agreed_attributes) - 5} more)"

        disputed = ", ".join(result.disputed_attributes[:5])
        if len(result.disputed_attributes) > 5:
            disputed += f" (+{len(result.disputed_attributes) - 5} more)"

        attr_table.add_row(
            "Agreed", str(len(result.agreed_attributes)), agreed or "[dim]none[/dim]"
        )
        attr_table.add_row(
            "Disputed",
            str(len(result.disputed_attributes)),
            disputed or "[dim]none[/dim]",
        )

        console.print(attr_table)

        # Model outputs
        console.print("\n[bold cyan]Model Outputs[/bold cyan]")
        model_table = Table(show_header=True, box=None, padding=(0, 2))
        model_table.add_column("Model", style="bold")
        model_table.add_column("Personas", justify="right")

        for model_name, output in result.model_outputs.items():
            count = len(output) if isinstance(output, list) else 1
            model_table.add_row(model_name, str(count))

        console.print(model_table)


def _create_progress_bar(score: float, width: int = 30) -> str:
    """Create a text-based progress bar."""
    filled = int(score * width)
    empty = width - filled

    if score >= 0.7:
        bar_char = "█"
        style = "green"
    elif score >= 0.5:
        bar_char = "█"
        style = "yellow"
    else:
        bar_char = "█"
        style = "red"

    bar = f"[{style}]" + (bar_char * filled) + "[/]"
    bar += "░" * empty
    return bar


if __name__ == "__main__":
    verify_app()
