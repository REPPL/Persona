# R-013: Local Model Assessment for Persona

Research into local LLM integration opportunities, infrastructure options, and privacy-preserving workflows for Persona.

## Executive Summary

This document provides a comprehensive assessment of where and how local models can be integrated into Persona, based on thorough codebase analysis and state-of-the-art research (December 2025).

**Key Finding:** Persona already has Ollama integration documented but no built-in `OllamaProvider` implementation exists in the codebase. The documentation describes Ollama support, but actual implementation requires adding a new provider class.

**Recommendation:** Implement native Ollama provider (F-112) as foundation, followed by PII detection (F-113), LLM-as-judge evaluation (F-114), synthetic data generation (F-115), and hybrid pipelines (F-116).

---

## Target Hardware

- **Primary:** Mac Studio M4 Max (128GB RAM) - enables 70B+ models
- **Secondary:** MacBook M1 Pro (16GB RAM) - enables 7-8B models
- **Cross-platform:** Windows & Linux machines with similar specifications

---

## Key Findings

### Where to Add Local Models

| Use Case | Priority | Rationale |
|----------|----------|-----------|
| **Privacy-preserving generation** | P0 | Enterprises cannot send sensitive data to cloud APIs |
| **Synthetic data from PII sources** | P1 | Generate shareable data from confidential research |
| **Local quality evaluation** | P2 | LLM-as-judge for persona scoring without API costs |
| **Cost optimisation (bulk)** | P2 | Local generation at ~$0/persona vs $0.15-0.50 |
| **Offline deployment** | P3 | Air-gapped environments (government, defence) |

### Infrastructure Recommendation

**Ollama** is the recommended infrastructure because:
- Native Apple Silicon support (Metal acceleration)
- Cross-platform (macOS, Windows, Linux)
- OpenAI-compatible API
- Simplest deployment (single binary)
- Active community, frequent updates
- 20% faster than LM Studio in benchmarks

### LLMs vs SLMs Assessment

| Model Size | Quality | Use Case |
|------------|---------|----------|
| **7B (SLM)** | 70-80% of frontier | Testing, iteration, constrained hardware |
| **24B** | 85-90% of frontier | Production on 16GB+ systems |
| **70B (LLM)** | 90-95% of frontier | Production on 48GB+ systems |
| **Frontier** | 100% (baseline) | Maximum quality, when data sharing permitted |

**2025 Consensus:** Hybrid SLM+LLM architecture optimal for 70-80% of enterprise use cases.

### PII Detection Framework

**Microsoft Presidio** recommended for:
- Multi-language NER (spaCy/Stanza/HuggingFace backends)
- Regex patterns for structured PII
- Customisable recognisers and anonymisation strategies
- Well-documented, pip-installable, actively maintained

---

## Infrastructure Comparison

| Framework | Best For | API Compatibility | Performance | Enterprise Ready |
|-----------|----------|-------------------|-------------|------------------|
| **Ollama** | Production API deployment | OpenAI-compatible | 20% faster than LM Studio | Yes |
| **vLLM** | High-throughput serving | OpenAI-compatible | Best for concurrent requests | Yes |
| **llama.cpp** | Maximum control | Native C++ | Smallest footprint (90MB) | Manual |
| **LM Studio** | GUI/Prototyping | OpenAI-compatible | Good for evaluation | No (GUI-focused) |
| **LocalAI** | Multi-backend | OpenAI-compatible | Flexible | Yes |

---

## Hardware-Specific Model Recommendations

### Mac Studio M4 Max (128GB RAM)

| Model | Quantisation | RAM Usage | Performance |
|-------|--------------|-----------|-------------|
| **Qwen2.5:72b** | Q4_K_M | ~45GB | Excellent quality, 128K context |
| **Llama3.1:70b** | Q4_K_M | ~42GB | Strong creative writing |
| **DeepSeek-R1:70b** | Q4_K_M | ~44GB | Advanced reasoning |
| **Mixtral:8x22b** | Q4_K_M | ~85GB | MoE, diverse outputs |

### MacBook M1 Pro (16GB RAM)

| Model | Quantisation | RAM Usage | Performance |
|-------|--------------|-----------|-------------|
| **Llama3.2:3b** | Q8_0 | ~4GB | Fast iteration, basic quality |
| **Mistral:7b** | Q4_K_M | ~5GB | Best 7B quality |
| **Qwen2.5:7b** | Q4_K_M | ~5GB | Strong instruction following |
| **Phi-3:medium** | Q4_K_M | ~8GB | Microsoft's efficient model |

### Apple Silicon Considerations

- Ollama uses Metal acceleration natively
- Unified memory architecture enables larger models than discrete GPU systems
- M4 Max offers ~40% faster inference than M1 Pro per parameter

---

## Best Models for Persona Generation (2025)

| Model | Parameters | RAM Required | Quality Assessment |
|-------|------------|--------------|-------------------|
| **Qwen2.5:72b** | 72B | 48GB+ | Excellent for persona generation |
| **Llama3:70b** | 70B | 48GB+ | Strong creative writing |
| **Mistral Small 3** | 24B | 16GB+ | Best quality/resource ratio |
| **Mixtral:8x7b** | 47B (MoE) | 32GB+ | Good for diverse personas |
| **Llama3.2:3b** | 3B | 4GB+ | Minimum viable for testing |

