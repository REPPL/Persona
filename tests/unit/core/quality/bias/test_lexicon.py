"""Tests for lexicon-based bias detection."""

import pytest

from persona.core.generation.parser import Persona
from persona.core.quality.bias.lexicon import LexiconMatcher
from persona.core.quality.bias.models import BiasCategory, Severity


class TestLexiconMatcher:
    """Tests for LexiconMatcher."""

    @pytest.fixture
    def matcher(self):
        """Create a lexicon matcher."""
        return LexiconMatcher("holisticbias")

    @pytest.fixture
    def biased_persona(self):
        """Create a persona with bias indicators."""
        return Persona.from_dict({
            "id": "test-1",
            "name": "Test Person",
            "demographics": {
                "age": 30,
                "gender": "female",
                "occupation": "nurse",
            },
            "behaviours": [
                "She is very emotional and caring",
                "Acts nurturing towards children",
            ],
            "goals": ["Maintain work-life balance"],
            "pain_points": ["Too sensitive for leadership roles"],
            "quote": "I'm naturally good at caring for others",
        })

    @pytest.fixture
    def clean_persona(self):
        """Create a persona without obvious bias."""
        return Persona.from_dict({
            "id": "test-2",
            "name": "Clean Person",
            "demographics": {
                "age": 35,
                "gender": "female",
                "occupation": "software engineer",
            },
            "behaviours": [
                "Works systematically on complex problems",
                "Collaborates effectively with team",
            ],
            "goals": ["Build scalable systems"],
            "pain_points": ["Limited time for deep work"],
            "quote": "I enjoy solving challenging technical problems",
        })

    def test_lexicon_loads(self, matcher):
        """Test that lexicon loads successfully."""
        assert matcher.lexicon is not None
        assert "gender" in matcher.lexicon
        assert "racial" in matcher.lexicon
        assert "age" in matcher.lexicon
        assert "professional" in matcher.lexicon

    def test_extract_persona_text(self, matcher, biased_persona):
        """Test extracting text from persona."""
        texts = matcher._extract_persona_text(biased_persona)

        assert len(texts) > 0
        assert any("emotional" in text.lower() for text in texts.values())
        assert any("nurturing" in text.lower() for text in texts.values())

    def test_match_patterns_finds_bias(self, matcher):
        """Test pattern matching finds bias terms."""
        text = "She is very emotional and nurturing"
        patterns = ["emotional", "nurturing", "weak"]

        matches = matcher._match_patterns(
            text, patterns, BiasCategory.GENDER, Severity.MEDIUM
        )

        assert len(matches) >= 2
        matched_patterns = [m[0] for m in matches]
        assert "emotional" in matched_patterns
        assert "nurturing" in matched_patterns

    def test_match_patterns_case_insensitive(self, matcher):
        """Test that matching is case-insensitive."""
        text = "She is VERY EMOTIONAL"
        patterns = ["emotional"]

        matches = matcher._match_patterns(
            text, patterns, BiasCategory.GENDER, Severity.MEDIUM
        )

        assert len(matches) == 1

    def test_determine_severity(self, matcher):
        """Test severity determination."""
        # High severity
        high_severity = matcher._determine_severity(
            "hysterical", BiasCategory.GENDER, "context"
        )
        assert high_severity == Severity.HIGH

        # Medium severity
        medium_severity = matcher._determine_severity(
            "emotional", BiasCategory.GENDER, "context"
        )
        assert medium_severity == Severity.MEDIUM

        # Low severity
        low_severity = matcher._determine_severity(
            "gentle", BiasCategory.GENDER, "context"
        )
        assert low_severity == Severity.LOW

    def test_analyse_gender_finds_stereotypes(self, matcher, biased_persona):
        """Test gender bias detection."""
        texts = matcher._extract_persona_text(biased_persona)
        findings = matcher.analyse_gender(texts, ["gender"])

        assert len(findings) > 0
        assert all(f.category == BiasCategory.GENDER for f in findings)
        assert any("emotional" in f.evidence.lower() for f in findings)

    def test_analyse_gender_skips_when_not_requested(self, matcher, biased_persona):
        """Test gender analysis skips when category not requested."""
        texts = matcher._extract_persona_text(biased_persona)
        findings = matcher.analyse_gender(texts, ["racial", "age"])

        assert len(findings) == 0

    def test_analyse_clean_persona(self, matcher, clean_persona):
        """Test that clean persona has few/no findings."""
        findings = matcher.analyse(clean_persona, ["gender", "racial", "age"])

        # Clean persona should have minimal findings
        assert len(findings) <= 1

    def test_analyse_biased_persona(self, matcher, biased_persona):
        """Test full analysis on biased persona."""
        findings = matcher.analyse(
            biased_persona, ["gender", "racial", "age", "professional"]
        )

        assert len(findings) > 0
        # Should find gender-related biases
        gender_findings = [f for f in findings if f.category == BiasCategory.GENDER]
        assert len(gender_findings) > 0

    def test_analyse_multiple_categories(self, matcher):
        """Test analysis across multiple categories."""
        persona = Persona.from_dict({
            "id": "test-3",
            "name": "Multi Bias",
            "demographics": {
                "age": 65,
                "occupation": "retired",
            },
            "behaviours": [
                "Is very emotional",  # Gender stereotype
                "Technophobic and forgetful",  # Age stereotype
            ],
            "goals": [],
            "pain_points": [],
        })

        findings = matcher.analyse(persona, ["gender", "age"])

        # Should find both gender and age biases
        categories_found = {f.category for f in findings}
        assert BiasCategory.GENDER in categories_found or BiasCategory.AGE in categories_found

    def test_confidence_scores(self, matcher, biased_persona):
        """Test that findings have appropriate confidence scores."""
        findings = matcher.analyse(biased_persona, ["gender"])

        for finding in findings:
            assert 0.0 <= finding.confidence <= 1.0
            # Lexicon-based should have relatively high confidence
            assert finding.confidence >= 0.5

    def test_method_attribution(self, matcher, biased_persona):
        """Test that findings are attributed to lexicon method."""
        findings = matcher.analyse(biased_persona, ["gender"])

        for finding in findings:
            assert finding.method == "lexicon"
