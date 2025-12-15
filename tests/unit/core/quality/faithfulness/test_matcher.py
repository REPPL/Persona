"""Tests for source matcher."""

from unittest.mock import Mock

import pytest

from persona.core.embedding.base import (
    BatchEmbeddingResponse,
    EmbeddingProvider,
    EmbeddingResponse,
)
from persona.core.quality.faithfulness.matcher import SourceMatcher
from persona.core.quality.faithfulness.models import Claim, ClaimType


class MockEmbeddingProvider(EmbeddingProvider):
    """Mock embedding provider for testing."""

    def __init__(self):
        self._embeddings = {}

    @property
    def name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return "mock-model"

    @property
    def dimension(self) -> int:
        return 3

    def is_configured(self) -> bool:
        return True

    def embed(self, text: str) -> EmbeddingResponse:
        # Simple mock: use text hash as embedding
        # For testing, we'll use predictable vectors
        if "25 years old" in text.lower() or "age: 25" in text.lower():
            vector = [0.9, 0.1, 0.0]
        elif "hiking" in text.lower():
            vector = [0.1, 0.9, 0.0]
        elif "teacher" in text.lower():
            vector = [0.0, 0.1, 0.9]
        else:
            vector = [0.3, 0.3, 0.3]

        return EmbeddingResponse(
            vector=vector,
            model=self.model,
            dimensions=self.dimension,
        )

    def embed_batch(self, texts: list[str]) -> BatchEmbeddingResponse:
        embeddings = [self.embed(text) for text in texts]
        return BatchEmbeddingResponse(embeddings=embeddings)


