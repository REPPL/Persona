"""
Data models for faithfulness and hallucination detection.

This module defines the core data structures for representing claims,
source matches, and faithfulness assessment results.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ClaimType(Enum):
    """Types of claims that can be extracted from personas."""

    FACTUAL = "factual"  # Verifiable fact (age, occupation, location)
    OPINION = "opinion"  # Stated opinion or belief
    PREFERENCE = "preference"  # Likes, dislikes, preferences
    BEHAVIOUR = "behaviour"  # Reported behaviour or habit
    QUOTE = "quote"  # Direct quote from source
    DEMOGRAPHIC = "demographic"  # Demographic information
    GOAL = "goal"  # Stated goal or objective
    PAIN_POINT = "pain_point"  # Stated problem or frustration


@dataclass
class Claim:
    """
    A single factual claim extracted from a persona.

    Attributes:
        text: The claim text (concise statement).
        source_field: Which persona field this came from (e.g., 'demographics.age').
        claim_type: Type of claim for categorisation.
        context: Additional context from the persona.
    """

    text: str
    source_field: str
    claim_type: ClaimType
    context: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "text": self.text,
            "source_field": self.source_field,
            "claim_type": self.claim_type.value,
            "context": self.context,
        }


@dataclass
class SourceMatch:
    """
    Match between a claim and source data.

    Attributes:
        claim: The claim being evaluated.
        source_text: Most similar passage from source data.
        similarity_score: Semantic similarity (0-1).
        is_supported: Whether the claim is supported by source.
        evidence_type: Type of evidence (direct, inferred, unsupported).
    """

    claim: Claim
    source_text: str
    similarity_score: float
    is_supported: bool
    evidence_type: str = "inferred"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "claim": self.claim.to_dict(),
            "source_text": self.source_text,
            "similarity_score": round(self.similarity_score, 3),
            "is_supported": self.is_supported,
            "evidence_type": self.evidence_type,
        }


@dataclass
class FaithfulnessReport:
    """
    Complete faithfulness assessment for a persona.

    Attributes:
        persona_id: ID of the evaluated persona.
        persona_name: Name of the evaluated persona.
        claims: All extracted claims.
        matches: Claim-source matches.
        supported_ratio: Ratio of supported claims (0-1).
        hallucination_ratio: Ratio of unsupported claims (0-1).
        unsupported_claims: Claims without source support.
        details: Additional assessment details.
    """

    persona_id: str
    persona_name: str
    claims: list[Claim]
    matches: list[SourceMatch]
    supported_ratio: float
    hallucination_ratio: float
    unsupported_claims: list[Claim] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def total_claims(self) -> int:
        """Get total number of claims."""
        return len(self.claims)

    @property
    def supported_count(self) -> int:
        """Get count of supported claims."""
        return sum(1 for m in self.matches if m.is_supported)

    @property
    def unsupported_count(self) -> int:
        """Get count of unsupported claims."""
        return len(self.unsupported_claims)

    @property
    def faithfulness_score(self) -> float:
        """
        Calculate faithfulness score (0-100).

        This is the percentage of claims supported by source data.
        """
        return self.supported_ratio * 100

    def get_claims_by_type(self, claim_type: ClaimType) -> list[Claim]:
        """Get all claims of a specific type."""
        return [c for c in self.claims if c.claim_type == claim_type]

    def get_unsupported_by_type(self, claim_type: ClaimType) -> list[Claim]:
        """Get unsupported claims of a specific type."""
        return [c for c in self.unsupported_claims if c.claim_type == claim_type]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "total_claims": self.total_claims,
            "supported_count": self.supported_count,
            "unsupported_count": self.unsupported_count,
            "supported_ratio": round(self.supported_ratio, 3),
            "hallucination_ratio": round(self.hallucination_ratio, 3),
            "faithfulness_score": round(self.faithfulness_score, 2),
            "claims": [c.to_dict() for c in self.claims],
            "matches": [m.to_dict() for m in self.matches],
            "unsupported_claims": [c.to_dict() for c in self.unsupported_claims],
            "details": self.details,
        }
