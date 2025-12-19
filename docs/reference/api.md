# API Reference

This page provides auto-generated API documentation for the Persona SDK.

## SDK Module

The main SDK module provides the high-level interface for persona generation.

### Main Classes

::: persona.sdk.generator.PersonaGenerator
    options:
      show_root_heading: true
      members:
        - generate
        - estimate_cost

::: persona.sdk.async_generator.AsyncPersonaGenerator
    options:
      show_root_heading: true
      members:
        - agenerate

### Configuration Models

::: persona.sdk.models.PersonaConfig
    options:
      show_root_heading: true

::: persona.sdk.models.ExperimentConfig
    options:
      show_root_heading: true

### Result Models

::: persona.sdk.models.PersonaModel
    options:
      show_root_heading: true

::: persona.sdk.models.GenerationResultModel
    options:
      show_root_heading: true

### Experiment SDK

::: persona.sdk.experiment.ExperimentSDK
    options:
      show_root_heading: true

::: persona.sdk.async_experiment.AsyncExperimentSDK
    options:
      show_root_heading: true

## Core Modules

### Generation Pipeline

::: persona.core.generation.pipeline
    options:
      show_root_heading: true
      members:
        - GenerationPipeline
        - GenerationConfig
        - GenerationResult

### Persona Parser

::: persona.core.generation.parser
    options:
      show_root_heading: true
      members:
        - PersonaParser
        - Persona
        - ParseResult

### Data Loading

::: persona.core.data
    options:
      show_root_heading: true
      members:
        - DataLoader

### Cost Estimation

::: persona.core.cost
    options:
      show_root_heading: true
      members:
        - CostEstimator
        - CostEstimate
        - PricingData

### Platform Utilities

::: persona.core.platform
    options:
      show_root_heading: true
      members:
        - PathManager
        - get_config_dir
        - get_data_dir
        - IS_WINDOWS
        - IS_MACOS
        - IS_LINUX

## Provider Modules

### Base Provider

::: persona.core.providers.base
    options:
      show_root_heading: true
      members:
        - LLMProvider
        - LLMResponse

### Anthropic Provider

::: persona.core.providers.anthropic
    options:
      show_root_heading: true
      members:
        - AnthropicProvider

### OpenAI Provider

::: persona.core.providers.openai
    options:
      show_root_heading: true
      members:
        - OpenAIProvider

### Gemini Provider

::: persona.core.providers.gemini
    options:
      show_root_heading: true
      members:
        - GeminiProvider

## Discovery Module

### Model Discovery

::: persona.core.discovery
    options:
      show_root_heading: true
      members:
        - ModelDiscovery
        - VendorDiscovery
        - ModelChecker

### Ollama Model Comparison

Compare tested Ollama models with available models from a running Ollama instance.

::: persona.core.discovery.ollama_models
    options:
      show_root_heading: true
      members:
        - compare_ollama_models
        - get_untested_models
        - OllamaModelRegistry
        - ModelComparisonResult

**Example usage:**

```python
from persona.core.discovery import compare_ollama_models, get_untested_models

# Check for new untested models (prints alert if found)
result = compare_ollama_models()
if result.has_untested_models:
    print(f"New models to test: {result.untested_models}")

# Get just the list of untested models
untested = get_untested_models()
```

## Exception Types

::: persona.sdk.exceptions
    options:
      show_root_heading: true
      members:
        - PersonaError
        - ConfigurationError
        - ValidationError
        - DataError
        - ProviderError
        - RateLimitError
        - BudgetExceededError
        - GenerationError

## Scripts API

### Script Generator

::: persona.core.scripts.generator.ScriptGenerator
    options:
      show_root_heading: true
      members:
        - generate
        - batch_generate

### Character Card Models

::: persona.core.scripts.models.CharacterCard
    options:
      show_root_heading: true

::: persona.core.scripts.models.Identity
    options:
      show_root_heading: true

::: persona.core.scripts.models.PsychologicalProfile
    options:
      show_root_heading: true

::: persona.core.scripts.models.CommunicationStyle
    options:
      show_root_heading: true

::: persona.core.scripts.models.KnowledgeBoundaries
    options:
      show_root_heading: true

### Privacy Audit

