# ADR-0025: Ollama Provider Integration

## Status

Accepted

## Context

Persona v1.3.0 needed local LLM support for:
- Privacy-preserving generation (data never leaves machine)
- Cost elimination (no API charges)
- Offline operation (air-gapped environments)
- Development and testing (fast iteration without API costs)

The integration needed to:
- Work with the existing multi-provider architecture
- Support Apple Silicon (Metal) acceleration
- Enable model discovery and management
- Provide comparable quality to cloud providers

## Decision

Implement a **native Ollama provider** as a built-in provider class:

### Architecture

```python
class OllamaProvider(LLMProvider):
    """Native Ollama provider for local LLM inference."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3:70b",
        timeout: int = 120,
    ):
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        response = await self.client.post(
            "/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
        )
        return self._parse_response(response.json())
```

### Model Registry

```python
class OllamaModelRegistry:
    """Discover and manage Ollama models."""

    RECOMMENDED_MODELS = {
        "high_quality": "qwen2.5:72b",
        "balanced": "llama3:70b",
        "fast": "mistral:7b",
        "minimal": "llama3.2:3b",
    }

    async def list_models(self) -> list[OllamaModel]:
        """List available local models."""
        response = await self.client.get("/api/tags")
        return [OllamaModel.from_api(m) for m in response.json()["models"]]

    async def pull_model(self, name: str) -> None:
        """Pull a model from Ollama registry."""
        async for progress in self._stream_pull(name):
            yield progress
```

### CLI Integration

```bash
# Generate with Ollama
persona generate --from data/ --provider ollama --model llama3:70b

# List local models
persona models --provider ollama

# Check Ollama status
persona check --provider ollama
```

## Consequences

**Positive:**
- Zero API costs for generation
- Data never leaves local machine
- Works offline after model download
- Apple Silicon optimised (Metal acceleration)
- Supports all Ollama-compatible models

**Negative:**
- Requires Ollama installation
- Large model downloads (GB-scale)
- Slower than cloud APIs (depending on hardware)
- Quality varies by model size/architecture
- Hardware requirements for larger models

## Alternatives Considered

### LiteLLM Ollama Passthrough

**Description:** Use LiteLLM's Ollama support.
**Pros:** Consistent with other providers, already integrated.
**Cons:** Additional abstraction layer, less control over Ollama-specific features.
**Why Not Chosen:** Native integration allows better model management and feature access.

### llama.cpp Direct

**Description:** Use llama.cpp Python bindings directly.
**Pros:** Lowest-level access, maximum control.
**Cons:** Complex setup, no model management, platform-specific builds.
**Why Not Chosen:** Ollama provides better UX and cross-platform support.

### vLLM

**Description:** Use vLLM for local inference.
**Pros:** Highest throughput, production-grade.
**Cons:** More complex setup, CUDA-focused, less Mac support.
**Why Not Chosen:** Ollama better for single-user CLI tool, especially on Mac.

### Custom Vendor Configuration

**Description:** Configure Ollama as custom vendor via YAML.
**Pros:** No code changes, already supported.
**Cons:** No model discovery, no Ollama-specific features, manual setup.
**Why Not Chosen:** First-class support provides better experience.

## Research Reference

See [R-013: Local Model Assessment](../../research/R-013-local-model-assessment.md) for comprehensive local LLM analysis.

## Implementation Details

### Model Quality Tiers

| Tier | Model | RAM Required | Quality |
|------|-------|--------------|---------|
| **Premium** | qwen2.5:72b | 48GB+ | 95% of frontier |
| **Standard** | llama3:70b | 42GB+ | 90% of frontier |
| **Efficient** | mistral:7b | 5GB+ | 75% of frontier |
| **Minimal** | llama3.2:3b | 4GB+ | 65% of frontier |

### Hardware Detection

```python
def get_optimal_model() -> str:
    """Select optimal model based on available RAM."""
    available_ram = get_available_ram_gb()
    if available_ram >= 48:
        return "qwen2.5:72b"
    elif available_ram >= 32:
        return "llama3:70b"
    elif available_ram >= 8:
        return "mistral:7b"
    else:
        return "llama3.2:3b"
```

### Hybrid Pipeline Support

The Ollama provider enables the hybrid pipeline (F-116):

```python
# Local draft, frontier refinement
persona generate --hybrid \
    --local-model llama3:70b \
    --frontier-provider anthropic \
    --frontier-model claude-sonnet-4-20250514
```

---

## Related Documentation

- [F-112: Native Ollama Provider](../../roadmap/features/completed/F-112-native-ollama-provider.md)
- [F-116: Hybrid Local/Frontier Pipeline](../../roadmap/features/completed/F-116-hybrid-local-frontier-pipeline.md)
- [R-013: Local Model Assessment](../../research/R-013-local-model-assessment.md)
- [Ollama Documentation](https://ollama.com/docs)
