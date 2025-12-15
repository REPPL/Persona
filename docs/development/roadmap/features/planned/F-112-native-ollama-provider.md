# F-112: Native Ollama Provider

## Overview

| Attribute | Value |
|-----------|-------|
| **Research** | R-013 |
| **Milestone** | v1.3.0 |
| **Priority** | P0 |
| **Category** | Provider |

## Problem Statement

Persona currently supports cloud-based LLM providers (OpenAI, Anthropic, Google) but lacks native support for local model inference. While Ollama is documented in `provider-apis.md`, no `OllamaProvider` class exists in the codebase. Users requiring privacy-preserving workflows, offline operation, or cost-free generation cannot use Persona without manual configuration.

Local model support is the foundation for all privacy-sensitive use cases:
- Enterprises with GDPR/HIPAA compliance requirements
- Air-gapped environments (government, defence)
- Cost-sensitive bulk generation workflows

## Design Approach

- Native `OllamaProvider` class extending `LLMProvider` ABC
- Auto-detection of available models from running Ollama instance
- Hardware-aware model recommendations based on system resources
- Graceful fallback when Ollama is not running
- OpenAI-compatible request/response format

### Provider Interface

```python
from persona.core.providers import OllamaProvider

# Basic usage
provider = OllamaProvider()
response = provider.generate("Create a persona based on...")

# Custom configuration
provider = OllamaProvider(
    base_url="http://localhost:11434",
    model="qwen2.5:72b",
    timeout=300  # Longer timeout for large models
)

# Auto-detect available models
models = provider.list_available_models()
```

### Model Detection

```python
# Query Ollama API for running models
GET http://localhost:11434/api/tags

# Response includes model metadata
{
    "models": [
        {"name": "llama3:70b", "size": 39000000000, ...},
        {"name": "mistral:7b", "size": 4100000000, ...}
    ]
}
```

### CLI Integration

```bash
# Generate with Ollama
persona generate --input data.csv --provider ollama --model llama3:8b

# List available local models
persona models --provider ollama

# Use default local model (auto-selected based on hardware)
persona generate --input data.csv --provider ollama
```

## Implementation Tasks

- [ ] Create `src/persona/core/providers/ollama.py`
- [ ] Implement `OllamaProvider` class extending `LLMProvider`
- [ ] Add model auto-detection via `/api/tags` endpoint
- [ ] Implement connection health check
- [ ] Add to `ProviderFactory.BUILTIN_PROVIDERS`
- [ ] Update `src/persona/core/providers/__init__.py` exports
- [ ] Add hardware-aware default model selection
- [ ] Implement graceful error handling (Ollama not running)
- [ ] Create `tests/unit/core/providers/test_ollama.py`
- [ ] Create integration tests (requires Ollama running)
- [ ] Update `docs/reference/provider-apis.md`
- [ ] Add CLI `--provider ollama` documentation

## Success Criteria

- [ ] `persona generate --provider ollama --model llama3:8b` works
- [ ] Auto-detects available models from running Ollama instance
- [ ] Graceful error message when Ollama not running
- [ ] Sensible default model selected based on available models
- [ ] Unit test coverage >= 90%
- [ ] Integration tests pass with local Ollama

## Technical Details

### Supported Models (Initial)

| Model | Parameters | Context | Notes |
|-------|------------|---------|-------|
| `llama3:70b` | 70B | 8K | High quality |
| `llama3:8b` | 8B | 8K | Fast, lightweight |
| `llama3.2:3b` | 3B | 128K | Long context |
| `qwen2.5:72b` | 72B | 128K | Excellent quality |
| `qwen2.5:7b` | 7B | 128K | Good balance |
| `mistral:7b` | 7B | 32K | Strong performance |
| `mixtral:8x7b` | 47B | 32K | MoE architecture |

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat` | POST | Generate chat completions |
| `/api/tags` | GET | List available models |
| `/api/show` | POST | Get model details |

### Request Format

```json
{
    "model": "llama3:70b",
    "messages": [
        {"role": "system", "content": "You are a UX researcher..."},
        {"role": "user", "content": "Generate personas from: ..."}
    ],
    "stream": false,
    "options": {
        "temperature": 0.7,
        "num_predict": 8192
    }
}
```

## Dependencies

- None (HTTP API, no additional Python packages)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Ollama not installed | Clear error message with install instructions |
| Model not pulled | Suggest `ollama pull <model>` command |
| Insufficient RAM | Recommend smaller model |
| Slow generation | Document expected speeds, add timeout config |

---

## Related Documentation

- [R-013: Local Model Assessment](../../research/R-013-local-model-assessment.md)
- [Provider APIs Reference](../../../reference/provider-apis.md)
- [F-002: LLM Provider Abstraction](../completed/F-002-llm-provider-abstraction.md)
