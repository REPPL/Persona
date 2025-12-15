"""
Voting strategies for multi-model consensus (F-120).

This module provides different strategies for determining consensus
across multiple model outputs.
"""

from abc import ABC, abstractmethod
from collections import Counter
from typing import Any

from persona.core.generation.parser import Persona
from persona.core.quality.verification.models import AttributeAgreement


class VotingStrategy(ABC):
    """
    Abstract base class for voting strategies.

    Voting strategies determine which attributes to include in the
    consensus persona based on agreement across models.
    """

    @abstractmethod
    def extract_consensus(
        self,
        personas: list[Persona],
        attribute_details: dict[str, AttributeAgreement],
    ) -> dict[str, Any]:
        """
        Extract consensus attributes from multiple personas.

        Args:
            personas: List of personas from different models.
            attribute_details: Detailed agreement information per attribute.

        Returns:
            Dictionary with consensus attributes.
        """
        ...

    @abstractmethod
    def get_agreed_attributes(
        self,
        attribute_details: dict[str, AttributeAgreement],
    ) -> list[str]:
        """
        Get list of attributes that meet agreement criteria.

        Args:
            attribute_details: Detailed agreement information per attribute.

        Returns:
            List of agreed attribute names.
        """
        ...

    @abstractmethod
    def get_disputed_attributes(
        self,
        attribute_details: dict[str, AttributeAgreement],
    ) -> list[str]:
        """
        Get list of attributes that don't meet agreement criteria.

        Args:
            attribute_details: Detailed agreement information per attribute.

        Returns:
            List of disputed attribute names.
        """
        ...


class MajorityVotingStrategy(VotingStrategy):
    """
    Majority voting strategy.

    Attributes are included if they appear in more than 50% of outputs.
    For attribute values, the most common value is selected.
    """

    def extract_consensus(
        self,
        personas: list[Persona],
        attribute_details: dict[str, AttributeAgreement],
    ) -> dict[str, Any]:
        """Extract consensus using majority rule."""
        consensus = {}

        for attr, details in attribute_details.items():
            if details.agreement_score > 0.5:
                # Attribute is in majority, pick most common value
                consensus[attr] = self._select_majority_value(details.values)

        return consensus

    def get_agreed_attributes(
        self,
        attribute_details: dict[str, AttributeAgreement],
    ) -> list[str]:
        """Get attributes with >50% agreement."""
        return [
            attr for attr, details in attribute_details.items()
            if details.agreement_score > 0.5
        ]

    def get_disputed_attributes(
        self,
        attribute_details: dict[str, AttributeAgreement],
    ) -> list[str]:
        """Get attributes with ≤50% agreement."""
        return [
            attr for attr, details in attribute_details.items()
            if details.agreement_score <= 0.5
        ]

    def _select_majority_value(self, values: list[Any]) -> Any:
        """
        Select the most common value from a list.

        Args:
            values: List of values to vote on.

        Returns:
            Most common value.
        """
        if not values:
            return None

        # For lists, convert to tuples for hashing
        hashable_values = []
        for v in values:
            if isinstance(v, list):
                hashable_values.append(tuple(v))
            elif isinstance(v, dict):
                hashable_values.append(tuple(sorted(v.items())))
            else:
                hashable_values.append(v)

        # Count occurrences
        counter = Counter(hashable_values)
        most_common = counter.most_common(1)[0][0]

        # Convert back to original type
        if isinstance(most_common, tuple):
            # Try to determine if it was a list or dict
            if values and isinstance(values[0], list):
                return list(most_common)
            elif values and isinstance(values[0], dict):
                return dict(most_common)
        return most_common


class UnanimousVotingStrategy(VotingStrategy):
    """
    Unanimous voting strategy.

    Attributes are only included if they appear in ALL outputs.
    This is the most conservative strategy.
    """

    def extract_consensus(
        self,
        personas: list[Persona],
        attribute_details: dict[str, AttributeAgreement],
    ) -> dict[str, Any]:
        """Extract consensus requiring unanimous agreement."""
        consensus = {}

        for attr, details in attribute_details.items():
            if details.agreement_score == 1.0:
                # Attribute is in all outputs
                consensus[attr] = self._select_common_value(details.values)

        return consensus

    def get_agreed_attributes(
        self,
        attribute_details: dict[str, AttributeAgreement],
    ) -> list[str]:
        """Get attributes with 100% agreement."""
        return [
            attr for attr, details in attribute_details.items()
            if details.agreement_score == 1.0
        ]

    def get_disputed_attributes(
        self,
        attribute_details: dict[str, AttributeAgreement],
    ) -> list[str]:
        """Get attributes without unanimous agreement."""
        return [
            attr for attr, details in attribute_details.items()
            if details.agreement_score < 1.0
        ]

    def _select_common_value(self, values: list[Any]) -> Any:
        """
        Select value from unanimous list.

        If all values are identical, return it. Otherwise, combine them.

        Args:
            values: List of values (should all be present).

        Returns:
            Common or combined value.
        """
        if not values:
            return None

        # Check if all values are identical
        first = values[0]
        if all(v == first for v in values):
            return first

        # If lists, combine and deduplicate
        if isinstance(first, list):
            combined = []
            seen = set()
            for value_list in values:
                for item in value_list:
                    item_key = (
                        tuple(sorted(item.items()))
                        if isinstance(item, dict)
                        else item
                    )
                    if item_key not in seen:
                        combined.append(item)
                        seen.add(item_key)
            return combined

        # If dicts, merge
        if isinstance(first, dict):
            merged = {}
            for value_dict in values:
                merged.update(value_dict)
            return merged

        # Otherwise, return first value
        return first


