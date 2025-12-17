"""
Bias detector orchestrator.

This module provides the main BiasDetector class that coordinates
multiple detection methods (lexicon, embedding, LLM) to produce
comprehensive bias reports.
"""

from typing import TYPE_CHECKING

from persona.core.generation.parser import Persona
from persona.core.quality.bias.embedding import (
    EmbeddingAnalyser,
    _check_embedding_available,
)
from persona.core.quality.bias.judge import BiasJudge
from persona.core.quality.bias.lexicon import LexiconMatcher
from persona.core.quality.bias.models import BiasConfig, BiasFinding, BiasReport

if TYPE_CHECKING:
    from persona.core.providers.base import LLMProvider


class BiasDetector:
    """
    Orchestrate multiple bias detection methods.

    Combines lexicon-based, embedding-based, and LLM-based detection
    to provide comprehensive bias analysis.
    """

    def __init__(
        self,
        config: BiasConfig | None = None,
        llm_provider: "LLMProvider | None" = None,
    ) -> None:
        """
        Initialise the bias detector.

        Args:
            config: Bias detection configuration.
            llm_provider: Optional LLM provider for judge-based detection.
        """
        self.config = config or BiasConfig()
        self._init_detectors(llm_provider)

    def _init_detectors(self, llm_provider: "LLMProvider | None") -> None:
        """
        Initialise detection components based on configuration.

        Args:
            llm_provider: Optional LLM provider.
        """
        self.lexicon = None
        self.embedding = None
        self.judge = None

        # Initialise lexicon matcher
        if "lexicon" in self.config.methods:
            try:
                self.lexicon = LexiconMatcher(self.config.lexicon)
            except (FileNotFoundError, ValueError, OSError):
                # If lexicon loading fails, continue without it
                pass

        # Initialise embedding analyser
        if "embedding" in self.config.methods:
            if _check_embedding_available():
                try:
                    self.embedding = EmbeddingAnalyser(self.config.embedding_model)
                except (ImportError, ValueError, OSError):
                    # If embedding model loading fails, continue without it
                    pass

        # Initialise LLM judge
        if "llm" in self.config.methods and llm_provider:
            self.judge = BiasJudge(llm_provider)

    def _aggregate_scores(self, findings: list[BiasFinding]) -> dict[str, float]:
        """
        Aggregate bias scores by category.

        Args:
            findings: List of all bias findings.

        Returns:
            Dictionary mapping category to bias score (0-1).
        """
        category_scores = {}

        for category_name in self.config.categories:
            # Get findings for this category
            category_findings = [
                f for f in findings if f.category.value == category_name
            ]

            if not category_findings:
                category_scores[category_name] = 0.0
                continue

            # Calculate weighted score based on severity and confidence
            severity_weights = {"low": 0.3, "medium": 0.6, "high": 1.0}

            total_score = 0.0
            for finding in category_findings:
                severity_weight = severity_weights.get(finding.severity.value, 0.5)
                total_score += severity_weight * finding.confidence

            # Normalise by number of findings (cap at 1.0)
            category_scores[category_name] = min(
                total_score / len(category_findings), 1.0
            )

        return category_scores

    def _calculate_overall(self, category_scores: dict[str, float]) -> float:
        """
        Calculate overall bias score.

        Args:
            category_scores: Scores by category.

        Returns:
            Overall bias score (0-1).
        """
        if not category_scores:
            return 0.0

        # Return mean of category scores
        return sum(category_scores.values()) / len(category_scores)

    def _deduplicate_findings(self, findings: list[BiasFinding]) -> list[BiasFinding]:
        """
        Remove duplicate findings across methods.

        Args:
            findings: All findings from all methods.

        Returns:
            Deduplicated findings list.
        """
        # Group by (category, evidence)
        seen = set()
        deduplicated = []

        for finding in findings:
            # Create fingerprint
            fingerprint = (
                finding.category.value,
                finding.evidence[:100],  # First 100 chars
            )

            if fingerprint not in seen:
                seen.add(fingerprint)
                deduplicated.append(finding)

        return deduplicated

    def analyse(self, persona: Persona) -> BiasReport:
        """
        Run all configured detection methods on a persona.

        Args:
            persona: The persona to analyse.

        Returns:
            Comprehensive bias report.
        """
        all_findings = []

        # Run lexicon-based detection
        if self.lexicon:
            try:
                lexicon_findings = self.lexicon.analyse(persona, self.config.categories)
                all_findings.extend(lexicon_findings)
            except (ValueError, KeyError, AttributeError):
                # Analysis failure - continue with other methods
                pass

        # Run embedding-based detection
        if self.embedding:
            try:
                embedding_findings = self.embedding.analyse(
                    persona, self.config.categories
                )
                all_findings.extend(embedding_findings)
            except (ValueError, KeyError, AttributeError, RuntimeError):
                # Analysis failure - continue with other methods
                pass

        # Run LLM judge detection
        if self.judge:
            try:
                judge_findings = self.judge.analyse(persona, self.config.categories)
                all_findings.extend(judge_findings)
            except (ValueError, KeyError, AttributeError, RuntimeError):
                # Analysis failure - continue with other methods
                pass

        # Filter by confidence threshold
        filtered_findings = [
            f for f in all_findings if f.confidence >= self.config.threshold
        ]

        # Deduplicate findings
        deduplicated_findings = self._deduplicate_findings(filtered_findings)

        # Aggregate scores by category
        category_scores = self._aggregate_scores(deduplicated_findings)

        # Calculate overall score
        overall_score = self._calculate_overall(category_scores)

        # Get persona ID and name
        persona_id = getattr(persona, "id", "unknown")
        persona_name = getattr(persona, "name", None)

        return BiasReport(
            persona_id=persona_id,
            persona_name=persona_name,
            overall_score=overall_score,
            findings=deduplicated_findings,
            category_scores=category_scores,
            methods_used=self.config.methods,
        )
