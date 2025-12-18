# Comparing LLM Providers

Learn how to compare persona output across different AI models.

**Level:** Intermediate | **Time:** 20 minutes

## What You'll Learn

- Setting up multiple providers
- Running the same data through different models
- Comparing output quality
- Understanding cost differences
- Choosing the right provider for your needs

## Prerequisites

- Completed [Getting Started](01-getting-started.md)
- API keys for at least two providers

## Why Compare Providers?

Different LLMs produce different results:

| Consideration | Varies By Provider |
|---------------|-------------------|
| **Quality** | Persona depth, consistency, creativity |
| **Cost** | Per-token pricing differs significantly |
| **Speed** | Response times vary |
| **Style** | Writing tone and formatting |
| **Accuracy** | How well grounded in source data |

Comparing helps you choose the best model for your project.

## Step 1: Configure Multiple Providers

Set up API keys for each provider you want to test:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic (Claude)
export ANTHROPIC_API_KEY="sk-ant-..."

# Google (Gemini)
export GOOGLE_API_KEY="..."
```

Verify all are configured:

```bash
persona check
```

**Expected output:**

```
Providers
───────────────────────────────────
OpenAI      ✓ API key configured
            Models: gpt-4o, gpt-4-turbo, gpt-3.5-turbo

Anthropic   ✓ API key configured
            Models: claude-3-opus, claude-3-sonnet, claude-3-haiku

Google      ✓ API key configured
            Models: gemini-pro, gemini-1.5-pro
```

## Step 2: Create a Comparison Experiment

Set up an experiment specifically for comparison:

```bash
persona create experiment
```

Name it `provider-comparison` and add your test data.

## Step 3: Generate with Each Provider

Run generation with each provider, creating separate outputs:

```bash
# OpenAI GPT-4o
persona generate \
  --from provider-comparison \
  --provider openai \
  --model gpt-4o \
  --output-suffix openai-gpt4o

# Anthropic Claude 3 Sonnet
persona generate \
  --from provider-comparison \
  --provider anthropic \
  --model claude-3-sonnet \
  --output-suffix anthropic-sonnet

# Google Gemini Pro
persona generate \
  --from provider-comparison \
  --provider google \
  --model gemini-1.5-pro \
  --output-suffix gemini-pro
```

This creates separate output folders:

```
outputs/
├── 20241213_143022_openai-gpt4o/
├── 20241213_143156_anthropic-sonnet/
└── 20241213_143312_gemini-pro/
```

## Step 4: Compare Outputs

### Quick Comparison

View personas side-by-side:

```bash
persona compare \
  outputs/20241213_143022_openai-gpt4o/personas/01 \
  outputs/20241213_143156_anthropic-sonnet/personas/01
```

**Output:**

```
Persona Comparison
───────────────────────────────────

Attribute       | OpenAI GPT-4o          | Claude 3 Sonnet
----------------|------------------------|------------------------
Name            | Sarah Chen             | Sarah Mitchell
Title           | Mobile Professional    | On-the-Go Manager
Age Range       | 30-35                  | 28-34
Occupation      | Marketing Manager      | Marketing Lead

Goals:
  GPT-4o:    ✓ Mobile efficiency       ✓ Offline access
  Sonnet:    ✓ Quick task completion   ✓ Seamless sync

Pain Points:
  GPT-4o:    ✓ No offline mode         ✓ Complex navigation
  Sonnet:    ✓ Connectivity issues     ✓ Feature overload

