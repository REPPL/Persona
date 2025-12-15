"""
Source matching for claim verification.

This module provides functionality for matching claims to source data
using semantic embeddings and similarity scoring.
"""

import re
from typing import Any

from persona.core.embedding.base import EmbeddingProvider
from persona.core.quality.faithfulness.models import Claim, SourceMatch


class SourceMatcher:
    """
    Match claims to source data using semantic similarity.

    Uses embedding-based semantic search to find the most relevant
    source passages for each claim, determining if claims are supported.

    Example:
        matcher = SourceMatcher(embedding_provider, threshold=0.7)
        matches = matcher.match_claims(claims, source_data)
        for match in matches:
            if match.is_supported:
                print(f"Supported: {match.claim.text}")
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        support_threshold: float = 0.7,
        chunk_size: int = 200,
        chunk_overlap: int = 50,
    ) -> None:
        """
        Initialise the source matcher.

        Args:
            embedding_provider: Provider for generating embeddings.
            support_threshold: Minimum similarity score to consider supported (0-1).
            chunk_size: Number of words per source chunk.
            chunk_overlap: Number of words to overlap between chunks.
        """
        self.embedding_provider = embedding_provider
        self.support_threshold = support_threshold
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def match_claims(
        self,
        claims: list[Claim],
        source_data: str,
    ) -> list[SourceMatch]:
        """
        Match claims to source data.

        Args:
            claims: List of claims to verify.
            source_data: Source text to match against.

        Returns:
            List of SourceMatch objects with similarity scores.
        """
        # Split source into chunks
        chunks = self._chunk_text(source_data)

        if not chunks:
            # No source data - all claims unsupported
            return [
                SourceMatch(
                    claim=claim,
                    source_text="",
                    similarity_score=0.0,
                    is_supported=False,
                    evidence_type="unsupported",
                )
                for claim in claims
            ]

        # Embed all chunks (batch for efficiency)
        chunk_embeddings = self.embedding_provider.embed_batch(chunks)

        # Match each claim
        matches: list[SourceMatch] = []
        for claim in claims:
            match = self._match_single_claim(claim, chunks, chunk_embeddings)
            matches.append(match)

        return matches

    def _match_single_claim(
        self,
        claim: Claim,
        chunks: list[str],
        chunk_embeddings: Any,
    ) -> SourceMatch:
        """
        Match a single claim to source chunks.

        Args:
            claim: The claim to match.
            chunks: Source text chunks.
            chunk_embeddings: Embeddings for all chunks.

        Returns:
            SourceMatch with best matching chunk.
        """
        # Embed the claim
        claim_embedding = self.embedding_provider.embed(claim.text)

        # Find best matching chunk
        best_score = 0.0
        best_chunk = ""
        best_idx = 0

        for idx, chunk_emb in enumerate(chunk_embeddings.embeddings):
            score = claim_embedding.cosine_similarity(chunk_emb)
            if score > best_score:
                best_score = score
                best_chunk = chunks[idx]
                best_idx = idx

        # Determine if supported
        is_supported = best_score >= self.support_threshold

        # Determine evidence type
        evidence_type = self._classify_evidence_type(best_score)

        return SourceMatch(
            claim=claim,
            source_text=best_chunk,
            similarity_score=best_score,
            is_supported=is_supported,
            evidence_type=evidence_type,
        )

    def _chunk_text(self, text: str) -> list[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Source text to chunk.

        Returns:
            List of text chunks.
        """
        if not text or not text.strip():
            return []

        # Split into sentences first for better chunk boundaries
        sentences = self._split_sentences(text)

        # Combine sentences into chunks
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_word_count = 0

        for sentence in sentences:
            word_count = len(sentence.split())

            # If adding this sentence would exceed chunk size
            if current_word_count + word_count > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(" ".join(current_chunk))

                # Start new chunk with overlap
                # Keep last few sentences for overlap
                overlap_sentences: list[str] = []
                overlap_words = 0
                for s in reversed(current_chunk):
                    overlap_words += len(s.split())
                    overlap_sentences.insert(0, s)
                    if overlap_words >= self.chunk_overlap:
                        break

                current_chunk = overlap_sentences
                current_word_count = overlap_words

            current_chunk.append(sentence)
            current_word_count += word_count

        # Add final chunk
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """
        Split text into sentences.

        Args:
            text: Text to split.

        Returns:
            List of sentences.
        """
        # Simple sentence splitting (good enough for this purpose)
        # Split on common sentence endings
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _classify_evidence_type(self, similarity_score: float) -> str:
        """
        Classify the type of evidence based on similarity score.

        Args:
            similarity_score: Similarity score (0-1).

        Returns:
            Evidence type classification.
        """
        if similarity_score >= 0.85:
            return "direct"
        elif similarity_score >= self.support_threshold:
            return "inferred"
        else:
            return "unsupported"

    def get_unsupported_claims(self, matches: list[SourceMatch]) -> list[Claim]:
        """
        Extract unsupported claims from matches.

        Args:
            matches: List of claim-source matches.

        Returns:
            List of claims that are not supported by source.
        """
        return [m.claim for m in matches if not m.is_supported]

    def calculate_faithfulness_metrics(
        self,
        matches: list[SourceMatch],
    ) -> dict[str, float]:
        """
        Calculate faithfulness metrics from matches.

        Args:
            matches: List of claim-source matches.

        Returns:
            Dictionary with faithfulness metrics.
        """
        if not matches:
            return {
                "supported_ratio": 0.0,
                "hallucination_ratio": 0.0,
                "average_similarity": 0.0,
                "direct_evidence_ratio": 0.0,
            }

        total = len(matches)
        supported = sum(1 for m in matches if m.is_supported)
        direct_evidence = sum(1 for m in matches if m.evidence_type == "direct")
        total_similarity = sum(m.similarity_score for m in matches)

        return {
            "supported_ratio": supported / total,
            "hallucination_ratio": (total - supported) / total,
            "average_similarity": total_similarity / total,
            "direct_evidence_ratio": direct_evidence / total,
        }
