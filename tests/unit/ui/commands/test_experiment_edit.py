"""Tests for experiment edit CLI command."""

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from persona.ui.cli import app


runner = CliRunner()


class TestEditCommand:
    """Tests for experiment edit command."""

    def test_edit_not_found(self):
        """Test editing nonexistent experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, [
                "experiment", "edit", "nonexistent",
                "--base-dir", tmpdir,
            ])
            assert result.exit_code == 1
            assert "not found" in result.output

    def test_edit_show_config(self):
        """Test edit without options shows config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create experiment first
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "-d", "Test experiment",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Current Configuration" in result.output
            assert "provider:" in result.output
            assert "count:" in result.output

    def test_edit_set_single_field(self):
        """Test setting a single field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--set", "count=10",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Set count = 10" in result.output

    def test_edit_set_multiple_fields(self):
        """Test setting multiple fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--set", "count=5",
                "--set", "provider=openai",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Set count = 5" in result.output
            assert "Set provider = openai" in result.output

    def test_edit_set_nested_field(self):
        """Test setting nested field path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--set", "generation.model=gpt-4o",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Set generation.model = gpt-4o" in result.output

    def test_edit_set_invalid_format(self):
        """Test setting field with invalid format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--set", "invalid_no_equals",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 1
            assert "Invalid format" in result.output

    def test_edit_set_invalid_field(self):
        """Test setting invalid field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--set", "nonexistent=value",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 1
            assert "Invalid field" in result.output

    def test_edit_add_source(self):
        """Test adding a data source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Create source file
            source_path = Path(tmpdir) / "data.csv"
            source_path.write_text("col1,col2\na,b\n")

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--add-source", str(source_path),
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Added source: data.csv" in result.output

    def test_edit_add_multiple_sources(self):
        """Test adding multiple data sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Create source files
            source1 = Path(tmpdir) / "data1.csv"
            source1.write_text("col1\n")
            source2 = Path(tmpdir) / "data2.csv"
            source2.write_text("col1\n")

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--add-source", str(source1),
                "--add-source", str(source2),
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Added source: data1.csv" in result.output
            assert "Added source: data2.csv" in result.output

    def test_edit_add_source_not_found(self):
        """Test adding nonexistent source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--add-source", "/nonexistent/file.csv",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 1
            assert "not found" in result.output.lower()

    def test_edit_remove_source(self):
        """Test removing a data source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Add source first
            source_path = Path(tmpdir) / "data.csv"
            source_path.write_text("col1\n")

            runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--add-source", str(source_path),
                "--base-dir", tmpdir,
            ])

            # Now remove it
            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--remove-source", "data.csv",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Removed source: data.csv" in result.output

    def test_edit_remove_source_not_found(self):
        """Test removing nonexistent source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--remove-source", "nonexistent.csv",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 1
            assert "not found" in result.output.lower()

    def test_edit_rollback(self):
        """Test rolling back edits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Make an edit
            runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--set", "count=10",
                "--base-dir", tmpdir,
            ])

            # Rollback
            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--rollback", "1",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Rolled back 1 edit" in result.output

    def test_edit_rollback_nothing(self):
        """Test rollback when nothing to rollback."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--rollback", "1",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Nothing to rollback" in result.output

    def test_edit_rollback_too_many(self):
        """Test rollback with too many steps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Make one edit
            runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--set", "count=10",
                "--base-dir", tmpdir,
            ])

            # Try to rollback more than available
            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--rollback", "5",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 1
            assert "Cannot rollback" in result.output

    def test_edit_clear_history(self):
        """Test clearing edit history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Make edits
            runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--set", "count=10",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--clear-history",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Cleared edit history" in result.output

    def test_edit_combined_operations(self):
        """Test combining multiple edit operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Create source file
            source_path = Path(tmpdir) / "data.csv"
            source_path.write_text("col1\n")

            result = runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--set", "count=5",
                "--add-source", str(source_path),
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Set count = 5" in result.output
            assert "Added source: data.csv" in result.output


class TestSourcesCommand:
    """Tests for experiment sources command."""

    def test_sources_not_found(self):
        """Test listing sources for nonexistent experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, [
                "experiment", "sources", "nonexistent",
                "--base-dir", tmpdir,
            ])
            assert result.exit_code == 1
            assert "not found" in result.output

    def test_sources_empty(self):
        """Test listing sources when none exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "sources", "test-exp",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "No data sources found" in result.output

    def test_sources_list(self):
        """Test listing sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Add sources
            source_path = Path(tmpdir) / "data.csv"
            source_path.write_text("col1\n")

            runner.invoke(app, [
                "experiment", "edit", "test-exp",
                "--add-source", str(source_path),
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "sources", "test-exp",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "data.csv" in result.output
