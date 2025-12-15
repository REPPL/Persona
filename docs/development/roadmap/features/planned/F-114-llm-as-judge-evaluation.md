# F-114: LLM-as-Judge Persona Evaluation

## Overview

| Attribute | Value |
|-----------|-------|
| **Research** | R-013 |
| **Milestone** | v1.4.0 |
| **Priority** | P2 |
| **Category** | Quality |

## Problem Statement

Current quality scoring (F-106) uses heuristic-based metrics that cannot evaluate semantic quality of personas:

- **Coherence** - Do all attributes logically fit together?
- **Realism** - Could this be a believable real person?
- **Usefulness** - Does it inform design decisions?
- **Distinctiveness** - Is it meaningfully different from other personas?

These qualities require semantic understanding that only LLMs can provide. Using frontier models for evaluation is expensive and may raise privacy concerns for sensitive personas. Local LLM-as-judge provides cost-free, private quality assessment.

**Research Finding:** PersonaEval (2025) shows even the best LLMs reach ~69% accuracy on persona role identification, while humans achieve 90.8%. Hybrid human+LLM evaluation recommended for critical decisions.

## Design Approach

- Local LLM evaluates personas against defined criteria
- Integrates with existing F-106 quality scoring system
- Configurable evaluation criteria
- Batch evaluation for efficiency
- Optional frontier model comparison

### Evaluation Pipeline

```
Generated Personas → Local Judge LLM → Quality Scores
                          ↓
                   Multi-Criteria Evaluation
                          ↓
                   Coherence | Realism | Usefulness | Distinctiveness
```

### Python API

```python
from persona.core.evaluation import PersonaJudge, EvaluationCriteria

# Create judge with local model
judge = PersonaJudge(provider="ollama", model="llama3:70b")

# Evaluate single persona
score = judge.evaluate(persona, criteria=[
    EvaluationCriteria.COHERENCE,
    EvaluationCriteria.REALISM,
    EvaluationCriteria.USEFULNESS,
])
# QualityScore(coherence=0.85, realism=0.78, usefulness=0.92, overall=0.85)

# Evaluate batch with distinctiveness
scores = judge.evaluate_batch(personas, criteria=[
    EvaluationCriteria.COHERENCE,
    EvaluationCriteria.REALISM,
    EvaluationCriteria.DISTINCTIVENESS,  # Requires batch context
])

# Compare against frontier model
comparison = judge.compare_to_frontier(
    persona,
    frontier_provider="anthropic",
    frontier_model="claude-sonnet-4-5-20250929"
)
```

### CLI Integration

```bash
# Evaluate personas with local judge
persona evaluate personas.json --judge ollama

# Specify model
persona evaluate personas.json --judge ollama --model qwen2.5:72b

# Evaluate specific criteria
persona evaluate personas.json --judge ollama --criteria coherence,realism

# Output detailed evaluation
persona evaluate personas.json --judge ollama --verbose

# Compare local vs frontier evaluation
persona evaluate personas.json --judge ollama --compare anthropic
```

### Evaluation Criteria

| Criterion | Description | Scoring |
|-----------|-------------|---------|
| **Coherence** | Internal consistency of attributes | 0.0 - 1.0 |
| **Realism** | Believability as a real person | 0.0 - 1.0 |
| **Usefulness** | Value for design decisions | 0.0 - 1.0 |
| **Distinctiveness** | Uniqueness within persona set | 0.0 - 1.0 |
| **Completeness** | Coverage of expected attributes | 0.0 - 1.0 |
| **Specificity** | Detail level and concreteness | 0.0 - 1.0 |

### Evaluation Prompt Template

```
You are evaluating the quality of a user persona. Score each criterion from 0.0 to 1.0.

Persona:
{persona_json}

Evaluate on:
1. COHERENCE: Do demographics, goals, behaviours, and quotes fit together logically?
2. REALISM: Could this be a believable real person? Are details plausible?
3. USEFULNESS: Would this persona help designers make better decisions?

Respond in JSON format:
{
    "coherence": {"score": 0.0-1.0, "reasoning": "..."},
    "realism": {"score": 0.0-1.0, "reasoning": "..."},
    "usefulness": {"score": 0.0-1.0, "reasoning": "..."}
}
```

## Implementation Tasks

- [ ] Create `src/persona/core/evaluation/__init__.py`
- [ ] Create `src/persona/core/evaluation/judge.py` with `PersonaJudge` class
- [ ] Create `src/persona/core/evaluation/criteria.py` with `EvaluationCriteria` enum
- [ ] Create evaluation prompt templates
- [ ] Implement single persona evaluation
- [ ] Implement batch evaluation with distinctiveness
- [ ] Integrate with F-106 quality scoring system
- [ ] Add frontier comparison option
- [ ] Create `persona evaluate` CLI subcommand
- [ ] Add `--judge` flag with provider selection
- [ ] Write unit tests with mocked responses
- [ ] Write integration tests with local Ollama
- [ ] Document evaluation criteria and interpretation
- [ ] Add calibration guidance (what scores mean)

## Success Criteria

- [ ] `persona evaluate personas.json --judge ollama` produces quality scores
- [ ] Scores correlate with human evaluation (target: >70% agreement)
- [ ] Batch evaluation includes distinctiveness scoring
- [ ] Integration with F-106 quality metrics
- [ ] Unit test coverage >= 90%
- [ ] Clear documentation on score interpretation

## Dependencies

- F-107: Native Ollama Provider
- F-106: Quality Metrics Scoring (existing)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| LLM bias in evaluation | Document limitations, recommend human review |
| Inconsistent scores across runs | Use low temperature, average multiple runs |
| Slow evaluation for large batches | Parallel evaluation, progress feedback |
| Model quality affects evaluation | Recommend 70B+ models for judging |

---

## Related Documentation

- [R-013: Local Model Assessment](../../research/R-013-local-model-assessment.md)
- [F-106: Quality Metrics Scoring](../completed/F-106-quality-metrics-scoring.md)
- [F-107: Native Ollama Provider](F-107-native-ollama-provider.md)
- [PersonaEval: Are LLM Evaluators Human Enough?](https://arxiv.org/abs/2508.10014)
