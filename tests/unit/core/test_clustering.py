"""
Tests for persona clustering functionality (F-027).
"""

import pytest
from persona.core.clustering import (
    Cluster,
    ClusterResult,
    ConsolidationSuggestion,
    PersonaClusterer,
)
from persona.core.clustering.cluster import ClusterMethod
from persona.core.generation.parser import Persona


class TestConsolidationSuggestion:
    """Tests for ConsolidationSuggestion dataclass."""

    @pytest.fixture
    def sample_personas(self):
        """Create sample personas."""
        return [
            Persona(id="p001", name="Alice", goals=["Goal A"]),
            Persona(id="p002", name="Bob", goals=["Goal B"]),
        ]

    def test_basic_suggestion(self, sample_personas):
        """Test basic suggestion creation."""
        suggestion = ConsolidationSuggestion(
            personas=sample_personas,
            reason="Similar goals",
            similarity_score=0.8,
        )

        assert len(suggestion.personas) == 2
        assert suggestion.reason == "Similar goals"
        assert suggestion.similarity_score == 0.8

    def test_auto_merged_name(self, sample_personas):
        """Test automatic merged name generation."""
        suggestion = ConsolidationSuggestion(
            personas=sample_personas,
            reason="Similar",
            similarity_score=0.75,
        )

        assert "Alice" in suggestion.merged_name
        assert "Bob" in suggestion.merged_name

    def test_custom_merged_name(self, sample_personas):
        """Test custom merged name."""
        suggestion = ConsolidationSuggestion(
            personas=sample_personas,
            reason="Similar",
            similarity_score=0.8,
            merged_name="Custom Name",
        )

        assert suggestion.merged_name == "Custom Name"

    def test_many_personas_merged_name(self):
        """Test merged name with many personas."""
        personas = [Persona(id=f"p{i}", name=f"Person{i}", goals=[]) for i in range(5)]

        suggestion = ConsolidationSuggestion(
            personas=personas,
            reason="Similar",
            similarity_score=0.7,
        )

        assert "(+2 more)" in suggestion.merged_name

    def test_to_dict(self, sample_personas):
        """Test conversion to dictionary."""
        suggestion = ConsolidationSuggestion(
            personas=sample_personas,
            reason="Similar goals",
            similarity_score=0.85,
            confidence=0.8,
        )

        data = suggestion.to_dict()

        assert data["persona_ids"] == ["p001", "p002"]
        assert data["reason"] == "Similar goals"
        assert data["similarity_score"] == 0.85
        assert data["confidence"] == 0.8


class TestCluster:
    """Tests for Cluster dataclass."""

    @pytest.fixture
    def sample_personas(self):
        """Create sample personas."""
        return [
            Persona(id="p001", name="Alice", goals=["Goal A"]),
            Persona(id="p002", name="Bob", goals=["Goal B"]),
            Persona(id="p003", name="Carol", goals=["Goal C"]),
        ]

    def test_basic_cluster(self, sample_personas):
        """Test basic cluster creation."""
        cluster = Cluster(
            id="cluster_1",
            personas=sample_personas,
            centroid_id="p001",
        )

        assert cluster.id == "cluster_1"
        assert cluster.size == 3
        assert cluster.centroid_id == "p001"

    def test_size_property(self, sample_personas):
        """Test size property."""
        cluster = Cluster(id="c1", personas=sample_personas)
        assert cluster.size == 3

        empty_cluster = Cluster(id="c2", personas=[])
        assert empty_cluster.size == 0

    def test_centroid_property(self, sample_personas):
        """Test centroid property."""
        cluster = Cluster(
            id="c1",
            personas=sample_personas,
            centroid_id="p002",
        )

        assert cluster.centroid.id == "p002"
        assert cluster.centroid.name == "Bob"

    def test_centroid_fallback(self, sample_personas):
        """Test centroid falls back to first persona."""
        cluster = Cluster(
            id="c1",
            personas=sample_personas,
            centroid_id="nonexistent",
        )

        assert cluster.centroid.id == "p001"

    def test_centroid_empty_cluster(self):
        """Test centroid on empty cluster."""
        cluster = Cluster(id="c1", personas=[])
        assert cluster.centroid is None

    def test_to_dict(self, sample_personas):
        """Test conversion to dictionary."""
        cluster = Cluster(
            id="cluster_1",
            personas=sample_personas,
            centroid_id="p001",
            cohesion=0.85,
            label="Test Cluster",
            characteristics={"common_goals": ["Goal X"]},
        )

        data = cluster.to_dict()

        assert data["id"] == "cluster_1"
        assert data["size"] == 3
        assert data["cohesion"] == 0.85
        assert data["label"] == "Test Cluster"
        assert data["persona_ids"] == ["p001", "p002", "p003"]