### Persona-Specific Findings

- Persona generation requires creativity + structure adherence
- 7B+ models sufficient for basic personas
- 24B+ models needed for complex, nuanced personas
- 70B models approach frontier quality

---

## Use Cases for Local Models

### 1. Privacy-Preserving Persona Generation (Critical)

**Problem:** Enterprises cannot send sensitive research data to cloud APIs due to:
- GDPR/HIPAA compliance
- Data residency requirements
- Proprietary information protection
- Financial/healthcare regulations

**Solution:** Local model generation pipeline

```
Input Data → PII Detection → Local LLM → Persona Output
         ↓
    [Microsoft Presidio]
         ↓
    Anonymise/Redact
```

### 2. Synthetic Data Generation from Sensitive Sources

**Problem:** Real user research data may contain:
- Customer interviews with PII
- Internal documents with trade secrets
- Healthcare patient feedback
- Financial user studies

**Solution:** Generate synthetic training data locally, then optionally refine with frontier models

```
Sensitive Data → Local LLM → Synthetic Dataset → [Optional] Frontier Refinement
                    ↓
              PII-Free Output
```

### 3. Persona Quality Evaluation (LLM-as-Judge)

**Problem:** Current quality scoring (F-106) uses heuristics, not semantic evaluation

**Solution:** Local LLM-as-judge pipeline

```
Generated Persona → Local Judge LLM → Quality Scores
                         ↓
                  Criteria: Coherence, Realism, Consistency
```

**Research Finding:** Even best LLMs reach ~69% accuracy on persona role identification (PersonaEval 2025), while humans achieve 90.8%. Hybrid human+LLM evaluation recommended.

### 4. Cost Optimisation for Bulk Generation

**Problem:** Generating 100+ personas with frontier models is expensive
- Claude Sonnet: ~$0.15-0.30 per persona
- GPT-4o: ~$0.20-0.40 per persona

**Solution:** Local models for bulk generation, frontier for refinement

### 5. Offline/Air-Gapped Deployment

**Problem:** Some environments have no internet access (government, defence, secure facilities)

**Solution:** Fully local pipeline with Ollama/vLLM

---

## Current Architecture Analysis

### Provider Abstraction (Well-Designed for Extension)

**Files:**
- `src/persona/core/providers/base.py` - `LLMProvider` ABC
- `src/persona/core/providers/factory.py` - `ProviderFactory`
- `src/persona/core/providers/custom.py` - `CustomVendorProvider`

**Existing Built-in Providers:**
- `OpenAIProvider` - Cloud API
- `AnthropicProvider` - Cloud API
- `GeminiProvider` - Cloud API

**Extension Points:**
1. **Custom Vendor System** - YAML-based configuration for OpenAI/Anthropic-compatible APIs
2. **Plugin Entry Points** - `persona.providers` in `pyproject.toml`
3. **Factory Pattern** - `ProviderFactory.BUILTIN_PROVIDERS` dictionary

### Integration Gaps Identified

| Feature | Documentation | Implementation |
|---------|--------------|----------------|
| Ollama Provider | Documented in `provider-apis.md` | No `OllamaProvider` class exists |
| Local Model Config | Examples in docs | Only via custom vendor YAML |
| PII Detection | Not documented | Not implemented |
| Quality Evaluation | Basic (F-106) | No LLM-as-judge |

---

## Recommended Integration Architecture

### Phase 1: Native Ollama Provider

**Create `src/persona/core/providers/ollama.py`:**

```python
class OllamaProvider(LLMProvider):
    """Native Ollama provider for local LLM inference."""

    MODELS = {
        "llama3:70b": {"context": 8192, "params": "70B"},
        "llama3:8b": {"context": 8192, "params": "8B"},
        "qwen2.5:72b": {"context": 131072, "params": "72B"},
        "mistral:7b": {"context": 32768, "params": "7B"},
    }

    def __init__(self, base_url: str = "http://localhost:11434", ...):
        ...
```

### Phase 2: PII Detection Pipeline

**Integrate Microsoft Presidio:**

```python
# New module: src/persona/core/privacy/detector.py
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PIIDetector:
    """Detect and anonymise PII in input data."""

    def detect(self, text: str) -> list[PIIEntity]:
        """Find PII entities in text."""
        ...

    def anonymise(self, text: str, strategy: str = "redact") -> str:
        """Anonymise detected PII."""
        ...
```

### Phase 3: LLM-as-Judge Evaluation

**New module: `src/persona/core/evaluation/judge.py`:**

```python
class PersonaJudge:
    """Evaluate persona quality using LLM-as-judge."""

    def __init__(self, provider: str = "ollama", model: str = "llama3:70b"):
        ...

    def evaluate(self, persona: Persona, criteria: list[str]) -> QualityScore:
        """Score persona on given criteria."""
        ...
```

### Phase 4: Hybrid Pipeline

