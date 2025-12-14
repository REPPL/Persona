"""
Tests for persona comparison functionality (F-021).
"""

import pytest

from persona.core.generation.parser import Persona
from persona.core.comparison import PersonaComparator, ComparisonResult, SimilarityScore


class TestSimilarityScore:
    """Tests for SimilarityScore dataclass."""

    def test_default_values(self):
        """Test default similarity scores."""
        score = SimilarityScore()

        assert score.overall == 0.0
        assert score.goals == 0.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        score = SimilarityScore(
            overall=75.5,
            goals=80.0,
            pain_points=70.0,
        )

        data = score.to_dict()

        assert data["overall"] == 75.5
        assert data["goals"] == 80.0


class TestComparisonResult:
    """Tests for ComparisonResult dataclass."""

    def test_is_similar_true(self):
        """Test is_similar when similarity is high."""
        result = ComparisonResult(
            persona_a_id="p001",
            persona_b_id="p002",
            similarity=SimilarityScore(overall=75.0),
        )

        assert result.is_similar is True

    def test_is_similar_false(self):
        """Test is_similar when similarity is low."""
        result = ComparisonResult(
            persona_a_id="p001",
            persona_b_id="p002",
            similarity=SimilarityScore(overall=50.0),
        )

        assert result.is_similar is False

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ComparisonResult(
            persona_a_id="p001",
            persona_b_id="p002",
            shared_goals=["Goal 1"],
        )

        data = result.to_dict()

        assert data["persona_a"] == "p001"
        assert data["shared_goals"] == ["Goal 1"]


