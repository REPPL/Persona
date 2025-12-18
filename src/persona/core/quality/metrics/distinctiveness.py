"""
Distinctiveness metric for persona quality scoring.

Evaluates how distinct a persona is from others in the set,
integrating with the existing PersonaComparator when available.
"""

from typing import TYPE_CHECKING, Any

from persona.core.generation.parser import Persona
from persona.core.quality.base import QualityMetric
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class DistinctivenessMetric(QualityMetric):
    """
    Evaluate how distinct a persona is from others in the set.

    Scoring breakdown:
    - Maximum similarity to any other persona (50%)
    - Average similarity to all others (30%)
    - Unique attribute count (20%)
    """

    def __init__(self, config: QualityConfig | None = None) -> None:
        """
        Initialise the distinctiveness metric.

        Args:
            config: Quality configuration with thresholds.
        """
        super().__init__(config)
        self._comparator = None

    @property
    def name(self) -> str:
        """Return the metric name."""
        return "distinctiveness"

    @property
    def description(self) -> str:
        """Return metric description."""
        return "Evaluate uniqueness compared to other personas"

    @property
    def requires_source_data(self) -> bool:
        """This metric does not require source data."""
        return False

    @property
    def requires_other_personas(self) -> bool:
        """This metric requires other personas for comparison."""
        return True

    @property
    def requires_evidence_report(self) -> bool:
        """This metric does not require evidence report."""
        return False

    def _get_comparator(self) -> Any:
        """Lazy load comparator to avoid circular imports."""
        if self._comparator is None:
            from persona.core.comparison.comparator import PersonaComparator

            self._comparator = PersonaComparator()
        return self._comparator

    def evaluate(
        self,
        persona: Persona,
        source_data: str | None = None,
        other_personas: list[Persona] | None = None,
        evidence_report: "EvidenceReport | None" = None,
    ) -> DimensionScore:
        """
        Calculate distinctiveness score for a persona.

        Args:
            persona: The persona to evaluate.
            other_personas: Other personas for comparison.

        Returns:
            DimensionScore with distinctiveness assessment.
        """
        issues: list[str] = []
        details: dict[str, Any] = {}

        if not other_personas:
            # Single persona - full distinctiveness by default
            return DimensionScore(
                dimension="distinctiveness",
                score=100.0,
                weight=self.config.weights["distinctiveness"],
                issues=["Only one persona - distinctiveness not applicable"],
                details={"note": "Single persona evaluation"},
            )

        # Filter out self if present in list
        other_personas = [p for p in other_personas if p.id != persona.id]

        if not other_personas:
            return DimensionScore(
                dimension="distinctiveness",
                score=100.0,
                weight=self.config.weights["distinctiveness"],
                issues=[],
                details={},
            )

        # Calculate similarities to all other personas
        similarities = self._calculate_similarities(persona, other_personas)

        if not similarities:
            return DimensionScore(
                dimension="distinctiveness",
                score=100.0,
                weight=self.config.weights["distinctiveness"],
                issues=[],
                details={},
            )

        # Max similarity score (50%)
        max_sim = max(s["similarity"] for s in similarities)
        max_sim_score = self._similarity_to_score(max_sim)
        details["max_similarity"] = round(max_sim, 2)

        if max_sim > self.config.max_similarity_threshold * 100:
            similar_to = next(s for s in similarities if s["similarity"] == max_sim)
            issues.append(
                f"Too similar to '{similar_to['other_name']}' "
                f"({max_sim:.0f}% similarity)"
            )

        # Average similarity score (30%)
        avg_sim = sum(s["similarity"] for s in similarities) / len(similarities)
        avg_sim_score = self._similarity_to_score(avg_sim)
        details["average_similarity"] = round(avg_sim, 2)

        # Unique attributes (20%)
        unique_score = self._calculate_unique_attributes(
            persona, other_personas, details
        )

        overall = max_sim_score * 0.50 + avg_sim_score * 0.30 + unique_score * 0.20

        details["similarity_details"] = [
            {
                "other_id": s["other_id"],
                "other_name": s["other_name"],
                "overall_similarity": round(s["similarity"], 2),
            }
            for s in similarities
        ]

        return DimensionScore(
            dimension="distinctiveness",
            score=overall,
            weight=self.config.weights["distinctiveness"],
            issues=issues,
            details=details,
        )

    def _calculate_similarities(
        self,
        persona: Persona,
        others: list[Persona],
    ) -> list[dict[str, Any]]:
        """Calculate similarity to each other persona."""
        similarities = []
        comparator = self._get_comparator()

        for other in others:
            try:
                result = comparator.compare(persona, other)
                similarities.append(
                    {
                        "other_id": other.id,
                        "other_name": other.name,
                        "similarity": result.similarity.overall,
                    }
                )
            except Exception:
                # If comparison fails, estimate based on text overlap
                similarity = self._estimate_similarity(persona, other)
                similarities.append(
                    {
                        "other_id": other.id,
                        "other_name": other.name,
                        "similarity": similarity,
                    }
                )

        return similarities

    def _estimate_similarity(self, p1: Persona, p2: Persona) -> float:
        """Estimate similarity when comparator is unavailable."""
        # Simple Jaccard similarity on goals and pain points
        p1_items = set()
        p2_items = set()

        for goal in p1.goals or []:
            p1_items.update(goal.lower().split())
        for pain in p1.pain_points or []:
            p1_items.update(pain.lower().split())

        for goal in p2.goals or []:
            p2_items.update(goal.lower().split())
        for pain in p2.pain_points or []:
            p2_items.update(pain.lower().split())

        if not p1_items or not p2_items:
            return 0.0

        intersection = len(p1_items & p2_items)
        union = len(p1_items | p2_items)

        return (intersection / union) * 100 if union > 0 else 0.0

    def _similarity_to_score(self, similarity: float) -> float:
        """
        Convert similarity percentage to distinctiveness score.

        0% similar = 100 distinctiveness
        100% similar = 0 distinctiveness
        """
        return max(0, 100 - similarity)

    def _calculate_unique_attributes(
        self,
        persona: Persona,
        others: list[Persona],
        details: dict[str, Any],
    ) -> float:
        """Calculate score based on unique goals/pain points."""
        # Collect all goals and pain points from others
        other_goals: set[str] = set()
        other_pains: set[str] = set()

        for other in others:
            other_goals.update(g.lower().strip() for g in (other.goals or []))
            other_pains.update(p.lower().strip() for p in (other.pain_points or []))

        # Count unique in this persona
        persona_goals = set(g.lower().strip() for g in (persona.goals or []))
        persona_pains = set(p.lower().strip() for p in (persona.pain_points or []))

        unique_goals = persona_goals - other_goals
        unique_pains = persona_pains - other_pains

        total = len(persona_goals) + len(persona_pains)
        unique = len(unique_goals) + len(unique_pains)

        details["unique_goals"] = len(unique_goals)
        details["unique_pain_points"] = len(unique_pains)
        details["total_attributes"] = total

        if total == 0:
            return 50.0

        return (unique / total) * 100
