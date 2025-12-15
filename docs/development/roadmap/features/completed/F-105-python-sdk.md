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

- [x] Design SDK module structure
- [x] Create core SDK classes (PersonaClient, PersonaGenerator, ExperimentSDK)
- [x] Implement Pydantic models for all types
- [x] Create exception hierarchy
- [x] Add type hints throughout
- [x] Wrap core functionality
- [x] Create sync interface
- [x] Create async interface (AsyncPersonaGenerator, AsyncExperimentSDK)
- [x] Add configuration system (SDKConfig with env vars, config file support)
- [x] Write comprehensive docstrings
- [x] Generate API reference docs
- [x] Write unit tests (226 tests)
- [x] Write integration tests
- [x] Create SDK tutorial and quickstart guide

## Success Criteria

- [x] All CLI functionality available via SDK
- [x] Full type hints throughout
- [x] Pydantic validation on all inputs
- [x] Clear exception messages with context
- [x] API reference auto-generated
- [x] Test coverage ≥ 90% (226 tests passing)

## Dependencies

- F-004: Persona generation pipeline
- F-006: Experiment management

---

## Implementation Summary

The Python SDK has been successfully implemented with the following components:

### Core SDK Classes

- **PersonaClient**: High-level convenience wrapper for simple use cases
- **PersonaGenerator**: Full-featured sync generator
- **AsyncPersonaGenerator**: Async generator with concurrent batch support
- **ExperimentSDK**: Experiment management SDK
- **AsyncExperimentSDK**: Async experiment management

### Configuration System

- **SDKConfig**: Multi-source configuration (env vars, config file, defaults)
- Environment variable support (PERSONA_*)
- YAML configuration file support (~/.persona/config.yaml)
- Priority-based config merging

### Models & Validation

- PersonaConfig, ExperimentConfig
- PersonaModel, GenerationResultModel, ExperimentModel
- Full Pydantic validation with clear error messages

### Exception Hierarchy

Complete exception hierarchy with context:
- PersonaError (base)
- ConfigurationError, ValidationError, DataError
- ProviderError, RateLimitError, BudgetExceededError
- GenerationError

### Testing

226 unit tests covering:
- All SDK classes and methods
- Configuration loading from multiple sources
- Error handling and exception hierarchy
- Async functionality
- Integration scenarios

### Documentation

- SDK Quickstart tutorial
- SDK Patterns guide
- Auto-generated API reference
- Error handling guide

---

## Related Documentation

- [Milestone v1.1.0](../../milestones/v1.1.0.md)
- [SDK Quickstart](../../../tutorials/sdk-quickstart.md)
- [SDK Patterns Guide](../../../guides/sdk-patterns.md)
- [API Reference](../../../reference/api.md)
- [ADR-0021: Programmatic API](../../decisions/adrs/ADR-0021-programmatic-api.md)

---

**Status**: Complete

