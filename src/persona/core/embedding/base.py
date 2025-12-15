"""
Abstract base class for embedding providers.

This module provides the EmbeddingProvider abstract base class that all
embedding providers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmbeddingResponse:
    """
    Response from an embedding provider.

    Attributes:
        vector: The embedding vector as a list of floats.
        model: The model used to generate the embedding.
        input_tokens: Number of tokens in the input text.
        dimensions: Dimensionality of the embedding vector.
        metadata: Additional provider-specific metadata.
    """

    vector: list[float]
    model: str
    input_tokens: int = 0
    dimensions: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set dimensions from vector if not provided."""
        if self.dimensions == 0 and self.vector:
            self.dimensions = len(self.vector)

    def cosine_similarity(self, other: "EmbeddingResponse") -> float:
        """
        Calculate cosine similarity with another embedding.

        Args:
            other: Another embedding response.

        Returns:
            Cosine similarity score between 0 and 1.

        Raises:
            ValueError: If dimensions don't match.
        """
        if self.dimensions != other.dimensions:
            raise ValueError(
                f"Dimension mismatch: {self.dimensions} vs {other.dimensions}"
            )

        if not self.vector or not other.vector:
            return 0.0

        dot_product = sum(a * b for a, b in zip(self.vector, other.vector))
        norm_a = sum(a * a for a in self.vector) ** 0.5
        norm_b = sum(b * b for b in other.vector) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)


@dataclass
class BatchEmbeddingResponse:
    """
    Response from batch embedding request.

    Attributes:
        embeddings: List of individual embedding responses.
        total_tokens: Total tokens used across all inputs.
        model: The model used for embedding.
    """

    embeddings: list[EmbeddingResponse]
    total_tokens: int = 0
    model: str = ""

    def __post_init__(self) -> None:
        """Calculate total tokens if not provided."""
        if self.total_tokens == 0 and self.embeddings:
            self.total_tokens = sum(e.input_tokens for e in self.embeddings)
        if not self.model and self.embeddings:
            self.model = self.embeddings[0].model


class EmbeddingProvider(ABC):
    """
    Abstract base class for embedding providers.

    Embedding providers generate vector representations of text that
    capture semantic meaning, enabling similarity comparisons.

    Example:
        class CustomEmbeddingProvider(EmbeddingProvider):
            @property
            def name(self) -> str:
                return "custom"

            @property
            def dimension(self) -> int:
                return 768

            def embed(self, text: str) -> EmbeddingResponse:
                # Implementation
                ...
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the unique name of this provider.

        Returns:
            Provider name (e.g., 'openai', 'local').
        """
        ...

    @property
    @abstractmethod
    def model(self) -> str:
        """
        Return the model identifier used for embeddings.

        Returns:
            Model name (e.g., 'text-embedding-3-small').
        """
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Return the dimensionality of embeddings.

        Returns:
            Vector dimension (e.g., 1536 for text-embedding-3-small).
        """
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """
        Check if the provider is properly configured.

        Returns:
            True if provider is ready to use.
        """
        ...

    @abstractmethod
    def embed(self, text: str) -> EmbeddingResponse:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResponse with the vector and metadata.

        Raises:
            RuntimeError: If embedding generation fails.
            ValueError: If text is empty or invalid.
        """
        ...

    def embed_batch(self, texts: list[str]) -> BatchEmbeddingResponse:
        """
        Generate embeddings for multiple texts.

        Default implementation calls embed() for each text.
        Override for providers that support batch operations.

        Args:
            texts: List of texts to embed.

        Returns:
            BatchEmbeddingResponse with all embeddings.
        """
        embeddings = [self.embed(text) for text in texts]
        return BatchEmbeddingResponse(embeddings=embeddings)

    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two texts.

        Args:
            text1: First text.
            text2: Second text.

        Returns:
            Cosine similarity score between 0 and 1.
        """
        emb1 = self.embed(text1)
        emb2 = self.embed(text2)
        return emb1.cosine_similarity(emb2)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<{self.__class__.__name__}(name='{self.name}', model='{self.model}')>"
