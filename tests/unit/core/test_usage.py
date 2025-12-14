"""
Tests for example usage output (F-038).
"""

import pytest

from persona.core.output.usage import (
    FeaturePrediction,
    InteractionPoint,
    InteractionType,
    JourneyStep,
    ProductContext,
    UsageFormatter,
    UsageLikelihood,
    UsageScenario,
    UsageScenarioGenerator,
)
from persona.core.generation.parser import Persona


@pytest.fixture
def sample_persona() -> Persona:
    """Create a sample persona for testing."""
    return Persona(
        id="persona-001",
        name="Sarah Chen",
        demographics={"role": "Marketing Manager"},
        goals=[
            "Streamline campaign workflows",
            "Improve team collaboration",
            "Achieve work-life balance",
        ],
        pain_points=[
            "Too many manual processes",
            "Difficulty tracking performance",
            "Context switching",
        ],
        behaviours=[
            "Checking analytics dashboards first thing in the morning",
            "Juggling multiple campaigns simultaneously",
            "Collaborating with cross-functional teams",
        ],
    )


@pytest.fixture
def minimal_persona() -> Persona:
    """Create a minimal persona for testing."""
    return Persona(
        id="persona-002",
        name="Alex",
        demographics={},
        goals=["Get things done"],
        pain_points=["Complexity"],
    )


class TestUsageLikelihood:
    """Tests for UsageLikelihood enum."""

    def test_likelihood_values(self):
        """Test likelihood enum values."""
        assert UsageLikelihood.DAILY.value == "daily"
        assert UsageLikelihood.WEEKLY.value == "weekly"
        assert UsageLikelihood.MONTHLY.value == "monthly"
        assert UsageLikelihood.RARELY.value == "rarely"
        assert UsageLikelihood.NEVER.value == "never"


class TestInteractionType:
    """Tests for InteractionType enum."""

    def test_interaction_values(self):
        """Test interaction type values."""
        assert InteractionType.FRICTION.value == "friction"
        assert InteractionType.DELIGHT.value == "delight"
        assert InteractionType.NEUTRAL.value == "neutral"


class TestInteractionPoint:
    """Tests for InteractionPoint dataclass."""

    def test_creation(self):
        """Test interaction point creation."""
        point = InteractionPoint(
            description="Loading slow",
            type=InteractionType.FRICTION,
            reason="Poor network connection",
        )
        assert point.description == "Loading slow"
        assert point.type == InteractionType.FRICTION
        assert point.reason == "Poor network connection"

    def test_default_reason(self):
        """Test default empty reason."""
        point = InteractionPoint(
            description="Quick access",
            type=InteractionType.DELIGHT,
        )
        assert point.reason == ""


class TestJourneyStep:
    """Tests for JourneyStep dataclass."""

    def test_creation(self):
        """Test journey step creation."""
        step = JourneyStep(
            time_context="Morning",
            action="Opens the app",
        )
        assert step.time_context == "Morning"
        assert step.action == "Opens the app"
        assert step.interactions == []

    def test_with_interactions(self):
        """Test journey step with interactions."""
        interactions = [
            InteractionPoint("Action 1", InteractionType.DELIGHT),
        ]
        step = JourneyStep(
            time_context="Morning",
            action="Opens the app",
            interactions=interactions,
        )
        assert len(step.interactions) == 1


class TestFeaturePrediction:
    """Tests for FeaturePrediction dataclass."""

    def test_creation(self):
        """Test feature prediction creation."""
        pred = FeaturePrediction(
            feature="Dashboard",
            likelihood=UsageLikelihood.DAILY,
            reason="Central to workflow",
        )
        assert pred.feature == "Dashboard"
        assert pred.likelihood == UsageLikelihood.DAILY
        assert pred.reason == "Central to workflow"


class TestUsageScenario:
    """Tests for UsageScenario dataclass."""

    def test_creation(self):
        """Test usage scenario creation."""
        scenario = UsageScenario(
            persona_name="Test User",
            persona_id="test-001",
        )
        assert scenario.persona_name == "Test User"
        assert scenario.persona_id == "test-001"
        assert scenario.journey_steps == []
        assert scenario.feature_predictions == []
        assert scenario.key_insights == []


