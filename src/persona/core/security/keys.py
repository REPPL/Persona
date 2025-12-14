"""
API key protection utilities (F-051).

Provides secure handling of API keys including masking, redaction,
and secure string storage.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any


# Common API key patterns for different providers
API_KEY_PATTERNS = [
    # Anthropic - more flexible pattern
    r"sk-ant-api\d{2}-[a-zA-Z0-9_-]{10,}",
    # OpenAI project keys
    r"sk-proj-[a-zA-Z0-9_-]{10,}",
    # OpenAI and generic sk- keys
    r"sk-[a-zA-Z0-9_-]{10,}",
    # Google/Gemini
    r"AIza[a-zA-Z0-9_-]{30,}",
]

# Compiled pattern for efficiency - order matters (most specific first)
_KEY_PATTERN = re.compile(
    "|".join(f"({p})" for p in API_KEY_PATTERNS),
    re.IGNORECASE,
)


def mask_api_key(key: str | None, show_prefix: int = 7, show_suffix: int = 4) -> str:
    """
    Mask an API key for safe display.

    Shows the first `show_prefix` characters and last `show_suffix` characters,
    with asterisks in between.

    Args:
        key: The API key to mask.
        show_prefix: Number of characters to show at the start.
        show_suffix: Number of characters to show at the end.

    Returns:
        Masked key string, e.g., "sk-ant-***...xyz9"

    Example:
        >>> mask_api_key("sk-ant-api03-abc123xyz789def456")
        'sk-ant-***...f456'
    """
    if not key:
        return "<not set>"

    if len(key) <= show_prefix + show_suffix:
        return "*" * len(key)

    prefix = key[:show_prefix]
    suffix = key[-show_suffix:] if show_suffix > 0 else ""

    return f"{prefix}***...{suffix}"


def redact_api_keys(text: str) -> str:
    """
    Redact all API keys from a text string.

    Scans the text for known API key patterns and replaces them
    with masked versions.

    Args:
        text: Text potentially containing API keys.

    Returns:
        Text with all API keys redacted.

    Example:
        >>> redact_api_keys("Using key sk-ant-api03-abc123...")
        'Using key sk-ant-***...123...'
    """
    if not text:
        return text

    def replace_key(match: re.Match) -> str:
        return mask_api_key(match.group(0))

    return _KEY_PATTERN.sub(replace_key, text)


@dataclass
class SecureString:
    """
    A string wrapper that prevents accidental exposure of sensitive data.

    The value is stored internally but never exposed in string representations,
    logs, or error messages.

    Attributes:
        _value: The actual secret value (private).

    Example:
        >>> secret = SecureString("sk-ant-api03-abc123")
        >>> print(secret)
        SecureString(***REDACTED***)
        >>> secret.get_value()
        'sk-ant-api03-abc123'
        >>> secret.get_masked()
        'sk-ant-***...c123'
    """

    _value: str

    def __post_init__(self) -> None:
        """Validate the secure string."""
        if not isinstance(self._value, str):
            raise TypeError("SecureString value must be a string")

    def get_value(self) -> str:
        """
        Get the actual secret value.

        Use with caution - only when the value is actually needed
        for API calls.

        Returns:
            The unmasked secret value.
        """
        return self._value

    def get_masked(self, show_prefix: int = 7, show_suffix: int = 4) -> str:
        """
        Get a masked version of the value for display.

        Args:
            show_prefix: Characters to show at start.
            show_suffix: Characters to show at end.

        Returns:
            Masked string safe for display.
        """
        return mask_api_key(self._value, show_prefix, show_suffix)

    def __str__(self) -> str:
        """Return a redacted representation."""
        return "SecureString(***REDACTED***)"

    def __repr__(self) -> str:
        """Return a redacted representation."""
        return "SecureString(***REDACTED***)"

    def __eq__(self, other: Any) -> bool:
        """Compare secure strings by value."""
        if isinstance(other, SecureString):
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        """Hash the secure string."""
        return hash(self._value)

    def __bool__(self) -> bool:
        """Return True if the value is non-empty."""
        return bool(self._value)

    def __len__(self) -> int:
        """Return the length of the value."""
        return len(self._value)


class KeyMaskingFilter(logging.Filter):
    """
    A logging filter that masks API keys in log messages.

    Install this filter on loggers to automatically redact
    API keys from all log output.

    Example:
        >>> import logging
        >>> logger = logging.getLogger("persona")
        >>> logger.addFilter(KeyMaskingFilter())
        >>> logger.info("Using key sk-ant-api03-abc123")
        # Output: "Using key sk-ant-***...c123"
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter a log record, masking any API keys.

        Args:
            record: The log record to filter.

        Returns:
            Always True (record is always emitted, but modified).
        """
        # Mask the message
        if record.msg:
            record.msg = redact_api_keys(str(record.msg))

        # Mask any arguments
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: redact_api_keys(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    redact_api_keys(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        # Mask exception info if present
        if record.exc_text:
            record.exc_text = redact_api_keys(record.exc_text)

        return True


def install_key_masking(logger_name: str = "persona") -> None:
    """
    Install key masking on a logger and all its children.

    Args:
        logger_name: Name of the logger to protect.
    """
    logger = logging.getLogger(logger_name)
    logger.addFilter(KeyMaskingFilter())


def format_key_for_display(
    key: str | SecureString | None,
    label: str = "API Key",
) -> str:
    """
    Format a key for safe display in CLI output.

    Args:
        key: The key to format.
        label: Label for the key.

    Returns:
        Formatted string safe for display.
    """
    if key is None:
        return f"{label}: <not configured>"

    if isinstance(key, SecureString):
        masked = key.get_masked()
    else:
        masked = mask_api_key(key)

    return f"{label}: {masked}"
