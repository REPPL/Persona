"""Tests for TUI validators."""

import pytest

from persona.tui.validators import (
    TerminalSize,
    get_terminal_size,
    validate_terminal_size,
)


def test_terminal_size_named_tuple():
    """Test TerminalSize named tuple."""
    size = TerminalSize(columns=120, rows=40)
    assert size.columns == 120
    assert size.rows == 40


def test_get_terminal_size():
    """Test getting terminal size."""
    size = get_terminal_size()
    assert isinstance(size, TerminalSize)
    assert size.columns > 0
    assert size.rows > 0


def test_validate_terminal_size_default():
    """Test terminal validation with default minimums."""
    # This test depends on actual terminal size
    # Just verify it returns the correct types
    is_valid, error = validate_terminal_size()
    assert isinstance(is_valid, bool)
    assert isinstance(error, str)


def test_validate_terminal_size_custom():
    """Test terminal validation with custom minimums."""
    # Very small minimum should always pass
    is_valid, error = validate_terminal_size(min_width=1, min_height=1)
    assert is_valid is True
    assert error == ""

    # Very large minimum will likely fail
    is_valid, error = validate_terminal_size(min_width=10000, min_height=10000)
    assert is_valid is False
    assert "too small" in error.lower() or "Terminal too small" in error