Similarity Score: 78%
```

### Detailed Comparison

Export a full comparison report:

```bash
persona compare --all --format markdown > comparison-report.md
```

## Step 5: Analyse Cost vs Quality

Check the cost for each generation:

```bash
cat outputs/20241213_143022_openai-gpt4o/metadata.json | jq '.cost'
cat outputs/20241213_143156_anthropic-sonnet/metadata.json | jq '.cost'
cat outputs/20241213_143312_gemini-pro/metadata.json | jq '.cost'
```

**Typical comparison (3 personas, ~1500 input tokens):**

| Provider | Model | Cost | Quality Notes |
|----------|-------|------|---------------|
| OpenAI | gpt-4o | $0.08 | Rich detail, creative names |
| Anthropic | claude-3-sonnet | $0.05 | Balanced, well-structured |
| Google | gemini-1.5-pro | $0.03 | Concise, sometimes terse |

## Step 6: Quality Evaluation Criteria

Use this rubric to evaluate each output:

### Specificity (1-5)

| Score | Description |
|-------|-------------|
| 1 | Generic statements only |
| 2 | Some specific details |
| 3 | Good mix of general and specific |
| 4 | Rich, specific details throughout |
| 5 | Exceptionally vivid and actionable |

### Consistency (1-5)

| Score | Description |
|-------|-------------|
| 1 | Major contradictions |
| 2 | Some inconsistencies |
| 3 | Mostly consistent |
| 4 | No contradictions, coherent |
| 5 | Perfectly aligned narrative |

### Groundedness (1-5)

| Score | Description |
|-------|-------------|
| 1 | Mostly hallucinated |
| 2 | Some unsupported claims |
| 3 | Generally reflects source data |
| 4 | Well-grounded, clear connections |
| 5 | Every claim traceable to source |

### Distinctiveness (1-5)

| Score | Description |
|-------|-------------|
| 1 | All personas nearly identical |
| 2 | Minor variations only |
| 3 | Clear differences but overlap |
| 4 | Distinct personas, clear segmentation |
| 5 | Vivid, memorable, unique personas |

## Step 7: Record Your Findings

Create a comparison log:

```yaml
# comparison-log.yaml
experiment: provider-comparison
date: 2024-12-13
data_source: "Customer interviews (n=15)"

evaluations:
  - provider: openai
    model: gpt-4o
    cost: 0.08
    scores:
      specificity: 4
      consistency: 5
      groundedness: 4
      distinctiveness: 4
    notes: "Rich creative details, sometimes too elaborate"

  - provider: anthropic
    model: claude-3-sonnet
    cost: 0.05
    scores:
      specificity: 4
      consistency: 4
      groundedness: 5
      distinctiveness: 3
    notes: "Very faithful to source, less creative"

  - provider: google
    model: gemini-1.5-pro
    cost: 0.03
    scores:
      specificity: 3
      consistency: 4
      groundedness: 4
      distinctiveness: 3
    notes: "Concise and accurate, but less depth"

recommendation: "Claude 3 Sonnet for research, GPT-4o for presentations"
```

## Provider Recommendations

Based on common use cases:

| Use Case | Recommended | Why |
|----------|-------------|-----|
| **Research accuracy** | Claude 3 Sonnet | Best groundedness |
| **Stakeholder presentations** | GPT-4o | Rich, engaging detail |
| **Budget-conscious** | Gemini Pro | Lower cost, good quality |
| **Quick iterations** | Claude 3 Haiku | Fast, cheap, good enough |
| **Maximum quality** | Claude 3 Opus | Best overall, highest cost |

## Cost Benchmarks

Approximate costs for generating 5 personas from 2000 tokens of input:

| Model | Input Cost | Output Cost | Total |
|-------|------------|-------------|-------|
| gpt-4o | $0.01 | $0.10 | ~$0.11 |
| gpt-4-turbo | $0.02 | $0.12 | ~$0.14 |
| claude-3-opus | $0.03 | $0.15 | ~$0.18 |
| claude-3-sonnet | $0.01 | $0.05 | ~$0.06 |
| claude-3-haiku | $0.00 | $0.01 | ~$0.01 |
| gemini-1.5-pro | $0.01 | $0.03 | ~$0.04 |

*Prices as of late 2024, subject to change*

## What's Next?

Now that you can compare providers:

1. **[Building a Library](05-building-library.md)** - Organise personas across projects
2. **[Validating Quality](06-validating-quality.md)** - Ensure accuracy with source data
3. **[G-01: Choosing a Provider](../guides/choosing-provider.md)** - Detailed decision guide

---

## Related Documentation

- [F-002: LLM Provider Abstraction](../development/roadmap/features/completed/F-002-llm-provider-abstraction.md)
- [Model Cards Reference](../reference/model-cards.md)
- [G-01: Choosing a Provider](../guides/choosing-provider.md)
