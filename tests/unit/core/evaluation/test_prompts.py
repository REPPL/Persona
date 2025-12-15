"""
Unit tests for evaluation prompts.
"""

import json

from persona.core.evaluation.criteria import EvaluationCriteria
from persona.core.evaluation.prompts import (
    EVALUATION_SYSTEM_PROMPT,
    build_single_evaluation_prompt,
    build_batch_evaluation_prompt,
    build_distinctiveness_prompt,
)


class TestPrompts:
    """Test prompt generation."""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined."""
        assert isinstance(EVALUATION_SYSTEM_PROMPT, str)
        assert len(EVALUATION_SYSTEM_PROMPT) > 0
        assert "coherence" in EVALUATION_SYSTEM_PROMPT.lower()
        assert "realism" in EVALUATION_SYSTEM_PROMPT.lower()

    def test_single_evaluation_prompt(self):
        """Test building single evaluation prompt."""
        persona = {
            "id": "p1",
            "name": "Test Persona",
            "age": 35,
            "role": "Developer",
        }
        criteria = [
            EvaluationCriteria.COHERENCE,
            EvaluationCriteria.REALISM,
        ]

        prompt = build_single_evaluation_prompt(persona, criteria)

        assert isinstance(prompt, str)
        assert "p1" in prompt
        assert "Test Persona" in prompt
        assert "COHERENCE" in prompt
        assert "REALISM" in prompt
        assert "JSON" in prompt

    def test_single_evaluation_prompt_structure(self):
        """Test that single evaluation prompt has expected structure."""
        persona = {"id": "p1", "name": "Test"}
        criteria = [EvaluationCriteria.COHERENCE]

        prompt = build_single_evaluation_prompt(persona, criteria)

        # Should contain persona data
        assert "p1" in prompt

        # Should contain criterion description
        assert "COHERENCE" in prompt

        # Should request JSON format
        assert "JSON" in prompt or "json" in prompt

    def test_batch_evaluation_prompt_no_distinctiveness(self):
        """Test batch prompt without distinctiveness (returns individual prompts)."""
        personas = [
            {"id": "p1", "name": "Persona 1"},
            {"id": "p2", "name": "Persona 2"},
        ]
        criteria = [
            EvaluationCriteria.COHERENCE,
            EvaluationCriteria.REALISM,
        ]

        prompts = build_batch_evaluation_prompt(personas, criteria)

        # Should return one prompt per persona
        assert isinstance(prompts, list)
        assert len(prompts) == 2
        assert "p1" in prompts[0]
        assert "p2" in prompts[1]

    def test_batch_evaluation_prompt_with_distinctiveness(self):
        """Test batch prompt with distinctiveness (returns single prompt)."""
        personas = [
            {"id": "p1", "name": "Persona 1"},
            {"id": "p2", "name": "Persona 2"},
        ]
        criteria = [
            EvaluationCriteria.COHERENCE,
            EvaluationCriteria.DISTINCTIVENESS,
        ]

        prompts = build_batch_evaluation_prompt(personas, criteria)

        # Should return single prompt with all personas
        assert isinstance(prompts, list)
        assert len(prompts) == 1
        assert "p1" in prompts[0]
        assert "p2" in prompts[0]
        assert "DISTINCTIVENESS" in prompts[0]

    def test_distinctiveness_prompt(self):
        """Test distinctiveness evaluation prompt."""
        persona = {"id": "p1", "name": "Target Persona"}
        others = [
            {"id": "p2", "name": "Other 1"},
            {"id": "p3", "name": "Other 2"},
        ]

        prompt = build_distinctiveness_prompt(persona, others)

        assert isinstance(prompt, str)
        assert "p1" in prompt
        assert "Target Persona" in prompt
        assert "p2" in prompt
        assert "p3" in prompt
        assert "DISTINCTIVENESS" in prompt
        assert "unique" in prompt.lower() or "distinct" in prompt.lower()

    def test_prompt_json_structure(self):
        """Test that prompts include valid JSON examples."""
        persona = {"id": "p1"}
        criteria = [EvaluationCriteria.COHERENCE]

        prompt = build_single_evaluation_prompt(persona, criteria)

        # Extract JSON example from prompt (rough check)
        assert "coherence" in prompt
        assert "score" in prompt
        assert "reasoning" in prompt