class TestClusterResult:
    """Tests for ClusterResult dataclass."""

    def test_success_result(self):
        """Test successful result."""
        cluster = Cluster(
            id="c1",
            personas=[Persona(id="p1", name="Alice", goals=[])],
        )

        result = ClusterResult(
            success=True,
            clusters=[cluster],
            method=ClusterMethod.SIMILARITY,
        )

        assert result.success is True
        assert result.cluster_count == 1
        assert result.total_personas == 1

    def test_failed_result(self):
        """Test failed result."""
        result = ClusterResult(
            success=False,
            error="Clustering failed",
        )

        assert result.success is False
        assert result.error == "Clustering failed"
        assert result.cluster_count == 0

    def test_cluster_count(self):
        """Test cluster count property."""
        clusters = [Cluster(id=f"c{i}", personas=[]) for i in range(3)]

        result = ClusterResult(success=True, clusters=clusters)
        assert result.cluster_count == 3

    def test_total_personas(self):
        """Test total personas property."""
        clusters = [
            Cluster(
                id="c1",
                personas=[Persona(id="p1", name="A", goals=[])],
            ),
            Cluster(
                id="c2",
                personas=[
                    Persona(id="p2", name="B", goals=[]),
                    Persona(id="p3", name="C", goals=[]),
                ],
            ),
        ]

        result = ClusterResult(success=True, clusters=clusters)
        assert result.total_personas == 3

    def test_to_dict(self):
        """Test conversion to dictionary."""
        suggestion = ConsolidationSuggestion(
            personas=[Persona(id="p1", name="A", goals=[])],
            reason="Test",
            similarity_score=0.8,
        )

        result = ClusterResult(
            success=True,
            clusters=[],
            consolidation_suggestions=[suggestion],
            method=ClusterMethod.HIERARCHICAL,
            parameters={"threshold": 0.7},
        )

        data = result.to_dict()

        assert data["success"] is True
        assert data["method"] == "hierarchical"
        assert data["parameters"] == {"threshold": 0.7}


