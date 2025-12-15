# F-115: Synthetic Data Generation Pipeline

## Overview

| Attribute | Value |
|-----------|-------|
| **Research** | R-013 |
| **Milestone** | v1.4.0 |
| **Priority** | P2 |
| **Category** | Privacy |

## Problem Statement

Organisations often have valuable user research data that cannot be shared or processed by cloud services due to privacy constraints:

- Customer interview transcripts with PII
- Internal user studies with confidential information
- Healthcare patient feedback
- Financial customer research

These datasets could inform persona generation, but their sensitive nature prevents use with frontier models. Users need a way to generate **synthetic training data** that preserves the statistical and semantic properties of the original data while removing all PII.

## Design Approach

- Generate privacy-safe synthetic data from sensitive sources
- Combine PII detection with local model generation
- Validate synthetic data quality against original
- Support multiple output formats (CSV, JSON, YAML)
- Optional frontier refinement of synthetic data

### Synthetic Data Pipeline

```
Sensitive Input → PII Detection → Statistical Analysis → Local LLM Generation
        ↓               ↓                 ↓                      ↓
   Original Data    Anonymised       Distribution          Synthetic Output
                    Version          Patterns
```

### Python API

```python
from persona.core.synthetic import SyntheticGenerator

# Create generator
generator = SyntheticGenerator(
    provider="ollama",
    model="qwen2.5:72b"
)

# Generate synthetic data from sensitive source
result = generator.synthesise(
    input_path="interviews.csv",
    output_path="synthetic.csv",
    count=100,  # Number of synthetic records
    preserve_schema=True,  # Match column structure
    preserve_distribution=True,  # Match statistical distribution
)

# Validate synthetic data
validation = generator.validate(
    original="interviews.csv",
    synthetic="synthetic.csv"
)
# ValidationResult(
#     schema_match=True,
#     distribution_similarity=0.92,
#     pii_detected=False,
#     semantic_similarity=0.85
# )
```

### CLI Integration

```bash
# Generate synthetic data from sensitive source
persona synthesise --input interviews.csv --output synthetic.csv

# Specify count and model
persona synthesise --input interviews.csv --output synthetic.csv --count 100 --model qwen2.5:72b

# Validate synthetic data quality
persona synthesise validate --original interviews.csv --synthetic synthetic.csv

# Preview synthetic sample (dry run)
persona synthesise preview --input interviews.csv --count 5
```

### Synthetic Data Quality Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Schema Match** | Column names and types preserved | 100% |
| **Distribution Similarity** | Statistical distribution preserved | >85% |
| **PII Presence** | No PII in synthetic output | 0% |
| **Semantic Similarity** | Meaning preserved | >80% |
| **Diversity** | Variety in synthetic records | >70% |

### Generation Strategy

1. **Analyse Original Data**
   - Extract schema (columns, types)
   - Calculate distributions (categorical frequencies, numeric ranges)
   - Identify patterns and relationships

2. **Generate Prompt**
   - Include schema requirements
   - Include distribution guidance
   - Include example format (anonymised)

3. **Local LLM Generation**
   - Generate synthetic records matching schema
   - Maintain statistical properties
   - Ensure no PII in output

4. **Validation**
   - Verify schema compliance
   - Check distribution similarity
   - Scan for PII
   - Evaluate semantic quality

## Implementation Tasks

- [ ] Create `src/persona/core/synthetic/__init__.py`
- [ ] Create `src/persona/core/synthetic/generator.py` with `SyntheticGenerator`
- [ ] Create `src/persona/core/synthetic/analyser.py` for data analysis
- [ ] Create `src/persona/core/synthetic/validator.py` for quality validation
- [ ] Implement schema extraction
- [ ] Implement distribution analysis
- [ ] Create generation prompt templates
- [ ] Integrate with F-113 PII detection
- [ ] Implement validation pipeline
- [ ] Create `persona synthesise` CLI subcommand
- [ ] Add preview/dry-run mode
- [ ] Support CSV, JSON, YAML output formats
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Document quality metrics and interpretation

## Success Criteria

- [ ] `persona synthesise --input interviews.csv --output synthetic.csv` works
- [ ] Output contains no PII from input (verified by F-108)
- [ ] Synthetic data statistically similar to original (>85% distribution match)
- [ ] Schema preserved (columns, types)
- [ ] Validation command confirms quality
- [ ] Unit test coverage >= 90%

## Dependencies

- F-112: Native Ollama Provider
- F-113: PII Detection & Anonymisation

## Technical Considerations

### Supported Input Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| CSV | `.csv` | Primary format |
| JSON | `.json` | Array of objects |
| YAML | `.yaml`, `.yml` | Array of objects |
| Excel | `.xlsx` | First sheet only |

### Distribution Preservation

For categorical columns:
- Count frequency of each value
- Generate synthetic values matching distribution

For numeric columns:
- Calculate mean, std, min, max
- Generate values within distribution bounds

For text columns:
- Extract length distribution
- Preserve semantic patterns (e.g., feedback tone)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| PII leakage in output | Multi-pass PII scan, conservative detection |
| Poor distribution match | Statistical validation, iterative refinement |
| Semantic drift | Include anonymised examples in prompt |
| Large dataset handling | Batch processing, progress feedback |

---

## Related Documentation

- [R-013: Local Model Assessment](../../../research/R-013-local-model-assessment.md)
- [F-112: Native Ollama Provider](F-112-native-ollama-provider.md)
- [F-113: PII Detection & Anonymisation](F-113-pii-detection-anonymisation.md)
- [Gretel AI Synthetic Data](https://github.com/gretelai/gretel-synthetics)
