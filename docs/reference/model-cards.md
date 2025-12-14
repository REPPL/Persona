# Model Cards and Capabilities

Technical reference for supported LLM models and their characteristics.

## Supported Providers

| Provider | Status | API | Authentication |
|----------|--------|-----|----------------|
| OpenAI | Supported | REST | Bearer token |
| Anthropic | Supported | REST | API key header |
| Google (Gemini) | Supported | REST | Query parameter |
| Ollama | Supported | Local | None |

---

## Anthropic Models

### Claude Opus 4.5 (Latest Flagship)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-opus-4-5-20251101` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $15.00 / 1M tokens |
| **Output Price** | $75.00 / 1M tokens |
| **Best For** | Maximum quality, complex reasoning, agentic tasks |

**Characteristics:**
- State-of-the-art across coding, agents, and computer use
- Best vision, reasoning, and mathematics skills
- Hybrid modes: instant responses and extended thinking
- Most expensive option

**Persona Quality:** Excellent

### Claude Sonnet 4.5

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-sonnet-4-5-20250929` |
| **Context Length** | 200,000 tokens (1M with beta header) |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $3.00 / 1M tokens |
| **Output Price** | $15.00 / 1M tokens |
| **Best For** | Best value, coding, agents |

**Characteristics:**
- Best coding model in the world
- Strongest for building complex agents
- Excellent evidence grounding
- **Recommended default**

**Persona Quality:** Excellent

### Claude Opus 4.1

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-opus-4-1-20250805` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $15.00 / 1M tokens |
| **Output Price** | $75.00 / 1M tokens |
| **Best For** | Agentic tasks, real-world coding |

**Characteristics:**
- Upgrade focused on agentic tasks
- Strong reasoning performance
- Available via API and cloud platforms

**Persona Quality:** Excellent

### Claude Sonnet 4

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-sonnet-4-20250514` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $3.00 / 1M tokens |
| **Output Price** | $15.00 / 1M tokens |
| **Best For** | Coding, reasoning, instructions |

**Characteristics:**
- Hybrid model with instant and thinking modes
- Significant upgrade from Sonnet 3.7
- Precise instruction following

**Persona Quality:** Excellent

### Claude Haiku 3.5

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-haiku-3-5-20241022` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $0.80 / 1M tokens |
| **Output Price** | $4.00 / 1M tokens |
| **Best For** | Fast prototyping, high volume |

**Characteristics:**
- Fast and cost-effective
- Good quality for size
- Suitable for iterations

**Persona Quality:** Good

### Claude 3 Opus (Legacy)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-3-opus-20240229` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 4,096 tokens |
| **Input Price** | $15.00 / 1M tokens |
| **Output Price** | $75.00 / 1M tokens |
| **Best For** | Research accuracy (legacy) |

**Status:** Legacy model, consider upgrading to Claude 4.x

### Claude 3 Sonnet (Legacy)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-3-sonnet-20240229` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 4,096 tokens |
| **Input Price** | $3.00 / 1M tokens |
| **Output Price** | $15.00 / 1M tokens |
| **Best For** | Balance (legacy) |

**Status:** Legacy model, consider upgrading to Claude 4.x

### Claude 3 Haiku (Legacy)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `claude-3-haiku-20240307` |
| **Context Length** | 200,000 tokens |
| **Output Limit** | 4,096 tokens |
| **Input Price** | $0.25 / 1M tokens |
| **Output Price** | $1.25 / 1M tokens |
| **Best For** | Fast prototyping (legacy) |

**Status:** Legacy model, still available

---

## OpenAI Models

### GPT-5 (Flagship)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gpt-5-20250807` |
| **Context Length** | 256,000 tokens |
| **Output Limit** | 16,384 tokens |
| **Input Price** | $10.00 / 1M tokens |
| **Output Price** | $30.00 / 1M tokens |
| **Best For** | Maximum quality, multimodal |

**Characteristics:**
- ~45% fewer factual errors than GPT-4o (with search)
- ~80% fewer errors than o3 (with thinking)
- Native multimodal (text, image, audio, video)
- Integrated tool usage and persistent memory

**Persona Quality:** Excellent

### GPT-5.2 (Latest)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gpt-5.2-20251201` |
| **Context Length** | 256,000 tokens |
| **Output Limit** | 16,384 tokens |
| **Input Price** | $12.00 / 1M tokens |
| **Output Price** | $36.00 / 1M tokens |
| **Best For** | Latest capabilities |

**Characteristics:**
- Released December 2025
- Beats GPT-5.1 in almost all benchmarks
- Latest OpenAI flagship

**Persona Quality:** Excellent

