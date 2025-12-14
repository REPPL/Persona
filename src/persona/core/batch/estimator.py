"""
Persona count estimation (F-065).

Estimates optimal persona count based on data analysis.
"""

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EstimationFactors:
    """
    Factors used in persona count estimation.
    
    Records the inputs to the estimation algorithm.
    """
    
    total_tokens: int = 0
    file_count: int = 0
    theme_count: int = 0
    unique_keywords: int = 0
    avg_tokens_per_file: float = 0.0
    data_richness_score: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_tokens": self.total_tokens,
            "file_count": self.file_count,
            "theme_count": self.theme_count,
            "unique_keywords": self.unique_keywords,
            "avg_tokens_per_file": round(self.avg_tokens_per_file, 0),
            "data_richness_score": round(self.data_richness_score, 2),
        }


@dataclass
class CountEstimate:
    """
    Persona count estimation result.
    
    Provides recommended count with confidence and reasoning.
    """
    
    recommended: int
    min_count: int
    max_count: int
    confidence: float  # 0.0 to 1.0
    reasoning: str
    factors: EstimationFactors = field(default_factory=EstimationFactors)
    
    @property
    def range(self) -> tuple[int, int]:
        """Get recommended range as tuple."""
        return (self.min_count, self.max_count)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "recommended": self.recommended,
            "min": self.min_count,
            "max": self.max_count,
            "confidence": round(self.confidence, 2),
            "reasoning": self.reasoning,
            "factors": self.factors.to_dict(),
        }
    
    def to_display(self) -> str:
        """Generate display-friendly output."""
        lines = [
            "Persona Count Estimation",
            "",
            "Data Analysis:",
            f"  - Files: {self.factors.file_count}",
            f"  - Total tokens: {self.factors.total_tokens:,}",
            f"  - Identified themes: {self.factors.theme_count}",
            "",
            f"Recommendation: {self.min_count}-{self.max_count} personas",
            "",
            "Reasoning:",
            f"  {self.reasoning}",
        ]
        return "\n".join(lines)


