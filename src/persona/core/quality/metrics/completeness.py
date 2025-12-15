"""
Completeness metric for persona quality scoring.

Evaluates how completely a persona's fields are populated,
including field depth and content richness.
"""

from typing import TYPE_CHECKING, Any

from persona.core.generation.parser import Persona
from persona.core.quality.base import QualityMetric
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class CompletenessMetric(QualityMetric):
    """
    Evaluate how completely a persona's fields are populated.

    Scoring breakdown:
    - Required fields present: 40%
    - Expected fields populated: 30%
    - Field depth (list lengths): 20%
    - Field richness (content quality): 10%
    """

    @property
    def name(self) -> str:
        """Return the metric name."""
        return "completeness"

    @property
    def description(self) -> str:
        """Return metric description."""
        return "Evaluate field population and content depth"

    @property
    def requires_source_data(self) -> bool:
        """This metric does not require source data."""
        return False

    @property
    def requires_other_personas(self) -> bool:
        """This metric does not require other personas."""
        return False

    @property
    def requires_evidence_report(self) -> bool:
        """This metric does not require evidence report."""
        return False

    def evaluate(
        self,
        persona: Persona,
        source_data: str | None = None,
        other_personas: list[Persona] | None = None,
        evidence_report: "EvidenceReport | None" = None,
    ) -> DimensionScore:
        """
        Calculate completeness score for a persona.

        Args:
            persona: The persona to evaluate.

        Returns:
            DimensionScore with completeness assessment.
        """
        issues: list[str] = []
        details: dict[str, Any] = {}

        # Required fields (40%)
        required_score = self._check_required_fields(persona, issues)
        details["required_fields_score"] = required_score

        # Expected fields (30%)
        expected_score = self._check_expected_fields(persona, issues, details)
        details["expected_fields_score"] = expected_score

        # Field depth (20%)
        depth_score = self._check_field_depth(persona, issues, details)
        details["field_depth_score"] = depth_score

        # Field richness (10%)
        richness_score = self._check_field_richness(persona, details)
        details["richness_score"] = richness_score

        # Weighted combination
        overall = (
            required_score * 0.40 +
            expected_score * 0.30 +
            depth_score * 0.20 +
            richness_score * 0.10
        )

        return DimensionScore(
            dimension="completeness",
            score=overall,
            weight=self.config.weights["completeness"],
            issues=issues,
            details=details,
        )

    def _check_required_fields(
        self, persona: Persona, issues: list[str]
    ) -> float:
        """Check required fields are present and non-empty."""
        present = 0
        total = len(self.config.required_fields)

        for field_name in self.config.required_fields:
            value = getattr(persona, field_name, None)
            if value and (isinstance(value, str) and value.strip()):
                present += 1
            elif value and not isinstance(value, str):
                present += 1
            else:
                issues.append(f"Missing required field: {field_name}")

        return (present / total) * 100 if total > 0 else 100

    def _check_expected_fields(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check expected fields have content."""
        populated = 0
        total = len(self.config.expected_fields)
        field_status: dict[str, bool] = {}

        for field_name in self.config.expected_fields:
            value = getattr(persona, field_name, None)
            if self._has_content(value):
                populated += 1
                field_status[field_name] = True
            else:
                issues.append(f"Expected field empty or missing: {field_name}")
                field_status[field_name] = False

        details["field_status"] = field_status
        return (populated / total) * 100 if total > 0 else 100

    def _check_field_depth(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check lists have sufficient items."""
        depth_scores: list[float] = []
        depth_details: dict[str, int] = {}

        # Goals
        goals_count = len(persona.goals or [])
        goals_score = min(100, (goals_count / self.config.min_goals) * 100)
        depth_details["goals_count"] = goals_count
        depth_scores.append(goals_score)
        if goals_count < self.config.min_goals:
            issues.append(
                f"Insufficient goals: {goals_count}/{self.config.min_goals}"
            )

        # Pain points
        pains_count = len(persona.pain_points or [])
        pains_score = min(100, (pains_count / self.config.min_pain_points) * 100)
        depth_details["pain_points_count"] = pains_count
        depth_scores.append(pains_score)
        if pains_count < self.config.min_pain_points:
            issues.append(
                f"Insufficient pain points: {pains_count}/{self.config.min_pain_points}"
            )

        # Behaviours
        behaviours_count = len(persona.behaviours or [])
        if self.config.min_behaviours > 0:
            behaviours_score = min(
                100, (behaviours_count / self.config.min_behaviours) * 100
            )
        else:
            behaviours_score = 100 if behaviours_count > 0 else 50
        depth_details["behaviours_count"] = behaviours_count
        depth_scores.append(behaviours_score)

        # Quotes
        quotes_count = len(persona.quotes or [])
        if self.config.min_quotes > 0:
            quotes_score = min(100, (quotes_count / self.config.min_quotes) * 100)
        else:
            quotes_score = 100 if quotes_count > 0 else 50
        depth_details["quotes_count"] = quotes_count
        depth_scores.append(quotes_score)

        details["depth"] = depth_details
        return sum(depth_scores) / len(depth_scores) if depth_scores else 100

    def _check_field_richness(
        self,
        persona: Persona,
        details: dict[str, Any],
    ) -> float:
        """Check content has sufficient detail (word counts, etc.)."""
        richness_scores: list[float] = []

        # Check average goal length (penalise very short goals)
        if persona.goals:
            avg_goal_words = sum(
                len(g.split()) for g in persona.goals
            ) / len(persona.goals)
            # 5+ words is considered good
            goal_richness = min(100, (avg_goal_words / 5) * 100)
            richness_scores.append(goal_richness)
            details["avg_goal_words"] = round(avg_goal_words, 1)

        # Check demographics completeness
        if persona.demographics:
            demo_count = len([v for v in persona.demographics.values() if v])
            demo_richness = min(100, (demo_count / 3) * 100)  # 3+ is good
            richness_scores.append(demo_richness)
            details["demographics_fields"] = demo_count
        else:
            details["demographics_fields"] = 0

        # Check pain point specificity
        if persona.pain_points:
            avg_pain_words = sum(
                len(p.split()) for p in persona.pain_points
            ) / len(persona.pain_points)
            pain_richness = min(100, (avg_pain_words / 5) * 100)
            richness_scores.append(pain_richness)
            details["avg_pain_point_words"] = round(avg_pain_words, 1)

        return sum(richness_scores) / len(richness_scores) if richness_scores else 50

    def _has_content(self, value: Any) -> bool:
        """Check if a value has meaningful content."""
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True
