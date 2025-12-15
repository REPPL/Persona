"""
Persona - Generate realistic user personas from your data using AI.

This package provides tools for generating user personas from qualitative
research data such as interviews, surveys, and user feedback.

Quick Start:
    >>> from persona import PersonaGenerator
    >>> generator = PersonaGenerator(provider="anthropic")
    >>> result = generator.generate("./interviews/")
    >>> for persona in result.personas:
    ...     print(f"{persona.name}: {persona.goals}")
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("persona")
except PackageNotFoundError:
    # Package not installed (e.g., running from source without pip install -e)
    __version__ = "0.0.0-dev"

# High-level SDK exports
from persona.sdk import (
    # Main classes
    PersonaGenerator,
    ExperimentSDK,
    # Async classes
    AsyncPersonaGenerator,
    AsyncExperimentSDK,
    agenerate_parallel,
    # Configuration models
    PersonaConfig,
    ExperimentConfig,
    # Result models
    PersonaModel,
    GenerationResultModel,
    ExperimentModel,
    # Exceptions
    PersonaError,
    ConfigurationError,
    ProviderError,
    ValidationError,
    DataError,
    BudgetExceededError,
    RateLimitError,
    GenerationError,
)

__all__ = [
    "__version__",
    # Main classes
    "PersonaGenerator",
    "ExperimentSDK",
    # Async classes
    "AsyncPersonaGenerator",
    "AsyncExperimentSDK",
    "agenerate_parallel",
    # Configuration models
    "PersonaConfig",
    "ExperimentConfig",
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
