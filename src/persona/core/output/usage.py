"""
Example usage output formatter for personas.

This module generates practical usage scenarios showing how personas
would interact with products, including user journeys, friction points,
and feature usage predictions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from persona.core.generation.parser import Persona
from persona.core.output.registry import (
    BaseFormatterV2,
    OutputSection,
    SectionConfig,
    register,
)


class UsageLikelihood(Enum):
    """Feature usage likelihood levels."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    RARELY = "rarely"
    NEVER = "never"


class InteractionType(Enum):
    """Types of user interactions."""

    FRICTION = "friction"
    DELIGHT = "delight"
    NEUTRAL = "neutral"


@dataclass
class InteractionPoint:
    """A point of interaction in a user journey."""

    description: str
    type: InteractionType
    reason: str = ""


@dataclass
class JourneyStep:
    """A step in a user journey."""

    time_context: str  # e.g., "Morning commute", "After lunch"
    action: str
    interactions: list[InteractionPoint] = field(default_factory=list)


@dataclass
class FeaturePrediction:
    """Prediction of feature usage by a persona."""

    feature: str
    likelihood: UsageLikelihood
    reason: str


@dataclass
class UsageScenario:
    """Complete usage scenario for a persona."""

    persona_name: str
    persona_id: str
    journey_steps: list[JourneyStep] = field(default_factory=list)
    feature_predictions: list[FeaturePrediction] = field(default_factory=list)
    key_insights: list[str] = field(default_factory=list)


@dataclass
class ProductContext:
    """Context about the product for scenario generation."""

    name: str = "the product"
    type: str = "application"
    features: list[str] = field(default_factory=list)
    primary_platform: str = "web"


class UsageScenarioGenerator:
    """
    Generate realistic usage scenarios for personas.

    Creates user journeys, friction/delight points, and feature
    usage predictions based on persona characteristics.

    Example:
        generator = UsageScenarioGenerator()
        scenario = generator.generate(persona)
    """

    def __init__(
        self,
        product_context: ProductContext | None = None,
    ) -> None:
        """
        Initialise scenario generator.

        Args:
            product_context: Optional product context for customisation.
        """
        self._context = product_context or ProductContext()

    def generate(self, persona: Persona) -> UsageScenario:
        """
        Generate a usage scenario for a persona.

        Args:
            persona: The persona to generate scenarios for.

        Returns:
            UsageScenario with journey and predictions.
        """
        scenario = UsageScenario(
            persona_name=persona.name,
            persona_id=persona.id,
        )

        # Generate journey steps based on behaviours
        scenario.journey_steps = self._generate_journey(persona)

        # Generate feature predictions based on goals and pain points
        scenario.feature_predictions = self._generate_predictions(persona)

        # Generate key insights
        scenario.key_insights = self._generate_insights(persona)

        return scenario

    def _generate_journey(self, persona: Persona) -> list[JourneyStep]:
        """Generate user journey steps."""
        steps = []
        behaviours = persona.behaviours or []
        pain_points = persona.pain_points or []
        goals = persona.goals or []

        # Morning step
        if behaviours:
            morning_action = behaviours[0] if behaviours else "Opening the application"
            morning_step = JourneyStep(
                time_context="Morning",
                action=f"{persona.name} starts the day by {morning_action.lower()}.",
                interactions=self._derive_interactions(morning_action, pain_points, goals),
            )
            steps.append(morning_step)

        # Mid-day step
        if len(behaviours) > 1:
            midday_action = behaviours[1]
            midday_step = JourneyStep(
                time_context="Midday",
                action=f"During the workday, {persona.name} focuses on {midday_action.lower()}.",
                interactions=self._derive_interactions(midday_action, pain_points, goals),
            )
            steps.append(midday_step)

        # End of day step
        if goals:
            eod_step = JourneyStep(
                time_context="End of Day",
                action=f"{persona.name} wraps up by reviewing progress towards their goals.",
                interactions=[
                    InteractionPoint(
                        description="Checking progress metrics",
                        type=InteractionType.DELIGHT if len(goals) <= 3 else InteractionType.NEUTRAL,
                        reason="Seeing measurable progress towards goals",
                    ),
                ],
            )
            steps.append(eod_step)

        return steps

    def _derive_interactions(
        self,
        action: str,
        pain_points: list[str],
        goals: list[str],
    ) -> list[InteractionPoint]:
        """Derive interaction points from action and persona data."""
        interactions = []

        # Check for friction from pain points
        action_lower = action.lower()
        for pain_point in pain_points[:2]:  # Limit to 2
            pain_lower = pain_point.lower()
            # Simple keyword matching for demo
            if any(
                word in action_lower
                for word in ["manual", "process", "track", "collaborate", "switch"]
            ):
                interactions.append(
                    InteractionPoint(
                        description=f"Encountering: {pain_point}",
                        type=InteractionType.FRICTION,
                        reason=pain_point,
                    )
                )
                break

        # Check for delight from goals
        for goal in goals[:1]:  # Limit to 1
            interactions.append(
                InteractionPoint(
                    description=f"Making progress on: {goal}",
                    type=InteractionType.DELIGHT,
                    reason=f"Aligns with goal: {goal}",
                )
            )
            break

        return interactions

    def _generate_predictions(self, persona: Persona) -> list[FeaturePrediction]:
        """Generate feature usage predictions."""
        predictions = []
        goals = persona.goals or []
        pain_points = persona.pain_points or []

        # Default features if none specified in context
        features = self._context.features or [
            "Dashboard",
            "Reports",
            "Export",
            "Settings",
            "Notifications",
        ]

        for feature in features[:5]:  # Limit to 5 features
            prediction = self._predict_feature_usage(feature, goals, pain_points)
            predictions.append(prediction)

        return predictions

    def _predict_feature_usage(
        self,
        feature: str,
        goals: list[str],
        pain_points: list[str],
    ) -> FeaturePrediction:
        """Predict usage likelihood for a single feature."""
        feature_lower = feature.lower()

        # Simple heuristic-based prediction
        if "dashboard" in feature_lower or "overview" in feature_lower:
            return FeaturePrediction(
                feature=feature,
                likelihood=UsageLikelihood.DAILY,
                reason="Central to daily workflow monitoring",
            )
        if "report" in feature_lower:
            return FeaturePrediction(
                feature=feature,
                likelihood=UsageLikelihood.WEEKLY,
                reason="Regular reporting needs",
            )
        if "export" in feature_lower:
            return FeaturePrediction(
                feature=feature,
                likelihood=UsageLikelihood.MONTHLY,
                reason="Periodic data extraction for stakeholders",
            )
        if "setting" in feature_lower:
            return FeaturePrediction(
                feature=feature,
                likelihood=UsageLikelihood.RARELY,
                reason="One-time setup with occasional adjustments",
            )

        # Default
        return FeaturePrediction(
            feature=feature,
            likelihood=UsageLikelihood.WEEKLY,
            reason="Regular use as part of standard workflow",
        )

    def _generate_insights(self, persona: Persona) -> list[str]:
        """Generate key insights about the persona's usage patterns."""
        insights = []
        goals = persona.goals or []
        pain_points = persona.pain_points or []
        behaviours = persona.behaviours or []

        if goals:
            insights.append(
                f"{persona.name}'s primary driver is achieving: {goals[0]}."
            )

        if pain_points:
            insights.append(
                f"Key friction area to address: {pain_points[0]}."
            )

        if behaviours:
            insights.append(
                f"Typical usage pattern involves: {behaviours[0].lower()}."
            )

        if len(goals) > 3:
            insights.append(
                "Multiple competing goals may lead to feature overwhelm - "
                "consider guided workflows."
            )

        return insights


