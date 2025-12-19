"""
Base LLM provider interface.

This module defines the abstract base class and common types
for all LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    """
    Standardised response from an LLM provider.

    Attributes:
        content: The generated text content.
        model: The model that generated the response.
        input_tokens: Number of input/prompt tokens.
        output_tokens: Number of output/completion tokens.
        finish_reason: Why generation stopped (e.g., 'stop', 'length').
        raw_response: The original provider response (for debugging).
    """

    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str = "stop"
    raw_response: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Return total tokens used."""
        return self.input_tokens + self.output_tokens


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All provider implementations must inherit from this class
    and implement the required methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model for this provider."""
        ...

    @property
    @abstractmethod
    def available_models(self) -> list[str]:
        """Return list of available models for this provider."""
        ...

    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.

        Args:
            prompt: The input prompt text.
            model: Model to use (defaults to provider's default).
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (0.0 to 1.0).
            **kwargs: Additional provider-specific parameters.

        Returns:
            LLMResponse with the generated content.

        Raises:
            ValueError: If the model is not available.
            RuntimeError: If the API call fails.
        """
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """
        Check if the provider is properly configured (API key set).

        Returns:
            True if the provider can make API calls.
        """
        ...

    async def generate_async(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Generate a response from the LLM asynchronously.

        Default implementation delegates to synchronous generate() method.
        Providers should override this for native async support.

        Args:
            prompt: The input prompt text.
            model: Model to use (defaults to provider's default).
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (0.0 to 1.0).
            **kwargs: Additional provider-specific parameters.

        Returns:
            LLMResponse with the generated content.

        Raises:
            ValueError: If the model is not available.
            RuntimeError: If the API call fails.
        """
        import asyncio

        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate(prompt, model, max_tokens, temperature, **kwargs),
        )

    def validate_model(self, model: str) -> bool:
        """
        Check if a model is available for this provider.

        Args:
            model: Model identifier to check.

        Returns:
            True if the model is available.
        """
        return model in self.available_models


class ProviderError(Exception):
    """Base exception for provider errors."""

    pass


class AuthenticationError(ProviderError):
    """Raised when API authentication fails."""

    pass


class RateLimitError(ProviderError):
    """Raised when API rate limit is exceeded."""

    pass


class ModelNotFoundError(ProviderError):
    """Raised when requested model is not available."""

    pass
