"""Installation smoke tests to catch packaging issues.

These tests verify that the CLI can be imported and run without
ModuleNotFoundError or other import issues. They help catch cases
where source files are accidentally gitignored.
"""

import subprocess
import sys


def test_cli_imports_successfully():
    """Verify CLI can be imported without ModuleNotFoundError."""
    result = subprocess.run(
        [sys.executable, "-c", "from persona.ui.cli import app"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"CLI import failed: {result.stderr}"


def test_cli_help_works():
    """Verify CLI --help runs without error."""
    # Use the installed entry point script
    result = subprocess.run(
        ["persona", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"CLI help failed: {result.stderr}"
    assert "persona" in result.stdout.lower()
