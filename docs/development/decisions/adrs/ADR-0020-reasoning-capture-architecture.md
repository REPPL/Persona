# ADR-0020: Reasoning Capture Architecture

## Status

Accepted

## Context

Persona aims to be research-grade software where every output is reproducible and auditable. Academic research (Shin et al. DIS 2024) emphasises the importance of transparency in AI-generated personas. Current implementation lacks systematic capture of LLM reasoning.

PersonaZero demonstrated the value of reasoning capture with delimiter-based extraction stored in markdown files. Users need to:
- Understand why specific persona attributes were generated
- Debug differences between runs
- Audit reasoning for stakeholder presentations
- Reproduce experiments with full context

## Decision

Implement comprehensive reasoning capture as **default behaviour** (not optional) with file-based storage.

### Capture Points

```
Input Data → [Capture: request.json]
     ↓
Template Render → [Capture: prompt in request.json]
     ↓
LLM Request → [Capture: api parameters]
     ↓
LLM Response → [Capture: response_raw.json]
     ↓
Reasoning Extract → [Capture: reasoning_trace.md]
     ↓
Output Parse → [Capture: personas/*.json]
     ↓
Metrics Calculate → [Capture: metrics.json]
```

### Storage Format

- **JSON** for machine-readable data (request, response, metrics)
- **Markdown** for human-readable reasoning traces
- All stored in `outputs/{timestamp}/reasoning/` directory

### Extraction Strategy

Use delimiter tags in prompts:

```xml
<reasoning>
Step 1: Analysing the input data...
Step 2: Identifying user segments...
</reasoning>

<output>
{"id": "persona-001", ...}
</output>
```

Provider-specific handling:
- **Claude**: Uses native `<thinking>` tags
- **OpenAI**: Requires explicit prompt instruction for `<reasoning>` tags
- **Gemini**: Requires explicit prompt instruction for `<reasoning>` tags

Fall back to full response if no delimiters present.

### Multi-Step Integration

Each step in multi-step workflow produces separate reasoning trace:
- `reasoning/step_01_extract.md`
- `reasoning/step_02_consolidate.md`
- `reasoning/step_03_validate.md`

Final trace aggregates all steps.

## Consequences

**Positive:**
- Complete audit trail for every generation
- Research reproducibility guaranteed
- Debugging becomes straightforward
- Stakeholder transparency enabled
- Aligns with industry best practices (OpenTelemetry, LangSmith patterns)

**Negative:**
- Increased storage requirements (~10-50KB per generation)
- Slight performance overhead for file writes
- Prompts must include reasoning delimiters for extraction

## Alternatives Considered

### Optional Reasoning Capture (--debug flag only)
- Rejected: Reproducibility should be default, not optional
- Users forget to enable, lose audit trail

### OpenTelemetry Integration Only
- Deferred to v0.3.0: Adds dependency complexity for v0.1.0
- Can add OTel export as enhancement later

### Database Storage (SQLite)
- Rejected: Files are simpler, portable, git-friendly
- Can add database option later for enterprise use

---

## Related Documentation

- [R-009: Reasoning Capture](../../research/R-009-reasoning-capture.md)
- [F-032: Reasoning Capture](../../roadmap/features/planned/F-032-reasoning-capture.md)
- [ADR-0011: Multi-Step Workflow](ADR-0011-multi-step-workflow.md)
- [ADR-0009: Timestamped Output Organisation](ADR-0009-timestamped-output-organisation.md)

