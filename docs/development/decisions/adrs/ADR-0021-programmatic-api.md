# ADR-0021: Programmatic API Architecture

## Status

Accepted

## Context

Users need programmatic access to Persona for:
- Integrating persona generation into CI/CD pipelines
- Building custom applications on top of Persona
- Automating batch experiments
- Creating web interfaces for non-technical users
- Language-agnostic access via HTTP

The CLI is designed for interactive use and doesn't provide structured return types, proper error handling, or async support needed for programmatic integration.

## Decision

Adopt a **library-first architecture** with an optional REST API:

### Layer 1: Python SDK (v0.5.0)
- Core functionality exposed as importable Python library
- Full type hints with Pydantic models
- Synchronous and asynchronous interfaces
- Same functionality as CLI
- CLI becomes a thin wrapper around SDK

### Layer 2: REST API (v0.9.0, Optional)
- FastAPI-based HTTP server
- OpenAPI documentation auto-generated
- Optional dependency (`pip install persona[api]`)
- Token-based authentication
- Webhooks for long-running operations

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Applications                        │
├─────────────┬─────────────────┬─────────────────────────────┤
│   CLI       │  Python Import  │      HTTP Clients           │
│  (Typer)    │   (SDK)         │   (Any Language)            │
├─────────────┴─────────────────┴─────────────────────────────┤
│                                                              │
│                    persona.sdk (Python SDK)                  │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Experiment  │  │ Generator   │  │ Types (Pydantic)    │  │
│  │ Management  │  │ (Sync/Async)│  │ PersonaConfig       │  │
│  │             │  │             │  │ GenerationResult    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                    persona.api (Optional REST)               │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ FastAPI     │  │ Endpoints   │  │ Webhooks            │  │
│  │ Server      │  │ /experiments│  │ Event Notifications │  │
│  │             │  │ /generate   │  │                     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                    persona.core (Business Logic)             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### SDK Interface Design

```python
from persona import PersonaGenerator, Experiment, AsyncPersonaGenerator
from persona.models import PersonaConfig, GenerationResult
from persona.exceptions import ProviderError, BudgetExceededError

# Synchronous usage
exp = Experiment.create(name="my-exp", data_sources=["data.csv"])
generator = PersonaGenerator(experiment=exp)
result: GenerationResult = generator.generate(PersonaConfig(count=3))

# Asynchronous usage
async def main():
    exp = await Experiment.acreate(name="my-exp", data_sources=["data.csv"])
    generator = AsyncPersonaGenerator(experiment=exp)
    result = await generator.agenerate(PersonaConfig(count=3))
```

## Consequences

**Positive:**
- Clean separation of concerns
- SDK usable without REST overhead
- REST API leverages SDK (no duplication)
- Type safety throughout Python ecosystem
- Async support enables efficient batch processing
- FastAPI provides automatic OpenAPI docs
- Optional API keeps base installation lean

**Negative:**
- More complex architecture than CLI-only
- Must maintain SDK API stability
- REST API adds deployment complexity
- Two interfaces to document

## Alternatives Considered

### REST-First Architecture
**Description:** Build REST API first, SDK calls REST endpoints.
**Pros:** Single implementation, language-agnostic from start.
**Cons:** Network overhead for local Python usage, requires running server.
**Why Not Chosen:** Persona is primarily a Python tool; forcing HTTP for local use adds unnecessary complexity.

### CLI Wrapper with JSON Output
**Description:** Programmatic access via subprocess calling CLI with `--json` output.
**Pros:** Simple, no new code.
**Cons:** No type safety, subprocess overhead, error handling awkward.
**Why Not Chosen:** Poor developer experience, not suitable for production integration.

### gRPC Instead of REST
**Description:** Use gRPC for API layer instead of REST.
**Pros:** Strong typing, efficient binary protocol, streaming support.
**Cons:** More complex setup, requires protobuf compilation, less accessible.
**Why Not Chosen:** REST with OpenAPI provides better accessibility for diverse clients.

### GraphQL Instead of REST
**Description:** Use GraphQL for flexible queries.
**Pros:** Client-defined queries, single endpoint.
**Cons:** Overkill for Persona's simple data model, learning curve.
**Why Not Chosen:** REST endpoints map cleanly to Persona's operations.

## Implementation Notes

### Dependency Management

```toml
# pyproject.toml
[project.optional-dependencies]
api = [
    "fastapi>=0.109",
    "uvicorn>=0.27",
    "python-multipart>=0.0.6",
]
```

### SDK Release Strategy

- SDK released in v0.5.0 alongside Python SDK feature
- REST API released in v0.9.0 as optional component
- CLI refactored to use SDK internally
- Backward compatibility maintained for CLI

---

## Related Documentation

- [F-087: Python SDK](../../roadmap/features/planned/F-087-python-sdk.md)
- [F-088: Async Support](../../roadmap/features/planned/F-088-async-support.md)
- [F-089: REST API](../../roadmap/features/planned/F-089-rest-api.md)
- [F-090: Webhooks](../../roadmap/features/planned/F-090-webhooks.md)
- [F-091: SDK Documentation](../../roadmap/features/planned/F-091-sdk-documentation.md)
- [Milestone v0.5.0](../../roadmap/milestones/v0.5.0.md)
- [Milestone v0.9.0](../../roadmap/milestones/v0.9.0.md)

