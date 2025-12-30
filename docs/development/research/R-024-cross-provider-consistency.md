# R-024: Cross-Provider Consistency Analysis

Research into understanding and measuring how persona generation quality varies across different LLM providers.

## Executive Summary

This document evaluates methods for analysing and reporting consistency differences between LLM providers when generating personas from the same input data.

**Key Finding:** Different providers produce systematically different personas even with identical prompts and data. Understanding these differences is crucial for reproducibility, provider selection, and quality assurance.

**Recommendation:** Implement a **cross-provider consistency framework** with automated comparison reports, enabling users to make informed provider choices and verify results across models.

---

## Context

### Current Multi-Provider State

Persona v1.11.0 supports:

| Provider | Models | Use Case |
|----------|--------|----------|
| **Anthropic** | Claude 3.5 Sonnet, Claude 3 Opus, Haiku | Primary, high quality |
| **OpenAI** | GPT-4o, GPT-4 Turbo, GPT-3.5 | Alternative, widely used |
| **Google** | Gemini Pro, Gemini Ultra | Alternative |
| **Ollama** | Llama 3, Mistral, Qwen | Local, privacy-preserving |

### The Consistency Problem

**Observation:** Same prompt + same data → different personas across providers

**Causes:**
- Different training data and methods
- Different alignment approaches
- Different response styles (verbose vs concise)
- Different JSON formatting tendencies
- Temperature and sampling differences

**Impact:**
- Results not reproducible across providers
- Difficulty comparing provider quality
- User confusion about "correct" output
- Testing challenges

---

## Consistency Dimensions

### Dimension 1: Structural Consistency

**What:** Does the output structure match expectations?

| Aspect | Measure | Target |
|--------|---------|--------|
| Schema compliance | % fields present | 100% |
| Field types | Correct types | 100% |
| Array lengths | Expected counts | ±10% |
| Nesting depth | Matches schema | Exact |

**Example Variation:**
```json
// Claude: Nested structure
{ "goals": { "primary": [...], "secondary": [...] } }

// GPT-4: Flat structure
{ "primary_goals": [...], "secondary_goals": [...] }
```

### Dimension 2: Content Consistency

**What:** Is the semantic content similar?

| Aspect | Measure | Target |
|--------|---------|--------|
| Key themes | Theme overlap % | >80% |
| Persona count | Requested vs actual | Exact |
| Attribute coverage | All required attributes | 100% |
| Evidence linkage | Citations present | >90% |

**Example Variation:**
```
# Claude: Detailed motivations
"Sarah is driven by a need for work-life balance, stemming from her
experience as a working mother in a demanding tech role..."

# GPT-4: Bullet-style motivations
"Motivations: Work-life balance, career growth, family time"
```

### Dimension 3: Stylistic Consistency

**What:** How does the writing style vary?

| Aspect | Measure | Range |
|--------|---------|-------|
| Verbosity | Words per persona | 200-800 |
| Sentence length | Avg words/sentence | 12-25 |
| Formality | Formal/informal ratio | Variable |
| First/third person | Perspective consistency | Variable |

### Dimension 4: Quality Consistency

**What:** Does quality vary by provider?

| Aspect | Measure | Target |
|--------|---------|--------|
| Coherence score | Internal consistency | >0.8 |
| Faithfulness score | Source alignment | >0.7 |
| Diversity score | Persona uniqueness | >0.6 |
| Bias score | Stereotype avoidance | <0.3 |

---

## Measurement Framework

### Automated Comparison Pipeline

```
Input Data
    ↓
┌─────────────────────────────────────────────┐
│ Generate with each provider                  │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ │Anthropic│ │ OpenAI  │ │ Gemini  │ │ Ollama  │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Normalise outputs                            │
│ - Schema alignment                           │
│ - Field name mapping                         │
│ - Type coercion                              │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Compute comparison metrics                   │
│ - Structural similarity                      │
│ - Semantic similarity (embeddings)           │
│ - Quality scores (existing metrics)          │
│ - Statistical analysis                       │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ Generate consistency report                  │
│ - Provider comparison matrix                 │
│ - Significant differences                    │
│ - Recommendations                            │
└─────────────────────────────────────────────┘
```

### Comparison Metrics

#### Semantic Similarity

```python
def compute_semantic_similarity(
    personas_a: list[Persona],
    personas_b: list[Persona]
) -> float:
    """Compute average semantic similarity between persona sets."""
    embeddings_a = [embed(p.to_text()) for p in personas_a]
    embeddings_b = [embed(p.to_text()) for p in personas_b]

    # Optimal matching using Hungarian algorithm
    cost_matrix = 1 - cosine_similarity_matrix(embeddings_a, embeddings_b)
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    return 1 - cost_matrix[row_ind, col_ind].mean()
```

#### Structural Alignment

