"""
Evidence linking module.

This module provides functionality for linking persona attributes
to their source evidence from the original data.
"""

from persona.core.evidence.linker import (
    AttributeEvidence,
    Evidence,
    EvidenceLinker,
    EvidenceReport,
    EvidenceStrength,
)

__all__ = [
    "EvidenceLinker",
    "Evidence",
    "EvidenceStrength",
    "EvidenceReport",
    "AttributeEvidence",
]
