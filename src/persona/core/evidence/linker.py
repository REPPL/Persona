"""
Evidence linking functionality.

This module provides the EvidenceLinker class for tracking and managing
the provenance of persona attributes from source data.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class EvidenceStrength(Enum):
    """Strength of evidence supporting an attribute."""

    STRONG = "strong"  # Multiple sources, direct quotes
    MODERATE = "moderate"  # Single source or paraphrased
    WEAK = "weak"  # Inferred from context
    INFERRED = "inferred"  # No direct evidence, AI inference


@dataclass
class Evidence:
    """
    A piece of evidence from source data.

    Attributes:
        quote: Direct quote from source.
        source_file: File where evidence was found.
        line_number: Line number in source file.
        participant_id: ID of participant if applicable.
        context: Surrounding context for the quote.
        confidence: Confidence score (0-100).
    """

    quote: str
    source_file: Path | str | None = None
    line_number: int | None = None
    participant_id: str | None = None
    context: str = ""
    confidence: float = 100.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "quote": self.quote,
            "source_file": str(self.source_file) if self.source_file else None,
            "line_number": self.line_number,
            "participant_id": self.participant_id,
            "context": self.context,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Evidence":
        """Create from dictionary."""
        source = data.get("source_file")
        return cls(
            quote=data["quote"],
            source_file=Path(source) if source else None,
            line_number=data.get("line_number"),
            participant_id=data.get("participant_id"),
            context=data.get("context", ""),
            confidence=data.get("confidence", 100.0),
        )


@dataclass
class AttributeEvidence:
    """
    Evidence linking for a specific persona attribute.

    Attributes:
        attribute_name: Name of the attribute (e.g., "goals", "pain_points").
        attribute_value: The attribute value being evidenced.
        evidence: List of supporting evidence.
        strength: Overall strength of evidence.
        notes: Additional notes about the evidence.
    """

    attribute_name: str
    attribute_value: str
    evidence: list[Evidence] = field(default_factory=list)
    strength: EvidenceStrength = EvidenceStrength.INFERRED
    notes: str = ""

    @property
    def evidence_count(self) -> int:
        """Number of evidence items."""
        return len(self.evidence)

    @property
    def has_evidence(self) -> bool:
        """Check if any evidence exists."""
        return len(self.evidence) > 0

    @property
    def average_confidence(self) -> float:
        """Average confidence across all evidence."""
        if not self.evidence:
            return 0.0
        return sum(e.confidence for e in self.evidence) / len(self.evidence)

    def calculate_strength(self) -> EvidenceStrength:
        """Calculate evidence strength based on evidence items."""
        if not self.evidence:
            return EvidenceStrength.INFERRED

        count = len(self.evidence)
        avg_confidence = self.average_confidence

        if count >= 2 and avg_confidence >= 80:
            return EvidenceStrength.STRONG
        elif count >= 1 and avg_confidence >= 60:
            return EvidenceStrength.MODERATE
        elif count >= 1:
            return EvidenceStrength.WEAK
        else:
            return EvidenceStrength.INFERRED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "attribute": self.attribute_name,
            "value": self.attribute_value,
            "strength": self.strength.value,
            "evidence_count": self.evidence_count,
            "average_confidence": round(self.average_confidence, 2),
            "evidence": [e.to_dict() for e in self.evidence],
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AttributeEvidence":
        """Create from dictionary."""
        strength_str = data.get("strength", "inferred")
        try:
            strength = EvidenceStrength(strength_str)
        except ValueError:
            strength = EvidenceStrength.INFERRED

        return cls(
            attribute_name=data["attribute"],
            attribute_value=data["value"],
            evidence=[Evidence.from_dict(e) for e in data.get("evidence", [])],
            strength=strength,
            notes=data.get("notes", ""),
        )


@dataclass
class EvidenceReport:
    """
    Complete evidence report for a persona.

    Attributes:
        persona_id: ID of the persona.
        persona_name: Name of the persona.
        attributes: Evidence for each attribute.
        source_files: List of source files used.
        overall_strength: Overall evidence strength.
        generated_at: When the report was generated.
    """

    persona_id: str
    persona_name: str
    attributes: list[AttributeEvidence] = field(default_factory=list)
    source_files: list[Path] = field(default_factory=list)
    overall_strength: EvidenceStrength = EvidenceStrength.INFERRED
    generated_at: str = ""

    @property
    def total_evidence_count(self) -> int:
        """Total evidence items across all attributes."""
        return sum(a.evidence_count for a in self.attributes)

    @property
    def strong_count(self) -> int:
        """Number of strongly supported attributes."""
        return sum(1 for a in self.attributes if a.strength == EvidenceStrength.STRONG)

    @property
    def weak_count(self) -> int:
        """Number of weakly supported attributes."""
        return sum(
            1
            for a in self.attributes
            if a.strength in (EvidenceStrength.WEAK, EvidenceStrength.INFERRED)
        )

    @property
    def coverage_percentage(self) -> float:
        """Percentage of attributes with evidence."""
        if not self.attributes:
            return 0.0
        evidenced = sum(1 for a in self.attributes if a.has_evidence)
        return (evidenced / len(self.attributes)) * 100

    def calculate_overall_strength(self) -> EvidenceStrength:
        """Calculate overall evidence strength."""
        if not self.attributes:
            return EvidenceStrength.INFERRED

        strengths = [a.strength for a in self.attributes]
        strong = strengths.count(EvidenceStrength.STRONG)
        moderate = strengths.count(EvidenceStrength.MODERATE)

        total = len(strengths)

        if strong >= total * 0.6:
            return EvidenceStrength.STRONG
        elif (strong + moderate) >= total * 0.5:
            return EvidenceStrength.MODERATE
        elif (strong + moderate) >= total * 0.25:
            return EvidenceStrength.WEAK
        else:
            return EvidenceStrength.INFERRED

    def get_attribute(self, name: str) -> AttributeEvidence | None:
        """Get evidence for a specific attribute."""
        for attr in self.attributes:
            if attr.attribute_name == name:
                return attr
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "overall_strength": self.overall_strength.value,
            "total_evidence_count": self.total_evidence_count,
            "coverage_percentage": round(self.coverage_percentage, 2),
            "strong_count": self.strong_count,
            "weak_count": self.weak_count,
            "source_files": [str(f) for f in self.source_files],
            "attributes": [a.to_dict() for a in self.attributes],
            "generated_at": self.generated_at,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvidenceReport":
        """Create from dictionary."""
        strength_str = data.get("overall_strength", "inferred")
        try:
            strength = EvidenceStrength(strength_str)
        except ValueError:
            strength = EvidenceStrength.INFERRED

        return cls(
            persona_id=data["persona_id"],
            persona_name=data["persona_name"],
            attributes=[
                AttributeEvidence.from_dict(a) for a in data.get("attributes", [])
            ],
            source_files=[Path(f) for f in data.get("source_files", [])],
            overall_strength=strength,
            generated_at=data.get("generated_at", ""),
        )


class EvidenceLinker:
    """
    Links persona attributes to their source evidence.

    Provides methods for tracking evidence, generating reports,
    and auditing persona provenance.

    Example:
        linker = EvidenceLinker()
        linker.add_evidence(
            attribute="goals",
            value="Learn Python",
            quote="I want to learn Python for my job",
            source_file=Path("interviews.csv"),
        )
        report = linker.generate_report("p001", "Alice")
    """

    def __init__(self) -> None:
        """Initialise the evidence linker."""
        self._attributes: dict[str, AttributeEvidence] = {}
        self._source_files: set[Path] = set()

    def add_evidence(
        self,
        attribute: str,
        value: str,
        quote: str,
        source_file: Path | str | None = None,
        line_number: int | None = None,
        participant_id: str | None = None,
        context: str = "",
        confidence: float = 100.0,
    ) -> None:
        """
        Add evidence for a persona attribute.

        Args:
            attribute: Attribute name (e.g., "goals").
            value: Attribute value being evidenced.
            quote: Direct quote from source.
            source_file: Source file path.
            line_number: Line number in source.
            participant_id: Participant ID if applicable.
            context: Surrounding context.
            confidence: Confidence score (0-100).
        """
        # Create key for this attribute-value pair
        key = f"{attribute}:{value}"

        # Get or create attribute evidence
        if key not in self._attributes:
            self._attributes[key] = AttributeEvidence(
                attribute_name=attribute,
                attribute_value=value,
            )

        # Add evidence
        evidence = Evidence(
            quote=quote,
            source_file=Path(source_file) if source_file else None,
            line_number=line_number,
            participant_id=participant_id,
            context=context,
            confidence=confidence,
        )
        self._attributes[key].evidence.append(evidence)

        # Update strength
        self._attributes[key].strength = self._attributes[key].calculate_strength()

        # Track source file
        if source_file:
            self._source_files.add(Path(source_file))

    def get_evidence(self, attribute: str, value: str) -> AttributeEvidence | None:
        """
        Get evidence for a specific attribute-value pair.

        Args:
            attribute: Attribute name.
            value: Attribute value.

        Returns:
            AttributeEvidence if found, None otherwise.
        """
        key = f"{attribute}:{value}"
        return self._attributes.get(key)

    def get_all_evidence(self, attribute: str) -> list[AttributeEvidence]:
        """
        Get all evidence for an attribute.

        Args:
            attribute: Attribute name.

        Returns:
            List of AttributeEvidence for this attribute.
        """
        return [
            ae for ae in self._attributes.values() if ae.attribute_name == attribute
        ]

    def generate_report(
        self,
        persona_id: str,
        persona_name: str,
    ) -> EvidenceReport:
        """
        Generate an evidence report.

        Args:
            persona_id: Persona ID.
            persona_name: Persona name.

        Returns:
            Complete EvidenceReport.
        """
        from datetime import datetime

        report = EvidenceReport(
            persona_id=persona_id,
            persona_name=persona_name,
            attributes=list(self._attributes.values()),
            source_files=list(self._source_files),
            generated_at=datetime.now().isoformat(),
        )

        report.overall_strength = report.calculate_overall_strength()

        return report

    def clear(self) -> None:
        """Clear all stored evidence."""
        self._attributes.clear()
        self._source_files.clear()

    def merge(self, other: "EvidenceLinker") -> None:
        """
        Merge evidence from another linker.

        Args:
            other: Another EvidenceLinker to merge.
        """
        for key, attr_evidence in other._attributes.items():
            if key in self._attributes:
                # Merge evidence lists
                self._attributes[key].evidence.extend(attr_evidence.evidence)
                self._attributes[key].strength = self._attributes[
                    key
                ].calculate_strength()
            else:
                self._attributes[key] = attr_evidence

        self._source_files.update(other._source_files)

    def export_audit_report(
        self,
        persona_id: str,
        persona_name: str,
        include_quotes: bool = True,
    ) -> str:
        """
        Export a human-readable audit report.

        Args:
            persona_id: Persona ID.
            persona_name: Persona name.
            include_quotes: Whether to include direct quotes.

        Returns:
            Formatted audit report string.
        """
        report = self.generate_report(persona_id, persona_name)

        lines = [
            "# Evidence Audit Report",
            "",
            f"**Persona:** {persona_name} ({persona_id})",
            f"**Generated:** {report.generated_at}",
            f"**Overall Strength:** {report.overall_strength.value.title()}",
            f"**Coverage:** {report.coverage_percentage:.1f}%",
            f"**Total Evidence Items:** {report.total_evidence_count}",
            "",
            "## Source Files",
            "",
        ]

        for source in report.source_files:
            lines.append(f"- {source}")

        lines.extend(
            [
                "",
                "## Attribute Evidence",
                "",
            ]
        )

        # Group by attribute
        by_attribute: dict[str, list[AttributeEvidence]] = {}
        for attr in report.attributes:
            if attr.attribute_name not in by_attribute:
                by_attribute[attr.attribute_name] = []
            by_attribute[attr.attribute_name].append(attr)

        for attr_name, attr_list in sorted(by_attribute.items()):
            lines.append(f"### {attr_name.replace('_', ' ').title()}")
            lines.append("")

            for attr in attr_list:
                strength_emoji = {
                    EvidenceStrength.STRONG: "🟢",
                    EvidenceStrength.MODERATE: "🟡",
                    EvidenceStrength.WEAK: "🟠",
                    EvidenceStrength.INFERRED: "🔴",
                }.get(attr.strength, "⚪")

                lines.append(
                    f"**{attr.attribute_value}** {strength_emoji} "
                    f"({attr.strength.value}, {attr.evidence_count} source(s))"
                )

                if include_quotes and attr.evidence:
                    for ev in attr.evidence:
                        source_info = ""
                        if ev.source_file:
                            source_info = f" — {ev.source_file}"
                            if ev.line_number:
                                source_info += f":{ev.line_number}"

                        lines.append(f'> "{ev.quote}"{source_info}')

                lines.append("")

        return "\n".join(lines)

    @staticmethod
    def from_persona_data(
        persona_data: dict[str, Any],
        source_files: list[Path] | None = None,
    ) -> "EvidenceLinker":
        """
        Create an EvidenceLinker from persona data with embedded evidence.

        Args:
            persona_data: Persona data dictionary.
            source_files: Optional list of source files.

        Returns:
            EvidenceLinker populated from persona data.
        """
        linker = EvidenceLinker()

        if source_files:
            linker._source_files.update(source_files)

        # Check for evidence field
        evidence_data = persona_data.get("evidence", {})

        for attr_name, attr_evidence in evidence_data.items():
            if isinstance(attr_evidence, list):
                for item in attr_evidence:
                    if isinstance(item, dict):
                        linker.add_evidence(
                            attribute=attr_name,
                            value=item.get("value", ""),
                            quote=item.get("quote", ""),
                            source_file=item.get("source_file"),
                            line_number=item.get("line_number"),
                            participant_id=item.get("participant_id"),
                            confidence=item.get("confidence", 100.0),
                        )

        return linker
