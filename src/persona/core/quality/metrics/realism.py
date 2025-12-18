"""
Realism metric for persona quality scoring.

Evaluates the plausibility of a persona, checking for
realistic names, coherent demographics, authentic quotes,
and specific goals.
"""

import re
from typing import TYPE_CHECKING, Any

from persona.core.generation.parser import Persona
from persona.core.quality.base import QualityMetric
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class RealismMetric(QualityMetric):
    """
    Evaluate the plausibility of a persona.

    Scoring breakdown:
    - Name plausibility: 25%
    - Demographic coherence: 25%
    - Quote authenticity: 25%
    - Goal specificity: 25%
    """

    # Generic/placeholder names to flag
    GENERIC_NAMES: set[str] = {
        "user",
        "persona",
        "customer",
        "person",
        "test",
        "example",
        "john doe",
        "jane doe",
        "placeholder",
        "user 1",
        "user 2",
        "persona 1",
        "persona 2",
        "sample",
        "demo",
        "test user",
        "default",
    }

    # Artificial-sounding quote patterns
    ARTIFICIAL_QUOTE_PATTERNS: list[str] = [
        r"^I (always|never|absolutely|definitely) ",
        r"\b(synergy|leverage|optimise|optimize|streamline|holistic)\b",
        r"^(As a|Being a|In my role as|In my capacity as)",
        r"^(I believe that|I think that|I feel that) (it is important|we should)",
    ]

    # Generic goal patterns
    GENERIC_GOAL_PATTERNS: list[str] = [
        r"^(be|become|get) (better|successful|happy|efficient)$",
        r"^improve (things|everything|myself|my life)$",
        r"^have a (good|better|nice|great) ",
        r"^(do|make) (more|less|better)$",
    ]

    @property
    def name(self) -> str:
        """Return the metric name."""
        return "realism"

    @property
    def description(self) -> str:
        """Return metric description."""
        return "Evaluate plausibility as a real person"

    @property
    def requires_source_data(self) -> bool:
        """This metric does not require source data."""
        return False

    @property
    def requires_other_personas(self) -> bool:
        """This metric does not require other personas."""
        return False

    @property
    def requires_evidence_report(self) -> bool:
        """This metric does not require evidence report."""
        return False

    def evaluate(
        self,
        persona: Persona,
        source_data: str | None = None,
        other_personas: list[Persona] | None = None,
        evidence_report: "EvidenceReport | None" = None,
    ) -> DimensionScore:
        """
        Calculate realism score for a persona.

        Args:
            persona: The persona to evaluate.

        Returns:
            DimensionScore with realism assessment.
        """
        issues: list[str] = []
        details: dict[str, Any] = {}

        # Name plausibility (25%)
        name_score = self._check_name_plausibility(persona, issues, details)

        # Demographic coherence (25%)
        demo_score = self._check_demographic_coherence(persona, issues, details)

        # Quote authenticity (25%)
        quote_score = self._check_quote_authenticity(persona, issues, details)

        # Goal specificity (25%)
        goal_score = self._check_goal_specificity(persona, issues, details)

        overall = (name_score + demo_score + quote_score + goal_score) / 4

        return DimensionScore(
            dimension="realism",
            score=overall,
            weight=self.config.weights["realism"],
            issues=issues,
            details=details,
        )

    def _check_name_plausibility(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check if name seems like a real person's name."""
        if not persona.name:
            issues.append("Missing name")
            details["name_type"] = "missing"
            return 0.0

        name = persona.name.strip()
        name_lower = name.lower()

        # Check for generic names
        if name_lower in self.GENERIC_NAMES:
            issues.append(f"Generic placeholder name: '{name}'")
            details["name_type"] = "generic"
            return 30.0

        # Check for reasonable name structure
        name_parts = name.split()

        if len(name_parts) < 2:
            issues.append("Name appears incomplete (single word)")
            details["name_type"] = "incomplete"
            return 60.0

        # Check for numbers or special characters
        if re.search(r"[0-9@#$%^&*()+=\[\]{}|\\/<>]", name):
            issues.append("Name contains unusual characters")
            details["name_type"] = "unusual_chars"
            return 40.0

        # Check for all caps or all lowercase
        if name.isupper() or name.islower():
            issues.append("Name has unusual capitalisation")
            details["name_type"] = "unusual_case"
            return 70.0

        details["name_type"] = "realistic"
        return 100.0

    def _check_demographic_coherence(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check if demographics form a coherent picture."""
        if not persona.demographics:
            details["demographics_present"] = False
            return 50.0  # Neutral if missing

        details["demographics_present"] = True
        coherence_issues: list[str] = []

        # Check age-occupation coherence
        age = persona.demographics.get("age") or persona.demographics.get("age_range")
        occupation = (
            persona.demographics.get("occupation")
            or persona.demographics.get("role")
            or persona.demographics.get("job")
        )

        if age and occupation:
            age_str = str(age).lower()
            occ_str = str(occupation).lower()

            # Flag unrealistic age-occupation combinations
            young_ages = ["16", "17", "18", "19", "20", "21"]
            senior_roles = [
                "ceo",
                "chief",
                "director",
                "vp",
                "vice president",
                "president",
                "managing director",
                "founder",
            ]

            if any(a in age_str for a in young_ages):
                if any(role in occ_str for role in senior_roles):
                    coherence_issues.append(
                        f"Age-occupation mismatch: {age} year old as {occupation}"
                    )

        # Check for placeholder demographics
        for key, value in persona.demographics.items():
            val_str = str(value).lower()
            if val_str in ["n/a", "na", "unknown", "tbd", "xxx", "placeholder"]:
                coherence_issues.append(f"Placeholder value in {key}: '{value}'")

        details["coherence_issues"] = coherence_issues
        issues.extend(coherence_issues)

        return max(0, 100 - (len(coherence_issues) * 25))

    def _check_quote_authenticity(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check if quotes sound like real speech."""
        if not persona.quotes:
            details["quotes_present"] = False
            return 50.0  # Neutral if missing

        details["quotes_present"] = True
        authentic_count = 0
        total = len(persona.quotes)
        artificial_quotes: list[str] = []

        for quote in persona.quotes:
            is_authentic, reason = self._is_authentic_quote(quote)
            if is_authentic:
                authentic_count += 1
            else:
                artificial_quotes.append(f"'{quote[:50]}...' ({reason})")

        # Only report first few artificial quotes
        if artificial_quotes:
            for artificial in artificial_quotes[:2]:
                issues.append(f"Quote seems artificial: {artificial}")

        details["authentic_quote_ratio"] = round(
            authentic_count / total if total > 0 else 0, 2
        )
        details["artificial_quote_count"] = len(artificial_quotes)

        return (authentic_count / total) * 100 if total > 0 else 50.0

    def _is_authentic_quote(self, quote: str) -> tuple[bool, str]:
        """
        Check if a quote sounds like real speech.

        Returns:
            Tuple of (is_authentic, reason_if_not).
        """
        # Check for artificial patterns
        for pattern in self.ARTIFICIAL_QUOTE_PATTERNS:
            if re.search(pattern, quote, re.IGNORECASE):
                return False, "corporate jargon"

        # Check for reasonable length (too short or too long is suspicious)
        word_count = len(quote.split())
        if word_count < 3:
            return False, "too short"
        if word_count > 60:
            return False, "too long"

        # Check for natural speech markers (contractions, fillers)
        natural_markers = [
            "I'm",
            "I've",
            "I'd",
            "don't",
            "can't",
            "won't",
            "it's",
            "that's",
            "there's",
            "we're",
            "they're",
            "...",
            "actually",
            "really",
            "just",
            "like",
        ]
        has_natural_marker = any(
            marker.lower() in quote.lower() for marker in natural_markers
        )

        # Quotes with natural markers are more authentic
        # But lack of markers doesn't mean artificial
        return True, ""

    def _check_goal_specificity(
        self,
        persona: Persona,
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Check if goals are specific rather than generic."""
        if not persona.goals:
            details["goals_present"] = False
            return 50.0

        details["goals_present"] = True
        specific_count = 0
        total = len(persona.goals)
        generic_goals: list[str] = []

        for goal in persona.goals:
            is_specific, reason = self._is_specific_goal(goal)
            if is_specific:
                specific_count += 1
            else:
                generic_goals.append(f"'{goal}' ({reason})")

        # Only report first few generic goals
        if generic_goals:
            for generic in generic_goals[:2]:
                issues.append(f"Goal too generic: {generic}")

        details["specific_goal_ratio"] = round(
            specific_count / total if total > 0 else 0, 2
        )
        details["generic_goal_count"] = len(generic_goals)

        return (specific_count / total) * 100 if total > 0 else 50.0

    def _is_specific_goal(self, goal: str) -> tuple[bool, str]:
        """
        Check if a goal is specific rather than generic.

        Returns:
            Tuple of (is_specific, reason_if_not).
        """
        goal_lower = goal.lower().strip()

        # Check for generic patterns
        for pattern in self.GENERIC_GOAL_PATTERNS:
            if re.match(pattern, goal_lower):
                return False, "matches generic pattern"

        # Check for sufficient detail (word count)
        word_count = len(goal.split())
        if word_count < 4:
            return False, "too brief"

        # Check for concrete nouns/verbs (not just abstract concepts)
        abstract_only = ["want", "need", "hope", "wish", "try", "better", "more"]
        words = set(goal_lower.split())
        if words.issubset(set(abstract_only) | {"to", "a", "the", "and", "or", "be"}):
            return False, "too abstract"

        return True, ""
