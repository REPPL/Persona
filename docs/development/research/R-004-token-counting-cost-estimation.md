# R-004: Token Counting & Cost Estimation

## Executive Summary

Token counting is essential for cost transparency before LLM generation. **tiktoken** remains the standard for OpenAI models (3-6x faster than alternatives), while **tokencost** provides multi-provider support including Anthropic's beta token counting API for Claude 3.5+. For Persona, we recommend using **LiteLLM's built-in cost functions** which integrate tiktoken internally and provide unified cost estimation across all three target providers.

## Current State of the Art (2025)

### Industry Standards

Token counting serves two critical purposes:
1. **Pre-generation cost estimation** - Inform users before expensive operations
2. **Context window management** - Avoid exceeding model limits

**Token-to-Text Ratio:** In English, approximately 1 token = 4 characters = 0.75 words. This varies significantly across languages and content types (code has different patterns).

**Output Token Challenge:** Output tokens cannot be known until generation completes. Best practice is to use `max_tokens` parameter to cap output costs.

### Academic Research

No significant academic research specific to token counting economics. The field follows practical engineering approaches.

### Open Source Ecosystem

| Library | Providers | Features | Maintenance |
|---------|-----------|----------|-------------|
| **tiktoken** (OpenAI) | OpenAI models | Official, fast (3-6x) | Active |
| **tokencost** (AgentOps) | 400+ LLMs | Multi-provider, pricing DB | Active |
| **llm_cost_estimation** | Multiple | Cost + token functions | Moderate |
| **LiteLLM** | 100+ | Built-in token_counter, completion_cost | Active |

## Alternatives Analysis

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **LiteLLM (built-in)** | Already our LLM layer, unified API | Less granular control | **Recommended** |
| **tokencost** | 400+ models, maintained pricing | Extra dependency | Consider for pricing accuracy |
| **tiktoken (direct)** | Official OpenAI, fastest | OpenAI-only | Use via LiteLLM |
| **Provider APIs** | Most accurate | Provider-specific code | Not needed |
| **Approximate** | No dependencies | Inaccurate | Avoid |

## Recommendation

### Primary Approach

Use **LiteLLM's built-in cost and token functions**:

```python
from litellm import token_counter, completion_cost, completion

# Pre-generation token counting
input_tokens = token_counter(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_data}
    ]
)

# Estimate cost (input only, output estimated)
estimated_cost = calculate_cost(
    model="gpt-4o",
    input_tokens=input_tokens,
    estimated_output_tokens=4000  # User-configured max
)

# Show user
print(f"Estimated cost: ${estimated_cost:.4f}")
print(f"Input tokens: {input_tokens:,}")
print(f"Max output tokens: 4,000")

# After generation - actual cost
response = completion(model="gpt-4o", messages=messages)
actual_cost = completion_cost(completion_response=response)
```

### Rationale

1. **Single Dependency** - LiteLLM already handles LLM abstraction
2. **Unified Interface** - Same API for all three providers
3. **Maintained Pricing** - LiteLLM updates pricing regularly
4. **Accuracy** - Uses tiktoken internally for OpenAI, appropriate tokenizers for others

### Implementation Notes

**Pricing Configuration (YAML):**

```yaml
# config/models/openai/gpt-4o.yaml
model: gpt-4o
vendor: openai
pricing:
  input_per_1k: 0.0025
  output_per_1k: 0.01
context_window: 128000
max_output: 16384
encoding: cl100k_base  # For tiktoken
```

**Cost Estimation Flow:**

```python
class CostEstimator:
    def estimate(self, data: str, config: ExperimentConfig) -> CostEstimate:
        # Count input tokens
        input_tokens = token_counter(
            model=config.model,
            text=data
        )

        # Load pricing from config
        pricing = self.load_pricing(config.model)

        # Calculate costs
        input_cost = (input_tokens / 1000) * pricing.input_per_1k
        max_output_cost = (config.max_tokens / 1000) * pricing.output_per_1k

        return CostEstimate(
            input_tokens=input_tokens,
            estimated_output_tokens=config.max_tokens,
            input_cost=input_cost,
            max_output_cost=max_output_cost,
            total_estimate=input_cost + max_output_cost,
            currency="USD"
        )
```

**User Display (Rich):**

```
┌─────────────────────────────────────────────┐
│           Cost Estimate                     │
├─────────────────────────────────────────────┤
│ Model:           gpt-4o                     │
│ Input tokens:    12,450                     │
│ Max output:      4,000                      │
├─────────────────────────────────────────────┤
│ Input cost:      $0.0311                    │
│ Max output cost: $0.0400                    │
│ ─────────────────────────────               │
│ Total estimate:  $0.0711                    │
└─────────────────────────────────────────────┘

Proceed with generation? [Y/n]
```

### Pricing Updates

**Strategy:** Bundle pricing in package, update with each release.

```
config/models/
├── openai/
│   ├── gpt-4o.yaml
│   ├── gpt-4o-mini.yaml
│   └── gpt-4-turbo.yaml
├── anthropic/
│   ├── claude-3-5-sonnet.yaml
│   └── claude-3-5-haiku.yaml
└── gemini/
    ├── gemini-1-5-pro.yaml
    └── gemini-1-5-flash.yaml
```

## Impact on Existing Decisions

### ADR Updates Required

**ADR-0010 (Cost Estimation Before Generation)** should be updated to:
- Specify LiteLLM as the token counting implementation
- Add tokencost as alternative considered
- Note pricing update strategy

### Feature Spec Updates

**F-007 (Cost Estimation)** should specify:
- LiteLLM's token_counter and completion_cost functions
- Pricing YAML configuration format
- User confirmation flow

**F-013 (Cost Estimation Before Generation)** should specify:
- Pre-generation estimate display format
- Post-generation actual cost recording

**F-014 (Model-Specific Pricing)** should specify:
- YAML pricing schema
- Update frequency (per release)

## Sources

- [tokencost Library (AgentOps-AI)](https://github.com/AgentOps-AI/tokencost)
- [tiktoken Tutorial (DataCamp)](https://www.datacamp.com/tutorial/estimating-cost-of-gpt-using-tiktoken-library-python)
- [LiteLLM Token Usage & Cost](https://docs.litellm.ai/docs/completion/token_usage)
- [Token Counting Guide (Winder AI)](https://winder.ai/calculating-token-counts-llm-context-windows-practical-guide/)
- [Langfuse Cost Tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking)

---

## Related Documentation

- [ADR-0010: Cost Estimation](../decisions/adrs/ADR-0010-cost-estimation.md)
- [F-007: Cost Estimation](../roadmap/features/completed/F-007-cost-estimation.md)
- [R-002: Multi-Provider Abstraction](./R-002-multi-provider-abstraction.md)
