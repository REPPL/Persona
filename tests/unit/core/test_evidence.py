"""
Tests for evidence linking functionality (F-024).
"""

from pathlib import Path

from persona.core.evidence import (
    AttributeEvidence,
    Evidence,
    EvidenceLinker,
    EvidenceReport,
    EvidenceStrength,
)


class TestEvidenceStrength:
    """Tests for EvidenceStrength enum."""

    def test_strength_values(self):
        """Test strength enum values."""
        assert EvidenceStrength.STRONG.value == "strong"
        assert EvidenceStrength.MODERATE.value == "moderate"
        assert EvidenceStrength.WEAK.value == "weak"
        assert EvidenceStrength.INFERRED.value == "inferred"


class TestEvidence:
    """Tests for Evidence dataclass."""

    def test_basic_evidence(self):
        """Test creating basic evidence."""
        evidence = Evidence(
            quote="I want to learn Python",
            source_file=Path("interviews.csv"),
            line_number=42,
        )

        assert evidence.quote == "I want to learn Python"
        assert evidence.source_file == Path("interviews.csv")
        assert evidence.line_number == 42
        assert evidence.confidence == 100.0

    def test_evidence_with_all_fields(self):
        """Test evidence with all fields."""
        evidence = Evidence(
            quote="Testing is important",
            source_file=Path("data.csv"),
            line_number=10,
            participant_id="P001",
            context="When asked about practices...",
            confidence=85.0,
        )

        assert evidence.participant_id == "P001"
        assert evidence.context == "When asked about practices..."
        assert evidence.confidence == 85.0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        evidence = Evidence(
            quote="Test quote",
            source_file=Path("test.csv"),
            line_number=5,
        )

        data = evidence.to_dict()

        assert data["quote"] == "Test quote"
        assert data["source_file"] == "test.csv"
        assert data["line_number"] == 5

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "quote": "Test quote",
            "source_file": "data.csv",
            "line_number": 10,
            "confidence": 90.0,
        }

        evidence = Evidence.from_dict(data)

        assert evidence.quote == "Test quote"
        assert evidence.source_file == Path("data.csv")
        assert evidence.confidence == 90.0


class TestAttributeEvidence:
    """Tests for AttributeEvidence dataclass."""

    def test_basic_attribute_evidence(self):
        """Test creating basic attribute evidence."""
        attr = AttributeEvidence(
            attribute_name="goals",
            attribute_value="Learn Python",
        )

        assert attr.attribute_name == "goals"
        assert attr.attribute_value == "Learn Python"
        assert attr.strength == EvidenceStrength.INFERRED
        assert attr.evidence_count == 0

    def test_has_evidence(self):
        """Test has_evidence property."""
        attr = AttributeEvidence(
            attribute_name="goals",
            attribute_value="Learn Python",
        )

        assert attr.has_evidence is False

        attr.evidence.append(Evidence(quote="I want to learn"))
        assert attr.has_evidence is True

    def test_average_confidence(self):
        """Test average confidence calculation."""
        attr = AttributeEvidence(
            attribute_name="goals",
            attribute_value="Test",
            evidence=[
                Evidence(quote="Quote 1", confidence=80.0),
                Evidence(quote="Quote 2", confidence=100.0),
            ],
        )

        assert attr.average_confidence == 90.0

    def test_average_confidence_empty(self):
        """Test average confidence with no evidence."""
        attr = AttributeEvidence(
            attribute_name="goals",
            attribute_value="Test",
        )

        assert attr.average_confidence == 0.0

    def test_calculate_strength_strong(self):
        """Test strength calculation for strong evidence."""
        attr = AttributeEvidence(
            attribute_name="goals",
            attribute_value="Test",
            evidence=[
                Evidence(quote="Q1", confidence=90.0),
                Evidence(quote="Q2", confidence=85.0),
            ],
        )

        strength = attr.calculate_strength()
        assert strength == EvidenceStrength.STRONG

    def test_calculate_strength_moderate(self):
        """Test strength calculation for moderate evidence."""
        attr = AttributeEvidence(
            attribute_name="goals",
            attribute_value="Test",
            evidence=[
                Evidence(quote="Q1", confidence=70.0),
            ],
        )

        strength = attr.calculate_strength()
        assert strength == EvidenceStrength.MODERATE

    def test_calculate_strength_weak(self):
        """Test strength calculation for weak evidence."""
        attr = AttributeEvidence(
            attribute_name="goals",
            attribute_value="Test",
            evidence=[
                Evidence(quote="Q1", confidence=40.0),
            ],
        )

        strength = attr.calculate_strength()
        assert strength == EvidenceStrength.WEAK

    def test_calculate_strength_inferred(self):
        """Test strength calculation for no evidence."""
        attr = AttributeEvidence(
            attribute_name="goals",
            attribute_value="Test",
        )

        strength = attr.calculate_strength()
        assert strength == EvidenceStrength.INFERRED

    def test_to_dict(self):
        """Test conversion to dictionary."""
        attr = AttributeEvidence(
            attribute_name="goals",
            attribute_value="Learn Python",
            strength=EvidenceStrength.MODERATE,
        )

        data = attr.to_dict()

        assert data["attribute"] == "goals"
        assert data["value"] == "Learn Python"
        assert data["strength"] == "moderate"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "attribute": "pain_points",
            "value": "Too complex",
            "strength": "weak",
            "evidence": [],
        }

        attr = AttributeEvidence.from_dict(data)

        assert attr.attribute_name == "pain_points"
        assert attr.attribute_value == "Too complex"
        assert attr.strength == EvidenceStrength.WEAK