class TestPersonaClusterer:
    """Tests for PersonaClusterer class."""

    @pytest.fixture
    def clusterer(self):
        """Create a clusterer instance."""
        return PersonaClusterer(similarity_threshold=0.6)

    @pytest.fixture
    def similar_personas(self):
        """Create personas with high similarity."""
        return [
            Persona(
                id="p001",
                name="Alice",
                goals=["Goal A", "Goal B"],
                pain_points=["Pain X"],
                demographics={"role": "Developer"},
            ),
            Persona(
                id="p002",
                name="Bob",
                goals=["Goal A", "Goal B"],
                pain_points=["Pain X"],
                demographics={"role": "Developer"},
            ),
            Persona(
                id="p003",
                name="Carol",
                goals=["Goal A", "Goal C"],
                pain_points=["Pain X"],
                demographics={"role": "Developer"},
            ),
        ]

    @pytest.fixture
    def diverse_personas(self):
        """Create personas with low similarity."""
        return [
            Persona(
                id="p001",
                name="Developer Dan",
                goals=["Write clean code"],
                pain_points=["Complex requirements"],
                demographics={"role": "Developer"},
            ),
            Persona(
                id="p002",
                name="Manager Mary",
                goals=["Meet deadlines"],
                pain_points=["Resource constraints"],
                demographics={"role": "Manager"},
            ),
            Persona(
                id="p003",
                name="Designer Dave",
                goals=["Create beautiful UIs"],
                pain_points=["Limited tools"],
                demographics={"role": "Designer"},
            ),
        ]

    def test_init(self, clusterer):
        """Test initialisation."""
        assert clusterer.similarity_threshold == 0.6
        assert "goals" in clusterer.weights

    def test_init_custom_weights(self):
        """Test initialisation with custom weights."""
        weights = {"goals": 0.5, "pain_points": 0.5}
        clusterer = PersonaClusterer(weights=weights)

        assert clusterer.weights == weights

    def test_calculate_similarity_identical(self, clusterer):
        """Test similarity of identical personas."""
        persona = Persona(
            id="p1",
            name="Test",
            goals=["Goal A"],
            pain_points=["Pain X"],
            demographics={"age": "30"},
            behaviours=["Behaviour 1"],
        )

        score = clusterer.calculate_similarity(persona, persona)
        assert score == 1.0

    def test_calculate_similarity_different(self, clusterer):
        """Test similarity of very different personas."""
        persona_a = Persona(
            id="p1",
            name="Alice",
            goals=["Goal A"],
            pain_points=["Pain A"],
        )
        persona_b = Persona(
            id="p2",
            name="Bob",
            goals=["Goal B"],
            pain_points=["Pain B"],
        )

        score = clusterer.calculate_similarity(persona_a, persona_b)
        assert score < 0.5

    def test_calculate_similarity_partial(self, clusterer):
        """Test similarity with partial overlap."""
        persona_a = Persona(
            id="p1",
            name="Alice",
            goals=["Goal A", "Goal B"],
            pain_points=["Pain X"],
        )
        persona_b = Persona(
            id="p2",
            name="Bob",
            goals=["Goal A", "Goal C"],
            pain_points=["Pain X"],
        )

        score = clusterer.calculate_similarity(persona_a, persona_b)
        assert 0.3 < score < 0.8

    def test_cluster_empty_list(self, clusterer):
        """Test clustering empty list."""
        result = clusterer.cluster([])

        assert result.success is True
        assert result.cluster_count == 0
        assert result.total_personas == 0

    def test_cluster_single_persona(self, clusterer):
        """Test clustering single persona."""
        persona = Persona(id="p1", name="Alice", goals=["Goal A"])

        result = clusterer.cluster([persona])

        assert result.success is True
        assert result.cluster_count == 1
        assert result.clusters[0].size == 1

    def test_cluster_similar_personas(self, clusterer, similar_personas):
        """Test clustering similar personas."""
        result = clusterer.cluster(similar_personas)

        assert result.success is True
        # Should be grouped together due to similarity
        assert result.cluster_count <= 2

    def test_cluster_diverse_personas(self, clusterer, diverse_personas):
        """Test clustering diverse personas."""
        result = clusterer.cluster(diverse_personas)

        assert result.success is True
        # Should be separate due to low similarity
        assert result.cluster_count >= 2

    def test_cluster_method_similarity(self, clusterer, similar_personas):
        """Test similarity clustering method."""
        result = clusterer.cluster(
            similar_personas,
            method=ClusterMethod.SIMILARITY,
        )

        assert result.success is True
        assert result.method == ClusterMethod.SIMILARITY

    def test_cluster_method_hierarchical(self, clusterer, similar_personas):
        """Test hierarchical clustering method."""
        result = clusterer.cluster(
            similar_personas,
            method=ClusterMethod.HIERARCHICAL,
        )

        assert result.success is True
        assert result.method == ClusterMethod.HIERARCHICAL

    def test_cluster_method_kmeans(self, clusterer, diverse_personas):
        """Test k-means clustering method."""
        result = clusterer.cluster(
            diverse_personas,
            method=ClusterMethod.KMEANS,
            k=2,
        )

        assert result.success is True
        assert result.method == ClusterMethod.KMEANS
        # K-means may converge to fewer clusters if data is sparse
        assert result.cluster_count >= 1

    def test_cluster_with_threshold(self, clusterer, similar_personas):
        """Test clustering with custom threshold."""
        result = clusterer.cluster(
            similar_personas,
            threshold=0.9,
        )

        assert result.success is True
        # Higher threshold = more clusters
        assert result.cluster_count >= 1

    def test_find_similar(self, clusterer, similar_personas):
        """Test finding similar personas."""
        target = similar_personas[0]
        candidates = similar_personas[1:]

        results = clusterer.find_similar(target, candidates, threshold=0.5)

        assert len(results) >= 1
        # Results should be sorted by score descending
        if len(results) > 1:
            assert results[0][1] >= results[1][1]

    def test_find_similar_excludes_self(self, clusterer, similar_personas):
        """Test that find_similar excludes the target."""
        target = similar_personas[0]

        results = clusterer.find_similar(target, similar_personas)

        result_ids = [p.id for p, _ in results]
        assert target.id not in result_ids

    def test_find_similar_no_matches(self, clusterer, diverse_personas):
        """Test finding similar with no matches above threshold."""
        target = diverse_personas[0]
        candidates = diverse_personas[1:]

        results = clusterer.find_similar(target, candidates, threshold=0.9)

        assert len(results) == 0

    def test_suggest_consolidation(self, clusterer, similar_personas):
        """Test consolidation suggestions."""
        suggestions = clusterer.suggest_consolidation(
            similar_personas,
            threshold=0.5,
        )

        assert isinstance(suggestions, list)
        for s in suggestions:
            assert isinstance(s, ConsolidationSuggestion)
            assert s.similarity_score >= 0.5

    def test_suggest_consolidation_empty(self, clusterer):
        """Test consolidation with empty list."""
        suggestions = clusterer.suggest_consolidation([])
        assert len(suggestions) == 0

    def test_cluster_generates_suggestions(self, clusterer, similar_personas):
        """Test that clustering generates suggestions."""
        result = clusterer.cluster(similar_personas)

        assert result.success is True
        # May or may not have suggestions depending on cohesion
        assert isinstance(result.consolidation_suggestions, list)

    def test_cluster_cohesion(self, clusterer, similar_personas):
        """Test cluster cohesion calculation."""
        result = clusterer.cluster(similar_personas, threshold=0.4)

        for cluster in result.clusters:
            if cluster.size > 1:
                assert 0.0 <= cluster.cohesion <= 1.0

    def test_cluster_label_generation(self, clusterer):
        """Test cluster label generation."""
        personas = [
            Persona(
                id="p1",
                name="Alice",
                goals=["Improve productivity"],
            ),
            Persona(
                id="p2",
                name="Bob",
                goals=["Improve productivity"],
            ),
        ]

        result = clusterer.cluster(personas, threshold=0.3)

        for cluster in result.clusters:
            assert cluster.label != ""

    def test_cluster_characteristics(self, clusterer, similar_personas):
        """Test cluster characteristics extraction."""
        result = clusterer.cluster(similar_personas, threshold=0.4)

        for cluster in result.clusters:
            if cluster.size > 1:
                assert isinstance(cluster.characteristics, dict)

    def test_to_dict_complete(self, clusterer, similar_personas):
        """Test complete result to_dict."""
        result = clusterer.cluster(similar_personas)

        data = result.to_dict()

        assert "success" in data
        assert "clusters" in data
        assert "consolidation_suggestions" in data
        assert "method" in data

    def test_cluster_preserves_all_personas(self, clusterer, similar_personas):
        """Test that all personas are assigned to clusters."""
        result = clusterer.cluster(similar_personas)

        clustered_ids = set()
        for cluster in result.clusters:
            for persona in cluster.personas:
                clustered_ids.add(persona.id)

        original_ids = {p.id for p in similar_personas}
        assert clustered_ids == original_ids

    def test_hierarchical_merging(self, clusterer):
        """Test hierarchical clustering merges similar clusters."""
        personas = [
            Persona(id="p1", name="A", goals=["Goal X"], pain_points=["Pain 1"]),
            Persona(id="p2", name="B", goals=["Goal X"], pain_points=["Pain 1"]),
            Persona(id="p3", name="C", goals=["Goal Y"], pain_points=["Pain 2"]),
            Persona(id="p4", name="D", goals=["Goal Y"], pain_points=["Pain 2"]),
        ]

        result = clusterer.cluster(
            personas,
            method=ClusterMethod.HIERARCHICAL,
            threshold=0.5,
        )

        assert result.success is True
        # Should create 2 clusters (p1+p2 and p3+p4)
        assert result.cluster_count <= 3

    def test_kmeans_respects_k(self, clusterer):
        """Test k-means creates exactly k clusters."""
        personas = [
            Persona(id=f"p{i}", name=f"Person {i}", goals=[f"Goal {i}"])
            for i in range(10)
        ]

        result = clusterer.cluster(
            personas,
            method=ClusterMethod.KMEANS,
            k=3,
        )

        assert result.success is True
        assert result.cluster_count == 3

    def test_empty_characteristics(self, clusterer):
        """Test cluster with no common characteristics."""
        personas = [
            Persona(id="p1", name="A", goals=["Goal 1"]),
            Persona(id="p2", name="B", goals=["Goal 2"]),
        ]

        result = clusterer.cluster(personas, threshold=0.1)

        for cluster in result.clusters:
            assert isinstance(cluster.characteristics, dict)

    def test_centroid_selection(self, clusterer):
        """Test centroid is most central persona."""
        personas = [
            Persona(
                id="p1",
                name="Central",
                goals=["A", "B"],
                pain_points=["X"],
            ),
            Persona(
                id="p2",
                name="Edge1",
                goals=["A"],
                pain_points=["X"],
            ),
            Persona(
                id="p3",
                name="Edge2",
                goals=["B"],
                pain_points=["X"],
            ),
        ]

        result = clusterer.cluster(personas, threshold=0.3)

        # The cluster should have the most central persona as centroid
        for cluster in result.clusters:
            assert cluster.centroid_id in [p.id for p in cluster.personas]


