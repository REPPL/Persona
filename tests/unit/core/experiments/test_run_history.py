"""Tests for experiment run history."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from persona.core.experiments import (
    ExperimentManager,
    RunHistory,
    RunMetadata,
    RunStatistics,
)


class TestRunMetadata:
    """Tests for RunMetadata dataclass."""

    def test_create_metadata(self):
        """Test creating run metadata."""
        meta = RunMetadata(
            run_id=1,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            model="gpt-4o",
            provider="openai",
            persona_count=3,
            cost=0.45,
        )
        assert meta.run_id == 1
        assert meta.model == "gpt-4o"
        assert meta.persona_count == 3

    def test_to_dict(self):
        """Test converting metadata to dictionary."""
        meta = RunMetadata(
            run_id=1,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            model="claude-sonnet-4.5",
            provider="anthropic",
            cost=0.72,
        )
        data = meta.to_dict()
        assert data["run_id"] == 1
        assert data["model"] == "claude-sonnet-4.5"
        assert "timestamp" in data

    def test_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            "run_id": 5,
            "timestamp": "2024-01-15T10:30:00",
            "model": "gpt-4o",
            "provider": "openai",
            "persona_count": 5,
            "cost": 0.62,
            "status": "completed",
        }
        meta = RunMetadata.from_dict(data)
        assert meta.run_id == 5
        assert meta.model == "gpt-4o"
        assert meta.persona_count == 5

    def test_from_dict_defaults(self):
        """Test defaults when creating from dictionary."""
        data = {
            "timestamp": "2024-01-15T10:30:00",
        }
        meta = RunMetadata.from_dict(data)
        assert meta.run_id == 0
        assert meta.model == "unknown"
        assert meta.status == "unknown"


class TestRunStatistics:
    """Tests for RunStatistics dataclass."""

    def test_create_statistics(self):
        """Test creating run statistics."""
        stats = RunStatistics(
            total_runs=10,
            completed_runs=8,
            failed_runs=2,
            total_personas=24,
            total_cost=5.50,
        )
        assert stats.total_runs == 10
        assert stats.completed_runs == 8
        assert stats.total_personas == 24

    def test_to_dict(self):
        """Test converting statistics to dictionary."""
        stats = RunStatistics(
            total_runs=5,
            total_cost=2.38,
            models_used=["gpt-4o", "claude-sonnet-4.5"],
        )
        data = stats.to_dict()
        assert data["total_runs"] == 5
        assert data["total_cost"] == 2.38
        assert "gpt-4o" in data["models_used"]


class TestRunHistory:
    """Tests for RunHistory class."""

    def test_record_run(self):
        """Test recording a run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            run = history.record_run(
                "test-exp",
                model="gpt-4o",
                provider="openai",
                persona_count=3,
                cost=0.45,
            )

            assert run.run_id == 1
            assert run.model == "gpt-4o"
            assert run.persona_count == 3

    def test_record_multiple_runs(self):
        """Test recording multiple runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            run1 = history.record_run("test-exp", model="gpt-4o", provider="openai")
            run2 = history.record_run("test-exp", model="claude-sonnet-4.5", provider="anthropic")
            run3 = history.record_run("test-exp", model="gemini-2.0", provider="gemini")

            assert run1.run_id == 1
            assert run2.run_id == 2
            assert run3.run_id == 3

    def test_get_runs(self):
        """Test getting all runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            history.record_run("test-exp", model="gpt-4o", provider="openai")
            history.record_run("test-exp", model="claude-sonnet-4.5", provider="anthropic")

            runs = history.get_runs("test-exp")

            assert len(runs) == 2
            # Most recent first
            assert runs[0].model == "claude-sonnet-4.5"

    def test_get_runs_last_n(self):
        """Test getting last N runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            for i in range(5):
                history.record_run("test-exp", model=f"model-{i}", provider="test")

            runs = history.get_runs("test-exp", last=2)

            assert len(runs) == 2

    def test_get_runs_filter_status(self):
        """Test filtering runs by status."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            history.record_run("test-exp", model="model-1", provider="test", status="completed")
            history.record_run("test-exp", model="model-2", provider="test", status="failed")
            history.record_run("test-exp", model="model-3", provider="test", status="completed")

            completed = history.get_runs("test-exp", status="completed")
            failed = history.get_runs("test-exp", status="failed")

            assert len(completed) == 2
            assert len(failed) == 1

    def test_get_run_by_id(self):
        """Test getting a specific run by ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            history.record_run("test-exp", model="model-1", provider="test")
            history.record_run("test-exp", model="model-2", provider="test")

            run = history.get_run("test-exp", 2)

            assert run is not None
            assert run.model == "model-2"

    def test_get_run_not_found(self):
        """Test getting nonexistent run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)

            run = history.get_run("test-exp", 999)

            assert run is None

    def test_get_statistics(self):
        """Test getting run statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            history.record_run(
                "test-exp", model="gpt-4o", provider="openai",
                persona_count=3, cost=0.45, status="completed"
            )
            history.record_run(
                "test-exp", model="claude-sonnet-4.5", provider="anthropic",
                persona_count=5, cost=0.72, status="completed"
            )
            history.record_run(
                "test-exp", model="gemini-2.0", provider="gemini",
                persona_count=0, cost=0.10, status="failed"
            )

            stats = history.get_statistics("test-exp")

            assert stats.total_runs == 3
            assert stats.completed_runs == 2
            assert stats.failed_runs == 1
            assert stats.total_personas == 8
            assert stats.total_cost == pytest.approx(1.27)
            assert "gpt-4o" in stats.models_used
            assert "openai" in stats.providers_used

    def test_get_statistics_empty(self):
        """Test getting statistics with no runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            stats = history.get_statistics("test-exp")

            assert stats.total_runs == 0
            assert stats.total_personas == 0

    def test_diff_runs(self):
        """Test comparing two runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            history.record_run(
                "test-exp", model="gpt-4o", provider="openai",
                persona_count=3, cost=0.45
            )
            history.record_run(
                "test-exp", model="claude-sonnet-4.5", provider="anthropic",
                persona_count=5, cost=0.72
            )

            diff = history.diff_runs("test-exp", 1, 2)

            assert "run_1" in diff
            assert "run_2" in diff
            assert "differences" in diff
            assert "model" in diff["differences"]
            assert diff["delta"]["persona_count"] == 2
            assert diff["delta"]["cost"] == pytest.approx(0.27)

    def test_diff_runs_not_found(self):
        """Test comparing with nonexistent run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            history.record_run("test-exp", model="gpt-4o", provider="openai")

            with pytest.raises(ValueError, match="not found"):
                history.diff_runs("test-exp", 1, 999)

    def test_clear_history(self):
        """Test clearing run history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            history.record_run("test-exp", model="gpt-4o", provider="openai")
            history.record_run("test-exp", model="claude-sonnet-4.5", provider="anthropic")

            assert len(history.get_runs("test-exp")) == 2

            history.clear_history("test-exp")

            assert len(history.get_runs("test-exp")) == 0

    def test_clear_history_no_runs(self):
        """Test clearing history when no runs exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)

            # Should not raise
            history.clear_history("test-exp")

    def test_persistence(self):
        """Test that runs persist across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            # First instance records runs
            history1 = RunHistory(manager)
            history1.record_run("test-exp", model="gpt-4o", provider="openai")

            # Second instance should see the runs
            history2 = RunHistory(manager)
            runs = history2.get_runs("test-exp")

            assert len(runs) == 1
            assert runs[0].model == "gpt-4o"

    def test_record_run_with_all_fields(self):
        """Test recording run with all fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExperimentManager(base_dir=tmpdir)
            manager.create("test-exp")

            history = RunHistory(manager)
            run = history.record_run(
                "test-exp",
                model="gpt-4o",
                provider="openai",
                persona_count=5,
                input_tokens=1500,
                output_tokens=3000,
                cost=0.62,
                status="completed",
                duration_seconds=45.5,
                output_dir="outputs/20240115_103000",
            )

            assert run.input_tokens == 1500
            assert run.output_tokens == 3000
            assert run.duration_seconds == 45.5
            assert run.output_dir == "outputs/20240115_103000"