class TestEvidenceReport:
    """Tests for EvidenceReport dataclass."""

    def test_basic_report(self):
        """Test creating basic report."""
        report = EvidenceReport(
            persona_id="p001",
            persona_name="Alice",
        )

        assert report.persona_id == "p001"
        assert report.persona_name == "Alice"
        assert report.total_evidence_count == 0

    def test_total_evidence_count(self):
        """Test total evidence counting."""
        report = EvidenceReport(
            persona_id="p001",
            persona_name="Alice",
            attributes=[
                AttributeEvidence(
                    attribute_name="goals",
                    attribute_value="Goal 1",
                    evidence=[Evidence(quote="Q1"), Evidence(quote="Q2")],
                ),
                AttributeEvidence(
                    attribute_name="goals",
                    attribute_value="Goal 2",
                    evidence=[Evidence(quote="Q3")],
                ),
            ],
        )

        assert report.total_evidence_count == 3

    def test_strong_count(self):
        """Test counting strong evidence."""
        report = EvidenceReport(
            persona_id="p001",
            persona_name="Alice",
            attributes=[
                AttributeEvidence(
                    attribute_name="a",
                    attribute_value="v1",
                    strength=EvidenceStrength.STRONG,
                ),
                AttributeEvidence(
                    attribute_name="b",
                    attribute_value="v2",
                    strength=EvidenceStrength.STRONG,
                ),
                AttributeEvidence(
                    attribute_name="c",
                    attribute_value="v3",
                    strength=EvidenceStrength.WEAK,
                ),
            ],
        )

        assert report.strong_count == 2

    def test_weak_count(self):
        """Test counting weak evidence."""
        report = EvidenceReport(
            persona_id="p001",
            persona_name="Alice",
            attributes=[
                AttributeEvidence(
                    attribute_name="a",
                    attribute_value="v1",
                    strength=EvidenceStrength.WEAK,
                ),
                AttributeEvidence(
                    attribute_name="b",
                    attribute_value="v2",
                    strength=EvidenceStrength.INFERRED,
                ),
            ],
        )

        assert report.weak_count == 2

    def test_coverage_percentage(self):
        """Test coverage percentage calculation."""
        report = EvidenceReport(
            persona_id="p001",
            persona_name="Alice",
            attributes=[
                AttributeEvidence(
                    attribute_name="a",
                    attribute_value="v1",
                    evidence=[Evidence(quote="Q")],
                ),
                AttributeEvidence(
                    attribute_name="b",
                    attribute_value="v2",
                    evidence=[],  # No evidence
                ),
            ],
        )

        assert report.coverage_percentage == 50.0

    def test_calculate_overall_strength(self):
        """Test overall strength calculation."""
        report = EvidenceReport(
            persona_id="p001",
            persona_name="Alice",
            attributes=[
                AttributeEvidence(
                    attribute_name="a",
                    attribute_value="v1",
                    strength=EvidenceStrength.STRONG,
                ),
                AttributeEvidence(
                    attribute_name="b",
                    attribute_value="v2",
                    strength=EvidenceStrength.STRONG,
                ),
                AttributeEvidence(
                    attribute_name="c",
                    attribute_value="v3",
                    strength=EvidenceStrength.MODERATE,
                ),
            ],
        )

        strength = report.calculate_overall_strength()
        assert strength == EvidenceStrength.STRONG

    def test_get_attribute(self):
        """Test getting attribute by name."""
        report = EvidenceReport(
            persona_id="p001",
            persona_name="Alice",
            attributes=[
                AttributeEvidence(
                    attribute_name="goals",
                    attribute_value="Goal 1",
                ),
            ],
        )

        attr = report.get_attribute("goals")
        assert attr is not None
        assert attr.attribute_value == "Goal 1"

        missing = report.get_attribute("nonexistent")
        assert missing is None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        report = EvidenceReport(
            persona_id="p001",
            persona_name="Alice",
            overall_strength=EvidenceStrength.MODERATE,
        )

        data = report.to_dict()

        assert data["persona_id"] == "p001"
        assert data["overall_strength"] == "moderate"

    def test_to_json(self):
        """Test JSON export."""
        report = EvidenceReport(
            persona_id="p001",
            persona_name="Alice",
        )

        json_str = report.to_json()
        assert '"persona_id": "p001"' in json_str

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "persona_id": "p002",
            "persona_name": "Bob",
            "overall_strength": "strong",
            "attributes": [],
        }

        report = EvidenceReport.from_dict(data)

        assert report.persona_id == "p002"
        assert report.overall_strength == EvidenceStrength.STRONG


