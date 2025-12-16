# R-015: Quality Metrics Taxonomy for Persona Generation

Research into comprehensive quality assessment frameworks for LLM-generated personas, synthesising NLG evaluation standards with persona-specific requirements.

## Executive Summary

Persona quality assessment requires a multi-dimensional approach combining established NLG metrics with domain-specific measures. This research synthesises academic literature (2024-2025) to define a comprehensive taxonomy of quality metrics applicable to generated personas.

**Key Finding:** No single metric captures persona quality. Effective assessment requires metrics across five dimensions: **Content Quality**, **Linguistic Quality**, **Faithfulness**, **Diversity**, and **Bias/Fairness**.

**Recommendation:** Implement a layered metrics architecture where automated metrics provide continuous quality signals, with optional LLM-as-Judge and human evaluation for comprehensive assessment.

---

## Taxonomy of Quality Metrics

### Dimension 1: Content Quality

Metrics assessing the substance and structure of generated content.

| Metric | Description | Range | Implementation |
|--------|-------------|-------|----------------|
| **Completeness** | Required fields present and populated | 0.0-1.0 | Field presence check |
| **Consistency** | Internal coherence of attributes | 0.0-1.0 | Contradiction detection |
| **Coherence** | Logical flow and organisation | 1-5 | G-Eval or heuristic |
| **Relevance** | Alignment with input data | 0.0-1.0 | Embedding similarity |
| **Specificity** | Concrete vs generic content | 0.0-1.0 | Pattern matching |

#### Completeness

**Definition:** Measures whether all required persona attributes are present and adequately populated.

**Calculation:**
```
Completeness = (populated_fields / required_fields) × field_depth_score
```

**Components:**
- Field presence (40%): Are required fields present?
- Field depth (30%): Do list fields have sufficient items?
- Field richness (30%): Is content substantive (word count, detail)?

**Thresholds:**
| Score | Interpretation |
|-------|----------------|
| > 0.9 | Excellent |
| 0.8-0.9 | Good |
| 0.6-0.8 | Acceptable |
| < 0.6 | Poor |

#### Consistency

**Definition:** Measures internal coherence—whether persona attributes align with each other logically.

**Detection Methods:**
1. **Contradiction patterns**: "loves X" vs "hates X"
2. **Demographic-goal alignment**: Age/occupation consistency
3. **Behavioural coherence**: Actions matching stated preferences
4. **Quote alignment**: Quotes reflecting persona characteristics

**Example Inconsistencies:**
- 25-year-old with 30 years of experience
- "Hates technology" but "Spends hours on social media"
- Goals contradicting stated frustrations

#### Coherence (G-Eval)

**Definition:** Measures the structural quality and logical flow of the generated persona.

**G-Eval Approach (Liu et al. 2023):**
1. Define evaluation criteria
2. Generate chain-of-thought reasoning
3. Output numeric score (1-5)

**Prompt Template:**
```
Evaluate the coherence of this persona on a scale of 1-5:
- 1: Disorganised, contradictory, hard to understand
- 3: Some logical issues but generally comprehensible
- 5: Well-organised, logical, clear narrative

Persona: {persona_json}

First, reason about the coherence step by step.
Then provide your score.
```

---

### Dimension 2: Linguistic Quality

Metrics assessing the language and vocabulary of generated content.

| Metric | Description | Range | Implementation |
|--------|-------------|-------|----------------|
| **Fluency** | Grammatical correctness | 1-5 | LLM-as-Judge |
| **Naturalness** | Human-like expression | 1-5 | LLM-as-Judge |
| **Lexical Diversity** | Vocabulary richness | 0.0-∞ | MTLD, MATTR |
| **Readability** | Ease of comprehension | Grade level | Flesch-Kincaid |

#### Lexical Diversity Metrics

**MTLD (Measure of Textual Lexical Diversity)**

**Definition:** Average number of consecutive words maintaining a TTR threshold (typically 0.72).

**Calculation (McCarthy & Jarvis 2010):**
```python
def calculate_mtld(tokens, threshold=0.72):
    factors = []
    factor_count = 0
    types = set()

    for token in tokens:
        types.add(token.lower())
        ttr = len(types) / (factor_count + 1)

        if ttr <= threshold:
            factors.append(factor_count + 1)
            types = set()
            factor_count = 0
        else:
            factor_count += 1

    # Handle partial factor at end
    if factor_count > 0:
        factors.append(factor_count / (1 - threshold))

    return sum(factors) / len(factors) if factors else 0
```

