"""
Custom vendor LLM provider implementation.

This module provides a generic provider that can connect to any
OpenAI-compatible API endpoint using custom vendor configuration.
"""

from typing import Any

import httpx

from persona.core.config.vendor import VendorConfig, AuthType
from persona.core.providers.base import (
    LLMProvider,
    LLMResponse,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
)


class CustomVendorProvider(LLMProvider):
    """
    Generic provider for custom LLM vendors.

    Uses VendorConfig to connect to any OpenAI-compatible endpoint,
    including Azure OpenAI, AWS Bedrock, and private deployments.

    Example:
        from persona.core.config import VendorConfig

        config = VendorConfig(
            id="local-llama",
            name="Local LLaMA",
            api_base="http://localhost:8080",
            auth_type="none",
            default_model="llama-3",
        )
        provider = CustomVendorProvider(config)
        response = provider.generate("Hello!")
    """

    def __init__(
        self,
        config: VendorConfig,
        api_key: str | None = None,
    ) -> None:
        """
        Initialise the custom vendor provider.

        Args:
            config: VendorConfig with endpoint and auth details.
            api_key: Optional API key (overrides config.auth_env).
        """
        self._config = config
        self._api_key = api_key

    @property
    def name(self) -> str:
        return self._config.id

    @property
    def display_name(self) -> str:
        """Return human-readable name."""
        return self._config.name

    @property
    def default_model(self) -> str:
        if self._config.default_model:
            return self._config.default_model
        if self._config.models:
            return self._config.models[0]
        return "default"

    @property
    def available_models(self) -> list[str]:
        return self._config.models or [self.default_model]

    def is_configured(self) -> bool:
        if self._api_key:
            return True
        return self._config.is_configured()

    def _get_auth_value(self) -> str | None:
        """Get auth value, preferring explicit api_key."""
        if self._api_key:
            return self._api_key
        return self._config.get_auth_value()

    def _build_headers(self) -> dict[str, str]:
        """Build request headers with authentication."""
        headers = {"Content-Type": "application/json"}

        # Add custom headers from config
        headers.update(self._config.resolve_headers())

        # Add authentication
        auth_value = self._get_auth_value()
        if auth_value:
            if self._config.auth_type == AuthType.BEARER:
                headers[self._config.auth_header] = f"Bearer {auth_value}"
            elif self._config.auth_type == AuthType.HEADER:
                headers[self._config.auth_header] = auth_value

        return headers

    def _build_request_payload(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Build request payload based on request format.

        Args:
            prompt: Input prompt.
            model: Model identifier.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            **kwargs: Additional parameters.

        Returns:
            Request payload dictionary.
        """
        if self._config.request_format == "anthropic":
            return {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                **kwargs,
            }

        # Default to OpenAI format
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }

        # Only add temperature if supported
        if temperature is not None and not model.startswith("o1"):
            payload["temperature"] = temperature

        payload.update(kwargs)
        return payload

    def _parse_response(
        self,
        data: dict[str, Any],
        model: str,
    ) -> LLMResponse:
        """
        Parse response based on response format.

        Args:
            data: Raw response data.
            model: Model used for generation.

        Returns:
            Standardised LLMResponse.
        """
        if self._config.response_format == "anthropic":
            content = ""
            if "content" in data and data["content"]:
                content = data["content"][0].get("text", "")

            usage = data.get("usage", {})
            return LLMResponse(
                content=content,
                model=data.get("model", model),
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                finish_reason=data.get("stop_reason", "stop"),
                raw_response=data,
            )

        # Default to OpenAI format
        choice = data["choices"][0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", model),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
            raw_response=data,
        )

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a response using the custom vendor's API."""
        if not self.is_configured():
            raise AuthenticationError(
                f"API key not configured for {self._config.name}. "
                f"Set {self._config.auth_env} environment variable."
            )

        model = model or self.default_model

        if self._config.models and not self.validate_model(model):
            raise ModelNotFoundError(
                f"Model not available for {self._config.name}: {model}"
            )

        # Build URL and headers
        url = self._config.build_url("chat", deployment=model)
        headers = self._build_headers()

        # Build request payload
        payload = self._build_request_payload(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

        try:
            with httpx.Client(timeout=float(self._config.timeout)) as client:
                response = client.post(url, headers=headers, json=payload)

            if response.status_code == 401:
                raise AuthenticationError(
                    f"Invalid API key for {self._config.name}"
                )

            if response.status_code == 429:
                raise RateLimitError(
                    f"Rate limit exceeded for {self._config.name}"
                )

            if response.status_code not in (200, 201):
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get(
                        "message", response.text
                    )
                except Exception:
                    error_msg = response.text

                raise RuntimeError(
                    f"{self._config.name} API error ({response.status_code}): "
                    f"{error_msg}"
                )

            data = response.json()
            return self._parse_response(data, model)

        except httpx.TimeoutException:
            raise RuntimeError(
                f"{self._config.name} API request timed out "
                f"after {self._config.timeout}s"
            )
        except httpx.RequestError as e:
            raise RuntimeError(
                f"{self._config.name} API request failed: {e}"
            )

    def test_connection(self) -> dict[str, Any]:
        """
        Test the vendor connection.

        Returns:
            Dictionary with test results.

        Raises:
            Various exceptions if connection fails.
        """
        result: dict[str, Any] = {
            "vendor": self._config.id,
            "name": self._config.name,
            "api_base": self._config.api_base,
            "configured": self.is_configured(),
            "models": self.available_models,
        }

        if not self.is_configured():
            result["error"] = f"Missing API key ({self._config.auth_env})"
            return result

        try:
            response = self.generate(
                prompt="Say 'OK' and nothing else.",
                max_tokens=10,
                temperature=0.0,
            )
            result["success"] = True
            result["response_model"] = response.model
            result["response_tokens"] = response.total_tokens
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        return result
