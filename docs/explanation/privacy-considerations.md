# Privacy Considerations

This document explains the privacy principles and safeguards built into Persona, particularly around handling source data and generating outputs that protect research participants.

## Core Privacy Principles

### 1. Data Stays Local

Persona processes data locally on your machine. Source files are never uploaded to external services except when explicitly sent to LLM providers for generation.

**What gets sent to LLM providers:**
- Anonymised/aggregated source data (configurable)
- Generation prompts
- Configuration parameters

**What stays local:**
- Original source files
- Generated personas
- Experiment logs and metadata

### 2. Abstraction Over Quotation

When generating personas, Persona abstracts patterns from source data rather than quoting directly. This protects individual research participants.

**Instead of:**
> "User said: 'I hate when the app crashes during checkout'"

**Persona generates:**
> "Experiences frustration with application stability during critical workflows"

### 3. Synthetic Markers

All generated content includes synthetic markers to prevent confusion with real user data:

```json
{
  "synthetic_marker": "SYNTHETIC_PERSONA",
  "provenance": {
    "generated_at": "2025-12-14T10:30:00Z",
    "tool": "persona",
    "version": "1.0.0"
  }
}
```

## Privacy in Conversation Scripts

The conversation scripts feature (F-104) has additional privacy safeguards:

### Quote Abstraction

The `QuoteAbstractor` component extracts linguistic features without exposing actual quotes:

| Source | Abstracted |
|--------|------------|
| "I literally can't even with this interface" | Uses emphatic language; expresses frustration |
| "The button is impossible to find" | Reports discoverability issues |

### Scenario Generalisation

Specific incidents are generalised into patterns:

| Source | Generalised |
|--------|-------------|
| "Last Tuesday at 3pm my order failed" | Experiences occasional order failures |
| "My colleague Sarah showed me this workaround" | Learns features through peer support |

### Privacy Audit

Before outputting conversation scripts, a privacy audit runs:

1. **Embedding Similarity Check**: Compares output against source data embeddings
2. **Leakage Score**: Must be < 0.1 to pass
3. **Block on Failure**: Output blocked if audit fails

## Best Practices

### For Source Data

1. **Pre-anonymise sensitive data** before loading into Persona
2. **Use codes** instead of real names in transcripts
3. **Remove identifiers** (dates, locations, names) from raw data
4. **Review source data** for unexpected PII before generation

### For Generated Output

1. **Review personas** before sharing with wider team
2. **Use synthetic markers** when presenting personas
3. **Don't claim personas represent individuals**
4. **Store outputs securely** (they may contain inferred characteristics)

### For Conversation Scripts

1. **Run privacy audit** (enabled by default)
2. **Review character cards** for any leaked details
3. **Test conversations** before using in research
4. **Document provenance** when using scripts with LLMs

## Compliance Considerations

Persona is a tool; compliance responsibility lies with users. Consider:

- **GDPR**: Ensure lawful basis for processing source data
- **Research Ethics**: Follow institutional review board requirements
- **Data Retention**: Delete source data according to your policies
- **Consent**: Ensure participants consented to this type of analysis

## Technical Implementation

Privacy features are implemented in:

- `persona.core.privacy` - Privacy audit and checks
- `persona.core.abstraction` - Quote and scenario abstraction
- `persona.core.script_generation` - Conversation script generation

See feature documentation for implementation details:
- [F-104: Conversation Scripts](../development/roadmap/features/completed/F-104-conversation-scripts.md)

---

## Related Documentation

- [How Generation Works](how-generation-works.md) - Generation pipeline overview
- [Reproducibility](reproducibility.md) - Experiment reproducibility
- [F-104: Conversation Scripts](../development/roadmap/features/completed/F-104-conversation-scripts.md) - Privacy-preserving scripts
- [Privacy Setup Guide](../guides/privacy-setup.md) - PII detection and anonymisation
