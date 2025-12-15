"""
OpenAI LLM provider implementation.

This module provides integration with OpenAI's GPT models.
"""

import os
from typing import Any

import httpx

from persona.core.providers.base import (
    LLMProvider,
    LLMResponse,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
)


class OpenAIProvider(LLMProvider):
    """
    OpenAI provider implementation.

    Supports GPT-4, GPT-4o, and other OpenAI chat models.

    Example:
        provider = OpenAIProvider()
        response = provider.generate("Write a haiku about code")
    """

    API_URL = "https://api.openai.com/v1/chat/completions"
    ENV_VAR = "OPENAI_API_KEY"

    # Available models with context windows
    MODELS = {
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 16385,
        "o1": 200000,
        "o1-mini": 128000,
        "o1-preview": 128000,
    }

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialise the OpenAI provider.

        Args:
            api_key: Optional API key. If not provided, reads from environment.
        """
        self._api_key = api_key or os.getenv(self.ENV_VAR)

    @property
    def name(self) -> str:
        return "openai"

    @property
    def default_model(self) -> str:
        return "gpt-4o"

    @property
    def available_models(self) -> list[str]:
        return list(self.MODELS.keys())

    def is_configured(self) -> bool:
        return bool(self._api_key)

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a response using OpenAI's API."""
        if not self.is_configured():
            raise AuthenticationError("OpenAI API key not configured")

        model = model or self.default_model

        if not self.validate_model(model):
            raise ModelNotFoundError(f"Model not available: {model}")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        # Handle o1 models which don't support temperature
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }

        # o1 models don't support temperature parameter
        if not model.startswith("o1"):
            payload["temperature"] = temperature

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(self.API_URL, headers=headers, json=payload)

            if response.status_code == 401:
                raise AuthenticationError("Invalid OpenAI API key")

            if response.status_code == 429:
                raise RateLimitError("OpenAI rate limit exceeded")

            if response.status_code != 200:
                error_data = response.json().get("error", {})
                raise RuntimeError(
                    f"OpenAI API error: {error_data.get('message', response.text)}"
                )

            data = response.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})

            return LLMResponse(
                content=choice["message"]["content"],
                model=data["model"],
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                finish_reason=choice.get("finish_reason", "stop"),
                raw_response=data,
            )

        except httpx.TimeoutException:
            raise RuntimeError("OpenAI API request timed out")
        except httpx.RequestError as e:
            raise RuntimeError(f"OpenAI API request failed: {e}")

    async def generate_async(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a response using OpenAI's API asynchronously."""
        if not self.is_configured():
            raise AuthenticationError("OpenAI API key not configured")

        model = model or self.default_model

        if not self.validate_model(model):
            raise ModelNotFoundError(f"Model not available: {model}")

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        # Handle o1 models which don't support temperature
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }

        # o1 models don't support temperature parameter
        if not model.startswith("o1"):
            payload["temperature"] = temperature

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(self.API_URL, headers=headers, json=payload)

            if response.status_code == 401:
                raise AuthenticationError("Invalid OpenAI API key")

            if response.status_code == 429:
                raise RateLimitError("OpenAI rate limit exceeded")

            if response.status_code != 200:
                error_data = response.json().get("error", {})
                raise RuntimeError(
                    f"OpenAI API error: {error_data.get('message', response.text)}"
                )

            data = response.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})

            return LLMResponse(
                content=choice["message"]["content"],
                model=data["model"],
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                finish_reason=choice.get("finish_reason", "stop"),
                raw_response=data,
            )

        except httpx.TimeoutException:
            raise RuntimeError("OpenAI API request timed out")
        except httpx.RequestError as e:
            raise RuntimeError(f"OpenAI API request failed: {e}")