class UsageFormatter(BaseFormatterV2):
    """
    Format personas with usage scenarios.

    Generates Markdown output including user journeys,
    friction/delight points, and feature predictions.
    """

    def __init__(
        self,
        product_context: ProductContext | None = None,
        sections: SectionConfig | None = None,
    ) -> None:
        """
        Initialise usage formatter.

        Args:
            product_context: Optional product context.
            sections: Section configuration.
        """
        super().__init__(sections=sections)
        self._generator = UsageScenarioGenerator(product_context)
        self._context = product_context or ProductContext()

    def format(
        self,
        persona: Persona,
        sections: SectionConfig | None = None,
    ) -> str:
        """
        Format a persona with usage scenarios.

        Args:
            persona: The persona to format.
            sections: Optional section override.

        Returns:
            Markdown formatted usage scenario.
        """
        scenario = self._generator.generate(persona)
        return self._format_scenario(scenario)

    def format_multiple(
        self,
        personas: list[Persona],
        sections: SectionConfig | None = None,
    ) -> str:
        """Format multiple personas with usage scenarios."""
        outputs = [self.format(p, sections) for p in personas]
        return "\n\n---\n\n".join(outputs)

    def extension(self) -> str:
        return ".md"

    def _format_scenario(self, scenario: UsageScenario) -> str:
        """Format a usage scenario as Markdown."""
        lines = []

        # Header
        lines.append(f"# Example Usage: {scenario.persona_name}")
        lines.append("")

        # User Journey
        if scenario.journey_steps:
            lines.append("## User Journey")
            lines.append("")

            for step in scenario.journey_steps:
                lines.append(f"### {step.time_context}")
                lines.append("")
                lines.append(step.action)
                lines.append("")

                for interaction in step.interactions:
                    icon = self._get_interaction_icon(interaction.type)
                    lines.append(f"- {icon} **{interaction.type.value.title()}**: {interaction.description}")
                    if interaction.reason:
                        lines.append(f"  - Reason: {interaction.reason}")

                lines.append("")

        # Feature Predictions
        if scenario.feature_predictions:
            lines.append("## Feature Usage Predictions")
            lines.append("")
            lines.append("| Feature | Usage Likelihood | Reason |")
            lines.append("|---------|-----------------|--------|")

            for pred in scenario.feature_predictions:
                likelihood = pred.likelihood.value.title()
                lines.append(f"| {pred.feature} | {likelihood} | {pred.reason} |")

            lines.append("")

        # Key Insights
        if scenario.key_insights:
            lines.append("## Key Insights")
            lines.append("")
            for insight in scenario.key_insights:
                lines.append(f"- {insight}")
            lines.append("")

        return "\n".join(lines).strip()

    def _get_interaction_icon(self, interaction_type: InteractionType) -> str:
        """Get icon for interaction type."""
        icons = {
            InteractionType.FRICTION: "⚠️",
            InteractionType.DELIGHT: "✨",
            InteractionType.NEUTRAL: "•",
        }
        return icons.get(interaction_type, "•")


# Register the formatter
@register(
    name="usage",
    description="Example usage scenarios with user journeys",
    extension=".md",
    supports_sections=False,
    supports_comparison=False,
)
class RegisteredUsageFormatter(UsageFormatter):
    """Registered version of UsageFormatter."""

    pass
