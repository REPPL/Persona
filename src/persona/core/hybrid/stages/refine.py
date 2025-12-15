"""
Refine stage: Improve low-quality personas using frontier models.

This stage takes personas that didn't meet the quality threshold and
uses frontier models (Anthropic/OpenAI) to improve them based on
evaluation feedback.
"""

import json
from typing import Any, Dict, List

from persona.core.hybrid.config import HybridConfig
from persona.core.hybrid.cost import CostTracker
from persona.core.hybrid.stages.filter import get_evaluation_feedback
from persona.core.providers import ProviderFactory


async def refine_personas(
    personas: List[Dict[str, Any]],
    config: HybridConfig,
    cost_tracker: CostTracker,
) -> List[Dict[str, Any]]:
    """
    Refine personas using frontier model.

    Takes low-quality personas and improves them using a frontier model,
    incorporating evaluation feedback to address specific weaknesses.

    Args:
        personas: List of persona dictionaries to refine.
        config: Hybrid pipeline configuration.
        cost_tracker: Cost tracker for recording token usage.

    Returns:
        List of refined persona dictionaries.

    Example:
        refined = await refine_personas(
            personas=needs_work,
            config=config,
            cost_tracker=tracker
        )
    """
    if not personas:
        return []

    # Skip if no frontier provider configured
    if not config.frontier_provider or not config.frontier_model:
        return personas

    # Check budget before refining
    if cost_tracker.is_over_budget:
        # Return unrefined personas if over budget
        return personas

    # Create frontier provider
    provider = ProviderFactory.create(config.frontier_provider)

    if not provider.is_configured():
        raise RuntimeError(
            f"{config.frontier_provider} provider not configured. "
            f"Set the required API key environment variable."
        )

    refined_personas = []

    for persona in personas:
        # Check budget before each refinement
        if cost_tracker.is_over_budget:
            # Add remaining personas unrefined
            refined_personas.append(persona)
            continue

        # Build refinement prompt with feedback
        feedback = get_evaluation_feedback(persona)
        prompt = _build_refinement_prompt(persona, feedback)

        try:
            # Refine with frontier model
            response = await provider.generate_async(
                prompt=prompt,
                model=config.frontier_model,
                temperature=config.frontier_temperature,
                max_tokens=2048,
                system_prompt=_get_refinement_system_prompt(),
            )

            # Track costs
            cost_tracker.add_frontier_usage(
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
            )

            # Parse refined persona
            refined = _parse_refined_persona(response.content, persona)

            # Mark as refined
            refined["_refined"] = True
            refined["_original_id"] = persona.get("id", "unknown")

            refined_personas.append(refined)

        except Exception as e:
            # On error, keep original persona and mark error
            persona["_refinement_error"] = str(e)
            refined_personas.append(persona)

    return refined_personas


def _get_refinement_system_prompt() -> str:
    """Get system prompt for refinement."""
    return """You are an expert UX researcher specialising in creating realistic user personas.
Your task is to improve an existing persona based on specific feedback about its quality.

Focus on:
- Improving coherence: Ensure all details are consistent and make sense together
- Enhancing realism: Make the persona more believable and grounded in reality
- Increasing usefulness: Add actionable details that help with design decisions

CRITICAL: Return only valid JSON, no additional text."""


def _build_refinement_prompt(
    persona: Dict[str, Any],
    feedback: Dict[str, str],
) -> str:
    """Build prompt for persona refinement."""
    prompt_parts = [
        "Improve the following persona based on the evaluation feedback below.",
        "",
        "# Original Persona",
        "",
        json.dumps(persona, indent=2),
        "",
    ]

    if feedback:
        prompt_parts.extend([
            "# Evaluation Feedback",
            "",
        ])
        for criterion, reasoning in feedback.items():
            prompt_parts.append(f"**{criterion}**: {reasoning}")
        prompt_parts.append("")

    prompt_parts.extend([
        "# Instructions",
        "",
        "Improve this persona by:",
        "1. Addressing the specific issues mentioned in the feedback",
        "2. Enhancing coherence - ensure all details are consistent",
        "3. Improving realism - make it more believable and grounded",
        "4. Adding useful details - include actionable information for designers",
        "",
        "Maintain the same structure and ID, but improve the content.",
        "Return ONLY the improved persona as valid JSON, no additional text.",
    ])

    return "\n".join(prompt_parts)


def _parse_refined_persona(
    content: str,
    original: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Parse refined persona from LLM response.

    Args:
        content: LLM response content.
        original: Original persona (fallback if parsing fails).

    Returns:
        Refined persona dictionary.
    """
    # Clean up content
    content = content.strip()

    # Remove markdown code blocks
    if content.startswith("```"):
        lines = content.split("\n")
        start_idx = 0
        end_idx = len(lines)

        for i, line in enumerate(lines):
            if line.strip().startswith("```"):
                if start_idx == 0:
                    start_idx = i + 1
                else:
                    end_idx = i
                    break

        content = "\n".join(lines[start_idx:end_idx])

    # Try to parse as JSON
    try:
        data = json.loads(content)

        if isinstance(data, dict):
            # Ensure ID matches original
            if "id" in original:
                data["id"] = original["id"]
            return data
        else:
            # Not a dict, return original
            return original

    except json.JSONDecodeError:
        # Try to find JSON object in text
        start_idx = content.find("{")
        end_idx = content.rfind("}")

        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx : end_idx + 1]
            try:
                data = json.loads(json_str)
                if isinstance(data, dict):
                    if "id" in original:
                        data["id"] = original["id"]
                    return data
            except json.JSONDecodeError:
                pass

        # Parsing failed, return original
        return original
