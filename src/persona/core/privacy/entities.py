"""
Data models for PII detection and anonymisation.

This module defines the core data structures used by the privacy module
to represent detected PII entities and anonymisation results.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class AnonymisationStrategy(str, Enum):
    """Anonymisation strategy for PII."""

    REDACT = "redact"
    REPLACE = "replace"
    HASH = "hash"


class PIIType(str, Enum):
    """Supported PII entity types."""

    PERSON = "PERSON"
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    PHONE_NUMBER = "PHONE_NUMBER"
    LOCATION = "LOCATION"
    DATE_TIME = "DATE_TIME"
    CREDIT_CARD = "CREDIT_CARD"
    IP_ADDRESS = "IP_ADDRESS"
    IBAN_CODE = "IBAN_CODE"
    NRP = "NRP"  # National Registry Number (SSN equivalent)
    MEDICAL_LICENSE = "MEDICAL_LICENSE"
    URL = "URL"
    US_SSN = "US_SSN"
    UK_NHS = "UK_NHS"
    # Additional common types
    ADDRESS = "LOCATION"  # Alias for LOCATION
    SSN = "US_SSN"  # Alias for US_SSN
    DATE_OF_BIRTH = "DATE_TIME"  # Alias for DATE_TIME


@dataclass
class PIIEntity:
    """
    Represents a detected PII entity.

    Attributes:
        type: Type of PII detected (e.g., PERSON, EMAIL_ADDRESS).
        text: The actual text that was detected.
        start: Start position in the original text.
        end: End position in the original text.
        score: Confidence score (0.0 to 1.0).
        metadata: Additional metadata from the detector.
    """

    type: str
    text: str
    start: int
    end: int
    score: float = 1.0
    metadata: dict[str, Any] | None = None

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"PIIEntity(type='{self.type}', text='{self.text}', "
            f"start={self.start}, end={self.end}, score={self.score:.2f})"
        )


@dataclass
class AnonymisationResult:
    """
    Result of anonymising text.

    Attributes:
        text: The anonymised text.
        entities: List of entities that were anonymised.
        strategy: Strategy used for anonymisation.
        original_length: Length of original text.
        anonymised_length: Length of anonymised text.
    """

    text: str
    entities: list[PIIEntity]
    strategy: AnonymisationStrategy
    original_length: int
    anonymised_length: int

    @property
    def entity_count(self) -> int:
        """Return number of entities anonymised."""
        return len(self.entities)

    @property
    def entity_types(self) -> set[str]:
        """Return unique entity types found."""
        return {entity.type for entity in self.entities}

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"AnonymisationResult(entities={self.entity_count}, "
            f"strategy={self.strategy.value}, "
            f"length={self.original_length}->{self.anonymised_length})"
        )
