"""
Cost estimation for LLM API usage.

This module provides the CostEstimator class for estimating
costs before running generation.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from persona.core.cost.pricing import PricingData, ModelPricing


@dataclass
class CostEstimate:
    """
    Cost estimation result.

    Attributes:
        model: Model used for estimation.
        provider: Provider name.
        input_tokens: Estimated input tokens.
        output_tokens: Estimated output tokens.
        input_cost: Cost for input tokens (USD).
        output_cost: Cost for output tokens (USD).
        total_cost: Total estimated cost (USD).
        pricing: The pricing data used.
    """

    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    input_cost: Decimal
    output_cost: Decimal
    total_cost: Decimal
    pricing: ModelPricing | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "provider": self.provider,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "input_cost_usd": float(self.input_cost),
            "output_cost_usd": float(self.output_cost),
            "total_cost_usd": float(self.total_cost),
        }


class CostEstimator:
    """
    Estimates costs for LLM API usage.

    Provides cost estimates based on token counts and model pricing.
    Useful for previewing costs before running expensive operations.

    Example:
        estimator = CostEstimator()
        estimate = estimator.estimate(
            model="claude-sonnet-4-20250514",
            input_tokens=5000,
            output_tokens=2000,
        )
        print(f"Estimated cost: ${estimate.total_cost:.4f}")
    """

    # Default output token estimates per persona
    DEFAULT_OUTPUT_PER_PERSONA = 800

    def __init__(self) -> None:
        """Initialise the cost estimator."""
        self._pricing = PricingData()

    def estimate(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int | None = None,
        provider: str | None = None,
        persona_count: int = 3,
    ) -> CostEstimate:
        """
        Estimate cost for a generation run.

        Args:
            model: Model identifier.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens (estimated if not provided).
            provider: Provider name hint.
            persona_count: Number of personas to generate (for output estimation).

        Returns:
            CostEstimate with detailed breakdown.
        """
        # Get pricing data
        pricing = PricingData.get_pricing(model, provider)

        # Estimate output tokens if not provided
        if output_tokens is None:
            output_tokens = self._estimate_output_tokens(persona_count)

        # Calculate costs
        if pricing:
            input_cost = (Decimal(input_tokens) / Decimal(1_000_000)) * pricing.input_price
            output_cost = (Decimal(output_tokens) / Decimal(1_000_000)) * pricing.output_price
            total_cost = input_cost + output_cost
            provider_name = pricing.provider
        else:
            # Unknown model - use default pricing
            input_cost = Decimal("0")
            output_cost = Decimal("0")
            total_cost = Decimal("0")
            provider_name = provider or "unknown"

        return CostEstimate(
            model=model,
            provider=provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            pricing=pricing,
        )

    def estimate_from_data(
        self,
        data: str,
        model: str,
        provider: str | None = None,
        persona_count: int = 3,
    ) -> CostEstimate:
        """
        Estimate cost from raw data content.

        Args:
            data: The data content to be processed.
            model: Model to use for estimation.
            provider: Provider name hint.
            persona_count: Number of personas to generate.

        Returns:
            CostEstimate for processing this data.
        """
        from persona.core.data import DataLoader

        loader = DataLoader()
        input_tokens = loader.count_tokens(data)

        return self.estimate(
            model=model,
            input_tokens=input_tokens,
            provider=provider,
            persona_count=persona_count,
        )

    def compare_models(
        self,
        input_tokens: int,
        output_tokens: int | None = None,
        persona_count: int = 3,
        provider: str | None = None,
    ) -> list[CostEstimate]:
        """
        Compare costs across multiple models.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens (estimated if not provided).
            persona_count: Number of personas (for output estimation).
            provider: Filter by specific provider.

        Returns:
            List of CostEstimate sorted by total cost (lowest first).
        """
        models = PricingData.list_models(provider)
        estimates = []

        for pricing in models:
            estimate = self.estimate(
                model=pricing.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                persona_count=persona_count,
            )
            estimates.append(estimate)

        # Sort by total cost
        estimates.sort(key=lambda e: e.total_cost)
        return estimates

    def _estimate_output_tokens(self, persona_count: int) -> int:
        """
        Estimate output tokens based on persona count.

        Args:
            persona_count: Number of personas to generate.

        Returns:
            Estimated output token count.
        """
        # Base overhead for JSON structure and metadata
        base_tokens = 200
        # Tokens per persona
        per_persona = self.DEFAULT_OUTPUT_PER_PERSONA

        return base_tokens + (per_persona * persona_count)

    def format_cost(self, cost: Decimal, currency: str = "USD") -> str:
        """
        Format a cost value for display.

        Args:
            cost: Cost value.
            currency: Currency code.

        Returns:
            Formatted cost string.
        """
        if currency == "USD":
            return f"${cost:.4f}"
        return f"{cost:.4f} {currency}"
