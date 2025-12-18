"""
Persona clustering functionality.

This module provides the PersonaClusterer class for grouping
similar personas and suggesting consolidation.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from persona.core.generation.parser import Persona


class ClusterMethod(Enum):
    """Clustering method options."""

    SIMILARITY = "similarity"  # Based on similarity threshold
    HIERARCHICAL = "hierarchical"  # Hierarchical clustering
    KMEANS = "kmeans"  # K-means style clustering


@dataclass
class ConsolidationSuggestion:
    """
    A suggestion for consolidating personas.

    Attributes:
        personas: Personas to consolidate.
        reason: Why consolidation is suggested.
        similarity_score: How similar the personas are.
        merged_name: Suggested name for merged persona.
        confidence: Confidence in the suggestion (0-1).
    """

    personas: list[Persona]
    reason: str
    similarity_score: float
    merged_name: str = ""
    confidence: float = 0.0

    def __post_init__(self):
        """Generate merged name if not provided."""
        if not self.merged_name and self.personas:
            names = [p.name for p in self.personas if p.name]
            if names:
                self.merged_name = f"Merged: {' + '.join(names[:3])}"
                if len(names) > 3:
                    self.merged_name += f" (+{len(names) - 3} more)"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_ids": [p.id for p in self.personas],
            "persona_names": [p.name for p in self.personas],
            "reason": self.reason,
            "similarity_score": self.similarity_score,
            "merged_name": self.merged_name,
            "confidence": self.confidence,
        }


@dataclass
class Cluster:
    """
    A cluster of similar personas.

    Attributes:
        id: Unique cluster identifier.
        personas: Personas in this cluster.
        centroid_id: ID of the most representative persona.
        cohesion: Internal cohesion score (0-1).
        label: Human-readable cluster label.
        characteristics: Common characteristics.
    """

    id: str
    personas: list[Persona] = field(default_factory=list)
    centroid_id: str = ""
    cohesion: float = 0.0
    label: str = ""
    characteristics: dict[str, Any] = field(default_factory=dict)

    @property
    def size(self) -> int:
        """Number of personas in cluster."""
        return len(self.personas)

    @property
    def centroid(self) -> Persona | None:
        """Get the centroid persona."""
        for p in self.personas:
            if p.id == self.centroid_id:
                return p
        return self.personas[0] if self.personas else None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "size": self.size,
            "centroid_id": self.centroid_id,
            "cohesion": self.cohesion,
            "label": self.label,
            "characteristics": self.characteristics,
            "persona_ids": [p.id for p in self.personas],
        }


@dataclass
class ClusterResult:
    """
    Result of a clustering operation.

    Attributes:
        success: Whether clustering succeeded.
        clusters: List of clusters.
        consolidation_suggestions: Suggested merges.
        method: Clustering method used.
        parameters: Parameters used.
        error: Error message if failed.
    """

    success: bool
    clusters: list[Cluster] = field(default_factory=list)
    consolidation_suggestions: list[ConsolidationSuggestion] = field(
        default_factory=list
    )
    method: ClusterMethod = ClusterMethod.SIMILARITY
    parameters: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def cluster_count(self) -> int:
        """Number of clusters."""
        return len(self.clusters)

    @property
    def total_personas(self) -> int:
        """Total personas across all clusters."""
        return sum(c.size for c in self.clusters)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "cluster_count": self.cluster_count,
            "total_personas": self.total_personas,
            "method": self.method.value,
            "parameters": self.parameters,
            "clusters": [c.to_dict() for c in self.clusters],
            "consolidation_suggestions": [
                s.to_dict() for s in self.consolidation_suggestions
            ],
            "error": self.error,
        }


class PersonaClusterer:
    """
    Clusters personas to identify similar groups.

    Provides functionality for grouping similar personas and
    suggesting consolidation to reduce redundancy.

    Example:
        clusterer = PersonaClusterer()
        result = clusterer.cluster(personas, method=ClusterMethod.SIMILARITY)
        for cluster in result.clusters:
            print(f"Cluster {cluster.id}: {cluster.size} personas")
    """

    # Default weights for similarity calculation
    DEFAULT_WEIGHTS = {
        "goals": 0.35,
        "pain_points": 0.30,
        "demographics": 0.20,
        "behaviours": 0.15,
    }

    def __init__(
        self,
        similarity_threshold: float = 0.6,
        weights: dict[str, float] | None = None,
    ) -> None:
        """
        Initialise the clusterer.

        Args:
            similarity_threshold: Minimum similarity to cluster (0-1).
            weights: Weights for similarity calculation.
        """
        self.similarity_threshold = similarity_threshold
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

    def cluster(
        self,
        personas: list[Persona],
        method: ClusterMethod = ClusterMethod.SIMILARITY,
        **kwargs: Any,
    ) -> ClusterResult:
        """
        Cluster personas into groups.

        Args:
            personas: Personas to cluster.
            method: Clustering method to use.
            **kwargs: Additional method-specific parameters.

        Returns:
            ClusterResult with clusters and suggestions.
        """
        # Preserve original parameters for result
        original_kwargs = kwargs.copy()

        if not personas:
            return ClusterResult(
                success=True,
                clusters=[],
                method=method,
                parameters=original_kwargs,
            )

        try:
            if method == ClusterMethod.SIMILARITY:
                clusters = self._cluster_by_similarity(personas, **kwargs)
            elif method == ClusterMethod.HIERARCHICAL:
                clusters = self._cluster_hierarchical(personas, **kwargs)
            elif method == ClusterMethod.KMEANS:
                k = kwargs.pop("k", self._estimate_k(len(personas)))
                clusters = self._cluster_kmeans(personas, k, **kwargs)
            else:
                clusters = self._cluster_by_similarity(personas, **kwargs)

            # Generate consolidation suggestions
            suggestions = self._generate_suggestions(clusters)

            return ClusterResult(
                success=True,
                clusters=clusters,
                consolidation_suggestions=suggestions,
                method=method,
                parameters=original_kwargs,
            )

        except Exception as e:
            return ClusterResult(
                success=False,
                error=str(e),
                method=method,
                parameters=original_kwargs,
            )

    def calculate_similarity(
        self,
        persona_a: Persona,
        persona_b: Persona,
    ) -> float:
        """
        Calculate similarity between two personas.

        Args:
            persona_a: First persona.
            persona_b: Second persona.

        Returns:
            Similarity score (0-1).
        """
        scores = {}

        # Goals similarity
        goals_a = set(persona_a.goals or [])
        goals_b = set(persona_b.goals or [])
        scores["goals"] = self._jaccard_similarity(goals_a, goals_b)

        # Pain points similarity
        pain_a = set(persona_a.pain_points or [])
        pain_b = set(persona_b.pain_points or [])
        scores["pain_points"] = self._jaccard_similarity(pain_a, pain_b)

        # Demographics similarity
        demo_a = persona_a.demographics or {}
        demo_b = persona_b.demographics or {}
        scores["demographics"] = self._dict_similarity(demo_a, demo_b)

        # Behaviours similarity
        behav_a = set(persona_a.behaviours or [])
        behav_b = set(persona_b.behaviours or [])
        scores["behaviours"] = self._jaccard_similarity(behav_a, behav_b)

        # Weighted average
        total = sum(scores.get(k, 0) * self.weights.get(k, 0) for k in self.weights)

        return total

    def find_similar(
        self,
        target: Persona,
        candidates: list[Persona],
        threshold: float | None = None,
    ) -> list[tuple[Persona, float]]:
        """
        Find personas similar to a target.

        Args:
            target: Target persona.
            candidates: Candidates to compare.
            threshold: Minimum similarity (default: instance threshold).

        Returns:
            List of (persona, score) tuples, sorted by score descending.
        """
        if threshold is None:
            threshold = self.similarity_threshold

        results = []
        for candidate in candidates:
            if candidate.id == target.id:
                continue

            score = self.calculate_similarity(target, candidate)
            if score >= threshold:
                results.append((candidate, score))

        return sorted(results, key=lambda x: x[1], reverse=True)

    def suggest_consolidation(
        self,
        personas: list[Persona],
        threshold: float | None = None,
    ) -> list[ConsolidationSuggestion]:
        """
        Suggest which personas could be consolidated.

        Args:
            personas: Personas to analyse.
            threshold: Minimum similarity for suggestion.

        Returns:
            List of consolidation suggestions.
        """
        if threshold is None:
            threshold = self.similarity_threshold

        # Build similarity matrix
        n = len(personas)
        similarities: dict[tuple[str, str], float] = {}

        for i in range(n):
            for j in range(i + 1, n):
                score = self.calculate_similarity(personas[i], personas[j])
                if score >= threshold:
                    similarities[(personas[i].id, personas[j].id)] = score

        # Group highly similar personas
        suggestions = []
        processed: set[str] = set()

        for (id_a, id_b), score in sorted(
            similarities.items(), key=lambda x: x[1], reverse=True
        ):
            if id_a in processed or id_b in processed:
                continue

            # Find all personas similar to this pair
            group = [p for p in personas if p.id in (id_a, id_b)]

            # Find reason for similarity
            reason = self._determine_similarity_reason(group[0], group[1])

            suggestion = ConsolidationSuggestion(
                personas=group,
                reason=reason,
                similarity_score=score,
                confidence=min(score, 0.95),  # Cap confidence
            )
            suggestions.append(suggestion)

            processed.add(id_a)
            processed.add(id_b)

        return suggestions

    def _cluster_by_similarity(
        self,
        personas: list[Persona],
        **kwargs: Any,
    ) -> list[Cluster]:
        """Cluster using similarity threshold."""
        threshold = kwargs.get("threshold", self.similarity_threshold)
        clusters: list[Cluster] = []
        assigned: set[str] = set()

        for persona in personas:
            if persona.id in assigned:
                continue

            # Find all similar personas
            cluster_members = [persona]
            assigned.add(persona.id)

            for other in personas:
                if other.id in assigned:
                    continue

                score = self.calculate_similarity(persona, other)
                if score >= threshold:
                    cluster_members.append(other)
                    assigned.add(other.id)

            # Create cluster
            cluster = Cluster(
                id=f"cluster_{len(clusters) + 1}",
                personas=cluster_members,
                centroid_id=persona.id,
                cohesion=self._calculate_cohesion(cluster_members),
                label=self._generate_cluster_label(cluster_members),
                characteristics=self._extract_characteristics(cluster_members),
            )
            clusters.append(cluster)

        return clusters

    def _cluster_hierarchical(
        self,
        personas: list[Persona],
        **kwargs: Any,
    ) -> list[Cluster]:
        """Hierarchical agglomerative clustering."""
        # Start with each persona in its own cluster
        clusters: list[list[Persona]] = [[p] for p in personas]

        # Merge until threshold
        threshold = kwargs.get("threshold", self.similarity_threshold)

        while len(clusters) > 1:
            # Find most similar pair
            best_i, best_j = 0, 1
            best_score = -1.0

            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    score = self._cluster_similarity(clusters[i], clusters[j])
                    if score > best_score:
                        best_score = score
                        best_i, best_j = i, j

            # Stop if best pair is below threshold
            if best_score < threshold:
                break

            # Merge clusters
            merged = clusters[best_i] + clusters[best_j]
            clusters = [
                c for idx, c in enumerate(clusters) if idx not in (best_i, best_j)
            ]
            clusters.append(merged)

        # Convert to Cluster objects
        return [
            Cluster(
                id=f"cluster_{i + 1}",
                personas=members,
                centroid_id=self._find_centroid(members).id,
                cohesion=self._calculate_cohesion(members),
                label=self._generate_cluster_label(members),
                characteristics=self._extract_characteristics(members),
            )
            for i, members in enumerate(clusters)
        ]

    def _cluster_kmeans(
        self,
        personas: list[Persona],
        k: int,
        **kwargs: Any,
    ) -> list[Cluster]:
        """K-means style clustering."""
        if k >= len(personas):
            # Each persona in its own cluster
            return [
                Cluster(
                    id=f"cluster_{i + 1}",
                    personas=[p],
                    centroid_id=p.id,
                    cohesion=1.0,
                    label=p.name or f"Single: {p.id}",
                )
                for i, p in enumerate(personas)
            ]

        # Initialise: pick k random centroids
        import random

        centroids = random.sample(personas, k)

        max_iterations = kwargs.get("max_iterations", 10)

        for _ in range(max_iterations):
            # Assign personas to nearest centroid
            assignments: dict[str, list[Persona]] = {c.id: [] for c in centroids}

            for persona in personas:
                # Find nearest centroid
                best_centroid = centroids[0]
                best_score = self.calculate_similarity(persona, best_centroid)

                for centroid in centroids[1:]:
                    score = self.calculate_similarity(persona, centroid)
                    if score > best_score:
                        best_score = score
                        best_centroid = centroid

                assignments[best_centroid.id].append(persona)

            # Update centroids
            new_centroids = []
            for centroid_id, members in assignments.items():
                if members:
                    new_centroid = self._find_centroid(members)
                    new_centroids.append(new_centroid)

            if len(new_centroids) == 0:
                break

            centroids = new_centroids

        # Build final clusters
        final_assignments: dict[str, list[Persona]] = {c.id: [] for c in centroids}

        for persona in personas:
            best_centroid = centroids[0]
            best_score = self.calculate_similarity(persona, best_centroid)

            for centroid in centroids[1:]:
                score = self.calculate_similarity(persona, centroid)
                if score > best_score:
                    best_score = score
                    best_centroid = centroid

            final_assignments[best_centroid.id].append(persona)

        return [
            Cluster(
                id=f"cluster_{i + 1}",
                personas=members,
                centroid_id=centroid_id,
                cohesion=self._calculate_cohesion(members),
                label=self._generate_cluster_label(members),
                characteristics=self._extract_characteristics(members),
            )
            for i, (centroid_id, members) in enumerate(final_assignments.items())
            if members
        ]

    def _jaccard_similarity(self, set_a: set, set_b: set) -> float:
        """Calculate Jaccard similarity between sets."""
        if not set_a and not set_b:
            return 1.0
        if not set_a or not set_b:
            return 0.0

        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0

    def _dict_similarity(
        self,
        dict_a: dict[str, Any],
        dict_b: dict[str, Any],
    ) -> float:
        """Calculate similarity between dictionaries."""
        if not dict_a and not dict_b:
            return 1.0
        if not dict_a or not dict_b:
            return 0.0

        all_keys = set(dict_a.keys()) | set(dict_b.keys())
        if not all_keys:
            return 1.0

        matches = sum(
            1
            for k in all_keys
            if dict_a.get(k) == dict_b.get(k) and k in dict_a and k in dict_b
        )
        return matches / len(all_keys)

    def _cluster_similarity(
        self,
        cluster_a: list[Persona],
        cluster_b: list[Persona],
    ) -> float:
        """Calculate average linkage similarity between clusters."""
        if not cluster_a or not cluster_b:
            return 0.0

        total = 0.0
        count = 0

        for pa in cluster_a:
            for pb in cluster_b:
                total += self.calculate_similarity(pa, pb)
                count += 1

        return total / count if count > 0 else 0.0

    def _find_centroid(self, personas: list[Persona]) -> Persona:
        """Find the most central persona in a group."""
        if len(personas) == 1:
            return personas[0]

        best_persona = personas[0]
        best_total = 0.0

        for candidate in personas:
            total = sum(
                self.calculate_similarity(candidate, other)
                for other in personas
                if other.id != candidate.id
            )
            if total > best_total:
                best_total = total
                best_persona = candidate

        return best_persona

    def _calculate_cohesion(self, personas: list[Persona]) -> float:
        """Calculate internal cohesion of a group."""
        if len(personas) <= 1:
            return 1.0

        total = 0.0
        count = 0

        for i, pa in enumerate(personas):
            for pb in personas[i + 1 :]:
                total += self.calculate_similarity(pa, pb)
                count += 1

        return total / count if count > 0 else 0.0

    def _generate_cluster_label(self, personas: list[Persona]) -> str:
        """Generate a human-readable label for a cluster."""
        if not personas:
            return "Empty Cluster"

        if len(personas) == 1:
            return personas[0].name or f"Single: {personas[0].id}"

        # Find common characteristics
        common_goals = self._find_common_items([set(p.goals or []) for p in personas])
        common_pains = self._find_common_items(
            [set(p.pain_points or []) for p in personas]
        )

        if common_goals:
            return f"Goal-focused: {list(common_goals)[0][:30]}"
        if common_pains:
            return f"Pain-focused: {list(common_pains)[0][:30]}"

        return f"Cluster of {len(personas)} personas"

    def _extract_characteristics(
        self,
        personas: list[Persona],
    ) -> dict[str, Any]:
        """Extract common characteristics from a cluster."""
        if not personas:
            return {}

        characteristics: dict[str, Any] = {}

        # Common goals
        common_goals = self._find_common_items([set(p.goals or []) for p in personas])
        if common_goals:
            characteristics["common_goals"] = list(common_goals)

        # Common pain points
        common_pains = self._find_common_items(
            [set(p.pain_points or []) for p in personas]
        )
        if common_pains:
            characteristics["common_pain_points"] = list(common_pains)

        # Common demographics
        all_demos = [p.demographics or {} for p in personas]
        common_demos = {}
        if all_demos:
            all_keys = set().union(*[d.keys() for d in all_demos])
            for key in all_keys:
                values = [d.get(key) for d in all_demos if key in d]
                if values and all(v == values[0] for v in values):
                    common_demos[key] = values[0]
        if common_demos:
            characteristics["common_demographics"] = common_demos

        return characteristics

    def _find_common_items(self, sets: list[set]) -> set:
        """Find items common to all sets."""
        if not sets:
            return set()
        result = sets[0].copy()
        for s in sets[1:]:
            result &= s
        return result

    def _estimate_k(self, n: int) -> int:
        """Estimate number of clusters using rule of thumb."""
        return max(2, int(math.sqrt(n / 2)))

    def _generate_suggestions(
        self,
        clusters: list[Cluster],
    ) -> list[ConsolidationSuggestion]:
        """Generate consolidation suggestions from clusters."""
        suggestions = []

        for cluster in clusters:
            if cluster.size >= 2 and cluster.cohesion >= self.similarity_threshold:
                suggestion = ConsolidationSuggestion(
                    personas=cluster.personas,
                    reason=f"High similarity within {cluster.label}",
                    similarity_score=cluster.cohesion,
                    confidence=min(cluster.cohesion * 0.9, 0.95),
                )
                suggestions.append(suggestion)

        return suggestions

    def _determine_similarity_reason(
        self,
        persona_a: Persona,
        persona_b: Persona,
    ) -> str:
        """Determine the main reason two personas are similar."""
        scores = {
            "goals": self._jaccard_similarity(
                set(persona_a.goals or []),
                set(persona_b.goals or []),
            ),
            "pain_points": self._jaccard_similarity(
                set(persona_a.pain_points or []),
                set(persona_b.pain_points or []),
            ),
            "demographics": self._dict_similarity(
                persona_a.demographics or {},
                persona_b.demographics or {},
            ),
            "behaviours": self._jaccard_similarity(
                set(persona_a.behaviours or []),
                set(persona_b.behaviours or []),
            ),
        }

        best_field = max(scores, key=lambda k: scores[k])
        return f"Similar {best_field.replace('_', ' ')}"
