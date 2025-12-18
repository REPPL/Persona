"""Tests for confidence scoring (F-069)."""


from persona.core.multimodel.confidence import (
    AttributeConfidence,
    ConfidenceLevel,
    ConfidenceScorer,
    PersonaConfidence,
    add_confidence_to_persona,
    score_confidence,
)


class TestConfidenceLevel:
    """Tests for ConfidenceLevel enum."""

    def test_high_value(self):
        """High level has correct value."""
        assert ConfidenceLevel.HIGH.value == "high"

    def test_medium_value(self):
        """Medium level has correct value."""
        assert ConfidenceLevel.MEDIUM.value == "medium"

    def test_low_value(self):
        """Low level has correct value."""
        assert ConfidenceLevel.LOW.value == "low"

    def test_high_description(self):
        """High level has description."""
        assert "multiple" in ConfidenceLevel.HIGH.description.lower()

    def test_low_description(self):
        """Low level has description."""
        assert "inferred" in ConfidenceLevel.LOW.description.lower()


class TestAttributeConfidence:
    """Tests for AttributeConfidence."""

    def test_to_dict(self):
        """Converts to dictionary."""
        attr = AttributeConfidence(
            attribute="role",
            value="Developer",
            confidence=ConfidenceLevel.HIGH,
            evidence_count=5,
            evidence_sources=["interview.md", "survey.csv"],
            reasoning="Explicitly mentioned",
        )
        data = attr.to_dict()

        assert data["attribute"] == "role"
        assert data["value"] == "Developer"
        assert data["confidence"] == "high"
        assert data["evidence_count"] == 5


class TestPersonaConfidence:
    """Tests for PersonaConfidence."""

    def test_to_dict(self):
        """Converts to dictionary."""
        pc = PersonaConfidence(
            persona_id="1",
            overall_confidence=ConfidenceLevel.MEDIUM,
            high_confidence_count=2,
            medium_confidence_count=3,
            low_confidence_count=1,
            confidence_score=0.65,
        )
        data = pc.to_dict()

        assert data["persona_id"] == "1"
        assert data["overall_confidence"] == "medium"
        assert data["confidence_score"] == 0.65

    def test_to_display(self):
        """Generates display output."""
        pc = PersonaConfidence(
            persona_id="test-1",
            overall_confidence=ConfidenceLevel.HIGH,
            attribute_confidences=[
                AttributeConfidence(
                    attribute="role",
                    value="Developer",
                    confidence=ConfidenceLevel.HIGH,
                    evidence_count=4,
                    reasoning="Well documented",
                ),
            ],
            confidence_score=0.85,
        )
        display = pc.to_display()

        assert "test-1" in display
        assert "HIGH" in display
        assert "role" in display


