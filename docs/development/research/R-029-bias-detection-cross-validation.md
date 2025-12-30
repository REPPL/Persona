# R-029: Bias Detection Cross-Validation

## Executive Summary

This research analyses approaches for improving bias detection accuracy through multi-method cross-validation. The current Persona bias detector has known limitations with cultural contexts and edge cases. Recommended approach: implement ensemble detection using multiple complementary methods (lexical, embedding-based, LLM-based) with cross-validation to reduce false positives and improve coverage.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-029 |
| **Category** | Research Compliance |
| **Status** | Complete |
| **Priority** | P2 |
| **Informs** | Enhanced bias detection features, Research compliance |

---

## Problem Statement

The current bias detection implementation (F-120) has limitations:
- Single-method detection (embedding similarity)
- Cultural context blind spots
- High false positive rate in certain domains
- Limited coverage of intersectional biases
- No confidence scoring or uncertainty quantification

For research compliance, bias detection must be robust, transparent, and culturally aware.

---

## State of the Art Analysis

### Bias Detection Methods

#### 1. Lexical/Pattern-Based

Search for known biased terms and patterns.

```python
class LexicalBiasDetector:
    def __init__(self, lexicon_path: Path):
        self.lexicon = self._load_lexicon(lexicon_path)

    def detect(self, text: str) -> list[BiasMatch]:
        matches = []
        for category, patterns in self.lexicon.items():
            for pattern in patterns:
                if match := re.search(pattern, text, re.IGNORECASE):
                    matches.append(BiasMatch(
                        category=category,
                        text=match.group(),
                        position=match.span(),
                        method="lexical"
                    ))
        return matches
```

| Aspect | Assessment |
|--------|------------|
| Precision | ✅ High for known terms |
| Recall | ❌ Misses novel/subtle bias |
| Speed | ✅ Very fast |
| Maintainability | ⚠️ Requires lexicon updates |

#### 2. Embedding-Based (Current)

Measure semantic similarity to known bias categories.

```python
class EmbeddingBiasDetector:
    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(model)
        self.bias_embeddings = self._load_category_embeddings()

    def detect(self, text: str) -> list[BiasScore]:
        text_embedding = self.encoder.encode(text)

        scores = []
        for category, category_embedding in self.bias_embeddings.items():
            similarity = cosine_similarity(text_embedding, category_embedding)
            if similarity > self.threshold:
                scores.append(BiasScore(
                    category=category,
                    score=similarity,
                    method="embedding"
                ))
        return scores
```

| Aspect | Assessment |
|--------|------------|
| Precision | ⚠️ Context-dependent |
| Recall | ⚠️ Better than lexical |
| Speed | ⚠️ Moderate |
| Adaptability | ✅ Learns from examples |

#### 3. LLM-Based Detection

Use language models to identify bias.

```python
class LLMBiasDetector:
    PROMPT = """
    Analyse the following persona for potential biases:

    {persona}

    Consider:
    - Demographic stereotypes
    - Cultural assumptions
    - Socioeconomic biases
    - Gender/age biases
    - Ableism indicators

    Return JSON with:
    - biases: list of detected biases
    - confidence: 0-1 for each
    - explanation: reasoning
    """

    async def detect(self, persona: dict) -> BiasAnalysis:
        response = await self.llm.generate(
            self.PROMPT.format(persona=json.dumps(persona))
        )
        return BiasAnalysis.parse(response)
```

| Aspect | Assessment |
|--------|------------|
| Precision | ✅ High with good prompts |
| Recall | ✅ Catches subtle biases |
| Speed | ❌ Slow, expensive |
| Explainability | ✅ Provides reasoning |

#### 4. Classifier-Based

Train supervised classifier on labelled data.

```python
class ClassifierBiasDetector:
    def __init__(self, model_path: Path):
        self.model = load_model(model_path)
        self.tokenizer = load_tokenizer(model_path)

    def detect(self, text: str) -> list[BiasClassification]:
        inputs = self.tokenizer(text, return_tensors="pt")
        outputs = self.model(**inputs)

        predictions = []
        for i, score in enumerate(outputs.logits[0]):
            if score > self.threshold:
                predictions.append(BiasClassification(
                    category=self.labels[i],
                    probability=torch.sigmoid(score).item(),
                    method="classifier"
                ))
        return predictions
```

