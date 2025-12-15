"""
OpenAI embedding provider implementation.

This module provides embedding generation using OpenAI's text-embedding models.
"""

import logging
import os
from typing import Any

from persona.core.embedding.base import (
    BatchEmbeddingResponse,
    EmbeddingProvider,
    EmbeddingResponse,
)

logger = logging.getLogger(__name__)


# Model configurations
OPENAI_EMBEDDING_MODELS: dict[str, dict[str, Any]] = {
    "text-embedding-3-small": {
        "dimension": 1536,
        "max_tokens": 8191,
        "cost_per_1k": 0.00002,
    },
    "text-embedding-3-large": {
        "dimension": 3072,
        "max_tokens": 8191,
        "cost_per_1k": 0.00013,
    },
    "text-embedding-ada-002": {
        "dimension": 1536,
        "max_tokens": 8191,
        "cost_per_1k": 0.0001,
    },
}


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI embedding provider.

    Uses OpenAI's text-embedding models for generating embeddings.
    Default model is text-embedding-3-small for cost efficiency.

    Example:
        provider = OpenAIEmbeddingProvider()
        if provider.is_configured():
            embedding = provider.embed("Hello, world!")
            print(f"Vector dimension: {embedding.dimensions}")
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
    ) -> None:
        """
        Initialise the OpenAI embedding provider.

        Args:
            model: The embedding model to use.
            api_key: Optional API key. If not provided, uses OPENAI_API_KEY env var.
        """
        self._model = model
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self._client: Any = None

        if model not in OPENAI_EMBEDDING_MODELS:
            logger.warning(
                f"Unknown model '{model}', using default configuration. "
                f"Known models: {list(OPENAI_EMBEDDING_MODELS.keys())}"
            )

    @property
    def name(self) -> str:
        """Return provider name."""
        return "openai"

    @property
    def model(self) -> str:
        """Return model identifier."""
        return self._model

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        config = OPENAI_EMBEDDING_MODELS.get(self._model, {})
        return config.get("dimension", 1536)

    def is_configured(self) -> bool:
        """Check if provider is configured with API key."""
        return bool(self._api_key)

    def _get_client(self) -> Any:
        """Lazy-load the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self._api_key)
            except ImportError:
                raise RuntimeError(
                    "OpenAI package not installed. "
                    "Install with: pip install openai"
                )
        return self._client

    def embed(self, text: str) -> EmbeddingResponse:
        """
        Generate embedding for a single text.

        Args:
            text: The text to embed.

        Returns:
            EmbeddingResponse with the vector and metadata.

        Raises:
            RuntimeError: If embedding generation fails.
            ValueError: If text is empty.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if not self.is_configured():
            raise RuntimeError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable."
            )

        try:
            client = self._get_client()
            response = client.embeddings.create(
                model=self._model,
                input=text,
            )

            embedding_data = response.data[0]
            usage = response.usage

            return EmbeddingResponse(
                vector=embedding_data.embedding,
                model=response.model,
                input_tokens=usage.total_tokens if usage else 0,
                dimensions=len(embedding_data.embedding),
                metadata={
                    "index": embedding_data.index,
                    "object": embedding_data.object,
                },
            )

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise RuntimeError(f"Embedding generation failed: {e}")

    def embed_batch(self, texts: list[str]) -> BatchEmbeddingResponse:
        """
        Generate embeddings for multiple texts.

        OpenAI API supports batch embedding for efficiency.

        Args:
            texts: List of texts to embed.

        Returns:
            BatchEmbeddingResponse with all embeddings.
        """
        if not texts:
            return BatchEmbeddingResponse(embeddings=[])

        if not self.is_configured():
            raise RuntimeError(
                "OpenAI API key not configured. "
                "Set OPENAI_API_KEY environment variable."
            )

        # Filter empty texts
        valid_texts = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")

        try:
            client = self._get_client()
            response = client.embeddings.create(
                model=self._model,
                input=[t for _, t in valid_texts],
            )

            embeddings = []
            for item in response.data:
                embeddings.append(
                    EmbeddingResponse(
                        vector=item.embedding,
                        model=response.model,
                        input_tokens=0,  # Per-item tokens not available in batch
                        dimensions=len(item.embedding),
                        metadata={"index": item.index},
                    )
                )

            return BatchEmbeddingResponse(
                embeddings=embeddings,
                total_tokens=response.usage.total_tokens if response.usage else 0,
                model=response.model,
            )

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise RuntimeError(f"Batch embedding generation failed: {e}")

    def get_cost_estimate(self, token_count: int) -> float:
        """
        Estimate cost for embedding tokens.

        Args:
            token_count: Number of tokens to embed.

        Returns:
            Estimated cost in USD.
        """
        config = OPENAI_EMBEDDING_MODELS.get(self._model, {})
        cost_per_1k = config.get("cost_per_1k", 0.0001)
        return (token_count / 1000) * cost_per_1k
