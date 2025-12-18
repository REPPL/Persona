"""Tests for academic validation models."""

import pytest
from persona.core.quality.academic.models import (
    AcademicValidationReport,
    BatchAcademicValidationReport,
    BertScore,
    GevalScore,
    GptSimilarityScore,
    RougeScore,
)


class TestRougeScore:
    """Tests for RougeScore model."""

    def test_creation(self):
        """Test creating a ROUGE score."""
        score = RougeScore(precision=0.8, recall=0.7, fmeasure=0.75)
        assert score.precision == 0.8
        assert score.recall == 0.7
        assert score.fmeasure == 0.75

    def test_to_dict(self):
        """Test converting ROUGE score to dict."""
        score = RougeScore(precision=0.8, recall=0.7, fmeasure=0.75)
        result = score.to_dict()
        assert result["precision"] == 0.8
        assert result["recall"] == 0.7
        assert result["fmeasure"] == 0.75


class TestBertScore:
    """Tests for BertScore model."""

    def test_creation(self):
        """Test creating a BERT score."""
        score = BertScore(
            precision=0.85,
            recall=0.82,
            f1=0.835,
            model="microsoft/deberta-xlarge-mnli",
        )
        assert score.precision == 0.85
        assert score.recall == 0.82
        assert score.f1 == 0.835
        assert score.model == "microsoft/deberta-xlarge-mnli"

    def test_to_dict(self):
        """Test converting BERT score to dict."""
        score = BertScore(precision=0.85, recall=0.82, f1=0.835)
        result = score.to_dict()
        assert result["precision"] == 0.85
        assert result["f1"] == 0.835
        assert "model" in result


class TestGptSimilarityScore:
    """Tests for GptSimilarityScore model."""

    def test_creation(self):
        """Test creating a GPT similarity score."""
        score = GptSimilarityScore(
            similarity=0.92,
            embedding_model="text-embedding-3-small",
            persona_dimensions=1536,
            source_dimensions=1536,
        )
        assert score.similarity == 0.92
        assert score.embedding_model == "text-embedding-3-small"
        assert score.persona_dimensions == 1536

    def test_to_dict(self):
        """Test converting GPT similarity score to dict."""
        score = GptSimilarityScore(
            similarity=0.92, embedding_model="text-embedding-3-small"
        )
        result = score.to_dict()
        assert result["similarity"] == 0.92
        assert result["embedding_model"] == "text-embedding-3-small"


class TestGevalScore:
    """Tests for GevalScore model."""

    def test_creation(self):
        """Test creating a G-eval score."""
        score = GevalScore(
            coherence=85.0,
            relevance=80.0,
            fluency=90.0,
            consistency=85.0,
            overall=85.0,
            model="qwen2.5:72b",
            reasoning={"coherence": "Well structured"},
        )
        assert score.coherence == 85.0
        assert score.overall == 85.0
        assert score.model == "qwen2.5:72b"
        assert "coherence" in score.reasoning

    def test_to_dict(self):
        """Test converting G-eval score to dict."""
        score = GevalScore(
            coherence=85.0,
            relevance=80.0,
            fluency=90.0,
            consistency=85.0,
            overall=85.0,
            model="qwen2.5:72b",
        )
        result = score.to_dict()
        assert result["coherence"] == 85.0
        assert result["overall"] == 85.0
        assert result["model"] == "qwen2.5:72b"


