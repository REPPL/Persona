"""Tests for flexible persona count (F-061)."""

import pytest
from persona.core.batch.count import (
    CountSpecification,
    CountType,
    parse_count,
    validate_count,
)


class TestCountSpecification:
    """Tests for CountSpecification."""

    def test_exact_count(self):
        """Creates exact count specification."""
        spec = CountSpecification.exact(3)

        assert spec.count_type == CountType.EXACT
        assert spec.value == 3
        assert spec.min_value == 3
        assert spec.max_value == 3

    def test_range_count(self):
        """Creates range count specification."""
        spec = CountSpecification.range(3, 5)

        assert spec.count_type == CountType.RANGE
        assert spec.min_value == 3
        assert spec.max_value == 5

    def test_approximate_count(self):
        """Creates approximate count specification."""
        spec = CountSpecification.approximate(4)

        assert spec.count_type == CountType.APPROXIMATE
        assert spec.value == 4
        assert spec.min_value == 3
        assert spec.max_value == 5

    def test_minimum_count(self):
        """Creates minimum count specification."""
        spec = CountSpecification.minimum(3)

        assert spec.count_type == CountType.MINIMUM
        assert spec.min_value == 3

    def test_exact_prompt(self):
        """Generates exact prompt."""
        spec = CountSpecification.exact(3)
        prompt = spec.to_prompt()

        assert "exactly 3" in prompt.lower()

    def test_range_prompt(self):
        """Generates range prompt."""
        spec = CountSpecification.range(3, 5)
        prompt = spec.to_prompt()

        assert "3-5" in prompt

    def test_approximate_prompt(self):
        """Generates approximate prompt."""
        spec = CountSpecification.approximate(4)
        prompt = spec.to_prompt()

        assert "around 4" in prompt.lower()

    def test_minimum_prompt(self):
        """Generates minimum prompt."""
        spec = CountSpecification.minimum(3)
        prompt = spec.to_prompt()

        assert "at least 3" in prompt.lower()

    def test_is_valid_count_exact(self):
        """Validates exact count."""
        spec = CountSpecification.exact(3)

        assert spec.is_valid_count(3)
        assert not spec.is_valid_count(2)
        assert not spec.is_valid_count(4)

    def test_is_valid_count_range(self):
        """Validates range count."""
        spec = CountSpecification.range(3, 5)

        assert spec.is_valid_count(3)
        assert spec.is_valid_count(4)
        assert spec.is_valid_count(5)
        assert not spec.is_valid_count(2)
        assert not spec.is_valid_count(6)

    def test_to_dict(self):
        """Converts to dictionary."""
        spec = CountSpecification.exact(3)
        data = spec.to_dict()

        assert data["type"] == "exact"
        assert data["value"] == 3
        assert "prompt" in data

    def test_str_exact(self):
        """String representation for exact."""
        spec = CountSpecification.exact(3)
        assert str(spec) == "3"

    def test_str_range(self):
        """String representation for range."""
        spec = CountSpecification.range(3, 5)
        assert str(spec) == "3-5"

    def test_str_approximate(self):
        """String representation for approximate."""
        spec = CountSpecification.approximate(4)
        assert str(spec) == "~4"


class TestParseCount:
    """Tests for parse_count function."""

    def test_parse_integer(self):
        """Parses integer directly."""
        spec = parse_count(3)

        assert spec.count_type == CountType.EXACT
        assert spec.value == 3

    def test_parse_integer_string(self):
        """Parses integer string."""
        spec = parse_count("3")

        assert spec.count_type == CountType.EXACT
        assert spec.value == 3

    def test_parse_range(self):
        """Parses range format."""
        spec = parse_count("3-5")

        assert spec.count_type == CountType.RANGE
        assert spec.min_value == 3
        assert spec.max_value == 5

    def test_parse_range_reversed(self):
        """Handles reversed range."""
        spec = parse_count("5-3")

        assert spec.min_value == 3
        assert spec.max_value == 5

    def test_parse_tilde_approximate(self):
        """Parses tilde approximate format."""
        spec = parse_count("~4")

        assert spec.count_type == CountType.APPROXIMATE
        assert spec.value == 4

    def test_parse_about(self):
        """Parses 'about N' format."""
        spec = parse_count("about 4")

        assert spec.count_type == CountType.APPROXIMATE
        assert spec.value == 4

    def test_parse_around(self):
        """Parses 'around N' format."""
        spec = parse_count("around 4")

        assert spec.count_type == CountType.APPROXIMATE

    def test_parse_at_least(self):
        """Parses 'at least N' format."""
        spec = parse_count("at least 3")

        assert spec.count_type == CountType.MINIMUM
        assert spec.min_value == 3

    def test_parse_up_to(self):
        """Parses 'up to N' format."""
        spec = parse_count("up to 5")

        assert spec.count_type == CountType.RANGE
        assert spec.max_value == 5

    def test_parse_invalid(self):
        """Raises error for invalid format."""
        with pytest.raises(ValueError):
            parse_count("invalid")

    def test_parse_case_insensitive(self):
        """Parses case-insensitively."""
        spec = parse_count("ABOUT 4")
        assert spec.count_type == CountType.APPROXIMATE


class TestValidateCount:
    """Tests for validate_count function."""

    def test_validate_valid(self):
        """Validates valid count."""
        spec = CountSpecification.range(3, 5)
        is_valid, error = validate_count(4, spec)

        assert is_valid
        assert error is None

    def test_validate_below_minimum(self):
        """Reports below minimum."""
        spec = CountSpecification.range(3, 5)
        is_valid, error = validate_count(2, spec)

        assert not is_valid
        assert "at least 3" in error

    def test_validate_above_maximum(self):
        """Reports above maximum."""
        spec = CountSpecification.range(3, 5)
        is_valid, error = validate_count(6, spec)

        assert not is_valid
        assert "at most 5" in error
