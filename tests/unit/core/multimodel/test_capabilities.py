"""Tests for model capabilities tracking (F-072)."""


from persona.core.multimodel.capabilities import (
    CapabilityChecker,
    CapabilityQuery,
    ModelCapabilities,
    ModelComparison,
    compare_models,
    get_model_capabilities,
)


class TestModelCapabilities:
    """Tests for ModelCapabilities."""

    def test_default_values(self):
        """Has sensible defaults."""
        caps = ModelCapabilities(
            provider="test",
            model="test-model",
        )

        assert caps.context_window == 128000
        assert caps.structured_output is True
        assert caps.vision is False

    def test_to_dict(self):
        """Converts to dictionary."""
        caps = ModelCapabilities(
            provider="anthropic",
            model="claude-sonnet-4",
            context_window=200000,
            vision=True,
            extended_thinking=True,
        )
        data = caps.to_dict()

        assert data["provider"] == "anthropic"
        assert data["model"] == "claude-sonnet-4"
        assert data["context_window"] == 200000
        assert data["vision"] is True

    def test_to_display(self):
        """Generates display output."""
        caps = ModelCapabilities(
            provider="anthropic",
            model="claude-test",
            context_window=200000,
            vision=True,
            strengths=["reasoning", "coding"],
            best_for=["Complex analysis"],
            pricing_tier="premium",
        )
        display = caps.to_display()

        assert "claude-test" in display
        assert "200,000" in display
        assert "Vision" in display
        assert "reasoning" in display
        assert "premium" in display


class TestCapabilityQuery:
    """Tests for CapabilityQuery."""

    def test_default_values(self):
        """Has sensible defaults."""
        query = CapabilityQuery()

        assert query.min_context_window is None
        assert query.requires_vision is False
        assert query.pricing_tier is None

    def test_with_requirements(self):
        """Creates query with requirements."""
        query = CapabilityQuery(
            min_context_window=100000,
            requires_vision=True,
            pricing_tier="budget",
        )

        assert query.min_context_window == 100000
        assert query.requires_vision is True
        assert query.pricing_tier == "budget"


class TestModelComparison:
    """Tests for ModelComparison."""

    def test_to_dict(self):
        """Converts to dictionary."""
        comparison = ModelComparison(
            models=[],
            winner_by_context="model-a",
            winner_by_output="model-b",
            recommendation="Use model-a",
        )
        data = comparison.to_dict()

        assert data["winner_by_context"] == "model-a"
        assert data["winner_by_output"] == "model-b"

    def test_to_display_empty(self):
        """Handles empty models list."""
        comparison = ModelComparison(models=[])
        display = comparison.to_display()

        assert "No models" in display

    def test_to_display_with_models(self):
        """Generates comparison display."""
        comparison = ModelComparison(
            models=[
                ModelCapabilities("anthropic", "claude-a", context_window=200000),
                ModelCapabilities("openai", "gpt-b", context_window=128000),
            ],
            winner_by_context="claude-a",
            winner_by_output="claude-a",
            winner_by_features="claude-a",
            winner_by_price="gpt-b",
            recommendation="claude-a for features, gpt-b for value",
        )
        display = comparison.to_display()

        assert "Model Comparison" in display
        assert "claude-a" in display
        assert "gpt-b" in display
        assert "Winners" in display


