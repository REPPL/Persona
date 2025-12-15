# R-014: Shin et al. Gap Analysis & State-of-the-Art Features

Research into features from academic literature not yet implemented in Persona.

## Executive Summary

Analysis of the [Shin et al. DIS 2024 paper](https://dl.acm.org/doi/10.1145/3643834.3660729) "Understanding Human-AI Workflows for Generating Personas" reveals **5 specific evaluation metrics** referenced in Persona's documentation but **not yet implemented** in code. Additionally, a [systematic review of 52 research articles](https://arxiv.org/html/2504.04927v1) (April 2025) identifies further state-of-the-art features that would strengthen Persona's academic credibility.

**Key Finding:** Persona's documentation (R-008, ADR-0019) references Shin et al.'s four evaluation metrics, but the codebase lacks implementations of ROUGE-L, BERTScore, GPT-similarity, and proper G-eval.

**Recommendation:** Implement academic validation metrics (F-117) and hallucination detection (F-118) in v1.6.0 milestone.

---

## Shin et al. Paper Analysis

### Paper Overview

**Citation:** Shin, J., Hedderich, M.A., Rey, B.J., Lucero, A., & Oulasvirta, A. (2024). "Understanding Human-AI Workflows for Generating Personas." *Designing Interactive Systems Conference (DIS 2024)*.

**Key Contribution:** Compared four workflows for persona generation:
- **LLM-auto**: Fully automated LLM generation
- **LLM-grouping**: Human characteristics, LLM clustering
- **LLM-summarizing**: Human-curated groups, LLM summarises (BEST)
- **Designer**: Traditional human-only approach

**Core Finding:** "LLM-summarizing can generate the most statistically representative personas... it could capture all attributes present in user data and generate the personas that best match the data semantically."

### The Four Evaluation Metrics

| Metric | Method | Purpose | Persona Status |
|--------|--------|---------|----------------|
| **ROUGE-L** | Longest common subsequence | Lexical overlap with source | Not implemented |
| **BERTScore** | distilbert-based-uncased embeddings | Contextual semantic similarity | Not implemented |
| **GPT-similarity** | text-embedding-ada-002 | High-dimensional semantic distance | Not implemented |
| **G-eval** | GPT-4 scoring (0-1) | Information validity vs source | Partial (PersonaJudge exists) |

**Key Finding from Paper:** "By every similarity metric, LLM-summarizing reached statistically higher scores than the other workflows (p < 0.01)."

### Implementation Gap

**Referenced in `docs/development/research/R-008-persona-validation-methodology.md`:**

The study evaluated persona quality using four metrics:
- ROUGE-L - Longest common subsequence (lexical overlap)
- BERTScore - Contextual embeddings (semantic similarity)
- GPT-based-similarity - text-embedding-ada-002
- G-eval - GPT-4 scoring (0-1)

**But NOT in codebase:** No `rouge.py`, `bertscore.py`, or `geval.py` in `src/persona/core/quality/metrics/` or `src/persona/core/evaluation/`.

---

## Additional Unimplemented Features

### Persona Perception Scale (PPS)

**Reference:** [Salminen et al. (2020)](https://www.sciencedirect.com/science/article/abs/pii/S1071581920300392) - International Journal of Human-Computer Studies

**Description:** Validated 28-item survey instrument measuring 6 dimensions:

| Dimension | Sample Item |
|-----------|-------------|
| **Credibility** | "The persona seems realistic" |
| **Consistency** | "The quotes match other information shown" |
| **Completeness** | "The persona profile is not missing vital information" |
| **Clarity** | "The persona is easy to understand" |
| **Empathy** | "I can relate to this persona" |
| **Willingness to Use** | "I would like to know more about this persona" |

**Persona Status:** Not implemented - No survey template generation

**Referenced in:** R-008, ADR-0019, F-019 (documented as Layer 3: Perceptual Validation)

### Automatic Claim Extraction & Verification

**Reference:** [RAGAS Framework](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)

**Description:** Extract verifiable claims from persona, match to source data, calculate faithfulness score:
```
Faithfulness = (supported claims) / (total claims)
```

**Persona Status:** Not implemented - Evidence linking is manual, not automatic

**Pipeline documented in R-008:**
```
Persona Attribute → Claim Extraction → Source Matching → Verification Score
```

### Hallucination Detection

**Options:**
- **RAGAS Faithfulness**: LLM-powered, 0.762 average precision
- **[Vectara HHEM-2.1-Open](https://huggingface.co/vectara/hallucination_evaluation_model)**: Free, small T5-based classifier

**Persona Status:** Not implemented

**Research context:** Expert surveys rate hallucination as highest concern (M = 5.94/7) for GenAI personas.

---

## Systematic Review Findings (April 2025)

### Source

[How Is Generative AI Used for Persona Development?: A Systematic Review of 52 Research Articles](https://arxiv.org/html/2504.04927v1)

### Additional State-of-the-Art Features NOT in Persona

| Feature | Description | Industry Adoption | Persona Status |
|---------|-------------|-------------------|----------------|
| **Bias Detection** | Stereotype lexicons, bias estimation | 11.5% of studies | Not implemented |
| **Multimodal Representation** | Text + AI-generated images | Emerging | Not implemented |
| **Model-Agnostic Verification** | Compare outputs across LLMs | 23.2% of studies | Not implemented |
| **Prompt Fidelity Scoring** | Measure output adherence to prompt | Recommended | Not implemented |
| **Lexical Diversity Metrics** | Vocabulary richness scoring | Recommended | Not implemented |

### Critical Gap from Review

> "Almost half of the articles (n = 23, 44%) did not clearly indicate how personas are evaluated."

Persona's existing validation framework (QualityScorer, PersonaJudge) positions it ahead of most implementations, but lacks the **academic-standard metrics** (ROUGE-L, BERTScore, G-eval).

---

## Implementation Comparison

### Currently Implemented in Persona

| Feature | Location | Notes |
|---------|----------|-------|
| Completeness Metric | `/quality/metrics/completeness.py` | Field presence, depth |
| Consistency Metric | `/quality/metrics/consistency.py` | Internal coherence |
| Evidence Strength | `/quality/metrics/evidence.py` | Coverage & diversity |
| Distinctiveness | `/quality/metrics/distinctiveness.py` | Similarity-based |
| Realism Metric | `/quality/metrics/realism.py` | Heuristic plausibility |
| LLM-as-Judge | `/evaluation/judge.py` | 6 criteria, multi-provider |
| Evidence Linking | `/evidence/linker.py` | Manual tracking |
| Validation Framework | `/validation/validator.py` | Pluggable rules |

### NOT Implemented (from Shin et al.)

| Metric | Complexity | Dependencies | Academic Value |
|--------|------------|--------------|----------------|
| **ROUGE-L** | Low | `rouge-score` PyPI | High - standard NLG metric |
| **BERTScore** | Low | `bert-score` PyPI | High - 0.93 correlation with humans |
| **GPT-similarity** | Low | OpenAI embeddings | Medium - proprietary |
| **G-eval** | Medium | GPT-4 + CoT prompts | High - state-of-the-art |
| **PPS Survey** | Medium | None (template) | High - validated instrument |

### NOT Implemented (from Systematic Review)

| Feature | Complexity | Value |
|---------|------------|-------|
| Automatic Claim Extraction | High | Required for faithfulness |
| RAGAS Faithfulness | Medium | Hallucination detection |
| HHEM Classifier | Low | Free, fast hallucination check |
| Bias Detection | Medium | Ethical AI compliance |
| Lexical Diversity | Low | Quality indicator |

---

## Recommendations

### Priority 1: Academic Credibility (v1.6.0 milestone)

Implement **Shin et al. four metrics** to enable direct comparison with academic research:

1. **ROUGE-L** - `pip install rouge-score`, ~100 lines
2. **BERTScore** - `pip install bert-score`, ~100 lines
3. **G-eval** - Proper CoT implementation via PersonaJudge, ~200 lines
4. **PPS Survey Generator** - Template + scoring, ~300 lines

**Impact:** Enables claims like "Persona achieves BERTScore of 0.85, comparable to Shin et al. LLM-summarizing workflow"

### Priority 2: Hallucination Detection (v1.6.0 milestone)

1. **Automatic Claim Extraction** - Parse persona to verifiable claims
2. **RAGAS Faithfulness** - Optional LLM-based verification
3. **HHEM Integration** - Fast, free classifier option

**Impact:** Addresses top expert concern (M = 5.94/7) for GenAI personas

### Priority 3: Research Compliance (Future consideration)

1. **Bias Detection** - Stereotype lexicon matching
2. **Model Comparison** - Multi-LLM output verification
3. **Lexical Diversity** - Type-token ratio, vocabulary richness

---

## Sources

### Primary Research

- [Shin et al. DIS 2024 - Human-AI Workflows](https://dl.acm.org/doi/10.1145/3643834.3660729)
- [GitHub: persona-generation-workflow](https://github.com/joongishin/persona-generation-workflow)
- [Systematic Review: GenAI for Persona Development](https://arxiv.org/html/2504.04927v1)

### Evaluation Metrics

- [G-eval: NLG Evaluation using GPT-4](https://arxiv.org/abs/2303.16634)
- [BERTScore: Evaluating Text Generation](https://huggingface.co/spaces/evaluate-metric/bertscore)
- [ROUGE Metric](https://spotintelligence.com/2024/08/12/rouge-metric-in-nlp/)
- [Persona Perception Scale](https://www.sciencedirect.com/science/article/abs/pii/S1071581920300392)

### Hallucination Detection

- [RAGAS Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)
- [Vectara HHEM-2.1-Open](https://huggingface.co/vectara/hallucination_evaluation_model)
- [Benchmarking Hallucination Detection in RAG](https://cleanlab.ai/blog/rag-tlm-hallucination-benchmarking/)

---

## Related Documentation

- [R-008: Persona Validation Methodology](R-008-persona-validation-methodology.md)
- [ADR-0019: Persona Validation Methodology](../decisions/adrs/ADR-0019-persona-validation-methodology.md)
- [F-117: Academic Validation Metrics](../roadmap/features/planned/F-117-academic-validation-metrics.md)
- [F-118: Hallucination Detection](../roadmap/features/planned/F-118-hallucination-detection.md)
- [v1.6.0: Academic Validation](../roadmap/milestones/v1.6.0.md)
