"""
JSON extraction utility for LLM responses.

This module provides a unified approach to extracting JSON from LLM responses,
handling common patterns like markdown code blocks, partial JSON, and various
response formats.
"""

import json
import re
from typing import Any


class JSONExtractor:
    """
    Unified JSON extraction from LLM responses.

    Handles common patterns in LLM outputs:
    - Markdown code blocks (```json ... ```)
    - Raw JSON objects and arrays
    - JSON embedded in natural language text
    - Partial/malformed JSON recovery

    Example:
        >>> extractor = JSONExtractor()
        >>> data = extractor.extract_json("```json\\n{\"name\": \"Alice\"}\\n```")
        >>> print(data)  # {'name': 'Alice'}
    """

    # Pattern to match JSON in markdown code blocks
    JSON_BLOCK_PATTERN = re.compile(
        r"```(?:json)?\s*\n?(.*?)\n?```",
        re.DOTALL | re.IGNORECASE,
    )

    @classmethod
    def strip_markdown_code_blocks(cls, text: str) -> str:
        """
        Remove markdown code block markers from text.

        Args:
            text: Text potentially containing markdown code blocks.

        Returns:
            Text with code block markers removed.

        Example:
            >>> JSONExtractor.strip_markdown_code_blocks("```json\\n{\"a\": 1}\\n```")
            '{"a": 1}'
        """
        text = text.strip()

        if not text.startswith("```"):
            return text

        lines = text.split("\n")
        start_idx = 0
        end_idx = len(lines)

        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("```"):
                if start_idx == 0:
                    # First ``` found, content starts after
                    start_idx = i + 1
                else:
                    # Closing ``` found
                    end_idx = i
                    break

        return "\n".join(lines[start_idx:end_idx]).strip()

    @classmethod
    def extract_json(cls, text: str) -> dict[str, Any] | list[Any]:
        """
        Extract and parse JSON from text.

        Tries multiple strategies:
        1. JSON in markdown code blocks
        2. Raw JSON parsing
        3. Finding JSON object ({...})
        4. Finding JSON array ([...])

        Args:
            text: Text containing JSON (possibly with surrounding content).

        Returns:
            Parsed JSON as dict or list. Returns empty dict if no JSON found.

        Example:
            >>> JSONExtractor.extract_json('Here is data: {"name": "Bob"}')
            {'name': 'Bob'}
        """
        # Try to find JSON in code blocks first
        match = cls.JSON_BLOCK_PATTERN.search(text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try stripping code blocks
        cleaned = cls.strip_markdown_code_blocks(text)

        # Try parsing the cleaned content directly
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object
        brace_start = cleaned.find("{")
        brace_end = cleaned.rfind("}")
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            try:
                return json.loads(cleaned[brace_start : brace_end + 1])
            except json.JSONDecodeError:
                pass

        # Try to find JSON array
        bracket_start = cleaned.find("[")
        bracket_end = cleaned.rfind("]")
        if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
            try:
                return json.loads(cleaned[bracket_start : bracket_end + 1])
            except json.JSONDecodeError:
                pass

        # Return empty dict if nothing found
        return {}

    @classmethod
    def extract_json_array(cls, text: str) -> list[dict[str, Any]]:
        """
        Extract a JSON array from text.

        Similar to extract_json but guarantees an array result.
        Single objects are wrapped in a list.

        Args:
            text: Text containing JSON array or object.

        Returns:
            List of dictionaries. Returns empty list if no valid JSON found.

        Example:
            >>> JSONExtractor.extract_json_array('{"name": "Alice"}')
            [{'name': 'Alice'}]
        """
        data = cls.extract_json(text)

        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        elif isinstance(data, dict) and data:
            return [data]
        else:
            return []

    @classmethod
    def extract_json_object(
        cls,
        text: str,
        fallback: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Extract a JSON object from text.

        Similar to extract_json but guarantees a dict result.
        If an array is found, returns the first object.

        Args:
            text: Text containing JSON.
            fallback: Value to return if extraction fails (default: empty dict).

        Returns:
            Dictionary. Returns fallback if no valid JSON object found.

        Example:
            >>> JSONExtractor.extract_json_object('[{"name": "Bob"}]')
            {'name': 'Bob'}
        """
        if fallback is None:
            fallback = {}

        data = cls.extract_json(text)

        if isinstance(data, dict) and data:
            return data
        elif isinstance(data, list):
            # Return first dict in array
            for item in data:
                if isinstance(item, dict) and item:
                    return item

        return fallback

    @classmethod
    def try_parse(cls, text: str) -> tuple[bool, dict[str, Any] | list[Any]]:
        """
        Try to parse JSON and report success/failure.

        Args:
            text: Text to parse.

        Returns:
            Tuple of (success, result). Result is parsed JSON or empty dict.

        Example:
            >>> success, data = JSONExtractor.try_parse('{"valid": true}')
            >>> print(success)  # True
        """
        result = cls.extract_json(text)

        # Check if we got meaningful data
        if isinstance(result, dict):
            success = bool(result)
        elif isinstance(result, list):
            success = bool(result)
        else:
            success = False

        return success, result
