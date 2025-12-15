"""
Bias and stereotype detection package.

This package provides comprehensive bias detection for personas using
multiple detection methods:

1. Lexicon-based: Pattern matching against HolisticBias vocabulary
2. Embedding-based: WEAT (Word Embedding Association Test) analysis
3. LLM-based: Judge model for subtle bias detection

Example:
    from persona.core.quality.bias import BiasDetector, BiasConfig

    config = BiasConfig(methods=["lexicon", "embedding"])
    detector = BiasDetector(config)
    report = detector.analyse(persona)

    if report.overall_score > 0.3:
        print(f"Warning: Potential bias detected")
        for finding in report.findings:
            print(f"  {finding.category}: {finding.description}")
"""

from persona.core.quality.bias.detector import BiasDetector
from persona.core.quality.bias.embedding import EMBEDDING_AVAILABLE, EmbeddingAnalyser
from persona.core.quality.bias.judge import BiasJudge
from persona.core.quality.bias.lexicon import LexiconMatcher
from persona.core.quality.bias.models import (
    BiasCategory,
    BiasConfig,
    BiasFinding,
    BiasReport,
    Severity,
)

__all__ = [
    "BiasCategory",
    "BiasConfig",
    "BiasDetector",
    "BiasFinding",
    "BiasJudge",
    "BiasReport",
    "EmbeddingAnalyser",
    "EMBEDDING_AVAILABLE",
    "LexiconMatcher",
    "Severity",
]
