"""
Tests for persona generation variations (F-033, F-034, F-035).
"""

import pytest
from dataclasses import dataclass

from persona.core.generation import (
    ComplexityLevel,
    DetailLevel,
    ComplexitySpec,
    DetailSpec,
    PersonaVariation,
    VariationMatrix,
    VariationResult,
    VariationValidator,
    COMPLEXITY_SPECS,
    DETAIL_SPECS,
    estimate_tokens,
    estimate_cost,
)


class TestComplexityLevel:
    """Tests for ComplexityLevel enum (F-033)."""

    def test_level_values(self):
        """Test complexity level values."""
        assert ComplexityLevel.SIMPLE.value == "simple"
        assert ComplexityLevel.MODERATE.value == "moderate"
        assert ComplexityLevel.COMPLEX.value == "complex"

    def test_all_levels(self):
        """Test all three levels are defined."""
        assert len(ComplexityLevel) == 3


class TestDetailLevel:
    """Tests for DetailLevel enum (F-034)."""

    def test_level_values(self):
        """Test detail level values."""
        assert DetailLevel.MINIMAL.value == "minimal"
        assert DetailLevel.DETAILED.value == "detailed"

    def test_all_levels(self):
        """Test both levels are defined."""
        assert len(DetailLevel) == 2


class TestComplexitySpec:
    """Tests for ComplexitySpec dataclass."""

    def test_simple_spec(self):
        """Test simple complexity specification."""
        spec = COMPLEXITY_SPECS[ComplexityLevel.SIMPLE]

        assert spec.level == ComplexityLevel.SIMPLE
        assert spec.min_goals == 2
        assert spec.max_goals == 3
        assert spec.min_pain_points == 2
        assert spec.max_pain_points == 3
        assert spec.evidence_required is False
        assert spec.behaviours_required is False
        assert spec.token_multiplier < 1.0

    def test_moderate_spec(self):
        """Test moderate complexity specification."""
        spec = COMPLEXITY_SPECS[ComplexityLevel.MODERATE]

        assert spec.level == ComplexityLevel.MODERATE
        assert spec.min_goals == 4
        assert spec.max_goals == 6
        assert spec.behaviours_required is True
        assert spec.evidence_required is False
        assert spec.token_multiplier == 1.0

    def test_complex_spec(self):
        """Test complex complexity specification."""
        spec = COMPLEXITY_SPECS[ComplexityLevel.COMPLEX]

        assert spec.level == ComplexityLevel.COMPLEX
        assert spec.min_goals == 7
        assert spec.max_goals == 10
        assert spec.behaviours_required is True
        assert spec.evidence_required is True
        assert spec.token_multiplier > 1.0


class TestDetailSpec:
    """Tests for DetailSpec dataclass."""

    def test_minimal_spec(self):
        """Test minimal detail specification."""
        spec = DETAIL_SPECS[DetailLevel.MINIMAL]

        assert spec.level == DetailLevel.MINIMAL
        assert spec.sentences_per_section == (1, 2)
        assert spec.use_quotes is False
        assert spec.narrative_style == "bullets"
        assert spec.token_multiplier < 1.0

    def test_detailed_spec(self):
        """Test detailed specification."""
        spec = DETAIL_SPECS[DetailLevel.DETAILED]

        assert spec.level == DetailLevel.DETAILED
        assert spec.sentences_per_section == (3, 5)
        assert spec.use_quotes is True
        assert spec.narrative_style == "prose"
        assert spec.token_multiplier > 1.0


