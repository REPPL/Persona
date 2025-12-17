"""
Content hashing utilities for data lineage.

Provides SHA-256 hashing for content integrity verification and
tamper detection across the lineage graph.
"""

import hashlib
import json
from pathlib import Path
from typing import Any

HASH_ALGORITHM = "sha256"
HASH_PREFIX = f"{HASH_ALGORITHM}:"


def hash_content(content: str | bytes) -> str:
    """
    Compute SHA-256 hash of content.

    Args:
        content: String or bytes to hash.

    Returns:
        Hash string in format "sha256:<hex_digest>".

    Example:
        ```python
        h = hash_content("hello world")
        # Returns: "sha256:b94d27b9..."
        ```
    """
    if isinstance(content, str):
        content = content.encode("utf-8")

    digest = hashlib.sha256(content).hexdigest()
    return f"{HASH_PREFIX}{digest}"


def hash_file(path: Path | str) -> str:
    """
    Compute SHA-256 hash of a file.

    Args:
        path: Path to file.

    Returns:
        Hash string in format "sha256:<hex_digest>".

    Raises:
        FileNotFoundError: If file doesn't exist.
        PermissionError: If file isn't readable.

    Example:
        ```python
        h = hash_file("./data/input.csv")
        # Returns: "sha256:abc123..."
        ```
    """
    path = Path(path)

    hasher = hashlib.sha256()
    with path.open("rb") as f:
        # Read in chunks for large files
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)

    return f"{HASH_PREFIX}{hasher.hexdigest()}"


def hash_dict(data: dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of a dictionary.

    The dictionary is serialised to JSON with sorted keys for
    consistent hashing regardless of key order.

    Args:
        data: Dictionary to hash.

    Returns:
        Hash string in format "sha256:<hex_digest>".

    Example:
        ```python
        h = hash_dict({"name": "Alice", "age": 30})
        # Returns: "sha256:def456..."
        ```
    """
    # Sort keys and use consistent separators for reproducibility
    json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hash_content(json_str)


def hash_persona(persona: dict[str, Any]) -> str:
    """
    Compute hash for a persona object.

    Extracts core persona attributes for hashing, excluding
    metadata that may change (timestamps, IDs).

    Args:
        persona: Persona dictionary.

    Returns:
        Hash string in format "sha256:<hex_digest>".
    """
    # Extract core content fields for hashing
    core_fields = {}

    # Always include these fields if present
    content_keys = [
        "name",
        "background",
        "demographics",
        "goals",
        "frustrations",
        "behaviours",
        "quote",
        "scenario",
        "attributes",
        "traits",
        "skills",
        "preferences",
    ]

    for key in content_keys:
        if key in persona:
            core_fields[key] = persona[key]

    return hash_dict(core_fields)


def verify_hash(content: str | bytes, expected_hash: str) -> bool:
    """
    Verify content against expected hash.

    Args:
        content: Content to verify.
        expected_hash: Expected hash string (with prefix).

    Returns:
        True if hash matches, False otherwise.

    Example:
        ```python
        h = hash_content("hello")
        verify_hash("hello", h)  # True
        verify_hash("world", h)  # False
        ```
    """
    actual_hash = hash_content(content)
    return actual_hash == expected_hash


def verify_file_hash(path: Path | str, expected_hash: str) -> bool:
    """
    Verify file against expected hash.

    Args:
        path: Path to file.
        expected_hash: Expected hash string (with prefix).

    Returns:
        True if hash matches, False otherwise.

    Raises:
        FileNotFoundError: If file doesn't exist.
    """
    actual_hash = hash_file(path)
    return actual_hash == expected_hash


def extract_digest(hash_string: str) -> str:
    """
    Extract hex digest from hash string.

    Args:
        hash_string: Hash string with prefix (e.g., "sha256:abc123").

    Returns:
        Hex digest without prefix.

    Raises:
        ValueError: If hash string is malformed.

    Example:
        ```python
        extract_digest("sha256:abc123")  # "abc123"
        ```
    """
    if not hash_string.startswith(HASH_PREFIX):
        raise ValueError(f"Invalid hash format: expected '{HASH_PREFIX}' prefix")

    return hash_string[len(HASH_PREFIX) :]


def is_valid_hash(hash_string: str) -> bool:
    """
    Check if a hash string is valid.

    Args:
        hash_string: Hash string to validate.

    Returns:
        True if valid sha256 hash format, False otherwise.
    """
    if not hash_string.startswith(HASH_PREFIX):
        return False

    digest = hash_string[len(HASH_PREFIX) :]

    # SHA-256 produces 64 hex characters
    if len(digest) != 64:
        return False

    # Check all characters are valid hex
    try:
        int(digest, 16)
        return True
    except ValueError:
        return False
