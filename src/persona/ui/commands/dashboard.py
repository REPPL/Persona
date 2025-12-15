"""
Dashboard command for launching the TUI.

This module provides the `persona dashboard` command for launching
the full-screen terminal user interface.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer

dashboard_app = typer.Typer(
    name="dashboard",
    help="Launch the TUI dashboard.",
    no_args_is_help=False,
)


@dashboard_app.callback(invoke_without_command=True)
def dashboard(
    ctx: typer.Context,
    experiments_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--experiments-dir",
            "-e",
            help="Path to experiments directory.",
        ),
    ] = None,
    no_mouse: Annotated[
        bool,
        typer.Option(
            "--no-mouse",
            help="Disable mouse support (keyboard only).",
        ),
    ] = False,
    theme: Annotated[
        Optional[str],
        typer.Option(
            "--theme",
            help="Colour theme (dark, light).",
        ),
    ] = None,
) -> None:
    """
    Launch the Persona TUI dashboard.

    The dashboard provides a full-screen terminal interface for:
    - Browsing and managing experiments
    - Monitoring persona generation in real-time
    - Viewing personas and quality scores
    - Tracking API costs

    Keyboard shortcuts:
        Q: Quit
        ?: Help
        D: Dashboard
        E: Experiments

    Example:
        persona dashboard
        persona dashboard --experiments-dir ./my-experiments
        persona dashboard --no-mouse
    """
    from persona.tui.app import PersonaApp
    from persona.tui.validators import validate_terminal_size

    # Validate terminal size before launching
    is_valid, error = validate_terminal_size(min_width=80, min_height=24)

    if not is_valid:
        console = _get_console()
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(1)

    # Determine experiments directory
    exp_dir = experiments_dir or Path.cwd() / "experiments"

    # Create and run the app
    try:
        app = PersonaApp(
            experiments_dir=exp_dir,
            enable_mouse=not no_mouse,
        )
        app.run()
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        pass
    except Exception as e:
        console = _get_console()
        console.print(f"[red]Error launching dashboard:[/red] {e}")
        raise typer.Exit(1)


def _get_console():
    """Get Rich console for output."""
    from persona.ui.console import get_console

    return get_console()