**Orchestrate local + frontier models:**

```python
class HybridPipeline:
    """Generate with local, refine with frontier."""

    def generate(self, data: str, count: int) -> list[Persona]:
        # 1. Anonymise input data
        safe_data = self.pii_detector.anonymise(data)

        # 2. Generate draft personas with local model
        drafts = self.local_provider.generate(safe_data, count * 2)

        # 3. Evaluate with local judge
        scored = self.judge.evaluate_batch(drafts)

        # 4. Optionally refine top candidates with frontier
        if self.use_frontier_refinement:
            return self.frontier_provider.refine(scored[:count])

        return scored[:count]
```

---

## PII Detection Frameworks Assessment

### Microsoft Presidio (Recommended)

**Capabilities:**
- NER-based detection (spaCy, Stanza, HuggingFace)
- Regex patterns for structured PII (SSN, credit cards, etc.)
- Multi-language support
- Customisable recognisers
- Anonymisation strategies: redact, hash, replace, encrypt

**Installation:**
```bash
pip install presidio-analyzer presidio-anonymizer spacy
python -m spacy download en_core_web_lg
```

### Alternatives Considered

| Tool | Pros | Cons |
|------|------|------|
| **Presidio** | Full-featured, Microsoft-backed | Requires spaCy model |
| **spaCy NER** | Fast, accurate | Only NER, no anonymisation |
| **Faker** | Generates fake PII | Detection not replacement |
| **scrubadub** | Simple API | Less accurate than Presidio |

---

## Quality Comparison: Local vs Frontier

Based on 2025 research, expected quality differences:

| Aspect | Local (70B) | Local (7B) | Frontier |
|--------|-------------|------------|----------|
| Persona coherence | 85-90% | 70-80% | 95%+ |
| Creative diversity | 80-85% | 65-75% | 90%+ |
| JSON structure adherence | 90%+ | 80-85% | 98%+ |
| Generation speed | 10-30 tok/s | 50-100 tok/s | 100+ tok/s |
| Cost per persona | ~$0 | ~$0 | $0.15-0.50 |

**Recommendation:** Use local 70B models for production privacy-sensitive work; local 7B for testing/development; frontier for maximum quality when data sharing is permitted.

---

## Proposed Features

This research identifies 5 features for implementation:

1. **F-112: Native Ollama Provider** (P0, v1.3.0)
2. **F-113: PII Detection & Anonymisation** (P1, v1.3.0)
3. **F-114: LLM-as-Judge Persona Evaluation** (P2, v1.4.0)
4. **F-115: Synthetic Data Generation Pipeline** (P2, v1.4.0)
5. **F-116: Hybrid Local/Frontier Pipeline** (P3, v1.5.0)

---

## Research Sources

### Local LLM Infrastructure
- [Local Synthetic Data Generation using LLama 3.2 and Ollama](https://www.analyticsvidhya.com/blog/2025/01/local-synthetic-data-generation/)
- [Best Ollama Models 2025: Complete Performance Guide](https://collabnix.com/best-ollama-models-in-2025-complete-performance-comparison/)
- [Local LLM Speed Test: Ollama vs LM Studio vs llama.cpp](https://www.arsturn.com/blog/local-llm-showdown-ollama-vs-lm-studio-vs-llama-cpp-speed-tests)
- [llama.cpp vs. ollama: Running LLMs Locally for Enterprises](https://picovoice.ai/blog/local-llms-llamacpp-ollama/)
- [vLLM OpenAI-Compatible Server](https://docs.vllm.ai/en/latest/serving/openai_compatible_server/)

### Privacy & Synthetic Data
- [Local LLMs for Data Sovereignty](https://www.e-spincorp.com/local-llms-data-sovereignty/)
- [Stop Sharing Your Data! How Enterprises Are Using Local LLMs](https://eqw.ai/stop-sharing-your-data-how-enterprises-are-using-local-llms-for-secure-data-synthesis/)
- [Microsoft Presidio - PII Detection Framework](https://github.com/microsoft/presidio)
- [Gretel AI Synthetic Data Generation](https://github.com/gretelai/gretel-synthetics)

### Evaluation & Quality
- [LLM-as-a-judge: Complete Guide](https://www.evidentlyai.com/llm-guide/llm-as-a-judge)
- [PersonaEval: Are LLM Evaluators Human Enough?](https://arxiv.org/abs/2508.10014)
- [SLM vs LLM: Accuracy, Latency, Cost Trade-Offs 2025](https://labelyourdata.com/articles/llm-fine-tuning/slm-vs-llm)

### Model Comparisons
- [LLM Comparison 2025: GPT-4 vs Claude vs Gemini](https://www.ideas2it.com/blogs/llm-comparison)
- [Best Open Source LLMs of 2025](https://klu.ai/blog/open-source-llm-models)

---

## Related Documentation

- [Provider APIs Reference](../../reference/provider-apis.md)
- [F-002: LLM Provider Abstraction](../roadmap/features/completed/F-002-llm-provider-abstraction.md)
- [F-106: Quality Metrics Scoring](../roadmap/features/completed/F-106-quality-metrics-scoring.md)
