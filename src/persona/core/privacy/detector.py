"""
PII detection using Microsoft Presidio.

This module provides the PIIDetector class that uses Presidio to detect
personally identifiable information in text.
"""

from typing import Any

from persona.core.privacy.entities import PIIEntity, PIIType


class PIIDetector:
    """
    Detects personally identifiable information (PII) in text.

    Uses Microsoft Presidio for detection. Gracefully degrades if
    Presidio is not installed.

    Example:
        detector = PIIDetector()
        entities = detector.detect("Contact John Smith at john@example.com")
        # [PIIEntity(type="PERSON", text="John Smith", ...),
        #  PIIEntity(type="EMAIL_ADDRESS", text="john@example.com", ...)]
    """

    def __init__(
        self,
        language: str = "en",
        score_threshold: float = 0.5,
        entities: list[str] | None = None,
    ) -> None:
        """
        Initialise PII detector.

        Args:
            language: Language code for detection (default: "en").
            score_threshold: Minimum confidence score (0.0-1.0).
            entities: List of entity types to detect (None = all).

        Raises:
            ImportError: If presidio-analyzer is not installed.
        """
        self.language = language
        self.score_threshold = score_threshold
        self.entities = entities

        # Import presidio (graceful degradation)
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_analyzer.nlp_engine import NlpEngineProvider

            self._analyzer = self._initialise_analyzer()
            self._available = True
        except ImportError as e:
            self._analyzer = None
            self._available = False
            self._import_error = e

    def _initialise_analyzer(self) -> Any:
        """
        Initialise Presidio analyzer engine.

        Returns:
            AnalyzerEngine instance.

        Raises:
            ImportError: If spaCy model is not available.
        """
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import NlpEngineProvider

        try:
            # Try to use the large English model
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
            }
            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()

            return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
        except (OSError, Exception):
            # Fallback to default model if en_core_web_lg not available
            return AnalyzerEngine()

    def is_available(self) -> bool:
        """
        Check if PII detection is available.

        Returns:
            True if Presidio is installed and configured, False otherwise.
        """
        return self._available

    def get_import_error(self) -> ImportError | None:
        """
        Get the import error if detection is not available.

        Returns:
            ImportError if Presidio is not installed, None otherwise.
        """
        return getattr(self, "_import_error", None)

    def detect(self, text: str, language: str | None = None) -> list[PIIEntity]:
        """
        Detect PII entities in text.

        Args:
            text: Text to analyse.
            language: Override language (default: use instance language).

        Returns:
            List of detected PII entities.

        Raises:
            RuntimeError: If detection is not available.
        """
        if not self._available:
            error_msg = "PII detection not available. Install with: pip install persona[privacy]"
            if hasattr(self, "_import_error"):
                error_msg += f"\nOriginal error: {self._import_error}"
            raise RuntimeError(error_msg)

        lang = language or self.language

        # Analyse text with Presidio
        results = self._analyzer.analyze(
            text=text,
            language=lang,
            entities=self.entities,
            score_threshold=self.score_threshold,
        )

        # Convert to PIIEntity objects
        entities = []
        for result in results:
            entity = PIIEntity(
                type=result.entity_type,
                text=text[result.start : result.end],
                start=result.start,
                end=result.end,
                score=result.score,
                metadata={
                    "recognition_metadata": result.recognition_metadata,
                    "analysis_explanation": (
                        result.analysis_explanation.to_dict()
                        if result.analysis_explanation
                        else None
                    ),
                },
            )
            entities.append(entity)

        return entities

    def get_supported_entities(self) -> list[str]:
        """
        Get list of supported entity types.

        Returns:
            List of supported entity type names.

        Raises:
            RuntimeError: If detection is not available.
        """
        if not self._available:
            raise RuntimeError(
                "PII detection not available. Install with: pip install persona[privacy]"
            )

        return self._analyzer.get_supported_entities(language=self.language)

    def scan_text(self, text: str) -> dict[str, Any]:
        """
        Scan text and return summary of detected PII.

        Args:
            text: Text to scan.

        Returns:
            Dictionary with scan results including:
            - entities: List of detected entities
            - entity_count: Total number of entities
            - entity_types: Unique entity types found
            - has_pii: Whether any PII was found
        """
        entities = self.detect(text)

        return {
            "entities": entities,
            "entity_count": len(entities),
            "entity_types": list({e.type for e in entities}),
            "has_pii": len(entities) > 0,
        }
