"""Tests for multi-model cost estimation (F-071)."""

import pytest

from persona.core.multimodel.generator import ModelSpec
from persona.core.multimodel.cost import (
    ModelCostDetail,
    MultiModelCostBreakdown,
    MultiModelCostEstimator,
    estimate_multi_model_cost,
)


class TestModelCostDetail:
    """Tests for ModelCostDetail."""

    def test_to_dict(self):
        """Converts to dictionary."""
        detail = ModelCostDetail(
            provider="anthropic",
            model="claude-sonnet-4",
            tokens_input=50000,
            tokens_output=2400,
            cost_input=0.15,
            cost_output=0.036,
            total_cost=0.186,
        )
        data = detail.to_dict()

        assert data["provider"] == "anthropic"
        assert data["model"] == "claude-sonnet-4"
        assert data["tokens_input"] == 50000
        assert data["total_cost"] == 0.186


class TestMultiModelCostBreakdown:
    """Tests for MultiModelCostBreakdown."""

    def test_to_dict(self):
        """Converts to dictionary."""
        breakdown = MultiModelCostBreakdown(
            subtotal=0.50,
            mode_overhead=0.05,
            total_cost=0.55,
            execution_mode="sequential",
            within_budget=True,
        )
        data = breakdown.to_dict()

        assert data["subtotal"] == 0.50
        assert data["mode_overhead"] == 0.05
        assert data["execution_mode"] == "sequential"

    def test_to_display(self):
        """Generates display output."""
        breakdown = MultiModelCostBreakdown(
            model_costs=[
                ModelCostDetail(
                    provider="anthropic",
                    model="claude-sonnet-4",
                    tokens_input=50000,
                    tokens_output=2400,
                    cost_input=0.15,
                    cost_output=0.036,
                    total_cost=0.186,
                ),
            ],
            subtotal=0.186,
            total_cost=0.186,
            execution_mode="parallel",
            comparison_single_model=0.186,
            overhead_percentage=0.0,
        )
        display = breakdown.to_display()

        assert "Multi-Model Cost" in display
        assert "parallel" in display
        assert "claude-sonnet-4" in display

    def test_to_display_with_budget(self):
        """Shows budget status in display."""
        breakdown = MultiModelCostBreakdown(
            model_costs=[],
            total_cost=0.50,
            budget_limit=1.00,
            within_budget=True,
        )
        display = breakdown.to_display()

        assert "Within" in display or "Budget" in display