class TestAcademicValidationReport:
    """Tests for AcademicValidationReport model."""

    def test_creation_with_all_metrics(self):
        """Test creating a report with all metrics."""
        rouge = RougeScore(precision=0.8, recall=0.7, fmeasure=0.75)
        bert = BertScore(precision=0.85, recall=0.82, f1=0.835)
        gpt = GptSimilarityScore(similarity=0.92, embedding_model="test")
        geval = GevalScore(
            coherence=85.0,
            relevance=80.0,
            fluency=90.0,
            consistency=85.0,
            overall=85.0,
            model="test",
        )

        report = AcademicValidationReport(
            persona_id="p1",
            persona_name="Test Persona",
            rouge_l=rouge,
            bertscore=bert,
            gpt_similarity=gpt,
            geval=geval,
        )

        assert report.persona_id == "p1"
        assert report.persona_name == "Test Persona"
        assert report.has_rouge_l
        assert report.has_bertscore
        assert report.has_gpt_similarity
        assert report.has_geval
        assert len(report.metrics_used) == 4

    def test_overall_score_calculation(self):
        """Test automatic overall score calculation."""
        rouge = RougeScore(precision=0.8, recall=0.7, fmeasure=0.75)  # 75/100
        bert = BertScore(precision=0.85, recall=0.82, f1=0.835)  # 83.5/100

        report = AcademicValidationReport(
            persona_id="p1",
            persona_name="Test Persona",
            rouge_l=rouge,
            bertscore=bert,
        )

        # Should be average of 75 and 83.5 = 79.25
        assert report.overall_score == pytest.approx(79.25, rel=0.01)

    def test_selective_metrics(self):
        """Test report with only some metrics."""
        rouge = RougeScore(precision=0.8, recall=0.7, fmeasure=0.75)

        report = AcademicValidationReport(
            persona_id="p1", persona_name="Test Persona", rouge_l=rouge
        )

        assert report.has_rouge_l
        assert not report.has_bertscore
        assert not report.has_gpt_similarity
        assert not report.has_geval
        assert len(report.metrics_used) == 1

    def test_to_dict(self):
        """Test converting report to dict."""
        rouge = RougeScore(precision=0.8, recall=0.7, fmeasure=0.75)

        report = AcademicValidationReport(
            persona_id="p1", persona_name="Test Persona", rouge_l=rouge
        )

        result = report.to_dict()
        assert result["persona_id"] == "p1"
        assert result["persona_name"] == "Test Persona"
        assert "rouge_l" in result
        assert "overall_score" in result
        assert "generated_at" in result


class TestBatchAcademicValidationReport:
    """Tests for BatchAcademicValidationReport model."""

    def test_creation(self):
        """Test creating a batch report."""
        report1 = AcademicValidationReport(
            persona_id="p1",
            persona_name="Persona 1",
            rouge_l=RougeScore(precision=0.8, recall=0.7, fmeasure=0.75),
        )
        report2 = AcademicValidationReport(
            persona_id="p2",
            persona_name="Persona 2",
            rouge_l=RougeScore(precision=0.6, recall=0.5, fmeasure=0.55),
        )

        batch = BatchAcademicValidationReport(reports=[report1, report2])

        assert batch.persona_count == 2
        assert batch.average_rouge_l == pytest.approx(0.65, rel=0.01)  # (0.75+0.55)/2

    def test_average_calculation(self):
        """Test average score calculation across all metrics."""
        report1 = AcademicValidationReport(
            persona_id="p1",
            persona_name="Persona 1",
            rouge_l=RougeScore(precision=0.8, recall=0.7, fmeasure=0.75),
            bertscore=BertScore(precision=0.85, recall=0.82, f1=0.835),
        )
        report2 = AcademicValidationReport(
            persona_id="p2",
            persona_name="Persona 2",
            rouge_l=RougeScore(precision=0.6, recall=0.5, fmeasure=0.55),
            bertscore=BertScore(precision=0.7, recall=0.65, f1=0.675),
        )

        batch = BatchAcademicValidationReport(reports=[report1, report2])

        # ROUGE-L average: (0.75 + 0.55) / 2 = 0.65
        assert batch.average_rouge_l == pytest.approx(0.65, rel=0.01)
        # BERTScore average: (0.835 + 0.675) / 2 = 0.755
        assert batch.average_bertscore == pytest.approx(0.755, rel=0.01)

    def test_to_dict(self):
        """Test converting batch report to dict."""
        report1 = AcademicValidationReport(
            persona_id="p1",
            persona_name="Persona 1",
            rouge_l=RougeScore(precision=0.8, recall=0.7, fmeasure=0.75),
        )

        batch = BatchAcademicValidationReport(reports=[report1])

        result = batch.to_dict()
        assert result["persona_count"] == 1
        assert "average_overall" in result
        assert "individual_reports" in result
        assert len(result["individual_reports"]) == 1