| Aspect | Assessment |
|--------|------------|
| Precision | ✅ High with good training |
| Recall | ⚠️ Limited to training distribution |
| Speed | ✅ Fast inference |
| Adaptability | ❌ Requires retraining |

### Cross-Validation Strategies

#### 1. Simple Majority Voting

```python
def majority_vote(detections: list[list[BiasMatch]]) -> list[BiasMatch]:
    """Accept bias if detected by majority of methods."""
    all_categories = set()
    for detection in detections:
        for match in detection:
            all_categories.add(match.category)

    confirmed = []
    for category in all_categories:
        votes = sum(1 for d in detections if any(m.category == category for m in d))
        if votes > len(detections) / 2:
            confirmed.append(category)

    return confirmed
```

#### 2. Weighted Ensemble

```python
@dataclass
class WeightedEnsemble:
    weights: dict[str, float]  # method -> weight
    threshold: float = 0.5

    def combine(self, detections: dict[str, list[BiasScore]]) -> list[BiasResult]:
        category_scores = defaultdict(float)

        for method, matches in detections.items():
            weight = self.weights.get(method, 1.0)
            for match in matches:
                category_scores[match.category] += match.score * weight

        # Normalise
        total_weight = sum(self.weights.values())
        results = []
        for category, score in category_scores.items():
            normalised = score / total_weight
            if normalised > self.threshold:
                results.append(BiasResult(
                    category=category,
                    confidence=normalised,
                    methods=list(detections.keys())
                ))

        return results
```

#### 3. Confidence-Based Fusion

```python
class ConfidenceFusion:
    def combine(self, detections: dict[str, BiasAnalysis]) -> BiasAnalysis:
        """Combine results weighted by method confidence."""
        combined = BiasAnalysis()

        for method, analysis in detections.items():
            method_confidence = self._get_method_confidence(method, analysis)

            for bias in analysis.biases:
                existing = combined.get_bias(bias.category)
                if existing:
                    # Update confidence using Bayesian-ish combination
                    existing.confidence = self._combine_confidences(
                        existing.confidence,
                        bias.confidence * method_confidence
                    )
                else:
                    combined.add_bias(bias.with_confidence(
                        bias.confidence * method_confidence
                    ))

        return combined
```

### Cultural Context Handling

#### Bias Lexicon Localisation

```yaml
# lexicons/bias_terms_en_GB.yaml
gender:
  terms:
    - "mankind"
    - "manpower"
  cultural_context: "British English tends to use gender-neutral alternatives"

# lexicons/bias_terms_en_US.yaml
gender:
  terms:
    - "fireman"
    - "policeman"
  cultural_context: "American English commonly uses gendered job titles"
```

#### Cultural Norms Database

```python
@dataclass
class CulturalNorm:
    region: str
    category: str
    norm: str
    is_bias_indicator: bool
    context: str

CULTURAL_NORMS = [
    CulturalNorm(
        region="East Asia",
        category="age",
        norm="Respect for elders in professional settings",
        is_bias_indicator=False,
        context="Age-based hierarchy is culturally normative"
    ),
    CulturalNorm(
        region="Western",
        category="age",
        norm="Age-neutral treatment expected",
        is_bias_indicator=True,
        context="Age-based assumptions may indicate bias"
    ),
]
```

---

## Evaluation Matrix

| Method | Precision | Recall | Speed | Explainability | Cultural Awareness |
|--------|-----------|--------|-------|----------------|-------------------|
| Lexical | ✅ | ❌ | ✅ | ✅ | ⚠️ |
| Embedding | ⚠️ | ⚠️ | ⚠️ | ❌ | ⚠️ |
| LLM-based | ✅ | ✅ | ❌ | ✅ | ✅ |
| Classifier | ✅ | ⚠️ | ✅ | ⚠️ | ❌ |
| Ensemble | ✅ | ✅ | ⚠️ | ✅ | ⚠️ |

---

## Recommendation

