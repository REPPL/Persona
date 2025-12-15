# Privacy Module Setup Guide

This guide explains how to install and use the PII detection and anonymisation features in Persona.

## Installation

The privacy module is an optional dependency. Install it with:

```bash
pip install persona[privacy]
```

This installs:
- `presidio-analyzer` - Microsoft's PII detection engine
- `presidio-anonymizer` - Anonymisation functionality
- `spacy` - Natural language processing library

### Download spaCy Model

After installation, download the required spaCy model:

```bash
python -m spacy download en_core_web_lg
```

This downloads the large English model (~500MB) needed for accurate PII detection.

## Quick Start

### Scan for PII

Check what PII exists in your data without modifying it:

```bash
persona privacy scan --input ./data/interviews.csv
```

### Anonymise Data

Create an anonymised version of your data:

```bash
persona privacy anonymise --input sensitive.csv --output safe.csv
```

### Anonymise During Generation

Anonymise PII automatically before sending to LLM:

```bash
persona generate --from sensitive.csv --anonymise
```

## Anonymisation Strategies

Choose from three strategies:

### Redact (Default)

Replace PII with type placeholders:

```bash
persona privacy anonymise --input data.csv --strategy redact
```

**Input:** `Contact John Smith at john@example.com`
**Output:** `Contact [PERSON] at [EMAIL_ADDRESS]`

### Replace

Replace PII with fake but realistic data:

```bash
persona privacy anonymise --input data.csv --strategy replace
```

**Input:** `Contact John Smith at john@example.com`
**Output:** `Contact Anonymous Person at anonymous@example.com`

### Hash

Replace PII with deterministic hashes:

```bash
persona privacy anonymise --input data.csv --strategy hash
```

**Input:** `Contact John Smith at john@example.com`
**Output:** `Contact a1b2c3d4 at e5f6g7h8`

## Supported PII Types

The privacy module detects:

- **PERSON** - Names (John Smith, Dr. Jones)
- **EMAIL_ADDRESS** - Email addresses
- **PHONE_NUMBER** - Phone numbers in various formats
- **LOCATION** - Cities, countries, addresses
- **DATE_TIME** - Dates including birth dates
- **CREDIT_CARD** - Credit card numbers
- **IP_ADDRESS** - IP addresses
- **US_SSN** - US Social Security Numbers
- **UK_NHS** - UK NHS numbers

## Advanced Usage

### Filter by Entity Types

Only detect specific PII types:

```bash
persona privacy scan --input data.csv --entities PERSON,EMAIL_ADDRESS
```

### Adjust Confidence Threshold

Set minimum confidence score (0.0-1.0):

```bash
persona privacy scan --input data.csv --threshold 0.7
```

Lower threshold = more detections (including false positives)
Higher threshold = fewer detections (may miss some PII)

### JSON Output

Get machine-readable output:

```bash
persona privacy scan --input data.csv --json
```

## Troubleshooting

### "PII detection not available" Error

**Cause:** Privacy dependencies not installed.

**Solution:**
```bash
pip install persona[privacy]
python -m spacy download en_core_web_lg
```

### spaCy Model Not Found

**Cause:** Large English model not downloaded.

**Solution:**
```bash
python -m spacy download en_core_web_lg
```

If the download fails, try:
```bash
python -m spacy download en_core_web_sm  # Smaller model
```

### False Positives/Negatives

**Adjust threshold:**
```bash
persona privacy scan --input data.csv --threshold 0.8  # Stricter
persona privacy scan --input data.csv --threshold 0.3  # More permissive
```

## Privacy Workflows

### Local-Only Processing

For maximum privacy, combine with Ollama (F-112):

```bash
# 1. Anonymise data
persona privacy anonymise --input sensitive.csv --output safe.csv

# 2. Generate with local Ollama
persona generate --from safe.csv --provider ollama --model llama2
```

No data leaves your machine!

### GDPR-Compliant Workflow

```bash
# 1. Scan for PII
persona privacy scan --input eu-data.csv

# 2. Anonymise if PII found
persona privacy anonymise --input eu-data.csv --output gdpr-safe.csv

# 3. Generate personas from safe data
persona generate --from gdpr-safe.csv
```

### Quick Anonymisation

Use the `--anonymise` flag for one-step processing:

```bash
persona generate --from sensitive.csv --anonymise --anonymise-strategy replace
```

This automatically detects and anonymises PII before generation.

## Best Practices

1. **Always scan first** - Use `persona privacy scan` to understand what PII exists
2. **Choose appropriate strategy** - Redact for maximum safety, replace for readability
3. **Test with samples** - Verify anonymisation on small samples before processing large datasets
4. **Review results** - Check anonymised output to ensure quality
5. **Document approach** - Record which strategy and settings you used

## Limitations

- **English only** - Currently supports English text only
- **Context matters** - Some PII may be missed without sufficient context
- **No guarantee** - PII detection is not perfect; review sensitive data carefully
- **Performance** - Large files may take time to process

## Related Documentation

- [F-113: PII Detection & Anonymisation](../development/roadmap/features/completed/F-113-pii-detection-anonymisation.md)
- [F-112: Native Ollama Provider](../development/roadmap/features/completed/F-112-native-ollama-provider.md)
- [v1.3.0 Milestone: Local Model Foundation](../development/roadmap/milestones/v1.3.0.md)
- [Microsoft Presidio Documentation](https://microsoft.github.io/presidio/)
