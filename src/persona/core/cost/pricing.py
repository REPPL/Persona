"""
Pricing data for LLM models.

This module contains pricing information for various LLM providers
and their models, updated as of early 2025.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar


@dataclass(frozen=True)
class ModelPricing:
    """
    Pricing information for a single model.

    Prices are in USD per million tokens.

    Attributes:
        model: Model identifier.
        provider: Provider name.
        input_price: Cost per million input tokens.
        output_price: Cost per million output tokens.
        context_window: Maximum context window size.
        description: Human-readable model description.
    """

    model: str
    provider: str
    input_price: Decimal
    output_price: Decimal
    context_window: int = 0
    description: str = ""

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> Decimal:
        """
        Estimate cost for given token counts.

        Args:
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Estimated cost in USD.
        """
        input_cost = (Decimal(input_tokens) / Decimal(1_000_000)) * self.input_price
        output_cost = (Decimal(output_tokens) / Decimal(1_000_000)) * self.output_price
        return input_cost + output_cost


class PricingData:
    """
    Centralised pricing data for all supported models.

    Pricing is updated as of January 2025.
    """

    # Anthropic models (prices per million tokens)
    ANTHROPIC_MODELS: ClassVar[dict[str, ModelPricing]] = {
        "claude-opus-4-20250514": ModelPricing(
            model="claude-opus-4-20250514",
            provider="anthropic",
            input_price=Decimal("15.00"),
            output_price=Decimal("75.00"),
            context_window=200_000,
            description="Most capable Claude model",
        ),
        "claude-sonnet-4-20250514": ModelPricing(
            model="claude-sonnet-4-20250514",
            provider="anthropic",
            input_price=Decimal("3.00"),
            output_price=Decimal("15.00"),
            context_window=200_000,
            description="Balanced performance and cost",
        ),
        "claude-3-5-sonnet-20241022": ModelPricing(
            model="claude-3-5-sonnet-20241022",
            provider="anthropic",
            input_price=Decimal("3.00"),
            output_price=Decimal("15.00"),
            context_window=200_000,
            description="Claude 3.5 Sonnet",
        ),
        "claude-3-5-haiku-20241022": ModelPricing(
            model="claude-3-5-haiku-20241022",
            provider="anthropic",
            input_price=Decimal("1.00"),
            output_price=Decimal("5.00"),
            context_window=200_000,
            description="Fast and affordable Claude model",
        ),
        "claude-3-opus-20240229": ModelPricing(
            model="claude-3-opus-20240229",
            provider="anthropic",
            input_price=Decimal("15.00"),
            output_price=Decimal("75.00"),
            context_window=200_000,
            description="Claude 3 Opus",
        ),
        "claude-3-sonnet-20240229": ModelPricing(
            model="claude-3-sonnet-20240229",
            provider="anthropic",
            input_price=Decimal("3.00"),
            output_price=Decimal("15.00"),
            context_window=200_000,
            description="Claude 3 Sonnet",
        ),
        "claude-3-haiku-20240307": ModelPricing(
            model="claude-3-haiku-20240307",
            provider="anthropic",
            input_price=Decimal("0.25"),
            output_price=Decimal("1.25"),
            context_window=200_000,
            description="Claude 3 Haiku",
        ),
    }

    # OpenAI models (prices per million tokens)
    OPENAI_MODELS: ClassVar[dict[str, ModelPricing]] = {
        "gpt-4o": ModelPricing(
            model="gpt-4o",
            provider="openai",
            input_price=Decimal("2.50"),
            output_price=Decimal("10.00"),
            context_window=128_000,
            description="GPT-4o - Latest multimodal model",
        ),
        "gpt-4o-mini": ModelPricing(
            model="gpt-4o-mini",
            provider="openai",
            input_price=Decimal("0.15"),
            output_price=Decimal("0.60"),
            context_window=128_000,
            description="GPT-4o Mini - Fast and affordable",
        ),
        "gpt-4-turbo": ModelPricing(
            model="gpt-4-turbo",
            provider="openai",
            input_price=Decimal("10.00"),
            output_price=Decimal("30.00"),
            context_window=128_000,
            description="GPT-4 Turbo",
        ),
        "gpt-4": ModelPricing(
            model="gpt-4",
            provider="openai",
            input_price=Decimal("30.00"),
            output_price=Decimal("60.00"),
            context_window=8_192,
            description="GPT-4",
        ),
        "gpt-3.5-turbo": ModelPricing(
            model="gpt-3.5-turbo",
            provider="openai",
            input_price=Decimal("0.50"),
            output_price=Decimal("1.50"),
            context_window=16_385,
            description="GPT-3.5 Turbo",
        ),
        "o1-preview": ModelPricing(
            model="o1-preview",
            provider="openai",
            input_price=Decimal("15.00"),
            output_price=Decimal("60.00"),
            context_window=128_000,
            description="o1-preview - Advanced reasoning",
        ),
        "o1-mini": ModelPricing(
            model="o1-mini",
            provider="openai",
            input_price=Decimal("3.00"),
            output_price=Decimal("12.00"),
            context_window=128_000,
            description="o1-mini - Fast reasoning",
        ),
    }

    # Google Gemini models (prices per million tokens)
    GEMINI_MODELS: ClassVar[dict[str, ModelPricing]] = {
        "gemini-2.0-flash": ModelPricing(
            model="gemini-2.0-flash",
            provider="gemini",
            input_price=Decimal("0.10"),
            output_price=Decimal("0.40"),
            context_window=1_000_000,
            description="Gemini 2.0 Flash - Fast and efficient",
        ),
        "gemini-1.5-pro": ModelPricing(
            model="gemini-1.5-pro",
            provider="gemini",
            input_price=Decimal("1.25"),
            output_price=Decimal("5.00"),
            context_window=2_000_000,
            description="Gemini 1.5 Pro - Large context",
        ),
        "gemini-1.5-flash": ModelPricing(
            model="gemini-1.5-flash",
            provider="gemini",
            input_price=Decimal("0.075"),
            output_price=Decimal("0.30"),
            context_window=1_000_000,
            description="Gemini 1.5 Flash",
        ),
        "gemini-1.0-pro": ModelPricing(
            model="gemini-1.0-pro",
            provider="gemini",
            input_price=Decimal("0.50"),
            output_price=Decimal("1.50"),
            context_window=32_760,
            description="Gemini 1.0 Pro",
        ),
    }

    @classmethod
    def get_pricing(
        cls, model: str, provider: str | None = None
    ) -> ModelPricing | None:
        """
        Get pricing for a specific model.

        Args:
            model: Model identifier.
            provider: Optional provider hint.

        Returns:
            ModelPricing if found, None otherwise.
        """
        # Check provider-specific first
        if provider:
            models = cls._get_provider_models(provider)
            if model in models:
                return models[model]

        # Search all providers
        for models in [cls.ANTHROPIC_MODELS, cls.OPENAI_MODELS, cls.GEMINI_MODELS]:
            if model in models:
                return models[model]

        return None

    @classmethod
    def list_models(cls, provider: str | None = None) -> list[ModelPricing]:
        """
        List all available models.

        Args:
            provider: Optional filter by provider.

        Returns:
            List of ModelPricing objects.
        """
        if provider:
            models = cls._get_provider_models(provider)
            return list(models.values())

        return (
            list(cls.ANTHROPIC_MODELS.values())
            + list(cls.OPENAI_MODELS.values())
            + list(cls.GEMINI_MODELS.values())
        )

    @classmethod
    def _get_provider_models(cls, provider: str) -> dict[str, ModelPricing]:
        """Get models for a specific provider."""
        provider = provider.lower()
        if provider == "anthropic":
            return cls.ANTHROPIC_MODELS
        elif provider == "openai":
            return cls.OPENAI_MODELS
        elif provider in ("gemini", "google"):
            return cls.GEMINI_MODELS
        return {}
