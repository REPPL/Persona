# Model Cards and Capabilities

Technical reference for supported LLM models and their characteristics.

## Supported Providers

| Provider | Status | API |
|----------|--------|-----|
| OpenAI | ✓ Supported | REST |
| Anthropic | ✓ Supported | REST |
| Google (Gemini) | ✓ Supported | REST |
| Ollama | ✓ Supported | Local |

## OpenAI Models

### GPT-4o

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gpt-4o` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 16,384 tokens |
| **Input Price** | $2.50 / 1M tokens |
| **Output Price** | $10.00 / 1M tokens |
| **Best For** | Balanced quality and cost |

**Characteristics:**
- Excellent creative writing
- Good structured output
- Fast response times
- Strong reasoning

**Persona Quality:** ⭐⭐⭐⭐⭐

### GPT-4 Turbo

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gpt-4-turbo` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 4,096 tokens |
| **Input Price** | $10.00 / 1M tokens |
| **Output Price** | $30.00 / 1M tokens |
| **Best For** | Maximum quality |

**Characteristics:**
- Highest quality output
- Slower than GPT-4o
- More expensive
- Best for final/presentation personas

**Persona Quality:** ⭐⭐⭐⭐⭐

### GPT-3.5 Turbo

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gpt-3.5-turbo` |
| **Context Length** | 16,385 tokens |
| **Output Limit** | 4,096 tokens |
| **Input Price** | $0.50 / 1M tokens |
| **Output Price** | $1.50 / 1M tokens |
| **Best For** | Budget processing |

**Characteristics:**
- Fast and cheap
- Lower quality output
- Good for prototyping
- May miss nuances

**Persona Quality:** ⭐⭐⭐

## Anthropic Models

### Claude 3 Opus

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-3-opus-20240229` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 4,096 tokens |
| **Input Price** | $15.00 / 1M tokens |
| **Output Price** | $75.00 / 1M tokens |
| **Best For** | Research accuracy |

**Characteristics:**
- Best groundedness to source data
- Excellent structured output
- Most expensive option
- Best for validation-critical work

**Persona Quality:** ⭐⭐⭐⭐⭐

### Claude 3 Sonnet

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-3-sonnet-20240229` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 4,096 tokens |
| **Input Price** | $3.00 / 1M tokens |
| **Output Price** | $15.00 / 1M tokens |
| **Best For** | Best value |

**Characteristics:**
- Excellent balance of quality/cost
- Strong evidence grounding
- Reliable structured output
- **Recommended default**

**Persona Quality:** ⭐⭐⭐⭐⭐

### Claude 3 Haiku

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-3-haiku-20240307` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 4,096 tokens |
| **Input Price** | $0.25 / 1M tokens |
| **Output Price** | $1.25 / 1M tokens |
| **Best For** | Fast prototyping |

**Characteristics:**
- Extremely fast
- Very low cost
- Reduced quality
- Good for iterations

**Persona Quality:** ⭐⭐⭐⭐

## Google Models

### Gemini 1.5 Pro

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-1.5-pro` |
| **Context Length** | 2,097,152 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $1.25 / 1M tokens |
| **Output Price** | $5.00 / 1M tokens |
| **Best For** | Large datasets |

**Characteristics:**
- Massive context window
- Good for batch processing
- Competitive pricing
- Strong multimodal

**Persona Quality:** ⭐⭐⭐⭐

### Gemini 1.5 Flash

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-1.5-flash` |
| **Context Length** | 1,048,576 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $0.075 / 1M tokens |
| **Output Price** | $0.30 / 1M tokens |
| **Best For** | Lowest cost |

**Characteristics:**
- Fastest response
- Lowest cost option
- Reduced quality
- Good for high volume

**Persona Quality:** ⭐⭐⭐

## Local Models (Ollama)

### Llama 3 70B

| Attribute | Value |
|-----------|-------|
| **Model ID** | `llama3:70b` |
| **Context Length** | 8,192 tokens |
| **Output Limit** | 2,048 tokens |
| **Price** | Free (local compute) |
| **Requirements** | 48GB+ GPU RAM |
| **Best For** | Privacy-sensitive data |

**Characteristics:**
- Complete privacy
- No API costs
- Requires significant hardware
- Quality approaches commercial models

**Persona Quality:** ⭐⭐⭐⭐

### Llama 3 8B

| Attribute | Value |
|-----------|-------|
| **Model ID** | `llama3:8b` |
| **Context Length** | 8,192 tokens |
| **Output Limit** | 2,048 tokens |
| **Price** | Free (local compute) |
| **Requirements** | 8GB+ GPU RAM |
| **Best For** | Local development |

**Characteristics:**
- Runs on consumer hardware
- No API costs
- Lower quality
- Fast for local

**Persona Quality:** ⭐⭐⭐

## Capability Matrix

| Model | Structured Output | Long Context | Evidence Linking | Speed |
|-------|-------------------|--------------|------------------|-------|
| GPT-4o | ✓ Excellent | ✓ 128K | ✓ Good | Fast |
| GPT-4 Turbo | ✓ Excellent | ✓ 128K | ✓ Good | Medium |
| GPT-3.5 | ✓ Good | ⚠ 16K | ⚠ Fair | Fast |
| Claude 3 Opus | ✓ Excellent | ✓ 200K | ✓ Excellent | Medium |
| Claude 3 Sonnet | ✓ Excellent | ✓ 200K | ✓ Excellent | Fast |
| Claude 3 Haiku | ✓ Good | ✓ 200K | ✓ Good | Fastest |
| Gemini 1.5 Pro | ✓ Good | ✓ 2M | ✓ Good | Fast |
| Gemini 1.5 Flash | ✓ Fair | ✓ 1M | ⚠ Fair | Fastest |
| Llama 3 70B | ✓ Good | ⚠ 8K | ⚠ Fair | Slow |

## Recommendations by Use Case

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| **General use** | Claude 3 Sonnet | Best value |
| **Maximum quality** | Claude 3 Opus | Highest accuracy |
| **Stakeholder presentations** | GPT-4o | Engaging writing |
| **Large datasets** | Gemini 1.5 Pro | 2M context |
| **Rapid prototyping** | Claude 3 Haiku | Fast and cheap |
| **Budget processing** | Gemini 1.5 Flash | Lowest cost |
| **Sensitive data** | Llama 3 70B | Full privacy |
| **Academic research** | Claude 3 Sonnet | Evidence grounding |

## Model Configuration

### Setting Default Model

```bash
# Set default provider and model
persona config set provider.default anthropic
persona config set provider.anthropic.model claude-3-sonnet-20240229
```

### Per-Generation Override

```bash
persona generate \
  --from my-experiment \
  --provider openai \
  --model gpt-4o
```

### Temperature Settings

| Setting | Effect | Recommended For |
|---------|--------|-----------------|
| 0.0 | Deterministic | Research, validation |
| 0.5 | Low variation | Production |
| 0.7 | Balanced (default) | General use |
| 1.0 | High variation | Exploration |

---

## Related Documentation

- [G-01: Choosing a Provider](../guides/choosing-provider.md)
- [T-04: Comparing Providers](../tutorials/04-comparing-providers.md)
- [F-002: LLM Provider Abstraction](../development/roadmap/features/planned/F-002-llm-provider-abstraction.md)

