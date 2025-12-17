"""
Unit tests for SQLite experiment store.
"""

import pytest

from persona.core.experiments import SQLiteExperimentStore


class TestSQLiteExperimentStore:
    """Tests for SQLiteExperimentStore."""

    @pytest.fixture
    def store(self) -> SQLiteExperimentStore:
        """Create an in-memory store for testing."""
        return SQLiteExperimentStore(":memory:")

    # =========================================================================
    # Experiment Tests
    # =========================================================================

    def test_create_experiment(self, store: SQLiteExperimentStore) -> None:
        """Test creating an experiment."""
        exp_id = store.create_experiment(
            name="test-experiment",
            description="A test experiment",
            hypothesis="This will work",
        )

        assert exp_id is not None
        assert len(exp_id) > 0

    def test_create_experiment_with_project(self, store: SQLiteExperimentStore) -> None:
        """Test creating an experiment linked to a project."""
        exp_id = store.create_experiment(
            name="test-experiment",
            project_id="proj-123",
            description="A test experiment",
        )

        exp = store.get_experiment(exp_id)
        assert exp is not None
        assert exp["project_id"] == "proj-123"

    def test_create_duplicate_experiment_raises(
        self, store: SQLiteExperimentStore
    ) -> None:
        """Test that duplicate experiment names raise an error."""
        store.create_experiment(name="test-experiment")

        with pytest.raises(ValueError, match="already exists"):
            store.create_experiment(name="test-experiment")

    def test_get_experiment(self, store: SQLiteExperimentStore) -> None:
        """Test retrieving an experiment."""
        exp_id = store.create_experiment(
            name="test-experiment",
            description="A test",
            hypothesis="Testing",
        )

        exp = store.get_experiment(exp_id)
        assert exp is not None
        assert exp["name"] == "test-experiment"
        assert exp["description"] == "A test"
        assert exp["hypothesis"] == "Testing"
        assert exp["status"] == "planned"

    def test_get_experiment_not_found(self, store: SQLiteExperimentStore) -> None:
        """Test retrieving a non-existent experiment."""
        result = store.get_experiment("nonexistent")
        assert result is None

    def test_get_experiment_by_name(self, store: SQLiteExperimentStore) -> None:
        """Test retrieving an experiment by name."""
        store.create_experiment(name="test-experiment")

        exp = store.get_experiment_by_name("test-experiment")
        assert exp is not None
        assert exp["name"] == "test-experiment"

    def test_list_experiments(self, store: SQLiteExperimentStore) -> None:
        """Test listing experiments."""
        store.create_experiment(name="exp-1")
        store.create_experiment(name="exp-2")
        store.create_experiment(name="exp-3")

        experiments = store.list_experiments()
        assert len(experiments) == 3

    def test_list_experiments_by_project(self, store: SQLiteExperimentStore) -> None:
        """Test filtering experiments by project."""
        store.create_experiment(name="exp-1", project_id="proj-a")
        store.create_experiment(name="exp-2", project_id="proj-a")
        store.create_experiment(name="exp-3", project_id="proj-b")

        proj_a_exps = store.list_experiments(project_id="proj-a")
        assert len(proj_a_exps) == 2

    def test_list_experiments_by_status(self, store: SQLiteExperimentStore) -> None:
        """Test filtering experiments by status."""
        exp1_id = store.create_experiment(name="exp-1")
        store.create_experiment(name="exp-2")
        store.update_experiment(exp1_id, status="active")

        active_exps = store.list_experiments(status="active")
        assert len(active_exps) == 1
        assert active_exps[0]["name"] == "exp-1"

    def test_update_experiment(self, store: SQLiteExperimentStore) -> None:
        """Test updating an experiment."""
        exp_id = store.create_experiment(name="test-experiment")

        result = store.update_experiment(
            exp_id,
            description="Updated description",
            status="active",
        )

        assert result is True
        exp = store.get_experiment(exp_id)
        assert exp["description"] == "Updated description"
        assert exp["status"] == "active"

    def test_delete_experiment(self, store: SQLiteExperimentStore) -> None:
        """Test deleting an experiment."""
        exp_id = store.create_experiment(name="test-experiment")

        result = store.delete_experiment(exp_id)
        assert result is True

        exp = store.get_experiment(exp_id)
        assert exp is None

    # =========================================================================
    # Variant Tests
    # =========================================================================

    def test_create_variant(self, store: SQLiteExperimentStore) -> None:
        """Test creating a variant."""
        exp_id = store.create_experiment(name="test-experiment")

        var_id = store.create_variant(
            experiment_id=exp_id,
            name="high-temp",
            parameters={"temperature": 0.9},
            description="High temperature variant",
        )

        assert var_id is not None

    def test_create_duplicate_variant_raises(
        self, store: SQLiteExperimentStore
    ) -> None:
        """Test that duplicate variant names raise an error."""
        exp_id = store.create_experiment(name="test-experiment")
        store.create_variant(exp_id, "variant-a", {"param": 1})

        with pytest.raises(ValueError, match="already exists"):
            store.create_variant(exp_id, "variant-a", {"param": 2})

    def test_get_variant(self, store: SQLiteExperimentStore) -> None:
        """Test retrieving a variant."""
        exp_id = store.create_experiment(name="test-experiment")
        var_id = store.create_variant(
            exp_id,
            "high-temp",
            {"temperature": 0.9},
        )

        var = store.get_variant(var_id)
        assert var is not None
        assert var["name"] == "high-temp"
        assert var["parameters"]["temperature"] == 0.9

    def test_list_variants(self, store: SQLiteExperimentStore) -> None:
        """Test listing variants for an experiment."""
        exp_id = store.create_experiment(name="test-experiment")
        store.create_variant(exp_id, "variant-a", {"param": 1})
        store.create_variant(exp_id, "variant-b", {"param": 2})

        variants = store.list_variants(exp_id)
        assert len(variants) == 2

    def test_update_variant(self, store: SQLiteExperimentStore) -> None:
        """Test updating a variant."""
        exp_id = store.create_experiment(name="test-experiment")
        var_id = store.create_variant(exp_id, "variant-a", {"param": 1})

        store.update_variant(var_id, description="Updated")
        var = store.get_variant(var_id)
        assert var["description"] == "Updated"

    def test_delete_variant(self, store: SQLiteExperimentStore) -> None:
        """Test deleting a variant."""
        exp_id = store.create_experiment(name="test-experiment")
        var_id = store.create_variant(exp_id, "variant-a", {"param": 1})

        result = store.delete_variant(var_id)
        assert result is True
        assert store.get_variant(var_id) is None

    # =========================================================================
    # Run Tests
    # =========================================================================

    def test_create_run(self, store: SQLiteExperimentStore) -> None:
        """Test creating a run."""
        exp_id = store.create_experiment(name="test-experiment")

        run_id = store.create_run(
            experiment_id=exp_id,
            model="claude-sonnet-4-20250514",
            provider="anthropic",
        )

        assert run_id is not None

    def test_create_run_with_variant(self, store: SQLiteExperimentStore) -> None:
        """Test creating a run with a variant."""
        exp_id = store.create_experiment(name="test-experiment")
        var_id = store.create_variant(exp_id, "high-temp", {"temperature": 0.9})

        run_id = store.create_run(
            experiment_id=exp_id,
            model="claude-sonnet-4-20250514",
            provider="anthropic",
            variant_id=var_id,
        )

        run = store.get_run(run_id)
        assert run["variant_id"] == var_id

    def test_run_numbers_increment(self, store: SQLiteExperimentStore) -> None:
        """Test that run numbers increment correctly."""
        exp_id = store.create_experiment(name="test-experiment")

        run1_id = store.create_run(exp_id, "model-a", "provider-a")
        run2_id = store.create_run(exp_id, "model-a", "provider-a")
        run3_id = store.create_run(exp_id, "model-a", "provider-a")

        run1 = store.get_run(run1_id)
        run2 = store.get_run(run2_id)
        run3 = store.get_run(run3_id)

        assert run1["run_number"] == 1
        assert run2["run_number"] == 2
        assert run3["run_number"] == 3

    def test_get_run(self, store: SQLiteExperimentStore) -> None:
        """Test retrieving a run."""
        exp_id = store.create_experiment(name="test-experiment")
        run_id = store.create_run(exp_id, "claude-sonnet", "anthropic")

        run = store.get_run(run_id)
        assert run is not None
        assert run["model"] == "claude-sonnet"
        assert run["provider"] == "anthropic"
        assert run["status"] == "running"

    def test_list_runs(self, store: SQLiteExperimentStore) -> None:
        """Test listing runs."""
        exp_id = store.create_experiment(name="test-experiment")
        store.create_run(exp_id, "model-a", "provider-a")
        store.create_run(exp_id, "model-b", "provider-b")
        store.create_run(exp_id, "model-c", "provider-c")

        runs = store.list_runs(exp_id)
        assert len(runs) == 3

    def test_list_runs_with_limit(self, store: SQLiteExperimentStore) -> None:
        """Test limiting the number of runs returned."""
        exp_id = store.create_experiment(name="test-experiment")
        for i in range(5):
            store.create_run(exp_id, f"model-{i}", "provider")

        runs = store.list_runs(exp_id, limit=3)
        assert len(runs) == 3

    def test_complete_run(self, store: SQLiteExperimentStore) -> None:
        """Test completing a run with metrics."""
        exp_id = store.create_experiment(name="test-experiment")
        run_id = store.create_run(exp_id, "claude-sonnet", "anthropic")

        result = store.complete_run(
            run_id,
            persona_count=5,
            input_tokens=1000,
            output_tokens=500,
            cost=0.045,
            duration_seconds=12.5,
            metrics={"quality_score": 0.95},
        )

        assert result is True

        run = store.get_run(run_id)
        assert run["status"] == "completed"
        assert run["persona_count"] == 5
        assert run["input_tokens"] == 1000
        assert run["output_tokens"] == 500
        assert run["cost"] == 0.045
        assert run["duration_seconds"] == 12.5
        assert run["metrics"]["quality_score"] == 0.95
        assert run["completed_at"] is not None

    def test_delete_run(self, store: SQLiteExperimentStore) -> None:
        """Test deleting a run."""
        exp_id = store.create_experiment(name="test-experiment")
        run_id = store.create_run(exp_id, "claude-sonnet", "anthropic")

        result = store.delete_run(run_id)
        assert result is True
        assert store.get_run(run_id) is None

    # =========================================================================
    # Statistics Tests
    # =========================================================================

    def test_get_experiment_statistics(self, store: SQLiteExperimentStore) -> None:
        """Test getting experiment statistics."""
        exp_id = store.create_experiment(name="test-experiment")

        # Create and complete some runs
        run1_id = store.create_run(exp_id, "claude-sonnet", "anthropic")
        run2_id = store.create_run(exp_id, "gpt-4o", "openai")
        run3_id = store.create_run(exp_id, "claude-sonnet", "anthropic")

        store.complete_run(run1_id, persona_count=3, cost=0.01, status="completed")
        store.complete_run(run2_id, persona_count=5, cost=0.02, status="completed")
        store.complete_run(run3_id, persona_count=0, cost=0.005, status="failed")

        stats = store.get_experiment_statistics(exp_id)

        assert stats["total_runs"] == 3
        assert stats["completed_runs"] == 2
        assert stats["failed_runs"] == 1
        assert stats["total_personas"] == 8
        assert stats["total_cost"] == pytest.approx(0.035)
        assert "claude-sonnet" in stats["models_used"]
        assert "gpt-4o" in stats["models_used"]

    def test_compare_runs(self, store: SQLiteExperimentStore) -> None:
        """Test comparing two runs."""
        exp_id = store.create_experiment(name="test-experiment")

        run1_id = store.create_run(exp_id, "claude-sonnet", "anthropic")
        run2_id = store.create_run(exp_id, "gpt-4o", "openai")

        store.complete_run(run1_id, persona_count=3, cost=0.01)
        store.complete_run(run2_id, persona_count=5, cost=0.02)

        comparison = store.compare_runs(run1_id, run2_id)

        assert "model" in comparison["differences"]
        assert "provider" in comparison["differences"]
        assert comparison["delta"]["persona_count"] == 2
        assert comparison["delta"]["cost"] == pytest.approx(0.01)

    # =========================================================================
    # Cascade Delete Tests
    # =========================================================================

    def test_delete_experiment_cascades_to_variants(
        self, store: SQLiteExperimentStore
    ) -> None:
        """Test that deleting an experiment deletes its variants."""
        exp_id = store.create_experiment(name="test-experiment")
        var_id = store.create_variant(exp_id, "variant-a", {"param": 1})

        store.delete_experiment(exp_id)

        assert store.get_variant(var_id) is None

    def test_delete_experiment_cascades_to_runs(
        self, store: SQLiteExperimentStore
    ) -> None:
        """Test that deleting an experiment deletes its runs."""
        exp_id = store.create_experiment(name="test-experiment")
        run_id = store.create_run(exp_id, "claude-sonnet", "anthropic")

        store.delete_experiment(exp_id)

        assert store.get_run(run_id) is None

    # =========================================================================
    # Context Manager Tests
    # =========================================================================

    def test_context_manager(self) -> None:
        """Test using store as context manager."""
        with SQLiteExperimentStore(":memory:") as store:
            exp_id = store.create_experiment(name="test")
            assert store.get_experiment(exp_id) is not None
