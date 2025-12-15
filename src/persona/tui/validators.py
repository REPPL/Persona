"""
Terminal size validation for the TUI.

This module provides validation functions to ensure the terminal
meets minimum size requirements before launching the TUI.
"""

import shutil
from typing import NamedTuple


class TerminalSize(NamedTuple):
    """Terminal size in columns and rows."""

    columns: int
    rows: int


def get_terminal_size() -> TerminalSize:
    """
    Get current terminal size.

    Returns:
        TerminalSize with columns and rows.
    """
    size = shutil.get_terminal_size(fallback=(80, 24))
    return TerminalSize(columns=size.columns, rows=size.lines)


def validate_terminal_size(
    min_width: int = 80, min_height: int = 24
) -> tuple[bool, str]:
    """
    Validate that terminal meets minimum size requirements.

    Args:
        min_width: Minimum width in columns.
        min_height: Minimum height in rows.

    Returns:
        Tuple of (is_valid, error_message).
    """
    size = get_terminal_size()

    if size.columns < min_width or size.rows < min_height:
        error = (
            f"Terminal too small: {size.columns}×{size.rows} "
            f"(minimum: {min_width}×{min_height})\n\n"
            "Please resize your terminal window and try again."
        )
        return False, error

    return True, ""