class TestSourceMatcher:
    """Tests for SourceMatcher."""

    def test_matcher_initialization(self):
        """Test matcher initialization with parameters."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(
            embedding_provider,
            support_threshold=0.7,
            chunk_size=200,
            chunk_overlap=50,
        )

        assert matcher.embedding_provider == embedding_provider
        assert matcher.support_threshold == 0.7
        assert matcher.chunk_size == 200
        assert matcher.chunk_overlap == 50

    def test_chunk_text_simple(self):
        """Test simple text chunking."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider, chunk_size=20, chunk_overlap=10)

        text = "This is a test. " * 30  # 150 words
        chunks = matcher._chunk_text(text)

        assert len(chunks) > 1
        # Each chunk should be around chunk_size + overlap
        for chunk in chunks:
            word_count = len(chunk.split())
            # Allow up to chunk_size + overlap + some tolerance
            assert word_count <= 35

    def test_chunk_text_empty(self):
        """Test chunking empty text."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider)

        chunks = matcher._chunk_text("")
        assert len(chunks) == 0

        chunks = matcher._chunk_text("   ")
        assert len(chunks) == 0

    def test_split_sentences(self):
        """Test sentence splitting."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider)

        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        sentences = matcher._split_sentences(text)

        assert len(sentences) == 4
        assert sentences[0] == "First sentence."
        assert sentences[1] == "Second sentence!"
        assert sentences[2] == "Third sentence?"
        assert sentences[3] == "Fourth sentence."

    def test_classify_evidence_type(self):
        """Test evidence type classification."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider, support_threshold=0.7)

        # Direct evidence (very high similarity)
        assert matcher._classify_evidence_type(0.95) == "direct"
        assert matcher._classify_evidence_type(0.85) == "direct"

        # Inferred evidence (above threshold but not direct)
        assert matcher._classify_evidence_type(0.75) == "inferred"
        assert matcher._classify_evidence_type(0.7) == "inferred"

        # Unsupported (below threshold)
        assert matcher._classify_evidence_type(0.65) == "unsupported"
        assert matcher._classify_evidence_type(0.3) == "unsupported"

    def test_match_claims_no_source(self):
        """Test matching with empty source data."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider)

        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        matches = matcher.match_claims([claim], "")

        assert len(matches) == 1
        assert matches[0].is_supported is False
        assert matches[0].similarity_score == 0.0
        assert matches[0].evidence_type == "unsupported"

    def test_match_claims_with_source(self):
        """Test matching claims to source data."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider, support_threshold=0.7)

        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        source_data = "The respondent is 25 years old and works as a teacher."

        matches = matcher.match_claims([claim], source_data)

        assert len(matches) == 1
        # Should find good match due to mock embedding similarity
        assert matches[0].similarity_score > 0.7
        assert matches[0].is_supported is True

    def test_match_multiple_claims(self):
        """Test matching multiple claims."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider, support_threshold=0.7)

        claim1 = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )
        claim2 = Claim(
            text="User likes hiking",
            source_field="preferences",
            claim_type=ClaimType.PREFERENCE,
        )

        source_data = "Respondent age: 25. No hobbies mentioned."

        matches = matcher.match_claims([claim1, claim2], source_data)

        assert len(matches) == 2
        # First claim should match well
        assert matches[0].similarity_score > 0.5
        # Second claim should match less well
        assert matches[1].similarity_score < matches[0].similarity_score

    def test_get_unsupported_claims(self):
        """Test extracting unsupported claims from matches."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider)

        claim1 = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )
        claim2 = Claim(
            text="User likes hiking",
            source_field="preferences",
            claim_type=ClaimType.PREFERENCE,
        )

        from persona.core.quality.faithfulness.models import SourceMatch

        match1 = SourceMatch(
            claim=claim1,
            source_text="Age: 25",
            similarity_score=0.9,
            is_supported=True,
        )
        match2 = SourceMatch(
            claim=claim2,
            source_text="No data",
            similarity_score=0.2,
            is_supported=False,
        )

        unsupported = matcher.get_unsupported_claims([match1, match2])

        assert len(unsupported) == 1
        assert unsupported[0] == claim2

    def test_calculate_faithfulness_metrics_empty(self):
        """Test metric calculation with no matches."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider)

        metrics = matcher.calculate_faithfulness_metrics([])

        assert metrics["supported_ratio"] == 0.0
        assert metrics["hallucination_ratio"] == 0.0
        assert metrics["average_similarity"] == 0.0
        assert metrics["direct_evidence_ratio"] == 0.0

    def test_calculate_faithfulness_metrics(self):
        """Test metric calculation with matches."""
        from persona.core.quality.faithfulness.models import Claim, SourceMatch

        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider)

        claim1 = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )
        claim2 = Claim(
            text="User likes hiking",
            source_field="preferences",
            claim_type=ClaimType.PREFERENCE,
        )
        claim3 = Claim(
            text="User is a teacher",
            source_field="demographics.occupation",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        match1 = SourceMatch(
            claim=claim1,
            source_text="Age: 25",
            similarity_score=0.95,
            is_supported=True,
            evidence_type="direct",
        )
        match2 = SourceMatch(
            claim=claim2,
            source_text="No data",
            similarity_score=0.2,
            is_supported=False,
            evidence_type="unsupported",
        )
        match3 = SourceMatch(
            claim=claim3,
            source_text="Teacher mentioned",
            similarity_score=0.75,
            is_supported=True,
            evidence_type="inferred",
        )

        metrics = matcher.calculate_faithfulness_metrics([match1, match2, match3])

        # 2 out of 3 supported
        assert metrics["supported_ratio"] == pytest.approx(2 / 3)
        assert metrics["hallucination_ratio"] == pytest.approx(1 / 3)
        # Average similarity
        assert metrics["average_similarity"] == pytest.approx((0.95 + 0.2 + 0.75) / 3)
        # 1 out of 3 direct
        assert metrics["direct_evidence_ratio"] == pytest.approx(1 / 3)

    def test_match_single_claim(self):
        """Test matching a single claim to chunks."""
        embedding_provider = MockEmbeddingProvider()
        matcher = SourceMatcher(embedding_provider, support_threshold=0.7)

        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        chunks = ["Age: 25 years", "Works as teacher", "Likes hiking"]
        chunk_embeddings = embedding_provider.embed_batch(chunks)

        match = matcher._match_single_claim(claim, chunks, chunk_embeddings)

        assert match.claim == claim
        assert match.similarity_score > 0.0
        # Should match best to first chunk
        assert "Age: 25" in match.source_text
