"""Consolidation mapping for multi-model outputs (F-070).

Compares personas across generations, calculates similarity,
and provides merge recommendations.
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PersonaSimilarity:
    """Similarity between two personas.

    Attributes:
        persona_a_id: First persona ID.
        persona_b_id: Second persona ID.
        similarity_score: Overall similarity (0.0 to 1.0).
        matching_attributes: Attributes that match.
        divergent_attributes: Attributes that differ.
        merge_recommendation: Whether merging is recommended.
        merge_reasoning: Reasoning for recommendation.
    """

    persona_a_id: str
    persona_b_id: str
    similarity_score: float
    matching_attributes: list[str] = field(default_factory=list)
    divergent_attributes: list[str] = field(default_factory=list)
    merge_recommendation: bool = False
    merge_reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_a": self.persona_a_id,
            "persona_b": self.persona_b_id,
            "similarity_score": self.similarity_score,
            "matching_attributes": self.matching_attributes,
            "divergent_attributes": self.divergent_attributes,
            "merge_recommendation": self.merge_recommendation,
            "merge_reasoning": self.merge_reasoning,
        }


@dataclass
class MergeRecommendation:
    """Recommendation for merging personas.

    Attributes:
        personas_to_merge: List of persona IDs to merge.
        merged_persona: The resulting merged persona.
        confidence: Confidence in the merge (0.0 to 1.0).
        reasoning: Explanation of the merge decision.
    """

    personas_to_merge: list[str]
    merged_persona: dict[str, Any]
    confidence: float
    reasoning: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "personas_to_merge": self.personas_to_merge,
            "merged_persona": self.merged_persona,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
        }


@dataclass
class ConsolidationMap:
    """Complete consolidation analysis.

    Attributes:
        similarities: Pairwise similarity scores.
        clusters: Groups of similar personas.
        merge_recommendations: Recommended merges.
        unique_personas: Personas with no close matches.
        consolidated_count: Number of personas after consolidation.
    """

    similarities: list[PersonaSimilarity] = field(default_factory=list)
    clusters: list[list[str]] = field(default_factory=list)
    merge_recommendations: list[MergeRecommendation] = field(default_factory=list)
    unique_personas: list[str] = field(default_factory=list)
    consolidated_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "similarities": [s.to_dict() for s in self.similarities],
            "clusters": self.clusters,
            "merge_recommendations": [m.to_dict() for m in self.merge_recommendations],
            "unique_personas": self.unique_personas,
            "consolidated_count": self.consolidated_count,
        }

    def to_display(self) -> str:
        """Generate human-readable display."""
        lines = [
            "Consolidation Map",
            "=" * 50,
            "",
            f"Total personas analysed: {sum(len(c) for c in self.clusters) + len(self.unique_personas)}",
            f"Clusters found: {len(self.clusters)}",
            f"Unique personas: {len(self.unique_personas)}",
            f"After consolidation: {self.consolidated_count} personas",
            "",
        ]

        # Show clusters
        if self.clusters:
            lines.append("Clusters (similar personas):")
            for i, cluster in enumerate(self.clusters, 1):
                lines.append(f"  Cluster {i}: {', '.join(cluster)}")

        # Show merge recommendations
        if self.merge_recommendations:
            lines.append("")
            lines.append("Merge Recommendations:")
            for rec in self.merge_recommendations:
                lines.append(
                    f"  → Merge: {', '.join(rec.personas_to_merge)} "
                    f"(confidence: {rec.confidence:.0%})"
                )
                lines.append(f"    Reason: {rec.reasoning}")

        # Show unique personas
        if self.unique_personas:
            lines.append("")
            lines.append("Unique Personas (no matches):")
            for p_id in self.unique_personas:
                lines.append(f"  • {p_id}")

        return "\n".join(lines)


class ConsolidationMapper:
    """Mapper for consolidating personas across models/runs.

    Compares personas, calculates similarity, identifies clusters,
    and provides merge recommendations.

    Example:
        >>> mapper = ConsolidationMapper()
        >>> result = mapper.consolidate([
        ...     {"id": "1", "role": "Developer", ...},
        ...     {"id": "2", "role": "Senior Dev", ...},
        ... ])
    """

    # Similarity threshold for merge recommendation
    MERGE_THRESHOLD = 0.75
    # Similarity threshold for clustering
    CLUSTER_THRESHOLD = 0.6

    def __init__(
        self,
        merge_threshold: float = 0.75,
        cluster_threshold: float = 0.6,
    ):
        """Initialise the mapper.

        Args:
            merge_threshold: Similarity threshold for recommending merge.
            cluster_threshold: Similarity threshold for clustering.
        """
        self.merge_threshold = merge_threshold
        self.cluster_threshold = cluster_threshold

    def consolidate(
        self,
        personas: list[dict[str, Any]],
    ) -> ConsolidationMap:
        """Analyse and consolidate personas.

        Args:
            personas: List of personas to consolidate.

        Returns:
            ConsolidationMap with analysis and recommendations.
        """
        if len(personas) < 2:
            return ConsolidationMap(
                unique_personas=[p.get("id", "unknown") for p in personas],
                consolidated_count=len(personas),
            )

        # Calculate pairwise similarities
        similarities = self._calculate_all_similarities(personas)

        # Build clusters
        clusters = self._build_clusters(personas, similarities)

        # Generate merge recommendations
        merge_recommendations = self._generate_merge_recommendations(
            personas, similarities
        )

        # Find unique personas (not in any cluster)
        clustered_ids = set()
        for cluster in clusters:
            clustered_ids.update(cluster)
        unique_personas = [
            p.get("id", "unknown")
            for p in personas
            if p.get("id", "unknown") not in clustered_ids
        ]

        # Calculate consolidated count
        # (one per cluster + all unique)
        consolidated_count = len(clusters) + len(unique_personas)

        return ConsolidationMap(
            similarities=similarities,
            clusters=clusters,
            merge_recommendations=merge_recommendations,
            unique_personas=unique_personas,
            consolidated_count=consolidated_count,
        )

    def calculate_similarity(
        self,
        persona_a: dict[str, Any],
        persona_b: dict[str, Any],
    ) -> PersonaSimilarity:
        """Calculate similarity between two personas.

        Args:
            persona_a: First persona.
            persona_b: Second persona.

        Returns:
            PersonaSimilarity with detailed comparison.
        """
        a_id = persona_a.get("id", "unknown-a")
        b_id = persona_b.get("id", "unknown-b")

        # Compare attributes
        matching = []
        divergent = []

        # Role comparison
        role_sim = self._compare_text(
            persona_a.get("role", ""),
            persona_b.get("role", ""),
        )
        if role_sim > 0.5:
            matching.append("role")
        else:
            divergent.append("role")

        # Goals comparison
        goals_a = set(persona_a.get("goals", []))
        goals_b = set(persona_b.get("goals", []))
        goals_sim = self._jaccard_similarity(goals_a, goals_b)
        if goals_sim > 0.3:
            matching.append("goals")
        elif goals_a or goals_b:
            divergent.append("goals")

        # Frustrations comparison
        frust_a = set(persona_a.get("frustrations", []))
        frust_b = set(persona_b.get("frustrations", []))
        frust_sim = self._jaccard_similarity(frust_a, frust_b)
        if frust_sim > 0.3:
            matching.append("frustrations")
        elif frust_a or frust_b:
            divergent.append("frustrations")

        # Background comparison
        bg_sim = self._compare_text(
            persona_a.get("background", ""),
            persona_b.get("background", ""),
        )
        if bg_sim > 0.3:
            matching.append("background")
        elif persona_a.get("background") or persona_b.get("background"):
            divergent.append("background")

        # Calculate overall similarity
        similarities = [role_sim, goals_sim, frust_sim, bg_sim]
        overall = sum(similarities) / len(similarities)

        # Determine merge recommendation
        merge_rec = overall >= self.merge_threshold
        if merge_rec:
            reasoning = (
                f"High similarity ({overall:.0%}) - " f"matching: {', '.join(matching)}"
            )
        else:
            reasoning = (
                f"Insufficient similarity ({overall:.0%}) - "
                f"divergent: {', '.join(divergent)}"
            )

        return PersonaSimilarity(
            persona_a_id=a_id,
            persona_b_id=b_id,
            similarity_score=overall,
            matching_attributes=matching,
            divergent_attributes=divergent,
            merge_recommendation=merge_rec,
            merge_reasoning=reasoning,
        )

    def merge_personas(
        self,
        personas: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Merge multiple personas into one.

        Args:
            personas: List of personas to merge.

        Returns:
            Merged persona dictionary.
        """
        if not personas:
            return {}

        if len(personas) == 1:
            return dict(personas[0])

        # Use first persona as base
        merged = dict(personas[0])
        merged["id"] = "merged-" + "-".join(p.get("id", "x")[:8] for p in personas)

        # Merge name (keep first)
        # merged["name"] stays as is

        # Merge role (most common)
        roles = [p.get("role", "") for p in personas if p.get("role")]
        if roles:
            merged["role"] = Counter(roles).most_common(1)[0][0]

        # Merge goals (union, deduplicated)
        all_goals = []
        for p in personas:
            all_goals.extend(p.get("goals", []))
        merged["goals"] = list(dict.fromkeys(all_goals))[:5]

        # Merge frustrations (union, deduplicated)
        all_frust = []
        for p in personas:
            all_frust.extend(p.get("frustrations", []))
        merged["frustrations"] = list(dict.fromkeys(all_frust))[:3]

        # Track contributing sources
        merged["merged_from"] = [p.get("id", "unknown") for p in personas]
        merged["merge_count"] = len(personas)

        return merged

    def _calculate_all_similarities(
        self,
        personas: list[dict[str, Any]],
    ) -> list[PersonaSimilarity]:
        """Calculate similarities between all persona pairs."""
        similarities = []
        for i, p1 in enumerate(personas):
            for p2 in personas[i + 1 :]:
                sim = self.calculate_similarity(p1, p2)
                similarities.append(sim)
        return similarities

    def _build_clusters(
        self,
        personas: list[dict[str, Any]],
        similarities: list[PersonaSimilarity],
    ) -> list[list[str]]:
        """Build clusters of similar personas."""
        # Create adjacency based on similarity threshold
        adjacency: dict[str, set[str]] = {}
        for p in personas:
            adjacency[p.get("id", "unknown")] = set()

        for sim in similarities:
            if sim.similarity_score >= self.cluster_threshold:
                adjacency[sim.persona_a_id].add(sim.persona_b_id)
                adjacency[sim.persona_b_id].add(sim.persona_a_id)

        # Find connected components (simple DFS)
        visited = set()
        clusters = []

        for p_id in adjacency:
            if p_id not in visited and adjacency[p_id]:
                cluster = []
                stack = [p_id]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        cluster.append(current)
                        stack.extend(adjacency[current] - visited)
                if len(cluster) > 1:
                    clusters.append(cluster)

        return clusters

    def _generate_merge_recommendations(
        self,
        personas: list[dict[str, Any]],
        similarities: list[PersonaSimilarity],
    ) -> list[MergeRecommendation]:
        """Generate merge recommendations from similarities."""
        recommendations = []
        persona_map = {p.get("id", "unknown"): p for p in personas}

        # Find pairs that should be merged
        for sim in similarities:
            if sim.merge_recommendation:
                p_a = persona_map.get(sim.persona_a_id, {})
                p_b = persona_map.get(sim.persona_b_id, {})

                merged = self.merge_personas([p_a, p_b])

                recommendations.append(
                    MergeRecommendation(
                        personas_to_merge=[sim.persona_a_id, sim.persona_b_id],
                        merged_persona=merged,
                        confidence=sim.similarity_score,
                        reasoning=sim.merge_reasoning,
                    )
                )

        return recommendations

    def _compare_text(self, text_a: str, text_b: str) -> float:
        """Compare two text strings using word overlap."""
        if not text_a or not text_b:
            return 0.0 if text_a != text_b else 1.0

        words_a = set(re.findall(r"\b\w+\b", text_a.lower()))
        words_b = set(re.findall(r"\b\w+\b", text_b.lower()))

        return self._jaccard_similarity(words_a, words_b)

    def _jaccard_similarity(self, set_a: set, set_b: set) -> float:
        """Calculate Jaccard similarity between two sets."""
        if not set_a and not set_b:
            return 1.0
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0


def consolidate_personas(
    personas: list[dict[str, Any]],
    merge_threshold: float = 0.75,
) -> ConsolidationMap:
    """Convenience function for persona consolidation.

    Args:
        personas: List of personas to consolidate.
        merge_threshold: Similarity threshold for merge.

    Returns:
        ConsolidationMap with analysis and recommendations.
    """
    mapper = ConsolidationMapper(merge_threshold=merge_threshold)
    return mapper.consolidate(personas)
