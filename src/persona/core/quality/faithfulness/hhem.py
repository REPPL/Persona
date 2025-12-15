"""
HHEM (Hughes Hallucination Evaluation Model) classifier.

This module provides advanced hallucination detection using the HHEM model,
which classifies claim-source pairs as entailment, contradiction, or neutral.

Optional dependency: requires transformers library.
"""

import logging
from typing import Any

from persona.core.quality.faithfulness.models import Claim, SourceMatch

logger = logging.getLogger(__name__)


class HHEMClassifier:
    """
    HHEM-based hallucination classifier.

    Uses the Hughes Hallucination Evaluation Model to classify
    claim-source pairs for more accurate hallucination detection.

    This is an optional enhancement that requires the transformers library.
    If not available, gracefully degrades to similarity-only matching.

    Example:
        try:
            classifier = HHEMClassifier()
            if classifier.is_available():
                result = classifier.classify("User is 25 years old", "Age: 25")
                print(result["label"])  # "entailment"
        except ImportError:
            # Fall back to similarity-only matching
            pass
    """

    # HHEM model identifier (Hugging Face)
    DEFAULT_MODEL = "vectara/hallucination_evaluation_model"

    def __init__(
        self,
        model_name: str | None = None,
        device: str = "cpu",
    ) -> None:
        """
        Initialise the HHEM classifier.

        Args:
            model_name: Model identifier (defaults to HHEM).
            device: Device to run model on ('cpu' or 'cuda').
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.device = device
        self._model: Any = None
        self._tokenizer: Any = None
        self._available = False

        # Try to load model
        self._load_model()

    def _load_model(self) -> None:
        """Load HHEM model and tokeniser if available."""
        try:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            logger.info(f"Loading HHEM model: {self.model_name}")

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name
            )
            self._model.to(self.device)
            self._model.eval()

            self._available = True
            logger.info("HHEM model loaded successfully")

        except ImportError:
            logger.warning(
                "transformers library not available - HHEM classifier disabled"
            )
            self._available = False
        except Exception as e:
            logger.warning(f"Failed to load HHEM model: {e}")
            self._available = False

    def is_available(self) -> bool:
        """
        Check if HHEM classifier is available.

        Returns:
            True if model loaded successfully.
        """
        return self._available

    def classify(
        self,
        claim_text: str,
        source_text: str,
    ) -> dict[str, Any]:
        """
        Classify claim-source relationship.

        Args:
            claim_text: The claim to verify.
            source_text: The source text to check against.

        Returns:
            Dictionary with classification results:
                - label: 'entailment', 'contradiction', or 'neutral'
                - score: Confidence score (0-1)
                - is_hallucination: True if contradiction detected

        Raises:
            RuntimeError: If model is not available.
        """
        if not self._available:
            raise RuntimeError("HHEM model not available")

        # Prepare input
        inputs = self._tokenizer(
            claim_text,
            source_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        inputs = inputs.to(self.device)

        # Run inference
        import torch

        with torch.no_grad():
            outputs = self._model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][predicted_class].item()

        # Map class to label
        # HHEM typically uses: 0=entailment, 1=neutral, 2=contradiction
        label_map = {
            0: "entailment",
            1: "neutral",
            2: "contradiction",
        }
        label = label_map.get(predicted_class, "neutral")

        return {
            "label": label,
            "score": confidence,
            "is_hallucination": label == "contradiction",
            "probabilities": {
                "entailment": probs[0][0].item(),
                "neutral": probs[0][1].item(),
                "contradiction": probs[0][2].item(),
            },
        }

    def refine_matches(
        self,
        matches: list[SourceMatch],
        contradiction_threshold: float = 0.7,
    ) -> list[SourceMatch]:
        """
        Refine source matches using HHEM classification.

        Args:
            matches: Initial matches from similarity-based matching.
            contradiction_threshold: Minimum confidence to override similarity.

        Returns:
            Refined matches with updated support status.
        """
        if not self._available:
            logger.warning("HHEM not available - returning original matches")
            return matches

        refined_matches: list[SourceMatch] = []

        for match in matches:
            # Skip if no source text
            if not match.source_text:
                refined_matches.append(match)
                continue

            # Classify with HHEM
            try:
                result = self.classify(match.claim.text, match.source_text)

                # Update match based on HHEM result
                updated_match = self._update_match_with_hhem(
                    match, result, contradiction_threshold
                )
                refined_matches.append(updated_match)

            except Exception as e:
                logger.warning(f"HHEM classification failed: {e}")
                refined_matches.append(match)

        return refined_matches

    def _update_match_with_hhem(
        self,
        match: SourceMatch,
        hhem_result: dict[str, Any],
        contradiction_threshold: float,
    ) -> SourceMatch:
        """
        Update match with HHEM classification results.

        Args:
            match: Original source match.
            hhem_result: HHEM classification result.
            contradiction_threshold: Threshold for contradiction override.

        Returns:
            Updated source match.
        """
        label = hhem_result["label"]
        confidence = hhem_result["score"]

        # Strong contradiction overrides similarity
        if label == "contradiction" and confidence >= contradiction_threshold:
            return SourceMatch(
                claim=match.claim,
                source_text=match.source_text,
                similarity_score=match.similarity_score,
                is_supported=False,
                evidence_type="contradiction",
            )

        # Strong entailment confirms support
        if label == "entailment" and confidence >= contradiction_threshold:
            return SourceMatch(
                claim=match.claim,
                source_text=match.source_text,
                similarity_score=match.similarity_score,
                is_supported=True,
                evidence_type="direct" if confidence >= 0.9 else "inferred",
            )

        # Neutral or low confidence - keep original
        return match

    def batch_classify(
        self,
        claim_source_pairs: list[tuple[str, str]],
    ) -> list[dict[str, Any]]:
        """
        Classify multiple claim-source pairs in batch.

        Args:
            claim_source_pairs: List of (claim, source) tuples.

        Returns:
            List of classification results.
        """
        if not self._available:
            raise RuntimeError("HHEM model not available")

        results: list[dict[str, Any]] = []
        for claim_text, source_text in claim_source_pairs:
            try:
                result = self.classify(claim_text, source_text)
                results.append(result)
            except Exception as e:
                logger.warning(f"Batch classification failed for pair: {e}")
                results.append({
                    "label": "neutral",
                    "score": 0.0,
                    "is_hallucination": False,
                    "probabilities": {
                        "entailment": 0.0,
                        "neutral": 1.0,
                        "contradiction": 0.0,
                    },
                })

        return results
