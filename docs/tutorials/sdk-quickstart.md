# SDK Quickstart

Get started with the Persona Python SDK in 5 minutes.

## Installation

```bash
pip install persona
```

## Basic Usage

```python
from persona import PersonaGenerator, PersonaConfig

# Create a generator
generator = PersonaGenerator(provider="anthropic")

# Generate personas from interview data
result = generator.generate("./interviews/")

# Access the generated personas
for persona in result.personas:
    print(f"Name: {persona.name}")
    print(f"Title: {persona.title}")
    print(f"Goals: {persona.goals}")
    print("---")
```

## Complete Example

Here's a more complete example showing common options:

```python
from persona import PersonaGenerator, PersonaConfig

# Create generator with specific model
generator = PersonaGenerator(
    provider="anthropic",
    model="claude-sonnet-4-5-20250929"
)

# Estimate cost before generating
estimate = generator.estimate_cost("./interviews/", count=5)
print(f"Estimated cost: ${estimate.total_cost:.4f}")

# Generate with configuration
config = PersonaConfig(
    count=5,
    complexity="complex",       # simple, moderate, complex
    detail_level="detailed",    # minimal, standard, detailed
    include_reasoning=True      # Include LLM's reasoning
)

result = generator.generate("./interviews/", config=config)

# Access results
print(f"Generated {len(result.personas)} personas")
print(f"Input tokens: {result.token_usage.input_tokens}")
print(f"Output tokens: {result.token_usage.output_tokens}")

# Export to JSON
result.to_json("output/")
```

## Supported Providers

| Provider | Environment Variable | Models |
|----------|---------------------|--------|
| Anthropic | `ANTHROPIC_API_KEY` | claude-sonnet-4-5-20250929, claude-opus-4-5-20251101 |
| OpenAI | `OPENAI_API_KEY` | gpt-4o, gpt-4-turbo |
| Google | `GOOGLE_API_KEY` | gemini-1.5-pro, gemini-1.5-flash |

## Data Formats

The SDK accepts various data formats:

```python
# Single CSV file
result = generator.generate("./data/surveys.csv")

# Directory of markdown interviews
result = generator.generate("./interviews/")

# JSON data
result = generator.generate("./data/responses.json")
```

## Error Handling

```python
from persona import PersonaGenerator, PersonaError, ProviderError, DataError

generator = PersonaGenerator(provider="anthropic")

try:
    result = generator.generate("./data/")
except ProviderError as e:
    print(f"API error: {e}")
except DataError as e:
    print(f"Data error: {e}")
except PersonaError as e:
    print(f"Persona error: {e}")
```

## Next Steps

- [SDK Patterns Guide](../guides/sdk-patterns.md) - Common usage patterns
- [Error Handling Guide](../guides/error-handling.md) - Handling errors gracefully
- [API Reference](../reference/api.md) - Complete API documentation
- [Preparing Data](../guides/preparing-data.md) - Data format guidelines

---

## Related Documentation

- [Getting Started Tutorial](./01-getting-started.md)
- [CLI Reference](../reference/cli-reference.md)
