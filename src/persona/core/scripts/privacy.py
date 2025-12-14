"""
Privacy audit for conversation scripts.

This module provides privacy auditing to ensure conversation scripts
don't leak source data. Output is BLOCKED if leakage exceeds threshold.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import re

from persona.core.generation.parser import Persona
from persona.core.scripts.models import CharacterCard


class LeakageType(Enum):
    """Types of potential data leakage."""

    DIRECT_QUOTE = "direct_quote"
    PARAPHRASE = "paraphrase"
    SPECIFIC_DETAIL = "specific_detail"
    IDENTIFIER = "identifier"


@dataclass
class LeakageInstance:
    """A detected instance of potential leakage."""

    type: LeakageType
    content: str
    source: str
    similarity: float
    severity: str = "medium"  # low, medium, high


@dataclass
class PrivacyConfig:
    """Configuration for privacy auditing."""

    max_leakage_score: float = 0.1
    check_direct_quotes: bool = True
    check_paraphrases: bool = True
    check_specific_details: bool = True
    check_identifiers: bool = True
    min_similarity_threshold: float = 0.7


@dataclass
class PrivacyAuditResult:
    """Result of a privacy audit."""

    passed: bool
    leakage_score: float
    leakages: list[LeakageInstance] = field(default_factory=list)
    details: str = ""

    @property
    def blocked(self) -> bool:
        """Whether output should be blocked."""
        return not self.passed


class PrivacyAuditor:
    """
    Audit conversation scripts for privacy leakage.

    Checks that generated scripts don't expose source data
    through direct quotes, paraphrases, or specific details.

    CRITICAL: Output is BLOCKED if leakage_score > config.max_leakage_score

    Example:
        auditor = PrivacyAuditor()
        result = auditor.audit(character_card, source_persona)
        if result.blocked:
            raise PrivacyLeakageError(result.details)
    """

    def __init__(self, config: PrivacyConfig | None = None) -> None:
        """
        Initialise privacy auditor.

        Args:
            config: Privacy configuration.
        """
        self._config = config or PrivacyConfig()

    def audit(
        self,
        card: CharacterCard,
        source_persona: Persona,
    ) -> PrivacyAuditResult:
        """
        Audit a character card for privacy leakage.

        Args:
            card: The character card to audit.
            source_persona: The source persona used to generate it.

        Returns:
            PrivacyAuditResult with leakage analysis.
        """
        leakages: list[LeakageInstance] = []

        # Get source quotes
        source_quotes = source_persona.quotes or []

        # Get card content to check
        card_content = self._extract_card_content(card)

        # Check direct quotes
        if self._config.check_direct_quotes:
            direct_leakages = self._check_direct_quotes(card_content, source_quotes)
            leakages.extend(direct_leakages)

        # Check paraphrases
        if self._config.check_paraphrases:
            paraphrase_leakages = self._check_paraphrases(card_content, source_quotes)
            leakages.extend(paraphrase_leakages)

        # Check specific details
        if self._config.check_specific_details:
            detail_leakages = self._check_specific_details(card_content, source_persona)
            leakages.extend(detail_leakages)

        # Check identifiers
        if self._config.check_identifiers:
            id_leakages = self._check_identifiers(card_content, source_persona)
            leakages.extend(id_leakages)

        # Calculate leakage score
        leakage_score = self._calculate_leakage_score(leakages)

        # Determine if passed
        passed = leakage_score <= self._config.max_leakage_score

        # Build details
        details = self._build_details(passed, leakage_score, leakages)

        return PrivacyAuditResult(
            passed=passed,
            leakage_score=leakage_score,
            leakages=leakages,
            details=details,
        )

    def _extract_card_content(self, card: CharacterCard) -> str:
        """Extract all text content from a character card."""
        parts = []

        # Identity
        parts.append(card.identity.title)
        parts.append(card.identity.demographics_summary)

        # Profile
        parts.extend(card.psychological_profile.goals)
        parts.extend(card.psychological_profile.motivations)
        parts.extend(card.psychological_profile.pain_points)
        parts.extend(card.psychological_profile.personality_traits)
        parts.extend(card.psychological_profile.flaws)

        # Communication
        parts.append(card.communication_style.tone)
        parts.extend(card.communication_style.speech_patterns)

        # Knowledge
        parts.extend(card.knowledge_boundaries.knows)
        parts.extend(card.knowledge_boundaries.can_infer)

        return " ".join(parts)

    def _check_direct_quotes(
        self,
        content: str,
        source_quotes: list[str],
    ) -> list[LeakageInstance]:
        """Check for direct quote matches."""
        leakages = []
        content_lower = content.lower()

        for quote in source_quotes:
            quote_lower = quote.lower()
            # Check for exact match
            if quote_lower in content_lower:
                leakages.append(
                    LeakageInstance(
                        type=LeakageType.DIRECT_QUOTE,
                        content=quote,
                        source="quotes",
                        similarity=1.0,
                        severity="high",
                    )
                )
            # Check for partial match (3+ word phrases)
            else:
                words = quote_lower.split()
                if len(words) >= 3:
                    # Check for 3-word subsequences
                    for i in range(len(words) - 2):
                        phrase = " ".join(words[i : i + 3])
                        if phrase in content_lower:
                            leakages.append(
                                LeakageInstance(
                                    type=LeakageType.DIRECT_QUOTE,
                                    content=phrase,
                                    source="quotes",
                                    similarity=0.8,
                                    severity="medium",
                                )
                            )
                            break  # Only flag once per quote

        return leakages

    def _check_paraphrases(
        self,
        content: str,
        source_quotes: list[str],
    ) -> list[LeakageInstance]:
        """Check for potential paraphrases using simple heuristics."""
        leakages = []

        for quote in source_quotes:
            # Simple word overlap check
            quote_words = set(self._extract_significant_words(quote))
            content_words = set(self._extract_significant_words(content))

            if len(quote_words) >= 3:
                overlap = quote_words & content_words
                similarity = len(overlap) / len(quote_words)

                if similarity >= self._config.min_similarity_threshold:
                    leakages.append(
                        LeakageInstance(
                            type=LeakageType.PARAPHRASE,
                            content=f"High word overlap: {overlap}",
                            source="quotes",
                            similarity=similarity,
                            severity="medium",
                        )
                    )

        return leakages

    def _check_specific_details(
        self,
        content: str,
        source_persona: Persona,
    ) -> list[LeakageInstance]:
        """Check for specific details that might identify the source."""
        leakages = []
        content_lower = content.lower()

        # Check for specific demographic values
        if source_persona.demographics:
            for key, value in source_persona.demographics.items():
                if key in ["age", "location", "company"]:
                    value_str = str(value).lower()
                    if len(value_str) > 3 and value_str in content_lower:
                        leakages.append(
                            LeakageInstance(
                                type=LeakageType.SPECIFIC_DETAIL,
                                content=f"{key}: {value}",
                                source="demographics",
                                similarity=1.0,
                                severity="medium",
                            )
                        )

        return leakages

    def _check_identifiers(
        self,
        content: str,
        source_persona: Persona,
    ) -> list[LeakageInstance]:
        """Check for identifiers that could trace back to source."""
        leakages = []
        content_lower = content.lower()

        # Check for persona ID
        if source_persona.id.lower() in content_lower:
            leakages.append(
                LeakageInstance(
                    type=LeakageType.IDENTIFIER,
                    content=source_persona.id,
                    source="persona_id",
                    similarity=1.0,
                    severity="high",
                )
            )

        # Check for email patterns (if any)
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if re.search(email_pattern, content):
            leakages.append(
                LeakageInstance(
                    type=LeakageType.IDENTIFIER,
                    content="Email address found",
                    source="content",
                    similarity=1.0,
                    severity="high",
                )
            )

        return leakages

    def _extract_significant_words(self, text: str) -> list[str]:
        """Extract significant words (excluding stopwords)."""
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "i", "you", "he", "she", "it", "we", "they", "me", "him",
            "her", "us", "them", "my", "your", "his", "its", "our",
            "their", "this", "that", "these", "those", "and", "or",
            "but", "if", "then", "else", "when", "where", "why", "how",
            "all", "each", "every", "both", "few", "more", "most",
            "other", "some", "such", "no", "not", "only", "same", "so",
            "than", "too", "very", "just", "can", "with", "from", "to",
            "of", "for", "on", "in", "at", "by", "as", "into",
        }

        words = re.findall(r"\b[a-z]+\b", text.lower())
        return [w for w in words if w not in stopwords and len(w) > 2]

    def _calculate_leakage_score(self, leakages: list[LeakageInstance]) -> float:
        """Calculate overall leakage score."""
        if not leakages:
            return 0.0

        # Weight by severity
        severity_weights = {"high": 0.5, "medium": 0.2, "low": 0.1}

        total_score = 0.0
        for leakage in leakages:
            weight = severity_weights.get(leakage.severity, 0.1)
            total_score += leakage.similarity * weight

        # Cap at 1.0
        return min(total_score, 1.0)

    def _build_details(
        self,
        passed: bool,
        score: float,
        leakages: list[LeakageInstance],
    ) -> str:
        """Build human-readable audit details."""
        lines = []

        if passed:
            lines.append("Privacy audit PASSED")
        else:
            lines.append("Privacy audit FAILED - Output BLOCKED")

        lines.append(f"Leakage score: {score:.3f} (threshold: {self._config.max_leakage_score})")

        if leakages:
            lines.append(f"Detected {len(leakages)} potential leakages:")
            for i, leak in enumerate(leakages[:5], 1):  # Show first 5
                lines.append(f"  {i}. [{leak.type.value}] {leak.content[:50]}...")

        return "\n".join(lines)


class PrivacyLeakageError(Exception):
    """Raised when privacy audit fails and output is blocked."""

    def __init__(self, audit_result: PrivacyAuditResult) -> None:
        """
        Initialise error with audit result.

        Args:
            audit_result: The failed audit result.
        """
        self.audit_result = audit_result
        super().__init__(audit_result.details)
