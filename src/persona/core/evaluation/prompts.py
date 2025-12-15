"""
Prompt templates for LLM-based persona evaluation.

This module provides the prompts used by LLM judges to evaluate
persona quality across different criteria.
"""

import json
from typing import Any

from persona.core.evaluation.criteria import EvaluationCriteria


EVALUATION_SYSTEM_PROMPT = """You are an expert in user experience research and persona development. Your task is to evaluate the quality of user personas objectively and consistently.

When evaluating personas, consider:
- **Coherence**: Do all attributes fit together logically?
- **Realism**: Are the details believable and plausible?
- **Usefulness**: Would this help designers make better decisions?
- **Completeness**: Are all important attributes covered?
- **Specificity**: Are details concrete rather than generic?

Provide scores from 0.0 to 1.0 where:
- 0.9-1.0: Exceptional quality
- 0.7-0.89: Good quality
- 0.5-0.69: Acceptable but needs improvement
- 0.3-0.49: Poor quality with significant issues
- 0.0-0.29: Failing, unusable

Be objective and consistent in your evaluation."""


def build_single_evaluation_prompt(
    persona: dict[str, Any],
    criteria: list[EvaluationCriteria],
) -> str:
    """
    Build prompt for evaluating a single persona.

    Args:
        persona: Persona data to evaluate.
        criteria: List of criteria to evaluate.

    Returns:
        Evaluation prompt for the LLM.
    """
    persona_json = json.dumps(persona, indent=2)

    # Build criteria descriptions
    criteria_lines = []
    for i, criterion in enumerate(criteria, 1):
        criteria_lines.append(f"{i}. **{criterion.value.upper()}**: {criterion.description}")

    criteria_text = "\n".join(criteria_lines)

    # Build expected JSON structure
    json_structure = {
        criterion.value: {
            "score": "0.0-1.0",
            "reasoning": "Brief explanation",
        }
        for criterion in criteria
    }
    json_example = json.dumps(json_structure, indent=2)

    prompt = f"""Evaluate the following user persona:

```json
{persona_json}
```

Evaluate on these criteria:
{criteria_text}

Respond in JSON format with the following structure:
```json
{json_example}
```

Provide objective scores and brief reasoning for each criterion."""

    return prompt


def build_batch_evaluation_prompt(
    personas: list[dict[str, Any]],
    criteria: list[EvaluationCriteria],
) -> list[str]:
    """
    Build prompts for evaluating multiple personas.

    For batch evaluation with DISTINCTIVENESS criterion, we need to
    provide context about all personas. Otherwise, we can evaluate
    each persona independently.

    Args:
        personas: List of persona data to evaluate.
        criteria: List of criteria to evaluate.

    Returns:
        List of evaluation prompts (one per persona if no batch context needed,
        or single prompt if batch context required).
    """
    # Check if any criterion requires batch context
    requires_batch_context = any(c.requires_batch for c in criteria)

    if not requires_batch_context:
        # Evaluate each persona independently
        return [build_single_evaluation_prompt(p, criteria) for p in personas]

    # Build batch evaluation prompt with all personas for context
    personas_json = json.dumps(personas, indent=2)

    # Build criteria descriptions
    criteria_lines = []
    for i, criterion in enumerate(criteria, 1):
        criteria_lines.append(f"{i}. **{criterion.value.upper()}**: {criterion.description}")

    criteria_text = "\n".join(criteria_lines)

    # Build expected JSON structure for all personas
    json_structure = [
        {
            "persona_id": "ID from persona data",
            "scores": {
                criterion.value: {
                    "score": "0.0-1.0",
                    "reasoning": "Brief explanation",
                }
                for criterion in criteria
            },
        }
        for _ in range(len(personas))
    ]
    json_example = json.dumps(json_structure, indent=2)

    prompt = f"""Evaluate the following set of {len(personas)} user personas:

```json
{personas_json}
```

Evaluate each persona on these criteria:
{criteria_text}

For **DISTINCTIVENESS**, compare each persona against the others in the set to assess uniqueness.

Respond in JSON format with an array containing evaluation for each persona:
```json
{json_example}
```

Provide objective scores and brief reasoning for each criterion. Ensure persona_id matches the ID from the input data."""

    return [prompt]


def build_distinctiveness_prompt(
    persona: dict[str, Any],
    other_personas: list[dict[str, Any]],
) -> str:
    """
    Build prompt for evaluating distinctiveness of a persona against others.

    This is used when evaluating distinctiveness separately from other criteria.

    Args:
        persona: The persona to evaluate.
        other_personas: Other personas to compare against.

    Returns:
        Distinctiveness evaluation prompt.
    """
    persona_json = json.dumps(persona, indent=2)
    others_json = json.dumps(other_personas, indent=2)

    prompt = f"""Evaluate how distinct and unique this persona is compared to the other personas in the set.

**Target Persona:**
```json
{persona_json}
```

**Other Personas in Set:**
```json
{others_json}
```

Evaluate **DISTINCTIVENESS**: Is this persona meaningfully different from the others?

Consider:
- Do they have different goals and motivations?
- Are their behaviours and patterns distinct?
- Do they represent different user types?
- Are the differences meaningful for design decisions?

Respond in JSON format:
```json
{{
  "distinctiveness": {{
    "score": "0.0-1.0",
    "reasoning": "Brief explanation of what makes this persona unique or similar"
  }}
}}
```

Score guidelines:
- 0.9-1.0: Highly distinct with clear unique characteristics
- 0.7-0.89: Reasonably distinct with some unique aspects
- 0.5-0.69: Some overlap but still differentiable
- 0.3-0.49: Significant overlap, minimal uniqueness
- 0.0-0.29: Nearly identical to other personas"""

    return prompt
