"""
Persona comparison functionality.

This module provides the PersonaComparator class for comparing
personas and identifying similarities and differences.
"""

from dataclasses import dataclass, field
from typing import Any

from persona.core.generation.parser import Persona


@dataclass
class SimilarityScore:
    """
    Similarity score between two personas.

    Attributes:
        overall: Overall similarity (0-100).
        goals: Goal similarity (0-100).
        pain_points: Pain point similarity (0-100).
        demographics: Demographics similarity (0-100).
        behaviours: Behaviour similarity (0-100).
    """

    overall: float = 0.0
    goals: float = 0.0
    pain_points: float = 0.0
    demographics: float = 0.0
    behaviours: float = 0.0

    def to_dict(self) -> dict[str, float]:
        """Convert to dictionary."""
        return {
            "overall": round(self.overall, 2),
            "goals": round(self.goals, 2),
            "pain_points": round(self.pain_points, 2),
            "demographics": round(self.demographics, 2),
            "behaviours": round(self.behaviours, 2),
        }


@dataclass
class FieldDifference:
    """
    Difference in a specific field between personas.

    Attributes:
        field: Field name.
        persona_a: Value in first persona.
        persona_b: Value in second persona.
        similarity: How similar the values are (0-100).
    """

    field: str
    persona_a: Any
    persona_b: Any
    similarity: float = 0.0


@dataclass
class ComparisonResult:
    """
    Result of comparing two personas.

    Attributes:
        persona_a_id: ID of first persona.
        persona_b_id: ID of second persona.
        similarity: Similarity scores.
        shared_goals: Goals that appear in both.
        unique_goals_a: Goals only in first persona.
        unique_goals_b: Goals only in second persona.
        shared_pain_points: Pain points in both.
        unique_pain_points_a: Pain points only in first.
        unique_pain_points_b: Pain points only in second.
        demographic_differences: Differences in demographics.
    """

    persona_a_id: str
    persona_b_id: str
    similarity: SimilarityScore = field(default_factory=SimilarityScore)
    shared_goals: list[str] = field(default_factory=list)
    unique_goals_a: list[str] = field(default_factory=list)
    unique_goals_b: list[str] = field(default_factory=list)
    shared_pain_points: list[str] = field(default_factory=list)
    unique_pain_points_a: list[str] = field(default_factory=list)
    unique_pain_points_b: list[str] = field(default_factory=list)
    demographic_differences: list[FieldDifference] = field(default_factory=list)

    @property
    def is_similar(self) -> bool:
        """Check if personas are considered similar (>70% overall)."""
        return self.similarity.overall >= 70.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_a": self.persona_a_id,
            "persona_b": self.persona_b_id,
            "similarity": self.similarity.to_dict(),
            "is_similar": self.is_similar,
            "shared_goals": self.shared_goals,
            "unique_goals_a": self.unique_goals_a,
            "unique_goals_b": self.unique_goals_b,
            "shared_pain_points": self.shared_pain_points,
            "unique_pain_points_a": self.unique_pain_points_a,
            "unique_pain_points_b": self.unique_pain_points_b,
        }


