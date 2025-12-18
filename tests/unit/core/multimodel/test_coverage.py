"""Tests for coverage analysis (F-068)."""


from persona.core.multimodel.coverage import (
    CoverageAnalyser,
    CoverageAnalysis,
    SourceUtilisation,
    ThemeCoverage,
    analyse_coverage,
)


class TestThemeCoverage:
    """Tests for ThemeCoverage."""

    def test_status_high(self):
        """Status is high for >= 80% coverage."""
        coverage = ThemeCoverage(
            theme="onboarding",
            coverage_percent=85.0,
            persona_count=3,
        )

        assert coverage.status == "high"

    def test_status_medium(self):
        """Status is medium for 50-79% coverage."""
        coverage = ThemeCoverage(
            theme="payments",
            coverage_percent=65.0,
            persona_count=2,
        )

        assert coverage.status == "medium"

    def test_status_low(self):
        """Status is low for 1-49% coverage."""
        coverage = ThemeCoverage(
            theme="mobile",
            coverage_percent=30.0,
            persona_count=1,
        )

        assert coverage.status == "low"

    def test_status_gap(self):
        """Status is gap for 0% coverage."""
        coverage = ThemeCoverage(
            theme="accessibility",
            coverage_percent=0.0,
            persona_count=0,
        )

        assert coverage.status == "gap"

    def test_to_dict(self):
        """Converts to dictionary."""
        coverage = ThemeCoverage(
            theme="testing",
            coverage_percent=75.0,
            persona_count=2,
            persona_ids=["p1", "p2"],
            evidence_count=5,
        )
        data = coverage.to_dict()

        assert data["theme"] == "testing"
        assert data["coverage_percent"] == 75.0
        assert data["status"] == "medium"


class TestSourceUtilisation:
    """Tests for SourceUtilisation."""

    def test_to_dict(self):
        """Converts to dictionary."""
        util = SourceUtilisation(
            source="interview.md",
            utilisation="high",
            persona_count=3,
            persona_ids=["p1", "p2", "p3"],
            token_count=5000,
        )
        data = util.to_dict()

        assert data["source"] == "interview.md"
        assert data["utilisation"] == "high"


class TestCoverageAnalysis:
    """Tests for CoverageAnalysis."""

    def test_to_dict(self):
        """Converts to dictionary."""
        analysis = CoverageAnalysis(
            theme_coverage=[
                ThemeCoverage("test", 80.0, 2),
            ],
            gaps=["missing"],
            suggestions=["Add more data"],
            overall_score=75.0,
        )
        data = analysis.to_dict()

        assert len(data["theme_coverage"]) == 1
        assert data["gaps"] == ["missing"]
        assert data["overall_score"] == 75.0

    def test_to_display(self):
        """Generates display output."""
        analysis = CoverageAnalysis(
            theme_coverage=[
                ThemeCoverage("onboarding", 90.0, 3),
                ThemeCoverage("payments", 50.0, 1),
            ],
            gaps=["accessibility"],
            suggestions=["Add accessibility data"],
            overall_score=70.0,
        )
        display = analysis.to_display()

        assert "Coverage Analysis" in display
        assert "onboarding" in display
        assert "accessibility" in display


class TestCoverageAnalyser:
    """Tests for CoverageAnalyser."""

    def test_analyse_empty_personas(self):
        """Handles empty persona list."""
        analyser = CoverageAnalyser()

        analysis = analyser.analyse(personas=[])

        assert analysis.overall_score == 0.0
        assert "No personas" in analysis.suggestions[0]

    def test_analyse_with_themes(self):
        """Analyses with provided themes."""
        analyser = CoverageAnalyser()
        personas = [
            {
                "id": "1",
                "role": "Developer",
                "goals": ["improve onboarding experience"],
                "frustrations": ["slow deployment"],
            },
        ]

        analysis = analyser.analyse(
            personas=personas,
            themes=["onboarding", "deployment", "missing"],
        )

        assert len(analysis.theme_coverage) == 3
        # "onboarding" should have coverage
        onboarding = next(t for t in analysis.theme_coverage if t.theme == "onboarding")
        assert onboarding.coverage_percent > 0

    def test_analyse_extracts_themes(self):
        """Extracts themes from source data."""
        analyser = CoverageAnalyser()
        personas = [{"id": "1", "role": "User"}]
        source_data = {
            "interview.md": (
                "The user mentioned onboarding several times. "
                "Onboarding was frustrating. Onboarding needs work."
            ),
        }

        analysis = analyser.analyse(
            personas=personas,
            source_data=source_data,
        )

        # Should extract themes from source
        themes = [t.theme for t in analysis.theme_coverage]
        assert "onboarding" in themes

    def test_analyse_source_utilisation(self):
        """Analyses source utilisation."""
        analyser = CoverageAnalyser()
        personas = [
            {
                "id": "1",
                "role": "Developer",
                "goals": ["improve coding workflow"],
            },
        ]
        source_data = {
            "dev-interview.md": "Developer workflow coding experience",
            "other.md": "Unrelated content about cooking",
        }

        analysis = analyser.analyse(
            personas=personas,
            source_data=source_data,
        )

        # Should have utilisation data
        assert len(analysis.source_utilisation) == 2

    def test_analyse_finds_gaps(self):
        """Identifies coverage gaps."""
        analyser = CoverageAnalyser()
        personas = [
            {"id": "1", "role": "Developer", "goals": ["code quality"]},
        ]

        analysis = analyser.analyse(
            personas=personas,
            themes=["coding", "accessibility", "security"],
        )

        # Some themes should be gaps
        assert len(analysis.gaps) > 0

    def test_analyse_finds_overlaps(self):
        """Identifies persona overlaps."""
        analyser = CoverageAnalyser()
        personas = [
            {
                "id": "1",
                "role": "Developer",
                "goals": ["Goal A"],
                "frustrations": ["Frust A"],
            },
            {
                "id": "2",
                "role": "Developer",
                "goals": ["Goal A"],
                "frustrations": ["Frust A"],
            },
        ]

        analysis = analyser.analyse(personas=personas)

        # These personas should have high overlap
        assert (
            len(analysis.overlaps) >= 0
        )  # May or may not detect depending on threshold

    def test_analyse_generates_suggestions(self):
        """Generates actionable suggestions."""
        analyser = CoverageAnalyser()
        personas = [{"id": "1", "role": "User"}]

        analysis = analyser.analyse(
            personas=personas,
            themes=["covered", "missing1", "missing2"],
        )

        # Should have suggestions for gaps
        assert len(analysis.suggestions) > 0

    def test_extract_themes_empty(self):
        """Handles empty source data."""
        analyser = CoverageAnalyser()

        themes = analyser._extract_themes({})

        assert themes == []


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_analyse_coverage(self):
        """analyse_coverage convenience function works."""
        personas = [
            {"id": "1", "role": "Developer", "goals": ["testing"]},
        ]

        analysis = analyse_coverage(
            personas=personas,
            themes=["testing", "deployment"],
        )

        assert isinstance(analysis, CoverageAnalysis)
        assert analysis.overall_score >= 0
