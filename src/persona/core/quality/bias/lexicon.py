"""
Lexicon-based bias detection using pattern matching.

This module provides the LexiconMatcher class that detects bias by matching
persona content against curated bias lexicons like HolisticBias.
"""

import json
import re
from pathlib import Path
from typing import Any

from persona.core.generation.parser import Persona
from persona.core.quality.bias.models import BiasCategory, BiasFinding, Severity


class LexiconMatcher:
    """
    Match persona content against bias lexicons.

    Uses pattern matching to identify stereotypical language and bias indicators
    from research-based lexicons.
    """

    def __init__(self, lexicon_name: str = "holisticbias") -> None:
        """
        Initialise the lexicon matcher.

        Args:
            lexicon_name: Name of the lexicon to load.
        """
        self.lexicon_name = lexicon_name
        self.lexicon = self._load_lexicon(lexicon_name)

    def _load_lexicon(self, name: str) -> dict[str, Any]:
        """
        Load lexicon from data directory.

        Args:
            name: Lexicon name (without .json extension).

        Returns:
            Loaded lexicon dictionary.
        """
        data_dir = Path(__file__).parent / "data"
        lexicon_path = data_dir / f"{name}.json"

        if not lexicon_path.exists():
            raise FileNotFoundError(f"Lexicon not found: {lexicon_path}")

        with open(lexicon_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _extract_persona_text(self, persona: Persona) -> dict[str, str]:
        """
        Extract all text content from persona.

        Args:
            persona: The persona to extract text from.

        Returns:
            Dictionary mapping field names to text content.
        """
        texts = {}

        # Demographics
        if hasattr(persona, "demographics") and persona.demographics:
            for key, value in persona.demographics.items():
                if isinstance(value, str):
                    texts[f"demographics.{key}"] = value
                elif value is not None:
                    texts[f"demographics.{key}"] = str(value)

        # Behaviours
        if hasattr(persona, "behaviours") and persona.behaviours:
            for i, behaviour in enumerate(persona.behaviours):
                texts[f"behaviours[{i}]"] = behaviour

        # Goals
        if hasattr(persona, "goals") and persona.goals:
            for i, goal in enumerate(persona.goals):
                texts[f"goals[{i}]"] = goal

        # Pain points
        if hasattr(persona, "pain_points") and persona.pain_points:
            for i, pain in enumerate(persona.pain_points):
                texts[f"pain_points[{i}]"] = pain

        # Quote
        if hasattr(persona, "quote") and persona.quote:
            texts["quote"] = persona.quote

        # Bio/description if present
        if hasattr(persona, "bio") and persona.bio:
            texts["bio"] = persona.bio

        return texts

    def _match_patterns(
        self,
        text: str,
        patterns: list[str],
        category: BiasCategory,
        severity: Severity,
    ) -> list[tuple[str, str, float]]:
        """
        Match patterns against text.

        Args:
            text: Text to search.
            patterns: Patterns to match.
            category: Bias category.
            severity: Severity level.

        Returns:
            List of (pattern, matched_text, confidence) tuples.
        """
        matches = []
        text_lower = text.lower()

        for pattern in patterns:
            pattern_lower = pattern.lower()

            # Case-insensitive substring match
            if pattern_lower in text_lower:
                # Extract surrounding context (up to 50 chars each side)
                start = max(0, text_lower.index(pattern_lower) - 50)
                end = min(
                    len(text),
                    text_lower.index(pattern_lower) + len(pattern_lower) + 50,
                )
                context = text[start:end].strip()

                # Higher confidence for exact phrase matches
                confidence = 0.9 if " " in pattern else 0.7
                matches.append((pattern, context, confidence))

        return matches

    def _determine_severity(
        self, pattern: str, category: BiasCategory, context: str
    ) -> Severity:
        """
        Determine severity of a bias finding.

        Args:
            pattern: The matched pattern.
            category: Bias category.
            context: Surrounding context.

        Returns:
            Severity level.
        """
        # High-severity patterns (harmful stereotypes)
        high_severity_patterns = {
            "hysterical",
            "irrational",
            "thug",
            "ghetto",
            "terrorist",
            "illegal",
            "primitive",
            "savage",
            "senile",
            "lazy",
            "entitled",
            "snowflake",
        }

        # Medium-severity patterns (clear stereotypes)
        medium_severity_patterns = {
            "emotional",
            "aggressive",
            "exotic",
            "articulate",
            "technophobic",
            "forgetful",
            "typical woman",
            "typical man",
        }

        pattern_lower = pattern.lower()

        if any(p in pattern_lower for p in high_severity_patterns):
            return Severity.HIGH
        elif any(p in pattern_lower for p in medium_severity_patterns):
            return Severity.MEDIUM
        else:
            return Severity.LOW

    def analyse_gender(
        self, texts: dict[str, str], categories: list[str]
    ) -> list[BiasFinding]:
        """
        Analyse for gender bias.

        Args:
            texts: Persona text fields.
            categories: Categories to check.

        Returns:
            List of gender bias findings.
        """
        if "gender" not in categories:
            return []

        findings = []
        gender_data = self.lexicon.get("gender", {})

        all_patterns = (
            gender_data.get("female_stereotypes", [])
            + gender_data.get("male_stereotypes", [])
            + gender_data.get("patterns", [])
        )

        for field, text in texts.items():
            matches = self._match_patterns(
                text, all_patterns, BiasCategory.GENDER, Severity.MEDIUM
            )

            for pattern, context, confidence in matches:
                severity = self._determine_severity(
                    pattern, BiasCategory.GENDER, context
                )
                findings.append(
                    BiasFinding(
                        category=BiasCategory.GENDER,
                        description=f"Gender stereotype detected: '{pattern}'",
                        evidence=context,
                        severity=severity,
                        method="lexicon",
                        confidence=confidence,
                        context=field,
                    )
                )

        return findings

    def analyse_racial(
        self, texts: dict[str, str], categories: list[str]
    ) -> list[BiasFinding]:
        """
        Analyse for racial bias.

        Args:
            texts: Persona text fields.
            categories: Categories to check.

        Returns:
            List of racial bias findings.
        """
        if "racial" not in categories:
            return []

        findings = []
        racial_data = self.lexicon.get("racial", {})

        all_patterns = racial_data.get("patterns", []) + racial_data.get(
            "descriptors", []
        )

        for field, text in texts.items():
            matches = self._match_patterns(
                text, all_patterns, BiasCategory.RACIAL, Severity.MEDIUM
            )

            for pattern, context, confidence in matches:
                severity = self._determine_severity(
                    pattern, BiasCategory.RACIAL, context
                )
                findings.append(
                    BiasFinding(
                        category=BiasCategory.RACIAL,
                        description=f"Racial stereotype detected: '{pattern}'",
                        evidence=context,
                        severity=severity,
                        method="lexicon",
                        confidence=confidence,
                        context=field,
                    )
                )

        return findings

    def analyse_age(
        self, texts: dict[str, str], categories: list[str]
    ) -> list[BiasFinding]:
        """
        Analyse for age bias.

        Args:
            texts: Persona text fields.
            categories: Categories to check.

        Returns:
            List of age bias findings.
        """
        if "age" not in categories:
            return []

        findings = []
        age_data = self.lexicon.get("age", {})

        all_patterns = (
            age_data.get("young_stereotypes", [])
            + age_data.get("old_stereotypes", [])
            + age_data.get("patterns", [])
        )

        for field, text in texts.items():
            matches = self._match_patterns(
                text, all_patterns, BiasCategory.AGE, Severity.MEDIUM
            )

            for pattern, context, confidence in matches:
                severity = self._determine_severity(pattern, BiasCategory.AGE, context)
                findings.append(
                    BiasFinding(
                        category=BiasCategory.AGE,
                        description=f"Age stereotype detected: '{pattern}'",
                        evidence=context,
                        severity=severity,
                        method="lexicon",
                        confidence=confidence,
                        context=field,
                    )
                )

        return findings

    def analyse_professional(
        self, texts: dict[str, str], categories: list[str]
    ) -> list[BiasFinding]:
        """
        Analyse for professional bias.

        Args:
            texts: Persona text fields.
            categories: Categories to check.

        Returns:
            List of professional bias findings.
        """
        if "professional" not in categories:
            return []

        findings = []
        professional_data = self.lexicon.get("professional", {})

        patterns = professional_data.get("patterns", [])

        for field, text in texts.items():
            matches = self._match_patterns(
                text, patterns, BiasCategory.PROFESSIONAL, Severity.MEDIUM
            )

            for pattern, context, confidence in matches:
                severity = self._determine_severity(
                    pattern, BiasCategory.PROFESSIONAL, context
                )
                findings.append(
                    BiasFinding(
                        category=BiasCategory.PROFESSIONAL,
                        description=f"Professional stereotype detected: '{pattern}'",
                        evidence=context,
                        severity=severity,
                        method="lexicon",
                        confidence=confidence,
                        context=field,
                    )
                )

        return findings

    def analyse(self, persona: Persona, categories: list[str]) -> list[BiasFinding]:
        """
        Analyse persona for bias across all requested categories.

        Args:
            persona: The persona to analyse.
            categories: List of bias categories to check.

        Returns:
            List of all detected bias findings.
        """
        # Extract text from persona
        texts = self._extract_persona_text(persona)

        # Collect findings from all categories
        findings = []
        findings.extend(self.analyse_gender(texts, categories))
        findings.extend(self.analyse_racial(texts, categories))
        findings.extend(self.analyse_age(texts, categories))
        findings.extend(self.analyse_professional(texts, categories))

        return findings
