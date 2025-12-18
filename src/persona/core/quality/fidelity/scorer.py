"""
Fidelity scorer orchestrator.

This module coordinates all fidelity checks and produces
comprehensive fidelity reports for personas.
"""


from persona.core.generation.parser import Persona
from persona.core.quality.fidelity.constraints import ConstraintValidator
from persona.core.quality.fidelity.content import ContentChecker
from persona.core.quality.fidelity.models import (
    FidelityConfig,
    FidelityReport,
    PromptConstraints,
    Violation,
)
from persona.core.quality.fidelity.schema import SchemaValidator
from persona.core.quality.fidelity.style import StyleChecker


class FidelityScorer:
    """
    Orchestrate fidelity scoring across all dimensions.

    Coordinates structural, content, constraint, and style checks
    to produce comprehensive fidelity reports.
    """

    def __init__(self, config: FidelityConfig | None = None):
        """
        Initialise the fidelity scorer.

        Args:
            config: Fidelity configuration. Uses defaults if not provided.
        """
        self.config = config or FidelityConfig()

        # Initialise validators
        self.schema_validator = SchemaValidator()
        self.content_checker = ContentChecker()
        self.constraint_validator = ConstraintValidator()
        self.style_checker = StyleChecker(self.config)

    def score(
        self,
        persona: Persona,
        constraints: PromptConstraints,
        original_prompt: str | None = None,
    ) -> FidelityReport:
        """
        Score persona fidelity against constraints.

        Args:
            persona: Persona to score.
            constraints: Constraints to validate against.
            original_prompt: Original prompt text for context (optional).

        Returns:
            FidelityReport with comprehensive assessment.
        """
        all_violations: list[Violation] = []
        scores: dict[str, float] = {}
        details: dict[str, any] = {}

        # Run structural validation
        if self.config.check_structure:
            structure_score, structure_violations = self.schema_validator.validate(
                persona, constraints
            )
            scores["structure"] = structure_score
            all_violations.extend(structure_violations)
            details["structure"] = {
                "violations": len(structure_violations),
                "checked": True,
            }
        else:
            scores["structure"] = 1.0
            details["structure"] = {"checked": False}

        # Run content validation
        if self.config.check_content:
            content_score, content_violations = self.content_checker.check(
                persona, constraints
            )
            scores["content"] = content_score
            all_violations.extend(content_violations)
            details["content"] = {
                "violations": len(content_violations),
                "checked": True,
            }
        else:
            scores["content"] = 1.0
            details["content"] = {"checked": False}

        # Run constraint validation
        if self.config.check_constraints:
            (
                constraint_score,
                constraint_violations,
            ) = self.constraint_validator.validate(persona, constraints)
            scores["constraint"] = constraint_score
            all_violations.extend(constraint_violations)
            details["constraint"] = {
                "violations": len(constraint_violations),
                "checked": True,
            }
        else:
            scores["constraint"] = 1.0
            details["constraint"] = {"checked": False}

        # Run style validation
        if self.config.check_style:
            style_score, style_violations = self.style_checker.check(
                persona, constraints, original_prompt
            )
            scores["style"] = style_score
            all_violations.extend(style_violations)
            details["style"] = {
                "violations": len(style_violations),
                "checked": True,
                "llm_judge_used": self.config.use_llm_judge,
            }
        else:
            scores["style"] = 1.0
            details["style"] = {"checked": False}

        # Calculate overall score (weighted average)
        overall_score = self._calculate_overall_score(scores)

        # Determine if passed
        # Pass if overall score >= 0.6 and no critical violations
        passed = overall_score >= 0.6 and not any(
            v.severity.value == "critical" for v in all_violations
        )

        return FidelityReport(
            persona_id=persona.id,
            persona_name=persona.name,
            overall_score=overall_score,
            structure_score=scores["structure"],
            content_score=scores["content"],
            constraint_score=scores["constraint"],
            style_score=scores["style"],
            violations=all_violations,
            passed=passed,
            details=details,
        )

    def _calculate_overall_score(self, scores: dict[str, float]) -> float:
        """
        Calculate weighted overall score.

        Weights:
        - Structure: 35% (most critical)
        - Content: 25% (important)
        - Constraint: 25% (important)
        - Style: 15% (least critical)

        Args:
            scores: Dictionary of dimension scores.

        Returns:
            Weighted overall score (0-1).
        """
        weights = {
            "structure": 0.35,
            "content": 0.25,
            "constraint": 0.25,
            "style": 0.15,
        }

        weighted_sum = sum(scores[dim] * weights[dim] for dim in scores)
        return weighted_sum
