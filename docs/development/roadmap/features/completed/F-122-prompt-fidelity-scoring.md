# F-122: Prompt Fidelity Scoring

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-007 |
| **Milestone** | v1.7.0 |
| **Priority** | P2 |
| **Category** | Quality |
| **Status** | Complete |

## Problem Statement

LLMs may generate fluent text while ignoring specific instructions, constraints, or formatting requirements. Standard metrics like BLEU/ROUGE don't capture semantic adherence to prompts. Without fidelity scoring, users cannot verify that personas actually reflect the requested characteristics.

## Research Foundation

### Academic Sources

- **IFEval Benchmark**: Programmatically verifiable instruction-following evaluation
- **Scale AI Dataset**: 1,054 instruction-following prompts across 9 categories
- **G-eval (2023)**: Chain-of-thought evaluation for NLG tasks
- **LPG-Bench (2025)**: Long-prompt alignment assessment with TIT-Score

### Key Findings

- Standard evaluation metrics fail to distinguish between fluent text and instruction adherence
- No major LLM delivers fully constraint-compliant outputs without human review
- LLM-as-judge with "reason-first" output improves adherence evaluation
- Specialised frameworks needed for constraint compliance measurement

### Fidelity Dimensions

| Dimension | Description | Example |
|-----------|-------------|---------|
| **Structural** | Schema/format adherence | JSON fields present, types correct |
| **Content** | Requested attributes included | Age range, profession specified |
| **Constraint** | Limits respected | Word count, complexity level |
| **Style** | Tone/voice requirements | Formal, empathetic, technical |

## Design Approach

### Architecture

```
Prompt Template + Generated Persona
              │
              ▼
     ┌────────────────┐
     │ Fidelity Check │
     └───────┬────────┘
             │
    ┌────────┼────────┬────────┐
    │        │        │        │
    ▼        ▼        ▼        ▼
Structure Content  Constraint Style
  Check    Check     Check    Check
    │        │        │        │
    └────────┴────────┴────────┘
             │
             ▼
      FidelityReport
```

### Verification Methods

| Method | Description | Automation |
|--------|-------------|------------|
| **Schema Validation** | JSON schema compliance | Fully automated |
| **Keyword Extraction** | Required terms present | Automated with NLP |
| **Constraint Parsing** | Numeric/length limits | Automated |
| **LLM-as-Judge** | Semantic adherence | Semi-automated |

### Python API

```python
from persona.core.quality.fidelity import (
    FidelityScorer,
    FidelityConfig,
    PromptConstraints,
)

# Define expected constraints
constraints = PromptConstraints(
    required_fields=["name", "age", "goals", "pain_points"],
    age_range=(25, 45),
    goal_count=(3, 5),
    complexity="detailed",
    style="professional",
    custom_rules=[
        "Must include technology-related goals",
        "Pain points should relate to time management",
    ],
)

# Configure scorer
config = FidelityConfig(
    check_structure=True,
    check_content=True,
    check_constraints=True,
    check_style=True,
    use_llm_judge=True,  # For semantic checks
)

# Score fidelity
scorer = FidelityScorer(config)
report = scorer.score(
    persona=generated_persona,
    constraints=constraints,
    original_prompt=prompt_text,
)

# Check results
print(f"Overall fidelity: {report.overall_score:.2f}")
print(f"Structure: {report.structure_score:.2f}")
print(f"Content: {report.content_score:.2f}")
print(f"Constraints: {report.constraint_score:.2f}")
print(f"Style: {report.style_score:.2f}")

for violation in report.violations:
    print(f"  - {violation.dimension}: {violation.description}")
```

### CLI Interface

```bash
# Check prompt fidelity
persona fidelity output/personas.json --prompt prompts/tech-professional.j2

# With explicit constraints
persona fidelity output/ \
    --require-fields name,age,goals \
    --age-range 25-45 \
    --goal-count 3-5

# Batch analysis
persona fidelity output/ --report fidelity-report.md

# Integration with generation
persona generate data.csv --template tech-pro --check-fidelity
```

### Constraint DSL

```yaml
# constraints/tech-professional.yaml
name: Tech Professional Persona
constraints:
  structure:
    required_fields: [name, age, occupation, goals, pain_points, behaviours]
    field_types:
      age: integer
      goals: list

  content:
    occupation_keywords: [developer, engineer, designer, manager, analyst]
    goal_themes: [productivity, learning, collaboration]

  limits:
    age_range: [25, 55]
    goal_count: [3, 6]
    pain_point_count: [2, 5]

  style:
    tone: professional
    detail_level: detailed
    avoid: [slang, excessive_jargon]
```

## Implementation Tasks

- [ ] Create fidelity module structure (`persona/core/quality/fidelity/`)
- [ ] Implement schema validation checker
- [ ] Implement keyword/content presence checker
- [ ] Implement numeric constraint validator
- [ ] Add LLM-as-Judge for semantic fidelity
- [ ] Create constraint DSL parser (YAML format)
- [ ] Implement FidelityReport model
- [ ] Add violation tracking with explanations
- [ ] Add `persona fidelity` CLI command
- [ ] Add `--check-fidelity` flag to generate command
- [ ] Create example constraint files
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Add documentation

## Success Criteria

- [ ] Schema violations detected automatically
- [ ] Content requirements verified with NLP
- [ ] Numeric constraints validated precisely
- [ ] Style adherence assessed via LLM
- [ ] Constraint DSL intuitive and documented
- [ ] CLI integration seamless
- [ ] Test coverage ≥ 85%

## Dependencies

- F-106: Quality Metrics Scoring (framework integration)
- F-114: LLM-as-Judge Evaluation (semantic checking)
- F-019: Persona Validation (schema validation)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Subjective style assessment | High | Medium | Clear rubrics, LLM calibration |
| Constraint DSL complexity | Medium | Medium | Start simple, iterate |
| False negatives on content | Medium | Low | Multiple detection methods |

---

## Related Documentation

- [Milestone v1.7.0](../../milestones/v1.7.0.md)
- [F-114: LLM-as-Judge Evaluation](../completed/F-114-llm-as-judge-evaluation.md)
- [Prompt Templates Reference](../../../../reference/prompt-templates.md)

---

**Status**: Complete
