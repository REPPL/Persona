"""
Basic package tests to verify installation.
"""

import pytest


def test_package_import():
    """Test that the persona package can be imported."""
    import persona
    assert hasattr(persona, "__version__")


def test_version_string():
    """Test that version string is valid."""
    from persona import __version__
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_cli_import():
    """Test that CLI module can be imported."""
    from persona.ui.cli import app
    assert app is not None


def test_core_import():
    """Test that core module can be imported."""
    from persona import core
    assert core is not None
