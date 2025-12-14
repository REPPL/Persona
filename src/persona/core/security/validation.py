"""
Input validation utilities (F-053).

Provides comprehensive input validation for paths, strings,
numeric values, and configuration parameters.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar
from urllib.parse import urlparse


T = TypeVar("T")


class ValidationError(Exception):
    """Base exception for validation errors."""

    def __init__(self, message: str, field: str | None = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value
        self.message = message

    def __str__(self) -> str:
        if self.field:
            return f"Validation error for '{self.field}': {self.message}"
        return f"Validation error: {self.message}"


class PathValidationError(ValidationError):
    """Exception for path validation errors."""

    pass


class ValueValidationError(ValidationError):
    """Exception for value validation errors."""

    pass


@dataclass
class PathValidationResult:
    """Result of path validation."""

    valid: bool
    resolved_path: Path | None
    error: str | None = None


@dataclass
class ValidationResult:
    """Result of general validation."""

    valid: bool
    value: Any = None
    error: str | None = None
    suggestions: list[str] | None = None


class InputValidator:
    """
    Validates user inputs at system boundaries.

    Provides validation for file paths, strings, numeric values,
    URLs, and configuration parameters.

    Example:
        >>> validator = InputValidator()
        >>> validator.validate_path("./data/file.csv")
        PathValidationResult(valid=True, resolved_path=PosixPath('/abs/data/file.csv'))
        >>> validator.validate_provider("openai")
        ValidationResult(valid=True, value='openai')
        >>> validator.validate_string("test", max_length=3)
        ValidationResult(valid=False, error="String exceeds maximum length of 3")
    """

    # Known safe providers
    KNOWN_PROVIDERS = {"openai", "anthropic", "gemini", "google"}

    # Known safe models (partial list)
    KNOWN_MODEL_PREFIXES = {
        "gpt-",
        "claude-",
        "gemini-",
        "text-",
        "o1-",
        "o3-",
    }

    # URL protocol allowlist
    ALLOWED_URL_PROTOCOLS = {"https"}

    # Default path restrictions
    DEFAULT_ALLOWED_ROOTS: list[Path] = []

    def __init__(
        self,
        allowed_roots: list[Path] | None = None,
        allowed_providers: set[str] | None = None,
    ):
        """
        Initialise the validator.

        Args:
            allowed_roots: List of allowed root directories for paths.
            allowed_providers: Set of allowed provider names.
        """
        self.allowed_roots = allowed_roots or self.DEFAULT_ALLOWED_ROOTS
        self.allowed_providers = allowed_providers or self.KNOWN_PROVIDERS

    def validate_path(
        self,
        path: str | Path,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_directory: bool = False,
        allowed_extensions: set[str] | None = None,
        allowed_roots: list[Path] | None = None,
    ) -> PathValidationResult:
        """
        Validate a file path for security and correctness.

        Args:
            path: Path to validate.
            must_exist: Require the path to exist.
            must_be_file: Require the path to be a file.
            must_be_directory: Require the path to be a directory.
            allowed_extensions: Set of allowed file extensions (e.g., {".csv", ".json"}).
            allowed_roots: Override default allowed root directories.

        Returns:
            PathValidationResult with validation status.

        Raises:
            PathValidationError: If validation fails and raise_on_error is True.
        """
        try:
            # Convert to Path and resolve
            path_obj = Path(path).expanduser()

            # Check for path traversal attempts
            path_str = str(path)
            if ".." in path_str:
                # Resolve to check if it escapes
                try:
                    resolved = path_obj.resolve()
                except (OSError, RuntimeError):
                    return PathValidationResult(
                        valid=False,
                        resolved_path=None,
                        error="Invalid path: contains potentially dangerous traversal",
                    )
            else:
                resolved = path_obj.resolve()

            # Check allowed roots if specified
            roots = allowed_roots or self.allowed_roots
            if roots:
                is_within_roots = any(
                    self._is_path_within(resolved, root) for root in roots
                )
                if not is_within_roots:
                    return PathValidationResult(
                        valid=False,
                        resolved_path=resolved,
                        error=f"Path is not within allowed directories",
                    )

            # Check existence
            if must_exist and not resolved.exists():
                return PathValidationResult(
                    valid=False,
                    resolved_path=resolved,
                    error=f"Path does not exist: {resolved}",
                )

            # Check type
            if must_be_file and resolved.exists() and not resolved.is_file():
                return PathValidationResult(
                    valid=False,
                    resolved_path=resolved,
                    error=f"Path is not a file: {resolved}",
                )

            if must_be_directory and resolved.exists() and not resolved.is_dir():
                return PathValidationResult(
                    valid=False,
                    resolved_path=resolved,
                    error=f"Path is not a directory: {resolved}",
                )

            # Check extension
            if allowed_extensions and resolved.suffix.lower() not in allowed_extensions:
                return PathValidationResult(
                    valid=False,
                    resolved_path=resolved,
                    error=f"Invalid file extension: {resolved.suffix}. Allowed: {allowed_extensions}",
                )

            return PathValidationResult(valid=True, resolved_path=resolved)

        except Exception as e:
            return PathValidationResult(
                valid=False,
                resolved_path=None,
                error=f"Invalid path: {e}",
            )

    def validate_string(
        self,
        value: str,
        min_length: int = 0,
        max_length: int | None = None,
        pattern: str | None = None,
        allowed_values: set[str] | None = None,
        field_name: str | None = None,
    ) -> ValidationResult:
        """
        Validate a string value.

        Args:
            value: String to validate.
            min_length: Minimum length.
            max_length: Maximum length.
            pattern: Regex pattern to match.
            allowed_values: Set of allowed values.
            field_name: Name of the field for error messages.

        Returns:
            ValidationResult with validation status.
        """
        if not isinstance(value, str):
            return ValidationResult(
                valid=False,
                error=f"Expected string, got {type(value).__name__}",
            )

        if len(value) < min_length:
            return ValidationResult(
                valid=False,
                value=value,
                error=f"String too short: minimum length is {min_length}",
            )

        if max_length is not None and len(value) > max_length:
            return ValidationResult(
                valid=False,
                value=value,
                error=f"String too long: maximum length is {max_length}",
            )

        if pattern and not re.match(pattern, value):
            return ValidationResult(
                valid=False,
                value=value,
                error=f"String does not match required pattern: {pattern}",
            )

        if allowed_values and value not in allowed_values:
            suggestions = self._suggest_similar(value, allowed_values)
            return ValidationResult(
                valid=False,
                value=value,
                error=f"Value not allowed: {value}",
                suggestions=suggestions,
            )

        return ValidationResult(valid=True, value=value)

    def validate_number(
        self,
        value: int | float,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        allow_float: bool = True,
        field_name: str | None = None,
    ) -> ValidationResult:
        """
        Validate a numeric value.

        Args:
            value: Number to validate.
            min_value: Minimum value (inclusive).
            max_value: Maximum value (inclusive).
            allow_float: Whether to allow floating point numbers.
            field_name: Name of the field for error messages.

        Returns:
            ValidationResult with validation status.
        """
        if not isinstance(value, (int, float)):
            return ValidationResult(
                valid=False,
                error=f"Expected number, got {type(value).__name__}",
            )

        if not allow_float and isinstance(value, float) and not value.is_integer():
            return ValidationResult(
                valid=False,
                value=value,
                error="Floating point numbers not allowed",
            )

        if min_value is not None and value < min_value:
            return ValidationResult(
                valid=False,
                value=value,
                error=f"Value {value} is below minimum {min_value}",
            )

        if max_value is not None and value > max_value:
            return ValidationResult(
                valid=False,
                value=value,
                error=f"Value {value} exceeds maximum {max_value}",
            )

        return ValidationResult(valid=True, value=value)

    def validate_url(
        self,
        url: str,
        require_https: bool = True,
        allowed_domains: set[str] | None = None,
        field_name: str | None = None,
    ) -> ValidationResult:
        """
        Validate a URL.

        Args:
            url: URL to validate.
            require_https: Require HTTPS protocol.
            allowed_domains: Set of allowed domain names.
            field_name: Name of the field for error messages.

        Returns:
            ValidationResult with validation status.
        """
        try:
            parsed = urlparse(url)

            if not parsed.scheme or not parsed.netloc:
                return ValidationResult(
                    valid=False,
                    value=url,
                    error="Invalid URL format",
                )

            if require_https and parsed.scheme.lower() != "https":
                return ValidationResult(
                    valid=False,
                    value=url,
                    error="Only HTTPS URLs are allowed",
                )

            if parsed.scheme.lower() not in self.ALLOWED_URL_PROTOCOLS:
                return ValidationResult(
                    valid=False,
                    value=url,
                    error=f"Protocol not allowed: {parsed.scheme}",
                )

            if allowed_domains:
                domain = parsed.netloc.lower()
                if domain not in allowed_domains:
                    return ValidationResult(
                        valid=False,
                        value=url,
                        error=f"Domain not allowed: {domain}",
                    )

            return ValidationResult(valid=True, value=url)

        except Exception as e:
            return ValidationResult(
                valid=False,
                value=url,
                error=f"Invalid URL: {e}",
            )

    def validate_provider(
        self,
        provider: str,
        custom_providers: set[str] | None = None,
    ) -> ValidationResult:
        """
        Validate a provider name.

        Args:
            provider: Provider name to validate.
            custom_providers: Additional custom provider names.

        Returns:
            ValidationResult with validation status.
        """
        provider_lower = provider.lower()
        all_providers = self.allowed_providers.copy()
        if custom_providers:
            all_providers.update(custom_providers)

        if provider_lower not in all_providers:
            suggestions = self._suggest_similar(provider_lower, all_providers)
            return ValidationResult(
                valid=False,
                value=provider,
                error=f"Unknown provider: {provider}",
                suggestions=suggestions,
            )

        return ValidationResult(valid=True, value=provider_lower)

    def validate_model(
        self,
        model: str,
        known_models: set[str] | None = None,
    ) -> ValidationResult:
        """
        Validate a model name.

        Args:
            model: Model name to validate.
            known_models: Set of known valid model names.

        Returns:
            ValidationResult with validation status.
        """
        model_lower = model.lower()

        # Check if it matches known prefixes
        has_valid_prefix = any(
            model_lower.startswith(prefix) for prefix in self.KNOWN_MODEL_PREFIXES
        )

        if known_models and model not in known_models and not has_valid_prefix:
            suggestions = self._suggest_similar(model, known_models)
            return ValidationResult(
                valid=False,
                value=model,
                error=f"Unknown model: {model}",
                suggestions=suggestions,
            )

        # Basic format validation
        if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$", model):
            return ValidationResult(
                valid=False,
                value=model,
                error="Invalid model name format",
            )

        return ValidationResult(valid=True, value=model)

    def validate_count(
        self,
        count: int,
        min_count: int = 1,
        max_count: int = 100,
    ) -> ValidationResult:
        """
        Validate a count value (e.g., persona count).

        Args:
            count: Count to validate.
            min_count: Minimum count.
            max_count: Maximum count.

        Returns:
            ValidationResult with validation status.
        """
        return self.validate_number(
            count,
            min_value=min_count,
            max_value=max_count,
            allow_float=False,
            field_name="count",
        )

    def _is_path_within(self, path: Path, root: Path) -> bool:
        """Check if a path is within a root directory."""
        try:
            path.relative_to(root.resolve())
            return True
        except ValueError:
            return False

    def _suggest_similar(self, value: str, candidates: set[str], max_suggestions: int = 3) -> list[str]:
        """Suggest similar values from candidates."""
        if not candidates:
            return []

        # Simple similarity: prefix match or Levenshtein-like scoring
        scored = []
        value_lower = value.lower()

        for candidate in candidates:
            candidate_lower = candidate.lower()

            # Exact prefix match gets highest score
            if candidate_lower.startswith(value_lower):
                scored.append((candidate, 100))
            elif value_lower in candidate_lower:
                scored.append((candidate, 50))
            else:
                # Simple character overlap score
                common = set(value_lower) & set(candidate_lower)
                score = len(common) / max(len(value_lower), len(candidate_lower)) * 30
                if score > 10:
                    scored.append((candidate, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:max_suggestions]]


def validate_path(
    path: str | Path,
    must_exist: bool = False,
    allowed_extensions: set[str] | None = None,
) -> Path:
    """
    Convenience function to validate and resolve a path.

    Args:
        path: Path to validate.
        must_exist: Require the path to exist.
        allowed_extensions: Set of allowed file extensions.

    Returns:
        Resolved Path object.

    Raises:
        PathValidationError: If validation fails.
    """
    validator = InputValidator()
    result = validator.validate_path(
        path,
        must_exist=must_exist,
        allowed_extensions=allowed_extensions,
    )

    if not result.valid:
        raise PathValidationError(result.error or "Path validation failed", value=path)

    return result.resolved_path  # type: ignore


def validate_provider(provider: str) -> str:
    """
    Convenience function to validate a provider name.

    Args:
        provider: Provider name to validate.

    Returns:
        Validated provider name (lowercase).

    Raises:
        ValueValidationError: If validation fails.
    """
    validator = InputValidator()
    result = validator.validate_provider(provider)

    if not result.valid:
        msg = result.error or "Provider validation failed"
        if result.suggestions:
            msg += f". Did you mean: {', '.join(result.suggestions)}?"
        raise ValueValidationError(msg, field="provider", value=provider)

    return result.value
