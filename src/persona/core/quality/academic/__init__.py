"""
Academic validation metrics for persona quality assessment.

This package provides research-grade validation metrics including:
- ROUGE-L: Surface-level text similarity
- BERTScore: Semantic similarity using contextual embeddings
- GPT Similarity: High-level semantic similarity using embeddings
- G-eval: LLM-based multi-dimensional quality assessment

Example:
    from persona.core.quality.academic import validate_persona

    report = validate_persona(
        persona=my_persona,
        source_data=research_text,
        metrics=["rouge_l", "bertscore", "geval"],
    )
    print(f"Overall academic score: {report.overall_score:.2f}")
"""

from persona.core.quality.academic.bertscore import BertScoreMetric
from persona.core.quality.academic.geval import GevalMetric
from persona.core.quality.academic.gpt_similarity import GptSimilarityMetric
from persona.core.quality.academic.models import (
    AcademicValidationReport,
    BatchAcademicValidationReport,
    BertScore,
    GevalScore,
    GptSimilarityScore,
    RougeScore,
)
from persona.core.quality.academic.rouge import RougeLMetric
from persona.core.quality.academic.validator import (
    AcademicValidator,
    validate_persona,
    validate_personas,
)

__all__ = [
    # Metrics
    "RougeLMetric",
    "BertScoreMetric",
    "GptSimilarityMetric",
    "GevalMetric",
    # Models
    "RougeScore",
    "BertScore",
    "GptSimilarityScore",
    "GevalScore",
    "AcademicValidationReport",
    "BatchAcademicValidationReport",
    # Validator
    "AcademicValidator",
    "validate_persona",
    "validate_personas",
]
