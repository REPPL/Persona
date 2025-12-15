"""
Multi-model verifier orchestrator (F-120).

This module provides the main MultiModelVerifier class that orchestrates
verification across multiple LLM models.
"""

import asyncio
from pathlib import Path
from typing import Any

from persona.core.generation.parser import Persona
from persona.core.multimodel.generator import ModelSpec
from persona.core.quality.verification.consistency import ConsistencyChecker
from persona.core.quality.verification.dispatcher import (
    ModelDispatcher,
    ModelGenerationResult,
)
from persona.core.quality.verification.models import (
    VerificationConfig,
    VerificationReport,
)
from persona.core.quality.verification.voting import get_voting_strategy


class MultiModelVerifier:
    """
    Multi-model verifier for detecting model-specific artifacts.

    Generates personas using multiple models and analyses consistency
    to detect hallucinations and model-specific biases.

    Example:
        >>> config = VerificationConfig(
        ...     models=["claude-sonnet-4", "gpt-4o"],
        ...     samples_per_model=3,
        ...     voting_strategy="majority"
        ... )
        >>> verifier = MultiModelVerifier(config)
        >>> report = await verifier.verify(data, count=3)
        >>> print(f"Passed: {report.passed}")
    """

    def __init__(
        self,
        config: VerificationConfig,
        dispatcher: ModelDispatcher | None = None,
        checker: ConsistencyChecker | None = None,
    ):
        """
        Initialise the multi-model verifier.

        Args:
            config: Verification configuration.
            dispatcher: Optional custom model dispatcher.
            checker: Optional custom consistency checker.
        """
        self.config = config
        self.dispatcher = dispatcher or ModelDispatcher(
            timeout_seconds=config.timeout_seconds
        )
        self.checker = checker or ConsistencyChecker(
            embedding_model=config.embedding_model
        )

    async def verify(
        self,
        data: str | Path,
        count: int = 3,
        prompt_template: str | None = None,
        persona_id: str | None = None,
    ) -> VerificationReport:
        """
        Verify persona generation across multiple models.

        Args:
            data: Source data for persona generation.
            count: Number of personas to generate.
            prompt_template: Optional custom prompt template.
            persona_id: Optional persona identifier for the report.

        Returns:
            VerificationReport with results.
        """
        # Parse model specs
        model_specs = [ModelSpec.parse(m) for m in self.config.models]

        # Generate personas from each model
        if self.config.parallel:
            results = await self.dispatcher.dispatch_parallel(
                data, model_specs, count, prompt_template
            )
        else:
            results = await self.dispatcher.dispatch_sequential(
                data, model_specs, count, prompt_template
            )

        # Extract successful results
        successful_results = [r for r in results if r.success]

        if not successful_results:
            # All models failed
            return VerificationReport(
                persona_id=persona_id or "verification-failed",
                config=self.config,
                consistency_score=0.0,
                passed=False,
            )

        # Collect all personas
        all_personas = []
        model_outputs = {}

        for result in successful_results:
            all_personas.extend(result.personas)
            model_key = f"{result.model.provider}:{result.model.model}"
            model_outputs[model_key] = [p.to_dict() for p in result.personas]

        # Calculate consistency metrics
        metrics = self.checker.calculate_metrics(all_personas)

        # Get attribute details
        attribute_details = self.checker.get_attribute_details(all_personas)

        # Apply voting strategy
        voting_strategy = get_voting_strategy(
            self.config.voting_strategy
        )

        agreed_attributes = voting_strategy.get_agreed_attributes(attribute_details)
        disputed_attributes = voting_strategy.get_disputed_attributes(attribute_details)
        consensus_persona = voting_strategy.extract_consensus(
            all_personas, attribute_details
        )

        # Use confidence score as consistency score
        consistency_score = metrics.confidence_score

        # Create report
        report = VerificationReport(
            persona_id=persona_id or "verification",
            config=self.config,
            consistency_score=consistency_score,
            agreed_attributes=agreed_attributes,
            disputed_attributes=disputed_attributes,
            model_outputs=model_outputs,
            metrics=metrics,
            consensus_persona=consensus_persona,
        )

        return report

    async def verify_self_consistency(
        self,
        data: str | Path,
        model: str,
        samples: int = 5,
        prompt_template: str | None = None,
        persona_id: str | None = None,
    ) -> VerificationReport:
        """
        Verify self-consistency of a single model.

        Generates multiple samples from the same model and measures
        consistency to detect randomness and instability.

        Args:
            data: Source data for persona generation.
            model: Model to test.
            samples: Number of samples to generate.
            prompt_template: Optional custom prompt template.
            persona_id: Optional persona identifier for the report.

        Returns:
            VerificationReport with self-consistency results.
        """
        model_spec = ModelSpec.parse(model)

        # Generate multiple samples
        results = await self.dispatcher.dispatch_self_consistency(
            data, model_spec, samples, prompt_template
        )

        # Extract successful results
        successful_results = [r for r in results if r.success]

        if not successful_results:
            return VerificationReport(
                persona_id=persona_id or "self-consistency-failed",
                config=self.config,
                consistency_score=0.0,
                passed=False,
            )

        # Collect all personas
        all_personas = []
        model_outputs = {}

        for i, result in enumerate(successful_results):
            all_personas.extend(result.personas)
            model_key = f"{result.model.provider}:{result.model.model}-sample{i+1}"
            model_outputs[model_key] = [p.to_dict() for p in result.personas]

        # Calculate consistency metrics
        metrics = self.checker.calculate_metrics(all_personas)

        # Get attribute details
        attribute_details = self.checker.get_attribute_details(all_personas)

        # Apply voting strategy
        voting_strategy = get_voting_strategy(
            self.config.voting_strategy
        )

        agreed_attributes = voting_strategy.get_agreed_attributes(attribute_details)
        disputed_attributes = voting_strategy.get_disputed_attributes(attribute_details)
        consensus_persona = voting_strategy.extract_consensus(
            all_personas, attribute_details
        )

        consistency_score = metrics.confidence_score

        # Create report
        report = VerificationReport(
            persona_id=persona_id or f"self-consistency-{model}",
            config=self.config,
            consistency_score=consistency_score,
            agreed_attributes=agreed_attributes,
            disputed_attributes=disputed_attributes,
            model_outputs=model_outputs,
            metrics=metrics,
            consensus_persona=consensus_persona,
        )

        return report

    async def verify_batch(
        self,
        data: str | Path,
        count: int = 3,
        prompt_template: str | None = None,
    ) -> list[VerificationReport]:
        """
        Verify a batch of personas.

        Args:
            data: Source data for persona generation.
            count: Number of personas to generate and verify.
            prompt_template: Optional custom prompt template.

        Returns:
            List of verification reports (one per persona).
        """
        # Generate once with all models
        report = await self.verify(data, count, prompt_template)

        # For batch mode, we return one report per persona
        # In this implementation, we return a single report
        # In production, you might split by persona
        return [report]


