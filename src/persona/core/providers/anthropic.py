"""
Anthropic LLM provider implementation.

This module provides integration with Anthropic's Claude models.
"""

import os
from typing import Any

import httpx

from persona.core.providers.base import (
    AuthenticationError,
    LLMProvider,
    LLMResponse,
    ModelNotFoundError,
    RateLimitError,
)


class AnthropicProvider(LLMProvider):
    """
    Anthropic provider implementation.

    Supports Claude 3.5, Claude 4, and Claude Opus 4.5 models.

    Example:
        provider = AnthropicProvider()
        response = provider.generate("Explain quantum computing")
    """

    API_URL = "https://api.anthropic.com/v1/messages"
    ENV_VAR = "ANTHROPIC_API_KEY"
    API_VERSION = "2023-06-01"

    # Available models with context windows
    MODELS = {
        "claude-opus-4-5-20251101": 200000,
        "claude-sonnet-4-5-20250929": 200000,
        "claude-sonnet-4-20250514": 200000,
        "claude-3-5-sonnet-20241022": 200000,
        "claude-3-5-haiku-20241022": 200000,
        "claude-3-opus-20240229": 200000,
        "claude-3-sonnet-20240229": 200000,
        "claude-3-haiku-20240307": 200000,
    }

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialise the Anthropic provider.

        Args:
            api_key: Optional API key. If not provided, reads from environment.
        """
        self._api_key = api_key or os.getenv(self.ENV_VAR)

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def default_model(self) -> str:
        return "claude-sonnet-4-5-20250929"

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
        """Generate a response using Anthropic's API."""
        if not self.is_configured():
            raise AuthenticationError("Anthropic API key not configured")

        model = model or self.default_model

        if not self.validate_model(model):
            raise ModelNotFoundError(f"Model not available: {model}")

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": self.API_VERSION,
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(self.API_URL, headers=headers, json=payload)

            if response.status_code == 401:
                raise AuthenticationError("Invalid Anthropic API key")

            if response.status_code == 429:
                raise RateLimitError("Anthropic rate limit exceeded")

            if response.status_code != 200:
                error_data = response.json().get("error", {})
                raise RuntimeError(
                    f"Anthropic API error: {error_data.get('message', response.text)}"
                )

            data = response.json()
            content_blocks = data.get("content", [])
            content = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    content += block.get("text", "")

            usage = data.get("usage", {})

            return LLMResponse(
                content=content,
                model=data["model"],
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                finish_reason=data.get("stop_reason", "end_turn"),
                raw_response=data,
            )

        except httpx.TimeoutException:
            raise RuntimeError("Anthropic API request timed out")
        except httpx.RequestError as e:
            raise RuntimeError(f"Anthropic API request failed: {e}")

    async def generate_async(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a response using Anthropic's API asynchronously."""
        if not self.is_configured():
            raise AuthenticationError("Anthropic API key not configured")

        model = model or self.default_model

        if not self.validate_model(model):
            raise ModelNotFoundError(f"Model not available: {model}")

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": self.API_VERSION,
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.API_URL, headers=headers, json=payload
                )

            if response.status_code == 401:
                raise AuthenticationError("Invalid Anthropic API key")

            if response.status_code == 429:
                raise RateLimitError("Anthropic rate limit exceeded")

            if response.status_code != 200:
                error_data = response.json().get("error", {})
                raise RuntimeError(
                    f"Anthropic API error: {error_data.get('message', response.text)}"
                )

            data = response.json()
            content_blocks = data.get("content", [])
            content = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    content += block.get("text", "")

            usage = data.get("usage", {})

            return LLMResponse(
                content=content,
                model=data["model"],
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                finish_reason=data.get("stop_reason", "end_turn"),
                raw_response=data,
            )

        except httpx.TimeoutException:
            raise RuntimeError("Anthropic API request timed out")
        except httpx.RequestError as e:
            raise RuntimeError(f"Anthropic API request failed: {e}")