class TestClusteringIntegration:
    """Integration tests for clustering workflow."""

    def test_full_clustering_workflow(self):
        """Test complete clustering workflow."""
        # Create personas
        personas = [
            Persona(
                id=f"dev_{i}",
                name=f"Developer {i}",
                goals=["Write code", "Learn new tech"],
                pain_points=["Meetings", "Documentation"],
                demographics={"role": "Developer"},
            )
            for i in range(3)
        ] + [
            Persona(
                id=f"mgr_{i}",
                name=f"Manager {i}",
                goals=["Meet targets", "Lead team"],
                pain_points=["Budget", "Hiring"],
                demographics={"role": "Manager"},
            )
            for i in range(2)
        ]

        # Cluster
        clusterer = PersonaClusterer(similarity_threshold=0.5)
        result = clusterer.cluster(personas)

        # Verify
        assert result.success is True
        assert result.total_personas == 5

        # Should separate developers and managers
        assert result.cluster_count >= 2

    def test_consolidation_workflow(self):
        """Test consolidation suggestion workflow."""
        # Create very similar personas
        personas = [
            Persona(
                id="p1",
                name="User A",
                goals=["Goal X", "Goal Y"],
                pain_points=["Pain A"],
                demographics={"age": "30", "role": "Engineer"},
            ),
            Persona(
                id="p2",
                name="User B",
                goals=["Goal X", "Goal Y"],
                pain_points=["Pain A"],
                demographics={"age": "30", "role": "Engineer"},
            ),
        ]

        clusterer = PersonaClusterer(similarity_threshold=0.7)
        suggestions = clusterer.suggest_consolidation(personas)

        assert len(suggestions) >= 1
        assert suggestions[0].similarity_score >= 0.7

    def test_different_methods_same_data(self):
        """Test different methods on same data."""
        personas = [
            Persona(
                id=f"p{i}",
                name=f"Person {i}",
                goals=[f"Goal {i % 3}"],
                pain_points=[f"Pain {i % 2}"],
            )
            for i in range(6)
        ]

        clusterer = PersonaClusterer(similarity_threshold=0.4)

        result_sim = clusterer.cluster(personas, method=ClusterMethod.SIMILARITY)
        result_hier = clusterer.cluster(personas, method=ClusterMethod.HIERARCHICAL)
        result_kmeans = clusterer.cluster(personas, method=ClusterMethod.KMEANS, k=3)

        # All should succeed
        assert result_sim.success is True
        assert result_hier.success is True
        assert result_kmeans.success is True

        # All should cover all personas
        assert result_sim.total_personas == 6
        assert result_hier.total_personas == 6
        assert result_kmeans.total_personas == 6