### GPT-5 Mini

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gpt-5-mini` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 16,384 tokens |
| **Input Price** | $2.50 / 1M tokens |
| **Output Price** | $7.50 / 1M tokens |
| **Best For** | Cost-effective quality |

**Characteristics:**
- Smaller, more cost-effective GPT-5 variant
- Good balance of quality and cost
- Suitable for most use cases

**Persona Quality:** Very Good

### GPT-4.5 Turbo

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gpt-4.5-turbo` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $5.00 / 1M tokens |
| **Output Price** | $15.00 / 1M tokens |
| **Best For** | Transitional quality |

**Characteristics:**
- Improved reasoning over GPT-4
- Reduced hallucinations
- Being phased out in favour of GPT-5

**Persona Quality:** Excellent

### GPT-4.1

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gpt-4.1` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $2.00 / 1M tokens |
| **Output Price** | $6.00 / 1M tokens |
| **Best For** | Coding, instruction-following |

**Characteristics:**
- Built for coding improvements
- Long-context understanding
- Good value option

**Persona Quality:** Very Good

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

**Persona Quality:** Excellent

### GPT-4o Mini

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gpt-4o-mini` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 16,384 tokens |
| **Input Price** | $0.15 / 1M tokens |
| **Output Price** | $0.60 / 1M tokens |
| **Best For** | Budget processing |

**Characteristics:**
- Very affordable
- Good for high volume
- Reduced quality compared to full GPT-4o

**Persona Quality:** Good

### o4-mini (Reasoning)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `o4-mini` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 16,384 tokens |
| **Input Price** | $1.50 / 1M tokens |
| **Output Price** | $4.50 / 1M tokens |
| **Best For** | Reasoning, math, coding |

**Characteristics:**
- Optimised for fast reasoning
- Best on AIME 2024/2025 benchmarks
- Cost-efficient for complex tasks

**Persona Quality:** Very Good

---

## Google Models

### Gemini 3.0 Pro (Latest Flagship)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-3.0-pro` |
| **Context Length** | 2,000,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $1.25 / 1M tokens |
| **Output Price** | $5.00 / 1M tokens |
| **Best For** | Large datasets, agentic coding |

**Characteristics:**
- Best vibe coding and agentic coding
- Tops WebDev Arena leaderboard (1487 Elo)
- Massive 2M context window
- Released November 2025

**Persona Quality:** Excellent

### Gemini 3.0 Deep Think

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-3.0-deep-think` |
| **Context Length** | 2,000,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $2.50 / 1M tokens |
| **Output Price** | $10.00 / 1M tokens |
| **Best For** | Complex reasoning, novel challenges |

**Characteristics:**
- Outperforms Gemini 3 Pro on complex tasks
- 41.0% on Humanity's Last Exam
- 93.8% on GPQA Diamond
- 45.1% on ARC-AGI-2

**Persona Quality:** Excellent

### Gemini 2.5 Pro

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-2.5-pro` |
| **Context Length** | 2,000,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $1.00 / 1M tokens |
| **Output Price** | $4.00 / 1M tokens |
| **Best For** | General use, reasoning |

**Characteristics:**
- "Thinking model" with reasoning steps
- Enhanced coding capabilities
- Deep Think mode for complex tasks

**Persona Quality:** Excellent

### Gemini 2.5 Flash

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-2.5-flash` |
| **Context Length** | 1,000,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $0.075 / 1M tokens |
| **Output Price** | $0.30 / 1M tokens |
| **Best For** | Fast, cost-effective |

**Characteristics:**
- Improved agentic tool use
- 54% on SWE-Bench Verified
- Native audio output

**Persona Quality:** Good

### Gemini 2.5 Flash-Lite

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-2.5-flash-lite` |
| **Context Length** | 1,000,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $0.02 / 1M tokens |
| **Output Price** | $0.08 / 1M tokens |
| **Best For** | Ultra-low cost, high volume |

**Characteristics:**
- Optimised for speed and cost
- Lowest cost option available
- Good for batch processing

**Persona Quality:** Moderate

### Gemini 1.5 Pro (Legacy)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-1.5-pro` |
| **Context Length** | 2,097,152 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $1.25 / 1M tokens |
| **Output Price** | $5.00 / 1M tokens |
| **Best For** | Large datasets (legacy) |

**Status:** Legacy model, consider upgrading to Gemini 2.5+

### Gemini 1.5 Flash (Legacy)

| Attribute | Value |
|-----------|-------|
| **Model ID** | `gemini-1.5-flash` |
| **Context Length** | 1,048,576 tokens |
| **Output Limit** | 8,192 tokens |
| **Input Price** | $0.075 / 1M tokens |
| **Output Price** | $0.30 / 1M tokens |
| **Best For** | Fast processing (legacy) |

**Status:** Legacy model, consider upgrading to Gemini 2.5+

---

## Local Models (Ollama)

### Llama 3.2 70B

| Attribute | Value |
|-----------|-------|
| **Model ID** | `llama3:70b` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Price** | Free (local compute) |
| **Requirements** | 48GB+ GPU RAM |
| **Best For** | Privacy-sensitive data |

