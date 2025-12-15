"""
Embedding providers for semantic analysis.

This package provides embedding generation for use in quality metrics,
faithfulness validation, and semantic similarity calculations.
"""

from persona.core.embedding.base import (
    BatchEmbeddingResponse,
    EmbeddingProvider,
    EmbeddingResponse,
)
from persona.core.embedding.factory import (
    EmbeddingFactory,
    get_embedding_provider,
)

__all__ = [
    "BatchEmbeddingResponse",
    "EmbeddingFactory",
    "EmbeddingProvider",
    "EmbeddingResponse",
    "get_embedding_provider",
]
