"""
Tests for cost estimation functionality (F-007, F-014).
"""

import pytest
from decimal import Decimal

from persona.core.cost import CostEstimator, PricingData, ModelPricing


class TestModelPricing:
    """Tests for ModelPricing dataclass."""

    def test_create_pricing(self):
        """Test creating pricing data."""
        pricing = ModelPricing(
            model="test-model",
            provider="test",
            input_price=Decimal("3.00"),
            output_price=Decimal("15.00"),
            context_window=200_000,
            description="Test model",
        )

        assert pricing.model == "test-model"
        assert pricing.input_price == Decimal("3.00")
        assert pricing.output_price == Decimal("15.00")

    def test_estimate_cost(self):
        """Test cost estimation from pricing."""
        pricing = ModelPricing(
            model="test",
            provider="test",
            input_price=Decimal("3.00"),  # $3 per million
            output_price=Decimal("15.00"),  # $15 per million
        )

        # 1000 input tokens = $0.003
        # 500 output tokens = $0.0075
        cost = pricing.estimate_cost(input_tokens=1000, output_tokens=500)

        assert cost == Decimal("0.0105")

    def test_estimate_cost_large(self):
        """Test cost estimation with larger token counts."""
        pricing = ModelPricing(
            model="test",
            provider="test",
            input_price=Decimal("1.00"),
            output_price=Decimal("5.00"),
        )

        # 1 million tokens each
        cost = pricing.estimate_cost(input_tokens=1_000_000, output_tokens=1_000_000)

        assert cost == Decimal("6.00")


class TestPricingData:
    """Tests for PricingData class."""

    def test_anthropic_models_exist(self):
        """Test that Anthropic models are defined."""
        models = PricingData.list_models("anthropic")

        assert len(models) > 0
        assert any("claude" in m.model for m in models)

    def test_openai_models_exist(self):
        """Test that OpenAI models are defined."""
        models = PricingData.list_models("openai")

        assert len(models) > 0
        assert any("gpt" in m.model for m in models)

    def test_gemini_models_exist(self):
        """Test that Gemini models are defined."""
        models = PricingData.list_models("gemini")

        assert len(models) > 0
        assert any("gemini" in m.model for m in models)

    def test_get_pricing_by_model(self):
        """Test getting pricing by model name."""
        pricing = PricingData.get_pricing("gpt-4o")

        assert pricing is not None
        assert pricing.model == "gpt-4o"
        assert pricing.provider == "openai"

    def test_get_pricing_with_provider_hint(self):
        """Test getting pricing with provider hint."""
        pricing = PricingData.get_pricing("claude-sonnet-4-20250514", provider="anthropic")

        assert pricing is not None
        assert pricing.provider == "anthropic"

    def test_get_pricing_unknown_model(self):
        """Test getting pricing for unknown model."""
        pricing = PricingData.get_pricing("nonexistent-model")

        assert pricing is None

    def test_list_all_models(self):
        """Test listing all models."""
        models = PricingData.list_models()

        assert len(models) > 10  # Should have many models
        providers = {m.provider for m in models}
        assert "anthropic" in providers
        assert "openai" in providers
        assert "gemini" in providers

    def test_model_has_context_window(self):
        """Test that models have context window info."""
        pricing = PricingData.get_pricing("claude-sonnet-4-20250514")

        assert pricing is not None
        assert pricing.context_window > 0


