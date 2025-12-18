"""Multi-model cost estimation (F-071).

Provides cost estimation for multi-model generation,
including per-model breakdown and mode overhead.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelCostDetail:
    """Cost details for a single model.

    Attributes:
        provider: The LLM provider.
        model: The model identifier.
        tokens_input: Estimated input tokens.
        tokens_output: Estimated output tokens.
        cost_input: Cost for input tokens (USD).
        cost_output: Cost for output tokens (USD).
        total_cost: Total cost (USD).
    """

    provider: str
    model: str
    tokens_input: int
    tokens_output: int
    cost_input: float
    cost_output: float
    total_cost: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "model": self.model,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "cost_input": self.cost_input,
            "cost_output": self.cost_output,
            "total_cost": self.total_cost,
        }


@dataclass
class MultiModelCostBreakdown:
    """Complete cost breakdown for multi-model generation.

    Attributes:
        model_costs: Cost breakdown per model.
        subtotal: Sum of all model costs.
        mode_overhead: Additional cost from execution mode.
        total_cost: Final total cost.
        execution_mode: The execution mode used.
        comparison_single_model: Cost if using single model only.
        overhead_percentage: Overhead compared to single model.
        within_budget: Whether cost is within budget.
        budget_limit: The budget limit if set.
    """

    model_costs: list[ModelCostDetail] = field(default_factory=list)
    subtotal: float = 0.0
    mode_overhead: float = 0.0
    total_cost: float = 0.0
    execution_mode: str = "parallel"
    comparison_single_model: float = 0.0
    overhead_percentage: float = 0.0
    within_budget: bool = True
    budget_limit: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_costs": [m.to_dict() for m in self.model_costs],
            "subtotal": self.subtotal,
            "mode_overhead": self.mode_overhead,
            "total_cost": self.total_cost,
            "execution_mode": self.execution_mode,
            "comparison_single_model": self.comparison_single_model,
            "overhead_percentage": self.overhead_percentage,
            "within_budget": self.within_budget,
            "budget_limit": self.budget_limit,
        }

    def to_display(self) -> str:
        """Generate human-readable display."""
        lines = [
            "Multi-Model Cost Estimation",
            "=" * 50,
            "",
            f"Execution Mode: {self.execution_mode}",
            "",
            "Per-Model Breakdown:",
            "─" * 50,
            f"{'Model':<25} {'Input':<10} {'Output':<10} {'Cost':>8}",
            "─" * 50,
        ]

        for mc in self.model_costs:
            lines.append(
                f"{mc.model:<25} {mc.tokens_input:>7,} "
                f"{mc.tokens_output:>10,} ${mc.total_cost:>7.4f}"
            )

        lines.extend(
            [
                "─" * 50,
                f"{'Subtotal:':<47} ${self.subtotal:>7.4f}",
            ]
        )

        if self.mode_overhead > 0:
            lines.append(
                f"{'Mode Overhead (' + self.execution_mode + '):':<47} "
                f"${self.mode_overhead:>7.4f}"
            )

        lines.extend(
            [
                "─" * 50,
                f"{'Total Estimated Cost:':<47} ${self.total_cost:>7.4f}",
                "",
                "Comparison:",
                f"  Single model (cheapest): ${self.comparison_single_model:.4f}",
                f"  Multi-model overhead: +{self.overhead_percentage:.0f}%",
            ]
        )

        if self.budget_limit is not None:
            status = "✓ Within" if self.within_budget else "✗ Exceeds"
            lines.append(f"  Budget: {status} ${self.budget_limit:.2f} limit")

        return "\n".join(lines)


class MultiModelCostEstimator:
    """Estimator for multi-model generation costs.

    Calculates per-model costs, execution mode overhead,
    and provides comparisons to single-model generation.

    Example:
        >>> estimator = MultiModelCostEstimator()
        >>> breakdown = estimator.estimate(
        ...     models=[
        ...         ModelSpec("anthropic", "claude-sonnet-4"),
        ...         ModelSpec("openai", "gpt-4o"),
        ...     ],
        ...     input_tokens=50000,
        ...     persona_count=3,
        ...     mode="consensus"
        ... )
    """

    # Pricing per 1M tokens (simplified, December 2024 rates)
    PRICING = {
        "anthropic": {
            "claude-opus-4-5-20251101": {"input": 15.0, "output": 75.0},
            "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
            "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
            "claude-haiku-3-5-20241022": {"input": 0.8, "output": 4.0},
            "default": {"input": 3.0, "output": 15.0},
        },
        "openai": {
            "gpt-4o": {"input": 2.5, "output": 10.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "o1": {"input": 15.0, "output": 60.0},
            "o1-mini": {"input": 3.0, "output": 12.0},
            "default": {"input": 5.0, "output": 15.0},
        },
        "gemini": {
            "gemini-1.5-pro": {"input": 1.25, "output": 5.0},
            "gemini-1.5-flash": {"input": 0.075, "output": 0.3},
            "gemini-2.0-flash-exp": {"input": 0.1, "output": 0.4},
            "default": {"input": 0.5, "output": 2.0},
        },
    }

    # Mode overhead multipliers
    MODE_OVERHEAD = {
        "parallel": 0.0,  # No overhead
        "sequential": 0.05,  # 5% for context passing
        "consensus": 0.15,  # 15% for clustering + merge step
    }

    def __init__(
        self,
        tokens_per_persona: int = 800,
        budget_limit: float | None = None,
    ):
        """Initialise the estimator.

        Args:
            tokens_per_persona: Expected output tokens per persona.
            budget_limit: Optional budget limit in USD.
        """
        self.tokens_per_persona = tokens_per_persona
        self.budget_limit = budget_limit

    def estimate(
        self,
        models: list,
        input_tokens: int,
        persona_count: int = 3,
        mode: str = "parallel",
    ) -> MultiModelCostBreakdown:
        """Estimate costs for multi-model generation.

        Args:
            models: List of ModelSpec objects.
            input_tokens: Estimated input tokens.
            persona_count: Number of personas to generate.
            mode: Execution mode (parallel, sequential, consensus).

        Returns:
            MultiModelCostBreakdown with detailed cost information.
        """
        model_costs = []
        output_tokens = persona_count * self.tokens_per_persona

        for model in models:
            detail = self._estimate_model_cost(
                provider=model.provider,
                model=model.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )
            model_costs.append(detail)

        # Calculate subtotal
        subtotal = sum(mc.total_cost for mc in model_costs)

        # Calculate mode overhead
        overhead_rate = self.MODE_OVERHEAD.get(mode, 0.0)
        mode_overhead = subtotal * overhead_rate

        # Calculate total
        total_cost = subtotal + mode_overhead

        # Calculate comparison (cheapest single model)
        comparison_single = min(mc.total_cost for mc in model_costs)

        # Calculate overhead percentage
        if comparison_single > 0:
            overhead_pct = ((total_cost - comparison_single) / comparison_single) * 100
        else:
            overhead_pct = 0.0

        # Check budget
        within_budget = True
        if self.budget_limit is not None:
            within_budget = total_cost <= self.budget_limit

        return MultiModelCostBreakdown(
            model_costs=model_costs,
            subtotal=subtotal,
            mode_overhead=mode_overhead,
            total_cost=total_cost,
            execution_mode=mode,
            comparison_single_model=comparison_single,
            overhead_percentage=overhead_pct,
            within_budget=within_budget,
            budget_limit=self.budget_limit,
        )

    def _estimate_model_cost(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> ModelCostDetail:
        """Estimate cost for a single model."""
        # Get pricing for provider/model
        provider_pricing = self.PRICING.get(provider, {})
        model_pricing = provider_pricing.get(
            model, provider_pricing.get("default", {"input": 3.0, "output": 15.0})
        )

        # Calculate costs
        cost_input = (input_tokens / 1_000_000) * model_pricing["input"]
        cost_output = (output_tokens / 1_000_000) * model_pricing["output"]
        total_cost = cost_input + cost_output

        return ModelCostDetail(
            provider=provider,
            model=model,
            tokens_input=input_tokens,
            tokens_output=output_tokens,
            cost_input=round(cost_input, 6),
            cost_output=round(cost_output, 6),
            total_cost=round(total_cost, 6),
        )

    def estimate_from_data(
        self,
        models: list,
        data: str,
        persona_count: int = 3,
        mode: str = "parallel",
    ) -> MultiModelCostBreakdown:
        """Estimate costs from source data.

        Args:
            models: List of ModelSpec objects.
            data: Source data string.
            persona_count: Number of personas to generate.
            mode: Execution mode.

        Returns:
            MultiModelCostBreakdown with detailed cost information.
        """
        # Estimate tokens from data (rough: 1 word ≈ 1.3 tokens)
        word_count = len(data.split())
        input_tokens = int(word_count * 1.3)

        return self.estimate(models, input_tokens, persona_count, mode)


def estimate_multi_model_cost(
    models: list,
    input_tokens: int,
    persona_count: int = 3,
    mode: str = "parallel",
    budget_limit: float | None = None,
) -> MultiModelCostBreakdown:
    """Convenience function for multi-model cost estimation.

    Args:
        models: List of ModelSpec objects.
        input_tokens: Estimated input tokens.
        persona_count: Number of personas to generate.
        mode: Execution mode.
        budget_limit: Optional budget limit.

    Returns:
        MultiModelCostBreakdown with detailed cost information.
    """
    estimator = MultiModelCostEstimator(budget_limit=budget_limit)
    return estimator.estimate(models, input_tokens, persona_count, mode)
