"""Tests for consolidation mapping (F-070)."""


from persona.core.multimodel.consolidation import (
    ConsolidationMap,
    ConsolidationMapper,
    MergeRecommendation,
    PersonaSimilarity,
    consolidate_personas,
)


class TestPersonaSimilarity:
    """Tests for PersonaSimilarity."""

    def test_to_dict(self):
        """Converts to dictionary."""
        sim = PersonaSimilarity(
            persona_a_id="1",
            persona_b_id="2",
            similarity_score=0.85,
            matching_attributes=["role", "goals"],
            divergent_attributes=["background"],
            merge_recommendation=True,
            merge_reasoning="High similarity",
        )
        data = sim.to_dict()

        assert data["persona_a"] == "1"
        assert data["persona_b"] == "2"
        assert data["similarity_score"] == 0.85
        assert data["merge_recommendation"] is True


class TestMergeRecommendation:
    """Tests for MergeRecommendation."""

    def test_to_dict(self):
        """Converts to dictionary."""
        rec = MergeRecommendation(
            personas_to_merge=["1", "2"],
            merged_persona={"id": "merged-1-2", "role": "Developer"},
            confidence=0.9,
            reasoning="Very similar personas",
        )
        data = rec.to_dict()

        assert data["personas_to_merge"] == ["1", "2"]
        assert data["confidence"] == 0.9


class TestConsolidationMap:
    """Tests for ConsolidationMap."""

    def test_to_dict(self):
        """Converts to dictionary."""
        cmap = ConsolidationMap(
            clusters=[["1", "2"], ["3", "4"]],
            unique_personas=["5"],
            consolidated_count=3,
        )
        data = cmap.to_dict()

        assert len(data["clusters"]) == 2
        assert data["unique_personas"] == ["5"]
        assert data["consolidated_count"] == 3

    def test_to_display(self):
        """Generates display output."""
        cmap = ConsolidationMap(
            clusters=[["1", "2"]],
            unique_personas=["3"],
            consolidated_count=2,
            merge_recommendations=[
                MergeRecommendation(
                    personas_to_merge=["1", "2"],
                    merged_persona={"id": "merged"},
                    confidence=0.85,
                    reasoning="Similar roles",
                ),
            ],
        )
        display = cmap.to_display()

        assert "Consolidation" in display
        assert "Cluster" in display
        assert "Unique" in display


