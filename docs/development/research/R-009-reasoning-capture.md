# R-009: Reasoning Capture

Research into LLM chain-of-thought and decision trace logging for reproducibility and auditability.

## Executive Summary

Research reproducibility requires complete transparency into LLM decision-making. Users cannot currently see why a persona was generated with specific attributes, debug differences between runs, audit reasoning for stakeholder review, or reproduce experiments with full context.

This research surveys the state of the art in LLM observability, from industry platforms (LangSmith, Arize Phoenix, Langfuse) to academic research on chain-of-thought (CoT) evaluation. The recommendation is to implement reasoning capture as **default behaviour** with three capture layers: request, response, and reasoning extraction.

**Key Finding:** PersonaZero already implemented reasoning capture using delimiter tags, demonstrating its value for the persona generation use case.

**Recommendation:** Implement comprehensive reasoning capture in v0.1.0 as default behaviour (not optional), storing request payloads, raw responses, and extracted reasoning traces alongside generated personas.

---

## Current State of the Art

### Industry Landscape

The LLM observability ecosystem has matured significantly in 2024-2025:

| Platform | Approach | Key Features | Open Source |
|----------|----------|--------------|-------------|
| **[LangSmith](https://docs.smith.langchain.com/observability/concepts)** | Trace hierarchy | Runs, spans, parent-child | No |
| **[Arize Phoenix](https://github.com/Arize-ai/phoenix)** | OpenTelemetry-based | Agent tracing, drift detection | Yes |
| **[Langfuse](https://langfuse.com/docs/tracing)** | Structured traces | Prompt versioning, JSON export | Yes |
| **[OpenLLMetry](https://github.com/traceloop/openllmetry)** | OTel extensions | Vendor-agnostic, standard spans | Yes |
| **[Weights & Biases Weave](https://wandb.ai/site/weave)** | ML lifecycle | Multi-agent tracking | No |

### OpenTelemetry GenAI Semantic Conventions

The [OpenTelemetry GenAI Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) (v1.37+) define a standard schema for LLM telemetry:

**Signal Types:**
- **Events**: Input/output content capture
- **Metrics**: Token usage, latency, time-to-first-token
- **Model Spans**: LLM invocation details
- **Agent Spans**: Multi-step reasoning workflows

**Key Attributes:**
```
gen_ai.request.model        # Model identifier
gen_ai.request.temperature  # Sampling temperature
gen_ai.usage.input_tokens   # Tokens consumed
gen_ai.usage.output_tokens  # Tokens generated
gen_ai.response.finish_reason  # Why generation stopped
gen_ai.operation.name       # chat, completion, embedding
```

### Chain-of-Thought (CoT) Research

Academic research on CoT reasoning capture reveals important considerations:

**Key Findings:**
- **[Evaluating Step-by-step Reasoning Traces (arXiv 2502.12289)](https://arxiv.org/abs/2502.12289)**: Surveys evaluation methods for reasoning traces
- **[Semi-structured LLM Reasoners Can Be Rigorously Audited (2505.24217)](https://arxiv.org/abs/2505.24217)**: Proposes structured auditing of reasoning traces
- **Faithfulness Problem**: Anthropic research shows CoT traces may not represent actual model reasoning
- **SSRM Format**: Semi-Structured Reasoning Models use Pythonic syntax for auditable traces

**Implementation Methods:**
1. **Zero-shot CoT**: "Let's think step by step" prompting
2. **Structured CoT**: Explicit step templates in prompts
3. **Multimodal CoT**: Cross-modal reasoning chains
4. **Self-Consistency**: Generate multiple traces, select most consistent

### Existing Open Source Implementations

**LangSmith Tracing Model:**
```python
# Hierarchical trace structure
Trace
├── Run (LLM call)
│   ├── input: {...}
│   ├── output: {...}
│   ├── metadata: {tokens, latency, model}
│   └── children: [Run, Run, ...]
└── Run (Tool call)
    └── ...
```

**Arize Phoenix (OpenTelemetry-based):**
```python
# Span-based tracing with OTel
with tracer.start_as_current_span("persona_generation") as span:
    span.set_attribute("gen_ai.request.model", "claude-3-sonnet")
    span.set_attribute("gen_ai.usage.input_tokens", 1500)
    # ... generation logic
    span.add_event("reasoning_step", {"step": 1, "content": "..."})
```

**Langfuse Structured Traces:**
```python
# JSON-exportable trace structure
trace = {
    "id": "trace-123",
    "name": "chain_of_thought_example",
    "observations": [
        {"type": "generation", "input": {...}, "output": {...}},
        {"type": "span", "name": "reasoning_step", "metadata": {...}}
    ]
}
```

### PersonaZero's Reasoning Capture Pattern

From the PersonaZero CLAUDE.md, the project implemented:

> "A reasoning capture feature saves step-by-step LLM reasoning in separate markdown files using delimiter tags."

**Implementation:**
- Reasoning saved alongside generation outputs
- Uses delimiter tags to parse reasoning from response
- Stored in markdown for human readability
- Integrated with multi-step workflow (extract → consolidate → validate)

---

## Gap Analysis: Current Persona State

Based on codebase exploration, Persona has:

**What Exists:**
- ✓ ADR-0011: Multi-step workflow with intermediate results
- ✓ ADR-0008: Structured JSON output
- ✓ ADR-0009: Timestamped output organisation
- ✓ F-073 to F-078: Logging infrastructure (planned for v0.9.0)
- ✓ Experiment metadata capture in config.yaml

**Critical Gaps:**
- ✗ No LLM response debugging output
- ✗ No chain-of-thought extraction/logging
- ✗ No intermediate step capture for multi-step workflows
- ✗ No OpenTelemetry integration
- ✗ No structured reasoning trace format
- ✗ No debug/verbose CLI flag for reasoning visibility

---

## Alternatives Analysis

### Approach 1: Optional Debug Flag Only

**Description:** Add `--debug` flag that enables reasoning capture when needed.

| Aspect | Assessment |
|--------|------------|
| **Simplicity** | High |
| **Storage** | Minimal (only when enabled) |
| **Reproducibility** | Low (users forget to enable) |
| **Research Value** | Limited |

**Verdict:** Rejected. Reproducibility should be default, not optional.

### Approach 2: Full OpenTelemetry Integration

**Description:** Implement complete OpenTelemetry spans with GenAI conventions.

| Aspect | Assessment |
|--------|------------|
| **Standards Compliance** | Excellent |
| **Interoperability** | High (integrates with observability stack) |
| **Complexity** | High (significant dependency) |
| **v0.1.0 Feasibility** | Low |

**Verdict:** Deferred to v0.3.0. Too complex for initial release.

### Approach 3: Database Storage (SQLite)

**Description:** Store reasoning traces in local SQLite database.

| Aspect | Assessment |
|--------|------------|
| **Queryability** | Excellent |
| **Portability** | Medium (binary files) |
| **Git Friendliness** | Poor |
| **Simplicity** | Medium |

**Verdict:** Rejected for v0.1.0. Files are simpler and more portable.

### Approach 4: File-Based Capture (Recommended)

**Description:** Store reasoning as JSON/Markdown files alongside outputs.

| Aspect | Assessment |
|--------|------------|
| **Simplicity** | High |
| **Portability** | Excellent (plain text) |
| **Git Friendliness** | Excellent |
| **Human Readability** | Excellent (Markdown traces) |
| **Machine Readability** | Good (JSON for metrics) |

**Verdict:** Recommended for v0.1.0. Simple, portable, fits existing output structure.

---

## Recommendation

### Three-Layer Reasoning Capture

Implement as **default behaviour** (not optional) in v0.1.0:

**1. Request Layer**: Capture what was sent
- Final prompt (after template rendering)
- Model parameters (temperature, max_tokens)
- Provider/model identification

**2. Response Layer**: Capture what was received
- Raw LLM response (before parsing)
- Finish reason
- Token usage (input/output/total)
- Latency metrics

**3. Reasoning Layer**: Extract chain-of-thought
- Delimiter-based extraction (if model provides reasoning)
- Step-by-step breakdown
- Confidence indicators (if available)

### Output Structure

```
outputs/20241215_143022/
├── metadata.json           # Generation metadata
├── reasoning/              # NEW: Reasoning capture
│   ├── request.json        # Complete request payload
│   ├── response_raw.json   # Raw LLM response
│   ├── reasoning_trace.md  # Extracted chain-of-thought
│   └── metrics.json        # Token usage, latency, cost
├── personas/
│   └── ...
```

### Reasoning Trace Format

```markdown
# Reasoning Trace: persona-001

## Generation Context
- Model: claude-3-sonnet-20241022
- Temperature: 0.7
- Timestamp: 2024-12-15T14:30:22Z

## Chain of Thought

### Step 1: Data Analysis
Analysing input data from 3 files containing 15 interview transcripts...
Key themes identified: mobile usage (12 mentions), frustration with export (8 mentions)

### Step 2: Segment Identification
Identified 3 distinct user segments based on usage patterns:
1. Power users (technical, daily usage)
2. Casual users (occasional, mobile-first)
3. Administrators (management focus)

### Step 3: Persona Synthesis
Creating persona for segment 1 (Power users):
- Demographic inference: 30-40, technical role based on language patterns
- Primary goal: efficiency (mentioned 15 times across interviews)
- Key pain point: export workflow (8 complaints, consistent theme)

## Confidence Scores
- Demographics: 0.75 (inferred from language, not stated)
- Goals: 0.92 (explicitly stated in multiple interviews)
- Pain points: 0.88 (consistent across participants)
```

### Extraction Strategy

Use delimiter tags in prompts to enable extraction:

```xml
<reasoning>
Step 1: Analysing the data...
Step 2: Identifying patterns...
</reasoning>

<output>
{
  "id": "persona-001",
  ...
}
</output>
```

Provider-specific handling:
- **Claude**: Uses `<thinking>` tags natively
- **OpenAI**: Requires explicit prompt instruction
- **Gemini**: Requires explicit prompt instruction

### CLI Integration

```bash
# Default: reasoning captured automatically
persona generate --from data/

# Enhanced output: show reasoning in terminal
persona generate --from data/ --verbose

# Suppress reasoning files (not recommended)
persona generate --from data/ --no-reasoning
```

---

## Impact on Existing Decisions

### ADR-0020: Reasoning Capture Architecture

This research supports creation of ADR-0020 documenting:
- Three-layer capture architecture
- File-based storage decision
- Delimiter-based extraction strategy
- Default-on behaviour rationale

### ADR-0009: Timestamped Output Organisation

Extends to include `reasoning/` subdirectory in output structure.

### ADR-0011: Multi-Step Workflow

Each step in multi-step workflow produces separate reasoning trace:
- `reasoning/step_01_extract.md`
- `reasoning/step_02_consolidate.md`
- `reasoning/step_03_validate.md`

### F-032: Reasoning Capture

New feature specification for v0.1.0 implementing this research.

---

## Roadmap Placement

### Recommended: v0.1.0 (Foundation)

**Rationale:**
- Reasoning capture is fundamental to reproducibility
- Retrofitting later is harder than building in from start
- Aligns with "research-grade" positioning
- PersonaZero already had this feature

### Feature Timeline

| Version | Reasoning Capture Scope |
|---------|------------------------|
| v0.1.0 | Basic capture (request, response, metrics) |
| v0.1.0 | Reasoning trace extraction (delimiter-based) |
| v0.1.0 | `--verbose` CLI flag |
| v0.2.0 | Multi-step reasoning (per-step traces) |
| v0.3.0 | OpenTelemetry export (optional) |
| v0.9.0 | Integration with F-073 (JSON Lines logger) |

---

## Sources

### Industry Platforms

- LangSmith Observability Concepts. https://docs.smith.langchain.com/observability/concepts
- Arize Phoenix. https://github.com/Arize-ai/phoenix
- Langfuse Tracing. https://langfuse.com/docs/tracing
- OpenLLMetry. https://github.com/traceloop/openllmetry
- Weights & Biases Weave. https://wandb.ai/site/weave

### Standards

- OpenTelemetry GenAI Semantic Conventions. https://opentelemetry.io/docs/specs/semconv/gen-ai/

### Academic Research

- Evaluating Step-by-step Reasoning Traces (arXiv 2502.12289). https://arxiv.org/abs/2502.12289
- Semi-structured LLM Reasoners Can Be Rigorously Audited (arXiv 2505.24217). https://arxiv.org/abs/2505.24217
- IBM: What is Chain of Thought Prompting. https://www.ibm.com/think/topics/chain-of-thoughts

---

## Related Documentation

- [F-032: Reasoning Capture](../roadmap/features/completed/F-032-reasoning-capture.md)
- [ADR-0020: Reasoning Capture Architecture](../decisions/adrs/ADR-0020-reasoning-capture-architecture.md)
- [ADR-0011: Multi-Step Workflow](../decisions/adrs/ADR-0011-multi-step-workflow.md)
- [ADR-0009: Timestamped Output Organisation](../decisions/adrs/ADR-0009-timestamped-output.md)
- [Reproducibility](../../explanation/reproducibility.md)

