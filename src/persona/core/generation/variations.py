"""
Persona generation variation settings.

This module provides complexity levels, detail levels, and variation
combinations for persona generation (F-033, F-034, F-035).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterator


class ComplexityLevel(Enum):
    """
    Persona complexity levels (F-033).

    Defines structural requirements for persona output.

    Attributes:
        SIMPLE: Demographics only, 2-3 goals/pain points. For rapid prototyping.
        MODERATE: Demographics + behaviours, 4-6 items. Standard use.
        COMPLEX: Full schema, 7-10 items, evidence required. Research-grade.
    """

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class DetailLevel(Enum):
    """
    Persona detail levels (F-034).

    Defines narrative depth for persona descriptions.

    Attributes:
        MINIMAL: 1-2 sentences per section, bullet points, keywords.
        DETAILED: 3-5 sentences per section, flowing prose, full quotes.
    """

    MINIMAL = "minimal"
    DETAILED = "detailed"


@dataclass
class ComplexitySpec:
    """
    Specification for a complexity level.

    Attributes:
        level: The complexity level.
        attributes: Required attribute categories.
        min_goals: Minimum number of goals.
        max_goals: Maximum number of goals.
        min_pain_points: Minimum pain points.
        max_pain_points: Maximum pain points.
        evidence_required: Whether evidence linking is required.
        behaviours_required: Whether behaviours are required.
        token_multiplier: Estimated token multiplier vs baseline.
    """

    level: ComplexityLevel
    attributes: list[str] = field(default_factory=list)
    min_goals: int = 2
    max_goals: int = 3
    min_pain_points: int = 2
    max_pain_points: int = 3
    evidence_required: bool = False
    behaviours_required: bool = False
    token_multiplier: float = 1.0


@dataclass
class DetailSpec:
    """
    Specification for a detail level.

    Attributes:
        level: The detail level.
        sentences_per_section: Target sentences per section.
        use_quotes: Whether to include direct quotes.
        narrative_style: Style of narrative ("bullets" or "prose").
        token_multiplier: Estimated token multiplier vs baseline.
    """

    level: DetailLevel
    sentences_per_section: tuple[int, int] = (1, 2)
    use_quotes: bool = False
    narrative_style: str = "bullets"
    token_multiplier: float = 1.0


# Pre-defined complexity specifications
COMPLEXITY_SPECS: dict[ComplexityLevel, ComplexitySpec] = {
    ComplexityLevel.SIMPLE: ComplexitySpec(
        level=ComplexityLevel.SIMPLE,
        attributes=["demographics"],
        min_goals=2,
        max_goals=3,
        min_pain_points=2,
        max_pain_points=3,
        evidence_required=False,
        behaviours_required=False,
        token_multiplier=0.5,
    ),
    ComplexityLevel.MODERATE: ComplexitySpec(
        level=ComplexityLevel.MODERATE,
        attributes=["demographics", "behaviours"],
        min_goals=4,
        max_goals=6,
        min_pain_points=4,
        max_pain_points=6,
        evidence_required=False,
        behaviours_required=True,
        token_multiplier=1.0,
    ),
    ComplexityLevel.COMPLEX: ComplexitySpec(
        level=ComplexityLevel.COMPLEX,
        attributes=["demographics", "behaviours", "motivations", "context"],
        min_goals=7,
        max_goals=10,
        min_pain_points=7,
        max_pain_points=10,
        evidence_required=True,
        behaviours_required=True,
        token_multiplier=1.8,
    ),
}


# Pre-defined detail specifications
DETAIL_SPECS: dict[DetailLevel, DetailSpec] = {
    DetailLevel.MINIMAL: DetailSpec(
        level=DetailLevel.MINIMAL,
        sentences_per_section=(1, 2),
        use_quotes=False,
        narrative_style="bullets",
        token_multiplier=0.6,
    ),
    DetailLevel.DETAILED: DetailSpec(
        level=DetailLevel.DETAILED,
        sentences_per_section=(3, 5),
        use_quotes=True,
        narrative_style="prose",
        token_multiplier=1.4,
    ),
}


@dataclass
class PersonaVariation:
    """
    A specific combination of complexity and detail levels.

    Attributes:
        id: Unique variation identifier (e.g., "V1").
        complexity: Complexity level.
        detail: Detail level.
        name: Human-readable name.
    """

    id: str
    complexity: ComplexityLevel
    detail: DetailLevel
    name: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            self.name = f"{self.complexity.value.title()} / {self.detail.value.title()}"

    @property
    def complexity_spec(self) -> ComplexitySpec:
        """Get the complexity specification."""
        return COMPLEXITY_SPECS[self.complexity]

    @property
    def detail_spec(self) -> DetailSpec:
        """Get the detail specification."""
        return DETAIL_SPECS[self.detail]

    @property
    def token_multiplier(self) -> float:
        """Combined token multiplier for cost estimation."""
        return (
            self.complexity_spec.token_multiplier
            * self.detail_spec.token_multiplier
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "complexity": self.complexity.value,
            "detail": self.detail.value,
            "name": self.name,
            "token_multiplier": self.token_multiplier,
        }


class VariationMatrix:
    """
    Manages all possible variation combinations (F-035).

    Generates the 6 variations from combining complexity and detail levels.

    Example:
        matrix = VariationMatrix()
        for variation in matrix.all():
            print(f"{variation.id}: {variation.name}")

        # Get specific variation
        v3 = matrix.get("V3")  # moderate/minimal
    """

    # All variations in the matrix
    VARIATIONS = [
        PersonaVariation("V1", ComplexityLevel.SIMPLE, DetailLevel.MINIMAL),
        PersonaVariation("V2", ComplexityLevel.SIMPLE, DetailLevel.DETAILED),
        PersonaVariation("V3", ComplexityLevel.MODERATE, DetailLevel.MINIMAL),
        PersonaVariation("V4", ComplexityLevel.MODERATE, DetailLevel.DETAILED),
        PersonaVariation("V5", ComplexityLevel.COMPLEX, DetailLevel.MINIMAL),
        PersonaVariation("V6", ComplexityLevel.COMPLEX, DetailLevel.DETAILED),
    ]

    def __init__(self) -> None:
        """Initialise the variation matrix."""
        self._by_id: dict[str, PersonaVariation] = {
            v.id: v for v in self.VARIATIONS
        }

    def all(self) -> list[PersonaVariation]:
        """Get all variations."""
        return list(self.VARIATIONS)

    def get(self, variation_id: str) -> PersonaVariation | None:
        """
        Get a variation by ID.

        Args:
            variation_id: Variation ID (e.g., "V1", "V3").

        Returns:
            The variation, or None if not found.
        """
        return self._by_id.get(variation_id.upper())

    def by_complexity(
        self,
        complexity: ComplexityLevel,
    ) -> list[PersonaVariation]:
        """Get all variations for a complexity level."""
        return [v for v in self.VARIATIONS if v.complexity == complexity]

    def by_detail(self, detail: DetailLevel) -> list[PersonaVariation]:
        """Get all variations for a detail level."""
        return [v for v in self.VARIATIONS if v.detail == detail]

    def find(
        self,
        complexity: ComplexityLevel,
        detail: DetailLevel,
    ) -> PersonaVariation | None:
        """Find a variation by its settings."""
        for v in self.VARIATIONS:
            if v.complexity == complexity and v.detail == detail:
                return v
        return None

    def __iter__(self) -> Iterator[PersonaVariation]:
        """Iterate over all variations."""
        return iter(self.VARIATIONS)

    def __len__(self) -> int:
        """Return number of variations."""
        return len(self.VARIATIONS)


@dataclass
class VariationResult:
    """
    Result of generating a persona variation.

    Attributes:
        variation: The variation settings.
        output_path: Path to output folder.
        success: Whether generation succeeded.
        token_count: Actual token count used.
        error: Error message if failed.
    """

    variation: PersonaVariation
    output_path: str = ""
    success: bool = False
    token_count: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "variation": self.variation.to_dict(),
            "output_path": self.output_path,
            "success": self.success,
            "token_count": self.token_count,
            "error": self.error,
        }


class VariationValidator:
    """
    Validates personas against variation requirements.

    Checks that generated personas meet the requirements
    for their specified complexity and detail levels.
    """

    def validate_complexity(
        self,
        persona: Any,
        complexity: ComplexityLevel,
    ) -> tuple[bool, list[str]]:
        """
        Validate persona meets complexity requirements.

        Args:
            persona: The persona to validate.
            complexity: Expected complexity level.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        spec = COMPLEXITY_SPECS[complexity]
        errors: list[str] = []

        # Check goals count
        goals = getattr(persona, "goals", []) or []
        if len(goals) < spec.min_goals:
            errors.append(
                f"Too few goals: {len(goals)} < {spec.min_goals}"
            )
        if len(goals) > spec.max_goals:
            errors.append(
                f"Too many goals: {len(goals)} > {spec.max_goals}"
            )

        # Check pain points count
        pain_points = getattr(persona, "pain_points", []) or []
        if len(pain_points) < spec.min_pain_points:
            errors.append(
                f"Too few pain points: {len(pain_points)} < {spec.min_pain_points}"
            )
        if len(pain_points) > spec.max_pain_points:
            errors.append(
                f"Too many pain points: {len(pain_points)} > {spec.max_pain_points}"
            )

        # Check behaviours if required
        if spec.behaviours_required:
            behaviours = getattr(persona, "behaviours", []) or []
            if not behaviours:
                errors.append("Behaviours required but missing")

        # Check evidence if required
        if spec.evidence_required:
            evidence = getattr(persona, "evidence", []) or []
            if not evidence:
                errors.append("Evidence linking required but missing")

        return len(errors) == 0, errors

    def validate_detail(
        self,
        persona: Any,
        detail: DetailLevel,
    ) -> tuple[bool, list[str]]:
        """
        Validate persona meets detail requirements.

        Args:
            persona: The persona to validate.
            detail: Expected detail level.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        spec = DETAIL_SPECS[detail]
        errors: list[str] = []

        # Check quote presence for detailed level
        if spec.use_quotes:
            quotes = getattr(persona, "quotes", []) or []
            if not quotes:
                errors.append("Detailed level should include quotes")

        # Note: Sentence counting would require more sophisticated analysis
        # and is typically done during prompt generation, not validation

        return len(errors) == 0, errors

    def validate(
        self,
        persona: Any,
        variation: PersonaVariation,
    ) -> tuple[bool, list[str]]:
        """
        Validate persona meets all variation requirements.

        Args:
            persona: The persona to validate.
            variation: Expected variation settings.

        Returns:
            Tuple of (is_valid, list of error messages).
        """
        all_errors: list[str] = []

        complexity_valid, complexity_errors = self.validate_complexity(
            persona,
            variation.complexity,
        )
        all_errors.extend(complexity_errors)

        detail_valid, detail_errors = self.validate_detail(
            persona,
            variation.detail,
        )
        all_errors.extend(detail_errors)

        return len(all_errors) == 0, all_errors


def estimate_tokens(
    base_tokens: int,
    variation: PersonaVariation,
) -> int:
    """
    Estimate tokens for a variation.

    Args:
        base_tokens: Baseline token estimate.
        variation: The variation settings.

    Returns:
        Estimated token count.
    """
    return int(base_tokens * variation.token_multiplier)


def estimate_cost(
    base_cost: float,
    variations: list[PersonaVariation],
) -> float:
    """
    Estimate total cost for multiple variations.

    Args:
        base_cost: Baseline cost estimate.
        variations: List of variations to generate.

    Returns:
        Estimated total cost.
    """
    total = 0.0
    for v in variations:
        total += base_cost * v.token_multiplier
    return total