class PersonaEstimator:
    """
    Estimates optimal persona count from data.
    
    Analyses data volume, diversity, and richness to suggest
    an appropriate number of personas to generate.
    
    Example:
        >>> estimator = PersonaEstimator()
        >>> estimate = estimator.estimate(
        ...     content="...",
        ...     file_count=10,
        ...     token_count=50000,
        ... )
        >>> print(f"Recommend {estimate.min_count}-{estimate.max_count} personas")
    """
    
    # Heuristics
    TOKENS_PER_RICH_PERSONA = 7500  # Target tokens backing each persona
    MIN_TOKENS_PER_PERSONA = 3000   # Minimum for thin persona
    MAX_PERSONAS_DEFAULT = 10       # Default maximum
    
    def __init__(
        self,
        tokens_per_persona: int = 7500,
        min_personas: int = 2,
        max_personas: int = 10,
    ):
        """
        Initialise the estimator.
        
        Args:
            tokens_per_persona: Target tokens per persona.
            min_personas: Minimum personas to recommend.
            max_personas: Maximum personas to recommend.
        """
        self._tokens_per_persona = tokens_per_persona
        self._min_personas = min_personas
        self._max_personas = max_personas
    
    def estimate(
        self,
        content: str | None = None,
        file_count: int = 1,
        token_count: int | None = None,
        token_counter: Any | None = None,
    ) -> CountEstimate:
        """
        Estimate optimal persona count.
        
        Args:
            content: Combined text content from data files.
            file_count: Number of source files.
            token_count: Pre-calculated token count.
            token_counter: TokenCounter for counting.
        
        Returns:
            CountEstimate with recommendation.
        """
        # Calculate tokens
        if token_count is None and content:
            if token_counter:
                token_count = token_counter.count_tokens(content)
            else:
                # Rough estimate: ~4 chars per token
                token_count = len(content) // 4
        token_count = token_count or 0
        
        # Extract themes
        themes = self._extract_themes(content or "")
        theme_count = len(themes)
        
        # Calculate factors
        factors = EstimationFactors(
            total_tokens=token_count,
            file_count=file_count,
            theme_count=theme_count,
            unique_keywords=len(set(themes)),
            avg_tokens_per_file=token_count / file_count if file_count > 0 else 0,
            data_richness_score=self._calculate_richness(content or ""),
        )
        
        # Estimate based on tokens
        token_based = max(1, token_count // self._tokens_per_persona)
        
        # Estimate based on themes
        theme_based = max(1, theme_count)
        
        # Source-based ceiling
        source_ceiling = file_count
        
        # Combine estimates
        recommended = min(token_based, theme_based, source_ceiling, self._max_personas)
        recommended = max(recommended, self._min_personas)
        
        # Calculate range
        min_count = max(self._min_personas, recommended - 2)
        max_count = min(self._max_personas, recommended + 2, source_ceiling)
        
        # Ensure valid range
        if min_count > max_count:
            min_count = max_count
        
        # Calculate confidence
        confidence = self._calculate_confidence(factors)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(factors, recommended)
        
        return CountEstimate(
            recommended=recommended,
            min_count=min_count,
            max_count=max_count,
            confidence=confidence,
            reasoning=reasoning,
            factors=factors,
        )
    
    def estimate_from_files(
        self,
        paths: list[Path],
        token_counter: Any | None = None,
    ) -> CountEstimate:
        """
        Estimate from file paths.
        
        Args:
            paths: List of data file paths.
            token_counter: Optional token counter.
        
        Returns:
            CountEstimate with recommendation.
        """
        # Combine content
        content_parts = []
        for path in paths:
            if path.exists() and path.is_file():
                try:
                    content_parts.append(path.read_text(encoding="utf-8"))
                except Exception:
                    pass
        
        combined = "\n\n".join(content_parts)
        
        return self.estimate(
            content=combined,
            file_count=len(paths),
            token_counter=token_counter,
        )
    
    def _extract_themes(self, content: str) -> list[str]:
        """
        Extract themes from content using simple keyword analysis.
        
        Returns list of identified theme keywords.
        """
        if not content:
            return []
        
        # Convert to lowercase and extract words
        words = re.findall(r"\b[a-z]{4,}\b", content.lower())
        
        # Count word frequencies
        word_counts = Counter(words)
        
        # Filter stopwords and get top themes
        stopwords = {
            "that", "this", "with", "from", "have", "been", "were", "they",
            "their", "what", "when", "where", "which", "would", "could",
            "should", "there", "these", "those", "about", "into", "your",
            "more", "some", "very", "just", "only", "other", "such", "than",
            "then", "also", "like", "much", "well", "even", "most", "each",
        }
        
        themes = [
            word for word, count in word_counts.most_common(50)
            if word not in stopwords and count >= 3
        ]
        
        return themes[:10]  # Top 10 themes
    
    def _calculate_richness(self, content: str) -> float:
        """
        Calculate data richness score (0.0 to 1.0).
        
        Higher scores indicate more diverse, detailed content.
        """
        if not content:
            return 0.0
        
        # Factors contributing to richness
        word_count = len(content.split())
        unique_words = len(set(content.lower().split()))
        
        # Lexical diversity
        diversity = unique_words / word_count if word_count > 0 else 0
        
        # Length factor (more content = potentially richer)
        length_score = min(1.0, word_count / 5000)
        
        # Combine factors
        richness = (diversity * 0.4) + (length_score * 0.6)
        return min(1.0, richness)
    
    def _calculate_confidence(self, factors: EstimationFactors) -> float:
        """Calculate confidence in the estimate."""
        confidence = 0.5  # Base confidence
        
        # More tokens = higher confidence
        if factors.total_tokens > 50000:
            confidence += 0.2
        elif factors.total_tokens > 20000:
            confidence += 0.1
        
        # More files = higher confidence
        if factors.file_count >= 5:
            confidence += 0.1
        
        # Clear themes = higher confidence
        if factors.theme_count >= 3:
            confidence += 0.1
        
        # Good richness = higher confidence
        if factors.data_richness_score >= 0.5:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_reasoning(
        self,
        factors: EstimationFactors,
        recommended: int,
    ) -> str:
        """Generate human-readable reasoning."""
        tokens_per = factors.total_tokens // recommended if recommended > 0 else 0
        
        parts = []
        
        if factors.theme_count > 0:
            parts.append(
                f"Your data contains content across ~{factors.theme_count} distinct themes."
            )
        
        parts.append(
            f"With {factors.total_tokens:,} tokens, each persona can be well-supported "
            f"with ~{tokens_per:,} tokens of backing data."
        )
        
        if recommended >= self._max_personas:
            parts.append(
                f"Generating more than {self._max_personas} personas may result in "
                f"thin personas with overlapping characteristics."
            )
        
        return " ".join(parts)


def estimate_personas(
    content: str,
    file_count: int = 1,
) -> CountEstimate:
    """
    Convenience function to estimate persona count.
    
    Args:
        content: Data content.
        file_count: Number of source files.
    
    Returns:
        CountEstimate with recommendation.
    """
    estimator = PersonaEstimator()
    return estimator.estimate(content=content, file_count=file_count)