class TestMultiModelCostEstimator:
    """Tests for MultiModelCostEstimator."""

    def test_estimate_single_model(self):
        """Estimates cost for single model."""
        estimator = MultiModelCostEstimator()
        models = [ModelSpec("anthropic", "claude-sonnet-4-20250514")]

        result = estimator.estimate(
            models=models,
            input_tokens=50000,
            persona_count=3,
            mode="parallel",
        )

        assert len(result.model_costs) == 1
        assert result.total_cost > 0
        assert result.execution_mode == "parallel"

    def test_estimate_multiple_models(self):
        """Estimates cost for multiple models."""
        estimator = MultiModelCostEstimator()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4-20250514"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = estimator.estimate(
            models=models,
            input_tokens=50000,
            persona_count=3,
        )

        assert len(result.model_costs) == 2
        assert result.subtotal > 0
        assert result.total_cost >= result.subtotal

    def test_estimate_parallel_no_overhead(self):
        """Parallel mode has no overhead."""
        estimator = MultiModelCostEstimator()
        models = [ModelSpec("anthropic", "claude-sonnet-4-20250514")]

        result = estimator.estimate(
            models=models,
            input_tokens=50000,
            mode="parallel",
        )

        assert result.mode_overhead == 0.0
        assert result.subtotal == result.total_cost

    def test_estimate_sequential_overhead(self):
        """Sequential mode has 5% overhead."""
        estimator = MultiModelCostEstimator()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4-20250514"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = estimator.estimate(
            models=models,
            input_tokens=50000,
            mode="sequential",
        )

        expected_overhead = result.subtotal * 0.05
        assert abs(result.mode_overhead - expected_overhead) < 0.0001

    def test_estimate_consensus_overhead(self):
        """Consensus mode has 15% overhead."""
        estimator = MultiModelCostEstimator()
        models = [ModelSpec("anthropic", "claude-sonnet-4-20250514")]

        result = estimator.estimate(
            models=models,
            input_tokens=50000,
            mode="consensus",
        )

        expected_overhead = result.subtotal * 0.15
        assert abs(result.mode_overhead - expected_overhead) < 0.0001

    def test_estimate_comparison_cheapest(self):
        """Provides comparison to cheapest single model."""
        estimator = MultiModelCostEstimator()
        models = [
            ModelSpec("anthropic", "claude-opus-4-5-20251101"),  # Expensive
            ModelSpec("openai", "gpt-4o-mini"),  # Cheap
        ]

        result = estimator.estimate(
            models=models,
            input_tokens=50000,
        )

        # Comparison should be the mini model cost
        assert result.comparison_single_model < result.subtotal

    def test_estimate_budget_within(self):
        """Detects when within budget."""
        estimator = MultiModelCostEstimator(budget_limit=10.00)
        models = [ModelSpec("anthropic", "claude-sonnet-4-20250514")]

        result = estimator.estimate(
            models=models,
            input_tokens=10000,  # Small input
        )

        assert result.within_budget is True
        assert result.budget_limit == 10.00

    def test_estimate_budget_exceeded(self):
        """Detects when budget exceeded."""
        estimator = MultiModelCostEstimator(budget_limit=0.0001)
        models = [ModelSpec("anthropic", "claude-opus-4-5-20251101")]

        result = estimator.estimate(
            models=models,
            input_tokens=1000000,  # Large input
        )

        assert result.within_budget is False

    def test_estimate_unknown_model_uses_default(self):
        """Unknown models use default pricing."""
        estimator = MultiModelCostEstimator()
        models = [ModelSpec("anthropic", "unknown-model-xyz")]

        result = estimator.estimate(
            models=models,
            input_tokens=50000,
        )

        # Should not fail, uses default pricing
        assert result.total_cost > 0

    def test_estimate_overhead_percentage(self):
        """Calculates overhead percentage vs single model."""
        estimator = MultiModelCostEstimator()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4-20250514"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = estimator.estimate(
            models=models,
            input_tokens=50000,
            mode="parallel",
        )

        # Overhead = (total - cheapest) / cheapest * 100
        assert result.overhead_percentage >= 0

    def test_estimate_from_data(self):
        """Estimates from source data string."""
        estimator = MultiModelCostEstimator()
        models = [ModelSpec("anthropic", "claude-sonnet-4-20250514")]
        data = "This is sample data with about ten words here for testing purposes."

        result = estimator.estimate_from_data(
            models=models,
            data=data,
            persona_count=3,
        )

        assert result.total_cost > 0
        assert result.model_costs[0].tokens_input > 0

    def test_custom_tokens_per_persona(self):
        """Respects custom tokens per persona setting."""
        estimator = MultiModelCostEstimator(tokens_per_persona=1000)
        models = [ModelSpec("anthropic", "claude-sonnet-4-20250514")]

        result = estimator.estimate(
            models=models,
            input_tokens=50000,
            persona_count=5,
        )

        # 5 personas * 1000 tokens = 5000 output tokens
        assert result.model_costs[0].tokens_output == 5000


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_estimate_multi_model_cost(self):
        """estimate_multi_model_cost convenience function works."""
        models = [
            ModelSpec("anthropic", "claude-sonnet-4-20250514"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = estimate_multi_model_cost(
            models=models,
            input_tokens=50000,
            persona_count=3,
            mode="parallel",
        )

        assert isinstance(result, MultiModelCostBreakdown)
        assert len(result.model_costs) == 2

    def test_estimate_multi_model_cost_with_budget(self):
        """estimate_multi_model_cost accepts budget limit."""
        models = [ModelSpec("anthropic", "claude-sonnet-4-20250514")]

        result = estimate_multi_model_cost(
            models=models,
            input_tokens=50000,
            budget_limit=5.00,
        )

        assert result.budget_limit == 5.00
