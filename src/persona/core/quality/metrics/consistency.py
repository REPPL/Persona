"""
Consistency metric for persona quality scoring.

Evaluates internal consistency of a persona, checking for
contradictions and alignment between different attributes.
"""

import re
from typing import Any

from persona.core.generation.parser import Persona
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import DimensionScore


class ConsistencyMetric:
    """
    Evaluate internal consistency of a persona.

    Scoring breakdown:
    - Demographic-goal alignment: 35%
    - Behaviour-pain point coherence: 30%
    - Quote alignment with persona traits: 20%
    - Internal list uniqueness: 15%
    """

    # Age-related keywords for goal consistency
    AGE_CAREER_PATTERNS: dict[str, list[str]] = {
        "young": ["entry-level", "first job", "graduate", "intern", "student"],
        "senior": ["retirement", "legacy", "mentoring", "leadership"],
    }

    def __init__(self, config: QualityConfig | None = None) -> None:
        """
        Initialise the consistency metric.

        Args:
            config: Quality configuration with thresholds.
        """
        self.config = config or QualityConfig()

    def evaluate(self, persona: Persona) -> DimensionScore:
        """
        Calculate consistency score for a persona.

        Args:
            persona: The persona to evaluate.

        Returns:
            DimensionScore with consistency assessment.
        """
        issues: list[str] = []
        details: dict[str, Any] = {}

        # Demographic-goal alignment (35%)
        demo_goal_score = self._check_demographic_goal_alignment(
            persona, issues, details
        )

        # Behaviour-pain coherence (30%)
        behaviour_pain_score = self._check_behaviour_pain_coherence(
            persona, issues, details
        )

        # Quote alignment (20%)
        quote_score = self._check_quote_alignment(persona, issues, details)

        # Internal uniqueness (15%)
        uniqueness_score = self._check_internal_uniqueness(persona, issues, details)

        # Weighted combination
        overall = (
            demo_goal_score * 0.35 +
            behaviour_pain_score * 0.30 +
            quote_score * 0.20 +
            uniqueness_score * 0.15
        )

        return DimensionScore(
            dimension="consistency",
            score=overall,
            weight=self.config.weights["consistency"],
            issues=issues,
            details=details,
        )

    def _check_demographic_goal_alignment(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check if goals align with demographics."""
        if not persona.demographics or not persona.goals:
            return 75.0  # Neutral if no data to check

        conflicts: list[str] = []

        # Extract age range if present
        age_info = persona.demographics.get("age") or persona.demographics.get(
            "age_range"
        )

        if age_info:
            age_str = str(age_info).lower()

            # Check young vs senior goal conflicts
            young_indicators = ["18", "19", "20", "21", "22", "23", "24", "25"]
            senior_indicators = ["55", "60", "65", "70"]

            if any(x in age_str for x in young_indicators):
                # Young person - shouldn't have senior goals
                for goal in persona.goals:
                    goal_lower = goal.lower()
                    if any(kw in goal_lower for kw in self.AGE_CAREER_PATTERNS["senior"]):
                        conflicts.append(
                            f"Age-goal mismatch: young person with senior goal '{goal[:50]}'"
                        )

            elif any(x in age_str for x in senior_indicators):
                # Senior person - shouldn't have early-career goals
                for goal in persona.goals:
                    goal_lower = goal.lower()
                    if any(kw in goal_lower for kw in self.AGE_CAREER_PATTERNS["young"]):
                        conflicts.append(
                            f"Age-goal mismatch: senior person with early-career goal '{goal[:50]}'"
                        )

        issues.extend(conflicts)
        details["demographic_goal_conflicts"] = conflicts

        # Score: 100 if no conflicts, -20 per conflict
        return max(0, 100 - (len(conflicts) * 20))

    def _check_behaviour_pain_coherence(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check if behaviours and pain points tell a coherent story."""
        if not persona.behaviours or not persona.pain_points:
            return 75.0

        contradictions: list[str] = []

        for behaviour in persona.behaviours:
            behaviour_lower = behaviour.lower()
            for pain in persona.pain_points:
                pain_lower = pain.lower()

                if self._is_contradiction(behaviour_lower, pain_lower):
                    contradictions.append(
                        f"Contradiction: behaviour '{behaviour[:40]}' "
                        f"vs pain '{pain[:40]}'"
                    )

        issues.extend(contradictions)
        details["behaviour_pain_contradictions"] = contradictions

        return max(0, 100 - (len(contradictions) * 25))

    def _is_contradiction(self, behaviour: str, pain: str) -> bool:
        """Detect if behaviour and pain point contradict."""
        # Simple pattern matching for obvious contradictions
        contradiction_pairs = [
            ("loves", "hates"),
            ("easy", "difficult"),
            ("quick", "slow"),
            ("enjoys", "avoids"),
            ("comfortable", "uncomfortable"),
            ("confident", "anxious"),
        ]

        for pos, neg in contradiction_pairs:
            if pos in behaviour and neg in pain:
                # Check if discussing same topic
                behaviour_words = set(re.findall(r'\w+', behaviour))
                pain_words = set(re.findall(r'\w+', pain))
                overlap = behaviour_words & pain_words
                # Need shared context words beyond the contradiction pair
                overlap -= {pos, neg}
                if len(overlap) >= 2:
                    return True

        return False

    def _check_quote_alignment(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check if quotes align with persona's stated characteristics."""
        if not persona.quotes:
            return 75.0

        aligned = 0
        total = len(persona.quotes)

        # Build set of trait words from goals and pain points
        all_traits: set[str] = set()
        for goal in (persona.goals or []):
            all_traits.update(re.findall(r'\w{4,}', goal.lower()))
        for pain in (persona.pain_points or []):
            all_traits.update(re.findall(r'\w{4,}', pain.lower()))

        # Remove common words
        stopwords = {
            "the", "and", "for", "that", "this", "with", "have", "from",
            "they", "what", "when", "where", "which", "their", "there",
            "would", "could", "should", "about", "just", "been", "being",
        }
        all_traits -= stopwords

        for quote in persona.quotes:
            quote_words = set(re.findall(r'\w{4,}', quote.lower()))
            if quote_words & all_traits:
                aligned += 1

        details["quote_alignment_rate"] = round(
            aligned / total if total > 0 else 0, 2
        )

        return (aligned / total) * 100 if total > 0 else 75.0

    def _check_internal_uniqueness(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check for duplicate content within persona."""
        duplicates: list[str] = []

        # Check goals for duplicates
        if persona.goals:
            goal_set = set(g.lower().strip() for g in persona.goals)
            if len(goal_set) < len(persona.goals):
                dup_count = len(persona.goals) - len(goal_set)
                duplicates.append(f"{dup_count} duplicate goal(s) detected")

        # Check pain points for duplicates
        if persona.pain_points:
            pain_set = set(p.lower().strip() for p in persona.pain_points)
            if len(pain_set) < len(persona.pain_points):
                dup_count = len(persona.pain_points) - len(pain_set)
                duplicates.append(f"{dup_count} duplicate pain point(s) detected")

        # Check behaviours for duplicates
        if persona.behaviours:
            behaviour_set = set(b.lower().strip() for b in persona.behaviours)
            if len(behaviour_set) < len(persona.behaviours):
                dup_count = len(persona.behaviours) - len(behaviour_set)
                duplicates.append(f"{dup_count} duplicate behaviour(s) detected")

        issues.extend(duplicates)
        details["internal_duplicates"] = duplicates

        return 100 if not duplicates else max(0, 100 - (len(duplicates) * 15))
