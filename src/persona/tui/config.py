"""
Configuration for the TUI dashboard.

This module provides configuration classes for the TUI, including
minimum terminal sizes, breakpoints, and theme settings.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TerminalRequirements:
    """Minimum terminal size requirements."""

    min_width: int = 80
    min_height: int = 24


@dataclass
class ResponsiveBreakpoint:
    """Responsive layout breakpoint."""

    name: str
    min_width: int
    max_width: int | None = None


class TUIConfig:
    """
    Configuration for the TUI dashboard.

    Defines minimum terminal sizes, responsive breakpoints,
    and other dashboard settings.

    Attributes:
        requirements: Minimum terminal size requirements.
        breakpoints: Responsive layout breakpoints.
        experiments_dir: Default experiments directory.
        refresh_interval: How often to refresh data (seconds).
        enable_mouse: Whether to enable mouse support.
    """

    def __init__(
        self,
        experiments_dir: str | Path = "./experiments",
        refresh_interval: float = 1.0,
        enable_mouse: bool = True,
    ) -> None:
        """
        Initialise TUI configuration.

        Args:
            experiments_dir: Path to experiments directory.
            refresh_interval: How often to refresh data (seconds).
            enable_mouse: Whether to enable mouse support.
        """
        self.requirements = TerminalRequirements()
        self.experiments_dir = Path(experiments_dir)
        self.refresh_interval = refresh_interval
        self.enable_mouse = enable_mouse

        # Define responsive breakpoints
        self.breakpoints = [
            ResponsiveBreakpoint("compact", 80, 119),
            ResponsiveBreakpoint("standard", 120, 159),
            ResponsiveBreakpoint("wide", 160, None),
        ]

    def get_breakpoint(self, width: int) -> str:
        """
        Determine current breakpoint based on width.

        Args:
            width: Terminal width in columns.

        Returns:
            Breakpoint name or "error" if too small.
        """
        if width < self.requirements.min_width:
            return "error"

        for bp in self.breakpoints:
            if bp.max_width is None:
                if width >= bp.min_width:
                    return bp.name
            elif bp.min_width <= width <= bp.max_width:
                return bp.name

        return "standard"  # Default fallback

    def meets_requirements(self, width: int, height: int) -> tuple[bool, str]:
        """
        Check if terminal meets minimum requirements.

        Args:
            width: Terminal width.
            height: Terminal height.

        Returns:
            Tuple of (meets_requirements, error_message).
        """
        errors = []

        if width < self.requirements.min_width:
            errors.append(
                f"Terminal width {width} < minimum {self.requirements.min_width}"
            )

        if height < self.requirements.min_height:
            errors.append(
                f"Terminal height {height} < minimum {self.requirements.min_height}"
            )

        if errors:
            return False, "; ".join(errors)

        return True, ""
