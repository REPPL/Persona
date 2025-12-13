# R-001: Structured LLM Output

## Executive Summary

Modern LLM providers now offer native structured output capabilities, but with varying levels of maturity. **Instructor** library (3M+ monthly downloads) provides the most robust cross-provider solution with automatic retries and Pydantic validation. For Persona, we recommend using Instructor as the primary abstraction layer, with fallback to provider-specific structured outputs for maximum reliability.

## Current State of the Art (2025)

### Industry Standards

The industry has converged on **three primary approaches** for structured LLM output:

1. **Native Structured Outputs** - Provider-enforced JSON schema compliance
2. **JSON Mode** - Guaranteed valid JSON without schema enforcement
3. **Tool/Function Calling** - Repurposing function definitions as output templates

**OpenAI** released Structured Outputs API in August 2024, offering server-side schema enforcement via `response_format` parameter. This guarantees 100% schema compliance for supported models.

**Anthropic** announced Structured Outputs in November 2025 (`anthropic-beta: structured-outputs-2025-11-13` header) for Claude Sonnet 4.5 and Opus 4.1. Prior to this, Claude required the "tool call trick" for reliable JSON.

**Google Gemini** supports JSON mode and function calling, with structured output support varying by model version.

### Academic Research

Research indicates that structured output methods can still fail in two ways:
1. Failure to produce a valid structured object
2. Valid JSON that doesn't adhere to the requested data model

Temperature settings significantly impact reliability—lower temperatures (0.2) improve factual precision in extracted data.

### Open Source Ecosystem

| Library | Downloads/Month | Providers | Key Features |
|---------|-----------------|-----------|--------------|
| **Instructor** | 3M+ | 15+ | Pydantic models, auto-retries, streaming |
| **LangChain** | High | Many | Broader framework, structured output support |
| **Outlines** | Growing | Local models | Grammar-based generation |
| **LiteLLM** | High | 100+ | Unified API with JSON mode support |

## Alternatives Analysis

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Instructor** | Cross-provider, Pydantic-native, auto-retries, 3M+ users | Additional dependency | **Recommended** |
| **Native Structured Outputs** | Provider-optimised, no extra dependencies | Provider-specific code paths | Use as backend |
| **JSON Mode** | Simple, widely supported | No schema enforcement | Insufficient for personas |
| **Tool/Function Calling** | Universal fallback | Verbose, inconsistent across providers | Use as fallback |
| **Manual Parsing** | No dependencies | Fragile, high maintenance | Avoid |

## Recommendation

### Primary Approach

Use **Instructor** library as the structured output layer:

```python
import instructor
from pydantic import BaseModel, Field
from typing import List

class Persona(BaseModel):
    """A user persona generated from research data."""
    name: str = Field(description="A realistic name for the persona")
    age: int = Field(ge=18, le=100)
    occupation: str
    goals: List[str] = Field(min_length=1)
    frustrations: List[str] = Field(min_length=1)
    quote: str = Field(description="A characteristic quote from this persona")

# Provider-agnostic client creation
client = instructor.from_provider("openai/gpt-4o")  # or anthropic/claude-3-5-sonnet

personas = client.chat.completions.create(
    response_model=List[Persona],
    messages=[
        {"role": "system", "content": "Generate user personas from research data."},
        {"role": "user", "content": user_data}
    ],
    max_retries=3
)
```

### Rationale

1. **Pydantic Integration** - Persona already uses Pydantic (per pyproject.toml), so Instructor is a natural fit
2. **Multi-Provider Support** - Works with OpenAI, Anthropic, and Gemini (our three target providers)
3. **Automatic Retries** - Handles transient failures without custom retry logic
4. **Type Safety** - Full IDE support with proper type inference
5. **Production-Proven** - 3M+ monthly downloads, active maintenance

### Implementation Notes

1. **Schema Design** - Keep Pydantic models in dedicated `src/persona/core/schemas/` directory
2. **Validation** - Use Pydantic validators for business rules (e.g., persona count ranges)
3. **Error Handling** - Instructor raises `InstructorRetryException` after max retries
4. **Streaming** - Instructor supports streaming partial responses for progress feedback

**Temperature Recommendation:** Use `temperature=0.7` for creative persona generation, but `temperature=0.2` for data extraction tasks.

## Impact on Existing Decisions

### ADR Updates Required

**ADR-0008 (Structured JSON Output)** should be updated to:
- Add "Alternatives Considered" section documenting Instructor, native APIs, and manual parsing
- Reference this research note
- Confirm Instructor as implementation approach

### Feature Spec Updates

**F-004 (Persona Generation)** should specify:
- Instructor as the structured output library
- Pydantic schema for persona model
- Retry configuration (default: 3 attempts)

**F-005 (Output Formatting)** should specify:
- JSON output derived from Pydantic model serialisation
- Markdown output via custom formatter (not Instructor)

## Sources

- [Instructor Library Documentation](https://python.useinstructor.com/)
- [Anthropic Structured Outputs Announcement](https://towardsdatascience.com/hands-on-with-anthropics-new-structured-output-capabilities/)
- [LiteLLM JSON Mode Documentation](https://docs.litellm.ai/docs/completion/json_mode)
- [Structured Output Comparison (OpenAI, Gemini, Anthropic)](https://medium.com/@rosgluk/structured-output-comparison-across-popular-llm-providers-openai-gemini-anthropic-mistral-and-1a5d42fa612a)
- [Enforcing JSON Outputs in Commercial LLMs](https://datachain.ai/blog/enforcing-json-outputs-in-commercial-llms)

---

## Related Documentation

- [ADR-0008: Structured JSON Output](../decisions/adrs/ADR-0008-structured-json-output.md)
- [F-004: Persona Generation](../roadmap/features/planned/F-004-persona-generation.md)
- [F-005: Output Formatting](../roadmap/features/planned/F-005-output-formatting.md)
