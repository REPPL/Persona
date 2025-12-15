"""
Tests for style checker.

Tests StyleChecker for style adherence validation.
"""

import pytest

from persona.core.generation.parser import Persona
from persona.core.quality.fidelity.models import FidelityConfig, PromptConstraints
from persona.core.quality.fidelity.style import StyleChecker


class TestStyleChecker:
    """Test StyleChecker."""

    def test_simple_check_with_llm_disabled(self):
        """Test simple style checking without LLM."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=["This is a detailed goal with many words"],
            pain_points=["This is a specific pain point"],
        )

        constraints = PromptConstraints(complexity="detailed")
        config = FidelityConfig(use_llm_judge=False)
        checker = StyleChecker(config)

        score, violations = checker.check(persona, constraints)

        assert 0.0 <= score <= 1.0
        assert isinstance(violations, list)

    def test_no_style_constraints(self):
        """Test checking with no style constraints."""
        persona = Persona(id="p1", name="Test User", goals=["Goal"])

        constraints = PromptConstraints()
        config = FidelityConfig(use_llm_judge=False)
        checker = StyleChecker(config)

        score, violations = checker.check(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_simple_complexity_check(self):
        """Test complexity checking via word count."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=["Short"],
            pain_points=["Brief"],
        )

        constraints = PromptConstraints(complexity="simple")
        config = FidelityConfig(use_llm_judge=False)
        checker = StyleChecker(config)

        score, violations = checker.check(persona, constraints)

        # Simple complexity with short entries should be fine
        assert score >= 0.5

    def test_detailed_complexity_requires_longer_text(self):
        """Test that detailed complexity expects longer content."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=["Short goal"],  # Too brief for detailed
            pain_points=["Brief"],
        )

        constraints = PromptConstraints(complexity="detailed")
        config = FidelityConfig(use_llm_judge=False)
        checker = StyleChecker(config)

        score, violations = checker.check(persona, constraints)

        # Should detect that content is too brief
        assert len(violations) > 0 or score < 1.0

    def test_comprehensive_complexity(self):
        """Test comprehensive complexity checking."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=[
                "This is a very comprehensive and detailed goal with extensive explanation",
                "Another long and detailed goal describing specific objectives and outcomes",
            ],
            pain_points=[
                "A comprehensive pain point with detailed explanation of the issue"
            ],
        )

        constraints = PromptConstraints(complexity="comprehensive")
        config = FidelityConfig(use_llm_judge=False)
        checker = StyleChecker(config)

        score, violations = checker.check(persona, constraints)

        # Comprehensive content should pass
        assert score >= 0.8

    def test_llm_check_fallback(self):
        """Test that LLM check falls back to simple check on error."""
        persona = Persona(id="p1", name="Test User", goals=["Goal"])

        constraints = PromptConstraints(style="professional")
        config = FidelityConfig(use_llm_judge=True)
        checker = StyleChecker(config)

        # Should fall back to simple check since LLM is not implemented
        score, violations = checker.check(persona, constraints)

        assert 0.0 <= score <= 1.0

    def test_build_evaluation_prompt(self):
        """Test LLM evaluation prompt building."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=["Goal 1"],
        )

        constraints = PromptConstraints(
            style="professional",
            complexity="detailed",
            custom_rules=["Use technical terms"],
        )

        config = FidelityConfig(use_llm_judge=True)
        checker = StyleChecker(config)

        prompt = checker._build_evaluation_prompt(
            persona, constraints, "Original prompt text"
        )

        # Verify prompt contains key elements
        assert "professional" in prompt
        assert "detailed" in prompt
        assert "Use technical terms" in prompt
        assert "Original prompt text" in prompt
        assert "Test User" in prompt

    def test_empty_persona(self):
        """Test handling of persona with no list fields."""
        persona = Persona(id="p1", name="Test User")

        constraints = PromptConstraints(complexity="detailed")
        config = FidelityConfig(use_llm_judge=False)
        checker = StyleChecker(config)

        score, violations = checker.check(persona, constraints)

        # Should not crash, returns some score
        assert 0.0 <= score <= 1.0
