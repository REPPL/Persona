"""
Full LLM response capture for debugging and auditing.

This module provides functionality for capturing, storing, and replaying
complete LLM responses including metadata, tokens, and timing information.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class RequestCapture:
    """Captured request sent to LLM API."""

    prompt: str
    model: str
    provider: str
    parameters: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TokenUsage:
    """Token usage statistics."""

    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.input_tokens + self.output_tokens


@dataclass
class ResponseCapture:
    """
    Captured LLM response with full metadata.

    Contains complete API response data for debugging,
    auditing, and response replay.
    """

    # Core response data
    raw_response: str
    parsed_content: Any = None

    # Request context
    request: RequestCapture | None = None

    # Model information
    model: str = ""
    provider: str = ""

    # Token usage
    tokens: TokenUsage = field(default_factory=TokenUsage)

    # Timing
    latency_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Provider-specific metadata
    provider_metadata: dict[str, Any] = field(default_factory=dict)

    # Unique identifier for this capture
    capture_id: str = field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "capture_id": self.capture_id,
            "raw_response": self.raw_response,
            "model": self.model,
            "provider": self.provider,
            "tokens": {
                "input": self.tokens.input_tokens,
                "output": self.tokens.output_tokens,
                "total": self.tokens.total_tokens,
            },
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
        }

        if self.request:
            result["request"] = {
                "prompt": self.request.prompt,
                "model": self.request.model,
                "provider": self.request.provider,
                "parameters": self.request.parameters,
                "timestamp": self.request.timestamp,
            }

        if self.parsed_content is not None:
            result["parsed_content"] = self.parsed_content

        if self.provider_metadata:
            result["provider_metadata"] = self.provider_metadata

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResponseCapture":
        """Create from dictionary."""
        tokens_data = data.get("tokens", {})
        tokens = TokenUsage(
            input_tokens=tokens_data.get("input", 0),
            output_tokens=tokens_data.get("output", 0),
        )

        request = None
        if "request" in data:
            req_data = data["request"]
            request = RequestCapture(
                prompt=req_data.get("prompt", ""),
                model=req_data.get("model", ""),
                provider=req_data.get("provider", ""),
                parameters=req_data.get("parameters", {}),
                timestamp=req_data.get("timestamp", ""),
            )

        return cls(
            capture_id=data.get("capture_id", ""),
            raw_response=data.get("raw_response", ""),
            parsed_content=data.get("parsed_content"),
            model=data.get("model", ""),
            provider=data.get("provider", ""),
            tokens=tokens,
            latency_ms=data.get("latency_ms", 0),
            timestamp=data.get("timestamp", ""),
            request=request,
            provider_metadata=data.get("provider_metadata", {}),
        )


class ResponseCaptureStore:
    """
    Store for managing captured responses.

    Handles saving, loading, and replaying captured LLM responses.

    Example:
        store = ResponseCaptureStore("./outputs/captures")
        store.save(capture)
        loaded = store.load(capture.capture_id)
    """

    def __init__(self, base_dir: Path | str = "./captures") -> None:
        """
        Initialise the capture store.

        Args:
            base_dir: Directory for storing captures.
        """
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, capture: ResponseCapture) -> Path:
        """
        Save a response capture.

        Args:
            capture: The capture to save.

        Returns:
            Path to saved capture file.
        """
        filename = f"{capture.capture_id}.json"
        filepath = self._base_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(capture.to_dict(), f, indent=2, ensure_ascii=False)

        return filepath

    def load(self, capture_id: str) -> ResponseCapture:
        """
        Load a response capture by ID.

        Args:
            capture_id: The capture ID to load.

        Returns:
            Loaded ResponseCapture.

        Raises:
            FileNotFoundError: If capture not found.
        """
        filepath = self._base_dir / f"{capture_id}.json"

        if not filepath.exists():
            raise FileNotFoundError(f"Capture not found: {capture_id}")

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        return ResponseCapture.from_dict(data)

    def list_captures(self) -> list[str]:
        """
        List all capture IDs.

        Returns:
            List of capture IDs.
        """
        captures = []
        for file in self._base_dir.glob("*.json"):
            captures.append(file.stem)
        return sorted(captures)

    def delete(self, capture_id: str) -> bool:
        """
        Delete a capture by ID.

        Args:
            capture_id: The capture ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        filepath = self._base_dir / f"{capture_id}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False


