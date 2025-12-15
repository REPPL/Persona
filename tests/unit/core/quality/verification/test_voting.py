"""Tests for voting strategies."""

import pytest

from persona.core.generation.parser import Persona
from persona.core.quality.verification.models import AttributeAgreement
from persona.core.quality.verification.voting import (
    MajorityVotingStrategy,
    UnanimousVotingStrategy,
    WeightedVotingStrategy,
    get_voting_strategy,
)


class TestMajorityVotingStrategy:
    """Tests for MajorityVotingStrategy."""

    def test_extract_consensus_simple(self):
        """Test consensus extraction with simple majority."""
        strategy = MajorityVotingStrategy()

        personas = [
            Persona(id="p1", name="Alice", goals=["Goal 1"]),
            Persona(id="p2", name="Alice", goals=["Goal 1"]),
            Persona(id="p3", name="Bob", goals=["Goal 2"]),
        ]

        attribute_details = {
            "name": AttributeAgreement("name", 3, 3, ["Alice", "Alice", "Bob"]),
            "goals": AttributeAgreement("goals", 3, 3, [["Goal 1"], ["Goal 1"], ["Goal 2"]]),
        }

        consensus = strategy.extract_consensus(personas, attribute_details)

        # Name is in all (100%), should pick most common (Alice)
        assert "name" in consensus
        assert consensus["name"] == "Alice"

        # Goals is in all (100%), should pick most common (["Goal 1"])
        assert "goals" in consensus

    def test_get_agreed_attributes(self):
        """Test getting agreed attributes (>50%)."""
        strategy = MajorityVotingStrategy()

        attribute_details = {
            "name": AttributeAgreement("name", 3, 3),  # 100%
            "goals": AttributeAgreement("goals", 2, 3),  # 67%
            "quotes": AttributeAgreement("quotes", 1, 3),  # 33%
        }

        agreed = strategy.get_agreed_attributes(attribute_details)

        assert "name" in agreed
        assert "goals" in agreed
        assert "quotes" not in agreed

    def test_get_disputed_attributes(self):
        """Test getting disputed attributes (≤50%)."""
        strategy = MajorityVotingStrategy()

        attribute_details = {
            "name": AttributeAgreement("name", 3, 3),  # 100%
            "goals": AttributeAgreement("goals", 2, 3),  # 67%
            "quotes": AttributeAgreement("quotes", 1, 3),  # 33%
        }

        disputed = strategy.get_disputed_attributes(attribute_details)

        assert "name" not in disputed
        assert "goals" not in disputed
        assert "quotes" in disputed

    def test_select_majority_value_simple(self):
        """Test selecting most common value."""
        strategy = MajorityVotingStrategy()

        values = ["Alice", "Alice", "Bob"]
        result = strategy._select_majority_value(values)

        assert result == "Alice"

    def test_select_majority_value_lists(self):
        """Test selecting most common list value."""
        strategy = MajorityVotingStrategy()

        values = [["Goal 1"], ["Goal 1"], ["Goal 2"]]
        result = strategy._select_majority_value(values)

        assert result == ["Goal 1"]

    def test_select_majority_value_dicts(self):
        """Test selecting most common dict value."""
        strategy = MajorityVotingStrategy()

        values = [{"age": 30}, {"age": 30}, {"age": 35}]
        result = strategy._select_majority_value(values)

        assert result == {"age": 30}