class TestCostEstimator:
    """Tests for CostEstimator class."""

    def test_estimate_known_model(self):
        """Test estimating cost for known model."""
        estimator = CostEstimator()
        estimate = estimator.estimate(
            model="claude-sonnet-4-20250514",
            input_tokens=10_000,
            output_tokens=2_000,
        )

        assert estimate.model == "claude-sonnet-4-20250514"
        assert estimate.input_tokens == 10_000
        assert estimate.output_tokens == 2_000
        assert estimate.total_cost > 0
        assert estimate.pricing is not None

    def test_estimate_unknown_model(self):
        """Test estimating cost for unknown model."""
        estimator = CostEstimator()
        estimate = estimator.estimate(
            model="unknown-model",
            input_tokens=1000,
            output_tokens=500,
        )

        assert estimate.model == "unknown-model"
        assert estimate.total_cost == Decimal("0")
        assert estimate.pricing is None

    def test_estimate_auto_output_tokens(self):
        """Test automatic output token estimation."""
        estimator = CostEstimator()
        estimate = estimator.estimate(
            model="gpt-4o",
            input_tokens=5000,
            persona_count=5,
        )

        # Should estimate output tokens based on persona count
        assert estimate.output_tokens > 0
        assert estimate.output_tokens > 5 * 500  # At least some per persona

    def test_compare_models(self):
        """Test comparing costs across models."""
        estimator = CostEstimator()
        estimates = estimator.compare_models(
            input_tokens=10_000,
            output_tokens=2_000,
        )

        assert len(estimates) > 5
        # Should be sorted by cost
        costs = [e.total_cost for e in estimates]
        assert costs == sorted(costs)

    def test_compare_models_single_provider(self):
        """Test comparing costs within single provider."""
        estimator = CostEstimator()
        estimates = estimator.compare_models(
            input_tokens=10_000,
            output_tokens=2_000,
            provider="anthropic",
        )

        assert len(estimates) > 0
        assert all(e.provider == "anthropic" for e in estimates)

    def test_format_cost(self):
        """Test cost formatting."""
        estimator = CostEstimator()

        formatted = estimator.format_cost(Decimal("0.0523"))
        assert formatted == "$0.0523"

        formatted = estimator.format_cost(Decimal("1.50"))
        assert formatted == "$1.5000"

    def test_estimate_to_dict(self):
        """Test estimate serialisation."""
        estimator = CostEstimator()
        estimate = estimator.estimate(
            model="gpt-4o-mini",
            input_tokens=1000,
            output_tokens=500,
        )

        data = estimate.to_dict()

        assert data["model"] == "gpt-4o-mini"
        assert data["input_tokens"] == 1000
        assert data["output_tokens"] == 500
        assert "total_cost_usd" in data
        assert isinstance(data["total_cost_usd"], float)

    def test_estimate_from_data(self):
        """Test estimating from raw data."""
        estimator = CostEstimator()
        data = "This is some test data " * 100

        estimate = estimator.estimate_from_data(
            data=data,
            model="claude-3-5-haiku-20241022",
            persona_count=3,
        )

        assert estimate.input_tokens > 0
        assert estimate.output_tokens > 0
        assert estimate.total_cost > 0


class TestCostCalculations:
    """Tests for specific cost calculations."""

    def test_claude_sonnet_cost(self):
        """Test Claude Sonnet pricing calculation."""
        pricing = PricingData.get_pricing("claude-sonnet-4-20250514")
        assert pricing is not None

        # 10k input, 2k output
        cost = pricing.estimate_cost(10_000, 2_000)

        # Expected: (10000/1M * 3) + (2000/1M * 15) = 0.03 + 0.03 = 0.06
        assert cost == Decimal("0.06")

    def test_gpt4o_mini_cost(self):
        """Test GPT-4o-mini pricing calculation."""
        pricing = PricingData.get_pricing("gpt-4o-mini")
        assert pricing is not None

        # 10k input, 2k output
        cost = pricing.estimate_cost(10_000, 2_000)

        # Expected: (10000/1M * 0.15) + (2000/1M * 0.60) = 0.0015 + 0.0012 = 0.0027
        assert cost == Decimal("0.0027")

    def test_gemini_flash_cost(self):
        """Test Gemini Flash pricing calculation."""
        pricing = PricingData.get_pricing("gemini-2.0-flash")
        assert pricing is not None

        # 10k input, 2k output
        cost = pricing.estimate_cost(10_000, 2_000)

        # Expected: (10000/1M * 0.10) + (2000/1M * 0.40) = 0.001 + 0.0008 = 0.0018
        assert cost == Decimal("0.0018")
