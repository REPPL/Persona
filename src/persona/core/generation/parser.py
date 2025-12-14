"""
Persona parsing and data structures.

This module provides the Persona data model and parsing logic
for extracting personas from LLM responses.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Persona:
    """
    A user persona generated from research data.

    Attributes:
        id: Unique identifier for the persona.
        name: Display name for the persona.
        demographics: Demographic information (age, occupation, etc.).
        goals: List of user goals.
        pain_points: List of pain points or frustrations.
        behaviours: List of typical behaviours.
        quotes: Representative quotes from research.
        additional: Any additional fields from the LLM response.
    """

    id: str
    name: str
    demographics: dict[str, Any] = field(default_factory=dict)
    goals: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    behaviours: list[str] = field(default_factory=list)
    quotes: list[str] = field(default_factory=list)
    additional: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Persona":
        """
        Create a Persona from a dictionary.

        Args:
            data: Dictionary with persona fields.

        Returns:
            Persona instance.
        """
        # Extract known fields
        known_fields = {
            "id", "name", "demographics", "goals",
            "pain_points", "behaviours", "quotes"
        }

        # Handle alternate field names
        if "painPoints" in data and "pain_points" not in data:
            data["pain_points"] = data.pop("painPoints")
        if "behaviors" in data and "behaviours" not in data:
            data["behaviours"] = data.pop("behaviors")

        # Collect additional fields
        additional = {k: v for k, v in data.items() if k not in known_fields}

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            demographics=data.get("demographics", {}),
            goals=data.get("goals", []),
            pain_points=data.get("pain_points", []),
            behaviours=data.get("behaviours", []),
            quotes=data.get("quotes", []),
            additional=additional,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert persona to dictionary."""
        result = {
            "id": self.id,
            "name": self.name,
            "demographics": self.demographics,
            "goals": self.goals,
            "pain_points": self.pain_points,
            "behaviours": self.behaviours,
            "quotes": self.quotes,
        }
        result.update(self.additional)
        return result


@dataclass
class ParseResult:
    """
    Result of parsing an LLM response.

    Attributes:
        personas: List of parsed personas.
        reasoning: Optional reasoning from the LLM.
        raw_output: The raw output section.
        full_response: The complete LLM response.
    """

    personas: list[Persona]
    reasoning: str | None = None
    raw_output: str = ""
    full_response: str = ""


class PersonaParser:
    """
    Parser for extracting personas from LLM responses.

    Handles various response formats and extracts structured
    persona data from JSON within the response.

    Example:
        parser = PersonaParser()
        result = parser.parse(llm_response)
        for persona in result.personas:
            print(persona.name)
    """

    # Regex patterns for extracting sections
    OUTPUT_PATTERN = re.compile(
        r"<output>\s*(.*?)\s*</output>",
        re.DOTALL | re.IGNORECASE
    )
    REASONING_PATTERN = re.compile(
        r"<reasoning>\s*(.*?)\s*</reasoning>",
        re.DOTALL | re.IGNORECASE
    )
    JSON_BLOCK_PATTERN = re.compile(
        r"```(?:json)?\s*(.*?)\s*```",
        re.DOTALL
    )

    def parse(self, response: str) -> ParseResult:
        """
        Parse an LLM response to extract personas.

        Args:
            response: The full LLM response text.

        Returns:
            ParseResult with extracted personas and metadata.
        """
        # Extract reasoning if present
        reasoning = self._extract_reasoning(response)

        # Extract output section
        raw_output = self._extract_output(response)

        # Parse JSON from output
        json_data = self._extract_json(raw_output or response)

        # Convert to personas
        personas = self._parse_personas(json_data)

        return ParseResult(
            personas=personas,
            reasoning=reasoning,
            raw_output=raw_output,
            full_response=response,
        )

    def _extract_reasoning(self, response: str) -> str | None:
        """Extract reasoning section from response."""
        match = self.REASONING_PATTERN.search(response)
        if match:
            return match.group(1).strip()
        return None

    def _extract_output(self, response: str) -> str:
        """Extract output section from response."""
        match = self.OUTPUT_PATTERN.search(response)
        if match:
            return match.group(1).strip()
        return ""

    def _extract_json(self, text: str) -> dict[str, Any] | list[Any]:
        """Extract and parse JSON from text."""
        # Try to find JSON in code blocks first
        match = self.JSON_BLOCK_PATTERN.search(text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find raw JSON object or array
        # Look for the outermost { } or [ ]
        text = text.strip()

        # Try parsing the whole thing as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            try:
                return json.loads(text[brace_start:brace_end + 1])
            except json.JSONDecodeError:
                pass

        # Try to find JSON array
        bracket_start = text.find("[")
        bracket_end = text.rfind("]")
        if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
            try:
                return json.loads(text[bracket_start:bracket_end + 1])
            except json.JSONDecodeError:
                pass

        # Return empty dict if nothing found
        return {}

    def _parse_personas(self, data: dict[str, Any] | list[Any]) -> list[Persona]:
        """Parse personas from JSON data."""
        personas = []

        if isinstance(data, list):
            # Array of personas
            for item in data:
                if isinstance(item, dict) and item:  # Skip empty dicts
                    personas.append(Persona.from_dict(item))

        elif isinstance(data, dict):
            # Skip empty dicts
            if not data:
                return personas

            # Object with personas key
            if "personas" in data:
                for item in data["personas"]:
                    if isinstance(item, dict) and item:  # Skip empty dicts
                        personas.append(Persona.from_dict(item))
            elif "id" in data or "name" in data:
                # Only treat as single persona if it has persona-like fields
                personas.append(Persona.from_dict(data))

        return personas