::: persona.core.scripts.privacy.PrivacyAuditor
    options:
      show_root_heading: true
      members:
        - audit
        - check_leakage

## Utility Modules

### JSON Extraction

Unified JSON parsing from LLM responses with markdown code block handling.

::: persona.core.utils.json_extractor
    options:
      show_root_heading: true
      members:
        - JSONExtractor
        - extract_json
        - extract_json_objects

**Example usage:**

```python
from persona.core.utils.json_extractor import JSONExtractor

extractor = JSONExtractor()

# Extract JSON from markdown code blocks
text = '```json\n{"name": "Alice"}\n```'
result = extractor.extract(text)
print(result)  # {"name": "Alice"}

# Extract multiple JSON objects
text = '{"a": 1} some text {"b": 2}'
objects = extractor.extract_all(text)
print(objects)  # [{"a": 1}, {"b": 2}]
```

### Async Helpers

Standardised sync/async wrappers with proper error handling.

::: persona.core.utils.async_helpers
    options:
      show_root_heading: true
      members:
        - run_sync
        - is_async_context
        - to_thread

**Example usage:**

```python
from persona.core.utils.async_helpers import run_sync, is_async_context

# Run async function synchronously
async def async_task():
    return "result"

result = run_sync(async_task())

# Check if currently in async context
if is_async_context():
    result = await async_task()
else:
    result = run_sync(async_task())
```

## Type Definitions

### Persona TypedDict

Type-safe persona data structures using TypedDict.

::: persona.core.types.persona
    options:
      show_root_heading: true
      members:
        - PersonaDict
        - PersonaIdentityDict
        - PersonaDemographicsDict
        - PersonaBehaviourDict
        - PersonaPreferencesDict

**Example usage:**

```python
from persona.core.types.persona import PersonaDict, PersonaIdentityDict

# Type-safe persona creation
identity: PersonaIdentityDict = {
    "name": "Alice Smith",
    "age": 32,
    "occupation": "Software Engineer"
}

persona: PersonaDict = {
    "identity": identity,
    "demographics": {...},
    "behaviour": {...},
    "preferences": {...}
}
```

## HTTP Infrastructure

### HTTP Base Provider

Shared connection pooling for all HTTP-based providers.

::: persona.core.providers.http_base
    options:
      show_root_heading: true
      members:
        - HTTPProvider
        - ConnectionPool
        - HTTPConfig

**Example usage:**

```python
from persona.core.providers.http_base import HTTPProvider

class MyProvider(HTTPProvider):
    def __init__(self):
        super().__init__(
            base_url="https://api.example.com",
            max_connections=10,
            timeout=30.0
        )

    async def make_request(self, endpoint: str, data: dict):
        return await self._post(endpoint, json=data)
```

## Pipeline Abstractions

### Pipeline Stage Base

Abstract base class for composable pipeline stages.

::: persona.core.hybrid.stages.base
    options:
      show_root_heading: true
      members:
        - PipelineStage
        - StageConfig
        - StageResult

**Example usage:**

```python
from persona.core.hybrid.stages.base import PipelineStage, StageResult

class CustomStage(PipelineStage):
    async def execute(self, input_data: list) -> StageResult:
        # Process input data
        processed = [self.transform(item) for item in input_data]
        return StageResult(
            output=processed,
            metrics={"items_processed": len(processed)}
        )
```

## Quality Module

### Metric Registry

Registry pattern for quality metrics with plugin support.

::: persona.core.quality.registry
    options:
      show_root_heading: true
      members:
        - MetricRegistry
        - register_metric
        - get_metric

**Example usage:**

```python
from persona.core.quality.registry import MetricRegistry, register_metric

# Register a custom metric
@register_metric("custom_score")
class CustomMetric:
    def calculate(self, persona: dict) -> float:
        # Custom scoring logic
        return 0.95

# Use the registry
registry = MetricRegistry()
metric = registry.get("custom_score")
score = metric.calculate(persona)
```

---

## Related Documentation

- [SDK Quickstart](../tutorials/sdk-quickstart.md)
- [SDK Patterns Guide](../guides/sdk-patterns.md)
- [Error Codes Reference](./error-codes.md)
- [Character Card Schema](./character-card-schema.md)
- [Conversation Scripts Guide](../guides/conversation-scripts.md)