```python
def compute_structural_alignment(
    personas_a: list[Persona],
    personas_b: list[Persona]
) -> dict:
    """Compare structural properties."""
    return {
        "field_overlap": jaccard(fields(personas_a), fields(personas_b)),
        "nesting_match": compare_nesting(personas_a, personas_b),
        "type_consistency": compare_types(personas_a, personas_b),
        "length_ratio": len(personas_a) / len(personas_b)
    }
```

#### Theme Extraction

```python
def extract_themes(personas: list[Persona]) -> set[str]:
    """Extract key themes from persona set."""
    # Use NLP to identify key themes
    texts = [p.to_text() for p in personas]
    # KeyBERT or similar for theme extraction
    themes = extract_keywords(texts, top_n=20)
    return set(themes)

def theme_overlap(
    personas_a: list[Persona],
    personas_b: list[Persona]
) -> float:
    """Compute theme overlap between sets."""
    themes_a = extract_themes(personas_a)
    themes_b = extract_themes(personas_b)
    return len(themes_a & themes_b) / len(themes_a | themes_b)
```

---

## Consistency Report Format

### Summary Dashboard

```markdown
# Cross-Provider Consistency Report

**Input:** customer_interviews.csv (15 interviews, 12,000 tokens)
**Personas Requested:** 5
**Providers Tested:** Anthropic Claude 3.5 Sonnet, OpenAI GPT-4o, Google Gemini Pro
**Date:** 2025-01-15

## Overall Consistency: 78%

| Provider Pair | Semantic | Structural | Quality | Overall |
|---------------|----------|------------|---------|---------|
| Claude ↔ GPT-4o | 0.82 | 0.95 | 0.85 | 0.87 |
| Claude ↔ Gemini | 0.75 | 0.90 | 0.80 | 0.82 |
| GPT-4o ↔ Gemini | 0.70 | 0.92 | 0.78 | 0.80 |

## Key Differences

1. **Verbosity:** Claude produces 40% more text per persona than GPT-4o
2. **Structure:** Gemini uses flatter JSON structures
3. **Themes:** All providers agree on top 3 themes; diverge on themes 4-6
4. **Quality:** Claude scores highest on coherence; GPT-4o on faithfulness

## Recommendation

For this dataset, **Claude 3.5 Sonnet** provides the most detailed personas.
**GPT-4o** is recommended if brevity and faithfulness are priorities.
```

### Detailed Comparison Matrix

```markdown
## Persona-Level Comparison

### Persona 1: "Tech-Savvy Professional"

| Attribute | Claude | GPT-4o | Gemini | Agreement |
|-----------|--------|--------|--------|-----------|
| Age range | 28-35 | 30-40 | 25-35 | Partial |
| Occupation | Software Engineer | Tech Professional | Developer | High |
| Goals | 5 items | 3 items | 4 items | Moderate |
| Pain points | 4 items | 3 items | 3 items | Moderate |
| Quote | Present | Present | Present | Full |

**Semantic similarity:** 0.84

### Theme Extraction

| Theme | Claude | GPT-4o | Gemini |
|-------|--------|--------|--------|
| Work-life balance | ✅ | ✅ | ✅ |
| Career growth | ✅ | ✅ | ✅ |
| Tech adoption | ✅ | ❌ | ✅ |
| Cost sensitivity | ✅ | ✅ | ❌ |
| Privacy concerns | ❌ | ✅ | ❌ |
```

---

## Statistical Analysis

### Reproducibility Testing

**Method:** Generate 10 times with same input, compute variance

```python
def test_reproducibility(
    provider: str,
    data: str,
    n_runs: int = 10
) -> dict:
    """Test output reproducibility for a provider."""
    results = [generate(provider, data) for _ in range(n_runs)]

    # Compute pairwise similarities
    similarities = []
    for i, j in combinations(range(n_runs), 2):
        sim = semantic_similarity(results[i], results[j])
        similarities.append(sim)

    return {
        "mean_similarity": np.mean(similarities),
        "std_similarity": np.std(similarities),
        "min_similarity": np.min(similarities),
        "max_similarity": np.max(similarities),
    }
```

**Expected Results:**
- Claude: 0.85-0.95 intra-provider consistency
- GPT-4o: 0.80-0.90 intra-provider consistency
- Gemini: 0.75-0.85 intra-provider consistency

### Significance Testing

**Method:** Permutation test for provider differences

```python
def test_provider_difference(
    personas_a: list[Persona],
    personas_b: list[Persona],
    metric: Callable,
    n_permutations: int = 1000
) -> dict:
    """Test if provider difference is significant."""
    observed_diff = metric(personas_a) - metric(personas_b)

    # Permutation test
    combined = personas_a + personas_b
    null_diffs = []
    for _ in range(n_permutations):
        shuffled = np.random.permutation(combined)
        split = len(personas_a)
        diff = metric(shuffled[:split]) - metric(shuffled[split:])
        null_diffs.append(diff)

    p_value = np.mean(np.abs(null_diffs) >= np.abs(observed_diff))

    return {
        "observed_difference": observed_diff,
        "p_value": p_value,
        "significant": p_value < 0.05
    }
```

---