**Interpretation:**
| MTLD | Interpretation |
|------|----------------|
| < 30 | Poor - highly repetitive |
| 30-50 | Below average |
| 50-70 | Average |
| 70-100 | Good |
| > 100 | Excellent |

**MATTR (Moving-Average Type-Token Ratio)**

**Definition:** Average TTR computed over a moving window of fixed size.

**Advantages:**
- Most stable metric across text lengths (Covington & McFall 2010)
- Reduces length bias inherent in simple TTR
- Configurable window size (typically 50-100 tokens)

**TTR (Type-Token Ratio)**

**Definition:** Unique words / Total words

**Limitation:** Strongly biased by text length—longer texts naturally have lower TTR.

**Use Case:** Only for comparing texts of similar length.

---

### Dimension 3: Faithfulness

Metrics assessing grounding in source data.

| Metric | Description | Range | Implementation |
|--------|-------------|-------|----------------|
| **Evidence Coverage** | % attributes with source evidence | 0.0-1.0 | Evidence linking |
| **ROUGE-L** | Lexical overlap with source | 0.0-1.0 | LCS algorithm |
| **BERTScore** | Semantic similarity to source | 0.0-1.0 | Contextual embeddings |
| **Faithfulness** | % supported claims | 0.0-1.0 | RAGAS-style |
| **Hallucination Rate** | % unsupported claims | 0.0-1.0 | Inverse of faithfulness |

#### ROUGE-L

**Definition:** Longest Common Subsequence (LCS) based F-measure between generated text and source.

**Calculation:**
```
R_lcs = LCS(generated, source) / len(source)
P_lcs = LCS(generated, source) / len(generated)
F_lcs = (1 + β²) × P_lcs × R_lcs / (R_lcs + β² × P_lcs)
```

**Use Case:** Measures lexical overlap—how much of the source vocabulary appears in output.

**Limitation:** Doesn't capture semantic similarity (paraphrasing scores low).

#### BERTScore

**Definition:** Semantic similarity using contextual embeddings from BERT models.

**Implementation (Zhang et al. 2020):**
```python
from bert_score import score

P, R, F1 = score(
    cands=[generated_text],
    refs=[source_text],
    model_type="distilbert-base-uncased",
    lang="en"
)
```

**Advantages:**
- Captures semantic similarity beyond lexical overlap
- 0.93 correlation with human judgements (Zhang et al.)
- Handles paraphrasing appropriately

**Interpretation:**
| Score | Interpretation |
|-------|----------------|
| > 0.9 | Excellent alignment |
| 0.8-0.9 | Good alignment |
| 0.7-0.8 | Moderate alignment |
| < 0.7 | Weak alignment |

#### Faithfulness (RAGAS-style)

**Definition:** Proportion of claims in generated text that are supported by source data.

**Pipeline:**
1. Extract claims from persona attributes
2. For each claim, find most similar source passage
3. Determine if claim is supported, partially supported, or unsupported
4. Calculate ratio of supported claims

**Formula:**
```
Faithfulness = supported_claims / total_claims
```

**Claim Verification Levels:**
| Level | Similarity | Interpretation |
|-------|------------|----------------|
| Strong | > 0.8 | Direct quote or explicit mention |
| Moderate | 0.6-0.8 | Paraphrased or inferred |
| Weak | 0.4-0.6 | Loosely related |
| Unsupported | < 0.4 | No evidence found |

---

### Dimension 4: Diversity

Metrics assessing variation across multiple generated personas.

| Metric | Description | Range | Implementation |
|--------|-------------|-------|----------------|
| **Distinctiveness** | Uniqueness vs other personas | 0.0-1.0 | Embedding distance |
| **Semantic Diversity** | Embedding space coverage | 0.0-1.0 | Cosine distances |
| **Entailment Diversity** | Statement independence | -1.0-1.0 | NLI model |
| **Attribute Overlap** | Shared characteristics | 0.0-1.0 | Jaccard similarity |

#### Distinctiveness

**Definition:** Measures how unique a persona is compared to others in the same generation batch.

