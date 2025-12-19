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

---

## Related Documentation

- [SDK Quickstart](../tutorials/sdk-quickstart.md)
- [SDK Patterns Guide](../guides/sdk-patterns.md)
- [Error Codes Reference](./error-codes.md)
- [Character Card Schema](./character-card-schema.md)
- [Conversation Scripts Guide](../guides/conversation-scripts.md)
