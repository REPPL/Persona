"""
CLI testing utilities.

This module provides helper functions for testing Persona's CLI interface.
"""

import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner, Result


def run_cli_command(
    app,
    args: list[str],
    input_text: str | None = None,
    env: dict[str, str] | None = None,
    catch_exceptions: bool = True,
) -> Result:
    """
    Run a CLI command and return the result.

    Args:
        app: The Typer application to test
        args: Command line arguments
        input_text: Optional stdin input
        env: Optional environment variables
        catch_exceptions: Whether to catch exceptions

    Returns:
        Typer test Result object
    """
    runner = CliRunner()
    return runner.invoke(
        app,
        args,
        input=input_text,
        env=env,
        catch_exceptions=catch_exceptions,
    )


def assert_cli_success(result: Result) -> None:
    """
    Assert that a CLI command succeeded.

    Args:
        result: The CLI result to check

    Raises:
        AssertionError: If the command failed
    """
    if result.exit_code != 0:
        raise AssertionError(
            f"CLI command failed with exit code {result.exit_code}\n"
            f"Output: {result.output}\n"
            f"Exception: {result.exception}"
        )


def assert_cli_failure(result: Result, expected_code: int = 1) -> None:
    """
    Assert that a CLI command failed with expected exit code.

    Args:
        result: The CLI result to check
        expected_code: Expected exit code (default: 1)

    Raises:
        AssertionError: If the command didn't fail as expected
    """
    if result.exit_code != expected_code:
        raise AssertionError(
            f"Expected exit code {expected_code}, got {result.exit_code}\n"
            f"Output: {result.output}"
        )


def assert_output_contains(result: Result, *expected_strings: str) -> None:
    """
    Assert that CLI output contains all expected strings.

    Args:
        result: The CLI result to check
        *expected_strings: Strings that should appear in output

    Raises:
        AssertionError: If any string is not found
    """
    for expected in expected_strings:
        if expected not in result.output:
            raise AssertionError(
                f"Expected '{expected}' not found in output:\n{result.output}"
            )


def assert_output_not_contains(result: Result, *unexpected_strings: str) -> None:
    """
    Assert that CLI output does not contain certain strings.

    Args:
        result: The CLI result to check
        *unexpected_strings: Strings that should not appear in output

    Raises:
        AssertionError: If any string is found
    """
    for unexpected in unexpected_strings:
        if unexpected in result.output:
            raise AssertionError(
                f"Unexpected '{unexpected}' found in output:\n{result.output}"
            )


def assert_file_created(path: Path) -> None:
    """
    Assert that a file was created.

    Args:
        path: Path to check

    Raises:
        AssertionError: If file doesn't exist
    """
    if not path.exists():
        raise AssertionError(f"Expected file not created: {path}")


def assert_json_file_valid(path: Path) -> dict[str, Any]:
    """
    Assert that a JSON file exists and is valid JSON.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON content

    Raises:
        AssertionError: If file doesn't exist or is invalid JSON
    """
    assert_file_created(path)
    try:
        with open(path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Invalid JSON in {path}: {e}")


def assert_experiment_structure(exp_dir: Path) -> None:
    """
    Assert that an experiment directory has the expected structure.

    Args:
        exp_dir: Path to experiment directory

    Raises:
        AssertionError: If structure is invalid
    """
    assert_file_created(exp_dir)
    assert_file_created(exp_dir / "config.yaml")


def assert_output_structure(output_dir: Path) -> None:
    """
    Assert that an output directory has the expected structure.

    Args:
        output_dir: Path to output directory

    Raises:
        AssertionError: If structure is invalid
    """
    assert_file_created(output_dir)
    assert_file_created(output_dir / "metadata.json")
    assert_file_created(output_dir / "personas")


def get_latest_output_dir(outputs_base: Path) -> Path | None:
    """
    Get the most recently created output directory.

    Args:
        outputs_base: Base outputs directory

    Returns:
        Path to latest output dir, or None if empty
    """
    if not outputs_base.exists():
        return None

    dirs = [d for d in outputs_base.iterdir() if d.is_dir()]
    if not dirs:
        return None

    # Sort by name (timestamps sort chronologically)
    return sorted(dirs)[-1]