**Calculation:**
```python
def distinctiveness(persona, other_personas, comparator):
    similarities = [comparator.similarity(persona, other)
                   for other in other_personas]
    max_sim = max(similarities)
    avg_sim = mean(similarities)

    return 1 - (0.5 * max_sim + 0.5 * avg_sim)
```

**Interpretation:**
- High distinctiveness (> 0.7): Personas are well-differentiated
- Low distinctiveness (< 0.4): Personas are too similar

#### Entailment Diversity (EDIV)

**Definition:** Uses NLI models to detect whether generated statements entail or contradict each other.

**Implementation (from persona-steered generation research):**
```python
from transformers import pipeline

nli = pipeline("zero-shot-classification",
               model="roberta-large-mnli")

def entailment_diversity(statements):
    scores = []
    for i, s1 in enumerate(statements):
        for s2 in statements[i+1:]:
            result = nli(s1, [s2])
            # Score: -1 (contradiction) to 1 (entailment)
            scores.append(result['scores'][0] - result['scores'][2])
    return mean(scores)
```

**Range:** -1.0 (all contradict) to 1.0 (all entail)

**Ideal:** Near 0 indicates diverse, independent statements.

---

### Dimension 5: Bias & Fairness

Metrics detecting stereotypes and unfair representations.

| Metric | Description | Range | Implementation |
|--------|-------------|-------|----------------|
| **Stereotype Score** | Presence of stereotypical content | 0.0-1.0 | Lexicon + embedding |
| **Demographic Parity** | Equal representation across groups | 0.0-1.0 | Distribution analysis |
| **Toxicity** | Harmful or offensive content | 0.0-1.0 | Perspective API |
| **Intersectional Bias** | Compound biases across categories | 0.0-1.0 | Multi-axis analysis |

#### Stereotype Detection Methods

**Lexicon-Based:**
- Use stereotype word lists (HolisticBias, StereoSet)
- Match against persona content
- Fast but limited coverage

**Embedding-Based (WEAT):**
- Word Embedding Association Test
- Measures association strength between concepts
- Detects implicit biases

**LLM-as-Judge:**
- Prompt LLM to identify stereotypical content
- Most flexible but slower
- Can explain findings

#### Key Datasets

| Dataset | Coverage | Use Case |
|---------|----------|----------|
| **HolisticBias** | 600 terms, 13 demographic axes | Comprehensive bias measurement |
| **StereoSet** | 17,000 sentences | Stereotype detection benchmark |
| **CrowS-Pairs** | 1,508 pairs | Comparative bias evaluation |
| **HONEST** | Multi-language | Gender stereotype detection |

---

## Implementation Architecture

### Layered Metrics System

```
                    ┌─────────────────────┐
                    │   Human Evaluation  │  ← Optional: PPS, expert review
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │   LLM-as-Judge      │  ← Optional: G-Eval, bias detection
                    │   (Coherence, Bias) │
                    └─────────┬───────────┘
                              │
┌─────────────────────────────▼─────────────────────────────┐
│                    Automated Metrics                       │
├───────────┬───────────┬───────────┬───────────┬──────────┤
│ Content   │ Linguistic│ Faithful- │ Diversity │ Bias     │
│ Quality   │ Quality   │ ness      │           │          │
├───────────┼───────────┼───────────┼───────────┼──────────┤
│Completeness│ MTLD     │ ROUGE-L   │Distinctive│Lexicon   │
│Consistency │ MATTR    │ BERTScore │ EDIV      │Embedding │
│Specificity │ Fluency  │Faithfulness│ SDIV     │          │
└───────────┴───────────┴───────────┴───────────┴──────────┘
```

### Default Configuration

```yaml
quality_metrics:
  # Content Quality
  completeness:
    required_fields: [name, age, occupation, goals, pain_points]
    min_goals: 3
    min_pain_points: 2
  consistency:
    enabled: true
    contradiction_patterns: true

  # Linguistic Quality
  lexical_diversity:
    metric: mtld
    threshold: 50
    window_size: 50  # for MATTR

  # Faithfulness
  faithfulness:
    embedding_model: text-embedding-3-small
    similarity_threshold: 0.7
    min_coverage: 0.8

  # Diversity (batch mode)
  diversity:
    min_distinctiveness: 0.6
    max_similarity: 0.7

  # Bias Detection
  bias:
    enabled: true
    methods: [lexicon]  # or [lexicon, embedding, llm]
    categories: [gender, racial, age, professional]
```

