"""
Model dispatcher for parallel persona generation (F-120).

This module provides functionality to dispatch persona generation
requests to multiple LLM models in parallel or sequentially.
"""

import asyncio
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from persona.core.generation.parser import Persona, PersonaParser
from persona.core.multimodel.generator import ModelSpec


@dataclass
class ModelGenerationResult:
    """
    Result from a single model's generation attempt.

    Attributes:
        model: Model specification used.
        personas: List of generated personas.
        success: Whether generation succeeded.
        error: Error message if failed.
        latency_ms: Generation time in milliseconds.
        tokens_input: Input tokens used.
        tokens_output: Output tokens generated.
        raw_response: Optional raw LLM response.
    """

    model: ModelSpec
    personas: list[Persona] = field(default_factory=list)
    success: bool = True
    error: str | None = None
    latency_ms: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    raw_response: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model.to_dict(),
            "persona_count": len(self.personas),
            "success": self.success,
            "error": self.error,
            "latency_ms": round(self.latency_ms, 2),
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
        }


class ModelDispatcher:
    """
    Dispatcher for multi-model persona generation.

    Handles parallel or sequential generation across multiple LLM models,
    collecting results and handling errors gracefully.

    Example:
        >>> dispatcher = ModelDispatcher(timeout_seconds=120)
        >>> models = [ModelSpec.parse("claude-sonnet-4"), ModelSpec.parse("gpt-4o")]
        >>> results = await dispatcher.dispatch_parallel(data, models, count=3)
    """

    def __init__(
        self,
        timeout_seconds: int = 300,
        parser: PersonaParser | None = None,
    ):
        """
        Initialise the model dispatcher.

        Args:
            timeout_seconds: Timeout for each model generation.
            parser: Optional custom persona parser.
        """
        self.timeout_seconds = timeout_seconds
        self.parser = parser or PersonaParser()

    async def dispatch_parallel(
        self,
        data: str | Path,
        models: list[ModelSpec],
        count: int = 3,
        prompt_template: str | None = None,
    ) -> list[ModelGenerationResult]:
        """
        Dispatch generation to multiple models in parallel.

        Args:
            data: Source data for persona generation.
            models: List of model specifications.
            count: Number of personas to generate per model.
            prompt_template: Optional custom prompt template.

        Returns:
            List of results from each model.
        """
        tasks = [
            self._generate_with_model(data, model, count, prompt_template)
            for model in models
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(
                    ModelGenerationResult(
                        model=models[i],
                        success=False,
                        error=str(result),
                    )
                )
            else:
                final_results.append(result)

        return final_results

    async def dispatch_sequential(
        self,
        data: str | Path,
        models: list[ModelSpec],
        count: int = 3,
        prompt_template: str | None = None,
    ) -> list[ModelGenerationResult]:
        """
        Dispatch generation to multiple models sequentially.

        Args:
            data: Source data for persona generation.
            models: List of model specifications.
            count: Number of personas to generate per model.
            prompt_template: Optional custom prompt template.

        Returns:
            List of results from each model.
        """
        results = []

        for model in models:
            result = await self._generate_with_model(
                data, model, count, prompt_template
            )
            results.append(result)

        return results

    async def dispatch_self_consistency(
        self,
        data: str | Path,
        model: ModelSpec,
        samples: int = 5,
        prompt_template: str | None = None,
    ) -> list[ModelGenerationResult]:
        """
        Generate multiple samples from the same model for self-consistency check.

        Args:
            data: Source data for persona generation.
            model: Model specification.
            samples: Number of samples to generate.
            prompt_template: Optional custom prompt template.

        Returns:
            List of results (one per sample).
        """
        tasks = [
            self._generate_with_model(data, model, count=1, prompt_template=prompt_template)
            for _ in range(samples)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error results
        final_results = []
        for result in results:
            if isinstance(result, Exception):
                final_results.append(
                    ModelGenerationResult(
                        model=model,
                        success=False,
                        error=str(result),
                    )
                )
            else:
                final_results.append(result)

        return final_results

    async def _generate_with_model(
        self,
        data: str | Path,
        model: ModelSpec,
        count: int,
        prompt_template: str | None = None,
    ) -> ModelGenerationResult:
        """
        Generate personas using a single model.

        Args:
            data: Source data for persona generation.
            model: Model specification.
            count: Number of personas to generate.
            prompt_template: Optional custom prompt template.

        Returns:
            ModelGenerationResult with generation output.
        """
        start_time = time.time()

        try:
            # In production, this would call the actual LLM provider
            # For now, use mock generation
            personas, tokens_in, tokens_out, raw_response = await self._mock_llm_call(
                data, model, count, prompt_template
            )

            latency_ms = (time.time() - start_time) * 1000

            return ModelGenerationResult(
                model=model,
                personas=personas,
                success=True,
                latency_ms=latency_ms,
                tokens_input=tokens_in,
                tokens_output=tokens_out,
                raw_response=raw_response,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return ModelGenerationResult(
                model=model,
                success=False,
                error=str(e),
                latency_ms=latency_ms,
            )

    async def _mock_llm_call(
        self,
        data: str | Path,
        model: ModelSpec,
        count: int,
        prompt_template: str | None = None,
    ) -> tuple[list[Persona], int, int, str]:
        """
        Mock LLM call for testing.

        In production, this would be replaced with actual provider calls.

        Returns:
            Tuple of (personas, tokens_in, tokens_out, raw_response).
        """
        # Simulate network latency
        await asyncio.sleep(0.1)

        # Generate mock personas
        personas = []
        for i in range(count):
            persona = Persona(
                id=f"persona-{i+1}-{model.model}",
                name=f"Test Persona {i+1}",
                demographics={"age": 30 + i, "occupation": "Professional"},
                goals=[f"Goal {i+1} from {model.model}"],
                pain_points=[f"Pain point {i+1}"],
                behaviours=[f"Behaviour {i+1}"],
                quotes=[f"Quote {i+1} from model"],
            )
            personas.append(persona)

        # Estimate tokens
        data_str = str(data) if isinstance(data, Path) else data
        tokens_in = len(data_str.split()) * 2
        tokens_out = count * 400

        # Mock response
        import json
        response_data = {
            "personas": [p.to_dict() for p in personas]
        }
        raw_response = f"<output>\n```json\n{json.dumps(response_data, indent=2)}\n```\n</output>"

        return personas, tokens_in, tokens_out, raw_response


async def dispatch_multi_model(
    data: str | Path,
    models: list[str | ModelSpec],
    count: int = 3,
    parallel: bool = True,
    timeout_seconds: int = 300,
) -> list[ModelGenerationResult]:
    """
    Convenience function for multi-model dispatch.

    Args:
        data: Source data for persona generation.
        models: List of model specs (strings or ModelSpec objects).
        count: Number of personas to generate per model.
        parallel: Whether to run in parallel.
        timeout_seconds: Timeout for each model.

    Returns:
        List of results from each model.
    """
    # Convert strings to ModelSpec
    model_specs = []
    for m in models:
        if isinstance(m, str):
            model_specs.append(ModelSpec.parse(m))
        else:
            model_specs.append(m)

    dispatcher = ModelDispatcher(timeout_seconds=timeout_seconds)

    if parallel:
        return await dispatcher.dispatch_parallel(data, model_specs, count)
    else:
        return await dispatcher.dispatch_sequential(data, model_specs, count)
