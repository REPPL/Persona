"""
Faithfulness validator for persona quality scoring.

This module provides the main orchestrator for faithfulness validation,
coordinating claim extraction, source matching, and hallucination detection.
"""

import logging
from typing import Any

from persona.core.embedding.base import EmbeddingProvider
from persona.core.generation.parser import Persona
from persona.core.providers.base import LLMProvider
from persona.core.quality.faithfulness.extractor import ClaimExtractor
from persona.core.quality.faithfulness.hhem import HHEMClassifier
from persona.core.quality.faithfulness.matcher import SourceMatcher
from persona.core.quality.faithfulness.models import (
    Claim,
    FaithfulnessReport,
)

logger = logging.getLogger(__name__)


class FaithfulnessValidator:
    """
    Orchestrate faithfulness validation for personas.

    Coordinates claim extraction, source matching, and optional
    HHEM-based hallucination detection to assess persona faithfulness.

    Example:
        validator = FaithfulnessValidator(
            llm_provider=llm,
            embedding_provider=embeddings,
            use_hhem=True,
        )
        report = validator.validate(persona, source_data)
        print(f"Faithfulness: {report.faithfulness_score}%")
        print(f"Hallucinations: {report.unsupported_count}")
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        embedding_provider: EmbeddingProvider,
        use_hhem: bool = False,
        support_threshold: float = 0.7,
        chunk_size: int = 200,
        chunk_overlap: int = 50,
    ) -> None:
        """
        Initialise the faithfulness validator.

        Args:
            llm_provider: LLM provider for claim extraction.
            embedding_provider: Embedding provider for source matching.
            use_hhem: Whether to use HHEM classifier for refinement.
            support_threshold: Minimum similarity to consider supported (0-1).
            chunk_size: Words per source chunk.
            chunk_overlap: Words to overlap between chunks.
        """
        self.llm_provider = llm_provider
        self.embedding_provider = embedding_provider
        self.use_hhem = use_hhem
        self.support_threshold = support_threshold

        # Initialise components
        self.extractor = ClaimExtractor(llm_provider)
        self.matcher = SourceMatcher(
            embedding_provider,
            support_threshold=support_threshold,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # Optional HHEM classifier
        self.hhem_classifier: HHEMClassifier | None = None
        if use_hhem:
            self.hhem_classifier = HHEMClassifier()
            if not self.hhem_classifier.is_available():
                logger.warning(
                    "HHEM classifier requested but not available - "
                    "falling back to similarity-only matching"
                )
                self.hhem_classifier = None

    def validate(
        self,
        persona: Persona,
        source_data: str,
    ) -> FaithfulnessReport:
        """
        Validate faithfulness of a persona against source data.

        Args:
            persona: The persona to validate.
            source_data: Source data to verify against.

        Returns:
            FaithfulnessReport with detailed assessment.
        """
        # Step 1: Extract claims
        logger.debug(f"Extracting claims from persona: {persona.name}")
        claims = self.extractor.extract_claims(persona)
        logger.debug(f"Extracted {len(claims)} claims")

        # Step 2: Match claims to source
        logger.debug("Matching claims to source data")
        matches = self.matcher.match_claims(claims, source_data)
        logger.debug(f"Generated {len(matches)} matches")

        # Step 3: Optional HHEM refinement
        if self.hhem_classifier and self.hhem_classifier.is_available():
            logger.debug("Refining matches with HHEM classifier")
            matches = self.hhem_classifier.refine_matches(matches)

        # Step 4: Calculate metrics
        metrics = self.matcher.calculate_faithfulness_metrics(matches)
        unsupported = self.matcher.get_unsupported_claims(matches)

        # Step 5: Build report
        report = FaithfulnessReport(
            persona_id=persona.id,
            persona_name=persona.name,
            claims=claims,
            matches=matches,
            supported_ratio=metrics["supported_ratio"],
            hallucination_ratio=metrics["hallucination_ratio"],
            unsupported_claims=unsupported,
            details={
                "total_claims": len(claims),
                "supported_count": len([m for m in matches if m.is_supported]),
                "unsupported_count": len(unsupported),
                "average_similarity": metrics["average_similarity"],
                "direct_evidence_ratio": metrics["direct_evidence_ratio"],
                "support_threshold": self.support_threshold,
                "used_hhem": self.hhem_classifier is not None
                and self.hhem_classifier.is_available(),
            },
        )

        logger.info(
            f"Validation complete - Faithfulness: {report.faithfulness_score:.1f}%, "
            f"Unsupported: {report.unsupported_count}/{report.total_claims}"
        )

        return report

    def validate_batch(
        self,
        personas: list[Persona],
        source_data: str,
    ) -> list[FaithfulnessReport]:
        """
        Validate multiple personas against source data.

        Args:
            personas: List of personas to validate.
            source_data: Source data to verify against.

        Returns:
            List of FaithfulnessReport objects.
        """
        reports: list[FaithfulnessReport] = []
        for persona in personas:
            try:
                report = self.validate(persona, source_data)
                reports.append(report)
            except Exception as e:
                logger.error(f"Validation failed for persona {persona.name}: {e}")
                # Create minimal report for failed validation
                reports.append(
                    FaithfulnessReport(
                        persona_id=persona.id,
                        persona_name=persona.name,
                        claims=[],
                        matches=[],
                        supported_ratio=0.0,
                        hallucination_ratio=1.0,
                        unsupported_claims=[],
                        details={"error": str(e)},
                    )
                )

        return reports

    def get_hallucination_summary(
        self,
        report: FaithfulnessReport,
    ) -> dict[str, Any]:
        """
        Generate human-readable summary of hallucinations.

        Args:
            report: Faithfulness report to summarise.

        Returns:
            Dictionary with hallucination summary.
        """
        # Group unsupported claims by type
        from collections import defaultdict

        by_type: dict[str, list[Claim]] = defaultdict(list)
        for claim in report.unsupported_claims:
            by_type[claim.claim_type.value].append(claim)

        # Build summary
        summary = {
            "total_hallucinations": report.unsupported_count,
            "hallucination_rate": f"{report.hallucination_ratio * 100:.1f}%",
            "faithfulness_score": f"{report.faithfulness_score:.1f}%",
            "by_type": {
                claim_type: len(claims) for claim_type, claims in by_type.items()
            },
            "examples": [
                {
                    "type": claim.claim_type.value,
                    "text": claim.text,
                    "field": claim.source_field,
                }
                for claim in report.unsupported_claims[:5]  # First 5 examples
            ],
        }

        return summary

    def set_support_threshold(self, threshold: float) -> None:
        """
        Update support threshold for matching.

        Args:
            threshold: New threshold (0-1).

        Raises:
            ValueError: If threshold not in valid range.
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be 0-1, got {threshold}")

        self.support_threshold = threshold
        self.matcher.support_threshold = threshold

    def enable_hhem(self) -> bool:
        """
        Enable HHEM classifier if available.

        Returns:
            True if HHEM was successfully enabled.
        """
        if self.hhem_classifier is None:
            self.hhem_classifier = HHEMClassifier()

        if self.hhem_classifier.is_available():
            self.use_hhem = True
            return True
        else:
            logger.warning("HHEM classifier not available")
            return False

    def disable_hhem(self) -> None:
        """Disable HHEM classifier."""
        self.use_hhem = False
