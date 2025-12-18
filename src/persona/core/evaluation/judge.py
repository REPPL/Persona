"""
LLM-based persona quality judge.

This module provides the PersonaJudge class that uses local or cloud
LLMs to evaluate persona quality across multiple criteria.
"""

import json
from typing import Any

from persona.core.evaluation.criteria import DEFAULT_CRITERIA, EvaluationCriteria
from persona.core.evaluation.models import (
    BatchEvaluationResult,
    CriterionScore,
    EvaluationResult,
)
from persona.core.evaluation.prompts import (
    EVALUATION_SYSTEM_PROMPT,
    build_batch_evaluation_prompt,
    build_single_evaluation_prompt,
)
from persona.core.providers import ProviderFactory


class PersonaJudge:
    """
    LLM-based judge for evaluating persona quality.

    Uses an LLM to assess personas across multiple quality criteria,
    providing scores and reasoning for each criterion.

    Example:
        judge = PersonaJudge(provider="ollama", model="qwen2.5:72b")
        result = judge.evaluate(persona, criteria=[
            EvaluationCriteria.COHERENCE,
            EvaluationCriteria.REALISM,
        ])
    """

    def __init__(
        self,
        provider: str = "ollama",
        model: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        """
        Initialise the persona judge.

        Args:
            provider: LLM provider to use (default: "ollama").
            model: Model name to use (default: provider's default).
            temperature: Sampling temperature (default: 0.0 for consistent scoring).
        """
        self.provider_name = provider
        self.provider = ProviderFactory.create(provider)
        self.model = model or self.provider.default_model
        self.temperature = temperature

    def evaluate(
        self,
        persona: dict[str, Any],
        criteria: list[EvaluationCriteria] | None = None,
    ) -> EvaluationResult:
        """
        Evaluate a single persona.

        Args:
            persona: Persona data to evaluate.
            criteria: Criteria to evaluate (default: COHERENCE, REALISM, USEFULNESS).

        Returns:
            Evaluation result with scores and reasoning.

        Raises:
            ValueError: If persona is missing required fields or if criteria
                       includes DISTINCTIVENESS (use evaluate_batch instead).
        """
        if not persona:
            raise ValueError("Persona data is required")

        if "id" not in persona:
            raise ValueError("Persona must have an 'id' field")

        criteria = criteria or DEFAULT_CRITERIA

        # Check for batch-only criteria
        batch_criteria = [c for c in criteria if c.requires_batch]
        if batch_criteria:
            raise ValueError(
                f"Criteria {[c.value for c in batch_criteria]} require batch "
                f"evaluation. Use evaluate_batch() instead."
            )

        # Build prompt
        prompt = build_single_evaluation_prompt(persona, criteria)

        # Call LLM
        response = self.provider.generate(
            prompt=prompt,
            model=self.model,
            temperature=self.temperature,
            system_prompt=EVALUATION_SYSTEM_PROMPT,
        )

        # Parse response
        scores = self._parse_evaluation_response(response.content, criteria)

        # Calculate overall score
        overall_score = sum(s.score for s in scores.values()) / len(scores)

        return EvaluationResult(
            persona_id=persona["id"],
            persona_name=persona.get("name"),
            scores=scores,
            overall_score=overall_score,
            model=self.model,
            provider=self.provider_name,
            raw_response=response.raw_response,
        )

    def evaluate_batch(
        self,
        personas: list[dict[str, Any]],
        criteria: list[EvaluationCriteria] | None = None,
    ) -> BatchEvaluationResult:
        """
        Evaluate multiple personas.

        If criteria includes DISTINCTIVENESS, personas are evaluated
        together with awareness of the full set. Otherwise, each persona
        is evaluated independently.

        Args:
            personas: List of persona data to evaluate.
            criteria: Criteria to evaluate (default: COHERENCE, REALISM, USEFULNESS).

        Returns:
            Batch evaluation result with individual and aggregate scores.

        Raises:
            ValueError: If personas list is empty or personas are missing required fields.
        """
        if not personas:
            raise ValueError("At least one persona is required")

        for i, persona in enumerate(personas):
            if "id" not in persona:
                raise ValueError(f"Persona at index {i} is missing 'id' field")

        criteria = criteria or DEFAULT_CRITERIA

        # Check if we need batch context
        requires_batch_context = any(c.requires_batch for c in criteria)

        if requires_batch_context:
            results = self._evaluate_batch_with_context(personas, criteria)
        else:
            # Evaluate each persona independently
            results = [self.evaluate(p, criteria) for p in personas]

        # Calculate aggregates
        average_overall = sum(r.overall_score for r in results) / len(results)

        average_by_criterion = {}
        for criterion in criteria:
            scores = [r.get_score(criterion) for r in results]
            scores = [s for s in scores if s is not None]
            if scores:
                average_by_criterion[criterion] = sum(scores) / len(scores)

        return BatchEvaluationResult(
            results=results,
            average_overall=average_overall,
            average_by_criterion=average_by_criterion,
            model=self.model,
            provider=self.provider_name,
        )

    def _evaluate_batch_with_context(
        self,
        personas: list[dict[str, Any]],
        criteria: list[EvaluationCriteria],
    ) -> list[EvaluationResult]:
        """
        Evaluate personas with batch context (for DISTINCTIVENESS).

        Args:
            personas: List of persona data to evaluate.
            criteria: Criteria to evaluate.

        Returns:
            List of evaluation results.
        """
        # Build batch prompt
        prompts = build_batch_evaluation_prompt(personas, criteria)
        prompt = prompts[0]  # Batch prompt is a single prompt with all personas

        # Call LLM
        response = self.provider.generate(
            prompt=prompt,
            model=self.model,
            temperature=self.temperature,
            system_prompt=EVALUATION_SYSTEM_PROMPT,
        )

        # Parse batch response
        results = self._parse_batch_evaluation_response(
            response.content, personas, criteria
        )

        return results

    def _parse_evaluation_response(
        self,
        content: str,
        criteria: list[EvaluationCriteria],
    ) -> dict[EvaluationCriteria, CriterionScore]:
        """
        Parse LLM response into criterion scores.

        Args:
            content: LLM response content.
            criteria: Expected criteria.

        Returns:
            Dictionary of criterion scores.

        Raises:
            ValueError: If response cannot be parsed.
        """
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```"):
                # Find first { and last }
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1:
                    content = content[start : end + 1]

            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}\n{content}")

        # Parse scores
        scores = {}
        for criterion in criteria:
            criterion_key = criterion.value
            if criterion_key not in data:
                raise ValueError(f"Missing criterion '{criterion_key}' in response")

            criterion_data = data[criterion_key]
            if not isinstance(criterion_data, dict):
                raise ValueError(f"Invalid format for criterion '{criterion_key}'")

            if "score" not in criterion_data:
                raise ValueError(f"Missing 'score' for criterion '{criterion_key}'")

            if "reasoning" not in criterion_data:
                raise ValueError(f"Missing 'reasoning' for criterion '{criterion_key}'")

            score = float(criterion_data["score"])
            reasoning = str(criterion_data["reasoning"])

            scores[criterion] = CriterionScore(score=score, reasoning=reasoning)

        return scores

    def _parse_batch_evaluation_response(
        self,
        content: str,
        personas: list[dict[str, Any]],
        criteria: list[EvaluationCriteria],
    ) -> list[EvaluationResult]:
        """
        Parse batch LLM response into evaluation results.

        Args:
            content: LLM response content.
            personas: Original persona data.
            criteria: Expected criteria.

        Returns:
            List of evaluation results.

        Raises:
            ValueError: If response cannot be parsed.
        """
        # Try to extract JSON from response
        try:
            content = content.strip()
            if content.startswith("```"):
                # Find first [ and last ]
                start = content.find("[")
                end = content.rfind("]")
                if start != -1 and end != -1:
                    content = content[start : end + 1]

            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse batch LLM response as JSON: {e}")

        if not isinstance(data, list):
            raise ValueError("Batch response must be a JSON array")

        if len(data) != len(personas):
            raise ValueError(f"Expected {len(personas)} evaluations, got {len(data)}")

        # Parse each evaluation
        results = []
        for eval_data, persona in zip(data, personas):
            if "persona_id" not in eval_data:
                raise ValueError("Missing 'persona_id' in batch evaluation")

            if "scores" not in eval_data:
                raise ValueError("Missing 'scores' in batch evaluation")

            # Parse scores
            scores = {}
            for criterion in criteria:
                criterion_key = criterion.value
                if criterion_key not in eval_data["scores"]:
                    raise ValueError(
                        f"Missing criterion '{criterion_key}' in batch evaluation"
                    )

                criterion_data = eval_data["scores"][criterion_key]
                score = float(criterion_data["score"])
                reasoning = str(criterion_data["reasoning"])

                scores[criterion] = CriterionScore(score=score, reasoning=reasoning)

            # Calculate overall score
            overall_score = sum(s.score for s in scores.values()) / len(scores)

            results.append(
                EvaluationResult(
                    persona_id=persona["id"],
                    persona_name=persona.get("name"),
                    scores=scores,
                    overall_score=overall_score,
                    model=self.model,
                    provider=self.provider_name,
                )
            )

        return results
