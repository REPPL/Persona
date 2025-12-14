"""Cost tracking post-generation (F-078).

Tracks actual costs after generation, compares to estimates,
and supports budget alerts.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json


@dataclass
class BudgetConfig:
    """Budget configuration.

    Attributes:
        daily: Daily budget limit (USD).
        weekly: Weekly budget limit (USD).
        monthly: Monthly budget limit (USD).
        warn_threshold: Percentage to trigger warning (0.0-1.0).
        block_threshold: Percentage to block operations (0.0-1.0).
    """
    daily: float | None = None
    weekly: float | None = None
    monthly: float | None = None
    warn_threshold: float = 0.8
    block_threshold: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "daily": self.daily,
            "weekly": self.weekly,
            "monthly": self.monthly,
            "warn_threshold": self.warn_threshold,
            "block_threshold": self.block_threshold,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BudgetConfig":
        """Create from dictionary."""
        return cls(
            daily=data.get("daily"),
            weekly=data.get("weekly"),
            monthly=data.get("monthly"),
            warn_threshold=data.get("warn_threshold", 0.8),
            block_threshold=data.get("block_threshold", 1.0),
        )


@dataclass
class CostRecord:
    """Record of a single cost event.

    Attributes:
        timestamp: When the cost occurred.
        experiment_id: Associated experiment.
        run_id: Associated run.
        estimated_cost: Pre-generation estimate.
        actual_cost: Post-generation actual cost.
        variance: Difference (actual - estimated).
        variance_percent: Percentage variance.
        model: Model used.
        provider: Provider used.
        input_tokens: Input tokens used.
        output_tokens: Output tokens used.
        breakdown: Cost breakdown by step.
    """
    timestamp: str
    experiment_id: str
    run_id: str
    estimated_cost: float
    actual_cost: float
    variance: float = 0.0
    variance_percent: float = 0.0
    model: str = ""
    provider: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    breakdown: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Calculate variance fields."""
        self.variance = self.actual_cost - self.estimated_cost
        if self.estimated_cost > 0:
            self.variance_percent = (self.variance / self.estimated_cost) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "costs": {
                "estimated_before": self.estimated_cost,
                "actual": self.actual_cost,
                "variance": self.variance,
                "variance_percent": self.variance_percent,
                "breakdown": self.breakdown,
            },
            "model": self.model,
            "provider": self.provider,
            "tokens": {
                "input": self.input_tokens,
                "output": self.output_tokens,
            },
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class BudgetStatus:
    """Current budget status.

    Attributes:
        period: Budget period (daily, weekly, monthly).
        limit: Budget limit.
        used: Amount used.
        remaining: Amount remaining.
        percent_used: Percentage used.
        status: Status (ok, warning, exceeded).
    """
    period: str
    limit: float
    used: float
    remaining: float
    percent_used: float
    status: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "period": self.period,
            "limit": self.limit,
            "used": self.used,
            "remaining": self.remaining,
            "percent_used": self.percent_used,
            "status": self.status,
        }


