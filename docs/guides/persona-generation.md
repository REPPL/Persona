# Persona Generation Guide

This guide walks you through generating personas from your research data using Persona.

## Overview

Persona transforms qualitative research data (interviews, surveys, feedback) into structured user personas using LLMs. The generation process:

1. **Loads** your data files (CSV, JSON, YAML, TXT)
2. **Normalises** different data formats into a common structure
3. **Sends** data to your chosen LLM provider with generation prompts
4. **Parses** the LLM response into structured persona objects
5. **Validates** the output meets quality requirements
6. **Saves** personas in your preferred output format

## Quick Start

### Generate Your First Persona

```bash
# Basic generation from interview data
persona generate --input ./data/interviews.csv --count 3

# With explicit provider and model
persona generate \
    --input ./data/feedback.json \
    --provider anthropic \
    --model claude-3-5-sonnet-20241022 \
    --count 5
```

### Interactive Mode

If you're unsure about options, use interactive mode:

```bash
persona generate -i
```

This guides you through selecting:
- Input data file
- LLM provider
- Number of personas
- Output format

## Preparing Your Data

### Supported Formats

| Format | Extension | Best For |
|--------|-----------|----------|
| CSV | `.csv` | Structured survey data |
| JSON | `.json` | Nested or complex data |
| YAML | `.yaml`, `.yml` | Human-readable structured data |
| Text | `.txt` | Free-form interview transcripts |

### Data Quality Tips

1. **Include context**: Personas are better when data includes context about user goals, frustrations, and behaviours
2. **Remove PII**: Pre-anonymise sensitive data or use `--anonymise` flag
3. **Sufficient volume**: More data points generally yield richer personas
4. **Consistent structure**: Consistent field names help the LLM understand patterns

### Example Data Structures

**CSV (Survey Responses)**:
```csv
respondent_id,role,pain_points,goals,frequency
001,Manager,"slow reports, manual processes",improve efficiency,daily
002,Developer,"unclear requirements",faster delivery,weekly
```

**JSON (Interview Notes)**:
```json
{
  "interviews": [
    {
      "participant": "P001",
      "role": "Marketing Manager",
      "quotes": [
        "I spend hours on reports that should take minutes"
      ],
      "observations": [
        "Uses multiple tools for single task"
      ]
    }
  ]
}
```

## Generation Options

### Provider Selection

```bash
# Anthropic (recommended for quality)
persona generate --input data.csv --provider anthropic

# OpenAI
persona generate --input data.csv --provider openai

# Google Gemini
persona generate --input data.csv --provider gemini

# Local Ollama (privacy-preserving)
persona generate --input data.csv --provider ollama --model llama3:8b
```

### Persona Count

```bash
# Generate specific number
persona generate --input data.csv --count 5

# Let the system estimate optimal count
persona generate --input data.csv --auto-count
```

### Complexity Levels

```bash
# Simple personas (quick, less detail)
persona generate --input data.csv --complexity simple

# Standard (default)
persona generate --input data.csv --complexity standard

# Detailed (comprehensive)
persona generate --input data.csv --complexity detailed
```

### Privacy Options

```bash
# Anonymise PII before sending to LLM
persona generate --input sensitive.csv --anonymise

# Choose anonymisation strategy
persona generate --input data.csv --anonymise --anonymise-strategy replace
```

## Output Formats

### JSON (Default)

```bash
persona generate --input data.csv --output-format json
```

Produces structured JSON files ideal for programmatic use:

```json
{
  "id": "persona-abc123",
  "name": "Sarah Chen",
  "title": "The Efficiency Seeker",
  "demographics": {
    "age_range": "30-35",
    "role": "Marketing Manager"
  },
  "goals": ["Streamline workflows", "Reduce manual tasks"],
  "pain_points": ["Slow reporting", "Tool fragmentation"]
}
```

### Markdown

```bash
persona generate --input data.csv --output-format markdown
```

Human-readable format for documentation:

```markdown
# Sarah Chen
## The Efficiency Seeker

### Demographics
- Age: 30-35
- Role: Marketing Manager

### Goals
- Streamline workflows
- Reduce manual tasks
```

### YAML

```bash
persona generate --input data.csv --output-format yaml
```

Good for configuration files and human editing.

## Output Location

```bash
# Default: ./outputs/<timestamp>/
persona generate --input data.csv

# Custom directory
persona generate --input data.csv --output ./my-personas

# Single file output (all personas in one file)
persona generate --input data.csv --output ./personas.json --single-file
```

## Advanced Options

### Cost Estimation

Before generating, estimate costs:

```bash
persona estimate --input data.csv --count 5 --provider anthropic
```

### Dry Run

See what would be generated without calling the LLM:

```bash
persona generate --input data.csv --dry-run
```

### Verbose Output

Get detailed progress information:

```bash
persona generate --input data.csv --verbose
```

### Streaming Output

See personas as they're generated:

```bash
persona generate --input data.csv --stream
```

## Workflows

### Workflow 1: Research to Personas

```bash
# 1. Preview your data
persona data preview ./interviews.csv

# 2. Estimate cost
persona estimate --input ./interviews.csv --count 5

# 3. Generate personas
persona generate --input ./interviews.csv --count 5

# 4. Review output
ls ./outputs/latest/
cat ./outputs/latest/persona-001.json
```

### Workflow 2: Sensitive Data

```bash
# 1. Scan for PII
persona privacy scan --input ./sensitive-data.csv

# 2. Generate with anonymisation
persona generate \
    --input ./sensitive-data.csv \
    --anonymise \
    --provider ollama \
    --model llama3:8b

# 3. Review for any remaining sensitive content
```

### Workflow 3: Batch Processing

```bash
# Process multiple data files
persona generate \
    --input ./data/ \
    --count 3 \
    --output ./all-personas
```

## Troubleshooting

### "No data found in file"

**Cause**: File is empty or in unexpected format.

**Solution**: Use `persona data preview` to inspect the file structure.

### "Rate limit exceeded"

**Cause**: Too many requests to LLM provider.

**Solution**: Wait and retry, or reduce batch size.

### "Invalid persona structure"

**Cause**: LLM response didn't match expected format.

**Solution**: Try a different model or adjust complexity level.

### "Budget exceeded"

**Cause**: Generation would exceed configured budget.

**Solution**: Reduce persona count or adjust budget in configuration.

## Best Practices

1. **Start small**: Generate 1-2 personas first to verify quality
2. **Review output**: Always review generated personas before sharing
3. **Iterate**: Adjust prompts and data based on output quality
4. **Document provenance**: Record which data produced which personas
5. **Version control**: Track persona versions as you refine

---

## Related Documentation

- [Preparing Data](preparing-data.md) - Data format details
- [Choosing a Provider](choosing-provider.md) - Provider comparison
- [Privacy Setup](privacy-setup.md) - PII detection and anonymisation
- [Conversation Scripts](conversation-scripts.md) - Turn personas into LLM scripts
- [Persona Schema Reference](../reference/persona-schema.md) - Output format specification

---

**Next Steps**:
- Try generating your first persona
- Explore different providers and models
- Learn about privacy options for sensitive data
