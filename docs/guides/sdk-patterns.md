# Common SDK Patterns

This guide covers common patterns and best practices when using the Persona SDK.

## Pattern 1: Cost Estimation Before Generation

Always estimate costs before running generation, especially with large datasets:

```python
from persona import PersonaGenerator, PersonaConfig

# Create generator
generator = PersonaGenerator(provider="anthropic")

# Estimate cost first
estimate = generator.estimate_cost("./data/", count=5)
print(f"Estimated cost: ${estimate.total_cost:.4f}")
print(f"Input tokens: {estimate.input_tokens}")
print(f"Output tokens: {estimate.output_tokens}")

# Proceed only if within budget
if estimate.total_cost < 1.00:
    config = PersonaConfig(count=5)
    result = generator.generate("./data/", config=config)
else:
    print("Cost exceeds budget, consider reducing count or using cheaper model")
```

## Pattern 2: Working with Multiple Providers

Compare results across different providers:

```python
from persona import PersonaGenerator, ProviderError

providers = ["anthropic", "openai", "gemini"]
results = {}

for provider in providers:
    try:
        generator = PersonaGenerator(provider=provider)
        results[provider] = generator.generate("./data/")
        print(f"{provider}: Generated {len(results[provider].personas)} personas")
    except ProviderError as e:
        print(f"{provider}: Failed - {e}")
```

## Pattern 3: Batch Processing Multiple Data Sources

Process multiple data directories:

```python
from pathlib import Path
from persona import PersonaGenerator, PersonaConfig

generator = PersonaGenerator(provider="anthropic")
all_personas = []

# Process each data source
config = PersonaConfig(count=2)
data_dirs = Path("./research/").glob("*/")
for data_dir in data_dirs:
    if data_dir.is_dir():
        print(f"Processing: {data_dir.name}")
        result = generator.generate(str(data_dir), config=config)
        all_personas.extend(result.personas)

print(f"Total personas: {len(all_personas)}")
```

## Pattern 4: Export Results

Export generated personas to various formats:

```python
from persona import PersonaGenerator

generator = PersonaGenerator(provider="anthropic")
result = generator.generate("./interviews/")

# Export to different formats
result.to_json("output/")           # JSON files
result.to_markdown("output/")       # Markdown files
result.to_csv("output/personas.csv") # CSV file
```

## Pattern 5: Complexity Levels

Use different complexity levels based on needs:

```python
from persona import PersonaGenerator, PersonaConfig

generator = PersonaGenerator(provider="anthropic")

# Quick generation for prototyping
simple_config = PersonaConfig(
    count=3,
    complexity="simple",      # Fast, less detailed
    detail_level="minimal"
)
simple = generator.generate("./data/", config=simple_config)

# Standard generation for most use cases
standard_config = PersonaConfig(
    count=3,
    complexity="moderate",    # Balanced
    detail_level="standard"
)
standard = generator.generate("./data/", config=standard_config)

# Detailed generation for production
detailed_config = PersonaConfig(
    count=3,
    complexity="complex",     # Thorough analysis
    detail_level="detailed"   # Rich output
)
detailed = generator.generate("./data/", config=detailed_config)
```

## Pattern 6: Preserving Generation Context

Keep track of generation metadata:

```python
from persona import PersonaGenerator, PersonaConfig
import json
from datetime import datetime

generator = PersonaGenerator(provider="anthropic", model="claude-sonnet-4-5-20250929")
config = PersonaConfig(count=5)
result = generator.generate("./data/", config=config)

# Save with full context
output = {
    "generated_at": result.generated_at.isoformat(),
    "config": {
        "provider": result.provider,
        "model": result.model,
        "input_tokens": result.token_usage.input_tokens,
        "output_tokens": result.token_usage.output_tokens,
    },
    "source_files": result.source_files,
    "personas": [p.model_dump() for p in result.personas],
}

with open("output/generation_record.json", "w") as f:
    json.dump(output, f, indent=2, default=str)
```

## Pattern 7: Retry with Exponential Backoff

Handle transient API failures:

```python
import time
from persona import PersonaGenerator, PersonaConfig, ProviderError, RateLimitError

def generate_with_retry(data_path, count=3, max_retries=3):
    generator = PersonaGenerator(provider="anthropic")
    config = PersonaConfig(count=count)

    for attempt in range(max_retries):
        try:
            return generator.generate(data_path, config=config)
        except RateLimitError as e:
            wait_time = e.retry_after or (2 ** attempt)
            if attempt < max_retries - 1:
                print(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
        except ProviderError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1, 2, 4 seconds
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

result = generate_with_retry("./data/", count=5)
```

## Pattern 8: Async Generation

Use async generation for non-blocking operations:

```python
import asyncio
from persona import AsyncPersonaGenerator, PersonaConfig

async def generate_personas():
    generator = AsyncPersonaGenerator(provider="anthropic")
    config = PersonaConfig(count=5)
    result = await generator.agenerate("./data/", config=config)
    return result

# Run async
result = asyncio.run(generate_personas())
print(f"Generated {len(result.personas)} personas")
```

---

## Related Documentation

- [SDK Quickstart](../tutorials/sdk-quickstart.md)
- [Error Handling Guide](./error-handling.md)
- [API Reference](../reference/api.md)
