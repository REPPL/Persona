# How Persona Generation Works

A detailed explanation of the data flow from input to persona output.

## Overview

Persona transforms qualitative research data into structured personas through a multi-stage pipeline. Understanding this process helps you optimise inputs and interpret outputs.

## The Generation Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  1. Load    │────▶│ 2. Prepare  │────▶│ 3. Prompt   │
│    Data     │     │    Data     │     │ Construction│
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  6. Save    │◀────│  5. Parse   │◀────│  4. LLM     │
│   Output    │     │   Response  │     │   Request   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Stage 1: Data Loading

### What Happens

The data loader reads files from your experiment's data directory:

```
experiments/my-experiment/data/
├── interviews.csv
├── survey-results.json
└── field-notes.md
```

### Processing

1. **File discovery** - Find all supported files
2. **Format detection** - Identify file type
3. **Content extraction** - Read and parse content
4. **Validation** - Check for errors

### Output

Combined text with file separators:

```
=== FILE: interviews.csv (CSV, 15 rows) ===
[CSV content converted to readable format]

=== FILE: survey-results.json (JSON, 89 entries) ===
[JSON content flattened to readable format]

=== FILE: field-notes.md (Markdown) ===
[Markdown content as-is]
```

## Stage 2: Data Preparation

### What Happens

Raw data is normalised and optimised for LLM processing.

### Processing

1. **Encoding normalisation** - Convert to UTF-8
2. **Format standardisation** - Consistent structure
3. **Token counting** - Estimate API cost
4. **Chunking** (if needed) - Split large datasets

### Token Counting

```
Token Estimation:
  interviews.csv:    1,200 tokens
  survey-results.json: 800 tokens
  field-notes.md:      500 tokens
  ─────────────────────────────
  Total:             2,500 tokens
  Estimated cost:    $0.08
```

## Stage 3: Prompt Construction

### What Happens

The template engine constructs the final prompt.

### Template Resolution

1. Check experiment config for overrides
2. Check user templates
3. Fall back to system template
4. Merge all layers

### Prompt Structure

```
┌─────────────────────────────────────────┐
│ SYSTEM PROMPT                           │
│ Instructions for the LLM about its role │
│ and how to generate personas            │
└─────────────────────────────────────────┘
                    +
┌─────────────────────────────────────────┐
│ USER PROMPT                             │
│ - Research data (from Stage 1-2)        │
│ - Persona count                         │
│ - Specific requirements                 │
│ - Output format instructions            │
└─────────────────────────────────────────┘
```

### Example Constructed Prompt

```
SYSTEM: You are an expert UX researcher skilled at synthesising
qualitative data into representative user personas. Create personas
that are specific, actionable, and grounded in the provided data.

USER: Based on the following research data, generate 3 distinct
user personas.

## Research Data

=== FILE: interviews.csv ===
[data content]

=== FILE: field-notes.md ===
[data content]

## Requirements
- Each persona must be clearly distinct
- Include demographics, goals, pain points
- Provide representative quotes from the data
- Output as valid JSON following the schema below

## Output Schema
{
  "personas": [
    {
      "name": "string",
      "title": "string",
      ...
    }
  ]
}
```

## Stage 4: LLM Request

### What Happens

The prompt is sent to the configured LLM provider.

### Request Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│ Persona  │────▶│   Provider   │────▶│   LLM API    │
│   CLI    │     │   Adapter    │     │  (OpenAI,    │
│          │◀────│              │◀────│   Claude,    │
│          │     │              │     │   Gemini)    │
└──────────┘     └──────────────┘     └──────────────┘
```

### Provider Configuration

```python
# Internal request configuration
request = {
    "provider": "anthropic",
    "model": "claude-3-sonnet",
    "temperature": 0.7,
    "max_tokens": 4096,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
}
```

### Streaming

Response streams back incrementally, displayed in terminal:

```
Generating personas...