class TestUnanimousVotingStrategy:
    """Tests for UnanimousVotingStrategy."""

    def test_extract_consensus_unanimous(self):
        """Test consensus extraction requiring unanimity."""
        strategy = UnanimousVotingStrategy()

        personas = [
            Persona(id="p1", name="Alice", goals=["Goal 1"]),
            Persona(id="p2", name="Alice", goals=["Goal 2"]),
            Persona(id="p3", name="Alice", goals=["Goal 3"]),
        ]

        attribute_details = {
            "name": AttributeAgreement("name", 3, 3, ["Alice", "Alice", "Alice"]),
            "goals": AttributeAgreement("goals", 3, 3, [["Goal 1"], ["Goal 2"], ["Goal 3"]]),
        }

        consensus = strategy.extract_consensus(personas, attribute_details)

        # Name is unanimous
        assert "name" in consensus
        assert consensus["name"] == "Alice"

        # Goals is unanimous but values differ - should combine
        assert "goals" in consensus

    def test_get_agreed_attributes(self):
        """Test getting unanimously agreed attributes."""
        strategy = UnanimousVotingStrategy()

        attribute_details = {
            "name": AttributeAgreement("name", 3, 3),  # 100%
            "goals": AttributeAgreement("goals", 2, 3),  # 67%
            "quotes": AttributeAgreement("quotes", 1, 3),  # 33%
        }

        agreed = strategy.get_agreed_attributes(attribute_details)

        assert "name" in agreed
        assert "goals" not in agreed  # Not unanimous
        assert "quotes" not in agreed

    def test_get_disputed_attributes(self):
        """Test getting non-unanimous attributes."""
        strategy = UnanimousVotingStrategy()

        attribute_details = {
            "name": AttributeAgreement("name", 3, 3),  # 100%
            "goals": AttributeAgreement("goals", 2, 3),  # 67%
        }

        disputed = strategy.get_disputed_attributes(attribute_details)

        assert "name" not in disputed
        assert "goals" in disputed

    def test_select_common_value_identical(self):
        """Test selecting value when all identical."""
        strategy = UnanimousVotingStrategy()

        values = ["Alice", "Alice", "Alice"]
        result = strategy._select_common_value(values)

        assert result == "Alice"

    def test_select_common_value_lists_combine(self):
        """Test combining different list values."""
        strategy = UnanimousVotingStrategy()

        values = [["Goal 1", "Goal 2"], ["Goal 2", "Goal 3"], ["Goal 1"]]
        result = strategy._select_common_value(values)

        # Should combine and deduplicate
        assert isinstance(result, list)
        assert len(result) >= 3

    def test_select_common_value_dicts_merge(self):
        """Test merging different dict values."""
        strategy = UnanimousVotingStrategy()

        values = [{"age": 30}, {"occupation": "Engineer"}, {"age": 30}]
        result = strategy._select_common_value(values)

        # Should merge dicts
        assert isinstance(result, dict)
        assert "age" in result or "occupation" in result


