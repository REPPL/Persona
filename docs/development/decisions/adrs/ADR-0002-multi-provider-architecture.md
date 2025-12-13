# ADR-0002: Multi-Provider LLM Architecture

## Status

Accepted

## Context

Users want flexibility in choosing LLM providers based on:
- Cost considerations
- Model capabilities
- Existing relationships
- Privacy requirements

## Decision

Design with pluggable LLM providers from day one:
- Abstract `LLMProvider` interface
- Provider-specific implementations (OpenAI, Anthropic, Gemini)
- Factory pattern for instantiation
- YAML-based provider configuration

## Consequences

**Positive:**
- Users can switch providers without workflow changes
- Easy to add new providers
- Configuration-driven, no code changes

**Negative:**
- More complex initial architecture
- Must maintain parity across providers

## Alternatives Considered

### LiteLLM (Recommended Implementation)
**Description:** Open-source library providing unified API for 100+ LLM providers.
**Pros:** Free, maintained, built-in cost tracking, extensive provider support.
**Cons:** ~500µs latency overhead per request.
**Decision:** Use as implementation layer. Overhead negligible for persona generation timescales.

### Custom Provider Abstraction
**Description:** Build our own provider interface and implementations.
**Pros:** Zero overhead, full control.
**Cons:** High development/maintenance burden, need to track API changes.
**Why Not Chosen:** LiteLLM provides this with minimal overhead.

### Direct SDK Usage
**Description:** Use each provider's SDK directly (openai, anthropic, google-generativeai).
**Pros:** Provider-optimised, no abstraction overhead.
**Cons:** Code duplication (3x), provider-specific code paths.
**Why Not Chosen:** Violates our multi-provider flexibility goal.

### OpenRouter
**Description:** Managed service routing to multiple providers.
**Pros:** Unified billing, no self-hosting.
**Cons:** Per-token markup, external dependency.
**Why Not Chosen:** Self-hosted approach preferred for v0.1.0.

## Research Reference

See [R-002: Multi-Provider Abstraction](../../research/R-002-multi-provider-abstraction.md) for comprehensive analysis.

---

## Related Documentation

- [F-002: LLM Provider Abstraction](../../roadmap/features/planned/F-002-llm-provider-abstraction.md)
- [System Design](../../planning/architecture/system-design.md)