class WeightedVotingStrategy(VotingStrategy):
    """
    Weighted voting strategy.

    Attributes are weighted by model capability scores.
    Models deemed more capable have higher influence.
    """

    def __init__(self, model_weights: dict[str, float] | None = None):
        """
        Initialise weighted voting strategy.

        Args:
            model_weights: Optional weights for each model.
                Format: {'model-name': weight}
                Default: Equal weights (1.0) for all models.
        """
        self.model_weights = model_weights or {}
        self.default_weight = 1.0

    def extract_consensus(
        self,
        personas: list[Persona],
        attribute_details: dict[str, AttributeAgreement],
    ) -> dict[str, Any]:
        """Extract consensus using weighted voting."""
        consensus = {}

        # Calculate weighted agreement threshold
        total_weight = self._calculate_total_weight(personas)
        threshold = total_weight * 0.5  # Weighted majority

        for attr, details in attribute_details.items():
            # Calculate weighted presence
            weighted_presence = self._calculate_weighted_presence(
                attr, personas
            )

            if weighted_presence > threshold:
                # Select value weighted by model capabilities
                consensus[attr] = self._select_weighted_value(
                    attr, personas
                )

        return consensus

    def get_agreed_attributes(
        self,
        attribute_details: dict[str, AttributeAgreement],
    ) -> list[str]:
        """Get attributes meeting weighted majority."""
        # This requires access to personas to calculate weights
        # For simplicity, fall back to simple majority
        return [
            attr for attr, details in attribute_details.items()
            if details.agreement_score > 0.5
        ]

    def get_disputed_attributes(
        self,
        attribute_details: dict[str, AttributeAgreement],
    ) -> list[str]:
        """Get attributes not meeting weighted majority."""
        return [
            attr for attr, details in attribute_details.items()
            if details.agreement_score <= 0.5
        ]

    def _calculate_total_weight(self, personas: list[Persona]) -> float:
        """Calculate total weight across all models."""
        total = 0.0
        for persona in personas:
            model = self._extract_model_name(persona)
            weight = self.model_weights.get(model, self.default_weight)
            total += weight
        return total

    def _calculate_weighted_presence(
        self,
        attribute: str,
        personas: list[Persona],
    ) -> float:
        """Calculate weighted presence of an attribute."""
        presence = 0.0
        for persona in personas:
            persona_dict = persona.to_dict()
            if attribute in persona_dict and persona_dict[attribute]:
                model = self._extract_model_name(persona)
                weight = self.model_weights.get(model, self.default_weight)
                presence += weight
        return presence

    def _select_weighted_value(
        self,
        attribute: str,
        personas: list[Persona],
    ) -> Any:
        """Select value weighted by model capabilities."""
        # Collect values with their weights
        weighted_values: dict[Any, float] = {}

        for persona in personas:
            persona_dict = persona.to_dict()
            if attribute in persona_dict:
                value = persona_dict[attribute]
                model = self._extract_model_name(persona)
                weight = self.model_weights.get(model, self.default_weight)

                # Make value hashable
                hashable_value = self._make_hashable(value)

                if hashable_value in weighted_values:
                    weighted_values[hashable_value] += weight
                else:
                    weighted_values[hashable_value] = weight

        if not weighted_values:
            return None

        # Select value with highest total weight
        best_value = max(weighted_values.items(), key=lambda x: x[1])[0]
        return self._restore_value(best_value)

    def _extract_model_name(self, persona: Persona) -> str:
        """Extract model name from persona."""
        # Check additional fields for model info
        if "model_source" in persona.additional:
            return persona.additional["model_source"]
        # Extract from ID if available
        if ":" in persona.id:
            parts = persona.id.split(":")
            if len(parts) > 1:
                return parts[-1]
        return "unknown"

    def _make_hashable(self, value: Any) -> Any:
        """Convert value to hashable type."""
        if isinstance(value, list):
            return tuple(value)
        elif isinstance(value, dict):
            return tuple(sorted(value.items()))
        return value

    def _restore_value(self, hashable_value: Any) -> Any:
        """Restore original value type."""
        if isinstance(hashable_value, tuple):
            # Try to determine original type
            if hashable_value and isinstance(hashable_value[0], tuple):
                # Was a dict
                return dict(hashable_value)
            # Was a list
            return list(hashable_value)
        return hashable_value


def get_voting_strategy(
    strategy_name: str,
    model_weights: dict[str, float] | None = None,
) -> VotingStrategy:
    """
    Get a voting strategy instance by name.

    Args:
        strategy_name: Name of the strategy ('majority', 'unanimous', 'weighted').
        model_weights: Optional weights for weighted strategy.

    Returns:
        VotingStrategy instance.

    Raises:
        ValueError: If strategy name is invalid.
    """
    strategies = {
        "majority": MajorityVotingStrategy,
        "unanimous": UnanimousVotingStrategy,
        "weighted": WeightedVotingStrategy,
    }

    if strategy_name not in strategies:
        raise ValueError(
            f"Unknown voting strategy: {strategy_name}. "
            f"Must be one of {list(strategies.keys())}"
        )

    strategy_class = strategies[strategy_name]

    if strategy_name == "weighted":
        return strategy_class(model_weights=model_weights)
    else:
        return strategy_class()