class TestEvidenceLinker:
    """Tests for EvidenceLinker class."""

    def test_init(self):
        """Test initialisation."""
        linker = EvidenceLinker()

        assert len(linker._attributes) == 0
        assert len(linker._source_files) == 0

    def test_add_evidence(self):
        """Test adding evidence."""
        linker = EvidenceLinker()

        linker.add_evidence(
            attribute="goals",
            value="Learn Python",
            quote="I want to learn Python",
            source_file=Path("data.csv"),
            line_number=10,
        )

        evidence = linker.get_evidence("goals", "Learn Python")
        assert evidence is not None
        assert len(evidence.evidence) == 1
        assert evidence.evidence[0].quote == "I want to learn Python"

    def test_add_multiple_evidence(self):
        """Test adding multiple evidence for same attribute."""
        linker = EvidenceLinker()

        linker.add_evidence(
            attribute="goals",
            value="Learn Python",
            quote="Quote 1",
        )
        linker.add_evidence(
            attribute="goals",
            value="Learn Python",
            quote="Quote 2",
        )

        evidence = linker.get_evidence("goals", "Learn Python")
        assert evidence is not None
        assert len(evidence.evidence) == 2

    def test_get_evidence_not_found(self):
        """Test getting non-existent evidence."""
        linker = EvidenceLinker()

        evidence = linker.get_evidence("goals", "Nonexistent")
        assert evidence is None

    def test_get_all_evidence(self):
        """Test getting all evidence for attribute."""
        linker = EvidenceLinker()

        linker.add_evidence(
            attribute="goals",
            value="Goal 1",
            quote="Q1",
        )
        linker.add_evidence(
            attribute="goals",
            value="Goal 2",
            quote="Q2",
        )
        linker.add_evidence(
            attribute="pain_points",
            value="Pain 1",
            quote="P1",
        )

        all_goals = linker.get_all_evidence("goals")
        assert len(all_goals) == 2

        all_pains = linker.get_all_evidence("pain_points")
        assert len(all_pains) == 1

    def test_generate_report(self):
        """Test report generation."""
        linker = EvidenceLinker()

        linker.add_evidence(
            attribute="goals",
            value="Learn Python",
            quote="I want to learn",
            source_file=Path("data.csv"),
        )

        report = linker.generate_report("p001", "Alice")

        assert report.persona_id == "p001"
        assert report.persona_name == "Alice"
        assert len(report.attributes) == 1
        assert len(report.source_files) == 1
        assert report.generated_at != ""

    def test_clear(self):
        """Test clearing evidence."""
        linker = EvidenceLinker()

        linker.add_evidence(
            attribute="goals",
            value="Goal",
            quote="Quote",
            source_file=Path("file.csv"),
        )

        linker.clear()

        assert len(linker._attributes) == 0
        assert len(linker._source_files) == 0

    def test_merge(self):
        """Test merging evidence linkers."""
        linker1 = EvidenceLinker()
        linker1.add_evidence(
            attribute="goals",
            value="Goal 1",
            quote="Q1",
        )

        linker2 = EvidenceLinker()
        linker2.add_evidence(
            attribute="goals",
            value="Goal 2",
            quote="Q2",
        )

        linker1.merge(linker2)

        all_goals = linker1.get_all_evidence("goals")
        assert len(all_goals) == 2

    def test_merge_same_attribute(self):
        """Test merging with same attribute value."""
        linker1 = EvidenceLinker()
        linker1.add_evidence(
            attribute="goals",
            value="Goal 1",
            quote="Q1",
        )

        linker2 = EvidenceLinker()
        linker2.add_evidence(
            attribute="goals",
            value="Goal 1",
            quote="Q2",
        )

        linker1.merge(linker2)

        evidence = linker1.get_evidence("goals", "Goal 1")
        assert evidence is not None
        assert len(evidence.evidence) == 2

    def test_export_audit_report(self):
        """Test audit report export."""
        linker = EvidenceLinker()

        linker.add_evidence(
            attribute="goals",
            value="Learn Python",
            quote="I really want to learn Python",
            source_file=Path("interviews.csv"),
            line_number=42,
        )

        report = linker.export_audit_report("p001", "Alice")

        assert "# Evidence Audit Report" in report
        assert "Alice" in report
        assert "Learn Python" in report
        assert "I really want to learn Python" in report

    def test_export_audit_report_without_quotes(self):
        """Test audit report without quotes."""
        linker = EvidenceLinker()

        linker.add_evidence(
            attribute="goals",
            value="Goal",
            quote="Quote",
        )

        report = linker.export_audit_report("p001", "Alice", include_quotes=False)

        assert "Goal" in report
        assert "Quote" not in report

    def test_from_persona_data(self):
        """Test creating linker from persona data."""
        persona_data = {
            "id": "p001",
            "name": "Alice",
            "evidence": {
                "goals": [
                    {
                        "value": "Learn Python",
                        "quote": "I want to learn",
                        "confidence": 90.0,
                    },
                ],
            },
        }

        linker = EvidenceLinker.from_persona_data(persona_data)

        evidence = linker.get_evidence("goals", "Learn Python")
        assert evidence is not None
        assert evidence.evidence[0].confidence == 90.0

    def test_from_persona_data_with_source_files(self):
        """Test creating linker with source files."""
        persona_data = {"evidence": {}}

        linker = EvidenceLinker.from_persona_data(
            persona_data,
            source_files=[Path("file1.csv"), Path("file2.csv")],
        )

        assert len(linker._source_files) == 2

    def test_strength_auto_calculation(self):
        """Test strength is auto-calculated when adding evidence."""
        linker = EvidenceLinker()

        # Add single evidence - should be moderate
        linker.add_evidence(
            attribute="goals",
            value="Goal",
            quote="Quote 1",
            confidence=80.0,
        )

        evidence = linker.get_evidence("goals", "Goal")
        assert evidence.strength == EvidenceStrength.MODERATE

        # Add second evidence - should become strong
        linker.add_evidence(
            attribute="goals",
            value="Goal",
            quote="Quote 2",
            confidence=90.0,
        )

        evidence = linker.get_evidence("goals", "Goal")
        assert evidence.strength == EvidenceStrength.STRONG

    def test_source_files_tracked(self):
        """Test source files are tracked."""
        linker = EvidenceLinker()

        linker.add_evidence(
            attribute="a",
            value="v1",
            quote="q1",
            source_file="file1.csv",
        )
        linker.add_evidence(
            attribute="b",
            value="v2",
            quote="q2",
            source_file="file2.csv",
        )

        assert len(linker._source_files) == 2
