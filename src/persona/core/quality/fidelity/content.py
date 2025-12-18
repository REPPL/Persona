"""
Content validation for fidelity scoring.

This module validates that personas contain required keywords, themes,
and content elements as specified in the prompt.
"""


from persona.core.generation.parser import Persona
from persona.core.quality.fidelity.models import PromptConstraints, Severity, Violation


class ContentChecker:
    """
    Check content requirements and presence of keywords/themes.

    Uses simple string matching and presence checks to validate
    that required content elements appear in the persona.
    """

    def check(
        self, persona: Persona, constraints: PromptConstraints
    ) -> tuple[float, list[Violation]]:
        """
        Check content requirements.

        Args:
            persona: Persona to check.
            constraints: Content constraints.

        Returns:
            Tuple of (score 0-1, list of violations).
        """
        violations: list[Violation] = []

        # Check occupation keywords
        if constraints.occupation_keywords:
            occ_violations = self._check_occupation_keywords(persona, constraints)
            violations.extend(occ_violations)

        # Check goal themes
        if constraints.goal_themes:
            goal_violations = self._check_goal_themes(persona, constraints)
            violations.extend(goal_violations)

        # Check required keywords in specific fields
        if constraints.required_keywords:
            keyword_violations = self._check_required_keywords(persona, constraints)
            violations.extend(keyword_violations)

        # Calculate score
        total_checks = (
            len(constraints.occupation_keywords)
            + len(constraints.goal_themes)
            + sum(len(kws) for kws in constraints.required_keywords.values())
        )

        if total_checks == 0:
            return 1.0, violations

        failed_checks = len(violations)
        score = max(0.0, 1.0 - (failed_checks / total_checks))

        return score, violations

    def _check_occupation_keywords(
        self, persona: Persona, constraints: PromptConstraints
    ) -> list[Violation]:
        """Check that occupation contains required keywords."""
        violations: list[Violation] = []

        # Get occupation field
        occupation = self._get_occupation(persona)
        if not occupation:
            violations.append(
                Violation(
                    dimension="content",
                    field="occupation",
                    description="Occupation field is empty",
                    severity=Severity.HIGH,
                    expected="occupation with keywords",
                    actual="empty",
                )
            )
            return violations

        # Check keywords
        occupation_lower = occupation.lower()
        missing_keywords = []

        for keyword in constraints.occupation_keywords:
            if keyword.lower() not in occupation_lower:
                missing_keywords.append(keyword)

        if missing_keywords:
            violations.append(
                Violation(
                    dimension="content",
                    field="occupation",
                    description=f"Occupation missing required keywords: {', '.join(missing_keywords)}",
                    severity=Severity.MEDIUM,
                    expected=f"Contains: {', '.join(constraints.occupation_keywords)}",
                    actual=occupation,
                )
            )

        return violations

    def _check_goal_themes(
        self, persona: Persona, constraints: PromptConstraints
    ) -> list[Violation]:
        """Check that goals contain required themes."""
        violations: list[Violation] = []

        if not persona.goals:
            violations.append(
                Violation(
                    dimension="content",
                    field="goals",
                    description="Goals field is empty",
                    severity=Severity.HIGH,
                    expected=f"Goals containing themes: {', '.join(constraints.goal_themes)}",
                    actual="empty",
                )
            )
            return violations

        # Combine all goals into searchable text
        goals_text = " ".join(persona.goals).lower()

        # Check each theme
        missing_themes = []
        for theme in constraints.goal_themes:
            if theme.lower() not in goals_text:
                missing_themes.append(theme)

        if missing_themes:
            violations.append(
                Violation(
                    dimension="content",
                    field="goals",
                    description=f"Goals missing required themes: {', '.join(missing_themes)}",
                    severity=Severity.MEDIUM,
                    expected=f"Contains themes: {', '.join(constraints.goal_themes)}",
                    actual=f"Found {len(persona.goals)} goals without all themes",
                )
            )

        return violations

    def _check_required_keywords(
        self, persona: Persona, constraints: PromptConstraints
    ) -> list[Violation]:
        """Check that specific fields contain required keywords."""
        violations: list[Violation] = []

        for field_name, keywords in constraints.required_keywords.items():
            # Get field value
            value = self._get_field_text(persona, field_name)
            if not value:
                violations.append(
                    Violation(
                        dimension="content",
                        field=field_name,
                        description=f"Field '{field_name}' is empty",
                        severity=Severity.HIGH,
                        expected=f"Contains keywords: {', '.join(keywords)}",
                        actual="empty",
                    )
                )
                continue

            # Check keywords
            value_lower = value.lower()
            missing_keywords = []

            for keyword in keywords:
                if keyword.lower() not in value_lower:
                    missing_keywords.append(keyword)

            if missing_keywords:
                violations.append(
                    Violation(
                        dimension="content",
                        field=field_name,
                        description=f"Field '{field_name}' missing keywords: {', '.join(missing_keywords)}",
                        severity=Severity.MEDIUM,
                        expected=f"Contains: {', '.join(keywords)}",
                        actual=f"Missing: {', '.join(missing_keywords)}",
                    )
                )

        return violations

    def _get_occupation(self, persona: Persona) -> str | None:
        """Extract occupation from persona demographics or additional fields."""
        # Check demographics first
        if persona.demographics and "occupation" in persona.demographics:
            return str(persona.demographics["occupation"])

        # Check additional fields
        if "occupation" in persona.additional:
            return str(persona.additional["occupation"])

        return None

    def _get_field_text(self, persona: Persona, field_name: str) -> str | None:
        """Get text content from a field for keyword searching."""
        # Handle nested fields like "demographics.age"
        if "." in field_name:
            parts = field_name.split(".", 1)
            parent = getattr(persona, parts[0], None)
            if isinstance(parent, dict):
                value = parent.get(parts[1])
            else:
                return None
        else:
            value = getattr(persona, field_name, None)

        # Convert to searchable text
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return " ".join(str(item) for item in value)
        if isinstance(value, dict):
            return " ".join(str(v) for v in value.values())
        return str(value)