class TestPersonaComparator:
    """Tests for PersonaComparator class."""

    def test_compare_identical_personas(self):
        """Test comparing identical personas."""
        persona = Persona(
            id="p001",
            name="Alice",
            goals=["Learn Python", "Build apps"],
            pain_points=["No time"],
            demographics={"age": "30"},
        )

        comparator = PersonaComparator()
        result = comparator.compare(persona, persona)

        assert result.similarity.overall >= 80.0
        assert len(result.shared_goals) == 2
        assert len(result.unique_goals_a) == 0

    def test_compare_different_personas(self):
        """Test comparing different personas."""
        persona_a = Persona(
            id="p001",
            name="Alice",
            goals=["Learn Python"],
            pain_points=["No time"],
        )
        persona_b = Persona(
            id="p002",
            name="Bob",
            goals=["Learn Java"],
            pain_points=["Too expensive"],
        )

        comparator = PersonaComparator()
        result = comparator.compare(persona_a, persona_b)

        assert result.similarity.overall < 50.0
        assert len(result.shared_goals) == 0
        assert len(result.unique_goals_a) == 1
        assert len(result.unique_goals_b) == 1

    def test_compare_partial_overlap(self):
        """Test comparing personas with partial overlap."""
        persona_a = Persona(
            id="p001",
            name="Alice",
            goals=["Learn Python", "Build apps", "Get job"],
            pain_points=["No time", "Too complex"],
        )
        persona_b = Persona(
            id="p002",
            name="Bob",
            goals=["Learn Python", "Write docs"],
            pain_points=["No time", "Boring"],
        )

        comparator = PersonaComparator()
        result = comparator.compare(persona_a, persona_b)

        assert "learn python" in [g.lower() for g in result.shared_goals]
        assert result.similarity.goals > 0

    def test_compare_demographics(self):
        """Test demographic comparison."""
        persona_a = Persona(
            id="p001",
            name="Alice",
            demographics={"age": "30", "role": "Developer"},
        )
        persona_b = Persona(
            id="p002",
            name="Bob",
            demographics={"age": "30", "role": "Designer"},
        )

        comparator = PersonaComparator()
        result = comparator.compare(persona_a, persona_b)

        # One field matches (age), one differs (role)
        assert result.similarity.demographics == 50.0
        assert len(result.demographic_differences) == 1

    def test_case_insensitive(self):
        """Test case insensitive comparison."""
        persona_a = Persona(
            id="p001",
            name="Alice",
            goals=["Learn Python"],
        )
        persona_b = Persona(
            id="p002",
            name="Bob",
            goals=["LEARN PYTHON"],
        )

        comparator = PersonaComparator(case_sensitive=False)
        result = comparator.compare(persona_a, persona_b)

        assert len(result.shared_goals) == 1

    def test_case_sensitive(self):
        """Test case sensitive comparison."""
        persona_a = Persona(
            id="p001",
            name="Alice",
            goals=["Learn Python"],
        )
        persona_b = Persona(
            id="p002",
            name="Bob",
            goals=["LEARN PYTHON"],
        )

        comparator = PersonaComparator(case_sensitive=True)
        result = comparator.compare(persona_a, persona_b)

        assert len(result.shared_goals) == 0

    def test_compare_all(self):
        """Test comparing all personas pairwise."""
        personas = [
            Persona(id="p001", name="Alice", goals=["A"]),
            Persona(id="p002", name="Bob", goals=["B"]),
            Persona(id="p003", name="Carol", goals=["C"]),
        ]

        comparator = PersonaComparator()
        results = comparator.compare_all(personas)

        # 3 personas = 3 pairs (p1-p2, p1-p3, p2-p3)
        assert len(results) == 3

    def test_find_most_similar(self):
        """Test finding most similar persona."""
        target = Persona(
            id="p001",
            name="Target",
            goals=["Learn Python", "Build apps"],
        )
        candidates = [
            Persona(id="p002", name="Alice", goals=["Learn Java"]),
            Persona(id="p003", name="Bob", goals=["Learn Python", "Build apps"]),
            Persona(id="p004", name="Carol", goals=["Cook food"]),
        ]

        comparator = PersonaComparator()
        match, result = comparator.find_most_similar(target, candidates)

        assert match is not None
        assert match.id == "p003"

    def test_find_most_similar_empty(self):
        """Test finding most similar with empty candidates."""
        target = Persona(id="p001", name="Target")

        comparator = PersonaComparator()
        match, result = comparator.find_most_similar(target, [])

        assert match is None
        assert result is None

    def test_find_duplicates(self):
        """Test finding duplicate personas."""
        personas = [
            Persona(
                id="p001",
                name="Alice",
                goals=["Goal A", "Goal B"],
                pain_points=["Pain 1"],
                demographics={"age": "30"},
            ),
            Persona(
                id="p002",
                name="Alice Clone",
                goals=["Goal A", "Goal B"],
                pain_points=["Pain 1"],
                demographics={"age": "30"},
            ),
            Persona(id="p003", name="Bob", goals=["Different"]),
        ]

        comparator = PersonaComparator()
        duplicates = comparator.find_duplicates(personas, threshold=70.0)

        assert len(duplicates) >= 1
        ids = {d[0].id for d in duplicates} | {d[1].id for d in duplicates}
        assert "p001" in ids or "p002" in ids

    def test_group_by_similarity(self):
        """Test grouping personas by similarity."""
        personas = [
            Persona(id="p001", name="Alice", goals=["Python"]),
            Persona(id="p002", name="Bob", goals=["Python"]),
            Persona(id="p003", name="Carol", goals=["Cooking"]),
            Persona(id="p004", name="Dave", goals=["Cooking"]),
        ]

        comparator = PersonaComparator()
        groups = comparator.group_by_similarity(personas, threshold=50.0)

        assert len(groups) >= 1
        # Should have at least 2 groups (tech vs cooking)

    def test_empty_personas(self):
        """Test comparing personas with no data."""
        persona_a = Persona(id="p001", name="Alice")
        persona_b = Persona(id="p002", name="Bob")

        comparator = PersonaComparator()
        result = comparator.compare(persona_a, persona_b)

        assert result.similarity.overall == 0.0
        assert len(result.shared_goals) == 0

    def test_behaviours_comparison(self):
        """Test behaviour similarity."""
        persona_a = Persona(
            id="p001",
            name="Alice",
            behaviours=["Uses keyboard shortcuts", "Reads documentation"],
        )
        persona_b = Persona(
            id="p002",
            name="Bob",
            behaviours=["Uses keyboard shortcuts", "Watches tutorials"],
        )

        comparator = PersonaComparator()
        result = comparator.compare(persona_a, persona_b)

        assert result.similarity.behaviours > 0
