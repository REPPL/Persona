"""
Data models for academic validation metrics.

This module provides data structures for representing results from
academic validation metrics like ROUGE-L, BERTScore, and G-eval.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RougeScore:
    """
    ROUGE-L score result.

    Attributes:
        precision: ROUGE-L precision (0-1).
        recall: ROUGE-L recall (0-1).
        fmeasure: ROUGE-L F-measure (0-1).
    """

    precision: float
    recall: float
    fmeasure: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "fmeasure": round(self.fmeasure, 4),
        }


@dataclass
class BertScore:
    """
    BERTScore result.

    Attributes:
        precision: BERTScore precision (0-1).
        recall: BERTScore recall (0-1).
        f1: BERTScore F1 (0-1).
        model: Model used for BERTScore.
    """

    precision: float
    recall: float
    f1: float
    model: str = "microsoft/deberta-xlarge-mnli"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "model": self.model,
        }


@dataclass
class GptSimilarityScore:
    """
    GPT embedding similarity score.

    Attributes:
        similarity: Cosine similarity (0-1).
        embedding_model: Model used for embeddings.
        persona_dimensions: Dimensionality of persona embedding.
        source_dimensions: Dimensionality of source embedding.
    """

    similarity: float
    embedding_model: str
    persona_dimensions: int = 0
    source_dimensions: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "similarity": round(self.similarity, 4),
            "embedding_model": self.embedding_model,
            "persona_dimensions": self.persona_dimensions,
            "source_dimensions": self.source_dimensions,
        }


@dataclass
class GevalScore:
    """
    G-eval (LLM-as-judge) score.

    Attributes:
        coherence: Coherence score (0-100).
        relevance: Relevance score (0-100).
        fluency: Fluency score (0-100).
        consistency: Consistency score (0-100).
        overall: Overall score (0-100).
        model: LLM model used for evaluation.
        reasoning: Detailed reasoning from the judge.
    """

    coherence: float
    relevance: float
    fluency: float
    consistency: float
    overall: float
    model: str
    reasoning: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "coherence": round(self.coherence, 2),
            "relevance": round(self.relevance, 2),
            "fluency": round(self.fluency, 2),
            "consistency": round(self.consistency, 2),
            "overall": round(self.overall, 2),
            "model": self.model,
            "reasoning": self.reasoning,
        }


@dataclass
class AcademicValidationReport:
    """
    Complete academic validation report for a persona.

    This report combines multiple academic validation metrics to provide
    a comprehensive assessment of persona quality according to research standards.

    Attributes:
        persona_id: ID of the validated persona.
        persona_name: Name of the validated persona.
        rouge_l: ROUGE-L scores (if computed).
        bertscore: BERTScore scores (if computed).
        gpt_similarity: GPT embedding similarity (if computed).
        geval: G-eval scores (if computed).
        overall_score: Aggregate score across all metrics (0-100).
        metrics_used: List of metrics that were computed.
        generated_at: Timestamp of validation.
    """

    persona_id: str
    persona_name: str
    rouge_l: RougeScore | None = None
    bertscore: BertScore | None = None
    gpt_similarity: GptSimilarityScore | None = None
    geval: GevalScore | None = None
    overall_score: float = 0.0
    metrics_used: list[str] = field(default_factory=list)
    generated_at: str = ""

    def __post_init__(self) -> None:
        """Set generated_at timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

        # Calculate overall score if metrics exist
        if not self.metrics_used:
            self.metrics_used = []
            if self.rouge_l:
                self.metrics_used.append("rouge_l")
            if self.bertscore:
                self.metrics_used.append("bertscore")
            if self.gpt_similarity:
                self.metrics_used.append("gpt_similarity")
            if self.geval:
                self.metrics_used.append("geval")

        if self.overall_score == 0.0 and self.metrics_used:
            self._calculate_overall_score()

    def _calculate_overall_score(self) -> None:
        """Calculate aggregate score across all computed metrics."""
        scores = []

        # ROUGE-L contributes F-measure scaled to 0-100
        if self.rouge_l:
            scores.append(self.rouge_l.fmeasure * 100)

        # BERTScore contributes F1 scaled to 0-100
        if self.bertscore:
            scores.append(self.bertscore.f1 * 100)

        # GPT similarity contributes similarity scaled to 0-100
        if self.gpt_similarity:
            scores.append(self.gpt_similarity.similarity * 100)

        # G-eval contributes overall score directly
        if self.geval:
            scores.append(self.geval.overall)

        # Average all available scores
        if scores:
            self.overall_score = sum(scores) / len(scores)

    @property
    def has_rouge_l(self) -> bool:
        """Check if ROUGE-L was computed."""
        return self.rouge_l is not None

    @property
    def has_bertscore(self) -> bool:
        """Check if BERTScore was computed."""
        return self.bertscore is not None

    @property
    def has_gpt_similarity(self) -> bool:
        """Check if GPT similarity was computed."""
        return self.gpt_similarity is not None

    @property
    def has_geval(self) -> bool:
        """Check if G-eval was computed."""
        return self.geval is not None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        result = {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "overall_score": round(self.overall_score, 2),
            "metrics_used": self.metrics_used,
            "generated_at": self.generated_at,
        }

        if self.rouge_l:
            result["rouge_l"] = self.rouge_l.to_dict()
        if self.bertscore:
            result["bertscore"] = self.bertscore.to_dict()
        if self.gpt_similarity:
            result["gpt_similarity"] = self.gpt_similarity.to_dict()
        if self.geval:
            result["geval"] = self.geval.to_dict()

        return result