### Primary: Ensemble Detection with Cultural Context

Implement multi-method bias detection with weighted ensemble combination.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Ensemble Bias Detector                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input Text                                                  │
│       │                                                      │
│       ├───────────────┬───────────────┬───────────────┐     │
│       ▼               ▼               ▼               ▼     │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  │
│  │ Lexical │    │Embedding│    │   LLM   │    │Classifier│  │
│  │Detector │    │Detector │    │Detector │    │ Detector │  │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘  │
│       │               │               │               │     │
│       └───────────────┴───────────────┴───────────────┘     │
│                           │                                  │
│                           ▼                                  │
│                  ┌─────────────────┐                        │
│                  │Weighted Ensemble│                        │
│                  │    Combiner     │                        │
│                  └─────────────────┘                        │
│                           │                                  │
│                           ▼                                  │
│                  ┌─────────────────┐                        │
│                  │Cultural Context │                        │
│                  │    Filter       │                        │
│                  └─────────────────┘                        │
│                           │                                  │
│                           ▼                                  │
│                    Final Results                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### CLI Commands

```bash
# Run ensemble bias detection
persona bias detect ./personas.json --method ensemble

# Compare detection methods
persona bias compare ./personas.json --methods lexical embedding llm

# Configure cultural context
persona bias config --locale en_GB --cultural-norms british

# View detection confidence
persona bias detect ./persona.json --show-confidence

# Generate bias report
persona bias report ./personas.json --output bias-report.md
```

### Configuration

```yaml
bias_detection:
  ensemble:
    enabled: true
    methods:
      lexical:
        enabled: true
        weight: 0.3
        lexicon: default  # or path to custom
      embedding:
        enabled: true
        weight: 0.3
        model: all-MiniLM-L6-v2
        threshold: 0.7
      llm:
        enabled: true
        weight: 0.4
        provider: anthropic
        model: claude-haiku
      classifier:
        enabled: false  # Requires trained model
        weight: 0.3
        model_path: null

    combination:
      method: weighted  # weighted, majority, confidence
      threshold: 0.5

  cultural_context:
    enabled: true
    locale: en_GB
    norms: default
    allow_cultural_override: true

  reporting:
    include_confidence: true
    include_reasoning: true
    include_methods: true
```

### Implementation

```python
class EnsembleBiasDetector:
    def __init__(self, config: BiasConfig):
        self.methods = self._init_methods(config)
        self.combiner = WeightedEnsemble(config.weights)
        self.cultural_filter = CulturalContextFilter(config.cultural_context)

    async def detect(self, persona: dict) -> BiasReport:
        text = self._extract_text(persona)

        # Run all methods in parallel
        results = await asyncio.gather(*[
            method.detect(text) for method in self.methods.values()
        ])

        detections = dict(zip(self.methods.keys(), results))

        # Combine results
        combined = self.combiner.combine(detections)

        # Apply cultural context
        filtered = self.cultural_filter.apply(combined)

        return BiasReport(
            biases=filtered,
            method_results=detections,
            cultural_context=self.cultural_filter.context
        )
```

---

## Implementation Priority

1. **Method abstraction layer** - Unified interface for detectors
2. **Weighted ensemble combiner** - Combine method results
3. **Cultural context filter** - Apply cultural norms
4. **LLM-based detector** - Add LLM detection option
5. **Comparison tooling** - Evaluate method effectiveness

---

## References

1. [Fairness in Machine Learning](https://fairmlbook.org/)
2. [Bias in NLP Survey](https://arxiv.org/abs/2101.11718)
3. [Cultural Bias in AI](https://arxiv.org/abs/2203.07316)
4. [Ensemble Methods for Bias Detection](https://aclanthology.org/2021.findings-acl.315/)
5. [Perspective API](https://perspectiveapi.com/)

---

## Related Documentation

- [F-120: Bias Detection](../roadmap/features/completed/F-120-bias-detection.md)
- [F-121: Research Ethics Compliance](../roadmap/features/completed/F-121-research-ethics-compliance.md)
- [R-015: Persona Quality Taxonomy](R-015-persona-quality-taxonomy.md)

---

**Status**: Complete
