"""Tests for cost tracking (F-078)."""

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest
from persona.core.logging.cost_tracker import (
    BudgetConfig,
    BudgetStatus,
    CostRecord,
    CostSummary,
    CostTracker,
    track_cost,
)


class TestBudgetConfig:
    """Tests for BudgetConfig dataclass."""

    def test_create_budget_config(self) -> None:
        """Can create a budget config."""
        config = BudgetConfig(
            daily=10.00,
            weekly=50.00,
            monthly=150.00,
        )

        assert config.daily == 10.00
        assert config.weekly == 50.00
        assert config.monthly == 150.00

    def test_defaults(self) -> None:
        """Has sensible defaults."""
        config = BudgetConfig()

        assert config.daily is None
        assert config.weekly is None
        assert config.monthly is None
        assert config.warn_threshold == 0.8
        assert config.block_threshold == 1.0

    def test_custom_thresholds(self) -> None:
        """Can set custom thresholds."""
        config = BudgetConfig(
            daily=10.00,
            warn_threshold=0.7,
            block_threshold=0.9,
        )

        assert config.warn_threshold == 0.7
        assert config.block_threshold == 0.9

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        config = BudgetConfig(
            daily=10.00,
            weekly=50.00,
        )

        result = config.to_dict()

        assert result["daily"] == 10.00
        assert result["weekly"] == 50.00
        assert result["monthly"] is None

    def test_from_dict(self) -> None:
        """Can create from dict."""
        data = {
            "daily": 15.00,
            "weekly": 75.00,
            "warn_threshold": 0.75,
        }

        config = BudgetConfig.from_dict(data)

        assert config.daily == 15.00
        assert config.weekly == 75.00
        assert config.warn_threshold == 0.75


class TestCostRecord:
    """Tests for CostRecord dataclass."""

    def test_create_cost_record(self) -> None:
        """Can create a cost record."""
        record = CostRecord(
            timestamp="2025-01-01T00:00:00+00:00",
            experiment_id="exp-123",
            run_id="run-456",
            estimated_cost=0.50,
            actual_cost=0.45,
        )

        assert record.timestamp == "2025-01-01T00:00:00+00:00"
        assert record.experiment_id == "exp-123"
        assert record.run_id == "run-456"
        assert record.estimated_cost == 0.50
        assert record.actual_cost == 0.45

    def test_variance_calculated_on_init(self) -> None:
        """Variance is calculated automatically."""
        record = CostRecord(
            timestamp="2025-01-01T00:00:00+00:00",
            experiment_id="exp-123",
            run_id="run-456",
            estimated_cost=0.50,
            actual_cost=0.45,
        )

        assert record.variance == pytest.approx(-0.05)  # actual - estimated
        assert record.variance_percent == pytest.approx(-10.0)

    def test_variance_percent_with_zero_estimate(self) -> None:
        """Variance percent is 0 when estimate is 0."""
        record = CostRecord(
            timestamp="2025-01-01T00:00:00+00:00",
            experiment_id="exp-123",
            run_id="run-456",
            estimated_cost=0.0,
            actual_cost=0.10,
        )

        assert record.variance_percent == 0.0

    def test_defaults(self) -> None:
        """Has sensible defaults."""
        record = CostRecord(
            timestamp="2025-01-01T00:00:00+00:00",
            experiment_id="exp-123",
            run_id="run-456",
            estimated_cost=0.50,
            actual_cost=0.50,
        )

        assert record.model == ""
        assert record.provider == ""
        assert record.input_tokens == 0
        assert record.output_tokens == 0
        assert record.breakdown == {}

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        record = CostRecord(
            timestamp="2025-01-01T00:00:00+00:00",
            experiment_id="exp-123",
            run_id="run-456",
            estimated_cost=0.50,
            actual_cost=0.45,
            model="claude",
            provider="anthropic",
            input_tokens=10000,
            output_tokens=2000,
            breakdown={"generation": 0.40, "validation": 0.05},
        )

        result = record.to_dict()

        assert result["timestamp"] == "2025-01-01T00:00:00+00:00"
        assert result["experiment_id"] == "exp-123"
        assert result["costs"]["estimated_before"] == 0.50
        assert result["costs"]["actual"] == 0.45
        assert result["costs"]["variance"] == pytest.approx(-0.05)
        assert result["model"] == "claude"
        assert result["tokens"]["input"] == 10000

    def test_to_json(self) -> None:
        """Can serialize to JSON."""
        record = CostRecord(
            timestamp="2025-01-01T00:00:00+00:00",
            experiment_id="exp-123",
            run_id="run-456",
            estimated_cost=0.50,
            actual_cost=0.48,
        )

        json_str = record.to_json()
        parsed = json.loads(json_str)

        assert parsed["experiment_id"] == "exp-123"
        assert parsed["costs"]["actual"] == 0.48


