"""Unit tests for run history tracking."""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from persona.core.experiments.history import (
    RunHistory,
    RunHistoryManager,
    RunInfo,
    TokenUsage,
)


class TestTokenUsage:
    """Tests for TokenUsage model."""

    def test_token_usage_defaults(self):
        """Should have sensible defaults."""
        usage = TokenUsage()
        assert usage.input == 0
        assert usage.output == 0
        assert usage.total == 0

    def test_token_usage_total_computed(self):
        """Should compute total from input + output."""
        usage = TokenUsage(input=100, output=200)
        assert usage.total == 300

    def test_token_usage_from_dict(self):
        """Should create from dictionary."""
        data = {"input": 500, "output": 1000}
        usage = TokenUsage(**data)
        assert usage.input == 500
        assert usage.output == 1000
        assert usage.total == 1500


class TestRunInfo:
    """Tests for RunInfo model."""

    def test_run_info_defaults(self):
        """Should have sensible defaults for optional fields."""
        now = datetime(2024, 12, 17, 12, 0, 0, tzinfo=timezone.utc)
        run = RunInfo(run_id="20241217_120000", started_at=now)
        assert run.status == "running"
        assert run.provider == ""
        assert run.model == ""
        assert run.persona_count == 0
        assert run.tokens.total == 0
        assert run.started_at == now

    def test_run_info_with_tokens(self):
        """Should accept TokenUsage object."""
        tokens = TokenUsage(input=100, output=200)
        now = datetime(2024, 12, 17, 12, 0, 0, tzinfo=timezone.utc)
        run = RunInfo(
            run_id="20241217_120000",
            started_at=now,
            provider="anthropic",
            model="claude-sonnet-4-5-20250514",
            persona_count=3,
            tokens=tokens,
            status="success",
        )
        assert run.tokens.total == 300
        assert run.persona_count == 3
        assert run.status == "success"

    def test_run_info_serialisation(self):
        """Should serialise to JSON-compatible dict."""
        run = RunInfo(
            run_id="20241217_120000",
            started_at=datetime(2024, 12, 17, 12, 0, 0, tzinfo=timezone.utc),
            provider="anthropic",
            model="claude-sonnet-4-5-20250514",
            persona_count=3,
            tokens=TokenUsage(input=100, output=200),
            status="success",
        )
        data = run.model_dump(mode="json")
        assert data["run_id"] == "20241217_120000"
        assert data["tokens"]["input"] == 100
        assert data["tokens"]["output"] == 200


class TestRunHistory:
    """Tests for RunHistory model."""

    def test_run_history_defaults(self):
        """Should have sensible defaults."""
        history = RunHistory(experiment="test-exp")
        assert history.experiment == "test-exp"
        assert history.runs == []

    def test_run_history_with_runs(self):
        """Should store multiple runs."""
        now = datetime(2024, 12, 17, 12, 0, 0, tzinfo=timezone.utc)
        runs = [
            RunInfo(run_id="run1", started_at=now, persona_count=3),
            RunInfo(run_id="run2", started_at=now, persona_count=5),
        ]
        history = RunHistory(experiment="test-exp", runs=runs)
        assert len(history.runs) == 2
        assert history.runs[0].run_id == "run1"