@dataclass
class BatchAcademicValidationReport:
    """
    Academic validation results for multiple personas.

    Attributes:
        reports: Individual validation reports.
        average_overall: Average overall score.
        average_rouge_l: Average ROUGE-L F-measure.
        average_bertscore: Average BERTScore F1.
        average_gpt_similarity: Average GPT similarity.
        average_geval: Average G-eval overall score.
        generated_at: Timestamp of validation.
    """

    reports: list[AcademicValidationReport]
    average_overall: float = 0.0
    average_rouge_l: float = 0.0
    average_bertscore: float = 0.0
    average_gpt_similarity: float = 0.0
    average_geval: float = 0.0
    generated_at: str = ""

    def __post_init__(self) -> None:
        """Calculate averages and set timestamp."""
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

        if self.reports:
            self._calculate_averages()

    def _calculate_averages(self) -> None:
        """Calculate average scores across all reports."""
        # Overall average
        self.average_overall = sum(r.overall_score for r in self.reports) / len(
            self.reports
        )

        # ROUGE-L average
        rouge_scores = [r.rouge_l.fmeasure for r in self.reports if r.rouge_l]
        if rouge_scores:
            self.average_rouge_l = sum(rouge_scores) / len(rouge_scores)

        # BERTScore average
        bert_scores = [r.bertscore.f1 for r in self.reports if r.bertscore]
        if bert_scores:
            self.average_bertscore = sum(bert_scores) / len(bert_scores)

        # GPT similarity average
        gpt_scores = [
            r.gpt_similarity.similarity for r in self.reports if r.gpt_similarity
        ]
        if gpt_scores:
            self.average_gpt_similarity = sum(gpt_scores) / len(gpt_scores)

        # G-eval average
        geval_scores = [r.geval.overall for r in self.reports if r.geval]
        if geval_scores:
            self.average_geval = sum(geval_scores) / len(geval_scores)

    @property
    def persona_count(self) -> int:
        """Get number of personas validated."""
        return len(self.reports)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_count": self.persona_count,
            "average_overall": round(self.average_overall, 2),
            "average_rouge_l": round(self.average_rouge_l, 4),
            "average_bertscore": round(self.average_bertscore, 4),
            "average_gpt_similarity": round(self.average_gpt_similarity, 4),
            "average_geval": round(self.average_geval, 2),
            "individual_reports": [r.to_dict() for r in self.reports],
            "generated_at": self.generated_at,
        }