class ResponseCaptureManager:
    """
    Manager for capturing and replaying LLM responses.

    Provides high-level API for response capture workflow.

    Example:
        manager = ResponseCaptureManager()

        # Capture mode
        capture = manager.capture(
            raw_response=response,
            request=request,
            tokens=tokens,
            latency_ms=latency,
        )
        manager.save(capture)

        # Replay mode
        captured = manager.load_for_replay(capture_id)
        # Use captured.raw_response for testing
    """

    def __init__(
        self,
        store: ResponseCaptureStore | None = None,
        enabled: bool = True,
    ) -> None:
        """
        Initialise capture manager.

        Args:
            store: Optional custom store.
            enabled: Whether capture is enabled.
        """
        self._store = store or ResponseCaptureStore()
        self._enabled = enabled
        self._captures: list[ResponseCapture] = []

    @property
    def enabled(self) -> bool:
        """Check if capture is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable capture."""
        self._enabled = value

    def capture(
        self,
        raw_response: str,
        model: str = "",
        provider: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: int = 0,
        request: RequestCapture | None = None,
        parsed_content: Any = None,
        provider_metadata: dict[str, Any] | None = None,
    ) -> ResponseCapture:
        """
        Create a response capture.

        Args:
            raw_response: Complete raw API response.
            model: Model ID used.
            provider: Provider name.
            input_tokens: Input token count.
            output_tokens: Output token count.
            latency_ms: Response time in milliseconds.
            request: Optional request capture.
            parsed_content: Optional parsed content.
            provider_metadata: Optional provider-specific metadata.

        Returns:
            ResponseCapture object.
        """
        capture = ResponseCapture(
            raw_response=raw_response,
            model=model,
            provider=provider,
            tokens=TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens),
            latency_ms=latency_ms,
            request=request,
            parsed_content=parsed_content,
            provider_metadata=provider_metadata or {},
        )

        if self._enabled:
            self._captures.append(capture)

        return capture

    def save(self, capture: ResponseCapture) -> Path | None:
        """
        Save a capture to store.

        Args:
            capture: The capture to save.

        Returns:
            Path to saved file, or None if disabled.
        """
        if not self._enabled:
            return None
        return self._store.save(capture)

    def save_all(self) -> list[Path]:
        """
        Save all captures in memory.

        Returns:
            List of saved file paths.
        """
        paths = []
        for capture in self._captures:
            path = self._store.save(capture)
            paths.append(path)
        self._captures.clear()
        return paths

    def load_for_replay(self, capture_id: str) -> ResponseCapture:
        """
        Load a capture for replay testing.

        Args:
            capture_id: The capture ID to load.

        Returns:
            Loaded ResponseCapture.
        """
        return self._store.load(capture_id)

    def list_available(self) -> list[str]:
        """
        List available captures for replay.

        Returns:
            List of capture IDs.
        """
        return self._store.list_captures()

    def get_session_captures(self) -> list[ResponseCapture]:
        """
        Get all captures from current session.

        Returns:
            List of unsaved captures.
        """
        return list(self._captures)

    def clear_session(self) -> None:
        """Clear session captures without saving."""
        self._captures.clear()


def create_request_capture(
    prompt: str,
    model: str,
    provider: str,
    **parameters: Any,
) -> RequestCapture:
    """
    Helper to create a request capture.

    Args:
        prompt: The prompt sent.
        model: Model ID.
        provider: Provider name.
        **parameters: Additional parameters.

    Returns:
        RequestCapture object.
    """
    return RequestCapture(
        prompt=prompt,
        model=model,
        provider=provider,
        parameters=parameters,
    )
