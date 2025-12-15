"""Tests for embedding base classes."""

import pytest

from persona.core.embedding.base import (
    BatchEmbeddingResponse,
    EmbeddingProvider,
    EmbeddingResponse,
)


class ConcreteEmbeddingProvider(EmbeddingProvider):
    """Concrete implementation for testing."""

    def __init__(self, dimension: int = 768) -> None:
        self._dimension = dimension
        self._configured = True

    @property
    def name(self) -> str:
        return "test_provider"

    @property
    def model(self) -> str:
        return "test-model-v1"

    @property
    def dimension(self) -> int:
        return self._dimension

    def is_configured(self) -> bool:
        return self._configured

    def embed(self, text: str) -> EmbeddingResponse:
        if not text:
            raise ValueError("Text cannot be empty")
        # Generate mock embedding
        vector = [0.1] * self._dimension
        return EmbeddingResponse(
            vector=vector,
            model=self.model,
            input_tokens=len(text.split()),
            dimensions=self._dimension,
        )


class TestEmbeddingResponse:
    """Tests for EmbeddingResponse dataclass."""

    def test_response_creation(self):
        """Test creating an embedding response."""
        vector = [0.1, 0.2, 0.3]
        response = EmbeddingResponse(
            vector=vector,
            model="test-model",
            input_tokens=10,
        )

        assert response.vector == vector
        assert response.model == "test-model"
        assert response.input_tokens == 10
        assert response.dimensions == 3  # Auto-calculated

    def test_response_explicit_dimensions(self):
        """Test response with explicit dimensions."""
        response = EmbeddingResponse(
            vector=[0.1, 0.2, 0.3],
            model="test-model",
            dimensions=3,
        )

        assert response.dimensions == 3

    def test_cosine_similarity_same_vector(self):
        """Test cosine similarity with same vector."""
        response = EmbeddingResponse(
            vector=[1.0, 0.0, 0.0],
            model="test-model",
        )

        similarity = response.cosine_similarity(response)
        assert abs(similarity - 1.0) < 0.001

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity with orthogonal vectors."""
        response1 = EmbeddingResponse(
            vector=[1.0, 0.0, 0.0],
            model="test-model",
        )
        response2 = EmbeddingResponse(
            vector=[0.0, 1.0, 0.0],
            model="test-model",
        )

        similarity = response1.cosine_similarity(response2)
        assert abs(similarity) < 0.001

    def test_cosine_similarity_opposite(self):
        """Test cosine similarity with opposite vectors."""
        response1 = EmbeddingResponse(
            vector=[1.0, 0.0, 0.0],
            model="test-model",
        )
        response2 = EmbeddingResponse(
            vector=[-1.0, 0.0, 0.0],
            model="test-model",
        )

        similarity = response1.cosine_similarity(response2)
        assert abs(similarity + 1.0) < 0.001

    def test_cosine_similarity_dimension_mismatch(self):
        """Test cosine similarity raises on dimension mismatch."""
        response1 = EmbeddingResponse(
            vector=[1.0, 0.0],
            model="test-model",
        )
        response2 = EmbeddingResponse(
            vector=[1.0, 0.0, 0.0],
            model="test-model",
        )

        with pytest.raises(ValueError, match="Dimension mismatch"):
            response1.cosine_similarity(response2)

    def test_cosine_similarity_empty_vector(self):
        """Test cosine similarity with empty vectors."""
        response1 = EmbeddingResponse(
            vector=[],
            model="test-model",
        )
        response2 = EmbeddingResponse(
            vector=[],
            model="test-model",
        )

        similarity = response1.cosine_similarity(response2)
        assert similarity == 0.0

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector."""
        response1 = EmbeddingResponse(
            vector=[0.0, 0.0, 0.0],
            model="test-model",
        )
        response2 = EmbeddingResponse(
            vector=[1.0, 0.0, 0.0],
            model="test-model",
        )

        similarity = response1.cosine_similarity(response2)
        assert similarity == 0.0


class TestBatchEmbeddingResponse:
    """Tests for BatchEmbeddingResponse dataclass."""

    def test_batch_response_creation(self):
        """Test creating a batch response."""
        embeddings = [
            EmbeddingResponse(vector=[0.1], model="test", input_tokens=5),
            EmbeddingResponse(vector=[0.2], model="test", input_tokens=3),
        ]

        batch = BatchEmbeddingResponse(embeddings=embeddings)

        assert len(batch.embeddings) == 2
        assert batch.total_tokens == 8  # Auto-calculated
        assert batch.model == "test"  # From first embedding

    def test_batch_response_explicit_tokens(self):
        """Test batch response with explicit total tokens."""
        embeddings = [
            EmbeddingResponse(vector=[0.1], model="test", input_tokens=5),
        ]

        batch = BatchEmbeddingResponse(
            embeddings=embeddings,
            total_tokens=100,
        )

        assert batch.total_tokens == 100

    def test_batch_response_empty(self):
        """Test batch response with no embeddings."""
        batch = BatchEmbeddingResponse(embeddings=[])

        assert batch.total_tokens == 0
        assert batch.model == ""


class TestEmbeddingProvider:
    """Tests for EmbeddingProvider abstract base class."""

    def test_provider_instantiation(self):
        """Test that concrete provider can be instantiated."""
        provider = ConcreteEmbeddingProvider()
        assert provider.name == "test_provider"
        assert provider.model == "test-model-v1"
        assert provider.dimension == 768

    def test_provider_is_configured(self):
        """Test is_configured method."""
        provider = ConcreteEmbeddingProvider()
        assert provider.is_configured() is True

    def test_provider_embed(self):
        """Test embedding generation."""
        provider = ConcreteEmbeddingProvider(dimension=128)
        response = provider.embed("Hello, world!")

        assert isinstance(response, EmbeddingResponse)
        assert len(response.vector) == 128
        assert response.dimensions == 128
        assert response.model == "test-model-v1"

    def test_provider_embed_empty_raises(self):
        """Test that embedding empty text raises error."""
        provider = ConcreteEmbeddingProvider()

        with pytest.raises(ValueError):
            provider.embed("")

    def test_provider_embed_batch_default(self):
        """Test default batch embedding implementation."""
        provider = ConcreteEmbeddingProvider(dimension=64)
        texts = ["Hello", "World", "Test"]

        response = provider.embed_batch(texts)

        assert isinstance(response, BatchEmbeddingResponse)
        assert len(response.embeddings) == 3
        for emb in response.embeddings:
            assert len(emb.vector) == 64

    def test_provider_similarity(self):
        """Test similarity method."""
        provider = ConcreteEmbeddingProvider(dimension=3)

        # Mock embeddings produce same vectors, so similarity = 1
        similarity = provider.similarity("hello", "world")
        assert abs(similarity - 1.0) < 0.001

    def test_provider_repr(self):
        """Test string representation."""
        provider = ConcreteEmbeddingProvider()
        repr_str = repr(provider)

        assert "ConcreteEmbeddingProvider" in repr_str
        assert "test_provider" in repr_str
        assert "test-model-v1" in repr_str
