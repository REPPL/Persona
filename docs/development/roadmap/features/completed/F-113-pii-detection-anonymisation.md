# F-113: PII Detection & Anonymisation

## Overview

| Attribute | Value |
|-----------|-------|
| **Research** | R-013 |
| **Milestone** | v1.3.0 |
| **Priority** | P1 |
| **Category** | Privacy |

## Problem Statement

Enterprises often have user research data containing Personally Identifiable Information (PII) that cannot be sent to cloud-based LLM providers due to:

- **GDPR compliance** - EU data protection regulations
- **HIPAA requirements** - Healthcare data protection
- **Data residency** - Legal requirements to keep data on-premise
- **Confidentiality** - Trade secrets, internal documents

Without PII detection and anonymisation, users must manually scrub data before using Persona, or avoid using the tool entirely for sensitive research.

## Design Approach

- Integrate Microsoft Presidio for PII detection
- Support multiple anonymisation strategies (redact, replace, hash)
- Optional dependency via `[privacy]` extra
- Seamless integration with data loading pipeline
- CLI flag for easy activation

### Privacy Pipeline

```
Input Data → PII Detection → Anonymisation → LLM Generation
                ↓                ↓
          [Presidio]       [Configurable Strategy]
                ↓                ↓
         Entity Detection   redact | replace | hash
```

### Python API

```python
from persona.core.privacy import PIIDetector, AnonymisationStrategy

# Detect PII
detector = PIIDetector()
entities = detector.detect("Contact John Smith at john@example.com")
# [PIIEntity(type="PERSON", text="John Smith", start=8, end=18),
#  PIIEntity(type="EMAIL", text="john@example.com", start=22, end=38)]

# Anonymise with different strategies
safe_text = detector.anonymise(text, strategy=AnonymisationStrategy.REDACT)
# "Contact [PERSON] at [EMAIL]"

safe_text = detector.anonymise(text, strategy=AnonymisationStrategy.REPLACE)
# "Contact Jane Doe at fake@example.com"

safe_text = detector.anonymise(text, strategy=AnonymisationStrategy.HASH)
# "Contact a1b2c3d4 at e5f6g7h8"
```

### CLI Integration

```bash
# Anonymise input before generation
persona generate --input sensitive.csv --anonymise

# Specify anonymisation strategy
persona generate --input sensitive.csv --anonymise --anonymise-strategy replace

# Preview what would be anonymised (dry run)
persona privacy scan --input sensitive.csv

# Anonymise file without generation
persona privacy anonymise --input sensitive.csv --output safe.csv
```

### Supported PII Types

| Type | Examples | Detection Method |
|------|----------|------------------|
| `PERSON` | John Smith, Dr. Jones | NER |
| `EMAIL` | user@domain.com | Regex + validation |
| `PHONE` | +44 123 456 7890 | Regex + format |
| `ADDRESS` | 123 Main St, London | NER |
| `SSN` | 123-45-6789 | Regex + checksum |
| `CREDIT_CARD` | 4111-1111-1111-1111 | Regex + Luhn |
| `DATE_OF_BIRTH` | 15/03/1985 | Regex + context |
| `IP_ADDRESS` | 192.168.1.1 | Regex |
| `LOCATION` | London, United Kingdom | NER |

## Implementation Tasks

- [x] Add `presidio-analyzer`, `presidio-anonymizer` to `[privacy]` extra in `pyproject.toml`
- [x] Create `src/persona/core/privacy/__init__.py`
- [x] Create `src/persona/core/privacy/detector.py` with `PIIDetector` class
- [x] Create `src/persona/core/privacy/anonymiser.py` with strategies
- [x] Create `src/persona/core/privacy/entities.py` with `PIIEntity` dataclass
- [x] Integrate with `DataLoader` pipeline
- [x] Add `--anonymise` flag to CLI
- [x] Add `--anonymise-strategy` option
- [x] Create `persona privacy scan` subcommand
- [x] Create `persona privacy anonymise` subcommand
- [x] Write unit tests for detection
- [x] Write unit tests for anonymisation
- [ ] Document supported PII types
- [ ] Add usage examples to docs

## Success Criteria

- [x] `persona generate --input sensitive.csv --anonymise` works
- [x] Detects: names, emails, phone numbers, addresses, SSNs (when Presidio installed)
- [x] Three anonymisation strategies available: redact, replace, hash
- [x] `persona privacy scan` shows detected PII without modification
- [x] Unit test coverage >= 90% (entities: 100%, available without Presidio)
- [x] Works without `[privacy]` extra (graceful import error)

## Dependencies

- F-112: Native Ollama Provider (for local-only privacy workflows)

### Python Dependencies

```toml
[project.optional-dependencies]
privacy = [
    "presidio-analyzer>=2.2",
    "presidio-anonymizer>=2.2",
    "spacy>=3.7",
]
```

**Post-install requirement:**
```bash
python -m spacy download en_core_web_lg
```

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| spaCy model download required | Document in install instructions, detect missing model |
| Large dependency size (~500MB) | Optional extra, not in core |
| False negatives (missed PII) | Document limitations, allow custom recognisers |
| False positives | Configurable confidence threshold |

---

## Related Documentation

- [R-013: Local Model Assessment](../../../research/R-013-local-model-assessment.md)
- [Microsoft Presidio Documentation](https://microsoft.github.io/presidio/)
- [F-112: Native Ollama Provider](F-112-native-ollama-provider.md)
