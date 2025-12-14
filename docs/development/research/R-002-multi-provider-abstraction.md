# R-002: Multi-Provider LLM Abstraction

## Executive Summary

The multi-provider LLM landscape in 2025 offers mature options including LiteLLM (100+ providers, free, open source) and commercial alternatives like Portkey and Bifrost. For Persona's scale and requirements, **LiteLLM** provides the best balance of simplicity, cost, and capability. At v0.1.0 scale, latency overhead (~500µs) is negligible, and the unified API significantly reduces implementation complexity.

## Current State of the Art (2025)

### Industry Standards

Multi-provider LLM abstraction has become essential as organisations use multiple AI providers for:
- **Cost optimisation** - Route to cheaper models for simple tasks
- **Capability matching** - Use best model for each use case
- **Redundancy** - Failover when providers have outages
- **Vendor flexibility** - Avoid lock-in

The industry has converged on two architectural patterns:
1. **SDK-level abstraction** - Libraries like LiteLLM
2. **Gateway/Proxy** - Self-hosted or managed services routing requests

### Academic Research

No significant academic research specific to LLM abstraction layers. The pattern follows standard API gateway and adapter design principles.

### Open Source Ecosystem

| Tool | Type | Providers | Latency Overhead | Cost |
|------|------|-----------|------------------|------|
| **LiteLLM** | SDK + Proxy | 100+ | ~500µs | Free |
| **Bifrost (Maxim AI)** | SDK | 50+ | ~11µs | Free tier |
| **Portkey** | Gateway | Many | Variable | Freemium |
| **OpenRouter** | Managed | 100+ | Variable | Per-token markup |
| **Custom SDK** | SDK | 3 | ~0µs | Dev time |

## Alternatives Analysis

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **LiteLLM** | Free, 100+ providers, unified API, active community | Latency overhead at scale | **Recommended for v0.1.0** |
| **Custom Abstraction** | Zero overhead, full control | High dev time, maintenance burden | Consider for v1.0.0 if needed |
| **Bifrost** | Fastest (50x faster than LiteLLM) | Less mature, smaller community | Monitor for future |
| **Direct SDKs** | Provider-optimised, no abstraction overhead | Code duplication, 3x implementation | Avoid |
| **OpenRouter** | Managed, unified billing | Per-token markup, external dependency | Avoid for self-hosted |

## Recommendation

### Primary Approach

Use **LiteLLM** as the multi-provider abstraction layer:

```python
from litellm import completion

# Provider-agnostic interface
response = completion(
    model="openai/gpt-4o",  # or "anthropic/claude-3-5-sonnet" or "gemini/gemini-1.5-pro"
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_data}
    ],
    temperature=0.7,
    max_tokens=4000
)

# Cost tracking built-in
from litellm import completion_cost
cost = completion_cost(completion_response=response)
```

**Provider Configuration via YAML:**

```yaml
# config/vendors/openai.yaml
provider: openai
api_base: https://api.openai.com/v1
models:
  - gpt-4o
  - gpt-4o-mini
  - gpt-4-turbo

# Environment variable: OPENAI_API_KEY
```

### Rationale

1. **Unified API** - Single interface for OpenAI, Anthropic, Gemini
2. **Cost Tracking** - Built-in `completion_cost()` aligns with F-007 (Cost Estimation)
3. **Token Counting** - Built-in `token_counter()` for pre-generation estimates
4. **Fallback Support** - Automatic retry and failover configuration
5. **Zero Cost** - Completely free and open source
6. **Community** - Large active community, rapid updates

### Implementation Notes

1. **Integration with Instructor** - LiteLLM works seamlessly with Instructor:
   ```python
   import instructor
   from litellm import completion
   
   client = instructor.from_litellm(completion)
   ```

2. **Provider-Specific Features** - Access via `extra_headers` or provider-specific parameters

3. **Observability** - Add Langfuse or Helicone for production monitoring (v0.9.0)

4. **Latency Considerations** - ~500µs overhead is negligible for persona generation (seconds-long operations)

### Hybrid Architecture (Future)

For v1.0.0, if performance becomes critical:
```
User Request → Persona Core → LiteLLM (routing) → Provider SDKs
                    ↓
              Observability (Langfuse)
```

## Impact on Existing Decisions

### ADR Updates Required

**ADR-0002 (Multi-Provider Architecture)** should be updated to:
- Add "Alternatives Considered" section (LiteLLM, custom, Bifrost, direct SDKs)
- Specify LiteLLM as the implementation choice
- Note upgrade path to custom abstraction if needed

### Feature Spec Updates

**F-002 (LLM Provider Abstraction)** should specify:
- LiteLLM as the abstraction library
- Provider configuration via YAML files
- Integration pattern with Instructor

**F-003 (Multi-Provider Support)** should specify:
- Initial providers: OpenAI, Anthropic, Gemini
- Model configuration per provider
- API key sourcing from environment variables

## Sources

- [LiteLLM Documentation](https://docs.litellm.ai/docs/)
- [Top 5 LiteLLM Alternatives 2025](https://www.truefoundry.com/blog/litellm-alternatives)
- [LLM Gateways in 2025](https://dev.to/kuldeep_paul/list-of-top-5-llm-gateways-in-2025-3iak)
- [LiteLLM vs MCP Comparison](https://sider.ai/blog/ai-tools/litellm-vs-model-context-protocol-which-one-should-you-use-in-2025)
- [Pomerium LiteLLM Alternatives](https://www.pomerium.com/blog/litellm-alternatives)

---

## Related Documentation

- [ADR-0002: Multi-Provider Architecture](../decisions/adrs/ADR-0002-multi-provider-architecture.md)
- [F-002: LLM Provider Abstraction](../roadmap/features/completed/F-002-llm-provider-abstraction.md)
- [R-001: Structured LLM Output](./R-001-structured-llm-output.md)
