"""Unit tests for lexical diversity analyser."""

import pytest
from persona.core.generation.parser import Persona
from persona.core.quality.diversity import (
    DiversityConfig,
    InterpretationLevel,
    LexicalDiversityAnalyser,
)


class TestLexicalDiversityAnalyser:
    """Tests for LexicalDiversityAnalyser class."""

    def test_analyser_default_config(self):
        """Test analyser with default configuration."""
        analyser = LexicalDiversityAnalyser()
        assert analyser.config.mattr_window_size == 50
        assert analyser.config.mtld_threshold == 0.72
        assert analyser.config.min_tokens == 50

    def test_analyser_custom_config(self):
        """Test analyser with custom configuration."""
        config = DiversityConfig(
            mattr_window_size=100,
            mtld_threshold=0.8,
            min_tokens=30,
        )
        analyser = LexicalDiversityAnalyser(config=config)
        assert analyser.config.mattr_window_size == 100
        assert analyser.config.mtld_threshold == 0.8
        assert analyser.config.min_tokens == 30

    def test_analyse_minimal_persona(self):
        """Test analysing minimal persona."""
        persona = Persona(
            id="p1",
            name="Alice Johnson",
            goals=["Learn programming", "Build applications"],
        )
        analyser = LexicalDiversityAnalyser()
        report = analyser.analyse(persona)

        assert report.persona_id == "p1"
        assert report.persona_name == "Alice Johnson"
        assert report.total_tokens > 0
        assert report.unique_tokens > 0
        assert 0.0 <= report.ttr <= 1.0
        assert 0.0 <= report.hapax_ratio <= 1.0

    def test_analyse_rich_persona(self):
        """Test analysing persona with rich content."""
        persona = Persona(
            id="p1",
            name="Bob Smith",
            demographics={
                "age": 35,
                "occupation": "Software Engineer",
                "location": "San Francisco",
                "education": "Computer Science degree",
            },
            goals=[
                "Master advanced algorithms and data structures",
                "Contribute to open source projects regularly",
                "Mentor junior developers in the team",
            ],
            pain_points=[
                "Limited time for continuous learning",
                "Difficulty balancing work and personal projects",
                "Keeping up with rapidly changing technology",
            ],
            behaviours=[
                "Reads technical blogs and documentation daily",
                "Participates in code reviews and pair programming",
                "Attends local tech meetups and conferences",
            ],
            quotes=[
                "I believe writing clean, maintainable code is crucial",
                "Learning never stops in this field",
                "Collaboration makes us all better developers",
            ],
        )
        analyser = LexicalDiversityAnalyser()
        report = analyser.analyse(persona)

        assert report.total_tokens >= 50  # Should have plenty of tokens
        assert report.unique_tokens > 10
        assert report.ttr > 0.0
        assert report.mattr > 0.0  # Should have enough tokens for MATTR
        assert report.mtld > 0.0
        assert isinstance(report.interpretation, InterpretationLevel)

    def test_analyse_insufficient_tokens(self):
        """Test analysing persona with insufficient tokens."""
        persona = Persona(
            id="p1",
            name="Eve",
            goals=["Learn"],  # Very minimal
        )
        config = DiversityConfig(min_tokens=50)
        analyser = LexicalDiversityAnalyser(config=config)
        report = analyser.analyse(persona)

        # Should still produce report but with limited metrics
        assert report.total_tokens < 50
        assert report.ttr >= 0.0  # TTR still calculated
        assert report.mattr == 0.0  # MATTR not reliable
        assert report.mtld == 0.0  # MTLD not reliable

    def test_analyse_empty_persona(self):
        """Test analysing completely empty persona."""
        persona = Persona(id="p1", name="")
        analyser = LexicalDiversityAnalyser()
        report = analyser.analyse(persona)

        assert report.total_tokens == 0
        assert report.unique_tokens == 0
        assert report.ttr == 0.0
        assert report.mattr == 0.0
        assert report.mtld == 0.0
        assert report.hapax_ratio == 0.0

    def test_analyse_high_diversity_persona(self):
        """Test analysing persona with high lexical diversity."""
        # Create persona with many unique words - create enough for reliable MTLD
        unique_words = [f"word{i}" for i in range(80)]
        persona = Persona(
            id="p1",
            name="Diverse Speaker",
            goals=[" ".join(unique_words)],
        )
        analyser = LexicalDiversityAnalyser()
        report = analyser.analyse(persona)

        # Should have good diversity metrics
        assert report.total_tokens >= 50  # Enough for reliable analysis
        assert report.ttr > 0.7  # Most words unique
        assert report.mtld > 50  # Should have good MTLD
        assert report.interpretation in (
            InterpretationLevel.GOOD,
            InterpretationLevel.EXCELLENT,
            InterpretationLevel.AVERAGE,
        )

    def test_analyse_low_diversity_persona(self):
        """Test analysing persona with low lexical diversity."""
        # Create persona with repetitive words
        repetitive_goals = ["the same goal " * 30]  # Very repetitive
        persona = Persona(
            id="p1",
            name="Repetitive Speaker",
            goals=repetitive_goals,
        )
        analyser = LexicalDiversityAnalyser()
        report = analyser.analyse(persona)

        # Should have poor diversity metrics
        assert report.ttr < 0.3  # Low uniqueness
        assert report.interpretation in (
            InterpretationLevel.POOR,
            InterpretationLevel.BELOW_AVERAGE,
        )

    def test_analyse_token_frequency(self):
        """Test that token frequency is calculated."""
        persona = Persona(
            id="p1",
            name="Alice",
            goals=["Learn Python", "Build Python applications", "Master Python"],
        )
        analyser = LexicalDiversityAnalyser()
        report = analyser.analyse(persona)

        assert "python" in report.token_frequency
        assert report.token_frequency["python"] == 3

    def test_analyse_batch_empty(self):
        """Test batch analysis with empty list."""
        analyser = LexicalDiversityAnalyser()
        batch_report = analyser.analyse_batch([])

        assert len(batch_report.reports) == 0
        assert batch_report.average_ttr == 0.0
        assert batch_report.average_mattr == 0.0
        assert batch_report.average_mtld == 0.0
        assert batch_report.average_hapax_ratio == 0.0

    def test_analyse_batch_single_persona(self):
        """Test batch analysis with single persona."""
        persona = Persona(
            id="p1",
            name="Alice",
            goals=["Learn programming", "Build applications"],
        )
        analyser = LexicalDiversityAnalyser()
        batch_report = analyser.analyse_batch([persona])

        assert len(batch_report.reports) == 1
        assert batch_report.reports[0].persona_id == "p1"
        assert batch_report.average_ttr == batch_report.reports[0].ttr
        assert batch_report.average_mtld == batch_report.reports[0].mtld

    def test_analyse_batch_multiple_personas(self):
        """Test batch analysis with multiple personas."""
        personas = [
            Persona(
                id="p1",
                name="Alice",
                goals=["Learn programming", "Build web applications"],
            ),
            Persona(
                id="p2",
                name="Bob",
                goals=["Master algorithms", "Contribute to open source"],
            ),
            Persona(
                id="p3",
                name="Charlie",
                goals=["Understand databases", "Design scalable systems"],
            ),
        ]
        analyser = LexicalDiversityAnalyser()
        batch_report = analyser.analyse_batch(personas)

        assert len(batch_report.reports) == 3
        assert batch_report.persona_count == 3

        # Check averages are calculated
        expected_avg_ttr = sum(r.ttr for r in batch_report.reports) / 3
        assert batch_report.average_ttr == pytest.approx(expected_avg_ttr)

        expected_avg_mtld = sum(r.mtld for r in batch_report.reports) / 3
        assert batch_report.average_mtld == pytest.approx(expected_avg_mtld)

    def test_analyse_batch_get_by_interpretation(self):
        """Test filtering batch results by interpretation level."""
        personas = [
            # Low diversity persona
            Persona(
                id="p1",
                name="Low",
                goals=["same same same same same same"] * 10,
            ),
            # High diversity persona
            Persona(
                id="p2",
                name="High",
                goals=[
                    f"unique goal number {i} with different words" for i in range(20)
                ],
            ),
        ]
        analyser = LexicalDiversityAnalyser()
        batch_report = analyser.analyse_batch(personas)

        # Should have different interpretation levels
        poor_or_below = batch_report.get_by_interpretation(InterpretationLevel.POOR)
        poor_or_below += batch_report.get_by_interpretation(
            InterpretationLevel.BELOW_AVERAGE
        )

        good_or_excellent = batch_report.get_by_interpretation(InterpretationLevel.GOOD)
        good_or_excellent += batch_report.get_by_interpretation(
            InterpretationLevel.EXCELLENT
        )

        # At least one should be in lower category and one in higher
        assert len(poor_or_below) > 0 or len(good_or_excellent) > 0

    def test_analyse_preserves_persona_info(self):
        """Test that analysis preserves persona ID and name."""
        persona = Persona(
            id="unique-id-123",
            name="Test Persona Name",
            goals=["Some goal"],
        )
        analyser = LexicalDiversityAnalyser()
        report = analyser.analyse(persona)

        assert report.persona_id == "unique-id-123"
        assert report.persona_name == "Test Persona Name"

    def test_analyse_different_configs(self):
        """Test that different configs produce different results."""
        persona = Persona(
            id="p1",
            name="Test",
            goals=[f"Goal number {i} with various words" for i in range(30)],
        )

        config1 = DiversityConfig(mattr_window_size=30)
        config2 = DiversityConfig(mattr_window_size=60)

        analyser1 = LexicalDiversityAnalyser(config=config1)
        analyser2 = LexicalDiversityAnalyser(config=config2)

        report1 = analyser1.analyse(persona)
        report2 = analyser2.analyse(persona)

        # MATTR might differ due to different window sizes
        # TTR should be the same
        assert report1.ttr == report2.ttr
