# Choosing the Right LLM Provider

A decision guide for selecting the optimal LLM provider for your persona generation needs.

## Goal

Choose the best LLM provider based on your specific requirements for quality, cost, privacy, and speed.

## Quick Decision Matrix

| Priority | Recommended Provider | Model |
|----------|---------------------|-------|
| **Best quality** | Anthropic | Claude 3 Opus |
| **Best value** | Anthropic | Claude 3 Sonnet |
| **Lowest cost** | Google | Gemini 1.5 Flash |
| **Fastest** | Anthropic | Claude 3 Haiku |
| **Data privacy** | Self-hosted | Ollama + Llama 3 |

## Provider Comparison

### OpenAI

| Aspect | Rating | Notes |
|--------|--------|-------|
| Quality | ⭐⭐⭐⭐⭐ | GPT-4o excellent for creative personas |
| Cost | ⭐⭐⭐ | Mid-range pricing |
| Speed | ⭐⭐⭐⭐ | Good response times |
| Privacy | ⭐⭐⭐ | Standard terms, API data not used for training |

**Best models:**
- `gpt-4o` - Balanced quality and cost
- `gpt-4-turbo` - Higher quality, higher cost
- `gpt-3.5-turbo` - Budget option, lower quality

**When to use:**
- Need creative, engaging personas
- Already have OpenAI infrastructure
- Value ecosystem integration

### Anthropic (Claude)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Quality | ⭐⭐⭐⭐⭐ | Excellent groundedness |
| Cost | ⭐⭐⭐⭐ | Competitive pricing |
| Speed | ⭐⭐⭐⭐ | Good response times |
| Privacy | ⭐⭐⭐⭐ | Strong privacy stance |

**Best models:**
- `claude-3-opus` - Highest quality
- `claude-3-sonnet` - Best value (recommended default)
- `claude-3-haiku` - Fastest, cheapest

**When to use:**
- Research accuracy is critical
- Need faithful representation of source data
- Value consistent, structured output

### Google (Gemini)

| Aspect | Rating | Notes |
|--------|--------|-------|
| Quality | ⭐⭐⭐⭐ | Good quality, improving |
| Cost | ⭐⭐⭐⭐⭐ | Lowest pricing |
| Speed | ⭐⭐⭐⭐ | Good response times |
| Privacy | ⭐⭐⭐ | Standard Google terms |

**Best models:**
- `gemini-1.5-pro` - Best quality
- `gemini-1.5-flash` - Fast and cheap

**When to use:**
- Budget is primary concern
- Processing large volumes
- Already in Google Cloud ecosystem

## Cost Comparison

**Estimated cost for 5 personas from 2000 tokens of input:**

| Provider | Model | Input | Output | Total |
|----------|-------|-------|--------|-------|
| OpenAI | gpt-4o | $0.01 | $0.10 | $0.11 |
| OpenAI | gpt-4-turbo | $0.02 | $0.12 | $0.14 |
| Anthropic | claude-3-opus | $0.03 | $0.15 | $0.18 |
| Anthropic | claude-3-sonnet | $0.01 | $0.05 | $0.06 |
| Anthropic | claude-3-haiku | $0.00 | $0.01 | $0.01 |
| Google | gemini-1.5-pro | $0.01 | $0.03 | $0.04 |

*Prices as of late 2024, subject to change*

## Quality Characteristics

### OpenAI GPT-4 Series

**Strengths:**
- Creative persona names and backstories
- Engaging writing style
- Good at inferring implicit details

**Weaknesses:**
- Sometimes too creative (adds unsupported details)
- Can be verbose

### Anthropic Claude Series

**Strengths:**
- Excellent groundedness to source data
- Structured, consistent output
- Good at citing evidence

**Weaknesses:**
- Sometimes conservative (less creative)
- Opus is expensive

### Google Gemini Series

**Strengths:**
- Concise output
- Good value
- Fast processing

**Weaknesses:**
- Less depth in personas
- Occasionally misses nuances

## Privacy Considerations

### Data Handling by Provider

| Provider | Training on API Data | Data Retention |
|----------|---------------------|----------------|
| OpenAI | No (API) | 30 days |
| Anthropic | No | As needed |
| Google | Configurable | Configurable |

### Sensitive Data Recommendations

1. **Highly sensitive:** Use self-hosted models (Ollama)
2. **Moderately sensitive:** Use Anthropic or OpenAI API
3. **General data:** Any provider acceptable

### Self-Hosted Option

For maximum privacy:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3:70b

# Configure Persona
persona config set provider.default ollama
persona config set provider.ollama.model llama3:70b
```

## Switching Providers

### Per-Generation Override

```bash
# Use different provider for one generation
persona generate \
  --from my-experiment \
  --provider anthropic \
  --model claude-3-sonnet
```

### Change Default Provider

```bash
# Set new default
persona config set provider.default anthropic
persona config set provider.anthropic.model claude-3-sonnet

# Verify
persona check
```

### Mid-Project Switching

When switching providers mid-project:

1. **Document the change** in experiment metadata
2. **Compare outputs** using `persona compare`
3. **Note differences** for stakeholders

## Recommendations by Use Case

| Use Case | Provider | Model | Reason |
|----------|----------|-------|--------|
| Academic research | Anthropic | Sonnet | Best groundedness |
| Stakeholder presentations | OpenAI | GPT-4o | Engaging personas |
| Rapid prototyping | Anthropic | Haiku | Fast and cheap |
| Large-scale processing | Google | Gemini Flash | Best cost efficiency |
| Sensitive data | Self-hosted | Llama 3 | Full privacy control |
| Maximum quality | Anthropic | Opus | Best overall quality |

## Verification

After choosing a provider, verify it works:

```bash
# Check configuration
persona check

# Expected output
Provider: anthropic
Model: claude-3-sonnet
Status: ✓ Connected

# Test with demo
persona demo --provider anthropic --model claude-3-sonnet
```

---

## Related Documentation

- [T-04: Comparing Providers](../tutorials/04-comparing-providers.md)
- [Model Cards Reference](../reference/model-cards.md)
- [F-002: LLM Provider Abstraction](../development/roadmap/features/planned/F-002-llm-provider-abstraction.md)