╭─────────────────────────────────────────────────╮
│ Generating persona 1 of 3...                    │
│ ████████████████████░░░░░░░░░░░░░░░░░░░░░ 52%   │
╰─────────────────────────────────────────────────╯
```

## Stage 5: Response Parsing

### What Happens

The LLM's response is parsed into structured data.

### Structured Output

Persona uses structured output (via Instructor library) to ensure valid JSON:

```python
# Response is validated against schema
class Persona(BaseModel):
    name: str
    title: str
    demographics: Demographics
    goals: list[str]
    pain_points: list[str]
    behaviours: list[str]
    quotes: list[str]
```

### Validation

1. **Schema validation** - Matches expected structure
2. **Content validation** - Non-empty, reasonable values
3. **Relationship validation** - Personas are distinct

### Error Handling

If parsing fails:

```
Retry 1/3: Response missing required field 'demographics'
Retry 2/3: Success
```

## Stage 6: Output Saving

### What Happens

Validated personas are saved in multiple formats.

### Output Structure

```
outputs/20241215_143022/
├── metadata.json        # Generation details
├── prompt.json          # Constructed prompt
├── files.txt            # Source file list
├── full_output.txt      # Raw LLM response
└── personas/
    ├── 01/
    │   ├── persona.json    # Structured data
    │   └── persona.md      # Human-readable
    ├── 02/
    │   └── ...
    └── 03/
        └── ...
```

### Metadata Contents

```json
{
  "experiment": "my-experiment",
  "timestamp": "2024-12-15T14:30:22Z",
  "provider": "anthropic",
  "model": "claude-3-sonnet",
  "template": "default",
  "tokens": {
    "input": 2500,
    "output": 1800,
    "total": 4300
  },
  "cost": {
    "input": 0.0075,
    "output": 0.027,
    "total": 0.0345
  },
  "personas_generated": 3,
  "source_files": [
    "interviews.csv",
    "survey-results.json",
    "field-notes.md"
  ],
  "duration_seconds": 12.5
}
```

## Quality Factors

### What Affects Quality

| Factor | Impact | Optimisation |
|--------|--------|--------------|
| **Data quality** | High | Clean, specific, representative |
| **Data quantity** | Medium | More diverse data = better |
| **Persona count** | Medium | Fewer = more depth each |
| **Model choice** | High | Better models = better output |
| **Template** | Medium | Domain-specific templates help |

### Data Quality Impact

```
Poor data → Generic personas
"Users want things to work well and be easy to use"

Good data → Specific personas
"Marketing managers aged 30-40 check dashboards every
morning before standup, frustrated by multi-step exports"
```

## Performance Characteristics

### Timing

| Stage | Typical Duration |
|-------|-----------------|
| Data loading | < 1 second |
| Preparation | < 1 second |
| Prompt construction | < 0.1 second |
| LLM request | 5-30 seconds |
| Parsing | < 1 second |
| Saving | < 1 second |

**Total:** 10-35 seconds for typical generation

### Cost Factors

| Factor | Cost Impact |
|--------|-------------|
| Input tokens | Proportional to data size |
| Output tokens | Proportional to persona count |
| Model | GPT-4 > Claude > Gemini |

## Error Handling

### Retry Logic

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Request │────▶│  Fail?  │────▶│  Retry  │
│         │     │         │     │  with   │
│         │◀────│  Yes    │◀────│ backoff │
└─────────┘     └─────────┘     └─────────┘
                    │ No
                    ▼
              ┌─────────┐
              │ Success │
              └─────────┘
```

### Handled Errors

- Rate limiting → Exponential backoff
- Timeout → Retry with increased timeout
- Invalid response → Retry with feedback
- Network error → Retry after delay

---

## Related Documentation

- [F-004: Persona Generation](../development/roadmap/features/completed/F-004-persona-generation.md)
- [Template Architecture](template-architecture.md)
- [Reproducibility](reproducibility.md)