class TestProductContext:
    """Tests for ProductContext dataclass."""

    def test_default_values(self):
        """Test default product context values."""
        context = ProductContext()
        assert context.name == "the product"
        assert context.type == "application"
        assert context.features == []
        assert context.primary_platform == "web"

    def test_custom_values(self):
        """Test custom product context."""
        context = ProductContext(
            name="TaskFlow",
            type="mobile app",
            features=["Tasks", "Calendar", "Reports"],
            primary_platform="mobile",
        )
        assert context.name == "TaskFlow"
        assert len(context.features) == 3


class TestUsageScenarioGenerator:
    """Tests for UsageScenarioGenerator."""

    def test_creation(self):
        """Test generator creation."""
        generator = UsageScenarioGenerator()
        assert generator._context is not None

    def test_creation_with_context(self):
        """Test generator with custom context."""
        context = ProductContext(name="TestApp")
        generator = UsageScenarioGenerator(context)
        assert generator._context.name == "TestApp"

    def test_generate_returns_scenario(self, sample_persona):
        """Test generate returns a UsageScenario."""
        generator = UsageScenarioGenerator()
        scenario = generator.generate(sample_persona)
        assert isinstance(scenario, UsageScenario)
        assert scenario.persona_name == "Sarah Chen"
        assert scenario.persona_id == "persona-001"

    def test_generate_includes_journey_steps(self, sample_persona):
        """Test generated scenario includes journey steps."""
        generator = UsageScenarioGenerator()
        scenario = generator.generate(sample_persona)
        assert len(scenario.journey_steps) > 0

    def test_generate_includes_feature_predictions(self, sample_persona):
        """Test generated scenario includes feature predictions."""
        generator = UsageScenarioGenerator()
        scenario = generator.generate(sample_persona)
        assert len(scenario.feature_predictions) > 0

    def test_generate_includes_insights(self, sample_persona):
        """Test generated scenario includes key insights."""
        generator = UsageScenarioGenerator()
        scenario = generator.generate(sample_persona)
        assert len(scenario.key_insights) > 0

    def test_journey_uses_behaviours(self, sample_persona):
        """Test journey steps are based on behaviours."""
        generator = UsageScenarioGenerator()
        scenario = generator.generate(sample_persona)
        # First behaviour should appear in morning step
        first_step = scenario.journey_steps[0]
        assert "checking analytics dashboards" in first_step.action.lower()

    def test_predictions_use_default_features(self, sample_persona):
        """Test predictions use default features when none provided."""
        generator = UsageScenarioGenerator()
        scenario = generator.generate(sample_persona)
        features = [p.feature for p in scenario.feature_predictions]
        assert "Dashboard" in features

    def test_predictions_use_context_features(self, sample_persona):
        """Test predictions use context features when provided."""
        context = ProductContext(features=["CustomFeature1", "CustomFeature2"])
        generator = UsageScenarioGenerator(context)
        scenario = generator.generate(sample_persona)
        features = [p.feature for p in scenario.feature_predictions]
        assert "CustomFeature1" in features
        assert "CustomFeature2" in features

    def test_insights_mention_goals(self, sample_persona):
        """Test insights mention primary goal."""
        generator = UsageScenarioGenerator()
        scenario = generator.generate(sample_persona)
        combined_insights = " ".join(scenario.key_insights)
        assert "streamline" in combined_insights.lower() or "workflow" in combined_insights.lower()

    def test_insights_mention_pain_points(self, sample_persona):
        """Test insights mention pain points."""
        generator = UsageScenarioGenerator()
        scenario = generator.generate(sample_persona)
        combined_insights = " ".join(scenario.key_insights)
        assert "manual" in combined_insights.lower() or "friction" in combined_insights.lower()

    def test_generate_minimal_persona(self, minimal_persona):
        """Test generating scenario for minimal persona."""
        generator = UsageScenarioGenerator()
        scenario = generator.generate(minimal_persona)
        assert scenario.persona_name == "Alex"
        # Should still have some content
        assert len(scenario.feature_predictions) > 0