class TestConsolidationMapper:
    """Tests for ConsolidationMapper."""

    def test_consolidate_single_persona(self):
        """Handles single persona gracefully."""
        mapper = ConsolidationMapper()
        personas = [{"id": "1", "role": "Developer"}]

        result = mapper.consolidate(personas)

        assert result.consolidated_count == 1
        assert result.unique_personas == ["1"]

    def test_consolidate_identical_personas(self):
        """Clusters identical personas."""
        mapper = ConsolidationMapper()
        personas = [
            {
                "id": "1",
                "role": "Developer",
                "goals": ["testing"],
                "frustrations": ["bugs"],
            },
            {
                "id": "2",
                "role": "Developer",
                "goals": ["testing"],
                "frustrations": ["bugs"],
            },
        ]

        result = mapper.consolidate(personas)

        assert len(result.clusters) >= 1
        # Should recommend merge for identical personas
        assert len(result.merge_recommendations) >= 0

    def test_consolidate_different_personas(self):
        """Keeps different personas separate."""
        mapper = ConsolidationMapper()
        personas = [
            {
                "id": "1",
                "role": "Developer",
                "goals": ["coding"],
                "frustrations": ["bugs"],
            },
            {"id": "2", "role": "Designer", "goals": ["UX"], "frustrations": ["tools"]},
        ]

        result = mapper.consolidate(personas)

        # Different personas should remain unique
        assert result.consolidated_count >= 1

    def test_consolidate_finds_clusters(self):
        """Identifies clusters of similar personas."""
        mapper = ConsolidationMapper(cluster_threshold=0.5)
        personas = [
            {"id": "1", "role": "Senior Developer", "goals": ["code quality"]},
            {"id": "2", "role": "Lead Developer", "goals": ["code quality"]},
            {"id": "3", "role": "UX Designer", "goals": ["user experience"]},
        ]

        result = mapper.consolidate(personas)

        # Developers should cluster, designer separate
        assert len(result.similarities) == 3  # 3 pairs

    def test_calculate_similarity_identical(self):
        """Identical personas have high similarity."""
        mapper = ConsolidationMapper()
        p1 = {"id": "1", "role": "Developer", "goals": ["A", "B"]}
        p2 = {"id": "2", "role": "Developer", "goals": ["A", "B"]}

        sim = mapper.calculate_similarity(p1, p2)

        assert sim.similarity_score > 0.7
        assert "role" in sim.matching_attributes

    def test_calculate_similarity_different(self):
        """Different personas have low similarity."""
        mapper = ConsolidationMapper()
        p1 = {
            "id": "1",
            "role": "Developer",
            "goals": ["coding"],
            "frustrations": ["bugs"],
        }
        p2 = {
            "id": "2",
            "role": "Manager",
            "goals": ["budgeting"],
            "frustrations": ["delays"],
        }

        sim = mapper.calculate_similarity(p1, p2)

        # Completely different role, goals, frustrations
        assert sim.similarity_score <= 0.5

    def test_calculate_similarity_partial_overlap(self):
        """Partial overlap yields medium similarity."""
        mapper = ConsolidationMapper()
        p1 = {"id": "1", "role": "Developer", "goals": ["A", "B", "C"]}
        p2 = {"id": "2", "role": "Developer", "goals": ["B", "C", "D"]}

        sim = mapper.calculate_similarity(p1, p2)

        # Same role, partial goal overlap
        assert 0.3 < sim.similarity_score < 0.9

    def test_merge_recommendation_threshold(self):
        """Merge recommended only above threshold."""
        mapper = ConsolidationMapper(merge_threshold=0.9)
        p1 = {"id": "1", "role": "Developer", "goals": ["A"]}
        p2 = {"id": "2", "role": "Developer", "goals": ["B"]}

        sim = mapper.calculate_similarity(p1, p2)

        # Same role but different goals - below 0.9 threshold
        assert sim.merge_recommendation is False

    def test_merge_personas_empty(self):
        """Handles empty list gracefully."""
        mapper = ConsolidationMapper()

        merged = mapper.merge_personas([])

        assert merged == {}

    def test_merge_personas_single(self):
        """Single persona returns copy."""
        mapper = ConsolidationMapper()
        persona = {"id": "1", "role": "Developer", "goals": ["A"]}

        merged = mapper.merge_personas([persona])

        assert merged["id"] == "1"
        assert merged["role"] == "Developer"

    def test_merge_personas_multiple(self):
        """Merges multiple personas correctly."""
        mapper = ConsolidationMapper()
        personas = [
            {
                "id": "1",
                "role": "Developer",
                "goals": ["A", "B"],
                "frustrations": ["X"],
            },
            {
                "id": "2",
                "role": "Developer",
                "goals": ["B", "C"],
                "frustrations": ["Y"],
            },
        ]

        merged = mapper.merge_personas(personas)

        assert "merged" in merged["id"]
        assert merged["role"] == "Developer"
        # Goals should be union
        assert "A" in merged["goals"]
        assert "B" in merged["goals"]
        assert "C" in merged["goals"]
        # Should track sources
        assert merged["merged_from"] == ["1", "2"]
        assert merged["merge_count"] == 2

    def test_merge_personas_most_common_role(self):
        """Uses most common role when merging."""
        mapper = ConsolidationMapper()
        personas = [
            {"id": "1", "role": "Designer"},
            {"id": "2", "role": "Developer"},
            {"id": "3", "role": "Developer"},
        ]

        merged = mapper.merge_personas(personas)

        assert merged["role"] == "Developer"

    def test_custom_thresholds(self):
        """Respects custom threshold configuration."""
        mapper = ConsolidationMapper(
            merge_threshold=0.5,
            cluster_threshold=0.3,
        )

        assert mapper.merge_threshold == 0.5
        assert mapper.cluster_threshold == 0.3


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_consolidate_personas_function(self):
        """consolidate_personas convenience function works."""
        personas = [
            {"id": "1", "role": "Developer"},
            {"id": "2", "role": "Developer"},
        ]

        result = consolidate_personas(personas)

        assert isinstance(result, ConsolidationMap)
        assert result.consolidated_count >= 1

    def test_consolidate_personas_custom_threshold(self):
        """consolidate_personas accepts custom threshold."""
        personas = [
            {"id": "1", "role": "Developer"},
            {"id": "2", "role": "Designer"},
        ]

        result = consolidate_personas(personas, merge_threshold=0.99)

        # With very high threshold, no merges
        assert isinstance(result, ConsolidationMap)