## Provider Profiles

### Expected Provider Characteristics

Based on empirical testing and literature:

| Provider | Verbosity | Structure | Creativity | Faithfulness |
|----------|-----------|-----------|------------|--------------|
| **Claude** | High | Deep nesting | High | High |
| **GPT-4o** | Medium | Balanced | Medium | Very High |
| **GPT-4 Turbo** | Medium | Balanced | High | High |
| **Gemini Pro** | Low-Medium | Flat | Medium | Medium |
| **Llama 3 70B** | Medium | Variable | Medium | Medium |

### Provider Selection Guide

| Use Case | Recommended Provider | Rationale |
|----------|---------------------|-----------|
| Detailed personas | Claude Sonnet | Highest verbosity, rich detail |
| Quick iteration | Claude Haiku | Fast, good quality |
| Faithfulness priority | GPT-4o | Best at staying grounded |
| Cost-sensitive | Ollama (local) | Zero API cost |
| Privacy-sensitive | Ollama (local) | Data never leaves machine |
| Balanced | GPT-4o | Good all-around |

---

## CLI Commands

```bash
# Compare providers for given data
persona compare providers --from ./data/interviews.csv \
    --providers anthropic,openai,gemini \
    --count 5

# Generate consistency report
persona compare report --from ./data/ \
    --output ./reports/consistency.md

# Test single provider reproducibility
persona compare reproducibility --provider anthropic \
    --runs 10

# Show provider profiles
persona compare profiles
```

### Output Example

```
Cross-Provider Consistency Analysis
═══════════════════════════════════════════════════════════

Input: ./data/interviews.csv (15 files, 12,000 tokens)
Personas: 5 per provider

Provider         │ Time    │ Cost   │ Quality │ Consistency
─────────────────┼─────────┼────────┼─────────┼────────────
Claude Sonnet    │ 12.3s   │ $0.18  │ 0.87    │ (baseline)
GPT-4o           │ 8.5s    │ $0.22  │ 0.84    │ 0.82
Gemini Pro       │ 10.1s   │ $0.15  │ 0.79    │ 0.75
Ollama Llama3    │ 45.2s   │ $0.00  │ 0.72    │ 0.68

Key Differences:
• Claude produces 40% more words per persona
• GPT-4o has highest faithfulness to source data
• Gemini uses simpler sentence structures
• Ollama comparable quality at zero cost

Recommendation: Claude Sonnet for detailed personas,
GPT-4o for source-grounded outputs, Ollama for privacy.
```

---

## Implementation Considerations

### Cost Management

Running comparison across all providers is expensive. Strategies:

1. **Sampling:** Compare on subset of data
2. **Caching:** Reuse previous generations
3. **Progressive:** Start with 2 providers, add more if needed
4. **Budget limit:** Stop when cost threshold reached

### Performance

Comparison adds significant time:

| Operation | Time (5 personas, 4 providers) |
|-----------|--------------------------------|
| Generation | ~60 seconds total |
| Normalisation | ~2 seconds |
| Embedding | ~5 seconds |
| Analysis | ~3 seconds |
| **Total** | ~70 seconds |

### Storage

Each comparison generates:
- Raw responses per provider (~50KB each)
- Normalised personas (~10KB each)
- Embeddings (~5KB each)
- Report (~20KB)

Approximately 300KB per full comparison.

---

## Proposed Features

This research informs the following features:

1. **F-146: Cross-Provider Consistency Report** (P1, v1.14.0)
2. **F-147: Provider Selection Advisor** (P2, v1.14.0)

---

## Research Sources

### LLM Comparison Studies

- [Comparing Large Language Models](https://arxiv.org/abs/2307.03109)
- [LLM Benchmark Overview](https://huggingface.co/spaces/lmsys/chatbot-arena-leaderboard)
- [Holistic Evaluation of Language Models (HELM)](https://crfm.stanford.edu/helm/latest/)
- [Open LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)

### Consistency and Reproducibility

- [On the Reproducibility of Neural Network Predictions](https://arxiv.org/abs/2102.03349)
- [Measuring Reliability of Large Language Models](https://arxiv.org/abs/2306.04564)
- [Semantic Similarity Methods](https://www.sbert.net/docs/usage/semantic_textual_similarity.html)

### Statistical Methods

- [Permutation Tests for Comparing Classifiers](https://jmlr.org/papers/v21/19-750.html)
- [Effect Size and Statistical Significance](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3444174/)

### Provider Documentation

- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Google Gemini API](https://ai.google.dev/docs)
- [Ollama Models](https://ollama.com/library)

---

## Related Documentation

- [F-002: LLM Provider Abstraction](../roadmap/features/completed/F-002-llm-provider-abstraction.md)
- [F-120: Multi-Model Verification](../roadmap/features/completed/F-120-multi-model-verification.md)
- [F-021: Persona Comparison](../roadmap/features/completed/F-021-persona-comparison.md)
- [R-013: Local Model Assessment](./R-013-local-model-assessment.md)