class PersonaComparator:
    """
    Compares personas to identify similarities and differences.

    Provides methods for pairwise comparison and group analysis.

    Example:
        comparator = PersonaComparator()
        result = comparator.compare(persona_a, persona_b)
        print(f"Similarity: {result.similarity.overall}%")
    """

    def __init__(self, case_sensitive: bool = False) -> None:
        """
        Initialise the comparator.

        Args:
            case_sensitive: Whether string comparison is case sensitive.
        """
        self._case_sensitive = case_sensitive

    def compare(self, persona_a: Persona, persona_b: Persona) -> ComparisonResult:
        """
        Compare two personas.

        Args:
            persona_a: First persona.
            persona_b: Second persona.

        Returns:
            ComparisonResult with similarities and differences.
        """
        result = ComparisonResult(
            persona_a_id=persona_a.id,
            persona_b_id=persona_b.id,
        )

        # Compare goals
        goals_a = self._normalise_list(persona_a.goals or [])
        goals_b = self._normalise_list(persona_b.goals or [])
        result.shared_goals = self._find_shared(goals_a, goals_b)
        result.unique_goals_a = self._find_unique(goals_a, goals_b)
        result.unique_goals_b = self._find_unique(goals_b, goals_a)

        # Compare pain points
        pains_a = self._normalise_list(persona_a.pain_points or [])
        pains_b = self._normalise_list(persona_b.pain_points or [])
        result.shared_pain_points = self._find_shared(pains_a, pains_b)
        result.unique_pain_points_a = self._find_unique(pains_a, pains_b)
        result.unique_pain_points_b = self._find_unique(pains_b, pains_a)

        # Compare demographics
        result.demographic_differences = self._compare_demographics(
            persona_a.demographics or {},
            persona_b.demographics or {},
        )

        # Calculate similarity scores
        result.similarity = self._calculate_similarity(
            persona_a, persona_b, result
        )

        return result

    def compare_all(self, personas: list[Persona]) -> list[ComparisonResult]:
        """
        Compare all personas pairwise.

        Args:
            personas: List of personas to compare.

        Returns:
            List of ComparisonResult for each pair.
        """
        results = []
        n = len(personas)

        for i in range(n):
            for j in range(i + 1, n):
                result = self.compare(personas[i], personas[j])
                results.append(result)

        return results

    def find_most_similar(
        self,
        target: Persona,
        candidates: list[Persona],
    ) -> tuple[Persona | None, ComparisonResult | None]:
        """
        Find the most similar persona to a target.

        Args:
            target: Persona to match against.
            candidates: List of personas to search.

        Returns:
            Tuple of (most similar persona, comparison result).
        """
        if not candidates:
            return None, None

        best_match = None
        best_result = None
        best_score = -1.0

        for candidate in candidates:
            if candidate.id == target.id:
                continue

            result = self.compare(target, candidate)
            if result.similarity.overall > best_score:
                best_score = result.similarity.overall
                best_match = candidate
                best_result = result

        return best_match, best_result

    def find_duplicates(
        self,
        personas: list[Persona],
        threshold: float = 90.0,
    ) -> list[tuple[Persona, Persona, ComparisonResult]]:
        """
        Find potential duplicate personas.

        Args:
            personas: List of personas to check.
            threshold: Similarity threshold for duplicates (default 90%).

        Returns:
            List of (persona_a, persona_b, comparison) tuples.
        """
        duplicates = []

        for i, persona_a in enumerate(personas):
            for persona_b in personas[i + 1:]:
                result = self.compare(persona_a, persona_b)
                if result.similarity.overall >= threshold:
                    duplicates.append((persona_a, persona_b, result))

        return duplicates

    def group_by_similarity(
        self,
        personas: list[Persona],
        threshold: float = 60.0,
    ) -> list[list[Persona]]:
        """
        Group personas by similarity.

        Args:
            personas: List of personas to group.
            threshold: Similarity threshold for grouping.

        Returns:
            List of persona groups.
        """
        if not personas:
            return []

        # Simple greedy clustering
        assigned = set()
        groups = []

        for persona in personas:
            if persona.id in assigned:
                continue

            # Start a new group
            group = [persona]
            assigned.add(persona.id)

            # Find similar personas
            for other in personas:
                if other.id in assigned:
                    continue

                result = self.compare(persona, other)
                if result.similarity.overall >= threshold:
                    group.append(other)
                    assigned.add(other.id)

            groups.append(group)

        return groups

    def _normalise_list(self, items: list[str]) -> list[str]:
        """Normalise list items for comparison."""
        if self._case_sensitive:
            return [s.strip() for s in items]
        return [s.lower().strip() for s in items]

    def _find_shared(self, list_a: list[str], list_b: list[str]) -> list[str]:
        """Find items shared between lists."""
        set_b = set(list_b)
        return [item for item in list_a if item in set_b]

    def _find_unique(self, list_a: list[str], list_b: list[str]) -> list[str]:
        """Find items unique to first list."""
        set_b = set(list_b)
        return [item for item in list_a if item not in set_b]

    def _compare_demographics(
        self,
        demo_a: dict[str, Any],
        demo_b: dict[str, Any],
    ) -> list[FieldDifference]:
        """Compare demographic dictionaries."""
        differences = []
        all_keys = set(demo_a.keys()) | set(demo_b.keys())

        for key in all_keys:
            val_a = demo_a.get(key)
            val_b = demo_b.get(key)

            if val_a != val_b:
                similarity = 0.0
                if val_a is not None and val_b is not None:
                    # Simple string similarity
                    similarity = self._string_similarity(str(val_a), str(val_b))

                differences.append(FieldDifference(
                    field=key,
                    persona_a=val_a,
                    persona_b=val_b,
                    similarity=similarity,
                ))

        return differences

    def _string_similarity(self, str_a: str, str_b: str) -> float:
        """Calculate simple string similarity (0-100)."""
        if not self._case_sensitive:
            str_a = str_a.lower()
            str_b = str_b.lower()

        if str_a == str_b:
            return 100.0

        # Simple word overlap
        words_a = set(str_a.split())
        words_b = set(str_b.split())

        if not words_a or not words_b:
            return 0.0

        overlap = len(words_a & words_b)
        total = len(words_a | words_b)

        return (overlap / total) * 100 if total > 0 else 0.0

    def _calculate_similarity(
        self,
        persona_a: Persona,
        persona_b: Persona,
        result: ComparisonResult,
    ) -> SimilarityScore:
        """Calculate similarity scores."""
        # Goals similarity
        goals_total = (
            len(result.shared_goals) +
            len(result.unique_goals_a) +
            len(result.unique_goals_b)
        )
        goals_sim = (
            (len(result.shared_goals) / goals_total * 100)
            if goals_total > 0 else 0.0
        )

        # Pain points similarity
        pains_total = (
            len(result.shared_pain_points) +
            len(result.unique_pain_points_a) +
            len(result.unique_pain_points_b)
        )
        pains_sim = (
            (len(result.shared_pain_points) / pains_total * 100)
            if pains_total > 0 else 0.0
        )

        # Demographics similarity
        demo_a = persona_a.demographics or {}
        demo_b = persona_b.demographics or {}
        all_demo_keys = set(demo_a.keys()) | set(demo_b.keys())

        if all_demo_keys:
            matching = sum(
                1 for k in all_demo_keys
                if demo_a.get(k) == demo_b.get(k)
            )
            demo_sim = (matching / len(all_demo_keys)) * 100
        else:
            demo_sim = 0.0

        # Behaviours similarity
        behaviours_a = self._normalise_list(persona_a.behaviours or [])
        behaviours_b = self._normalise_list(persona_b.behaviours or [])
        shared_behaviours = self._find_shared(behaviours_a, behaviours_b)
        behaviours_total = len(set(behaviours_a) | set(behaviours_b))
        behaviours_sim = (
            (len(shared_behaviours) / behaviours_total * 100)
            if behaviours_total > 0 else 0.0
        )

        # Overall (weighted average)
        weights = {
            "goals": 0.35,
            "pain_points": 0.30,
            "demographics": 0.20,
            "behaviours": 0.15,
        }

        overall = (
            goals_sim * weights["goals"] +
            pains_sim * weights["pain_points"] +
            demo_sim * weights["demographics"] +
            behaviours_sim * weights["behaviours"]
        )

        return SimilarityScore(
            overall=overall,
            goals=goals_sim,
            pain_points=pains_sim,
            demographics=demo_sim,
            behaviours=behaviours_sim,
        )