class TestBudgetStatus:
    """Tests for BudgetStatus dataclass."""

    def test_create_budget_status(self) -> None:
        """Can create budget status."""
        status = BudgetStatus(
            period="daily",
            limit=10.00,
            used=8.50,
            remaining=1.50,
            percent_used=85.0,
            status="warning",
        )

        assert status.period == "daily"
        assert status.limit == 10.00
        assert status.used == 8.50
        assert status.remaining == 1.50
        assert status.percent_used == 85.0
        assert status.status == "warning"

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        status = BudgetStatus(
            period="weekly",
            limit=50.00,
            used=25.00,
            remaining=25.00,
            percent_used=50.0,
            status="ok",
        )

        result = status.to_dict()

        assert result["period"] == "weekly"
        assert result["limit"] == 50.00
        assert result["status"] == "ok"


class TestCostSummary:
    """Tests for CostSummary dataclass."""

    def test_create_summary(self) -> None:
        """Can create cost summary."""
        summary = CostSummary(
            experiment_id="exp-123",
            total_runs=5,
            total_estimated=2.50,
            total_actual=2.35,
            total_variance=-0.15,
            average_per_run=0.47,
        )

        assert summary.experiment_id == "exp-123"
        assert summary.total_runs == 5
        assert summary.total_actual == 2.35

    def test_defaults(self) -> None:
        """Has sensible defaults."""
        summary = CostSummary(experiment_id="exp-123")

        assert summary.total_runs == 0
        assert summary.total_estimated == 0.0
        assert summary.total_actual == 0.0
        assert summary.by_model == {}
        assert summary.budget_status == []

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        summary = CostSummary(
            experiment_id="exp-123",
            total_runs=3,
            total_actual=1.50,
            by_model={"claude": 1.00, "gpt-4": 0.50},
        )

        result = summary.to_dict()

        assert result["experiment_id"] == "exp-123"
        assert result["total_runs"] == 3
        assert result["by_model"]["claude"] == 1.00

    def test_to_display(self) -> None:
        """Can generate display output."""
        summary = CostSummary(
            experiment_id="exp-123",
            total_runs=3,
            total_estimated=1.50,
            total_actual=1.45,
            total_variance=-0.05,
            average_per_run=0.48,
            budget_status=[
                BudgetStatus(
                    period="daily",
                    limit=10.00,
                    used=1.45,
                    remaining=8.55,
                    percent_used=14.5,
                    status="ok",
                )
            ],
        )

        display = summary.to_display()

        assert "Cost Report" in display
        assert "Estimated" in display
        assert "Actual" in display
        assert "Budget Status" in display


