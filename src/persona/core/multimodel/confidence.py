"""Confidence scoring for persona attributes (F-069).

Provides confidence levels (high/medium/low) for persona attributes
based on evidence strength from source data.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConfidenceLevel(Enum):
    """Confidence level for an attribute."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def description(self) -> str:
        """Human-readable description."""
        descriptions = {
            "high": "Strongly supported by multiple evidence sources",
            "medium": "Reasonably supported by single source or inference",
            "low": "Inferred or extrapolated from patterns",
        }
        return descriptions[self.value]


@dataclass
class AttributeConfidence:
    """Confidence information for a single attribute.

    Attributes:
        attribute: The attribute name.
        value: The attribute value.
        confidence: Confidence level (high/medium/low).
        evidence_count: Number of supporting evidence items.
        evidence_sources: List of sources providing evidence.
        reasoning: Human-readable reasoning for confidence level.
    """

    attribute: str
    value: Any
    confidence: ConfidenceLevel
    evidence_count: int = 0
    evidence_sources: list[str] = field(default_factory=list)
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "attribute": self.attribute,
            "value": self.value,
            "confidence": self.confidence.value,
            "evidence_count": self.evidence_count,
            "evidence_sources": self.evidence_sources,
            "reasoning": self.reasoning,
        }


@dataclass
class PersonaConfidence:
    """Confidence information for a complete persona.

    Attributes:
        persona_id: The persona identifier.
        overall_confidence: Aggregate confidence level.
        attribute_confidences: Confidence for each attribute.
        high_confidence_count: Number of high confidence attributes.
        medium_confidence_count: Number of medium confidence attributes.
        low_confidence_count: Number of low confidence attributes.
        confidence_score: Numeric score (0.0 to 1.0).
    """

    persona_id: str
    overall_confidence: ConfidenceLevel
    attribute_confidences: list[AttributeConfidence] = field(default_factory=list)
    high_confidence_count: int = 0
    medium_confidence_count: int = 0
    low_confidence_count: int = 0
    confidence_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_id": self.persona_id,
            "overall_confidence": self.overall_confidence.value,
            "attribute_confidences": [a.to_dict() for a in self.attribute_confidences],
            "high_confidence_count": self.high_confidence_count,
            "medium_confidence_count": self.medium_confidence_count,
            "low_confidence_count": self.low_confidence_count,
            "confidence_score": self.confidence_score,
        }

    def to_display(self) -> str:
        """Generate human-readable display."""
        lines = [
            f"Persona: {self.persona_id}",
            f"Overall Confidence: {self.overall_confidence.value.upper()}",
            f"Score: {self.confidence_score:.0%}",
            "",
            "Attribute Breakdown:",
        ]

        for attr in self.attribute_confidences:
            icon = {"high": "●", "medium": "◐", "low": "○"}[attr.confidence.value]
            lines.append(
                f"  {icon} {attr.attribute}: {attr.confidence.value} "
                f"({attr.evidence_count} sources)"
            )
            if attr.reasoning:
                lines.append(f"      └─ {attr.reasoning}")

        return "\n".join(lines)