class TestRunHistoryManager:
    """Tests for RunHistoryManager."""

    @pytest.fixture
    def temp_experiment(self, tmp_path):
        """Create temporary experiment directory."""
        exp_dir = tmp_path / "test-experiment"
        exp_dir.mkdir()
        (exp_dir / "data").mkdir()
        (exp_dir / "outputs").mkdir()
        return exp_dir

    @pytest.fixture
    def manager(self, temp_experiment):
        """Create manager for temp experiment."""
        return RunHistoryManager(temp_experiment, "test-experiment")

    def test_init_creates_history_path(self, manager, temp_experiment):
        """Should set correct history path."""
        assert manager.history_path == temp_experiment / "history.json"

    def test_record_run_creates_file(self, manager, temp_experiment):
        """Should create history.json on first run."""
        manager.record_run(
            provider="anthropic",
            model="claude-sonnet-4-5-20250514",
            persona_count=3,
            tokens={"input": 100, "output": 200},
            output_dir="20241217_120000",
        )

        assert (temp_experiment / "history.json").exists()

    def test_record_run_returns_run_info(self, manager):
        """Should return the recorded RunInfo."""
        run = manager.record_run(
            provider="openai",
            model="gpt-4o",
            persona_count=5,
            tokens={"input": 500, "output": 1000},
            output_dir="20241217_130000",
        )

        assert run.provider == "openai"
        assert run.model == "gpt-4o"
        assert run.persona_count == 5
        assert run.tokens.total == 1500
        assert run.status == "success"

    def test_list_runs_empty(self, manager):
        """Should return empty list when no runs."""
        runs = manager.list_runs()
        assert runs == []

    def test_list_runs_returns_all(self, manager):
        """Should return all runs."""
        manager.record_run(
            provider="anthropic",
            model="claude-sonnet-4-5-20250514",
            persona_count=3,
            tokens={"input": 100, "output": 200},
            output_dir="run1",
        )
        manager.record_run(
            provider="openai",
            model="gpt-4o",
            persona_count=5,
            tokens={"input": 500, "output": 1000},
            output_dir="run2",
        )

        runs = manager.list_runs()
        assert len(runs) == 2

    def test_list_runs_filter_by_status(self, manager):
        """Should filter runs by status."""
        manager.record_run(
            provider="anthropic",
            model="claude-sonnet-4-5-20250514",
            persona_count=3,
            tokens={"input": 100, "output": 200},
            output_dir="run1",
            status="success",
        )
        manager.record_run(
            provider="openai",
            model="gpt-4o",
            persona_count=0,
            tokens={"input": 50, "output": 0},
            output_dir="run2",
            status="failed",
        )

        success_runs = manager.list_runs(status="success")
        assert len(success_runs) == 1
        assert success_runs[0].status == "success"

        failed_runs = manager.list_runs(status="failed")
        assert len(failed_runs) == 1
        assert failed_runs[0].status == "failed"

    def test_list_runs_filter_by_provider(self, manager):
        """Should filter runs by provider."""
        manager.record_run(
            provider="anthropic",
            model="claude-sonnet-4-5-20250514",
            persona_count=3,
            tokens={"input": 100, "output": 200},
            output_dir="run1",
        )
        manager.record_run(
            provider="openai",
            model="gpt-4o",
            persona_count=5,
            tokens={"input": 500, "output": 1000},
            output_dir="run2",
        )

        anthropic_runs = manager.list_runs(provider="anthropic")
        assert len(anthropic_runs) == 1
        assert anthropic_runs[0].provider == "anthropic"

    def test_list_runs_filter_by_model(self, manager):
        """Should filter runs by model."""
        manager.record_run(
            provider="openai",
            model="gpt-4o",
            persona_count=3,
            tokens={"input": 100, "output": 200},
            output_dir="run1",
        )
        manager.record_run(
            provider="openai",
            model="gpt-4o-mini",
            persona_count=5,
            tokens={"input": 500, "output": 1000},
            output_dir="run2",
        )

        gpt4_runs = manager.list_runs(model="gpt-4o")
        assert len(gpt4_runs) == 1
        assert gpt4_runs[0].model == "gpt-4o"

    def test_list_runs_with_limit(self, manager):
        """Should limit number of returned runs."""
        for i in range(5):
            manager.record_run(
                provider="anthropic",
                model="claude-sonnet-4-5-20250514",
                persona_count=i,
                tokens={"input": 100 * i, "output": 200 * i},
                output_dir=f"run{i}",
            )

        runs = manager.list_runs(limit=3)
        assert len(runs) == 3

    def test_get_run_by_id(self, manager):
        """Should retrieve specific run by ID."""
        run = manager.record_run(
            provider="anthropic",
            model="claude-sonnet-4-5-20250514",
            persona_count=3,
            tokens={"input": 100, "output": 200},
            output_dir="specific-run",
        )

        retrieved = manager.get_run(run.run_id)
        assert retrieved is not None
        assert retrieved.run_id == run.run_id
        assert retrieved.persona_count == 3

    def test_get_run_not_found(self, manager):
        """Should return None for non-existent run."""
        result = manager.get_run("nonexistent-id")
        assert result is None

    def test_start_and_complete_run(self, manager):
        """Should track run lifecycle."""
        run = manager.start_run(
            provider="anthropic",
            model="claude-sonnet-4-5-20250514",
        )
        assert run.status == "running"
        assert run.completed_at is None

        completed = manager.complete_run(
            run.run_id,
            status="success",
            persona_count=3,
            tokens={"input": 100, "output": 200},
            output_dir="lifecycle-run",
        )
        assert completed.status == "success"
        assert completed.completed_at is not None
        assert completed.persona_count == 3
        assert completed.output_dir == "lifecycle-run"

    def test_history_persists_across_instances(self, temp_experiment):
        """Should persist history across manager instances."""
        manager1 = RunHistoryManager(temp_experiment, "test-experiment")
        manager1.record_run(
            provider="anthropic",
            model="claude-sonnet-4-5-20250514",
            persona_count=3,
            tokens={"input": 100, "output": 200},
            output_dir="run1",
        )

        # Create new manager instance
        manager2 = RunHistoryManager(temp_experiment, "test-experiment")
        runs = manager2.list_runs()
        assert len(runs) == 1
        assert runs[0].provider == "anthropic"

    def test_corrupted_history_handled(self, temp_experiment):
        """Should handle corrupted history file gracefully."""
        history_path = temp_experiment / "history.json"
        history_path.write_text("not valid json {{{")

        manager = RunHistoryManager(temp_experiment, "test-experiment")
        runs = manager.list_runs()
        assert runs == []  # Should return empty, not crash