class TestCostTracker:
    """Tests for CostTracker class."""

    def test_create_tracker(self) -> None:
        """Can create a cost tracker."""
        tracker = CostTracker()

        assert tracker.budget is not None

    def test_create_with_budget(self) -> None:
        """Can create tracker with budget."""
        budget = BudgetConfig(daily=10.00)
        tracker = CostTracker(budget=budget)

        assert tracker.budget.daily == 10.00

    def test_record_cost(self) -> None:
        """Can record a cost event."""
        tracker = CostTracker()

        record = tracker.record(
            experiment_id="exp-123",
            run_id="run-456",
            estimated=0.50,
            actual=0.48,
            model="claude",
            provider="anthropic",
            input_tokens=10000,
            output_tokens=2000,
        )

        assert record.experiment_id == "exp-123"
        assert record.run_id == "run-456"
        assert record.estimated_cost == 0.50
        assert record.actual_cost == 0.48
        assert record.model == "claude"

    def test_record_with_breakdown(self) -> None:
        """Can record cost with breakdown."""
        tracker = CostTracker()

        record = tracker.record(
            experiment_id="exp-123",
            run_id="run-456",
            estimated=0.50,
            actual=0.48,
            breakdown={"generation": 0.40, "validation": 0.08},
        )

        assert record.breakdown["generation"] == 0.40
        assert record.breakdown["validation"] == 0.08

    def test_get_records(self) -> None:
        """Can retrieve recorded costs."""
        tracker = CostTracker()

        tracker.record(
            experiment_id="exp-123", run_id="run-1", estimated=0.50, actual=0.48
        )
        tracker.record(
            experiment_id="exp-123", run_id="run-2", estimated=0.50, actual=0.52
        )
        tracker.record(
            experiment_id="exp-456", run_id="run-3", estimated=0.50, actual=0.49
        )

        all_records = tracker.get_records()
        assert len(all_records) == 3

        exp_123_records = tracker.get_records(experiment_id="exp-123")
        assert len(exp_123_records) == 2

    def test_get_summary(self) -> None:
        """Can get cost summary."""
        tracker = CostTracker()

        tracker.record(
            experiment_id="exp-123",
            run_id="run-1",
            estimated=0.50,
            actual=0.48,
            model="claude",
        )
        tracker.record(
            experiment_id="exp-123",
            run_id="run-2",
            estimated=0.50,
            actual=0.52,
            model="claude",
        )
        tracker.record(
            experiment_id="exp-123",
            run_id="run-3",
            estimated=0.40,
            actual=0.38,
            model="gpt-4",
        )

        summary = tracker.get_summary(experiment_id="exp-123")

        assert summary.total_runs == 3
        assert summary.total_estimated == 1.40
        assert summary.total_actual == 1.38
        assert summary.by_model["claude"] == 1.00
        assert summary.by_model["gpt-4"] == 0.38

    def test_get_summary_all_experiments(self) -> None:
        """Can get summary for all experiments."""
        tracker = CostTracker()

        tracker.record(
            experiment_id="exp-123", run_id="run-1", estimated=0.50, actual=0.48
        )
        tracker.record(
            experiment_id="exp-456", run_id="run-2", estimated=0.50, actual=0.52
        )

        summary = tracker.get_summary()

        assert summary.total_runs == 2
        assert summary.total_actual == 1.00

    def test_get_summary_empty(self) -> None:
        """Summary handles no records."""
        budget = BudgetConfig(daily=10.00)
        tracker = CostTracker(budget=budget)

        summary = tracker.get_summary(experiment_id="nonexistent")

        assert summary.total_runs == 0
        assert summary.total_actual == 0.0

    def test_check_budget_daily(self) -> None:
        """Can check daily budget status."""
        budget = BudgetConfig(daily=10.00, warn_threshold=0.8)
        tracker = CostTracker(budget=budget)

        # Record some costs
        tracker.record(
            experiment_id="exp-123", run_id="run-1", estimated=8.00, actual=8.50
        )

        statuses = tracker.check_budget()

        # Should have daily status
        daily_status = next((s for s in statuses if s.period == "daily"), None)
        assert daily_status is not None
        assert daily_status.used == 8.50
        assert daily_status.status == "warning"  # 85% > 80% threshold

    def test_check_budget_exceeded(self) -> None:
        """Budget exceeded when over 100%."""
        budget = BudgetConfig(daily=10.00)
        tracker = CostTracker(budget=budget)

        tracker.record(
            experiment_id="exp-123", run_id="run-1", estimated=10.00, actual=11.00
        )

        statuses = tracker.check_budget()

        daily_status = next((s for s in statuses if s.period == "daily"), None)
        assert daily_status is not None
        assert daily_status.status == "exceeded"

    def test_check_budget_ok(self) -> None:
        """Budget ok when under warning threshold."""
        budget = BudgetConfig(daily=10.00, warn_threshold=0.8)
        tracker = CostTracker(budget=budget)

        tracker.record(
            experiment_id="exp-123", run_id="run-1", estimated=5.00, actual=5.00
        )

        statuses = tracker.check_budget()

        daily_status = next((s for s in statuses if s.period == "daily"), None)
        assert daily_status is not None
        assert daily_status.status == "ok"  # 50% < 80%

    def test_should_block(self) -> None:
        """should_block returns True when exceeded."""
        budget = BudgetConfig(daily=10.00)
        tracker = CostTracker(budget=budget)

        assert tracker.should_block() is False

        tracker.record(
            experiment_id="exp-123", run_id="run-1", estimated=10.00, actual=11.00
        )

        assert tracker.should_block() is True

    def test_should_warn(self) -> None:
        """should_warn returns True at warning level."""
        budget = BudgetConfig(daily=10.00, warn_threshold=0.8)
        tracker = CostTracker(budget=budget)

        assert tracker.should_warn() is False

        tracker.record(
            experiment_id="exp-123", run_id="run-1", estimated=8.50, actual=8.50
        )

        assert tracker.should_warn() is True

    def test_persistence_to_file(self) -> None:
        """Tracker persists records to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "costs.jsonl"

            tracker = CostTracker(storage_path=storage_path)
            tracker.record(
                experiment_id="exp-123", run_id="run-1", estimated=0.50, actual=0.48
            )
            tracker.record(
                experiment_id="exp-123", run_id="run-2", estimated=0.50, actual=0.52
            )

            assert storage_path.exists()

            lines = storage_path.read_text().strip().split("\n")
            assert len(lines) == 2

            for line in lines:
                data = json.loads(line)
                assert "experiment_id" in data
                assert "costs" in data

    def test_load_history_from_file(self) -> None:
        """Tracker loads history from existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "costs.jsonl"

            # Create initial tracker and record costs
            tracker1 = CostTracker(storage_path=storage_path)
            tracker1.record(
                experiment_id="exp-123", run_id="run-1", estimated=0.50, actual=0.48
            )
            tracker1.record(
                experiment_id="exp-123", run_id="run-2", estimated=0.50, actual=0.52
            )

            # Create new tracker and load history
            tracker2 = CostTracker(storage_path=storage_path)

            records = tracker2.get_records()
            assert len(records) == 2


class TestTrackCostConvenience:
    """Tests for track_cost convenience function."""

    def test_creates_cost_record(self) -> None:
        """track_cost creates a CostRecord."""
        record = track_cost(
            experiment_id="exp-123",
            run_id="run-456",
            estimated=0.50,
            actual=0.48,
        )

        assert isinstance(record, CostRecord)
        assert record.experiment_id == "exp-123"
        assert record.run_id == "run-456"
        assert record.estimated_cost == 0.50
        assert record.actual_cost == 0.48

    def test_timestamp_is_generated(self) -> None:
        """Timestamp is automatically generated."""
        record = track_cost(
            experiment_id="exp-123",
            run_id="run-456",
            estimated=0.50,
            actual=0.48,
        )

        # Verify timestamp is recent (within last minute)
        timestamp = datetime.fromisoformat(record.timestamp.replace("Z", "+00:00"))
        now = datetime.now(UTC)
        diff = (now - timestamp).total_seconds()
        assert diff < 60
