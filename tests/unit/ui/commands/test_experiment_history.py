"""Tests for experiment history CLI command."""

import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from persona.ui.cli import app


runner = CliRunner()


class TestHistoryCommand:
    """Tests for experiment history command."""

    def test_history_not_found(self):
        """Test history for nonexistent experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, [
                "experiment", "history", "nonexistent",
                "--base-dir", tmpdir,
            ])
            assert result.exit_code == 1
            assert "not found" in result.output

    def test_history_no_runs(self):
        """Test history with no runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "No runs found" in result.output

    def test_history_with_runs(self):
        """Test history with recorded runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Record some runs
            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "gpt-4o", "--provider", "openai",
                "--personas", "3", "--cost", "0.45",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Run History" in result.output
            assert "gpt-4o" in result.output
            assert "#1" in result.output

    def test_history_last_n(self):
        """Test history with --last option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            # Record multiple runs
            for i in range(5):
                runner.invoke(app, [
                    "experiment", "record-run", "test-exp",
                    "--model", f"model-{i}", "--provider", "test",
                    "--base-dir", tmpdir,
                ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--last", "2",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            # Should show most recent
            assert "#5" in result.output
            assert "#4" in result.output

    def test_history_stats(self):
        """Test history --stats option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "gpt-4o", "--provider", "openai",
                "--personas", "3", "--cost", "0.45",
                "--base-dir", tmpdir,
            ])
            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "claude-sonnet-4.5", "--provider", "anthropic",
                "--personas", "5", "--cost", "0.72",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--stats",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Statistics" in result.output
            assert "Total:" in result.output
            assert "Completed:" in result.output
            assert "Cost:" in result.output

    def test_history_diff(self):
        """Test history --diff option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "gpt-4o", "--provider", "openai",
                "--personas", "3", "--cost", "0.45",
                "--base-dir", tmpdir,
            ])
            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "claude-sonnet-4.5", "--provider", "anthropic",
                "--personas", "5", "--cost", "0.72",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--diff", "1,2",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Comparison" in result.output
            assert "Differences" in result.output or "Delta" in result.output

    def test_history_diff_invalid_format(self):
        """Test history --diff with invalid format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--diff", "invalid",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 1

    def test_history_diff_run_not_found(self):
        """Test history --diff with nonexistent run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "gpt-4o", "--provider", "openai",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--diff", "1,999",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 1
            assert "not found" in result.output

    def test_history_status_filter(self):
        """Test history --status filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "gpt-4o", "--provider", "openai",
                "--status", "completed",
                "--base-dir", tmpdir,
            ])
            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "claude-sonnet-4.5", "--provider", "anthropic",
                "--status", "failed",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--status", "completed",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "gpt-4o" in result.output

    def test_history_json_output(self):
        """Test history with JSON output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "gpt-4o", "--provider", "openai",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--json",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert '"experiment":' in result.output
            assert '"runs":' in result.output

    def test_history_stats_json(self):
        """Test history stats with JSON output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "gpt-4o", "--provider", "openai",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "history", "test-exp",
                "--stats", "--json",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert '"total_runs":' in result.output


class TestRecordRunCommand:
    """Tests for experiment record-run command."""

    def test_record_run_not_found(self):
        """Test recording run for nonexistent experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, [
                "experiment", "record-run", "nonexistent",
                "--model", "gpt-4o", "--provider", "openai",
                "--base-dir", tmpdir,
            ])
            assert result.exit_code == 1
            assert "not found" in result.output

    def test_record_run_basic(self):
        """Test recording a basic run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "gpt-4o", "--provider", "openai",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Recorded run #1" in result.output

    def test_record_run_full(self):
        """Test recording run with all options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "claude-sonnet-4.5",
                "--provider", "anthropic",
                "--personas", "5",
                "--cost", "0.72",
                "--status", "completed",
                "--output-dir", "outputs/run1",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Recorded run #1" in result.output


class TestClearHistoryCommand:
    """Tests for experiment clear-history command."""

    def test_clear_history_not_found(self):
        """Test clearing history for nonexistent experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, [
                "experiment", "clear-history", "nonexistent",
                "--force",
                "--base-dir", tmpdir,
            ])
            assert result.exit_code == 1
            assert "not found" in result.output

    def test_clear_history_force(self):
        """Test clearing history with --force."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            runner.invoke(app, [
                "experiment", "record-run", "test-exp",
                "--model", "gpt-4o", "--provider", "openai",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "clear-history", "test-exp",
                "--force",
                "--base-dir", tmpdir,
            ])

            assert result.exit_code == 0
            assert "Cleared run history" in result.output

    def test_clear_history_cancelled(self):
        """Test clearing history cancelled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            runner.invoke(app, [
                "experiment", "create", "test-exp",
                "--base-dir", tmpdir,
            ])

            result = runner.invoke(app, [
                "experiment", "clear-history", "test-exp",
                "--base-dir", tmpdir,
            ], input="n\n")

            assert result.exit_code == 0
            assert "Cancelled" in result.output
