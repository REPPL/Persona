"""Unit tests for experiment manifest."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from persona.core.experiments.manifest import (
    ExperimentManifest,
    ExperimentSummary,
    ManifestManager,
)


class TestExperimentSummary:
    """Tests for ExperimentSummary model."""

    def test_defaults(self):
        """Should have sensible defaults."""
        summary = ExperimentSummary(name="test-exp", path="/path/to/exp")

        assert summary.name == "test-exp"
        assert summary.path == "/path/to/exp"
        assert summary.description == ""
        assert summary.run_count == 0
        assert summary.last_run is None
        assert summary.total_personas == 0
        assert summary.total_tokens == 0
        assert summary.providers_used == []

    def test_with_all_fields(self):
        """Should accept all fields."""
        now = datetime.now(timezone.utc)
        summary = ExperimentSummary(
            name="research-study",
            path="/projects/research",
            description="User research",
            run_count=5,
            last_run=now,
            total_personas=15,
            total_tokens=10000,
            providers_used=["anthropic", "openai"],
        )

        assert summary.run_count == 5
        assert summary.total_personas == 15
        assert summary.providers_used == ["anthropic", "openai"]


class TestExperimentManifest:
    """Tests for ExperimentManifest model."""

    def test_defaults(self):
        """Should have sensible defaults."""
        manifest = ExperimentManifest()

        assert manifest.experiments == {}
        assert manifest.version == 1
        assert manifest.last_updated is not None

    def test_get_experiment(self):
        """Should retrieve experiment by name."""
        manifest = ExperimentManifest()
        summary = ExperimentSummary(name="test", path="/test")
        manifest.experiments["test"] = summary

        result = manifest.get_experiment("test")
        assert result is not None
        assert result.name == "test"

    def test_get_experiment_returns_none_for_missing(self):
        """Should return None for missing experiment."""
        manifest = ExperimentManifest()
        result = manifest.get_experiment("nonexistent")
        assert result is None

    def test_add_experiment(self):
        """Should add new experiment."""
        manifest = ExperimentManifest()
        summary = manifest.add_experiment(
            name="new-exp",
            path="/path/to/new",
            description="New experiment",
        )

        assert "new-exp" in manifest.experiments
        assert summary.name == "new-exp"
        assert summary.description == "New experiment"

    def test_remove_experiment(self):
        """Should remove existing experiment."""
        manifest = ExperimentManifest()
        manifest.add_experiment("to-remove", "/path")

        result = manifest.remove_experiment("to-remove")
        assert result is True
        assert "to-remove" not in manifest.experiments

    def test_remove_experiment_returns_false_for_missing(self):
        """Should return False for missing experiment."""
        manifest = ExperimentManifest()
        result = manifest.remove_experiment("nonexistent")
        assert result is False

    def test_update_run_stats(self):
        """Should update stats after run."""
        manifest = ExperimentManifest()
        manifest.add_experiment("test", "/test")

        manifest.update_run_stats(
            name="test",
            persona_count=3,
            token_count=1000,
            provider="anthropic",
        )

        exp = manifest.experiments["test"]
        assert exp.run_count == 1
        assert exp.total_personas == 3
        assert exp.total_tokens == 1000
        assert "anthropic" in exp.providers_used

    def test_update_run_stats_accumulates(self):
        """Should accumulate stats across runs."""
        manifest = ExperimentManifest()
        manifest.add_experiment("test", "/test")

        manifest.update_run_stats("test", 3, 1000, "anthropic")
        manifest.update_run_stats("test", 5, 2000, "openai")

        exp = manifest.experiments["test"]
        assert exp.run_count == 2
        assert exp.total_personas == 8
        assert exp.total_tokens == 3000
        assert set(exp.providers_used) == {"anthropic", "openai"}

    def test_update_run_stats_ignores_missing(self):
        """Should not crash for missing experiment."""
        manifest = ExperimentManifest()
        # Should not raise
        manifest.update_run_stats("nonexistent", 3, 1000, "anthropic")

    def test_list_experiments_all(self):
        """Should list all experiments sorted."""
        manifest = ExperimentManifest()
        manifest.add_experiment("zebra", "/z")
        manifest.add_experiment("alpha", "/a")
        manifest.add_experiment("middle", "/m")

        result = manifest.list_experiments()
        names = [e.name for e in result]
        assert names == ["alpha", "middle", "zebra"]

    def test_list_experiments_filter_has_runs(self):
        """Should filter by has_runs."""
        manifest = ExperimentManifest()
        manifest.add_experiment("with-runs", "/w")
        manifest.add_experiment("no-runs", "/n")
        manifest.update_run_stats("with-runs", 3, 1000, "anthropic")

        with_runs = manifest.list_experiments(has_runs=True)
        assert len(with_runs) == 1
        assert with_runs[0].name == "with-runs"

        without_runs = manifest.list_experiments(has_runs=False)
        assert len(without_runs) == 1
        assert without_runs[0].name == "no-runs"

    def test_list_experiments_filter_provider(self):
        """Should filter by provider."""
        manifest = ExperimentManifest()
        manifest.add_experiment("anthropic-exp", "/a")
        manifest.add_experiment("openai-exp", "/o")
        manifest.update_run_stats("anthropic-exp", 3, 1000, "anthropic")
        manifest.update_run_stats("openai-exp", 3, 1000, "openai")

        result = manifest.list_experiments(provider="anthropic")
        assert len(result) == 1
        assert result[0].name == "anthropic-exp"

    def test_get_statistics(self):
        """Should return aggregate statistics."""
        manifest = ExperimentManifest()
        manifest.add_experiment("exp1", "/1")
        manifest.add_experiment("exp2", "/2")
        manifest.update_run_stats("exp1", 3, 1000, "anthropic")
        manifest.update_run_stats("exp1", 2, 500, "anthropic")
        manifest.update_run_stats("exp2", 5, 2000, "openai")

        stats = manifest.get_statistics()
        assert stats["experiment_count"] == 2
        assert stats["total_runs"] == 3
        assert stats["total_personas"] == 10
        assert stats["total_tokens"] == 3500
        assert set(stats["providers"]) == {"anthropic", "openai"}


class TestManifestManager:
    """Tests for ManifestManager class."""

    @pytest.fixture
    def temp_base_dir(self, tmp_path):
        """Create temporary experiments base directory."""
        base_dir = tmp_path / "experiments"
        base_dir.mkdir()
        return base_dir

    @pytest.fixture
    def manager(self, temp_base_dir):
        """Create manager for temp base directory."""
        return ManifestManager(base_dir=temp_base_dir)

    def test_manifest_path(self, manager, temp_base_dir):
        """Should use correct manifest path."""
        assert manager.manifest_path == temp_base_dir / ".manifest.json"

    def test_load_creates_empty_when_missing(self, manager, temp_base_dir):
        """Should create empty manifest when file doesn't exist."""
        manifest = manager.load()

        assert isinstance(manifest, ExperimentManifest)
        assert manifest.experiments == {}

    def test_save_creates_file(self, manager, temp_base_dir):
        """Should create manifest file on save."""
        manifest = manager.load()
        manifest.add_experiment("test", str(temp_base_dir / "test"))
        manager.save()

        assert (temp_base_dir / ".manifest.json").exists()

    def test_update_experiment(self, manager, temp_base_dir):
        """Should update experiment in manifest."""
        manager.update_experiment(
            name="new-exp",
            path=str(temp_base_dir / "new-exp"),
            description="New experiment",
        )

        manifest = manager.load()
        assert "new-exp" in manifest.experiments
        assert manifest.experiments["new-exp"].description == "New experiment"

    def test_remove_experiment(self, manager, temp_base_dir):
        """Should remove experiment from manifest."""
        manager.update_experiment("to-remove", str(temp_base_dir / "to-remove"))
        manager.remove_experiment("to-remove")

        manifest = manager.load()
        assert "to-remove" not in manifest.experiments

    def test_record_run(self, manager, temp_base_dir):
        """Should record run in manifest."""
        manager.update_experiment("test", str(temp_base_dir / "test"))
        manager.record_run(
            experiment_name="test",
            persona_count=3,
            token_count=1000,
            provider="anthropic",
        )

        manifest = manager.load()
        exp = manifest.experiments["test"]
        assert exp.run_count == 1
        assert exp.total_personas == 3

    def test_rebuild_from_filesystem(self, temp_base_dir):
        """Should rebuild manifest from filesystem."""
        # Create experiment directories
        exp1_dir = temp_base_dir / "exp-one"
        exp1_dir.mkdir()
        (exp1_dir / "config.yaml").write_text("description: First experiment")

        exp2_dir = temp_base_dir / "exp-two"
        exp2_dir.mkdir()
        (exp2_dir / "config.yaml").write_text("description: Second experiment")
        (exp2_dir / "history.json").write_text(json.dumps({
            "runs": [
                {
                    "persona_count": 3,
                    "tokens": {"input": 100, "output": 200},
                    "provider": "anthropic",
                    "completed_at": "2024-12-17T12:00:00Z",
                }
            ]
        }))

        manager = ManifestManager(base_dir=temp_base_dir)
        manifest = manager.rebuild()

        assert len(manifest.experiments) == 2
        assert "exp-one" in manifest.experiments
        assert "exp-two" in manifest.experiments

        exp2 = manifest.experiments["exp-two"]
        assert exp2.run_count == 1
        assert exp2.total_personas == 3
        assert exp2.total_tokens == 300

    def test_rebuild_ignores_hidden_dirs(self, temp_base_dir):
        """Should ignore hidden directories."""
        (temp_base_dir / ".hidden").mkdir()
        (temp_base_dir / "valid-exp").mkdir()
        (temp_base_dir / "valid-exp" / "config.yaml").write_text("name: valid")

        manager = ManifestManager(base_dir=temp_base_dir)
        manifest = manager.rebuild()

        assert ".hidden" not in manifest.experiments
        assert "valid-exp" in manifest.experiments

    def test_rebuild_handles_corrupted_history(self, temp_base_dir):
        """Should handle corrupted history.json gracefully."""
        exp_dir = temp_base_dir / "bad-history"
        exp_dir.mkdir()
        (exp_dir / "config.yaml").write_text("name: bad")
        (exp_dir / "history.json").write_text("not valid json {{{")

        manager = ManifestManager(base_dir=temp_base_dir)
        manifest = manager.rebuild()

        # Should still add experiment, just with zero stats
        assert "bad-history" in manifest.experiments
        assert manifest.experiments["bad-history"].run_count == 0

    def test_persistence(self, temp_base_dir):
        """Should persist across manager instances."""
        manager1 = ManifestManager(base_dir=temp_base_dir)
        manager1.update_experiment("test", str(temp_base_dir / "test"))
        manager1.save()

        # New instance
        manager2 = ManifestManager(base_dir=temp_base_dir)
        manifest = manager2.load()

        assert "test" in manifest.experiments

    def test_corrupted_manifest_triggers_rebuild(self, temp_base_dir):
        """Should rebuild if manifest file is corrupted."""
        # Create valid experiment
        exp_dir = temp_base_dir / "valid-exp"
        exp_dir.mkdir()
        (exp_dir / "config.yaml").write_text("name: valid")

        # Write corrupted manifest
        (temp_base_dir / ".manifest.json").write_text("not valid json")

        manager = ManifestManager(base_dir=temp_base_dir)
        manifest = manager.load()

        # Should have rebuilt from filesystem
        assert "valid-exp" in manifest.experiments
