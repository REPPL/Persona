"""
Shared console utilities for CLI output.

Provides a consistent console experience across all CLI commands,
respecting the NO_COLOR standard (https://no-color.org/).
"""

import os
from enum import IntEnum

from rich.console import Console

# Standard output width for clean display
MAX_WIDTH = 100


class Verbosity(IntEnum):
    """Verbosity levels for CLI output.

    Levels:
        QUIET: Errors and final result only (-q/--quiet)
        NORMAL: Standard output (default)
        VERBOSE: Additional context (-v/--verbose)
        DEBUG: Full debug information (-vv)
    """

    QUIET = 0
    NORMAL = 1
    VERBOSE = 2
    DEBUG = 3


class PersonaConsole:
    """Enhanced console with verbosity support.

    Wraps Rich Console with verbosity-aware output methods.
    """

    def __init__(
        self,
        *,
        no_color: bool = False,
        verbosity: Verbosity = Verbosity.NORMAL,
    ) -> None:
        """Initialise console with settings.

        Args:
            no_color: Force disable colour output.
            verbosity: Output verbosity level.
        """
        disable_color = no_color or os.environ.get("NO_COLOR") is not None
        self._console = Console(
            no_color=disable_color,
            width=min(MAX_WIDTH, Console().width),
            quiet=verbosity == Verbosity.QUIET,
        )
        self._verbosity = verbosity

    @property
    def verbosity(self) -> Verbosity:
        """Get current verbosity level."""
        return self._verbosity

    @property
    def is_quiet(self) -> bool:
        """Check if in quiet mode."""
        return self._verbosity == Verbosity.QUIET

    @property
    def is_verbose(self) -> bool:
        """Check if in verbose mode (or higher)."""
        return self._verbosity >= Verbosity.VERBOSE

    @property
    def is_debug(self) -> bool:
        """Check if in debug mode."""
        return self._verbosity >= Verbosity.DEBUG

    def print(self, *args, **kwargs) -> None:
        """Print to console (respects quiet mode)."""
        self._console.print(*args, **kwargs)

    def print_verbose(self, *args, **kwargs) -> None:
        """Print only in verbose mode or higher."""
        if self.is_verbose:
            self._console.print(*args, **kwargs)

    def print_debug(self, *args, **kwargs) -> None:
        """Print only in debug mode."""
        if self.is_debug:
            self._console.print(*args, **kwargs)

    def status(self, *args, **kwargs):
        """Create a status context (spinner)."""
        return self._console.status(*args, **kwargs)

    def rule(self, *args, **kwargs) -> None:
        """Print a horizontal rule."""
        self._console.rule(*args, **kwargs)

    def log(self, *args, **kwargs) -> None:
        """Log with timestamp (verbose mode only)."""
        if self.is_verbose:
            self._console.log(*args, **kwargs)

    # Delegate common Rich Console attributes
    @property
    def width(self) -> int:
        """Get console width."""
        return self._console.width

    @property
    def no_color(self) -> bool:
        """Check if colour is disabled."""
        return self._console.no_color


def get_console(
    *,
    no_color: bool = False,
    quiet: bool = False,
    verbosity: int = 1,
) -> PersonaConsole:
    """Get a console with appropriate settings.

    Args:
        no_color: Force disable colour output.
        quiet: Suppress all output except errors (sets verbosity to QUIET).
        verbosity: Verbosity level (0=quiet, 1=normal, 2=verbose, 3=debug).

    Returns:
        PersonaConsole configured for Persona CLI.

    The console respects:
    - NO_COLOR environment variable (https://no-color.org/)
    - Explicit no_color parameter
    - Terminal width (capped at MAX_WIDTH)
    - Verbosity levels for conditional output
    """
    # Quiet flag overrides verbosity
    if quiet:
        level = Verbosity.QUIET
    else:
        # Clamp verbosity to valid range
        level = Verbosity(min(max(verbosity, 0), 3))

    return PersonaConsole(no_color=no_color, verbosity=level)