class TestConfidenceScorer:
    """Tests for ConfidenceScorer."""

    def test_score_persona_basic(self):
        """Scores a basic persona."""
        scorer = ConfidenceScorer()
        persona = {
            "id": "1",
            "role": "Developer",
            "goals": ["Improve workflow"],
        }

        result = scorer.score_persona(persona)

        assert result.persona_id == "1"
        assert len(result.attribute_confidences) == 2

    def test_score_persona_with_source_data(self):
        """Scores with source data for evidence."""
        scorer = ConfidenceScorer()
        persona = {
            "id": "1",
            "role": "Developer",
            "goals": ["code quality", "faster builds"],
        }
        source_data = {
            "interview.md": "The developer wants code quality. Code quality is key.",
            "survey.csv": "Quality, faster builds, code quality",
            "notes.md": "Focus on code quality improvements",
        }

        result = scorer.score_persona(persona, source_data)

        # "code quality" appears multiple times across sources
        goals_conf = next(
            a for a in result.attribute_confidences if a.attribute == "goals"
        )
        assert goals_conf.evidence_count > 0

    def test_score_persona_high_evidence(self):
        """High evidence count results in high confidence."""
        scorer = ConfidenceScorer(high_threshold=3)
        persona = {"id": "1", "role": "Senior Developer"}
        source_data = {
            "s1.md": "senior developer role",
            "s2.md": "Senior Developer position",
            "s3.md": "senior developer experience",
        }

        result = scorer.score_persona(persona, source_data)

        role_conf = next(
            a for a in result.attribute_confidences if a.attribute == "role"
        )
        assert role_conf.confidence == ConfidenceLevel.HIGH

    def test_score_persona_low_evidence(self):
        """No evidence results in low confidence."""
        scorer = ConfidenceScorer()
        persona = {"id": "1", "role": "Exotic Role"}
        source_data = {
            "interview.md": "Unrelated content about cooking",
        }

        result = scorer.score_persona(persona, source_data)

        role_conf = next(
            a for a in result.attribute_confidences if a.attribute == "role"
        )
        assert role_conf.confidence == ConfidenceLevel.LOW

    def test_score_persona_no_source_assumes_medium(self):
        """Without source data, assumes medium confidence."""
        scorer = ConfidenceScorer()
        persona = {"id": "1", "role": "Designer"}

        result = scorer.score_persona(persona)

        role_conf = next(
            a for a in result.attribute_confidences if a.attribute == "role"
        )
        assert role_conf.confidence == ConfidenceLevel.MEDIUM

    def test_score_personas_multiple(self):
        """Scores multiple personas."""
        scorer = ConfidenceScorer()
        personas = [
            {"id": "1", "role": "Developer"},
            {"id": "2", "role": "Designer"},
            {"id": "3", "role": "Manager"},
        ]

        results = scorer.score_personas(personas)

        assert len(results) == 3
        assert results[0].persona_id == "1"
        assert results[2].persona_id == "3"

    def test_custom_thresholds(self):
        """Respects custom confidence thresholds."""
        scorer = ConfidenceScorer(high_threshold=5, medium_threshold=2)
        persona = {"id": "1", "role": "Developer"}
        source_data = {"s1.md": "developer developer developer"}  # 3 mentions

        result = scorer.score_persona(persona, source_data)

        role_conf = next(
            a for a in result.attribute_confidences if a.attribute == "role"
        )
        # 3 mentions is above medium (2) but below high (5)
        assert role_conf.confidence == ConfidenceLevel.MEDIUM

    def test_evidence_map_override(self):
        """Uses pre-computed evidence map when provided."""
        scorer = ConfidenceScorer()
        persona = {"id": "1", "role": "Developer", "goals": ["testing"]}
        evidence_map = {
            "role": ["s1.md", "s2.md", "s3.md", "s4.md"],
            "goals": [],
        }

        result = scorer.score_persona(persona, evidence_map=evidence_map)

        role_conf = next(
            a for a in result.attribute_confidences if a.attribute == "role"
        )
        goals_conf = next(
            a for a in result.attribute_confidences if a.attribute == "goals"
        )

        assert role_conf.confidence == ConfidenceLevel.HIGH
        assert goals_conf.confidence == ConfidenceLevel.LOW

    def test_overall_confidence_calculation(self):
        """Calculates overall confidence from attribute mix."""
        scorer = ConfidenceScorer()
        persona = {
            "id": "1",
            "role": "Developer",
            "goals": ["goal1"],
            "frustrations": ["frust1"],
            "background": "Some background",
        }

        result = scorer.score_persona(persona)

        # Should calculate overall based on mix
        assert result.overall_confidence in [
            ConfidenceLevel.HIGH,
            ConfidenceLevel.MEDIUM,
            ConfidenceLevel.LOW,
        ]
        assert 0.0 <= result.confidence_score <= 1.0


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_score_confidence(self):
        """score_confidence convenience function works."""
        persona = {"id": "1", "role": "Developer"}

        result = score_confidence(persona)

        assert isinstance(result, PersonaConfidence)

    def test_add_confidence_to_persona(self):
        """add_confidence_to_persona adds confidence info."""
        persona = {
            "id": "1",
            "role": "Developer",
            "goals": ["testing"],
        }

        enhanced = add_confidence_to_persona(persona)

        assert "confidence" in enhanced
        assert "overall" in enhanced["confidence"]
        assert "score" in enhanced["confidence"]
        assert "attributes" in enhanced["confidence"]
        # Original data preserved
        assert enhanced["id"] == "1"
        assert enhanced["role"] == "Developer"
