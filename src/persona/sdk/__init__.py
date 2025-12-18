"""
Persona SDK - Programmatic interface for persona generation.

This module provides a clean, type-safe SDK for integrating Persona
into applications, scripts, and CI/CD pipelines.

Quick Start with PersonaClient:
    from persona.sdk import PersonaClient

    client = PersonaClient()
    result = client.generate(data="./interviews.csv", count=5)

    for persona in result.personas:
        print(f"{persona.name}: {persona.goals}")

Advanced Example with PersonaGenerator:
    from persona.sdk import PersonaGenerator, PersonaConfig

    generator = PersonaGenerator(provider="anthropic")
    result = generator.generate(
        data_path="./interviews.csv",
        config=PersonaConfig(count=3)
    )
    for persona in result.personas:
        print(f"{persona.name}: {persona.goals}")

Async Example:
    import asyncio
    from persona.sdk import AsyncPersonaGenerator, PersonaConfig

    async def main():
        generator = AsyncPersonaGenerator(provider="anthropic")
        result = await generator.agenerate(
            data_path="./interviews.csv",
            config=PersonaConfig(count=3)
        )
        for persona in result.personas:
            print(f"{persona.name}: {persona.goals}")

    asyncio.run(main())
"""

from persona.sdk.async_experiment import AsyncExperimentSDK
from persona.sdk.async_generator import AsyncPersonaGenerator, agenerate_parallel
from persona.sdk.client import PersonaClient
from persona.sdk.config import SDKConfig
from persona.sdk.exceptions import (
    BudgetExceededError,
    ConfigurationError,
    DataError,
    GenerationError,
    PersonaError,
    ProviderError,
    RateLimitError,
    ValidationError,
)
from persona.sdk.experiment import ExperimentSDK
from persona.sdk.generator import PersonaGenerator
from persona.sdk.models import (
    ExperimentConfig,
    ExperimentModel,
    GenerationResultModel,
    PersonaConfig,
    PersonaModel,
)

__all__ = [
    # Main classes
    "PersonaClient",
    "PersonaGenerator",
    "ExperimentSDK",
    # Async classes
    "AsyncPersonaGenerator",
    "AsyncExperimentSDK",
    "agenerate_parallel",
    # Configuration
    "PersonaConfig",
    "ExperimentConfig",
    "SDKConfig",
    # Result models
    "PersonaModel",
    "GenerationResultModel",
    "ExperimentModel",
    # Exceptions
    "PersonaError",
    "ConfigurationError",
    "ProviderError",
    "ValidationError",
    "DataError",
    "BudgetExceededError",
    "RateLimitError",
    "GenerationError",
]
