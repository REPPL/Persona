"""
Tests for fidelity models.

Tests Violation, PromptConstraints, FidelityConfig, and FidelityReport models.
"""


from persona.core.quality.fidelity.models import (
    FidelityConfig,
    FidelityReport,
    PromptConstraints,
    Severity,
    Violation,
)


class TestViolation:
    """Test Violation model."""

    def test_violation_creation(self):
        """Test creating a violation."""
        violation = Violation(
            dimension="structure",
            field="age",
            description="Age is missing",
            severity=Severity.CRITICAL,
            expected="present",
            actual="missing",
        )

        assert violation.dimension == "structure"
        assert violation.field == "age"
        assert violation.severity == Severity.CRITICAL

    def test_violation_to_dict(self):
        """Test converting violation to dictionary."""
        violation = Violation(
            dimension="content",
            field="goals",
            description="Missing keywords",
            severity=Severity.HIGH,
            expected="productivity",
            actual="none",
        )

        result = violation.to_dict()
        assert result["dimension"] == "content"
        assert result["field"] == "goals"
        assert result["severity"] == "high"
        assert result["expected"] == "productivity"

    def test_violation_without_field(self):
        """Test violation without specific field."""
        violation = Violation(
            dimension="style",
            description="Wrong tone",
            severity=Severity.MEDIUM,
        )

        assert violation.field is None
        assert violation.dimension == "style"


class TestPromptConstraints:
    """Test PromptConstraints model."""

    def test_empty_constraints(self):
        """Test creating empty constraints."""
        constraints = PromptConstraints()

        assert constraints.required_fields == []
        assert constraints.field_types == {}
        assert constraints.age_range is None

    def test_full_constraints(self):
        """Test creating full constraints."""
        constraints = PromptConstraints(
            required_fields=["name", "age"],
            field_types={"age": "integer"},
            age_range=(25, 45),
            goal_count=(3, 5),
            complexity="detailed",
            style="professional",
            occupation_keywords=["developer", "engineer"],
        )

        assert constraints.required_fields == ["name", "age"]
        assert constraints.age_range == (25, 45)
        assert constraints.goal_count == (3, 5)
        assert constraints.style == "professional"
        assert "developer" in constraints.occupation_keywords

    def test_constraints_to_dict(self):
        """Test converting constraints to dictionary."""
        constraints = PromptConstraints(
            required_fields=["name"],
            age_range=(20, 30),
        )

        result = constraints.to_dict()
        assert result["required_fields"] == ["name"]
        assert result["age_range"] == (20, 30)
        assert "field_types" in result


class TestFidelityConfig:
    """Test FidelityConfig model."""

    def test_default_config(self):
        """Test default configuration."""
        config = FidelityConfig()

        assert config.check_structure is True
        assert config.check_content is True
        assert config.check_constraints is True
        assert config.check_style is True
        assert config.use_llm_judge is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = FidelityConfig(
            check_structure=True,
            check_style=False,
            use_llm_judge=False,
        )

        assert config.check_structure is True
        assert config.check_style is False
        assert config.use_llm_judge is False

    def test_config_to_dict(self):
        """Test converting config to dictionary."""
        config = FidelityConfig(use_llm_judge=False)

        result = config.to_dict()
        assert result["use_llm_judge"] is False
        assert result["check_structure"] is True


class TestFidelityReport:
    """Test FidelityReport model."""

    def test_empty_report(self):
        """Test creating empty report."""
        report = FidelityReport(
            persona_id="p1",
            persona_name="Test",
            overall_score=0.8,
            structure_score=0.9,
            content_score=0.7,
            constraint_score=0.8,
            style_score=0.8,
        )

        assert report.persona_id == "p1"
        assert report.overall_score == 0.8
        assert report.violations == []
        assert report.passed is True

    def test_report_with_violations(self):
        """Test report with violations."""
        violations = [
            Violation(
                dimension="structure",
                description="Missing field",
                severity=Severity.HIGH,
            ),
            Violation(
                dimension="content",
                description="Missing keyword",
                severity=Severity.MEDIUM,
            ),
        ]

        report = FidelityReport(
            persona_id="p1",
            persona_name="Test",
            overall_score=0.5,
            structure_score=0.4,
            content_score=0.6,
            constraint_score=0.5,
            style_score=0.5,
            violations=violations,
            passed=False,
        )

        assert len(report.violations) == 2
        assert report.violation_count == 2
        assert report.passed is False

    def test_critical_violations_property(self):
        """Test critical violations property."""
        violations = [
            Violation(
                dimension="structure", description="Test", severity=Severity.CRITICAL
            ),
            Violation(dimension="content", description="Test", severity=Severity.HIGH),
            Violation(
                dimension="style", description="Test", severity=Severity.CRITICAL
            ),
        ]

        report = FidelityReport(
            persona_id="p1",
            persona_name="Test",
            overall_score=0.5,
            structure_score=0.5,
            content_score=0.5,
            constraint_score=0.5,
            style_score=0.5,
            violations=violations,
        )

        critical = report.critical_violations
        assert len(critical) == 2
        assert all(v.severity == Severity.CRITICAL for v in critical)

    def test_high_violations_property(self):
        """Test high violations property."""
        violations = [
            Violation(
                dimension="structure", description="Test", severity=Severity.CRITICAL
            ),
            Violation(dimension="content", description="Test", severity=Severity.HIGH),
            Violation(dimension="style", description="Test", severity=Severity.HIGH),
        ]

        report = FidelityReport(
            persona_id="p1",
            persona_name="Test",
            overall_score=0.5,
            structure_score=0.5,
            content_score=0.5,
            constraint_score=0.5,
            style_score=0.5,
            violations=violations,
        )

        high = report.high_violations
        assert len(high) == 2
        assert all(v.severity == Severity.HIGH for v in high)

    def test_violation_by_dimension(self):
        """Test violation counts by dimension."""
        violations = [
            Violation(
                dimension="structure", description="Test", severity=Severity.CRITICAL
            ),
            Violation(
                dimension="structure", description="Test", severity=Severity.HIGH
            ),
            Violation(
                dimension="content", description="Test", severity=Severity.MEDIUM
            ),
        ]

        report = FidelityReport(
            persona_id="p1",
            persona_name="Test",
            overall_score=0.5,
            structure_score=0.5,
            content_score=0.5,
            constraint_score=0.5,
            style_score=0.5,
            violations=violations,
        )

        by_dim = report.violation_by_dimension
        assert by_dim["structure"] == 2
        assert by_dim["content"] == 1

    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        report = FidelityReport(
            persona_id="p1",
            persona_name="Test",
            overall_score=0.85,
            structure_score=0.9,
            content_score=0.8,
            constraint_score=0.85,
            style_score=0.85,
        )

        result = report.to_dict()
        assert result["persona_id"] == "p1"
        assert result["overall_score"] == 0.85
        assert result["violation_count"] == 0
        assert result["passed"] is True