class ConfidenceScorer:
    """Scorer for persona attribute confidence.

    Analyses persona attributes against source data to determine
    confidence levels based on evidence strength.

    Example:
        >>> scorer = ConfidenceScorer()
        >>> confidence = scorer.score_persona(
        ...     persona={"id": "1", "role": "Developer", ...},
        ...     source_data={"interview.md": "content..."}
        ... )
    """

    # Thresholds for confidence levels
    HIGH_THRESHOLD = 3  # Evidence count for high confidence
    MEDIUM_THRESHOLD = 1  # Evidence count for medium confidence

    # Key attributes to analyse
    KEY_ATTRIBUTES = [
        "role",
        "name",
        "goals",
        "frustrations",
        "background",
        "demographics",
        "behaviours",
        "needs",
        "pain_points",
    ]

    def __init__(
        self,
        high_threshold: int = 3,
        medium_threshold: int = 1,
    ):
        """Initialise the scorer.

        Args:
            high_threshold: Minimum evidence for high confidence.
            medium_threshold: Minimum evidence for medium confidence.
        """
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def score_persona(
        self,
        persona: dict[str, Any],
        source_data: dict[str, str] | None = None,
        evidence_map: dict[str, list[str]] | None = None,
    ) -> PersonaConfidence:
        """Score confidence for a single persona.

        Args:
            persona: The persona dictionary.
            source_data: Optional dict of source content.
            evidence_map: Optional pre-computed evidence mapping.

        Returns:
            PersonaConfidence with attribute-level scores.
        """
        persona_id = persona.get("id", "unknown")
        attribute_confidences = []

        for attr in self.KEY_ATTRIBUTES:
            if attr in persona:
                value = persona[attr]
                confidence = self._score_attribute(
                    attr, value, source_data, evidence_map
                )
                attribute_confidences.append(confidence)

        # Calculate counts
        high_count = sum(
            1 for a in attribute_confidences if a.confidence == ConfidenceLevel.HIGH
        )
        medium_count = sum(
            1 for a in attribute_confidences if a.confidence == ConfidenceLevel.MEDIUM
        )
        low_count = sum(
            1 for a in attribute_confidences if a.confidence == ConfidenceLevel.LOW
        )

        # Calculate overall confidence
        overall = self._calculate_overall(high_count, medium_count, low_count)

        # Calculate numeric score
        score = self._calculate_score(attribute_confidences)

        return PersonaConfidence(
            persona_id=persona_id,
            overall_confidence=overall,
            attribute_confidences=attribute_confidences,
            high_confidence_count=high_count,
            medium_confidence_count=medium_count,
            low_confidence_count=low_count,
            confidence_score=score,
        )

    def score_personas(
        self,
        personas: list[dict[str, Any]],
        source_data: dict[str, str] | None = None,
    ) -> list[PersonaConfidence]:
        """Score confidence for multiple personas.

        Args:
            personas: List of persona dictionaries.
            source_data: Optional dict of source content.

        Returns:
            List of PersonaConfidence objects.
        """
        return [self.score_persona(p, source_data) for p in personas]

    def _score_attribute(
        self,
        attribute: str,
        value: Any,
        source_data: dict[str, str] | None,
        evidence_map: dict[str, list[str]] | None,
    ) -> AttributeConfidence:
        """Score confidence for a single attribute."""
        # Use pre-computed evidence if available
        if evidence_map and attribute in evidence_map:
            sources = evidence_map[attribute]
            evidence_count = len(sources)
        elif source_data:
            # Search for evidence in source data
            sources, evidence_count = self._find_evidence(attribute, value, source_data)
        else:
            # No source data - assume medium confidence
            sources = []
            evidence_count = 1

        # Determine confidence level
        if evidence_count >= self.high_threshold:
            confidence = ConfidenceLevel.HIGH
            reasoning = f"Explicitly mentioned in {evidence_count} sources"
        elif evidence_count >= self.medium_threshold:
            confidence = ConfidenceLevel.MEDIUM
            reasoning = f"Mentioned in {evidence_count} source(s)"
        else:
            confidence = ConfidenceLevel.LOW
            reasoning = "Inferred from patterns, no direct evidence"

        return AttributeConfidence(
            attribute=attribute,
            value=value,
            confidence=confidence,
            evidence_count=evidence_count,
            evidence_sources=sources,
            reasoning=reasoning,
        )

    def _find_evidence(
        self,
        attribute: str,
        value: Any,
        source_data: dict[str, str],
    ) -> tuple[list[str], int]:
        """Find evidence for an attribute in source data."""
        sources = []
        evidence_count = 0

        # Convert value to searchable string
        if isinstance(value, list):
            search_terms = value
        else:
            search_terms = [str(value)]

        for source_name, content in source_data.items():
            content_lower = content.lower()
            for term in search_terms:
                if str(term).lower() in content_lower:
                    sources.append(source_name)
                    evidence_count += content_lower.count(str(term).lower())
                    break  # Count source once

        return sources, evidence_count

    def _calculate_overall(
        self,
        high_count: int,
        medium_count: int,
        low_count: int,
    ) -> ConfidenceLevel:
        """Calculate overall confidence from attribute counts."""
        total = high_count + medium_count + low_count
        if total == 0:
            return ConfidenceLevel.LOW

        # Weighted calculation
        score = (high_count * 1.0 + medium_count * 0.5 + low_count * 0.2) / total

        if score >= 0.7:
            return ConfidenceLevel.HIGH
        elif score >= 0.4:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _calculate_score(
        self,
        attribute_confidences: list[AttributeConfidence],
    ) -> float:
        """Calculate numeric confidence score (0.0 to 1.0)."""
        if not attribute_confidences:
            return 0.0

        weights = {
            ConfidenceLevel.HIGH: 1.0,
            ConfidenceLevel.MEDIUM: 0.5,
            ConfidenceLevel.LOW: 0.2,
        }

        total = sum(weights[a.confidence] for a in attribute_confidences)
        return total / len(attribute_confidences)


def score_confidence(
    persona: dict[str, Any],
    source_data: dict[str, str] | None = None,
) -> PersonaConfidence:
    """Convenience function for confidence scoring.

    Args:
        persona: The persona dictionary.
        source_data: Optional dict of source content.

    Returns:
        PersonaConfidence with attribute-level scores.
    """
    scorer = ConfidenceScorer()
    return scorer.score_persona(persona, source_data)


def add_confidence_to_persona(
    persona: dict[str, Any],
    source_data: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Add confidence information to a persona.

    Args:
        persona: The persona dictionary.
        source_data: Optional dict of source content.

    Returns:
        Persona dict with added confidence information.
    """
    confidence = score_confidence(persona, source_data)

    # Create enhanced persona
    enhanced = dict(persona)
    enhanced["confidence"] = {
        "overall": confidence.overall_confidence.value,
        "score": confidence.confidence_score,
        "attributes": {
            a.attribute: {
                "confidence": a.confidence.value,
                "evidence_count": a.evidence_count,
                "reasoning": a.reasoning,
            }
            for a in confidence.attribute_confidences
        },
    }

    return enhanced