class TestWeightedVotingStrategy:
    """Tests for WeightedVotingStrategy."""

    def test_extract_consensus_equal_weights(self):
        """Test consensus with equal weights (same as majority)."""
        strategy = WeightedVotingStrategy()

        personas = [
            Persona(id="p1", name="Alice", goals=["Goal 1"]),
            Persona(id="p2", name="Alice", goals=["Goal 1"]),
            Persona(id="p3", name="Bob", goals=["Goal 2"]),
        ]

        attribute_details = {
            "name": AttributeAgreement("name", 3, 3, ["Alice", "Alice", "Bob"]),
            "goals": AttributeAgreement("goals", 3, 3, [["Goal 1"], ["Goal 1"], ["Goal 2"]]),
        }

        consensus = strategy.extract_consensus(personas, attribute_details)

        # With equal weights, should behave like majority
        assert "name" in consensus

    def test_extract_consensus_custom_weights(self):
        """Test consensus with custom model weights."""
        model_weights = {
            "model1": 2.0,  # Higher capability
            "model2": 1.0,
            "model3": 1.0,
        }

        strategy = WeightedVotingStrategy(model_weights=model_weights)

        # Create personas with model info
        personas = [
            Persona(id="p1", name="Alice", additional={"model_source": "model1"}),
            Persona(id="p2", name="Bob", additional={"model_source": "model2"}),
            Persona(id="p3", name="Bob", additional={"model_source": "model3"}),
        ]

        attribute_details = {
            "name": AttributeAgreement("name", 3, 3, ["Alice", "Bob", "Bob"]),
        }

        consensus = strategy.extract_consensus(personas, attribute_details)

        # Alice has weight 2.0, Bob has combined weight 2.0
        # Should be tied or close
        assert "name" in consensus

    def test_get_agreed_attributes(self):
        """Test getting agreed attributes with weighted strategy."""
        strategy = WeightedVotingStrategy()

        attribute_details = {
            "name": AttributeAgreement("name", 3, 3),
            "goals": AttributeAgreement("goals", 2, 3),
            "quotes": AttributeAgreement("quotes", 1, 3),
        }

        agreed = strategy.get_agreed_attributes(attribute_details)

        # Falls back to simple majority for this method
        assert "name" in agreed
        assert "goals" in agreed

    def test_calculate_total_weight(self):
        """Test total weight calculation."""
        model_weights = {"model1": 2.0, "model2": 1.5}
        strategy = WeightedVotingStrategy(model_weights=model_weights)

        personas = [
            Persona(id="p1", name="Alice", additional={"model_source": "model1"}),
            Persona(id="p2", name="Bob", additional={"model_source": "model2"}),
            Persona(id="p3", name="Charlie", additional={"model_source": "unknown"}),
        ]

        total = strategy._calculate_total_weight(personas)

        # 2.0 + 1.5 + 1.0 (default) = 4.5
        assert total == 4.5

    def test_calculate_weighted_presence(self):
        """Test weighted presence calculation."""
        model_weights = {"model1": 2.0, "model2": 1.0}
        strategy = WeightedVotingStrategy(model_weights=model_weights)

        personas = [
            Persona(id="p1", name="Alice", goals=["Goal 1"], additional={"model_source": "model1"}),
            Persona(id="p2", name="Bob", goals=["Goal 1"], additional={"model_source": "model2"}),
            Persona(id="p3", name="Charlie", additional={"model_source": "model2"}),  # No goals
        ]

        presence = strategy._calculate_weighted_presence("goals", personas)

        # 2.0 (model1 has goals) + 1.0 (model2 has goals) = 3.0
        assert presence == 3.0

    def test_extract_model_name(self):
        """Test model name extraction."""
        strategy = WeightedVotingStrategy()

        # From model_source in additional
        p1 = Persona(id="p1", name="Alice", additional={"model_source": "gpt-4"})
        assert strategy._extract_model_name(p1) == "gpt-4"

        # From ID if formatted as provider:model
        p2 = Persona(id="anthropic:claude-sonnet-4", name="Bob")
        assert "claude-sonnet-4" in strategy._extract_model_name(p2)

        # Unknown if not available
        p3 = Persona(id="p3", name="Charlie")
        assert strategy._extract_model_name(p3) == "unknown"


class TestGetVotingStrategy:
    """Tests for get_voting_strategy factory function."""

    def test_get_majority_strategy(self):
        """Test getting majority strategy."""
        strategy = get_voting_strategy("majority")
        assert isinstance(strategy, MajorityVotingStrategy)

    def test_get_unanimous_strategy(self):
        """Test getting unanimous strategy."""
        strategy = get_voting_strategy("unanimous")
        assert isinstance(strategy, UnanimousVotingStrategy)

    def test_get_weighted_strategy(self):
        """Test getting weighted strategy."""
        strategy = get_voting_strategy("weighted")
        assert isinstance(strategy, WeightedVotingStrategy)

    def test_get_weighted_strategy_with_weights(self):
        """Test getting weighted strategy with custom weights."""
        weights = {"model1": 2.0}
        strategy = get_voting_strategy("weighted", model_weights=weights)
        assert isinstance(strategy, WeightedVotingStrategy)
        assert strategy.model_weights == weights

    def test_get_invalid_strategy(self):
        """Test error on invalid strategy name."""
        with pytest.raises(ValueError, match="Unknown voting strategy"):
            get_voting_strategy("invalid")
