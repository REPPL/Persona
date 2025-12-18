"""
Consistency checking for multi-model verification (F-120).

This module provides functionality to measure consistency across
persona generation outputs from different models.
"""


from persona.core.embedding import EmbeddingProvider, get_embedding_provider
from persona.core.generation.parser import Persona
from persona.core.quality.verification.models import (
    AttributeAgreement,
    ConsistencyMetrics,
)


class ConsistencyChecker:
    """
    Check consistency across multiple persona generation outputs.

    Measures agreement at multiple levels:
    - Attribute presence (which fields appear)
    - Semantic similarity (embedding-based)
    - Factual convergence (claim overlap)

    Example:
        >>> checker = ConsistencyChecker()
        >>> personas = [persona1, persona2, persona3]
        >>> metrics = checker.calculate_metrics(personas)
        >>> print(f"Consistency: {metrics.confidence_score:.2%}")
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider | None = None,
        embedding_model: str = "text-embedding-3-small",
    ):
        """
        Initialise the consistency checker.

        Args:
            embedding_provider: Optional custom embedding provider.
            embedding_model: Model to use for embeddings.
        """
        if embedding_provider is None:
            try:
                self.embedding_provider = get_embedding_provider(
                    provider_name="openai", model=embedding_model
                )
            except Exception:
                # Fall back to None if provider can't be created
                self.embedding_provider = None
        else:
            self.embedding_provider = embedding_provider

    def calculate_metrics(
        self,
        personas: list[Persona],
        weights: dict[str, float] | None = None,
    ) -> ConsistencyMetrics:
        """
        Calculate consistency metrics across personas.

        Args:
            personas: List of personas to compare.
            weights: Optional custom weights for metrics.

        Returns:
            ConsistencyMetrics with calculated values.
        """
        if len(personas) < 2:
            # Need at least 2 personas to measure consistency
            return ConsistencyMetrics(
                attribute_agreement=1.0,
                semantic_consistency=1.0,
                factual_convergence=1.0,
                weights=weights,
            )

        # Calculate individual metrics
        attr_agreement = self._calculate_attribute_agreement(personas)
        semantic_consistency = self._calculate_semantic_consistency(personas)
        factual_convergence = self._calculate_factual_convergence(personas)

        return ConsistencyMetrics(
            attribute_agreement=attr_agreement,
            semantic_consistency=semantic_consistency,
            factual_convergence=factual_convergence,
            weights=weights,
        )

    def _calculate_attribute_agreement(self, personas: list[Persona]) -> float:
        """
        Calculate what percentage of attributes appear in all personas.

        Args:
            personas: List of personas to compare.

        Returns:
            Agreement score between 0 and 1.
        """
        if not personas:
            return 0.0

        # Collect all attributes across all personas
        all_attributes = set()
        for persona in personas:
            persona_dict = persona.to_dict()
            # Focus on substantive fields
            substantive_fields = [
                "name",
                "demographics",
                "goals",
                "pain_points",
                "behaviours",
                "quotes",
            ]
            for field in substantive_fields:
                if field in persona_dict and persona_dict[field]:
                    all_attributes.add(field)

        if not all_attributes:
            return 0.0

        # Count how many personas have each attribute
        agreements = []
        for attr in all_attributes:
            count = sum(
                1 for p in personas if attr in p.to_dict() and p.to_dict()[attr]
            )
            agreements.append(count / len(personas))

        # Return average agreement across all attributes
        return sum(agreements) / len(agreements) if agreements else 0.0

    def _calculate_semantic_consistency(self, personas: list[Persona]) -> float:
        """
        Calculate semantic similarity using embeddings.

        Args:
            personas: List of personas to compare.

        Returns:
            Semantic consistency score between 0 and 1.
        """
        if len(personas) < 2:
            return 1.0

        # Convert personas to text representations
        texts = [self._persona_to_text(p) for p in personas]

        # Get embeddings
        try:
            if (
                self.embedding_provider is None
                or not self.embedding_provider.is_configured()
            ):
                # Fall back to simpler comparison if embeddings unavailable
                return self._simple_text_similarity(texts)

            embeddings = [self.embedding_provider.embed(text) for text in texts]

            # Calculate pairwise similarities
            similarities = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    sim = embeddings[i].cosine_similarity(embeddings[j])
                    similarities.append(sim)

            return sum(similarities) / len(similarities) if similarities else 0.0

        except Exception:
            # Fall back to simple comparison on error
            return self._simple_text_similarity(texts)

    def _calculate_factual_convergence(self, personas: list[Persona]) -> float:
        """
        Calculate what percentage of factual claims appear in majority of outputs.

        Args:
            personas: List of personas to compare.

        Returns:
            Convergence score between 0 and 1.
        """
        if len(personas) < 2:
            return 1.0

        # Extract factual claims from each persona
        all_claims = []
        for persona in personas:
            claims = self._extract_claims(persona)
            all_claims.append(claims)

        if not any(all_claims):
            return 0.0

        # Find unique claims
        unique_claims = set()
        for claims in all_claims:
            unique_claims.update(claims)

        # Count how many personas contain each claim
        claim_counts = {}
        for claim in unique_claims:
            count = sum(1 for claims in all_claims if claim in claims)
            claim_counts[claim] = count

        # Calculate percentage of claims in majority
        majority_threshold = len(personas) / 2
        majority_claims = sum(
            1 for count in claim_counts.values() if count > majority_threshold
        )

        return majority_claims / len(unique_claims) if unique_claims else 0.0

    def get_attribute_details(
        self,
        personas: list[Persona],
    ) -> dict[str, AttributeAgreement]:
        """
        Get detailed agreement information for each attribute.

        Args:
            personas: List of personas to analyse.

        Returns:
            Dictionary mapping attribute names to agreement details.
        """
        if not personas:
            return {}

        # Collect all attributes
        all_attributes = set()
        for persona in personas:
            all_attributes.update(persona.to_dict().keys())

        # Calculate agreement for each attribute
        details = {}
        total_count = len(personas)

        for attr in all_attributes:
            values = []
            present_count = 0

            for persona in personas:
                persona_dict = persona.to_dict()
                if attr in persona_dict and persona_dict[attr]:
                    values.append(persona_dict[attr])
                    present_count += 1

            details[attr] = AttributeAgreement(
                attribute=attr,
                present_count=present_count,
                total_count=total_count,
                values=values,
            )

        return details

    def _persona_to_text(self, persona: Persona) -> str:
        """
        Convert persona to text representation for embedding.

        Args:
            persona: Persona to convert.

        Returns:
            Text representation.
        """
        parts = [f"Name: {persona.name}"]

        if persona.demographics:
            demo_parts = [f"{k}: {v}" for k, v in persona.demographics.items()]
            parts.append(f"Demographics: {', '.join(demo_parts)}")

        if persona.goals:
            parts.append(f"Goals: {'; '.join(persona.goals)}")

        if persona.pain_points:
            parts.append(f"Pain Points: {'; '.join(persona.pain_points)}")

        if persona.behaviours:
            parts.append(f"Behaviours: {'; '.join(persona.behaviours)}")

        if persona.quotes:
            parts.append(f"Quotes: {'; '.join(persona.quotes)}")

        return " | ".join(parts)

    def _simple_text_similarity(self, texts: list[str]) -> float:
        """
        Calculate simple text similarity without embeddings.

        Uses Jaccard similarity on word sets.

        Args:
            texts: List of texts to compare.

        Returns:
            Similarity score between 0 and 1.
        """
        if len(texts) < 2:
            return 1.0

        # Convert to word sets
        word_sets = [set(text.lower().split()) for text in texts]

        # Calculate pairwise Jaccard similarities
        similarities = []
        for i in range(len(word_sets)):
            for j in range(i + 1, len(word_sets)):
                intersection = len(word_sets[i] & word_sets[j])
                union = len(word_sets[i] | word_sets[j])
                sim = intersection / union if union > 0 else 0.0
                similarities.append(sim)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _extract_claims(self, persona: Persona) -> set[str]:
        """
        Extract factual claims from a persona.

        Args:
            persona: Persona to extract claims from.

        Returns:
            Set of claim strings.
        """
        claims = set()

        # Add goals as claims
        for goal in persona.goals:
            claims.add(goal.lower().strip())

        # Add pain points as claims
        for pain in persona.pain_points:
            claims.add(pain.lower().strip())

        # Add behaviours as claims
        for behaviour in persona.behaviours:
            claims.add(behaviour.lower().strip())

        # Add demographic info as claims
        for key, value in persona.demographics.items():
            claims.add(f"{key}: {value}".lower().strip())

        return claims