### Scoring Aggregation

**Overall Quality Score:**
```python
def aggregate_quality(scores: dict, weights: dict) -> float:
    """
    Default weights:
    - completeness: 0.20
    - consistency: 0.15
    - faithfulness: 0.25
    - diversity: 0.15
    - bias_free: 0.15  # 1 - bias_score
    - lexical_diversity: 0.10
    """
    weighted_sum = sum(
        scores[metric] * weights[metric]
        for metric in weights
    )
    return weighted_sum
```

**Quality Levels:**
| Score | Level | Description |
|-------|-------|-------------|
| ≥ 0.9 | Excellent | Publication-ready |
| 0.8-0.9 | Good | Minor improvements possible |
| 0.6-0.8 | Acceptable | Usable with caveats |
| 0.4-0.6 | Poor | Significant issues |
| < 0.4 | Failing | Unusable |

---

## Research Sources

### NLG Evaluation Surveys

- [LLM-based NLG Evaluation: Current Status and Challenges](https://direct.mit.edu/coli/article/51/2/661/128807/LLM-based-NLG-Evaluation-Current-Status-and) (MIT Press, 2025)
- [Reference-free Evaluation Metrics for Text Generation: A Survey](https://arxiv.org/html/2501.12011) (arXiv, January 2025)
- [A Survey of Evaluation Metrics Used for NLG Systems](https://dl.acm.org/doi/10.1145/3485766) (ACM Computing Surveys)
- [Automatic Metrics in Natural Language Generation: A Survey](https://arxiv.org/html/2408.09169v1) (August 2024)

### Quality Assessment Frameworks

- [G-Eval: NLG Evaluation using GPT-4](https://arxiv.org/abs/2303.16634) (Liu et al., EMNLP 2023)
- [MTQ-Eval: Multilingual Text Quality Evaluation](https://arxiv.org/html/2511.09374v1) (November 2025)
- [BERTScore: Evaluating Text Generation](https://arxiv.org/abs/1904.09675) (Zhang et al., ICLR 2020)

### Lexical Diversity

- [MTLD: Measure of Textual Lexical Diversity](https://doi.org/10.3758/BRM.42.2.381) (McCarthy & Jarvis, 2010)
- [MATTR Stability Analysis](https://doi.org/10.3758/BRM.42.2.381) (Covington & McFall, 2010)
- [lexical-diversity Python Package](https://pypi.org/project/lexical-diversity/)

### Persona-Specific Evaluation

- [Evaluating LLM Biases in Persona-Steered Generation](https://aclanthology.org/2024.findings-acl.586/) (ACL 2024)
- [PersonaGym: Evaluating Persona Agents](https://arxiv.org/abs/2407.18416)
- [Persona Perception Scale](https://www.sciencedirect.com/science/article/abs/pii/S1071581920300392) (Salminen et al., 2020)

### Bias Detection

- [HolisticBias Dataset](https://arxiv.org/abs/2205.09209)
- [Marked Personas: Stereotype Detection](https://arxiv.org/abs/2305.18189) (ACL 2023)
- [Survey on Stereotype Detection in NLP](https://arxiv.org/pdf/2505.17642) (2025)

### Faithfulness & Hallucination

- [RAGAS: Retrieval Augmented Generation Assessment](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)
- [Vectara HHEM Classifier](https://huggingface.co/vectara/hallucination_evaluation_model)
- [R-008: Persona Validation Methodology](R-008-persona-validation-methodology.md)

---

## Related Documentation

- [F-106: Quality Metrics Scoring](../roadmap/features/completed/F-106-quality-metrics.md)
- [F-119: Bias & Stereotype Detection](../roadmap/features/completed/F-119-bias-stereotype-detection.md)
- [F-121: Lexical Diversity Metrics](../roadmap/features/completed/F-121-lexical-diversity-metrics.md)
- [R-008: Persona Validation Methodology](R-008-persona-validation-methodology.md)
- [Quality Metrics Reference](../../reference/quality-metrics.md)

---

**Status**: Complete
