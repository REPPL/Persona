"""
Embedding-based bias detection using WEAT (Word Embedding Association Test).

This module implements the WEAT algorithm to detect implicit biases in
persona representations using semantic embeddings.
"""

from typing import Any

from persona.core.generation.parser import Persona
from persona.core.quality.bias.models import BiasCategory, BiasFinding, Severity

# Optional dependency - gracefully degrade if not available
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    np = None  # type: ignore
    SentenceTransformer = None  # type: ignore


class EmbeddingAnalyser:
    """
    Detect bias using WEAT (Word Embedding Association Test).

    WEAT measures the association between target concepts and attributes
    in embedding space to detect implicit bias.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialise the embedding analyser.

        Args:
            model_name: Sentence transformer model to use.

        Raises:
            ImportError: If sentence-transformers is not installed.
        """
        if not EMBEDDING_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for embedding-based bias detection. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self._load_weat_sets()

    def _load_weat_sets(self) -> None:
        """Load WEAT target and attribute word sets."""
        # Gender bias: career vs family associations
        self.gender_targets = {
            "male": [
                "he",
                "him",
                "his",
                "man",
                "male",
                "boy",
                "father",
                "son",
                "brother",
                "husband",
            ],
            "female": [
                "she",
                "her",
                "hers",
                "woman",
                "female",
                "girl",
                "mother",
                "daughter",
                "sister",
                "wife",
            ],
        }

        self.gender_attributes = {
            "career": [
                "career",
                "professional",
                "business",
                "executive",
                "salary",
                "office",
                "management",
                "corporation",
            ],
            "family": [
                "family",
                "home",
                "children",
                "domestic",
                "household",
                "nurture",
                "caring",
                "parent",
            ],
        }

        # Age bias: young vs old associations
        self.age_targets = {
            "young": [
                "young",
                "youth",
                "teenager",
                "millennial",
                "gen z",
                "junior",
                "early career",
            ],
            "old": [
                "old",
                "elderly",
                "senior",
                "retired",
                "aged",
                "mature",
                "veteran",
                "experienced",
            ],
        }

        self.age_attributes = {
            "technology": [
                "technology",
                "digital",
                "online",
                "software",
                "computer",
                "internet",
                "app",
            ],
            "traditional": [
                "traditional",
                "conventional",
                "established",
                "classic",
                "legacy",
                "old-fashioned",
            ],
        }

    def _compute_cosine_similarity(
        self, embedding_a: Any, embedding_b: Any
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding_a: First embedding vector.
            embedding_b: Second embedding vector.

        Returns:
            Cosine similarity (-1 to 1).
        """
        return float(
            np.dot(embedding_a, embedding_b)
            / (np.linalg.norm(embedding_a) * np.linalg.norm(embedding_b))
        )

    def _mean_cosine_similarity(
        self, target_embedding: Any, attribute_embeddings: list[Any]
    ) -> float:
        """
        Compute mean cosine similarity between target and attribute embeddings.

        Args:
            target_embedding: Target embedding.
            attribute_embeddings: List of attribute embeddings.

        Returns:
            Mean similarity score.
        """
        similarities = [
            self._compute_cosine_similarity(target_embedding, attr_emb)
            for attr_emb in attribute_embeddings
        ]
        return float(np.mean(similarities))

    def _compute_weat_score(
        self,
        target_texts: list[str],
        attribute_a: list[str],
        attribute_b: list[str],
    ) -> float:
        """
        Compute WEAT effect size.

        The WEAT score measures the differential association between
        a set of target concepts and two sets of attributes.

        Args:
            target_texts: Target concept texts from persona.
            attribute_a: First attribute word set.
            attribute_b: Second attribute word set.

        Returns:
            WEAT effect size (-inf to +inf, typically -2 to 2).
        """
        if not target_texts:
            return 0.0

        # Get embeddings
        target_embeddings = self.model.encode(target_texts)
        attr_a_embeddings = self.model.encode(attribute_a)
        attr_b_embeddings = self.model.encode(attribute_b)

        # Compute association scores for each target
        scores = []
        for target_emb in target_embeddings:
            mean_sim_a = self._mean_cosine_similarity(target_emb, attr_a_embeddings)
            mean_sim_b = self._mean_cosine_similarity(target_emb, attr_b_embeddings)
            scores.append(mean_sim_a - mean_sim_b)

        # Return mean effect size
        return float(np.mean(scores))

    def _extract_persona_text(self, persona: Persona) -> list[str]:
        """
        Extract text segments from persona.

        Args:
            persona: The persona to extract text from.

        Returns:
            List of text segments.
        """
        texts = []

        # Behaviours
        if hasattr(persona, "behaviours") and persona.behaviours:
            texts.extend(persona.behaviours)

        # Goals
        if hasattr(persona, "goals") and persona.goals:
            texts.extend(persona.goals)

        # Pain points
        if hasattr(persona, "pain_points") and persona.pain_points:
            texts.extend(persona.pain_points)

        # Quote
        if hasattr(persona, "quote") and persona.quote:
            texts.append(persona.quote)

        return texts

    def analyse_gender_bias(
        self, persona: Persona, threshold: float
    ) -> list[BiasFinding]:
        """
        Analyse gender bias using WEAT.

        Args:
            persona: The persona to analyse.
            threshold: Effect size threshold for reporting.

        Returns:
            List of gender bias findings.
        """
        findings = []
        texts = self._extract_persona_text(persona)

        if not texts:
            return findings

        # Compute WEAT score for career vs family associations
        effect_size = self._compute_weat_score(
            texts,
            self.gender_attributes["career"],
            self.gender_attributes["family"],
        )

        # Report significant associations
        if abs(effect_size) >= threshold:
            direction = "career" if effect_size > 0 else "family"
            severity = (
                Severity.HIGH
                if abs(effect_size) > 1.0
                else Severity.MEDIUM
                if abs(effect_size) > 0.7
                else Severity.LOW
            )

            findings.append(
                BiasFinding(
                    category=BiasCategory.GENDER,
                    description=f"Gender-{direction} association detected (WEAT effect size: {effect_size:.3f})",
                    evidence="; ".join(texts[:3]),  # Show first 3 text segments
                    severity=severity,
                    method="embedding",
                    confidence=min(abs(effect_size), 1.0),
                    context="WEAT analysis",
                )
            )

        return findings

    def analyse_age_bias(
        self, persona: Persona, threshold: float
    ) -> list[BiasFinding]:
        """
        Analyse age bias using WEAT.

        Args:
            persona: The persona to analyse.
            threshold: Effect size threshold for reporting.

        Returns:
            List of age bias findings.
        """
        findings = []
        texts = self._extract_persona_text(persona)

        if not texts:
            return findings

        # Compute WEAT score for technology vs traditional associations
        effect_size = self._compute_weat_score(
            texts,
            self.age_attributes["technology"],
            self.age_attributes["traditional"],
        )

        # Report significant associations
        if abs(effect_size) >= threshold:
            direction = "technology" if effect_size > 0 else "traditional"
            severity = (
                Severity.HIGH
                if abs(effect_size) > 1.0
                else Severity.MEDIUM
                if abs(effect_size) > 0.7
                else Severity.LOW
            )

            findings.append(
                BiasFinding(
                    category=BiasCategory.AGE,
                    description=f"Age-{direction} association detected (WEAT effect size: {effect_size:.3f})",
                    evidence="; ".join(texts[:3]),
                    severity=severity,
                    method="embedding",
                    confidence=min(abs(effect_size), 1.0),
                    context="WEAT analysis",
                )
            )

        return findings

    def analyse(self, persona: Persona, categories: list[str]) -> list[BiasFinding]:
        """
        Analyse persona for bias using WEAT.

        Args:
            persona: The persona to analyse.
            categories: List of bias categories to check.

        Returns:
            List of detected bias findings.
        """
        findings = []
        threshold = 0.5  # Default WEAT threshold

        if "gender" in categories:
            findings.extend(self.analyse_gender_bias(persona, threshold))

        if "age" in categories:
            findings.extend(self.analyse_age_bias(persona, threshold))

        return findings