**Characteristics:**
- Complete privacy
- No API costs
- Quality approaches commercial models
- Requires significant hardware

**Persona Quality:** Very Good

### Llama 3.2 8B

| Attribute | Value |
|-----------|-------|
| **Model ID** | `llama3:8b` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Price** | Free (local compute) |
| **Requirements** | 8GB+ GPU RAM |
| **Best For** | Local development |

**Characteristics:**
- Runs on consumer hardware
- Good for prototyping
- Lower quality than 70B

**Persona Quality:** Good

### Qwen 2.5 72B

| Attribute | Value |
|-----------|-------|
| **Model ID** | `qwen2.5:72b` |
| **Context Length** | 128,000 tokens |
| **Output Limit** | 8,192 tokens |
| **Price** | Free (local compute) |
| **Requirements** | 48GB+ GPU RAM |
| **Best For** | Alternative to Llama |

**Characteristics:**
- Strong multilingual support
- Competitive with commercial models
- Good structured output

**Persona Quality:** Very Good

---

## Capability Matrix

| Model | Structured Output | Long Context | Evidence Linking | Speed | Cost |
|-------|-------------------|--------------|------------------|-------|------|
| Claude Opus 4.5 | Excellent | 200K | Excellent | Medium | $$$$ |
| Claude Sonnet 4.5 | Excellent | 200K-1M | Excellent | Fast | $$ |
| Claude Haiku 3.5 | Good | 200K | Good | Fastest | $ |
| GPT-5 | Excellent | 256K | Good | Fast | $$$ |
| GPT-5 Mini | Very Good | 128K | Good | Fast | $$ |
| GPT-4o | Excellent | 128K | Good | Fast | $$ |
| o4-mini | Very Good | 128K | Good | Fast | $ |
| Gemini 3.0 Pro | Excellent | 2M | Good | Fast | $$ |
| Gemini 3.0 Deep Think | Excellent | 2M | Excellent | Medium | $$$ |
| Gemini 2.5 Flash | Good | 1M | Good | Fastest | $ |
| Gemini 2.5 Flash-Lite | Moderate | 1M | Moderate | Fastest | ¢ |
| Llama 3.2 70B | Good | 128K | Good | Slow | Free |

---

## Recommendations by Use Case

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| **General use** | Claude Sonnet 4.5 | Best value, excellent quality |
| **Maximum quality** | Claude Opus 4.5 | Highest accuracy across tasks |
| **Stakeholder presentations** | GPT-5 | Engaging writing, low hallucination |
| **Large datasets** | Gemini 3.0 Pro | 2M context window |
| **Rapid prototyping** | Gemini 2.5 Flash | Fast and cheap |
| **Ultra-budget** | Gemini 2.5 Flash-Lite | Lowest cost |
| **Complex reasoning** | Gemini 3.0 Deep Think | Best on novel challenges |
| **Sensitive data** | Llama 3.2 70B | Complete privacy |
| **Academic research** | Claude Sonnet 4.5 | Evidence grounding |
| **Agentic workflows** | Claude Opus 4.5 | Best for autonomous tasks |

---

## Model Configuration

### Setting Default Model

```bash
# Set default provider and model
persona config set provider.default anthropic
persona config set provider.anthropic.model claude-sonnet-4-5-20250929
```

### Per-Generation Override

```bash
persona generate \
  --from my-experiment \
  --provider openai \
  --model gpt-5-20250807
```

### Temperature Settings

| Setting | Effect | Recommended For |
|---------|--------|-----------------|
| 0.0 | Deterministic | Research, validation |
| 0.5 | Low variation | Production |
| 0.7 | Balanced (default) | General use |
| 1.0 | High variation | Exploration |

---

## Pricing Summary (December 2025)

### By Cost Tier

**Premium ($15+ input):**
- Claude Opus 4.5, Opus 4.1

**Standard ($2-10 input):**
- GPT-5, GPT-5.2, GPT-4.5, Claude Sonnet 4.5, Gemini 3.0 Deep Think

**Budget ($0.50-2 input):**
- GPT-5 Mini, GPT-4.1, o4-mini, Gemini 3.0 Pro, Gemini 2.5 Pro, Claude Haiku 3.5

**Ultra-Budget (<$0.50 input):**
- GPT-4o Mini, Gemini 2.5 Flash, Gemini 2.5 Flash-Lite

**Free (Local):**
- All Ollama models

---

## Related Documentation

- [Provider APIs](provider-apis.md) - API specifications
- [Configuration Reference](configuration-reference.md) - Configuration options
- [G-01: Choosing a Provider](../guides/choosing-provider.md)
- [T-04: Comparing Providers](../tutorials/04-comparing-providers.md)
- [F-002: LLM Provider Abstraction](../development/roadmap/features/planned/F-002-llm-provider-abstraction.md)

