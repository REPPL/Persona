"""Model capabilities tracking (F-072).

Tracks and queries model capabilities to help users
select appropriate models for their use case.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelCapabilities:
    """Capabilities for a single model.

    Attributes:
        provider: The LLM provider.
        model: The model identifier.
        context_window: Maximum context window tokens.
        max_output: Maximum output tokens.
        structured_output: Supports structured JSON output.
        vision: Supports image analysis.
        function_calling: Supports function/tool calling.
        streaming: Supports streaming responses.
        extended_thinking: Supports extended thinking mode.
        batch_api: Supports batch API.
        strengths: List of model strengths.
        best_for: List of use cases this model excels at.
        pricing_tier: Pricing tier (budget, standard, premium).
    """
    provider: str
    model: str
    context_window: int = 128000
    max_output: int = 4096
    structured_output: bool = True
    vision: bool = False
    function_calling: bool = True
    streaming: bool = True
    extended_thinking: bool = False
    batch_api: bool = False
    strengths: list[str] = field(default_factory=list)
    best_for: list[str] = field(default_factory=list)
    pricing_tier: str = "standard"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "model": self.model,
            "context_window": self.context_window,
            "max_output": self.max_output,
            "structured_output": self.structured_output,
            "vision": self.vision,
            "function_calling": self.function_calling,
            "streaming": self.streaming,
            "extended_thinking": self.extended_thinking,
            "batch_api": self.batch_api,
            "strengths": self.strengths,
            "best_for": self.best_for,
            "pricing_tier": self.pricing_tier,
        }

    def to_display(self) -> str:
        """Generate human-readable display."""
        lines = [
            f"Model Capabilities: {self.model}",
            "=" * 50,
            "",
            "Context & Output:",
            f"  Context window:    {self.context_window:,} tokens",
            f"  Max output:        {self.max_output:,} tokens",
            "",
            "Features:",
        ]

        features = [
            ("Structured output (JSON mode)", self.structured_output),
            ("Vision (image analysis)", self.vision),
            ("Function calling", self.function_calling),
            ("Streaming", self.streaming),
            ("Extended thinking", self.extended_thinking),
            ("Batch API", self.batch_api),
        ]

        for name, enabled in features:
            icon = "✓" if enabled else "✗"
            lines.append(f"  {icon} {name}")

        if self.strengths:
            lines.append("")
            lines.append("Strengths:")
            for strength in self.strengths:
                lines.append(f"  • {strength}")

        if self.best_for:
            lines.append("")
            lines.append("Best For:")
            for use_case in self.best_for:
                lines.append(f"  • {use_case}")

        lines.append("")
        lines.append(f"Pricing Tier: {self.pricing_tier}")

        return "\n".join(lines)


@dataclass
class CapabilityQuery:
    """Query for model capabilities.

    Attributes:
        min_context_window: Minimum required context window.
        requires_vision: Must support vision.
        requires_structured_output: Must support structured output.
        requires_function_calling: Must support function calling.
        requires_streaming: Must support streaming.
        requires_extended_thinking: Must support extended thinking.
        pricing_tier: Preferred pricing tier.
        use_case: Specific use case to match.
    """
    min_context_window: int | None = None
    requires_vision: bool = False
    requires_structured_output: bool = False
    requires_function_calling: bool = False
    requires_streaming: bool = False
    requires_extended_thinking: bool = False
    pricing_tier: str | None = None
    use_case: str | None = None


@dataclass
class ModelComparison:
    """Comparison of multiple models.

    Attributes:
        models: List of model capabilities being compared.
        winner_by_context: Model with largest context window.
        winner_by_output: Model with largest output.
        winner_by_features: Model with most features.
        winner_by_price: Most cost-effective model.
        recommendation: Overall recommendation.
    """
    models: list[ModelCapabilities]
    winner_by_context: str | None = None
    winner_by_output: str | None = None
    winner_by_features: str | None = None
    winner_by_price: str | None = None
    recommendation: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "models": [m.to_dict() for m in self.models],
            "winner_by_context": self.winner_by_context,
            "winner_by_output": self.winner_by_output,
            "winner_by_features": self.winner_by_features,
            "winner_by_price": self.winner_by_price,
            "recommendation": self.recommendation,
        }

    def to_display(self) -> str:
        """Generate human-readable comparison."""
        if not self.models:
            return "No models to compare"

        lines = [
            "Model Comparison",
            "=" * 70,
            "",
        ]

        # Header
        headers = ["Feature"] + [m.model[:20] for m in self.models]
        col_width = 20
        header_line = " | ".join(h.ljust(col_width) for h in headers)
        lines.append(header_line)
        lines.append("-" * len(header_line))

        # Context window
        row = ["Context Window"] + [
            f"{m.context_window:,}" for m in self.models
        ]
        lines.append(" | ".join(c.ljust(col_width) for c in row))

        # Max output
        row = ["Max Output"] + [
            f"{m.max_output:,}" for m in self.models
        ]
        lines.append(" | ".join(c.ljust(col_width) for c in row))

        # Features
        features = [
            ("Structured Output", "structured_output"),
            ("Vision", "vision"),
            ("Function Calling", "function_calling"),
            ("Streaming", "streaming"),
            ("Extended Thinking", "extended_thinking"),
        ]

        for name, attr in features:
            row = [name] + [
                "✓" if getattr(m, attr) else "✗" for m in self.models
            ]
            lines.append(" | ".join(c.ljust(col_width) for c in row))

        # Pricing tier
        row = ["Pricing"] + [m.pricing_tier for m in self.models]
        lines.append(" | ".join(c.ljust(col_width) for c in row))

        # Winners
        lines.extend([
            "",
            "Winners:",
            f"  Largest Context: {self.winner_by_context}",
            f"  Largest Output:  {self.winner_by_output}",
            f"  Most Features:   {self.winner_by_features}",
            f"  Best Value:      {self.winner_by_price}",
            "",
            f"Recommendation: {self.recommendation}",
        ])

        return "\n".join(lines)


class CapabilityChecker:
    """Checker for model capabilities.

    Provides capability queries, model comparisons, and
    recommendations based on use cases.

    Example:
        >>> checker = CapabilityChecker()
        >>> models = checker.find_models(
        ...     query=CapabilityQuery(min_context_window=100000)
        ... )
    """

    # Known model capabilities
    CAPABILITIES = {
        # Anthropic models
        ("anthropic", "claude-opus-4-5-20251101"): ModelCapabilities(
            provider="anthropic",
            model="claude-opus-4-5-20251101",
            context_window=200000,
            max_output=32768,
            structured_output=True,
            vision=True,
            function_calling=True,
            streaming=True,
            extended_thinking=True,
            batch_api=True,
            strengths=["reasoning", "coding", "analysis", "creativity"],
            best_for=["Complex persona generation", "Research synthesis", "Creative writing"],
            pricing_tier="premium",
        ),
        ("anthropic", "claude-sonnet-4-5-20250929"): ModelCapabilities(
            provider="anthropic",
            model="claude-sonnet-4-5-20250929",
            context_window=200000,
            max_output=16384,
            structured_output=True,
            vision=True,
            function_calling=True,
            streaming=True,
            extended_thinking=True,
            batch_api=True,
            strengths=["coding", "analysis", "instruction_following"],
            best_for=["Standard persona generation", "Code-related personas"],
            pricing_tier="standard",
        ),
        ("anthropic", "claude-sonnet-4-20250514"): ModelCapabilities(
            provider="anthropic",
            model="claude-sonnet-4-20250514",
            context_window=200000,
            max_output=16384,
            structured_output=True,
            vision=True,
            function_calling=True,
            streaming=True,
            extended_thinking=False,
            batch_api=True,
            strengths=["coding", "analysis", "speed"],
            best_for=["Fast persona generation", "Iterative refinement"],
            pricing_tier="standard",
        ),
        ("anthropic", "claude-haiku-3-5-20241022"): ModelCapabilities(
            provider="anthropic",
            model="claude-haiku-3-5-20241022",
            context_window=200000,
            max_output=8192,
            structured_output=True,
            vision=True,
            function_calling=True,
            streaming=True,
            extended_thinking=False,
            batch_api=True,
            strengths=["speed", "efficiency"],
            best_for=["Quick iterations", "Cost-sensitive generation"],
            pricing_tier="budget",
        ),
        # OpenAI models
        ("openai", "gpt-4o"): ModelCapabilities(
            provider="openai",
            model="gpt-4o",
            context_window=128000,
            max_output=16384,
            structured_output=True,
            vision=True,
            function_calling=True,
            streaming=True,
            extended_thinking=False,
            batch_api=True,
            strengths=["general_knowledge", "instruction_following"],
            best_for=["General persona generation", "Multi-modal inputs"],
            pricing_tier="standard",
        ),
        ("openai", "gpt-4o-mini"): ModelCapabilities(
            provider="openai",
            model="gpt-4o-mini",
            context_window=128000,
            max_output=16384,
            structured_output=True,
            vision=True,
            function_calling=True,
            streaming=True,
            extended_thinking=False,
            batch_api=True,
            strengths=["speed", "efficiency"],
            best_for=["Budget generation", "Simple personas"],
            pricing_tier="budget",
        ),
        ("openai", "o1"): ModelCapabilities(
            provider="openai",
            model="o1",
            context_window=200000,
            max_output=100000,
            structured_output=True,
            vision=True,
            function_calling=True,
            streaming=True,
            extended_thinking=True,
            batch_api=False,
            strengths=["reasoning", "complex_analysis"],
            best_for=["Complex research synthesis", "Deep analysis"],
            pricing_tier="premium",
        ),
        # Gemini models
        ("gemini", "gemini-1.5-pro"): ModelCapabilities(
            provider="gemini",
            model="gemini-1.5-pro",
            context_window=2000000,
            max_output=8192,
            structured_output=True,
            vision=True,
            function_calling=True,
            streaming=True,
            extended_thinking=False,
            batch_api=False,
            strengths=["long_context", "multimodal"],
            best_for=["Large dataset analysis", "Video/audio input"],
            pricing_tier="standard",
        ),
        ("gemini", "gemini-1.5-flash"): ModelCapabilities(
            provider="gemini",
            model="gemini-1.5-flash",
            context_window=1000000,
            max_output=8192,
            structured_output=True,
            vision=True,
            function_calling=True,
            streaming=True,
            extended_thinking=False,
            batch_api=False,
            strengths=["speed", "long_context"],
            best_for=["Fast long-context generation"],
            pricing_tier="budget",
        ),
    }

    def __init__(self):
        """Initialise the capability checker."""
        pass

    def get_capabilities(
        self,
        provider: str,
        model: str,
    ) -> ModelCapabilities | None:
        """Get capabilities for a specific model.

        Args:
            provider: The LLM provider.
            model: The model identifier.

        Returns:
            ModelCapabilities or None if not found.
        """
        return self.CAPABILITIES.get((provider, model))

    def find_models(
        self,
        query: CapabilityQuery,
    ) -> list[ModelCapabilities]:
        """Find models matching a capability query.

        Args:
            query: The capability requirements.

        Returns:
            List of matching ModelCapabilities.
        """
        matches = []

        for caps in self.CAPABILITIES.values():
            if self._matches_query(caps, query):
                matches.append(caps)

        return matches

    def _matches_query(
        self,
        caps: ModelCapabilities,
        query: CapabilityQuery,
    ) -> bool:
        """Check if capabilities match a query."""
        if query.min_context_window and caps.context_window < query.min_context_window:
            return False
        if query.requires_vision and not caps.vision:
            return False
        if query.requires_structured_output and not caps.structured_output:
            return False
        if query.requires_function_calling and not caps.function_calling:
            return False
        if query.requires_streaming and not caps.streaming:
            return False
        if query.requires_extended_thinking and not caps.extended_thinking:
            return False
        if query.pricing_tier and caps.pricing_tier != query.pricing_tier:
            return False
        if query.use_case:
            use_case_match = any(
                query.use_case.lower() in uc.lower()
                for uc in caps.best_for
            )
            if not use_case_match:
                return False

        return True

    def compare_models(
        self,
        models: list[tuple[str, str]],
    ) -> ModelComparison:
        """Compare multiple models.

        Args:
            models: List of (provider, model) tuples.

        Returns:
            ModelComparison with detailed comparison.
        """
        caps_list = []
        for provider, model in models:
            caps = self.get_capabilities(provider, model)
            if caps:
                caps_list.append(caps)

        if not caps_list:
            return ModelComparison(models=[])

        # Find winners
        winner_context = max(caps_list, key=lambda c: c.context_window)
        winner_output = max(caps_list, key=lambda c: c.max_output)

        # Count features
        def feature_count(c: ModelCapabilities) -> int:
            return sum([
                c.structured_output,
                c.vision,
                c.function_calling,
                c.streaming,
                c.extended_thinking,
                c.batch_api,
            ])

        winner_features = max(caps_list, key=feature_count)

        # Best value (budget tier with most features)
        budget_models = [c for c in caps_list if c.pricing_tier == "budget"]
        if budget_models:
            winner_price = max(budget_models, key=feature_count)
        else:
            winner_price = min(
                caps_list,
                key=lambda c: {"budget": 1, "standard": 2, "premium": 3}[c.pricing_tier]
            )

        # Generate recommendation
        if len(caps_list) == 1:
            recommendation = f"{caps_list[0].model} is the only option"
        else:
            recommendation = (
                f"For best value: {winner_price.model}. "
                f"For largest context: {winner_context.model}. "
                f"For most features: {winner_features.model}."
            )

        return ModelComparison(
            models=caps_list,
            winner_by_context=winner_context.model,
            winner_by_output=winner_output.model,
            winner_by_features=winner_features.model,
            winner_by_price=winner_price.model,
            recommendation=recommendation,
        )

    def check_compatibility(
        self,
        provider: str,
        model: str,
        requirements: dict[str, Any],
    ) -> tuple[bool, list[str]]:
        """Check if a model meets requirements.

        Args:
            provider: The LLM provider.
            model: The model identifier.
            requirements: Dict of required capabilities.

        Returns:
            Tuple of (compatible, list of issues).
        """
        caps = self.get_capabilities(provider, model)
        if not caps:
            return False, [f"Unknown model: {provider}:{model}"]

        issues = []

        if "min_context" in requirements:
            if caps.context_window < requirements["min_context"]:
                issues.append(
                    f"Context window {caps.context_window:,} < "
                    f"required {requirements['min_context']:,}"
                )

        if requirements.get("vision") and not caps.vision:
            issues.append("Vision capability required but not available")

        if requirements.get("extended_thinking") and not caps.extended_thinking:
            issues.append("Extended thinking required but not available")

        return len(issues) == 0, issues


def get_model_capabilities(
    provider: str,
    model: str,
) -> ModelCapabilities | None:
    """Convenience function to get model capabilities.

    Args:
        provider: The LLM provider.
        model: The model identifier.

    Returns:
        ModelCapabilities or None if not found.
    """
    checker = CapabilityChecker()
    return checker.get_capabilities(provider, model)


def compare_models(
    models: list[tuple[str, str]],
) -> ModelComparison:
    """Convenience function to compare models.

    Args:
        models: List of (provider, model) tuples.

    Returns:
        ModelComparison with detailed comparison.
    """
    checker = CapabilityChecker()
    return checker.compare_models(models)
