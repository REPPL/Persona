"""
LLM-based persona quality evaluation.

This package provides tools for evaluating persona quality using
LLM judges. Supports local models (via Ollama) and cloud providers.

Example:
    from persona.core.evaluation import PersonaJudge, EvaluationCriteria

    judge = PersonaJudge(provider="ollama", model="qwen2.5:72b")
    result = judge.evaluate(persona, criteria=[
        EvaluationCriteria.COHERENCE,
        EvaluationCriteria.REALISM,
        EvaluationCriteria.USEFULNESS,
    ])
"""

from persona.core.evaluation.criteria import (
    BATCH_CRITERIA,
    COMPREHENSIVE_CRITERIA,
    DEFAULT_CRITERIA,
    EvaluationCriteria,
)
from persona.core.evaluation.judge import PersonaJudge
from persona.core.evaluation.models import (
    BatchEvaluationResult,
    CriterionScore,
    EvaluationResult,
)

__all__ = [
    "PersonaJudge",
    "EvaluationCriteria",
    "CriterionScore",
    "EvaluationResult",
    "BatchEvaluationResult",
    "DEFAULT_CRITERIA",
    "COMPREHENSIVE_CRITERIA",
    "BATCH_CRITERIA",
]
