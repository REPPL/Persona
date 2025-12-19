"""
Google Gemini LLM provider implementation.

This module provides integration with Google's Gemini models.
"""

import os
from typing import Any

import httpx

from persona.core.providers.base import (
    AuthenticationError,
    LLMResponse,
    ModelNotFoundError,
    RateLimitError,
)
from persona.core.providers.http_base import HTTPProvider


class GeminiProvider(HTTPProvider):
    """
    Google Gemini provider implementation.

    Supports Gemini 1.5 Pro, Gemini 2.0, and other Gemini models.
    Uses HTTP connection pooling for improved performance.

    Example:
        provider = GeminiProvider()
        response = provider.generate("Describe the solar system")
    """

    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
    ENV_VAR = "GOOGLE_API_KEY"

    # Available models with context windows
    MODELS = {
        "gemini-2.0-flash-exp": 1048576,
        "gemini-1.5-pro": 2097152,
        "gemini-1.5-flash": 1048576,
        "gemini-1.5-flash-8b": 1048576,
        "gemini-1.0-pro": 32760,
    }

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialise the Gemini provider.

        Args:
            api_key: Optional API key. If not provided, reads from environment.
        """
        super().__init__()
        self._api_key = api_key or os.getenv(self.ENV_VAR)

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def default_model(self) -> str:
        return "gemini-1.5-pro"

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
        """Generate a response using Google's Gemini API."""
        if not self.is_configured():
            raise AuthenticationError("Google API key not configured")

        model = model or self.default_model

        if not self.validate_model(model):
            raise ModelNotFoundError(f"Model not available: {model}")

        url = f"{self.API_BASE}/{model}:generateContent?key={self._api_key}"

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            # Use pooled HTTP client
            client = self.get_sync_client()
            response = client.post(url, headers=headers, json=payload)

            if response.status_code == 401 or response.status_code == 403:
                raise AuthenticationError("Invalid Google API key")

            if response.status_code == 429:
                raise RateLimitError("Google API rate limit exceeded")

            if response.status_code != 200:
                error_data = response.json().get("error", {})
                raise RuntimeError(
                    f"Gemini API error: {error_data.get('message', response.text)}"
                )

            data = response.json()
            candidates = data.get("candidates", [])

            if not candidates:
                raise RuntimeError("No response candidates from Gemini API")

            candidate = candidates[0]
            content_parts = candidate.get("content", {}).get("parts", [])
            content = ""
            for part in content_parts:
                content += part.get("text", "")

            usage = data.get("usageMetadata", {})

            return LLMResponse(
                content=content,
                model=model,
                input_tokens=usage.get("promptTokenCount", 0),
                output_tokens=usage.get("candidatesTokenCount", 0),
                finish_reason=candidate.get("finishReason", "STOP"),
                raw_response=data,
            )

        except httpx.TimeoutException:
            raise RuntimeError("Gemini API request timed out")
        except httpx.RequestError as e:
            raise RuntimeError(f"Gemini API request failed: {e}")

    async def generate_async(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a response using Google's Gemini API asynchronously."""
        if not self.is_configured():
            raise AuthenticationError("Google API key not configured")

        model = model or self.default_model

        if not self.validate_model(model):
            raise ModelNotFoundError(f"Model not available: {model}")

        url = f"{self.API_BASE}/{model}:generateContent?key={self._api_key}"

        headers = {
            "Content-Type": "application/json",
        }

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            },
        }

        try:
            # Use pooled HTTP client
            client = await self.get_async_client()
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 401 or response.status_code == 403:
                raise AuthenticationError("Invalid Google API key")

            if response.status_code == 429:
                raise RateLimitError("Google API rate limit exceeded")

            if response.status_code != 200:
                error_data = response.json().get("error", {})
                raise RuntimeError(
                    f"Gemini API error: {error_data.get('message', response.text)}"
                )

            data = response.json()
            candidates = data.get("candidates", [])

            if not candidates:
                raise RuntimeError("No response candidates from Gemini API")

            candidate = candidates[0]
            content_parts = candidate.get("content", {}).get("parts", [])
            content = ""
            for part in content_parts:
                content += part.get("text", "")

            usage = data.get("usageMetadata", {})

            return LLMResponse(
                content=content,
                model=model,
                input_tokens=usage.get("promptTokenCount", 0),
                output_tokens=usage.get("candidatesTokenCount", 0),
                finish_reason=candidate.get("finishReason", "STOP"),
                raw_response=data,
            )

        except httpx.TimeoutException:
            raise RuntimeError("Gemini API request timed out")
        except httpx.RequestError as e:
            raise RuntimeError(f"Gemini API request failed: {e}")
