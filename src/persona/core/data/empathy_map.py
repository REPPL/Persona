"""
Empathy map data loading and validation.

This module provides support for loading empathy map data from co-creation
workshops using the Boag empathy mapping method. Empathy maps have five
dimensions: Tasks, Feelings, Influences, Pain Points, and Goals.

References:
    Boag, P. (2015). Adapting Empathy Maps for UX Design. Boagworld.
    https://boagworld.com/usability/adapting-empathy-maps-for-ux-design/
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import yaml


class EmpathyMapDimension(Enum):
    """
    The five dimensions of an empathy map.

    Based on the Boag empathy mapping method used in co-creation workshops.
    """

    TASKS = "tasks"
    FEELINGS = "feelings"
    INFLUENCES = "influences"
    PAIN_POINTS = "pain_points"
    GOALS = "goals"


@dataclass
class ParticipantTypeMap:
    """
    Empathy map data for a specific participant type.

    Attributes:
        participant_type: Name of the participant type (e.g., "music_fan").
        tasks: What the participant is trying to accomplish.
        feelings: How the participant feels during the experience.
        influences: What/who influences the participant's decisions.
        pain_points: Frustrations and challenges faced.
        goals: What the participant wants to achieve.
    """

    participant_type: str
    tasks: list[str] = field(default_factory=list)
    feelings: list[str] = field(default_factory=list)
    influences: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)

    def get_dimension(self, dimension: EmpathyMapDimension) -> list[str]:
        """Get items for a specific dimension."""
        dimension_map = {
            EmpathyMapDimension.TASKS: self.tasks,
            EmpathyMapDimension.FEELINGS: self.feelings,
            EmpathyMapDimension.INFLUENCES: self.influences,
            EmpathyMapDimension.PAIN_POINTS: self.pain_points,
            EmpathyMapDimension.GOALS: self.goals,
        }
        return dimension_map.get(dimension, [])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "participant_type": self.participant_type,
            "tasks": self.tasks,
            "feelings": self.feelings,
            "influences": self.influences,
            "pain_points": self.pain_points,
            "goals": self.goals,
        }

    def to_text(self) -> str:
        """Convert to readable text format for LLM processing."""
        lines = [
            f"## Participant Type: {self.participant_type}",
            "",
        ]

        if self.tasks:
            lines.append("### Tasks")
            for item in self.tasks:
                lines.append(f"- {item}")
            lines.append("")

        if self.feelings:
            lines.append("### Feelings")
            for item in self.feelings:
                lines.append(f"- {item}")
            lines.append("")

        if self.influences:
            lines.append("### Influences")
            for item in self.influences:
                lines.append(f"- {item}")
            lines.append("")

        if self.pain_points:
            lines.append("### Pain Points")
            for item in self.pain_points:
                lines.append(f"- {item}")
            lines.append("")

        if self.goals:
            lines.append("### Goals")
            for item in self.goals:
                lines.append(f"- {item}")
            lines.append("")

        return "\n".join(lines)


@dataclass
class EmpathyMap:
    """
    Complete empathy map from a co-creation workshop.

    Attributes:
        participants: Number of workshop participants.
        method: Research method used (e.g., "co-creation workshop").
        data: Empathy map data for each participant type.
        metadata: Additional metadata about the workshop.
    """

    participants: int = 0
    method: str = ""
    data: list[ParticipantTypeMap] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def participant_types(self) -> list[str]:
        """Return list of participant type names."""
        return [d.participant_type for d in self.data]

    def get_participant_type(self, name: str) -> ParticipantTypeMap | None:
        """Get empathy map data for a specific participant type."""
        for d in self.data:
            if d.participant_type == name:
                return d
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "participants": self.participants,
            "method": self.method,
            "data": [d.to_dict() for d in self.data],
            "metadata": self.metadata,
        }

    def to_text(self) -> str:
        """Convert to readable text format for LLM processing."""
        lines = [
            "# Empathy Map Data",
            "",
            f"**Participants:** {self.participants}",
            f"**Method:** {self.method}",
            "",
        ]

        if self.metadata:
            lines.append("## Metadata")
            for key, value in self.metadata.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        lines.append("---")
        lines.append("")

        for participant_map in self.data:
            lines.append(participant_map.to_text())
            lines.append("---")
            lines.append("")

        return "\n".join(lines)


@dataclass
class EmpathyMapValidationError:
    """Validation error for empathy map data."""

    field: str
    message: str
    participant_type: str | None = None

    def __str__(self) -> str:
        if self.participant_type:
            return f"[{self.participant_type}] {self.field}: {self.message}"
        return f"{self.field}: {self.message}"


@dataclass
class EmpathyMapValidationResult:
    """Result of empathy map validation."""

    is_valid: bool
    errors: list[EmpathyMapValidationError] = field(default_factory=list)
    warnings: list[EmpathyMapValidationError] = field(default_factory=list)

    def add_error(
        self,
        field: str,
        message: str,
        participant_type: str | None = None,
    ) -> None:
        """Add a validation error."""
        self.errors.append(
            EmpathyMapValidationError(
                field=field,
                message=message,
                participant_type=participant_type,
            )
        )
        self.is_valid = False

    def add_warning(
        self,
        field: str,
        message: str,
        participant_type: str | None = None,
    ) -> None:
        """Add a validation warning."""
        self.warnings.append(
            EmpathyMapValidationError(
                field=field,
                message=message,
                participant_type=participant_type,
            )
        )


class EmpathyMapLoader:
    """
    Loads and validates empathy map data from YAML/JSON files.

    Empathy maps capture qualitative research data from co-creation workshops
    organised around five dimensions: Tasks, Feelings, Influences, Pain Points,
    and Goals.

    Example:
        loader = EmpathyMapLoader()
        empathy_map = loader.load(Path("workshop_data.yaml"))
        text = empathy_map.to_text()  # For LLM processing
    """

    # Required dimensions for a valid empathy map
    REQUIRED_DIMENSIONS = [
        "tasks",
        "feelings",
        "influences",
        "pain_points",
        "goals",
    ]

    # Minimum items per dimension for a useful map
    MIN_ITEMS_PER_DIMENSION = 1

    def __init__(self, strict: bool = False) -> None:
        """
        Initialise the loader.

        Args:
            strict: If True, all dimensions must have items.
                   If False (default), warnings are issued for empty dimensions.
        """
        self.strict = strict

    def load(self, path: Path) -> EmpathyMap:
        """
        Load empathy map from a YAML or JSON file.

        Args:
            path: Path to the empathy map file.

        Returns:
            Parsed EmpathyMap object.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is unsupported or data is invalid.
        """
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"Empathy map file not found: {path}")

        suffix = path.suffix.lower()
        if suffix in [".yaml", ".yml"]:
            data = self._load_yaml(path)
        elif suffix == ".json":
            data = self._load_json(path)
        else:
            raise ValueError(
                f"Unsupported empathy map format: {suffix}. "
                "Supported formats: .yaml, .yml, .json"
            )

        empathy_map = self._parse(data)

        # Validate
        result = self.validate(empathy_map)
        if not result.is_valid:
            errors = "\n".join(str(e) for e in result.errors)
            raise ValueError(f"Invalid empathy map:\n{errors}")

        return empathy_map

    def load_text(self, content: str, format: str = "yaml") -> EmpathyMap:
        """
        Load empathy map from text content.

        Args:
            content: YAML or JSON content string.
            format: Content format ("yaml" or "json").

        Returns:
            Parsed EmpathyMap object.

        Raises:
            ValueError: If content is invalid.
        """
        if format.lower() in ["yaml", "yml"]:
            data = yaml.safe_load(content)
        elif format.lower() == "json":
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported format: {format}")

        empathy_map = self._parse(data)

        result = self.validate(empathy_map)
        if not result.is_valid:
            errors = "\n".join(str(e) for e in result.errors)
            raise ValueError(f"Invalid empathy map:\n{errors}")

        return empathy_map

    def validate(self, empathy_map: EmpathyMap) -> EmpathyMapValidationResult:
        """
        Validate an empathy map.

        Args:
            empathy_map: The empathy map to validate.

        Returns:
            Validation result with errors and warnings.
        """
        result = EmpathyMapValidationResult(is_valid=True)

        # Check for data entries
        if not empathy_map.data:
            result.add_error("data", "No participant type data provided")
            return result

        # Validate each participant type
        for participant_map in empathy_map.data:
            self._validate_participant_map(participant_map, result)

        return result

    def _load_yaml(self, path: Path) -> dict[str, Any]:
        """Load YAML file."""
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            raise ValueError(f"Empty YAML file: {path}")
        return data

    def _load_json(self, path: Path) -> dict[str, Any]:
        """Load JSON file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data

    def _parse(self, data: dict[str, Any]) -> EmpathyMap:
        """Parse raw data into EmpathyMap structure."""
        if not isinstance(data, dict):
            raise ValueError("Empathy map data must be a dictionary")

        participants = data.get("participants", 0)
        method = data.get("method", "")
        raw_data = data.get("data", [])

        # Extract metadata (everything except known fields)
        known_fields = {"participants", "method", "data"}
        metadata = {k: v for k, v in data.items() if k not in known_fields}

        # Parse participant type maps
        parsed_data = []
        for entry in raw_data:
            participant_map = self._parse_participant_map(entry)
            parsed_data.append(participant_map)

        return EmpathyMap(
            participants=participants,
            method=method,
            data=parsed_data,
            metadata=metadata,
        )

    def _parse_participant_map(self, data: dict[str, Any]) -> ParticipantTypeMap:
        """Parse a single participant type's empathy map."""
        if not isinstance(data, dict):
            raise ValueError("Participant data must be a dictionary")

        participant_type = data.get("participant_type", "unknown")

        # Extract dimension data, handling freeform text
        tasks = self._normalise_list(data.get("tasks", []))
        feelings = self._normalise_list(data.get("feelings", []))
        influences = self._normalise_list(data.get("influences", []))
        pain_points = self._normalise_list(data.get("pain_points", []))
        goals = self._normalise_list(data.get("goals", []))

        return ParticipantTypeMap(
            participant_type=participant_type,
            tasks=tasks,
            feelings=feelings,
            influences=influences,
            pain_points=pain_points,
            goals=goals,
        )

    def _normalise_list(self, value: Any) -> list[str]:
        """
        Normalise input to a list of strings.

        Handles freeform text entries by preserving them as-is.
        """
        if value is None:
            return []

        if isinstance(value, str):
            # Single freeform text entry
            return [value.strip()] if value.strip() else []

        if isinstance(value, list):
            result = []
            for item in value:
                if isinstance(item, str):
                    stripped = item.strip()
                    if stripped:
                        result.append(stripped)
                elif item is not None:
                    # Convert other types to string
                    result.append(str(item).strip())
            return result

        # Convert other types to single-item list
        return [str(value).strip()]

    def _validate_participant_map(
        self,
        participant_map: ParticipantTypeMap,
        result: EmpathyMapValidationResult,
    ) -> None:
        """Validate a participant type's empathy map."""
        ptype = participant_map.participant_type

        # Check participant type name
        if not ptype or ptype == "unknown":
            result.add_error(
                "participant_type",
                "Participant type name is required",
            )

        # Check each dimension
        dimensions = {
            "tasks": participant_map.tasks,
            "feelings": participant_map.feelings,
            "influences": participant_map.influences,
            "pain_points": participant_map.pain_points,
            "goals": participant_map.goals,
        }

        for dim_name, dim_data in dimensions.items():
            if not dim_data:
                if self.strict:
                    result.add_error(
                        dim_name,
                        f"Dimension '{dim_name}' has no items",
                        participant_type=ptype,
                    )
                else:
                    result.add_warning(
                        dim_name,
                        f"Dimension '{dim_name}' is empty",
                        participant_type=ptype,
                    )