class TestPersonaVariation:
    """Tests for PersonaVariation dataclass."""

    def test_basic_creation(self):
        """Test basic variation creation."""
        v = PersonaVariation(
            id="V1",
            complexity=ComplexityLevel.SIMPLE,
            detail=DetailLevel.MINIMAL,
        )

        assert v.id == "V1"
        assert v.complexity == ComplexityLevel.SIMPLE
        assert v.detail == DetailLevel.MINIMAL

    def test_auto_name(self):
        """Test automatic name generation."""
        v = PersonaVariation(
            id="V1",
            complexity=ComplexityLevel.SIMPLE,
            detail=DetailLevel.MINIMAL,
        )

        assert "Simple" in v.name
        assert "Minimal" in v.name

    def test_custom_name(self):
        """Test custom name override."""
        v = PersonaVariation(
            id="V1",
            complexity=ComplexityLevel.SIMPLE,
            detail=DetailLevel.MINIMAL,
            name="Quick Prototype",
        )

        assert v.name == "Quick Prototype"

    def test_complexity_spec_property(self):
        """Test complexity_spec property."""
        v = PersonaVariation("V1", ComplexityLevel.MODERATE, DetailLevel.MINIMAL)

        assert v.complexity_spec.level == ComplexityLevel.MODERATE
        assert v.complexity_spec.behaviours_required is True

    def test_detail_spec_property(self):
        """Test detail_spec property."""
        v = PersonaVariation("V1", ComplexityLevel.SIMPLE, DetailLevel.DETAILED)

        assert v.detail_spec.level == DetailLevel.DETAILED
        assert v.detail_spec.use_quotes is True

    def test_token_multiplier(self):
        """Test combined token multiplier."""
        # Simple/minimal should be lowest
        v1 = PersonaVariation("V1", ComplexityLevel.SIMPLE, DetailLevel.MINIMAL)

        # Complex/detailed should be highest
        v6 = PersonaVariation("V6", ComplexityLevel.COMPLEX, DetailLevel.DETAILED)

        assert v1.token_multiplier < v6.token_multiplier

    def test_to_dict(self):
        """Test conversion to dictionary."""
        v = PersonaVariation("V3", ComplexityLevel.MODERATE, DetailLevel.MINIMAL)
        data = v.to_dict()

        assert data["id"] == "V3"
        assert data["complexity"] == "moderate"
        assert data["detail"] == "minimal"
        assert "token_multiplier" in data


class TestVariationMatrix:
    """Tests for VariationMatrix class (F-035)."""

    @pytest.fixture
    def matrix(self) -> VariationMatrix:
        """Create a variation matrix."""
        return VariationMatrix()

    def test_all_variations(self, matrix):
        """Test getting all variations."""
        all_vars = matrix.all()

        assert len(all_vars) == 6

    def test_get_by_id(self, matrix):
        """Test getting variation by ID."""
        v1 = matrix.get("V1")
        v3 = matrix.get("V3")
        v6 = matrix.get("V6")

        assert v1.complexity == ComplexityLevel.SIMPLE
        assert v1.detail == DetailLevel.MINIMAL

        assert v3.complexity == ComplexityLevel.MODERATE
        assert v3.detail == DetailLevel.MINIMAL

        assert v6.complexity == ComplexityLevel.COMPLEX
        assert v6.detail == DetailLevel.DETAILED

    def test_get_by_id_case_insensitive(self, matrix):
        """Test ID lookup is case insensitive."""
        v1_upper = matrix.get("V1")
        v1_lower = matrix.get("v1")

        assert v1_upper == v1_lower

    def test_get_nonexistent(self, matrix):
        """Test getting non-existent variation."""
        result = matrix.get("V99")
        assert result is None

    def test_by_complexity(self, matrix):
        """Test filtering by complexity."""
        simple_vars = matrix.by_complexity(ComplexityLevel.SIMPLE)
        complex_vars = matrix.by_complexity(ComplexityLevel.COMPLEX)

        assert len(simple_vars) == 2  # V1, V2
        assert len(complex_vars) == 2  # V5, V6

        for v in simple_vars:
            assert v.complexity == ComplexityLevel.SIMPLE

    def test_by_detail(self, matrix):
        """Test filtering by detail."""
        minimal_vars = matrix.by_detail(DetailLevel.MINIMAL)
        detailed_vars = matrix.by_detail(DetailLevel.DETAILED)

        assert len(minimal_vars) == 3  # V1, V3, V5
        assert len(detailed_vars) == 3  # V2, V4, V6

        for v in minimal_vars:
            assert v.detail == DetailLevel.MINIMAL

    def test_find(self, matrix):
        """Test finding specific combination."""
        v = matrix.find(ComplexityLevel.MODERATE, DetailLevel.DETAILED)

        assert v is not None
        assert v.id == "V4"

    def test_iteration(self, matrix):
        """Test iterating over matrix."""
        count = 0
        for v in matrix:
            assert isinstance(v, PersonaVariation)
            count += 1

        assert count == 6

    def test_len(self, matrix):
        """Test length."""
        assert len(matrix) == 6


