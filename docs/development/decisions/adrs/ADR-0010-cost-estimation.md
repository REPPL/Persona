# ADR-0010: Cost Estimation Before Generation

## Status

Accepted

## Context

LLM API calls cost money. Users need:
- Cost visibility before committing
- Ability to abort if too expensive
- Understanding of cost drivers
- Historical cost tracking

## Decision

Always show cost estimate before generation:
- Token counting for input data
- Model pricing from configuration
- Display estimate with confirmation
- Record actual costs in metadata

## Consequences

**Positive:**
- No surprise costs
- Informed decisions
- Cost awareness
- Historical tracking

**Negative:**
- Estimate may differ from actual
- Requires maintained pricing data
- Extra user confirmation step

## Alternatives Considered

### LiteLLM Built-in (Recommended Implementation)
**Description:** Use LiteLLM's `token_counter` and `completion_cost` functions.
**Pros:** Already our LLM layer, unified API, maintained pricing.
**Cons:** Depends on LiteLLM pricing data freshness.
**Decision:** Use as primary implementation.

### tokencost Library
**Description:** Dedicated token counting and pricing library (AgentOps-AI).
**Pros:** 400+ models, Anthropic API integration for Claude 3.5+.
**Cons:** Additional dependency, potential overlap with LiteLLM.
**Why Not Chosen:** LiteLLM provides sufficient capability; consider if accuracy issues arise.

### tiktoken Direct
**Description:** Use OpenAI's tiktoken directly.
**Pros:** Official, fastest (3-6x), accurate for OpenAI models.
**Cons:** OpenAI-only, need separate tokenizers for other providers.
**Why Not Chosen:** LiteLLM uses tiktoken internally; abstraction preferred.

### Provider APIs
**Description:** Use each provider's token counting API.
**Pros:** Most accurate.
**Cons:** Provider-specific code, extra API calls.
**Why Not Chosen:** Adds latency and complexity.

## Implementation Note

Bundle pricing YAML files with package, update per release. Use `max_tokens` parameter to cap output costs.

## Research Reference

See [R-004: Token Counting & Cost Estimation](../../research/R-004-token-counting-cost-estimation.md) for comprehensive analysis.

---

## Related Documentation

- [F-007: Cost Estimation](../../roadmap/features/planned/F-007-cost-estimation.md)