@dataclass
class CostSummary:
    """Summary of costs for an experiment.

    Attributes:
        experiment_id: Experiment identifier.
        total_runs: Number of runs.
        total_estimated: Total estimated cost.
        total_actual: Total actual cost.
        total_variance: Total variance.
        average_per_run: Average cost per run.
        by_model: Costs by model.
        budget_status: Current budget status.
    """
    experiment_id: str
    total_runs: int = 0
    total_estimated: float = 0.0
    total_actual: float = 0.0
    total_variance: float = 0.0
    average_per_run: float = 0.0
    by_model: dict[str, float] = field(default_factory=dict)
    budget_status: list[BudgetStatus] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "experiment_id": self.experiment_id,
            "total_runs": self.total_runs,
            "total_estimated": self.total_estimated,
            "total_actual": self.total_actual,
            "total_variance": self.total_variance,
            "average_per_run": self.average_per_run,
            "by_model": self.by_model,
            "budget_status": [b.to_dict() for b in self.budget_status],
        }

    def to_display(self) -> str:
        """Generate human-readable display."""
        lines = [
            "Cost Report",
            "=" * 50,
            "",
            "This Run:",
            f"  Estimated: ${self.total_estimated:.4f}",
        ]

        if self.total_runs > 0:
            variance_sign = "+" if self.total_variance >= 0 else ""
            variance_pct = (self.total_variance / self.total_estimated * 100) if self.total_estimated > 0 else 0
            lines.append(
                f"  Actual:    ${self.total_actual:.4f} "
                f"({variance_sign}{variance_pct:.1f}%)"
            )

        if self.total_runs > 1:
            lines.extend([
                "",
                f"Experiment Total ({self.total_runs} runs):",
                f"  Total cost: ${self.total_actual:.4f}",
                f"  Average per run: ${self.average_per_run:.4f}",
            ])

        # Budget status
        for budget in self.budget_status:
            lines.extend([
                "",
                f"Budget Status ({budget.period.title()}):",
                f"  Used: ${budget.used:.2f} / ${budget.limit:.2f} ({budget.percent_used:.1f}%)",
                f"  Remaining: ${budget.remaining:.2f}",
                "",
            ])

            # Progress bar
            filled = int(budget.percent_used / 5)
            bar = "█" * filled + "░" * (20 - filled)
            status_icon = "✓" if budget.status == "ok" else "⚠" if budget.status == "warning" else "✗"
            lines.append(f"  {status_icon} {bar} {budget.percent_used:.0f}%")

        return "\n".join(lines)


