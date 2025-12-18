"""Tests for bias detector orchestrator."""

import pytest
from persona.core.generation.parser import Persona
from persona.core.quality.bias.detector import BiasDetector
from persona.core.quality.bias.models import (
    BiasCategory,
    BiasConfig,
    BiasFinding,
    Severity,
)


class MockLLMProvider:
    """Mock LLM provider for testing."""

    def __init__(self, response="[]"):
        self.response = response
        self.calls = []

    def complete(self, prompt: str) -> str:
        """Mock completion."""
        self.calls.append(prompt)
        return self.response


class TestBiasDetector:
    """Tests for BiasDetector."""

    @pytest.fixture
    def clean_persona(self):
        """Create a clean persona."""
        return Persona.from_dict(
            {
                "id": "clean-1",
                "name": "Clean Person",
                "demographics": {
                    "age": 30,
                    "occupation": "engineer",
                },
                "behaviours": ["Works systematically"],
                "goals": ["Build great products"],
                "pain_points": ["Time constraints"],
            }
        )

    @pytest.fixture
    def biased_persona(self):
        """Create a biased persona."""
        return Persona.from_dict(
            {
                "id": "biased-1",
                "name": "Biased Person",
                "demographics": {
                    "age": 28,
                    "gender": "female",
                    "occupation": "nurse",
                },
                "behaviours": [
                    "Very emotional and nurturing",
                    "Technophobic and confused by computers",
                ],
                "goals": ["Care for others"],
                "pain_points": ["Too sensitive for leadership"],
                "quote": "I'm naturally caring",
            }
        )

    def test_detector_initialization(self):
        """Test detector initialization."""
        config = BiasConfig(methods=["lexicon"])
        detector = BiasDetector(config)

        assert detector.config is not None
        assert detector.lexicon is not None

    def test_detector_with_custom_config(self):
        """Test detector with custom configuration."""
        config = BiasConfig(
            methods=["lexicon"],
            categories=["gender"],
            threshold=0.5,
        )
        detector = BiasDetector(config)

        assert detector.config.methods == ["lexicon"]
        assert detector.config.categories == ["gender"]
        assert detector.config.threshold == 0.5

    def test_analyse_clean_persona_lexicon_only(self, clean_persona):
        """Test analysing clean persona with lexicon method."""
        config = BiasConfig(methods=["lexicon"], categories=["gender", "age"])
        detector = BiasDetector(config)

        report = detector.analyse(clean_persona)

        assert report.persona_id == "clean-1"
        assert report.persona_name == "Clean Person"
        assert report.overall_score >= 0.0
        # Clean persona should have low bias score
        assert len(report.findings) <= 1
        assert "lexicon" in report.methods_used

    def test_analyse_biased_persona_lexicon_only(self, biased_persona):
        """Test analysing biased persona with lexicon method."""
        config = BiasConfig(methods=["lexicon"], categories=["gender", "age"])
        detector = BiasDetector(config)

        report = detector.analyse(biased_persona)

        assert report.persona_id == "biased-1"
        assert len(report.findings) > 0
        assert report.has_bias
        assert report.overall_score > 0.0

    def test_analyse_with_llm_judge(self, biased_persona):
        """Test analysis with LLM judge."""
        # Mock LLM response with bias findings
        mock_llm_response = """[
            {
                "category": "gender",
                "description": "Gender stereotype detected",
                "evidence": "Very emotional and nurturing",
                "severity": "medium",
                "confidence": 0.8
            }
        ]"""

        mock_llm = MockLLMProvider(response=mock_llm_response)
        config = BiasConfig(methods=["llm"], categories=["gender"])
        detector = BiasDetector(config, llm_provider=mock_llm)

        report = detector.analyse(biased_persona)

        assert len(mock_llm.calls) == 1  # LLM was called
        assert "llm" in report.methods_used

    def test_aggregate_scores_by_category(self):
        """Test score aggregation by category."""
        config = BiasConfig(methods=["lexicon"])
        detector = BiasDetector(config)

        findings = [
            BiasFinding(
                category=BiasCategory.GENDER,
                description="Bias 1",
                evidence="Evidence 1",
                severity=Severity.HIGH,
                method="lexicon",
                confidence=0.9,
            ),
            BiasFinding(
                category=BiasCategory.GENDER,
                description="Bias 2",
                evidence="Evidence 2",
                severity=Severity.MEDIUM,
                method="lexicon",
                confidence=0.7,
            ),
            BiasFinding(
                category=BiasCategory.AGE,
                description="Bias 3",
                evidence="Evidence 3",
                severity=Severity.LOW,
                method="lexicon",
                confidence=0.5,
            ),
        ]

        scores = detector._aggregate_scores(findings)

        assert "gender" in scores
        assert "age" in scores
        assert scores["gender"] > scores["age"]  # Higher severity = higher score

    def test_calculate_overall_score(self):
        """Test overall score calculation."""
        config = BiasConfig(methods=["lexicon"])
        detector = BiasDetector(config)

        category_scores = {
            "gender": 0.8,
            "racial": 0.3,
            "age": 0.5,
        }

        overall = detector._calculate_overall(category_scores)

        expected = (0.8 + 0.3 + 0.5) / 3
        assert abs(overall - expected) < 0.01

    def test_deduplicate_findings(self):
        """Test finding deduplication."""
        config = BiasConfig(methods=["lexicon"])
        detector = BiasDetector(config)

        findings = [
            BiasFinding(
                category=BiasCategory.GENDER,
                description="Bias 1",
                evidence="Same evidence text",
                severity=Severity.MEDIUM,
                method="lexicon",
                confidence=0.8,
            ),
            BiasFinding(
                category=BiasCategory.GENDER,
                description="Bias 2",
                evidence="Same evidence text",
                severity=Severity.MEDIUM,
                method="embedding",
                confidence=0.7,
            ),
            BiasFinding(
                category=BiasCategory.AGE,
                description="Bias 3",
                evidence="Different evidence",
                severity=Severity.LOW,
                method="llm",
                confidence=0.6,
            ),
        ]

        deduplicated = detector._deduplicate_findings(findings)

        # Should remove duplicate based on category and evidence
        assert len(deduplicated) == 2

    def test_confidence_threshold_filtering(self, biased_persona):
        """Test that low-confidence findings are filtered."""
        config = BiasConfig(
            methods=["lexicon"],
            categories=["gender"],
            threshold=0.95,  # Very high threshold
        )
        detector = BiasDetector(config)

        report = detector.analyse(biased_persona)

        # With high threshold, should have fewer findings
        for finding in report.findings:
            assert finding.confidence >= 0.95

    def test_empty_persona_handling(self):
        """Test handling of persona with no content."""
        config = BiasConfig(methods=["lexicon"])
        detector = BiasDetector(config)

        empty_persona = Persona.from_dict(
            {
                "id": "empty-1",
                "name": "Empty",
                "demographics": {},
                "behaviours": [],
                "goals": [],
                "pain_points": [],
            }
        )

        report = detector.analyse(empty_persona)

        assert report.persona_id == "empty-1"
        assert len(report.findings) == 0
        assert report.overall_score == 0.0

    def test_category_scores_in_report(self, biased_persona):
        """Test that category scores are included in report."""
        config = BiasConfig(
            methods=["lexicon"],
            categories=["gender", "age"],
        )
        detector = BiasDetector(config)

        report = detector.analyse(biased_persona)

        assert "gender" in report.category_scores
        assert "age" in report.category_scores
        # All scores should be 0-1 range
        for score in report.category_scores.values():
            assert 0.0 <= score <= 1.0

    def test_methods_used_tracking(self, biased_persona):
        """Test that methods used are tracked in report."""
        config = BiasConfig(methods=["lexicon"])
        detector = BiasDetector(config)

        report = detector.analyse(biased_persona)

        assert report.methods_used == ["lexicon"]

    def test_graceful_failure_handling(self, biased_persona):
        """Test that detector handles failures gracefully."""
        # Use invalid lexicon to trigger error
        config = BiasConfig(
            methods=["lexicon"],
            lexicon="nonexistent",
        )

        # Should not raise, but detector won't have lexicon
        detector = BiasDetector(config)
        report = detector.analyse(biased_persona)

        # Should still return a valid report
        assert report is not None
        assert report.persona_id == "biased-1"