async def verify_multi_model(
    data: str | Path,
    models: list[str],
    count: int = 3,
    samples_per_model: int = 3,
    voting_strategy: str = "majority",
    consistency_threshold: float = 0.7,
    parallel: bool = True,
) -> VerificationReport:
    """
    Convenience function for multi-model verification.

    Args:
        data: Source data for persona generation.
        models: List of model identifiers.
        count: Number of personas to generate.
        samples_per_model: Number of samples per model.
        voting_strategy: Voting strategy to use.
        consistency_threshold: Minimum consistency score to pass.
        parallel: Whether to run in parallel.

    Returns:
        VerificationReport with results.
    """
    config = VerificationConfig(
        models=models,
        samples_per_model=samples_per_model,
        voting_strategy=voting_strategy,
        consistency_threshold=consistency_threshold,
        parallel=parallel,
    )

    verifier = MultiModelVerifier(config)
    return await verifier.verify(data, count)


async def verify_self_consistency(
    data: str | Path,
    model: str,
    samples: int = 5,
    consistency_threshold: float = 0.7,
) -> VerificationReport:
    """
    Convenience function for self-consistency verification.

    Args:
        data: Source data for persona generation.
        model: Model to test.
        samples: Number of samples to generate.
        consistency_threshold: Minimum consistency score to pass.

    Returns:
        VerificationReport with results.
    """
    config = VerificationConfig(
        models=[model],
        samples_per_model=samples,
        consistency_threshold=consistency_threshold,
    )

    verifier = MultiModelVerifier(config)
    return await verifier.verify_self_consistency(data, model, samples)


# Synchronous wrappers for convenience
def verify_multi_model_sync(*args: Any, **kwargs: Any) -> VerificationReport:
    """Synchronous wrapper for verify_multi_model."""
    return asyncio.run(verify_multi_model(*args, **kwargs))


def verify_self_consistency_sync(*args: Any, **kwargs: Any) -> VerificationReport:
    """Synchronous wrapper for verify_self_consistency."""
    return asyncio.run(verify_self_consistency(*args, **kwargs))
