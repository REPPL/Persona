"""Coverage analysis for persona generation (F-068).

Analyses how well generated personas represent the source data,
identifying gaps, overlaps, and theme coverage.
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ThemeCoverage:
    """Coverage information for a theme.

    Attributes:
        theme: The theme name.
        coverage_percent: Percentage of coverage (0-100).
        persona_count: Number of personas covering this theme.
        persona_ids: IDs of personas covering this theme.
        evidence_count: Number of evidence mentions.
    """

    theme: str
    coverage_percent: float
    persona_count: int
    persona_ids: list[str] = field(default_factory=list)
    evidence_count: int = 0

    @property
    def status(self) -> str:
        """Get coverage status icon."""
        if self.coverage_percent >= 80:
            return "high"
        elif self.coverage_percent >= 50:
            return "medium"
        elif self.coverage_percent > 0:
            return "low"
        else:
            return "gap"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "theme": self.theme,
            "coverage_percent": self.coverage_percent,
            "persona_count": self.persona_count,
            "persona_ids": self.persona_ids,
            "evidence_count": self.evidence_count,
            "status": self.status,
        }


@dataclass
class SourceUtilisation:
    """Utilisation information for a data source.

    Attributes:
        source: Source file or identifier.
        utilisation: Utilisation level (high/medium/low).
        persona_count: Number of personas supported.
        persona_ids: IDs of personas this source supports.
        token_count: Approximate tokens in source.
    """

    source: str
    utilisation: str
    persona_count: int
    persona_ids: list[str] = field(default_factory=list)
    token_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "utilisation": self.utilisation,
            "persona_count": self.persona_count,
            "persona_ids": self.persona_ids,
            "token_count": self.token_count,
        }


@dataclass
class CoverageAnalysis:
    """Complete coverage analysis result.

    Attributes:
        theme_coverage: Coverage by theme.
        source_utilisation: Utilisation by source.
        persona_backing: Which sources back each persona.
        gaps: Themes with no coverage.
        overlaps: Pairs of personas with high overlap.
        suggestions: Actionable suggestions.
        overall_score: Overall coverage score (0-100).
    """

    theme_coverage: list[ThemeCoverage] = field(default_factory=list)
    source_utilisation: list[SourceUtilisation] = field(default_factory=list)
    persona_backing: dict[str, list[str]] = field(default_factory=dict)
    gaps: list[str] = field(default_factory=list)
    overlaps: list[tuple[str, str, float]] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    overall_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "theme_coverage": [t.to_dict() for t in self.theme_coverage],
            "source_utilisation": [s.to_dict() for s in self.source_utilisation],
            "persona_backing": self.persona_backing,
            "gaps": self.gaps,
            "overlaps": [
                {"persona_a": a, "persona_b": b, "overlap": o}
                for a, b, o in self.overlaps
            ],
            "suggestions": self.suggestions,
            "overall_score": self.overall_score,
        }

    def to_display(self) -> str:
        """Generate human-readable display."""
        lines = ["Coverage Analysis", "=" * 50, ""]

        # Theme coverage
        lines.append("Theme Coverage:")
        for theme in sorted(self.theme_coverage, key=lambda t: -t.coverage_percent):
            icon = {"high": "✓", "medium": "◐", "low": "⚠", "gap": "✗"}[theme.status]
            lines.append(
                f"  {icon} {theme.theme:25} {theme.coverage_percent:5.1f}% "
                f"({theme.persona_count} personas)"
            )

        # Gaps
        if self.gaps:
            lines.append("")
            lines.append("Gaps (themes with no coverage):")
            for gap in self.gaps:
                lines.append(f"  ✗ {gap}")

        # Source utilisation
        lines.append("")
        lines.append("Source Utilisation:")
        for source in self.source_utilisation:
            lines.append(
                f"  ├─ {source.source:30} {source.utilisation:6} "
                f"(supports {source.persona_count} personas)"
            )

        # Suggestions
        if self.suggestions:
            lines.append("")
            lines.append("Suggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        # Overall score
        lines.append("")
        lines.append(f"Overall Coverage Score: {self.overall_score:.1f}%")

        return "\n".join(lines)


class CoverageAnalyser:
    """Analyser for persona coverage.

    Examines how well generated personas represent the source data,
    identifying themes, gaps, and areas for improvement.

    Example:
        >>> analyser = CoverageAnalyser()
        >>> analysis = analyser.analyse(
        ...     personas=[{"id": "1", "role": "Developer", ...}],
        ...     source_data={"interviews.md": "content..."},
        ...     themes=["onboarding", "payments", "mobile"]
        ... )
    """

    # Common stopwords to ignore in theme extraction
    STOPWORDS = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "dare",
        "ought",
        "used",
        "to",
        "of",
        "in",
        "for",
        "on",
        "with",
        "at",
        "by",
        "from",
        "as",
        "into",
        "through",
        "during",
        "before",
        "after",
        "above",
        "below",
        "between",
        "under",
        "again",
        "further",
        "then",
        "once",
        "here",
        "there",
        "when",
        "where",
        "why",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "not",
        "only",
        "own",
        "same",
        "so",
        "than",
        "too",
        "very",
        "just",
        "and",
        "but",
        "if",
        "or",
        "because",
        "until",
        "while",
        "that",
        "this",
        "these",
        "those",
        "what",
        "which",
        "who",
        "whom",
        "i",
        "me",
        "my",
        "myself",
        "we",
        "our",
        "you",
        "your",
        "he",
        "him",
        "his",
        "she",
        "her",
        "it",
        "its",
        "they",
        "them",
        "their",
    }

    def __init__(self, min_theme_mentions: int = 3):
        """Initialise the analyser.

        Args:
            min_theme_mentions: Minimum mentions to consider a theme.
        """
        self.min_theme_mentions = min_theme_mentions

    def analyse(
        self,
        personas: list[dict[str, Any]],
        source_data: dict[str, str] | None = None,
        themes: list[str] | None = None,
    ) -> CoverageAnalysis:
        """Analyse coverage of personas against source data.

        Args:
            personas: List of generated personas.
            source_data: Dict mapping source names to content.
            themes: Optional list of expected themes to check.

        Returns:
            CoverageAnalysis with detailed coverage information.
        """
        if not personas:
            return CoverageAnalysis(
                suggestions=["No personas to analyse"],
                overall_score=0.0,
            )

        # Extract themes from source data if not provided
        if themes is None and source_data:
            themes = self._extract_themes(source_data)
        elif themes is None:
            themes = self._extract_themes_from_personas(personas)

        # Analyse theme coverage
        theme_coverage = self._analyse_theme_coverage(personas, themes)

        # Analyse source utilisation
        source_utilisation = []
        persona_backing = {}
        if source_data:
            source_utilisation = self._analyse_source_utilisation(personas, source_data)
            persona_backing = self._build_persona_backing(personas, source_data)

        # Find gaps
        gaps = [t.theme for t in theme_coverage if t.coverage_percent == 0]

        # Find overlaps
        overlaps = self._find_overlaps(personas)

        # Generate suggestions
        suggestions = self._generate_suggestions(
            theme_coverage, source_utilisation, gaps, overlaps
        )

        # Calculate overall score
        overall_score = self._calculate_overall_score(theme_coverage)

        return CoverageAnalysis(
            theme_coverage=theme_coverage,
            source_utilisation=source_utilisation,
            persona_backing=persona_backing,
            gaps=gaps,
            overlaps=overlaps,
            suggestions=suggestions,
            overall_score=overall_score,
        )

    def _extract_themes(self, source_data: dict[str, str]) -> list[str]:
        """Extract themes from source data using word frequency."""
        all_text = " ".join(source_data.values()).lower()
        words = re.findall(r"\b[a-z]{4,}\b", all_text)

        # Count words, excluding stopwords
        word_counts = Counter(w for w in words if w not in self.STOPWORDS)

        # Get top themes
        themes = [
            word
            for word, count in word_counts.most_common(20)
            if count >= self.min_theme_mentions
        ]

        return themes[:10]

    def _extract_themes_from_personas(
        self,
        personas: list[dict[str, Any]],
    ) -> list[str]:
        """Extract themes from persona content."""
        themes = set()
        for persona in personas:
            # Extract from goals
            for goal in persona.get("goals", []):
                words = re.findall(r"\b[a-z]{4,}\b", goal.lower())
                themes.update(w for w in words if w not in self.STOPWORDS)

            # Extract from frustrations
            for frust in persona.get("frustrations", []):
                words = re.findall(r"\b[a-z]{4,}\b", frust.lower())
                themes.update(w for w in words if w not in self.STOPWORDS)

            # Extract from role
            role = persona.get("role", "")
            words = re.findall(r"\b[a-z]{4,}\b", role.lower())
            themes.update(w for w in words if w not in self.STOPWORDS)

        return list(themes)[:10]

    def _analyse_theme_coverage(
        self,
        personas: list[dict[str, Any]],
        themes: list[str],
    ) -> list[ThemeCoverage]:
        """Analyse how well themes are covered by personas."""
        coverage = []

        for theme in themes:
            matching_personas = []
            evidence_count = 0

            for persona in personas:
                # Check all text fields
                persona_text = " ".join(
                    [
                        persona.get("name", ""),
                        persona.get("role", ""),
                        " ".join(persona.get("goals", [])),
                        " ".join(persona.get("frustrations", [])),
                        persona.get("background", ""),
                    ]
                ).lower()

                if theme.lower() in persona_text:
                    matching_personas.append(persona.get("id", "unknown"))
                    evidence_count += persona_text.count(theme.lower())

            # Calculate coverage percentage
            coverage_percent = (len(matching_personas) / len(personas)) * 100

            coverage.append(
                ThemeCoverage(
                    theme=theme,
                    coverage_percent=coverage_percent,
                    persona_count=len(matching_personas),
                    persona_ids=matching_personas,
                    evidence_count=evidence_count,
                )
            )

        return coverage

    def _analyse_source_utilisation(
        self,
        personas: list[dict[str, Any]],
        source_data: dict[str, str],
    ) -> list[SourceUtilisation]:
        """Analyse how source data is utilised across personas."""
        utilisation = []

        for source, content in source_data.items():
            # Simple heuristic: check if source content themes appear in personas
            source_words = set(re.findall(r"\b[a-z]{4,}\b", content.lower()))
            source_words -= self.STOPWORDS

            matching_personas = []
            for persona in personas:
                persona_text = " ".join(
                    [
                        persona.get("name", ""),
                        persona.get("role", ""),
                        " ".join(persona.get("goals", [])),
                        " ".join(persona.get("frustrations", [])),
                    ]
                ).lower()
                persona_words = set(re.findall(r"\b[a-z]{4,}\b", persona_text))

                # Check overlap
                overlap = len(source_words & persona_words)
                if overlap >= 3:
                    matching_personas.append(persona.get("id", "unknown"))

            # Determine utilisation level
            if len(matching_personas) >= 3:
                level = "high"
            elif len(matching_personas) >= 1:
                level = "medium"
            else:
                level = "low"

            utilisation.append(
                SourceUtilisation(
                    source=source,
                    utilisation=level,
                    persona_count=len(matching_personas),
                    persona_ids=matching_personas,
                    token_count=len(content.split()),
                )
            )

        return utilisation

    def _build_persona_backing(
        self,
        personas: list[dict[str, Any]],
        source_data: dict[str, str],
    ) -> dict[str, list[str]]:
        """Build mapping of which sources back each persona."""
        backing = {}

        for persona in personas:
            persona_id = persona.get("id", "unknown")
            backing[persona_id] = []

            persona_text = " ".join(
                [
                    persona.get("name", ""),
                    persona.get("role", ""),
                    " ".join(persona.get("goals", [])),
                ]
            ).lower()
            persona_words = set(re.findall(r"\b[a-z]{4,}\b", persona_text))

            for source, content in source_data.items():
                source_words = set(re.findall(r"\b[a-z]{4,}\b", content.lower()))
                overlap = len(persona_words & source_words)
                if overlap >= 3:
                    backing[persona_id].append(source)

        return backing

    def _find_overlaps(
        self,
        personas: list[dict[str, Any]],
    ) -> list[tuple[str, str, float]]:
        """Find pairs of personas with high overlap."""
        overlaps = []

        for i, p1 in enumerate(personas):
            for p2 in personas[i + 1 :]:
                overlap = self._calculate_persona_overlap(p1, p2)
                if overlap >= 0.7:
                    overlaps.append(
                        (
                            p1.get("id", "unknown"),
                            p2.get("id", "unknown"),
                            overlap,
                        )
                    )

        return overlaps

    def _calculate_persona_overlap(
        self,
        p1: dict[str, Any],
        p2: dict[str, Any],
    ) -> float:
        """Calculate overlap between two personas."""
        # Compare goals
        goals1 = set(p1.get("goals", []))
        goals2 = set(p2.get("goals", []))
        goal_overlap = len(goals1 & goals2) / max(len(goals1 | goals2), 1)

        # Compare frustrations
        frust1 = set(p1.get("frustrations", []))
        frust2 = set(p2.get("frustrations", []))
        frust_overlap = len(frust1 & frust2) / max(len(frust1 | frust2), 1)

        # Compare role
        role_match = 1.0 if p1.get("role") == p2.get("role") else 0.0

        # Weighted average
        return (goal_overlap * 0.4) + (frust_overlap * 0.4) + (role_match * 0.2)

    def _generate_suggestions(
        self,
        theme_coverage: list[ThemeCoverage],
        source_utilisation: list[SourceUtilisation],
        gaps: list[str],
        overlaps: list[tuple[str, str, float]],
    ) -> list[str]:
        """Generate actionable suggestions."""
        suggestions = []

        # Suggest for gaps
        if gaps:
            suggestions.append(f"Add more data sources covering: {', '.join(gaps[:3])}")

        # Suggest for overlaps
        if overlaps:
            suggestions.append(
                f"Consider merging similar personas: {overlaps[0][0]} and {overlaps[0][1]}"
            )

        # Suggest for low utilisation
        low_util = [s for s in source_utilisation if s.utilisation == "low"]
        if low_util:
            suggestions.append(
                f"Source '{low_util[0].source}' is underrepresented - "
                "consider dedicated persona"
            )

        # Suggest for uneven coverage
        high_coverage = [t for t in theme_coverage if t.coverage_percent >= 80]
        low_coverage = [t for t in theme_coverage if 0 < t.coverage_percent < 50]
        if len(high_coverage) > 2 * len(low_coverage) and low_coverage:
            suggestions.append(
                f"Coverage is uneven - strengthen focus on: {low_coverage[0].theme}"
            )

        return suggestions

    def _calculate_overall_score(
        self,
        theme_coverage: list[ThemeCoverage],
    ) -> float:
        """Calculate overall coverage score."""
        if not theme_coverage:
            return 0.0

        total_coverage = sum(t.coverage_percent for t in theme_coverage)
        return total_coverage / len(theme_coverage)


def analyse_coverage(
    personas: list[dict[str, Any]],
    source_data: dict[str, str] | None = None,
    themes: list[str] | None = None,
) -> CoverageAnalysis:
    """Convenience function for coverage analysis.

    Args:
        personas: List of generated personas.
        source_data: Dict mapping source names to content.
        themes: Optional list of expected themes.

    Returns:
        CoverageAnalysis with detailed coverage information.
    """
    analyser = CoverageAnalyser()
    return analyser.analyse(personas, source_data, themes)
