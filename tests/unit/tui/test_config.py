"""Tests for TUI configuration."""

import pytest

from persona.tui.config import TUIConfig, TerminalRequirements, ResponsiveBreakpoint


def test_terminal_requirements_defaults():
    """Test terminal requirements default values."""
    req = TerminalRequirements()
    assert req.min_width == 80
    assert req.min_height == 24


def test_responsive_breakpoint():
    """Test responsive breakpoint creation."""
    bp = ResponsiveBreakpoint("compact", 80, 119)
    assert bp.name == "compact"
    assert bp.min_width == 80
    assert bp.max_width == 119


def test_tui_config_initialization():
    """Test TUI config initialization."""
    config = TUIConfig()
    assert config.requirements.min_width == 80
    assert config.requirements.min_height == 24
    assert config.refresh_interval == 1.0
    assert config.enable_mouse is True
    assert len(config.breakpoints) == 3


def test_get_breakpoint_too_small():
    """Test breakpoint detection for too small terminal."""
    config = TUIConfig()
    assert config.get_breakpoint(70) == "error"


def test_get_breakpoint_compact():
    """Test breakpoint detection for compact layout."""
    config = TUIConfig()
    assert config.get_breakpoint(80) == "compact"
    assert config.get_breakpoint(100) == "compact"
    assert config.get_breakpoint(119) == "compact"


def test_get_breakpoint_standard():
    """Test breakpoint detection for standard layout."""
    config = TUIConfig()
    assert config.get_breakpoint(120) == "standard"
    assert config.get_breakpoint(140) == "standard"
    assert config.get_breakpoint(159) == "standard"


def test_get_breakpoint_wide():
    """Test breakpoint detection for wide layout."""
    config = TUIConfig()
    assert config.get_breakpoint(160) == "wide"
    assert config.get_breakpoint(200) == "wide"


def test_meets_requirements_success():
    """Test terminal meets requirements."""
    config = TUIConfig()
    meets, error = config.meets_requirements(80, 24)
    assert meets is True
    assert error == ""


def test_meets_requirements_width_fail():
    """Test terminal width too small."""
    config = TUIConfig()
    meets, error = config.meets_requirements(70, 24)
    assert meets is False
    assert "width" in error.lower()


def test_meets_requirements_height_fail():
    """Test terminal height too small."""
    config = TUIConfig()
    meets, error = config.meets_requirements(80, 20)
    assert meets is False
    assert "height" in error.lower()


def test_meets_requirements_both_fail():
    """Test terminal too small in both dimensions."""
    config = TUIConfig()
    meets, error = config.meets_requirements(70, 20)
    assert meets is False
    assert "width" in error.lower()
    assert "height" in error.lower()