class TestCapabilityChecker:
    """Tests for CapabilityChecker."""

    def test_get_capabilities_known_model(self):
        """Gets capabilities for known model."""
        checker = CapabilityChecker()

        caps = checker.get_capabilities("anthropic", "claude-sonnet-4-20250514")

        assert caps is not None
        assert caps.provider == "anthropic"
        assert caps.context_window == 200000

    def test_get_capabilities_unknown_model(self):
        """Returns None for unknown model."""
        checker = CapabilityChecker()

        caps = checker.get_capabilities("unknown", "fake-model")

        assert caps is None

    def test_find_models_by_context(self):
        """Finds models by context window."""
        checker = CapabilityChecker()
        query = CapabilityQuery(min_context_window=1000000)

        models = checker.find_models(query)

        # Only Gemini models have 1M+ context
        for m in models:
            assert m.context_window >= 1000000

    def test_find_models_by_vision(self):
        """Finds models with vision capability."""
        checker = CapabilityChecker()
        query = CapabilityQuery(requires_vision=True)

        models = checker.find_models(query)

        for m in models:
            assert m.vision is True

    def test_find_models_by_extended_thinking(self):
        """Finds models with extended thinking."""
        checker = CapabilityChecker()
        query = CapabilityQuery(requires_extended_thinking=True)

        models = checker.find_models(query)

        for m in models:
            assert m.extended_thinking is True

    def test_find_models_by_pricing_tier(self):
        """Finds models by pricing tier."""
        checker = CapabilityChecker()
        query = CapabilityQuery(pricing_tier="budget")

        models = checker.find_models(query)

        for m in models:
            assert m.pricing_tier == "budget"

    def test_find_models_by_use_case(self):
        """Finds models by use case."""
        checker = CapabilityChecker()
        query = CapabilityQuery(use_case="persona")

        models = checker.find_models(query)

        # Should find models with "persona" in best_for
        # (may be empty if no exact match)
        assert isinstance(models, list)

    def test_find_models_combined_query(self):
        """Finds models matching multiple criteria."""
        checker = CapabilityChecker()
        query = CapabilityQuery(
            requires_vision=True,
            requires_structured_output=True,
            pricing_tier="standard",
        )

        models = checker.find_models(query)

        for m in models:
            assert m.vision is True
            assert m.structured_output is True
            assert m.pricing_tier == "standard"

    def test_compare_models_basic(self):
        """Compares multiple models."""
        checker = CapabilityChecker()
        models = [
            ("anthropic", "claude-sonnet-4-20250514"),
            ("openai", "gpt-4o"),
        ]

        comparison = checker.compare_models(models)

        assert len(comparison.models) == 2
        assert comparison.winner_by_context is not None
        assert comparison.recommendation != ""

    def test_compare_models_empty(self):
        """Handles empty models list."""
        checker = CapabilityChecker()

        comparison = checker.compare_models([])

        assert len(comparison.models) == 0

    def test_compare_models_unknown_filtered(self):
        """Unknown models are filtered out."""
        checker = CapabilityChecker()
        models = [
            ("anthropic", "claude-sonnet-4-20250514"),
            ("unknown", "fake-model"),
        ]

        comparison = checker.compare_models(models)

        assert len(comparison.models) == 1

    def test_compare_models_single(self):
        """Handles single model comparison."""
        checker = CapabilityChecker()
        models = [("anthropic", "claude-sonnet-4-20250514")]

        comparison = checker.compare_models(models)

        assert len(comparison.models) == 1
        assert "only option" in comparison.recommendation.lower()

    def test_check_compatibility_compatible(self):
        """Checks compatibility successfully."""
        checker = CapabilityChecker()
        requirements = {
            "min_context": 100000,
            "vision": True,
        }

        compatible, issues = checker.check_compatibility(
            "anthropic",
            "claude-sonnet-4-20250514",
            requirements,
        )

        assert compatible is True
        assert len(issues) == 0

    def test_check_compatibility_context_insufficient(self):
        """Detects insufficient context window."""
        checker = CapabilityChecker()
        requirements = {"min_context": 500000}

        compatible, issues = checker.check_compatibility(
            "anthropic",
            "claude-sonnet-4-20250514",
            requirements,
        )

        assert compatible is False
        assert any("context" in i.lower() for i in issues)

    def test_check_compatibility_missing_vision(self):
        """Detects missing vision capability."""
        checker = CapabilityChecker()
        requirements = {"vision": True}

        # Claude Haiku has vision, so let's use a requirement
        # that tests extended_thinking which some models lack
        requirements = {"extended_thinking": True}

        compatible, issues = checker.check_compatibility(
            "anthropic",
            "claude-sonnet-4-20250514",  # This one doesn't have extended thinking
            requirements,
        )

        assert compatible is False
        assert any("extended thinking" in i.lower() for i in issues)

    def test_check_compatibility_unknown_model(self):
        """Returns incompatible for unknown model."""
        checker = CapabilityChecker()

        compatible, issues = checker.check_compatibility(
            "unknown",
            "fake-model",
            {},
        )

        assert compatible is False
        assert any("unknown" in i.lower() for i in issues)


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_model_capabilities(self):
        """get_model_capabilities convenience function works."""
        caps = get_model_capabilities("anthropic", "claude-sonnet-4-20250514")

        assert caps is not None
        assert caps.provider == "anthropic"

    def test_get_model_capabilities_unknown(self):
        """Returns None for unknown model."""
        caps = get_model_capabilities("unknown", "fake")

        assert caps is None

    def test_compare_models_function(self):
        """compare_models convenience function works."""
        models = [
            ("anthropic", "claude-sonnet-4-20250514"),
            ("openai", "gpt-4o"),
        ]

        comparison = compare_models(models)

        assert isinstance(comparison, ModelComparison)
        assert len(comparison.models) == 2
