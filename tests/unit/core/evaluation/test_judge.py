"""
Unit tests for PersonaJudge.
"""

import json
import pytest
from unittest.mock import Mock, patch

from persona.core.evaluation.criteria import EvaluationCriteria
from persona.core.evaluation.judge import PersonaJudge
from persona.core.evaluation.models import EvaluationResult, BatchEvaluationResult
from persona.core.providers.base import LLMResponse


class TestPersonaJudge:
    """Test PersonaJudge class."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider."""
        provider = Mock()
        provider.default_model = "test-model"
        return provider

    @pytest.fixture
    def sample_persona(self):
        """Create a sample persona for testing."""
        return {
            "id": "p1",
            "name": "Test Persona",
            "age": 35,
            "role": "Software Developer",
            "goals": ["Build great products", "Learn new technologies"],
        }

    @pytest.fixture
    def sample_llm_response(self):
        """Create a sample LLM response."""
        response_data = {
            "coherence": {
                "score": 0.85,
                "reasoning": "Attributes fit together well",
            },
            "realism": {
                "score": 0.78,
                "reasoning": "Believable character",
            },
            "usefulness": {
                "score": 0.92,
                "reasoning": "Would help design decisions",
            },
        }
        return LLMResponse(
            content=json.dumps(response_data),
            model="test-model",
            input_tokens=100,
            output_tokens=50,
            finish_reason="stop",
        )

    def test_create_judge(self, mock_provider):
        """Test creating a PersonaJudge."""
        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider
            judge = PersonaJudge(provider="ollama", model="qwen2.5:72b")

            assert judge.provider_name == "ollama"
            assert judge.model == "qwen2.5:72b"
            assert judge.temperature == 0.0

    def test_create_judge_default_model(self, mock_provider):
        """Test creating judge with default model."""
        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider
            judge = PersonaJudge(provider="ollama")

            assert judge.model == "test-model"  # From mock provider

    def test_evaluate_single_persona(
        self, mock_provider, sample_persona, sample_llm_response
    ):
        """Test evaluating a single persona."""
        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider
            mock_provider.generate.return_value = sample_llm_response

            judge = PersonaJudge(provider="ollama")
            result = judge.evaluate(
                sample_persona,
                criteria=[
                    EvaluationCriteria.COHERENCE,
                    EvaluationCriteria.REALISM,
                    EvaluationCriteria.USEFULNESS,
                ],
            )

            assert isinstance(result, EvaluationResult)
            assert result.persona_id == "p1"
            assert result.persona_name == "Test Persona"
            assert len(result.scores) == 3
            assert result.get_score(EvaluationCriteria.COHERENCE) == 0.85
            assert result.get_score(EvaluationCriteria.REALISM) == 0.78
            assert result.get_score(EvaluationCriteria.USEFULNESS) == 0.92

            # Check overall score calculation
            expected_overall = (0.85 + 0.78 + 0.92) / 3
            assert abs(result.overall_score - expected_overall) < 0.01

    def test_evaluate_missing_id(self, mock_provider):
        """Test that evaluating persona without ID raises error."""
        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider

            judge = PersonaJudge(provider="ollama")

            with pytest.raises(ValueError, match="id"):
                judge.evaluate({"name": "No ID"})

    def test_evaluate_with_distinctiveness_raises_error(
        self, mock_provider, sample_persona
    ):
        """Test that single evaluation with DISTINCTIVENESS raises error."""
        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider

            judge = PersonaJudge(provider="ollama")

            with pytest.raises(ValueError, match="batch"):
                judge.evaluate(
                    sample_persona,
                    criteria=[EvaluationCriteria.DISTINCTIVENESS],
                )

    def test_evaluate_batch(self, mock_provider, sample_llm_response):
        """Test evaluating multiple personas."""
        personas = [
            {"id": "p1", "name": "Persona 1"},
            {"id": "p2", "name": "Persona 2"},
        ]

        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider
            mock_provider.generate.return_value = sample_llm_response

            judge = PersonaJudge(provider="ollama")
            result = judge.evaluate_batch(
                personas,
                criteria=[
                    EvaluationCriteria.COHERENCE,
                    EvaluationCriteria.REALISM,
                    EvaluationCriteria.USEFULNESS,
                ],
            )

            assert isinstance(result, BatchEvaluationResult)
            assert result.persona_count == 2
            assert len(result.results) == 2

    def test_evaluate_batch_empty_list(self, mock_provider):
        """Test that evaluating empty list raises error."""
        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider

            judge = PersonaJudge(provider="ollama")

            with pytest.raises(ValueError, match="At least one"):
                judge.evaluate_batch([])

    def test_evaluate_batch_with_distinctiveness(self, mock_provider):
        """Test batch evaluation with distinctiveness criterion."""
        personas = [
            {"id": "p1", "name": "Persona 1"},
            {"id": "p2", "name": "Persona 2"},
        ]

        batch_response_data = [
            {
                "persona_id": "p1",
                "scores": {
                    "coherence": {"score": 0.85, "reasoning": "Good"},
                    "distinctiveness": {"score": 0.75, "reasoning": "Somewhat unique"},
                },
            },
            {
                "persona_id": "p2",
                "scores": {
                    "coherence": {"score": 0.80, "reasoning": "OK"},
                    "distinctiveness": {"score": 0.70, "reasoning": "Some overlap"},
                },
            },
        ]

        batch_response = LLMResponse(
            content=json.dumps(batch_response_data),
            model="test-model",
            input_tokens=200,
            output_tokens=100,
            finish_reason="stop",
        )

        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider
            mock_provider.generate.return_value = batch_response

            judge = PersonaJudge(provider="ollama")
            result = judge.evaluate_batch(
                personas,
                criteria=[
                    EvaluationCriteria.COHERENCE,
                    EvaluationCriteria.DISTINCTIVENESS,
                ],
            )

            assert result.persona_count == 2
            assert result.results[0].get_score(EvaluationCriteria.DISTINCTIVENESS) == 0.75
            assert result.results[1].get_score(EvaluationCriteria.DISTINCTIVENESS) == 0.70

    def test_parse_evaluation_response_with_markdown(self, mock_provider):
        """Test parsing response with markdown code blocks."""
        response_with_markdown = """```json
{
    "coherence": {
        "score": 0.85,
        "reasoning": "Good"
    }
}
```"""

        llm_response = LLMResponse(
            content=response_with_markdown,
            model="test-model",
            input_tokens=100,
            output_tokens=50,
            finish_reason="stop",
        )

        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider
            mock_provider.generate.return_value = llm_response

            judge = PersonaJudge(provider="ollama")
            result = judge.evaluate(
                {"id": "p1", "name": "Test"},
                criteria=[EvaluationCriteria.COHERENCE],
            )

            assert result.get_score(EvaluationCriteria.COHERENCE) == 0.85

    def test_parse_evaluation_response_invalid_json(self, mock_provider):
        """Test that invalid JSON raises error."""
        invalid_response = LLMResponse(
            content="This is not JSON",
            model="test-model",
            input_tokens=100,
            output_tokens=50,
            finish_reason="stop",
        )

        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider
            mock_provider.generate.return_value = invalid_response

            judge = PersonaJudge(provider="ollama")

            with pytest.raises(ValueError, match="parse"):
                judge.evaluate(
                    {"id": "p1", "name": "Test"},
                    criteria=[EvaluationCriteria.COHERENCE],
                )

    def test_parse_evaluation_response_missing_criterion(self, mock_provider):
        """Test that missing criterion in response raises error."""
        incomplete_response = LLMResponse(
            content=json.dumps({"coherence": {"score": 0.85, "reasoning": "Good"}}),
            model="test-model",
            input_tokens=100,
            output_tokens=50,
            finish_reason="stop",
        )

        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider
            mock_provider.generate.return_value = incomplete_response

            judge = PersonaJudge(provider="ollama")

            with pytest.raises(ValueError, match="Missing criterion"):
                judge.evaluate(
                    {"id": "p1", "name": "Test"},
                    criteria=[
                        EvaluationCriteria.COHERENCE,
                        EvaluationCriteria.REALISM,  # Missing
                    ],
                )

    def test_parse_evaluation_response_missing_score(self, mock_provider):
        """Test that missing score raises error."""
        bad_response = LLMResponse(
            content=json.dumps({"coherence": {"reasoning": "Good"}}),  # No score
            model="test-model",
            input_tokens=100,
            output_tokens=50,
            finish_reason="stop",
        )

        with patch("persona.core.evaluation.judge.ProviderFactory.create") as mock_factory:
            mock_factory.return_value = mock_provider
            mock_provider.generate.return_value = bad_response

            judge = PersonaJudge(provider="ollama")

            with pytest.raises(ValueError, match="score"):
                judge.evaluate(
                    {"id": "p1", "name": "Test"},
                    criteria=[EvaluationCriteria.COHERENCE],
                )
