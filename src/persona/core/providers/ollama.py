"""
Ollama LLM provider implementation.

This module provides integration with Ollama for local model inference.
Supports all models available through a running Ollama instance.
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

# Patterns indicating embedding-only models (not for text generation)
EMBEDDING_PATTERNS = ["embed", "embedding", "nomic-embed", "bge-", "e5-"]


class OllamaProvider(LLMProvider):
    """
    Ollama provider implementation.

    Supports local LLM inference through Ollama. Provides privacy-preserving
    workflows, offline operation, and cost-free generation.

    Example:
        provider = OllamaProvider()
        response = provider.generate("Explain quantum computing")

        # Custom configuration
        provider = OllamaProvider(
            base_url="http://localhost:11434",
            model="qwen2.5:72b"
        )

        # List available models
        models = provider.list_available_models()
    """

    DEFAULT_BASE_URL = "http://localhost:11434"
    ENV_VAR_BASE_URL = "OLLAMA_BASE_URL"

    # Common models - this is a fallback list
    # The actual available models are fetched from the Ollama API
    COMMON_MODELS = {
        "llama3:70b": 8000,
        "llama3:8b": 8000,
        "llama3.2:3b": 128000,
        "qwen2.5:72b": 128000,
        "qwen2.5:7b": 128000,
        "mistral:7b": 32000,
        "mixtral:8x7b": 32000,
    }

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 300.0,
        api_key: str | None = None,  # Ignored, for compatibility with ProviderFactory
    ) -> None:
        """
        Initialise the Ollama provider.

        Args:
            base_url: Ollama server URL. Defaults to http://localhost:11434
                     or OLLAMA_BASE_URL environment variable.
            model: Default model to use. If not specified, will be auto-detected.
            timeout: Request timeout in seconds (default: 300s for large models).
            api_key: Ignored parameter for compatibility with ProviderFactory.
        """
        self._base_url = (
            base_url or os.getenv(self.ENV_VAR_BASE_URL) or self.DEFAULT_BASE_URL
        )
        # Remove trailing slash if present
        self._base_url = self._base_url.rstrip("/")
        self._default_model = model
        self._timeout = timeout
        self._available_models_cache: list[str] | None = None

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def default_model(self) -> str:
        """
        Return the default model for this provider.

        If a model was specified during initialisation, use that.
        Otherwise, auto-detect the best available model.
        """
        if self._default_model:
            return self._default_model

        # Try to auto-detect from available models
        available = self.available_models
        if available:
            # Prefer larger, higher-quality models
            preference_order = [
                "qwen2.5:72b",
                "llama3:70b",
                "mixtral:8x7b",
                "qwen2.5:7b",
                "mistral:7b",
                "llama3:8b",
                "llama3.2:3b",
            ]
            for preferred in preference_order:
                if preferred in available:
                    return preferred
            # If none of our preferred models, return the first available
            return available[0]

        # Fallback if Ollama is not running
        return "llama3:8b"

    @property
    def available_models(self) -> list[str]:
        """
        Return list of available models from Ollama.

        Queries the Ollama API to get the list of pulled models.
        Falls back to common models list if Ollama is not accessible.
        """
        if self._available_models_cache is not None:
            return self._available_models_cache

        try:
            models = self.list_available_models()
            self._available_models_cache = models
            return models
        except Exception:
            # Fallback to common models if Ollama is not running
            return list(self.COMMON_MODELS.keys())

    def list_available_models(self) -> list[str]:
        """
        Query Ollama for available models.

        Returns:
            List of model names that are pulled and ready to use.

        Raises:
            RuntimeError: If Ollama is not running or not accessible.
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self._base_url}/api/tags")

            if response.status_code != 200:
                raise RuntimeError(
                    f"Ollama API error: {response.status_code} - {response.text}"
                )

            data = response.json()
            models = data.get("models", [])
            model_names = [model["name"] for model in models]

            # Filter out embedding-only models
            return [
                name
                for name in model_names
                if not any(pattern in name.lower() for pattern in EMBEDDING_PATTERNS)
            ]

        except httpx.ConnectError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {self._base_url}. "
                "Is Ollama running? Start it with 'ollama serve'"
            )
        except httpx.TimeoutException:
            raise RuntimeError(
                f"Ollama connection timed out at {self._base_url}. "
                "Check if Ollama is running."
            )
        except httpx.RequestError as e:
            raise RuntimeError(f"Ollama connection failed: {e}")

    def is_configured(self) -> bool:
        """
        Check if Ollama is running and accessible.

        Returns:
            True if Ollama server is reachable.
        """
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self._base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    def health_check(self) -> dict[str, Any]:
        """
        Perform a health check on the Ollama connection.

        Returns:
            Dictionary with health check results including:
            - is_running: Whether Ollama is accessible
            - base_url: The configured base URL
            - available_models: List of pulled models
            - model_count: Number of available models
        """
        try:
            models = self.list_available_models()
            return {
                "is_running": True,
                "base_url": self._base_url,
                "available_models": models,
                "model_count": len(models),
            }
        except Exception as e:
            return {
                "is_running": False,
                "base_url": self._base_url,
                "error": str(e),
                "available_models": [],
                "model_count": 0,
            }

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a response using Ollama's API."""
        if not self.is_configured():
            raise AuthenticationError(
                f"Ollama is not running or not accessible at {self._base_url}. "
                "Start Ollama with 'ollama serve'"
            )

        model = model or self.default_model

        # Validate model is available
        available = self.available_models
        if model not in available:
            raise ModelNotFoundError(
                f"Model '{model}' not available. "
                f"Available models: {', '.join(available)}. "
                f"Pull the model with 'ollama pull {model}'"
            )

        headers = {
            "Content-Type": "application/json",
        }

        # Extract system prompt if provided
        system_prompt = kwargs.get("system_prompt", "")

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    f"{self._base_url}/api/chat", headers=headers, json=payload
                )

            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", response.text)
                raise RuntimeError(f"Ollama API error: {error_msg}")

            data = response.json()

            # Extract content from message
            message = data.get("message", {})
            content = message.get("content", "")

            # Extract token counts if available
            # Ollama returns prompt_eval_count and eval_count
            input_tokens = data.get("prompt_eval_count", 0)
            output_tokens = data.get("eval_count", 0)

            # Determine finish reason
            done = data.get("done", False)
            finish_reason = "stop" if done else "length"

            return LLMResponse(
                content=content,
                model=data.get("model", model),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                finish_reason=finish_reason,
                raw_response=data,
            )

        except httpx.TimeoutException:
            raise RuntimeError(
                f"Ollama request timed out after {self._timeout}s. "
                "Large models may need a longer timeout."
            )
        except httpx.RequestError as e:
            raise RuntimeError(f"Ollama API request failed: {e}")

    async def generate_async(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a response using Ollama's API asynchronously."""
        if not self.is_configured():
            raise AuthenticationError(
                f"Ollama is not running or not accessible at {self._base_url}. "
                "Start Ollama with 'ollama serve'"
            )

        model = model or self.default_model

        # Validate model is available
        available = self.available_models
        if model not in available:
            raise ModelNotFoundError(
                f"Model '{model}' not available. "
                f"Available models: {', '.join(available)}. "
                f"Pull the model with 'ollama pull {model}'"
            )

        headers = {
            "Content-Type": "application/json",
        }

        # Extract system prompt if provided
        system_prompt = kwargs.get("system_prompt", "")

        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/api/chat", headers=headers, json=payload
                )

            if response.status_code != 200:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("error", response.text)
                raise RuntimeError(f"Ollama API error: {error_msg}")

            data = response.json()

            # Extract content from message
            message = data.get("message", {})
            content = message.get("content", "")

            # Extract token counts if available
            input_tokens = data.get("prompt_eval_count", 0)
            output_tokens = data.get("eval_count", 0)

            # Determine finish reason
            done = data.get("done", False)
            finish_reason = "stop" if done else "length"

            return LLMResponse(
                content=content,
                model=data.get("model", model),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                finish_reason=finish_reason,
                raw_response=data,
            )

        except httpx.TimeoutException:
            raise RuntimeError(
                f"Ollama request timed out after {self._timeout}s. "
                "Large models may need a longer timeout."
            )
        except httpx.RequestError as e:
            raise RuntimeError(f"Ollama API request failed: {e}")
