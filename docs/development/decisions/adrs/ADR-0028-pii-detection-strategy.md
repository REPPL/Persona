# ADR-0028: PII Detection Strategy

## Status

Accepted

## Context

Persona v1.3.0 needed PII detection and anonymisation for:
- GDPR/HIPAA compliance when processing user research data
- Safe data sharing across teams and organisations
- Privacy-preserving cloud API usage
- Research ethics requirements

The implementation needed to:
- Detect common PII types (names, emails, phones, etc.)
- Support multiple anonymisation strategies
- Be configurable for different regulatory contexts
- Work with minimal false positives/negatives

## Decision

Implement PII detection using **Microsoft Presidio** with configurable recognisers:

### Architecture

```
Input Data
    ↓
┌─────────────────────────────────────────┐
│ Presidio Analyzer                        │
│ ┌─────────────────────────────────────┐ │
│ │ NER Recognisers (spaCy)             │ │
│ │ - PERSON, ORG, GPE, DATE            │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ Pattern Recognisers (regex)         │ │
│ │ - EMAIL, PHONE, SSN, CREDIT_CARD    │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ Custom Recognisers                   │ │
│ │ - Project-specific patterns          │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Presidio Anonymizer                      │
│ - Redact: [PERSON]                       │
│ - Replace: John → Michael                │
│ - Hash: John → 8c3d...                   │
│ - Encrypt: John → aGVsbG8=               │
└─────────────────────────────────────────┘
    ↓
Anonymised Data
```

### Entity Types

| Entity | Detection Method | Example |
|--------|------------------|---------|
| PERSON | NER (spaCy) | "John Smith" |
| EMAIL | Regex | "john@example.com" |
| PHONE | Regex | "+1-555-123-4567" |
| CREDIT_CARD | Regex + checksum | "4111-1111-1111-1111" |
| SSN | Regex | "123-45-6789" |
| DATE_OF_BIRTH | Regex + NER | "Born: 01/15/1985" |
| ADDRESS | NER (GPE) | "123 Main St, NYC" |
| IP_ADDRESS | Regex | "192.168.1.1" |
| URL | Regex | "https://example.com" |
| ORGANISATION | NER | "Acme Corporation" |

### Anonymisation Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **redact** | Replace with [TYPE] | Maximum privacy |
| **replace** | Replace with fake value | Readability |
| **hash** | SHA-256 hash | Linkability |
| **mask** | Partial mask (Jo***) | Partial visibility |

### CLI Integration

```bash
# Scan for PII
persona privacy scan ./data/interviews/

# Anonymise with redaction
persona privacy anonymise ./data/ --strategy redact

# Anonymise with replacement (using Faker)
persona privacy anonymise ./data/ --strategy replace

# Anonymise inline during generation
persona generate --from data/ --anonymise --anonymise-strategy replace
```

### Configuration

```yaml
privacy:
  pii_detection:
    enabled: true
    language: en
    entities:
      - PERSON
      - EMAIL
      - PHONE
      - CREDIT_CARD
      - SSN
    threshold: 0.7  # Confidence threshold
    custom_patterns:
      - name: EMPLOYEE_ID
        pattern: "EMP-\\d{6}"
        score: 0.9
  anonymisation:
    default_strategy: redact
    per_entity:
      PERSON: replace
      EMAIL: hash
      PHONE: redact
```

## Consequences

**Positive:**
- Industry-standard library (Microsoft-backed)
- Multi-language NER support
- Extensible with custom recognisers
- Multiple anonymisation strategies
- Well-documented and actively maintained

**Negative:**
- Requires spaCy model download (~500MB)
- NER not perfect (some false positives/negatives)
- Processing adds latency
- May over-anonymise legitimate non-PII names

## Alternatives Considered

### Custom Regex-Only

**Description:** Build custom regex patterns for PII detection.
**Pros:** Lightweight, no ML dependencies, fast.
**Cons:** Poor accuracy for names/locations, maintenance burden.
**Why Not Chosen:** NER-based detection significantly more accurate.

### AWS Comprehend

**Description:** Use AWS Comprehend PII detection.
**Pros:** High accuracy, managed service.
**Cons:** Sends data to cloud, cost per request, AWS dependency.
**Why Not Chosen:** Defeats privacy purpose; data leaves machine.

### spaCy NER Only

**Description:** Use spaCy NER directly without Presidio.
**Pros:** Simpler dependency, good NER.
**Cons:** No anonymisation, no pattern matching, more code needed.
**Why Not Chosen:** Presidio provides complete solution.

### Private AI

**Description:** Commercial PII detection service.
**Pros:** High accuracy, compliance-focused.
**Cons:** Paid service, cloud-based.
**Why Not Chosen:** Want open-source, local solution.

## Research Reference

See [R-013: Local Model Assessment](../../research/R-013-local-model-assessment.md) for PII framework analysis.

## Implementation Details

### Detector Module

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PIIDetector:
    def __init__(self, language: str = "en", entities: list[str] | None = None):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.language = language
        self.entities = entities or self.DEFAULT_ENTITIES

    def detect(self, text: str) -> list[PIIEntity]:
        """Detect PII in text."""
        results = self.analyzer.analyze(
            text=text,
            language=self.language,
            entities=self.entities
        )
        return [
            PIIEntity(
                type=r.entity_type,
                start=r.start,
                end=r.end,
                score=r.score,
                text=text[r.start:r.end]
            )
            for r in results
        ]

    def anonymise(
        self,
        text: str,
        strategy: str = "redact"
    ) -> str:
        """Anonymise detected PII."""
        results = self.analyzer.analyze(text, self.language, self.entities)
        operators = self._get_operators(strategy)
        return self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        ).text
```

### Integration with Generation

```python
async def generate_with_privacy(
    self,
    data: str,
    anonymise: bool = True,
    strategy: str = "redact"
) -> list[Persona]:
    if anonymise:
        data = self.pii_detector.anonymise(data, strategy)

    return await self.generate(data)
```

### Faker Integration for Replacement

```python
from faker import Faker

class ReplacementOperator:
    def __init__(self):
        self.faker = Faker()
        self.cache = {}  # Consistent replacement

    def operate(self, text: str, entity_type: str) -> str:
        if text in self.cache:
            return self.cache[text]

        replacement = self._generate_replacement(entity_type)
        self.cache[text] = replacement
        return replacement

    def _generate_replacement(self, entity_type: str) -> str:
        if entity_type == "PERSON":
            return self.faker.name()
        elif entity_type == "EMAIL":
            return self.faker.email()
        elif entity_type == "PHONE":
            return self.faker.phone_number()
        # ... etc
```

---

## Related Documentation

- [F-113: PII Detection & Anonymisation](../../roadmap/features/completed/F-113-pii-detection-anonymisation.md)
- [R-013: Local Model Assessment](../../research/R-013-local-model-assessment.md)
- [Microsoft Presidio Documentation](https://microsoft.github.io/presidio/)
- [GDPR Article 4 - Personal Data Definition](https://gdpr.eu/article-4-definitions/)
