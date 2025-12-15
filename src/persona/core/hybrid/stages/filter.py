"""
Filter stage: Evaluate persona quality using PersonaJudge.

This stage uses PersonaJudge to evaluate generated personas and separate
high-quality personas from those that need refinement.
"""

from typing import Any, Dict, List, Tuple

from persona.core.evaluation.criteria import EvaluationCriteria
from persona.core.evaluation.judge import PersonaJudge
from persona.core.hybrid.config import HybridConfig
from persona.core.hybrid.cost import CostTracker


async def filter_personas(
    personas: List[Dict[str, Any]],
    config: HybridConfig,
    cost_tracker: CostTracker,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filter personas based on quality threshold.

    Uses PersonaJudge to evaluate each persona and separates them into
    high-quality (passing threshold) and low-quality (needs refinement).

    Args:
        personas: List of persona dictionaries to evaluate.
        config: Hybrid pipeline configuration.
        cost_tracker: Cost tracker for recording token usage.

    Returns:
        Tuple of (passing_personas, needs_refinement_personas).
        - passing_personas: Personas that meet quality threshold
        - needs_refinement_personas: Personas that need frontier refinement

    Example:
        passing, needs_work = await filter_personas(
            personas=drafts,
            config=config,
            cost_tracker=tracker
        )
    """
    if not personas:
        return [], []

    # If no frontier provider, all personas pass (local-only mode)
    if not config.is_hybrid_mode:
        return personas, []

    # Create judge
    judge = PersonaJudge(
        provider=config.judge_provider,
        model=config.judge_model,
        temperature=0.0,  # Consistent scoring
    )

    # Evaluate personas
    criteria = [
        EvaluationCriteria.COHERENCE,
        EvaluationCriteria.REALISM,
        EvaluationCriteria.USEFULNESS,
    ]

    passing_personas = []
    needs_refinement = []

    for persona in personas:
        try:
            # Evaluate individual persona
            result = judge.evaluate(persona, criteria=criteria)

            # Track token usage
            if result.raw_response:
                # Estimate token usage from response
                # (Actual tracking would require provider-specific logic)
                estimated_input = len(str(persona)) // 4  # Rough estimate
                estimated_output = len(str(result.to_dict())) // 4
                cost_tracker.add_judge_usage(estimated_input, estimated_output)

            # Store evaluation result in persona
            persona["_evaluation"] = result.to_dict()

            # Check if passes threshold
            if result.overall_score >= config.quality_threshold:
                passing_personas.append(persona)
            else:
                needs_refinement.append(persona)

        except Exception as e:
            # On evaluation error, mark for refinement to be safe
            persona["_evaluation_error"] = str(e)
            needs_refinement.append(persona)

    return passing_personas, needs_refinement


def get_evaluation_score(persona: Dict[str, Any]) -> float:
    """
    Get evaluation score from persona metadata.

    Args:
        persona: Persona dictionary with evaluation metadata.

    Returns:
        Overall quality score (0.0-1.0), or 0.0 if not evaluated.
    """
    if "_evaluation" not in persona:
        return 0.0

    evaluation = persona["_evaluation"]
    return evaluation.get("overall_score", 0.0)


def get_evaluation_feedback(persona: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract evaluation feedback for refinement.

    Args:
        persona: Persona dictionary with evaluation metadata.

    Returns:
        Dictionary mapping criterion to reasoning.
    """
    if "_evaluation" not in persona:
        return {}

    evaluation = persona["_evaluation"]
    scores = evaluation.get("scores", {})

    feedback = {}
    for criterion, score_data in scores.items():
        if isinstance(score_data, dict):
            reasoning = score_data.get("reasoning", "")
            if reasoning:
                feedback[criterion] = reasoning

    return feedback
