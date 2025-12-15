"""
Privacy module for PII detection and anonymisation.

This module provides functionality to detect and anonymise personally
identifiable information (PII) in research data before sending to LLM providers.

Uses Microsoft Presidio for detection and anonymisation. Install with:
    pip install persona[privacy]

After installation, download the spaCy model:
    python -m spacy download en_core_web_lg

Example:
    from persona.core.privacy import PIIDetector, PIIAnonymiser, AnonymisationStrategy

    # Detect PII
    detector = PIIDetector()
    entities = detector.detect("Contact John Smith at john@example.com")

    # Anonymise with different strategies
    anonymiser = PIIAnonymiser()
    result = anonymiser.anonymise(text, entities, AnonymisationStrategy.REDACT)
    # "Contact [PERSON] at [EMAIL_ADDRESS]"
"""

from persona.core.privacy.anonymiser import PIIAnonymiser
from persona.core.privacy.detector import PIIDetector
from persona.core.privacy.entities import (
    AnonymisationResult,
    AnonymisationStrategy,
    PIIEntity,
    PIIType,
)

__all__ = [
    "PIIDetector",
    "PIIAnonymiser",
    "PIIEntity",
    "PIIType",
    "AnonymisationStrategy",
    "AnonymisationResult",
]
