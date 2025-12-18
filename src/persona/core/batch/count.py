"""
Flexible persona count specification (F-061).

Provides flexible count specification parsing for persona generation.
"""

import re
from dataclasses import dataclass
from enum import Enum


class CountType(Enum):
    """Types of count specifications."""

    EXACT = "exact"  # Exactly N personas
    RANGE = "range"  # Between min and max
    APPROXIMATE = "approximate"  # Around N (with flexibility)
    MINIMUM = "minimum"  # At least N


@dataclass
class CountSpecification:
    """
    A flexible persona count specification.

    Supports exact counts, ranges, and approximate values.

    Examples:
        >>> spec = CountSpecification.exact(3)
        >>> spec.to_prompt()
        'Generate exactly 3 personas'

        >>> spec = CountSpecification.range(3, 5)
        >>> spec.to_prompt()
        'Generate 3-5 personas based on data richness'
    """

    count_type: CountType
    value: int = 0
    min_value: int = 0
    max_value: int = 0

    @classmethod
    def exact(cls, count: int) -> "CountSpecification":
        """Create an exact count specification."""
        return cls(
            count_type=CountType.EXACT,
            value=count,
            min_value=count,
            max_value=count,
        )

    @classmethod
    def range(cls, min_count: int, max_count: int) -> "CountSpecification":
        """Create a range count specification."""
        return cls(
            count_type=CountType.RANGE,
            value=(min_count + max_count) // 2,
            min_value=min_count,
            max_value=max_count,
        )

    @classmethod
    def approximate(cls, target: int, variance: int = 1) -> "CountSpecification":
        """Create an approximate count specification."""
        return cls(
            count_type=CountType.APPROXIMATE,
            value=target,
            min_value=max(1, target - variance),
            max_value=target + variance,
        )

    @classmethod
    def minimum(
        cls, min_count: int, max_count: int | None = None
    ) -> "CountSpecification":
        """Create a minimum count specification."""
        return cls(
            count_type=CountType.MINIMUM,
            value=min_count,
            min_value=min_count,
            max_value=max_count or min_count + 5,
        )

    def to_prompt(self) -> str:
        """
        Generate LLM prompt instruction for this count.

        Returns:
            Prompt instruction string.
        """
        if self.count_type == CountType.EXACT:
            return f"Generate exactly {self.value} personas"

        elif self.count_type == CountType.RANGE:
            return (
                f"Generate {self.min_value}-{self.max_value} personas "
                f"based on data richness"
            )

        elif self.count_type == CountType.APPROXIMATE:
            return (
                f"Generate around {self.value} personas "
                f"({self.min_value}-{self.max_value} acceptable)"
            )

        elif self.count_type == CountType.MINIMUM:
            return f"Generate at least {self.min_value} personas"

        return f"Generate {self.value} personas"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "type": self.count_type.value,
            "value": self.value,
            "min": self.min_value,
            "max": self.max_value,
            "prompt": self.to_prompt(),
        }

    def is_valid_count(self, count: int) -> bool:
        """
        Check if a count is valid for this specification.

        Args:
            count: The count to validate.

        Returns:
            True if the count is valid.
        """
        return self.min_value <= count <= self.max_value

    def __str__(self) -> str:
        """String representation."""
        if self.count_type == CountType.EXACT:
            return str(self.value)
        elif self.count_type == CountType.RANGE:
            return f"{self.min_value}-{self.max_value}"
        elif self.count_type == CountType.APPROXIMATE:
            return f"~{self.value}"
        elif self.count_type == CountType.MINIMUM:
            return f"at least {self.min_value}"
        return str(self.value)


def parse_count(value: str | int) -> CountSpecification:
    """
    Parse a count specification from string or integer.

    Supported formats:
        - "3" or 3: Exactly 3
        - "3-5": Between 3 and 5
        - "~4" or "about 4": Approximately 4
        - "at least 3": Minimum 3

    Args:
        value: Count specification string or integer.

    Returns:
        CountSpecification instance.

    Raises:
        ValueError: If the format is invalid.
    """
    # Handle integer directly
    if isinstance(value, int):
        return CountSpecification.exact(value)

    # Normalise string
    value = str(value).strip().lower()

    # Try exact integer
    if value.isdigit():
        return CountSpecification.exact(int(value))

    # Try range format: "3-5"
    range_match = re.match(r"^(\d+)\s*[-–]\s*(\d+)$", value)
    if range_match:
        min_val = int(range_match.group(1))
        max_val = int(range_match.group(2))
        if min_val > max_val:
            min_val, max_val = max_val, min_val
        return CountSpecification.range(min_val, max_val)

    # Try approximate format: "~4" or "about 4" or "around 4"
    approx_match = re.match(r"^[~≈]?\s*(\d+)$", value)
    if approx_match:
        return CountSpecification.approximate(int(approx_match.group(1)))

    about_match = re.match(r"^(?:about|around|approximately)\s+(\d+)$", value)
    if about_match:
        return CountSpecification.approximate(int(about_match.group(1)))

    # Try minimum format: "at least 3"
    min_match = re.match(r"^at\s+least\s+(\d+)$", value)
    if min_match:
        return CountSpecification.minimum(int(min_match.group(1)))

    # Try "up to N" format
    max_match = re.match(r"^up\s+to\s+(\d+)$", value)
    if max_match:
        max_val = int(max_match.group(1))
        return CountSpecification.range(1, max_val)

    raise ValueError(f"Invalid count specification: {value!r}")


def validate_count(
    actual: int,
    spec: CountSpecification,
) -> tuple[bool, str | None]:
    """
    Validate an actual count against a specification.

    Args:
        actual: The actual count generated.
        spec: The count specification.

    Returns:
        Tuple of (is_valid, error_message or None).
    """
    if spec.is_valid_count(actual):
        return True, None

    if actual < spec.min_value:
        return False, f"Generated {actual} personas, expected at least {spec.min_value}"

    if actual > spec.max_value:
        return False, f"Generated {actual} personas, expected at most {spec.max_value}"

    return False, f"Generated {actual} personas, expected {spec}"