class TestVariationResult:
    """Tests for VariationResult dataclass."""

    def test_basic_creation(self):
        """Test basic result creation."""
        v = PersonaVariation("V1", ComplexityLevel.SIMPLE, DetailLevel.MINIMAL)
        result = VariationResult(variation=v)

        assert result.variation == v
        assert result.success is False
        assert result.token_count == 0
        assert result.error is None

    def test_successful_result(self):
        """Test successful result."""
        v = PersonaVariation("V1", ComplexityLevel.SIMPLE, DetailLevel.MINIMAL)
        result = VariationResult(
            variation=v,
            output_path="/output/V1",
            success=True,
            token_count=1500,
        )

        assert result.success is True
        assert result.output_path == "/output/V1"
        assert result.token_count == 1500

    def test_failed_result(self):
        """Test failed result."""
        v = PersonaVariation("V1", ComplexityLevel.SIMPLE, DetailLevel.MINIMAL)
        result = VariationResult(
            variation=v,
            success=False,
            error="Generation failed: timeout",
        )

        assert result.success is False
        assert result.error == "Generation failed: timeout"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        v = PersonaVariation("V1", ComplexityLevel.SIMPLE, DetailLevel.MINIMAL)
        result = VariationResult(variation=v, success=True)
        data = result.to_dict()

        assert "variation" in data
        assert data["success"] is True


class TestVariationValidator:
    """Tests for VariationValidator class."""

    @pytest.fixture
    def validator(self) -> VariationValidator:
        """Create a validator."""
        return VariationValidator()

    def test_validate_simple_valid(self, validator):
        """Test validating valid simple persona."""

        @dataclass
        class MockPersona:
            goals: list
            pain_points: list

        persona = MockPersona(
            goals=["Goal 1", "Goal 2"],
            pain_points=["Pain 1", "Pain 2", "Pain 3"],
        )

        is_valid, errors = validator.validate_complexity(
            persona,
            ComplexityLevel.SIMPLE,
        )

        assert is_valid
        assert len(errors) == 0

    def test_validate_simple_too_few_goals(self, validator):
        """Test validating persona with too few goals."""

        @dataclass
        class MockPersona:
            goals: list
            pain_points: list

        persona = MockPersona(goals=["Goal 1"], pain_points=["Pain 1", "Pain 2"])

        is_valid, errors = validator.validate_complexity(
            persona,
            ComplexityLevel.SIMPLE,
        )

        assert not is_valid
        assert any("Too few goals" in e for e in errors)

    def test_validate_simple_too_many_goals(self, validator):
        """Test validating persona with too many goals."""

        @dataclass
        class MockPersona:
            goals: list
            pain_points: list

        persona = MockPersona(
            goals=["G1", "G2", "G3", "G4", "G5"],
            pain_points=["P1", "P2"],
        )

        is_valid, errors = validator.validate_complexity(
            persona,
            ComplexityLevel.SIMPLE,
        )

        assert not is_valid
        assert any("Too many goals" in e for e in errors)

    def test_validate_moderate_requires_behaviours(self, validator):
        """Test moderate complexity requires behaviours."""

        @dataclass
        class MockPersona:
            goals: list
            pain_points: list
            behaviours: list

        # Without behaviours
        persona = MockPersona(
            goals=["G1", "G2", "G3", "G4"],
            pain_points=["P1", "P2", "P3", "P4"],
            behaviours=[],
        )

        is_valid, errors = validator.validate_complexity(
            persona,
            ComplexityLevel.MODERATE,
        )

        assert not is_valid
        assert any("Behaviours required" in e for e in errors)

    def test_validate_complex_requires_evidence(self, validator):
        """Test complex complexity requires evidence."""

        @dataclass
        class MockPersona:
            goals: list
            pain_points: list
            behaviours: list
            evidence: list

        persona = MockPersona(
            goals=["G1", "G2", "G3", "G4", "G5", "G6", "G7"],
            pain_points=["P1", "P2", "P3", "P4", "P5", "P6", "P7"],
            behaviours=["B1"],
            evidence=[],  # Missing
        )

        is_valid, errors = validator.validate_complexity(
            persona,
            ComplexityLevel.COMPLEX,
        )

        assert not is_valid
        assert any("Evidence" in e for e in errors)

    def test_validate_detailed_should_have_quotes(self, validator):
        """Test detailed level should have quotes."""

        @dataclass
        class MockPersona:
            quotes: list

        persona = MockPersona(quotes=[])

        is_valid, errors = validator.validate_detail(
            persona,
            DetailLevel.DETAILED,
        )

        assert not is_valid
        assert any("quotes" in e for e in errors)

    def test_validate_full_variation(self, validator):
        """Test validating against full variation."""

        @dataclass
        class MockPersona:
            goals: list
            pain_points: list
            behaviours: list
            quotes: list

        persona = MockPersona(
            goals=["G1", "G2", "G3", "G4", "G5"],
            pain_points=["P1", "P2", "P3", "P4", "P5"],
            behaviours=["B1", "B2"],
            quotes=["Quote 1"],
        )

        variation = PersonaVariation(
            "V4",
            ComplexityLevel.MODERATE,
            DetailLevel.DETAILED,
        )

        is_valid, errors = validator.validate(persona, variation)

        assert is_valid


