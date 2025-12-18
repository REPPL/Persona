"""Tests for consistency checking."""

import pytest
from persona.core.generation.parser import Persona
from persona.core.quality.verification.consistency import ConsistencyChecker


class MockEmbeddingProvider:
    """Mock embedding provider for testing."""

    def __init__(self, configured: bool = True):
        self._configured = configured

    def is_configured(self) -> bool:
        return self._configured

    def embed(self, text: str):
        """Return mock embedding."""
        from persona.core.embedding.base import EmbeddingResponse

        # Simple deterministic embedding based on text length
        vector = [float(i) for i in range(384)]
        for i, char in enumerate(text[:384]):
            vector[i] += ord(char) / 1000.0

        return EmbeddingResponse(
            vector=vector,
            model="mock-model",
            input_tokens=len(text.split()),
            dimensions=384,
        )


class TestConsistencyChecker:
    """Tests for ConsistencyChecker."""

    def test_single_persona_perfect_consistency(self):
        """Test that single persona has perfect consistency."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        personas = [
            Persona(
                id="p1",
                name="Alice",
                goals=["Goal 1"],
            )
        ]

        metrics = checker.calculate_metrics(personas)

        assert metrics.attribute_agreement == 1.0
        assert metrics.semantic_consistency == 1.0
        assert metrics.factual_convergence == 1.0

    def test_identical_personas_perfect_consistency(self):
        """Test that identical personas have perfect consistency."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        personas = [
            Persona(
                id="p1",
                name="Alice",
                demographics={"age": 30},
                goals=["Goal 1"],
            ),
            Persona(
                id="p2",
                name="Alice",
                demographics={"age": 30},
                goals=["Goal 1"],
            ),
        ]

        metrics = checker.calculate_metrics(personas)

        assert metrics.attribute_agreement == 1.0
        # Semantic consistency might not be perfect due to mock embeddings
        assert metrics.semantic_consistency > 0.9

    def test_attribute_agreement_calculation(self):
        """Test attribute agreement calculation."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        personas = [
            Persona(
                id="p1",
                name="Alice",
                demographics={"age": 30},
                goals=["Goal 1"],
                pain_points=["Pain 1"],
            ),
            Persona(
                id="p2",
                name="Bob",
                demographics={"age": 35},
                goals=["Goal 2"],
                # No pain_points
            ),
            Persona(
                id="p3",
                name="Charlie",
                demographics={"age": 40},
                goals=["Goal 3"],
                pain_points=["Pain 2"],
            ),
        ]

        metrics = checker.calculate_metrics(personas)

        # All have name, demographics, goals (100%)
        # 2/3 have pain_points (66%)
        # Average: (1.0 + 1.0 + 1.0 + 0.66) / 4 ≈ 0.915
        assert 0.8 < metrics.attribute_agreement < 1.0

    def test_semantic_consistency_with_embeddings(self):
        """Test semantic consistency calculation with embeddings."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=True)
        )

        # Similar personas should have high semantic consistency
        personas = [
            Persona(
                id="p1",
                name="Software Engineer",
                goals=["Build applications"],
            ),
            Persona(
                id="p2",
                name="Developer",
                goals=["Create software"],
            ),
        ]

        metrics = checker.calculate_metrics(personas)

        # Should have reasonable semantic consistency
        assert metrics.semantic_consistency > 0.5

    def test_semantic_consistency_fallback(self):
        """Test semantic consistency falls back when embeddings unavailable."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        personas = [
            Persona(id="p1", name="Alice", goals=["Goal 1"]),
            Persona(id="p2", name="Bob", goals=["Goal 2"]),
        ]

        metrics = checker.calculate_metrics(personas)

        # Should still calculate a value using simple text similarity
        assert 0.0 <= metrics.semantic_consistency <= 1.0

    def test_factual_convergence(self):
        """Test factual convergence calculation."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        personas = [
            Persona(
                id="p1",
                name="Alice",
                goals=["Goal 1", "Goal 2"],
                pain_points=["Pain 1"],
            ),
            Persona(
                id="p2",
                name="Bob",
                goals=["Goal 1", "Goal 3"],
                pain_points=["Pain 1"],
            ),
            Persona(
                id="p3",
                name="Charlie",
                goals=["Goal 1"],
                pain_points=["Pain 1", "Pain 2"],
            ),
        ]

        metrics = checker.calculate_metrics(personas)

        # Goal 1 and Pain 1 appear in all (majority)
        # Other goals/pains appear in minority
        assert metrics.factual_convergence > 0.3

    def test_get_attribute_details(self):
        """Test getting detailed attribute agreement."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        personas = [
            Persona(id="p1", name="Alice", goals=["Goal 1"]),
            Persona(id="p2", name="Bob", goals=["Goal 2"]),
            Persona(id="p3", name="Charlie"),  # No goals
        ]

        details = checker.get_attribute_details(personas)

        # All have name
        assert details["name"].present_count == 3
        assert details["name"].agreement_score == 1.0

        # Only 2 have goals
        assert details["goals"].present_count == 2
        assert details["goals"].agreement_score == pytest.approx(2 / 3)

    def test_persona_to_text(self):
        """Test persona text conversion."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        persona = Persona(
            id="p1",
            name="Alice",
            demographics={"age": 30, "occupation": "Engineer"},
            goals=["Goal 1", "Goal 2"],
            pain_points=["Pain 1"],
            behaviours=["Behaviour 1"],
            quotes=["Quote 1"],
        )

        text = checker._persona_to_text(persona)

        # Should include all fields
        assert "Alice" in text
        assert "age: 30" in text
        assert "Engineer" in text
        assert "Goal 1" in text
        assert "Pain 1" in text
        assert "Behaviour 1" in text
        assert "Quote 1" in text

    def test_simple_text_similarity(self):
        """Test simple text similarity calculation."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        # Identical texts
        similarity = checker._simple_text_similarity(["hello world", "hello world"])
        assert similarity == 1.0

        # Completely different texts
        similarity = checker._simple_text_similarity(["hello", "goodbye"])
        assert similarity == 0.0

        # Partially overlapping texts
        similarity = checker._simple_text_similarity(["hello world", "hello there"])
        assert 0.0 < similarity < 1.0

    def test_extract_claims(self):
        """Test claim extraction from persona."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        persona = Persona(
            id="p1",
            name="Alice",
            demographics={"age": 30, "occupation": "Engineer"},
            goals=["Build apps"],
            pain_points=["Too complex"],
            behaviours=["Codes daily"],
        )

        claims = checker._extract_claims(persona)

        # Should include goals, pain points, behaviours, demographics
        assert any("build apps" in claim for claim in claims)
        assert any("too complex" in claim for claim in claims)
        assert any("codes daily" in claim for claim in claims)
        assert any("age: 30" in claim for claim in claims)

    def test_custom_weights(self):
        """Test metrics calculation with custom weights."""
        checker = ConsistencyChecker(
            embedding_provider=MockEmbeddingProvider(configured=False)
        )

        personas = [
            Persona(id="p1", name="Alice", goals=["Goal 1"]),
            Persona(id="p2", name="Bob", goals=["Goal 2"]),
        ]

        custom_weights = {
            "attribute_agreement": 0.5,
            "semantic_consistency": 0.3,
            "factual_convergence": 0.2,
        }

        metrics = checker.calculate_metrics(personas, weights=custom_weights)

        assert metrics.weights == custom_weights
        # Confidence score should use custom weights
        expected = (
            metrics.attribute_agreement * 0.5
            + metrics.semantic_consistency * 0.3
            + metrics.factual_convergence * 0.2
        )
        assert abs(metrics.confidence_score - expected) < 0.001
