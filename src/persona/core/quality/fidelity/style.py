"""
Style validation using LLM-as-Judge.

This module uses an LLM to evaluate whether the generated persona
adheres to style requirements like tone, detail level, and voice.
"""

import json

from persona.core.generation.parser import Persona
from persona.core.quality.fidelity.models import (
    FidelityConfig,
    PromptConstraints,
    Severity,
    Violation,
)


class StyleChecker:
    """
    Check style adherence using LLM-as-Judge.

    Uses an LLM to evaluate qualitative aspects like tone, voice,
    and detail level that are difficult to assess programmatically.
    """

    def __init__(self, config: FidelityConfig):
        """
        Initialise the style checker.

        Args:
            config: Fidelity configuration with LLM settings.
        """
        self.config = config

    def check(
        self,
        persona: Persona,
        constraints: PromptConstraints,
        original_prompt: str | None = None,
    ) -> tuple[float, list[Violation]]:
        """
        Check style adherence.

        Args:
            persona: Persona to check.
            constraints: Style constraints.
            original_prompt: Original prompt text for context (optional).

        Returns:
            Tuple of (score 0-1, list of violations).
        """
        # If LLM judge is disabled, skip style checking
        if not self.config.use_llm_judge:
            return self._simple_style_check(persona, constraints)

        # If no style requirements, return perfect score
        if not constraints.style and not constraints.custom_rules:
            return 1.0, []

        # Use LLM to evaluate style
        try:
            return self._llm_style_check(persona, constraints, original_prompt)
        except Exception:
            # Fall back to simple check if LLM fails
            return self._simple_style_check(persona, constraints)

    def _simple_style_check(
        self, persona: Persona, constraints: PromptConstraints
    ) -> tuple[float, list[Violation]]:
        """
        Simple rule-based style checking without LLM.

        Checks basic style indicators like complexity level.
        """
        violations: list[Violation] = []

        # Check complexity by word count heuristics
        if constraints.complexity:
            complexity_violations = self._check_complexity(persona, constraints)
            violations.extend(complexity_violations)

        # Calculate score
        if not violations:
            return 1.0, violations

        # Penalise but don't fail completely
        score = max(0.5, 1.0 - (len(violations) * 0.2))
        return score, violations

    def _check_complexity(
        self, persona: Persona, constraints: PromptConstraints
    ) -> list[Violation]:
        """Check if complexity level matches expectation."""
        violations: list[Violation] = []

        complexity = constraints.complexity
        if not complexity:
            return violations

        # Calculate average field length as complexity proxy
        total_words = 0
        field_count = 0

        for field in [persona.goals, persona.pain_points, persona.behaviours]:
            if field:
                for item in field:
                    total_words += len(str(item).split())
                    field_count += 1

        if field_count == 0:
            return violations

        avg_words = total_words / field_count

        # Thresholds for complexity
        complexity_thresholds = {
            "simple": (0, 8),  # Short, concise entries
            "detailed": (8, 20),  # Medium-length entries
            "comprehensive": (15, 100),  # Long, detailed entries
        }

        if complexity.lower() in complexity_thresholds:
            min_words, max_words = complexity_thresholds[complexity.lower()]

            if avg_words < min_words:
                violations.append(
                    Violation(
                        dimension="style",
                        field=None,
                        description=f"Content is too brief for '{complexity}' complexity",
                        severity=Severity.MEDIUM,
                        expected=f"{complexity} style ({min_words}+ words per entry)",
                        actual=f"{avg_words:.1f} words per entry",
                    )
                )
            elif avg_words > max_words and complexity.lower() == "simple":
                violations.append(
                    Violation(
                        dimension="style",
                        field=None,
                        description=f"Content is too verbose for '{complexity}' complexity",
                        severity=Severity.LOW,
                        expected=f"{complexity} style (≤{max_words} words per entry)",
                        actual=f"{avg_words:.1f} words per entry",
                    )
                )

        return violations

    def _llm_style_check(
        self,
        persona: Persona,
        constraints: PromptConstraints,
        original_prompt: str | None,
    ) -> tuple[float, list[Violation]]:
        """
        Use LLM to evaluate style adherence.

        This is a placeholder for actual LLM integration.
        In production, this would call the LLM API with a carefully crafted prompt.
        """
        violations: list[Violation] = []

        # Build evaluation prompt
        eval_prompt = self._build_evaluation_prompt(
            persona, constraints, original_prompt
        )

        # TODO: Call LLM API here
        # For now, fall back to simple check
        # In production, this would:
        # 1. Call LLM with eval_prompt
        # 2. Parse structured response (JSON)
        # 3. Extract violations and score
        # 4. Return results

        # Example of what LLM response parsing might look like:
        # response = llm_client.generate(eval_prompt)
        # result = json.loads(response)
        # score = result['score']
        # for issue in result['violations']:
        #     violations.append(Violation(...))

        return self._simple_style_check(persona, constraints)

    def _build_evaluation_prompt(
        self,
        persona: Persona,
        constraints: PromptConstraints,
        original_prompt: str | None,
    ) -> str:
        """
        Build LLM evaluation prompt.

        Args:
            persona: Persona to evaluate.
            constraints: Style constraints.
            original_prompt: Original prompt for context.

        Returns:
            Formatted prompt for LLM evaluation.
        """
        persona_json = json.dumps(persona.to_dict(), indent=2)

        prompt = """You are evaluating whether a generated persona adheres to style requirements.

# Style Requirements

"""

        if constraints.style:
            prompt += f"**Tone/Style**: {constraints.style}\n"

        if constraints.complexity:
            prompt += f"**Complexity Level**: {constraints.complexity}\n"

        if constraints.custom_rules:
            prompt += "\n**Custom Rules**:\n"
            for rule in constraints.custom_rules:
                prompt += f"- {rule}\n"

        if original_prompt:
            prompt += f"\n**Original Prompt**:\n{original_prompt}\n"

        prompt += f"""
# Generated Persona

{persona_json}

# Evaluation Task

Evaluate whether the persona adheres to the style requirements.
Provide your assessment as JSON with the following structure:

{{
    "score": <float between 0.0 and 1.0>,
    "violations": [
        {{
            "description": "<what style requirement was violated>",
            "severity": "<critical|high|medium|low>",
            "expected": "<what was expected>",
            "actual": "<what was observed>"
        }}
    ],
    "reasoning": "<brief explanation of your evaluation>"
}}

Respond ONLY with valid JSON, no additional text.
"""

        return prompt
