"""
Cost tracker widget for the TUI dashboard.

This module provides widgets for tracking and displaying API costs
across generation runs.
"""

from decimal import Decimal

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Static


class CostTracker(Static):
    """
    Widget for tracking and displaying API costs.

    Shows:
    - Current session cost
    - Total historical cost
    - Cost breakdown by provider
    - Budget warnings

    Example:
        tracker = CostTracker()
        tracker.add_cost("anthropic", Decimal("0.42"))
    """

    DEFAULT_CSS = """
    CostTracker {
        height: auto;
        border: solid $primary;
        padding: 1 2;
    }

    CostTracker .title {
        text-style: bold;
        color: $accent;
    }

    CostTracker .cost-total {
        text-style: bold;
        color: $success;
        margin: 1 0;
    }

    CostTracker .cost-item {
        color: $text-muted;
    }

    CostTracker .warning {
        color: $warning;
        text-style: bold;
    }
    """

    def __init__(self) -> None:
        """Initialise the cost tracker."""
        super().__init__()
        self.session_cost = Decimal("0")
        self.total_cost = Decimal("0")
        self.costs_by_provider: dict[str, Decimal] = {}
        self.budget_limit: Decimal | None = None

    def compose(self) -> ComposeResult:
        """Compose the cost tracker layout."""
        with Vertical():
            yield Label("💰 Cost Tracker", classes="title")
            yield Label("Session: $0.00", id="session-cost", classes="cost-total")
            yield Label("Total: $0.00", id="total-cost", classes="cost-item")
            yield Label("", id="provider-breakdown", classes="cost-item")
            yield Label("", id="budget-warning", classes="warning")

    def add_cost(self, provider: str, cost: Decimal) -> None:
        """
        Add cost to the tracker.

        Args:
            provider: Provider name (e.g., "anthropic", "openai").
            cost: Cost amount in USD.
        """
        self.session_cost += cost
        self.total_cost += cost

        if provider not in self.costs_by_provider:
            self.costs_by_provider[provider] = Decimal("0")
        self.costs_by_provider[provider] += cost

        self._update_display()

    def set_budget_limit(self, limit: Decimal) -> None:
        """
        Set a budget limit for warnings.

        Args:
            limit: Budget limit in USD.
        """
        self.budget_limit = limit
        self._update_display()

    def reset_session(self) -> None:
        """Reset session costs (keeps total)."""
        self.session_cost = Decimal("0")
        self._update_display()

    def _update_display(self) -> None:
        """Update the displayed cost information."""
        # Update session cost
        session_label = self.query_one("#session-cost", Label)
        session_label.update(f"Session: ${self.session_cost:.4f}")

        # Update total cost
        total_label = self.query_one("#total-cost", Label)
        total_label.update(f"Total: ${self.total_cost:.4f}")

        # Update provider breakdown
        if self.costs_by_provider:
            breakdown = ", ".join(
                f"{p}: ${c:.2f}" for p, c in self.costs_by_provider.items()
            )
            breakdown_label = self.query_one("#provider-breakdown", Label)
            breakdown_label.update(breakdown)

        # Check budget warning
        warning_label = self.query_one("#budget-warning", Label)
        if self.budget_limit and self.session_cost >= self.budget_limit:
            warning_label.update(f"⚠️  Budget limit ${self.budget_limit} exceeded!")
        else:
            warning_label.update("")

    def get_session_cost(self) -> Decimal:
        """Get current session cost."""
        return self.session_cost

    def get_total_cost(self) -> Decimal:
        """Get total historical cost."""
        return self.total_cost

    def get_breakdown(self) -> dict[str, Decimal]:
        """Get cost breakdown by provider."""
        return self.costs_by_provider.copy()