class CostTracker:
    """Tracker for post-generation costs.

    Tracks actual costs, compares to estimates, and
    manages budget alerts.

    Example:
        >>> tracker = CostTracker(budget=BudgetConfig(daily=10.00))
        >>> tracker.record(
        ...     experiment_id="exp-abc123",
        ...     run_id="run-def456",
        ...     estimated=0.45,
        ...     actual=0.42,
        ...     model="claude"
        ... )
        >>> summary = tracker.get_summary("exp-abc123")
    """

    def __init__(
        self,
        budget: BudgetConfig | None = None,
        storage_path: Path | None = None,
    ):
        """Initialise the tracker.

        Args:
            budget: Budget configuration.
            storage_path: Path to store cost history.
        """
        self.budget = budget or BudgetConfig()
        self.storage_path = storage_path
        self._records: list[CostRecord] = []
        self._cumulative_today: float = 0.0
        self._cumulative_week: float = 0.0
        self._cumulative_month: float = 0.0

        if storage_path and storage_path.exists():
            self._load_history()

    def _load_history(self) -> None:
        """Load cost history from storage."""
        if not self.storage_path:
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                for line in f:
                    data = json.loads(line)
                    # Reconstruct CostRecord
                    costs = data.get("costs", {})
                    tokens = data.get("tokens", {})
                    record = CostRecord(
                        timestamp=data["timestamp"],
                        experiment_id=data["experiment_id"],
                        run_id=data["run_id"],
                        estimated_cost=costs.get("estimated_before", 0),
                        actual_cost=costs.get("actual", 0),
                        model=data.get("model", ""),
                        provider=data.get("provider", ""),
                        input_tokens=tokens.get("input", 0),
                        output_tokens=tokens.get("output", 0),
                        breakdown=costs.get("breakdown", {}),
                    )
                    self._records.append(record)
                    self._update_cumulative(record)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _save_record(self, record: CostRecord) -> None:
        """Save a record to storage."""
        if not self.storage_path:
            return
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(record.to_json() + "\n")

    def _update_cumulative(self, record: CostRecord) -> None:
        """Update cumulative totals from a record."""
        # Simplified: add to all periods
        # Real implementation would check timestamps
        self._cumulative_today += record.actual_cost
        self._cumulative_week += record.actual_cost
        self._cumulative_month += record.actual_cost

    def record(
        self,
        experiment_id: str,
        run_id: str,
        estimated: float,
        actual: float,
        model: str = "",
        provider: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        breakdown: dict[str, float] | None = None,
    ) -> CostRecord:
        """Record a cost event.

        Args:
            experiment_id: Experiment identifier.
            run_id: Run identifier.
            estimated: Pre-generation estimate.
            actual: Post-generation actual cost.
            model: Model used.
            provider: Provider used.
            input_tokens: Input tokens.
            output_tokens: Output tokens.
            breakdown: Cost breakdown by step.

        Returns:
            Created CostRecord.
        """
        record = CostRecord(
            timestamp=datetime.now(timezone.utc).isoformat(),
            experiment_id=experiment_id,
            run_id=run_id,
            estimated_cost=estimated,
            actual_cost=actual,
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            breakdown=breakdown or {},
        )

        self._records.append(record)
        self._update_cumulative(record)
        self._save_record(record)

        return record

    def check_budget(self) -> list[BudgetStatus]:
        """Check current budget status.

        Returns:
            List of BudgetStatus for each configured period.
        """
        statuses = []

        periods = [
            ("daily", self.budget.daily, self._cumulative_today),
            ("weekly", self.budget.weekly, self._cumulative_week),
            ("monthly", self.budget.monthly, self._cumulative_month),
        ]

        for period, limit, used in periods:
            if limit is None:
                continue

            remaining = max(0, limit - used)
            percent = (used / limit) * 100 if limit > 0 else 0

            if percent >= self.budget.block_threshold * 100:
                status = "exceeded"
            elif percent >= self.budget.warn_threshold * 100:
                status = "warning"
            else:
                status = "ok"

            statuses.append(BudgetStatus(
                period=period,
                limit=limit,
                used=used,
                remaining=remaining,
                percent_used=percent,
                status=status,
            ))

        return statuses

    def should_block(self) -> bool:
        """Check if operations should be blocked due to budget.

        Returns:
            True if any budget is exceeded.
        """
        statuses = self.check_budget()
        return any(s.status == "exceeded" for s in statuses)

    def should_warn(self) -> bool:
        """Check if a budget warning should be shown.

        Returns:
            True if any budget is at warning level.
        """
        statuses = self.check_budget()
        return any(s.status in ("warning", "exceeded") for s in statuses)

    def get_records(
        self,
        experiment_id: str | None = None,
    ) -> list[CostRecord]:
        """Get cost records with optional filtering.

        Args:
            experiment_id: Filter by experiment.

        Returns:
            List of matching CostRecords.
        """
        records = self._records
        if experiment_id:
            records = [r for r in records if r.experiment_id == experiment_id]
        return records

    def get_summary(
        self,
        experiment_id: str | None = None,
    ) -> CostSummary:
        """Get cost summary for an experiment.

        Args:
            experiment_id: Experiment to summarise (or all).

        Returns:
            CostSummary with aggregated data.
        """
        records = self.get_records(experiment_id)

        if not records:
            return CostSummary(
                experiment_id=experiment_id or "",
                budget_status=self.check_budget(),
            )

        total_estimated = sum(r.estimated_cost for r in records)
        total_actual = sum(r.actual_cost for r in records)
        total_variance = total_actual - total_estimated

        by_model: dict[str, float] = {}
        for r in records:
            if r.model:
                by_model[r.model] = by_model.get(r.model, 0) + r.actual_cost

        return CostSummary(
            experiment_id=experiment_id or "",
            total_runs=len(records),
            total_estimated=total_estimated,
            total_actual=total_actual,
            total_variance=total_variance,
            average_per_run=total_actual / len(records) if records else 0,
            by_model=by_model,
            budget_status=self.check_budget(),
        )


def track_cost(
    experiment_id: str,
    run_id: str,
    estimated: float,
    actual: float,
) -> CostRecord:
    """Convenience function to track a cost.

    Args:
        experiment_id: Experiment identifier.
        run_id: Run identifier.
        estimated: Pre-generation estimate.
        actual: Post-generation actual cost.

    Returns:
        CostRecord.
    """
    return CostRecord(
        timestamp=datetime.now(timezone.utc).isoformat(),
        experiment_id=experiment_id,
        run_id=run_id,
        estimated_cost=estimated,
        actual_cost=actual,
    )
