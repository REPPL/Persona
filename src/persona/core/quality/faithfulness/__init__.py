"""
Faithfulness and hallucination detection package.

This package provides comprehensive faithfulness validation for personas,
detecting hallucinations and unsupported claims through:

1. Claim extraction from persona attributes
2. Semantic matching to source data
3. Optional HHEM-based classification

Example:
    from persona.core.quality.faithfulness import FaithfulnessValidator

    validator = FaithfulnessValidator(llm_provider, embedding_provider)
    report = validator.validate(persona, source_data)

    print(f"Faithfulness: {report.faithfulness_score}%")
    for claim in report.unsupported_claims:
        print(f"Unsupported: {claim.text}")
"""

from persona.core.quality.faithfulness.extractor import ClaimExtractor
from persona.core.quality.faithfulness.hhem import HHEMClassifier
from persona.core.quality.faithfulness.matcher import SourceMatcher
from persona.core.quality.faithfulness.models import (
    Claim,
    ClaimType,
    FaithfulnessReport,
    SourceMatch,
)
from persona.core.quality.faithfulness.validator import FaithfulnessValidator

__all__ = [
    "Claim",
    "ClaimExtractor",
    "ClaimType",
    "FaithfulnessReport",
    "FaithfulnessValidator",
    "HHEMClassifier",
    "SourceMatch",
    "SourceMatcher",
]