class TestTokenAndCostEstimation:
    """Tests for token and cost estimation functions."""

    def test_estimate_tokens(self):
        """Test token estimation for variations."""
        v_simple = PersonaVariation("V1", ComplexityLevel.SIMPLE, DetailLevel.MINIMAL)
        v_complex = PersonaVariation("V6", ComplexityLevel.COMPLEX, DetailLevel.DETAILED)

        simple_tokens = estimate_tokens(1000, v_simple)
        complex_tokens = estimate_tokens(1000, v_complex)

        # Simple should be much less than complex
        assert simple_tokens < complex_tokens
        assert simple_tokens < 1000  # Below baseline
        assert complex_tokens > 1000  # Above baseline

    def test_estimate_cost_single(self):
        """Test cost estimation for single variation."""
        v = PersonaVariation("V3", ComplexityLevel.MODERATE, DetailLevel.MINIMAL)

        cost = estimate_cost(1.0, [v])

        assert cost > 0

    def test_estimate_cost_all_variations(self):
        """Test cost estimation for all variations."""
        matrix = VariationMatrix()
        all_vars = matrix.all()

        total_cost = estimate_cost(1.0, all_vars)

        # Should be sum of all multipliers
        expected = sum(v.token_multiplier for v in all_vars)
        assert abs(total_cost - expected) < 0.01


class TestVariationIntegration:
    """Integration tests for variation system."""

    def test_variation_matrix_covers_all_combinations(self):
        """Test matrix covers all complexity/detail combinations."""
        matrix = VariationMatrix()

        for complexity in ComplexityLevel:
            for detail in DetailLevel:
                v = matrix.find(complexity, detail)
                assert v is not None, f"Missing {complexity.value}/{detail.value}"

    def test_variation_ids_are_sequential(self):
        """Test variation IDs are V1 through V6."""
        matrix = VariationMatrix()

        for i in range(1, 7):
            v = matrix.get(f"V{i}")
            assert v is not None, f"Missing V{i}"

    def test_token_multipliers_are_ordered(self):
        """Test token multipliers increase with complexity/detail."""
        matrix = VariationMatrix()

        v1 = matrix.get("V1")  # simple/minimal
        v4 = matrix.get("V4")  # moderate/detailed
        v6 = matrix.get("V6")  # complex/detailed

        assert v1.token_multiplier < v4.token_multiplier < v6.token_multiplier

    def test_validation_consistency(self):
        """Test validation is consistent with specs."""
        validator = VariationValidator()
        matrix = VariationMatrix()

        # Create persona that exactly meets moderate requirements
        @dataclass
        class TestPersona:
            goals: list
            pain_points: list
            behaviours: list
            quotes: list

        moderate_persona = TestPersona(
            goals=["G1", "G2", "G3", "G4"],
            pain_points=["P1", "P2", "P3", "P4"],
            behaviours=["B1"],
            quotes=[],
        )

        # Should pass moderate/minimal
        v3 = matrix.get("V3")  # moderate/minimal
        is_valid, errors = validator.validate(moderate_persona, v3)
        assert is_valid, f"Should pass V3: {errors}"

        # Should fail simple (too many goals)
        v1 = matrix.get("V1")  # simple/minimal
        is_valid, errors = validator.validate(moderate_persona, v1)
        assert not is_valid, "Should fail V1 (too many goals)"
