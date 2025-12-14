"""
Shared console utilities for CLI output.

Provides a consistent console experience across all CLI commands,
respecting the NO_COLOR standard (https://no-color.org/).
"""

import os

from rich.console import Console

# Standard output width for clean display
MAX_WIDTH = 100


def get_console(*, no_color: bool = False, quiet: bool = False) -> Console:
    """Get a console with appropriate settings.

    Args:
        no_color: Force disable colour output.
        quiet: Suppress all output except errors.

    Returns:
        Rich Console configured for Persona CLI.

    The console respects:
    - NO_COLOR environment variable (https://no-color.org/)
    - Explicit no_color parameter
    - Terminal width (capped at MAX_WIDTH)
    """
    disable_color = no_color or os.environ.get("NO_COLOR") is not None
    return Console(
        no_color=disable_color,
        width=min(MAX_WIDTH, Console().width),
        quiet=quiet,
    )
