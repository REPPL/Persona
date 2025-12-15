"""
PII anonymisation strategies.

This module provides anonymisation functionality for detected PII using
various strategies (redact, replace, hash).
"""

import hashlib
from typing import Any

from persona.core.privacy.entities import (
    AnonymisationResult,
    AnonymisationStrategy,
    PIIEntity,
)


class PIIAnonymiser:
    """
    Anonymises PII in text using various strategies.

    Supports three strategies:
    - REDACT: Replace PII with [TYPE] placeholder
    - REPLACE: Replace PII with fake but realistic data
    - HASH: Replace PII with a deterministic hash

    Example:
        anonymiser = PIIAnonymiser()
        result = anonymiser.anonymise(
            text="Contact John at john@example.com",
            entities=[...],
            strategy=AnonymisationStrategy.REDACT
        )
        # "Contact [PERSON] at [EMAIL_ADDRESS]"
    """

    def __init__(self) -> None:
        """Initialise anonymiser."""
        self._anonymizer = None
        self._available = False
        self._import_error = None

        # Try to import presidio-anonymizer
        try:
            from presidio_anonymizer import AnonymizerEngine

            self._anonymizer = AnonymizerEngine()
            self._available = True
        except ImportError as e:
            self._import_error = e

    def is_available(self) -> bool:
        """
        Check if anonymisation is available.

        Returns:
            True if Presidio anonymizer is installed, False otherwise.
        """
        return self._available

    def get_import_error(self) -> ImportError | None:
        """
        Get the import error if anonymisation is not available.

        Returns:
            ImportError if Presidio is not installed, None otherwise.
        """
        return self._import_error

    def anonymise(
        self,
        text: str,
        entities: list[PIIEntity],
        strategy: AnonymisationStrategy = AnonymisationStrategy.REDACT,
    ) -> AnonymisationResult:
        """
        Anonymise text based on detected entities.

        Args:
            text: Original text.
            entities: List of detected PII entities.
            strategy: Anonymisation strategy to use.

        Returns:
            AnonymisationResult with anonymised text and metadata.

        Raises:
            RuntimeError: If anonymisation is not available.
        """
        if not self._available:
            error_msg = "PII anonymisation not available. Install with: pip install persona[privacy]"
            if self._import_error:
                error_msg += f"\nOriginal error: {self._import_error}"
            raise RuntimeError(error_msg)

        if strategy == AnonymisationStrategy.REDACT:
            anonymised_text = self._anonymise_redact(text, entities)
        elif strategy == AnonymisationStrategy.REPLACE:
            anonymised_text = self._anonymise_replace(text, entities)
        elif strategy == AnonymisationStrategy.HASH:
            anonymised_text = self._anonymise_hash(text, entities)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

        return AnonymisationResult(
            text=anonymised_text,
            entities=entities,
            strategy=strategy,
            original_length=len(text),
            anonymised_length=len(anonymised_text),
        )

    def _anonymise_redact(self, text: str, entities: list[PIIEntity]) -> str:
        """
        Redact PII by replacing with [TYPE] placeholders.

        Args:
            text: Original text.
            entities: List of detected entities.

        Returns:
            Text with PII redacted.
        """
        from presidio_anonymizer.entities import OperatorConfig

        # Convert PIIEntity to Presidio format
        analyzer_results = self._convert_entities(entities)

        # Use Presidio's redact operator
        operators = {entity.type: OperatorConfig("redact") for entity in entities}

        result = self._anonymizer.anonymize(
            text=text, analyzer_results=analyzer_results, operators=operators
        )

        return result.text

    def _anonymise_replace(self, text: str, entities: list[PIIEntity]) -> str:
        """
        Replace PII with fake but realistic data.

        Args:
            text: Original text.
            entities: List of detected entities.

        Returns:
            Text with PII replaced.
        """
        from presidio_anonymizer.entities import OperatorConfig

        # Convert PIIEntity to Presidio format
        analyzer_results = self._convert_entities(entities)

        # Use Presidio's replace operator with type-specific fake data
        operators = {}
        for entity in entities:
            operator = self._get_replace_operator(entity.type)
            operators[entity.type] = operator

        result = self._anonymizer.anonymize(
            text=text, analyzer_results=analyzer_results, operators=operators
        )

        return result.text

    def _anonymise_hash(self, text: str, entities: list[PIIEntity]) -> str:
        """
        Replace PII with deterministic hashes.

        Args:
            text: Original text.
            entities: List of detected entities.

        Returns:
            Text with PII hashed.
        """
        from presidio_anonymizer.entities import OperatorConfig

        # Convert PIIEntity to Presidio format
        analyzer_results = self._convert_entities(entities)

        # Use Presidio's hash operator
        operators = {
            entity.type: OperatorConfig("hash", {"hash_type": "sha256"})
            for entity in entities
        }

        result = self._anonymizer.anonymize(
            text=text, analyzer_results=analyzer_results, operators=operators
        )

        return result.text

    def _convert_entities(self, entities: list[PIIEntity]) -> list[Any]:
        """
        Convert PIIEntity objects to Presidio RecognizerResult format.

        Args:
            entities: List of PIIEntity objects.

        Returns:
            List of RecognizerResult objects.
        """
        from presidio_analyzer import RecognizerResult

        results = []
        for entity in entities:
            result = RecognizerResult(
                entity_type=entity.type,
                start=entity.start,
                end=entity.end,
                score=entity.score,
            )
            results.append(result)

        return results

    def _get_replace_operator(self, entity_type: str) -> Any:
        """
        Get appropriate replace operator for entity type.

        Args:
            entity_type: Type of entity.

        Returns:
            OperatorConfig for replacement.
        """
        from presidio_anonymizer.entities import OperatorConfig

        # Map entity types to replacement strategies
        replacements = {
            "PERSON": OperatorConfig("replace", {"new_value": "Anonymous Person"}),
            "EMAIL_ADDRESS": OperatorConfig(
                "replace", {"new_value": "anonymous@example.com"}
            ),
            "PHONE_NUMBER": OperatorConfig(
                "replace", {"new_value": "+44 20 7946 0000"}
            ),
            "LOCATION": OperatorConfig("replace", {"new_value": "London"}),
            "DATE_TIME": OperatorConfig("replace", {"new_value": "2024-01-01"}),
            "CREDIT_CARD": OperatorConfig(
                "replace", {"new_value": "0000-0000-0000-0000"}
            ),
            "IP_ADDRESS": OperatorConfig("replace", {"new_value": "0.0.0.0"}),
            "US_SSN": OperatorConfig("replace", {"new_value": "000-00-0000"}),
            "UK_NHS": OperatorConfig("replace", {"new_value": "000 000 0000"}),
            "IBAN_CODE": OperatorConfig(
                "replace", {"new_value": "GB00 0000 0000 0000 0000 00"}
            ),
            "URL": OperatorConfig("replace", {"new_value": "https://example.com"}),
        }

        return replacements.get(
            entity_type, OperatorConfig("replace", {"new_value": "[REDACTED]"})
        )
