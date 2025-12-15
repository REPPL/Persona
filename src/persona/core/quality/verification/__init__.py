"""
Multi-model verification for persona generation (F-120).

This package provides functionality to verify persona generation across
multiple LLM models, detecting model-specific artifacts and hallucinations.

Key Components:
    - VerificationConfig: Configuration for verification runs
    - MultiModelVerifier: Main orchestrator for verification
    - ConsistencyChecker: Measures consistency across outputs
    - VotingStrategy: Determines consensus from multiple outputs
    - VerificationReport: Results and metrics from verification

Example:
    Basic verification across multiple models:

    >>> from persona.core.quality.verification import (
    ...     MultiModelVerifier,
    ...     VerificationConfig,
    ... )
    >>> config = VerificationConfig(
    ...     models=["claude-sonnet-4-20250514", "gpt-4o", "gemini-2.0-flash"],
    ...     samples_per_model=3,
    ...     voting_strategy="majority",
    ... )
    >>> verifier = MultiModelVerifier(config)
    >>> report = await verifier.verify(source_data, count=3)
    >>> print(f"Consistency: {report.consistency_score:.2%}")
    >>> consensus = report.get_consensus_persona()

    Self-consistency check:

    >>> report = await verifier.verify_self_consistency(
    ...     source_data,
    ...     model="claude-sonnet-4",
    ...     samples=5
    ... )

    Convenience functions:

    >>> from persona.core.quality.verification import verify_multi_model
    >>> report = await verify_multi_model(
    ...     data="research.txt",
    ...     models=["claude-sonnet-4", "gpt-4o"],
    ...     count=3,
    ... )
"""

from persona.core.quality.verification.consistency import ConsistencyChecker
from persona.core.quality.verification.dispatcher import (
    ModelDispatcher,
    ModelGenerationResult,
    dispatch_multi_model,
)
from persona.core.quality.verification.models import (
    AttributeAgreement,
    ConsistencyMetrics,
    VerificationConfig,
    VerificationReport,
)
from persona.core.quality.verification.verifier import (
    MultiModelVerifier,
    verify_multi_model,
    verify_multi_model_sync,
    verify_self_consistency,
    verify_self_consistency_sync,
)
from persona.core.quality.verification.voting import (
    MajorityVotingStrategy,
    UnanimousVotingStrategy,
    VotingStrategy,
    WeightedVotingStrategy,
    get_voting_strategy,
)

__all__ = [
    # Main verifier
    "MultiModelVerifier",
    "verify_multi_model",
    "verify_multi_model_sync",
    "verify_self_consistency",
    "verify_self_consistency_sync",
    # Configuration and results
    "VerificationConfig",
    "VerificationReport",
    "ConsistencyMetrics",
    "AttributeAgreement",
    # Components
    "ConsistencyChecker",
    "ModelDispatcher",
    "ModelGenerationResult",
    "dispatch_multi_model",
    # Voting strategies
    "VotingStrategy",
    "MajorityVotingStrategy",
    "UnanimousVotingStrategy",
    "WeightedVotingStrategy",
    "get_voting_strategy",
]
