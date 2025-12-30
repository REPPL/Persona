# F-147: Bias Detection Multi-Method

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-147 |
| **Title** | Bias Detection Multi-Method |
| **Priority** | P1 (High) |
| **Category** | Compliance |
| **Milestone** | [v1.14.0](../../milestones/v1.14.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-120 (Bias Detection) |

---

## Problem Statement

Current single-method bias detection has limitations:
- High false positive rate for certain domains
- Misses subtle or cultural biases
- No confidence scoring
- Limited explainability

Multi-method ensemble detection provides more robust, trustworthy results.

---

## Design Approach

Combine multiple bias detection methods with ensemble voting and confidence scoring.

---

## Key Capabilities

### 1. Multi-Method Detection

Run multiple detection methods simultaneously.

```bash
# Ensemble detection (default)
persona bias detect --method ensemble ./personas/

# Specific methods
persona bias detect --method lexical ./personas/
persona bias detect --method embedding ./personas/
persona bias detect --method llm ./personas/
```

### 2. Ensemble Confidence Scoring

Weight and combine method results.

```python
class EnsembleDetector:
    weights = {
        "lexical": 0.3,
        "embedding": 0.3,
        "llm": 0.4
    }

    def detect(self, persona: dict) -> BiasReport:
        results = {}
        for method, detector in self.detectors.items():
            results[method] = detector.detect(persona)

        return self._combine_results(results)
```

### 3. Cultural Context Awareness

Apply cultural context to reduce false positives.

```bash
# Specify cultural context
persona bias detect --locale en_GB --cultural-norms british ./personas/
```

### 4. Method Comparison

Compare detection methods for analysis.

```bash
persona bias compare --methods lexical,embedding,llm ./personas/
```

**Output:**
```
Bias Detection Method Comparison
════════════════════════════════════════════════════════════════

Method Agreement Matrix
─────────────────────────
| | lexical | embedding | llm |
|---|---------|-----------|-----|
| lexical | 100% | 72% | 68% |
| embedding | 72% | 100% | 85% |
| llm | 68% | 85% | 100% |

Detection Statistics
────────────────────
| Method | Detections | Unique | Confidence |
|--------|------------|--------|------------|
| lexical | 15 | 5 | 0.82 |
| embedding | 12 | 3 | 0.76 |
| llm | 18 | 8 | 0.91 |
| ensemble | 22 | - | 0.87 |

Recommendation: Use ensemble for production
```

---

## CLI Commands

```bash
# Detection
persona bias detect [--method METHOD] [--threshold N] PATH
persona bias detect --method ensemble --verbose PATH

# Comparison
persona bias compare --methods METHOD,METHOD PATH

# Configuration
persona bias config --show
persona bias config --set ensemble.weights.llm 0.5
```

---

## Success Criteria

- [ ] Ensemble detection reduces false positives by 50%
- [ ] Confidence scores correlate with accuracy
- [ ] Cultural context reduces inappropriate flags
- [ ] Method comparison aids debugging
- [ ] Explainability improved
- [ ] Test coverage >= 85%

---

## Related Documentation

- [v1.14.0 Milestone](../../milestones/v1.14.0.md)
- [F-120: Bias Detection](../completed/F-120-bias-detection.md)
- [R-029: Bias Detection Cross-Validation](../../../research/R-029-bias-detection-cross-validation.md)

---

**Status**: Planned
