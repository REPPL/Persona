# F-105: Python SDK

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-007, UC-008 |
| **Milestone** | v1.1.0 |
| **Priority** | P0 |
| **Category** | SDK |

## Problem Statement

Developers need to integrate Persona into their applications, scripts, and CI/CD pipelines. The CLI is designed for interactive use and doesn't support programmatic access with proper return types and error handling.

## Design Approach

- Library-first approach (SDK wraps core, CLI wraps SDK)
- Full type hints throughout
- Pydantic models for all inputs/outputs
- Sync and async interfaces
- Same functionality as CLI
- Proper exceptions with context

### SDK Interface

```python
from persona import PersonaGenerator, Experiment
from persona.models import PersonaConfig, GenerationResult

# Create experiment
exp = Experiment.create(
    name="my-experiment",
    data_sources=["./interviews.csv"],
    provider="anthropic",
    model="claude-sonnet-4-5-20250929"
)

# Configure generation
config = PersonaConfig(
    count=3,
    complexity="moderate",
    detail="detailed"
)

# Generate personas
generator = PersonaGenerator(experiment=exp)
result: GenerationResult = generator.generate(config)

# Access results
for persona in result.personas:
    print(f"{persona.name}: {persona.title}")

# Export
result.to_json("./output/")
result.to_markdown("./output/")
```

### Exception Hierarchy

```python
from persona.exceptions import (
    PersonaError,           # Base exception
    ConfigurationError,     # Config issues
    ProviderError,          # LLM provider issues
    ValidationError,        # Schema validation
    BudgetExceededError,    # Cost limit hit
    RateLimitError,         # Rate limited
)
```

## Implementation Tasks

- [ ] Design SDK module structure
- [ ] Create core SDK classes (Experiment, PersonaGenerator)
- [ ] Implement Pydantic models for all types
- [ ] Create exception hierarchy
- [ ] Add type hints throughout
- [ ] Wrap core functionality
- [ ] Create sync interface
- [ ] Write comprehensive docstrings
- [ ] Generate API reference docs
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Create SDK tutorial

## Success Criteria

- [ ] All CLI functionality available via SDK
- [ ] Full type hints pass mypy strict
- [ ] Pydantic validation on all inputs
- [ ] Clear exception messages
- [ ] API reference auto-generated
- [ ] Test coverage ≥ 90%

## Dependencies

- F-004: Persona generation pipeline
- F-006: Experiment management

---

## Related Documentation

- [Milestone v1.1.0](../../milestones/v1.1.0.md)
- [ADR-0021: Programmatic API](../../decisions/adrs/ADR-0021-programmatic-api.md)

