"""
Draft stage: Generate initial personas using local models.

This stage uses local Ollama models to generate initial persona drafts
from input data.
"""

from typing import Any

from persona.core.hybrid.config import HybridConfig
from persona.core.hybrid.cost import CostTracker
from persona.core.providers import ProviderFactory
from persona.core.utils import JSONExtractor


async def draft_personas(
    input_data: str,
    config: HybridConfig,
    count: int,
    cost_tracker: CostTracker,
) -> list[dict[str, Any]]:
    """
    Generate draft personas using local model.

    Args:
        input_data: Raw input data for persona generation.
        config: Hybrid pipeline configuration.
        count: Number of personas to generate.
        cost_tracker: Cost tracker for recording token usage.

    Returns:
        List of generated persona dictionaries.

    Example:
        personas = await draft_personas(
            input_data="User interview transcripts...",
            config=config,
            count=10,
            cost_tracker=tracker
        )
    """
    # Create local provider
    provider = ProviderFactory.create(config.local_provider)

    # Verify provider is configured
    if not provider.is_configured():
        raise RuntimeError(
            f"{config.local_provider} provider not configured. "
            f"Is Ollama running? Start it with 'ollama serve'"
        )

    # Generate in batches
    all_personas = []
    batches = (count + config.batch_size - 1) // config.batch_size

    for batch_idx in range(batches):
        # Calculate how many for this batch
        remaining = count - len(all_personas)
        batch_count = min(config.batch_size, remaining)

        # Build generation prompt
        prompt = _build_draft_prompt(input_data, batch_count)

        # Generate with local model
        response = await provider.generate_async(
            prompt=prompt,
            model=config.local_model,
            temperature=config.local_temperature,
            max_tokens=4096,
            system_prompt=_get_system_prompt(),
        )

        # Track costs
        cost_tracker.add_local_usage(
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
        )

        # Parse personas from response
        batch_personas = _parse_personas(response.content, batch_idx)
        all_personas.extend(batch_personas)

        # Stop if we've hit budget
        if cost_tracker.is_over_budget:
            break

        # Stop if we have enough
        if len(all_personas) >= count:
            break

    # Trim to exact count
    return all_personas[:count]


def _get_system_prompt() -> str:
    """Get system prompt for draft generation."""
    return """You are an expert UX researcher specialising in creating realistic user personas.
Your task is to generate detailed, realistic personas based on research data.
Each persona should be coherent, believable, and useful for design decisions.

CRITICAL: Generate personas as valid JSON only. Do not include any explanatory text."""


def _build_draft_prompt(input_data: str, count: int) -> str:
    """Build prompt for draft generation."""
    prompt_parts = [
        f"Based on the following research data, generate {count} distinct user personas.",
        "",
        "# Research Data",
        "",
        input_data,
        "",
        "# Output Format",
        "",
        "Generate personas as a JSON array with the following structure:",
        "[",
        "  {",
        '    "id": "persona-1",',
        '    "name": "Full Name",',
        '    "age": 35,',
        '    "occupation": "Job Title",',
        '    "background": "Brief background paragraph",',
        '    "goals": ["Goal 1", "Goal 2", "Goal 3"],',
        '    "pain_points": ["Pain 1", "Pain 2", "Pain 3"],',
        '    "behaviors": ["Behavior 1", "Behavior 2"],',
        '    "quote": "A characteristic quote"',
        "  }",
        "]",
        "",
        "Requirements:",
        "- Each persona must be distinct and based on patterns in the research data",
        "- Include realistic demographic details",
        "- Focus on goals, pain points, and behaviors relevant to the domain",
        "- Provide a memorable quote that captures their perspective",
        "- Return ONLY valid JSON, no additional text",
    ]

    return "\n".join(prompt_parts)


def _parse_personas(
    content: str,
    batch_idx: int = 0,
) -> list[dict[str, Any]]:
    """
    Parse personas from LLM response.

    Args:
        content: LLM response content.
        batch_idx: Batch index for fallback ID generation.

    Returns:
        List of persona dictionaries.
    """
    # Use unified JSON extractor
    personas = JSONExtractor.extract_json_array(content)

    # Ensure each persona has required fields
    validated_personas = []
    for i, persona in enumerate(personas):
        if not isinstance(persona, dict):
            continue

        # Ensure ID exists
        if "id" not in persona:
            persona["id"] = f"persona-{batch_idx}-{i+1}"

        # Ensure basic fields exist
        if "name" not in persona:
            persona["name"] = f"User {i+1}"

        validated_personas.append(persona)

    return validated_personas