class TestUsageFormatter:
    """Tests for UsageFormatter."""

    def test_extension_is_md(self):
        """Test file extension is .md."""
        formatter = UsageFormatter()
        assert formatter.extension() == ".md"

    def test_format_returns_string(self, sample_persona):
        """Test format returns a string."""
        formatter = UsageFormatter()
        result = formatter.format(sample_persona)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_includes_persona_name(self, sample_persona):
        """Test format includes persona name in header."""
        formatter = UsageFormatter()
        result = formatter.format(sample_persona)
        assert "Sarah Chen" in result

    def test_format_includes_user_journey_section(self, sample_persona):
        """Test format includes user journey section."""
        formatter = UsageFormatter()
        result = formatter.format(sample_persona)
        assert "## User Journey" in result

    def test_format_includes_feature_predictions_section(self, sample_persona):
        """Test format includes feature predictions section."""
        formatter = UsageFormatter()
        result = formatter.format(sample_persona)
        assert "## Feature Usage Predictions" in result

    def test_format_includes_predictions_table(self, sample_persona):
        """Test format includes predictions table."""
        formatter = UsageFormatter()
        result = formatter.format(sample_persona)
        assert "| Feature |" in result
        assert "| Usage Likelihood |" in result

    def test_format_includes_insights_section(self, sample_persona):
        """Test format includes key insights section."""
        formatter = UsageFormatter()
        result = formatter.format(sample_persona)
        assert "## Key Insights" in result

    def test_format_includes_interaction_icons(self, sample_persona):
        """Test format includes interaction type icons."""
        formatter = UsageFormatter()
        result = formatter.format(sample_persona)
        # Should include at least one of the icons
        assert "⚠️" in result or "✨" in result or "•" in result

    def test_format_multiple_separates_with_divider(self, sample_persona, minimal_persona):
        """Test format_multiple separates personas."""
        formatter = UsageFormatter()
        result = formatter.format_multiple([sample_persona, minimal_persona])
        assert "Sarah Chen" in result
        assert "Alex" in result
        assert "---" in result

    def test_format_with_product_context(self, sample_persona):
        """Test formatting with custom product context."""
        context = ProductContext(
            name="TaskMaster",
            features=["Tasks", "Calendar"],
        )
        formatter = UsageFormatter(product_context=context)
        result = formatter.format(sample_persona)
        assert "Tasks" in result
        assert "Calendar" in result


class TestUsageFormatterEdgeCases:
    """Tests for edge cases in usage formatting."""

    def test_no_behaviours(self):
        """Test formatting persona without behaviours."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal"],
            pain_points=["Pain"],
            behaviours=[],
        )
        formatter = UsageFormatter()
        result = formatter.format(persona)
        # Should still produce output
        assert "Test User" in result

    def test_no_goals(self):
        """Test formatting persona without goals."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=[],
            pain_points=["Pain"],
        )
        formatter = UsageFormatter()
        result = formatter.format(persona)
        assert "Test User" in result

    def test_no_pain_points(self):
        """Test formatting persona without pain points."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal"],
            pain_points=[],
        )
        formatter = UsageFormatter()
        result = formatter.format(persona)
        assert "Test User" in result

    def test_many_goals_triggers_insight(self):
        """Test many goals triggers overwhelm insight."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal 1", "Goal 2", "Goal 3", "Goal 4", "Goal 5"],
            pain_points=[],
        )
        generator = UsageScenarioGenerator()
        scenario = generator.generate(persona)
        combined_insights = " ".join(scenario.key_insights)
        assert "overwhelm" in combined_insights.lower() or "competing" in combined_insights.lower()


class TestUsageFormatterRegistration:
    """Tests for usage formatter registration."""

    def test_usage_format_registered(self):
        """Test usage format is registered."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        assert registry.has("usage")

    def test_usage_format_info(self):
        """Test usage format info."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        info = registry.get_info("usage")
        assert info.name == "usage"
        assert info.extension == ".md"

    def test_get_usage_formatter(self):
        """Test getting usage formatter from registry."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        formatter = registry.get("usage")
        assert formatter is not None
        assert hasattr(formatter, "format")
