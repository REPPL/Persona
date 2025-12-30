# R-028: Model Fine-Tuning Integration

## Executive Summary

This research analyses approaches for integrating fine-tuned models and custom adapters into Persona's generation pipeline. Fine-tuning enables domain-specific persona generation with improved quality and consistency. Recommended approach: implement adapter support through OpenAI fine-tuning API, Anthropic fine-tuning (when available), and local LoRA/QLoRA adapters for Ollama models.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-028 |
| **Category** | Advanced Capabilities |
| **Status** | Complete |
| **Priority** | P2 |
| **Informs** | Future fine-tuning features, Custom model support |

---

## Problem Statement

Generic LLMs produce good personas but lack:
- Domain-specific vocabulary and concepts
- Consistent formatting and structure
- Organisation-specific persona attributes
- Industry-specific behavioural patterns

Fine-tuned models can address these gaps, but integrating them requires:
- Support for multiple fine-tuning approaches
- Adapter management and versioning
- Training data preparation
- Quality comparison tooling

---

## State of the Art Analysis

### Fine-Tuning Approaches

#### 1. Full Fine-Tuning

Train all model parameters on domain data.

| Aspect | Assessment |
|--------|------------|
| Quality | ✅ Best results |
| Cost | ❌ Very expensive |
| Flexibility | ❌ Requires model hosting |
| Accessibility | ❌ Enterprise only |

**Use Case:** Large organisations with dedicated ML infrastructure.

#### 2. Parameter-Efficient Fine-Tuning (PEFT)

Train small adapter layers, keep base model frozen.

**LoRA (Low-Rank Adaptation):**
```python
# Conceptual example
class LoRALayer:
    def __init__(self, original_layer, rank: int = 8):
        self.original = original_layer
        self.lora_A = nn.Linear(original_layer.in_features, rank, bias=False)
        self.lora_B = nn.Linear(rank, original_layer.out_features, bias=False)

    def forward(self, x):
        return self.original(x) + self.lora_B(self.lora_A(x))
```

| Aspect | Assessment |
|--------|------------|
| Quality | ✅ Near full fine-tuning quality |
| Cost | ✅ Much lower than full |
| Flexibility | ✅ Swap adapters easily |
| Accessibility | ⚠️ Requires local GPU |

#### 3. API-Based Fine-Tuning

Use provider's fine-tuning APIs.

**OpenAI Fine-Tuning:**
```bash
# Prepare training data
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}

# Create fine-tuning job
openai api fine_tuning.jobs.create \
  -m gpt-4o-mini \
  -t training_file.jsonl
```

| Aspect | Assessment |
|--------|------------|
| Quality | ✅ Good results |
| Cost | ⚠️ Training + inference costs |
| Flexibility | ⚠️ Provider-dependent |
| Accessibility | ✅ No infrastructure needed |

#### 4. Prompt Tuning

Learn soft prompts instead of model parameters.

| Aspect | Assessment |
|--------|------------|
| Quality | ⚠️ Limited improvement |
| Cost | ✅ Very low |
| Flexibility | ✅ Easy to switch |
| Accessibility | ✅ Works with any model |

### Provider Fine-Tuning Support

| Provider | Method | Models | Status |
|----------|--------|--------|--------|
| OpenAI | API fine-tuning | GPT-4o-mini, GPT-4o | ✅ Available |
| Anthropic | Custom models | Claude | 🔄 Enterprise only |
| Google | Vertex AI | Gemini | ✅ Available |
| Ollama | LoRA adapters | Llama, Mistral, etc. | ✅ Available |

### Local Fine-Tuning Options

#### Ollama with Adapters

```bash
# Create model with LoRA adapter
ollama create persona-tuned -f ./Modelfile

# Modelfile contents:
FROM llama3.2:8b
ADAPTER ./persona-lora.gguf
PARAMETER temperature 0.7
SYSTEM "You are a persona generation expert..."
```

#### Unsloth for Training

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3.2-8b-bnb-4bit",
    max_seq_length=4096,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16,
    lora_dropout=0,
)

# Train on persona data...
```

---

## Training Data Preparation

### Data Format

```json
{
  "conversations": [
    {
      "input": {
        "source_data": "Interview transcript about healthcare preferences...",
        "instructions": "Generate a detailed persona for a healthcare app user"
      },
      "output": {
        "persona": {
          "name": "Sarah Chen",
          "demographics": {...},
          "behaviours": [...],
          "needs": [...]
        }
      }
    }
  ]
}
```

### Data Quality Requirements

| Requirement | Description |
|-------------|-------------|
| **Volume** | 100-1000 high-quality examples |
| **Diversity** | Cover all persona types and domains |
| **Consistency** | Uniform format and quality |
| **Validation** | Human-reviewed for accuracy |

### Data Augmentation

```python
class PersonaDataAugmenter:
    def augment(self, example: dict) -> list[dict]:
        augmented = [example]

        # Rephrase source data
        augmented.append(self.rephrase_source(example))

        # Vary persona attributes
        augmented.extend(self.vary_attributes(example))

        # Add noise for robustness
        augmented.append(self.add_noise(example))

        return augmented
```

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Fine-Tuning Integration                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Training   │───▶│   Adapter    │───▶│  Generation  │  │
│  │   Pipeline   │    │   Registry   │    │   Pipeline   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │    Data      │    │   Adapter    │    │   Quality    │  │
│  │  Preparation │    │   Storage    │    │  Comparison  │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Adapter Registry

```python
@dataclass
class AdapterMetadata:
    name: str
    version: str
    base_model: str
    provider: str  # openai, ollama, etc.
    domain: str  # healthcare, fintech, etc.
    training_date: datetime
    metrics: dict[str, float]

class AdapterRegistry:
    def register(self, adapter: AdapterMetadata, path: Path) -> None:
        """Register an adapter for use."""

    def get(self, name: str, version: str | None = None) -> Adapter:
        """Get an adapter by name and optional version."""

    def list(self, domain: str | None = None) -> list[AdapterMetadata]:
        """List available adapters."""

    def compare(self, adapters: list[str], test_data: Path) -> ComparisonReport:
        """Compare adapter quality on test data."""
```

---

## Evaluation Matrix

| Approach | Quality | Cost | Complexity | Portability |
|----------|---------|------|------------|-------------|
| OpenAI fine-tuning | ✅ | ⚠️ | ✅ | ❌ |
| Ollama + LoRA | ⚠️ | ✅ | ⚠️ | ✅ |
| Full fine-tuning | ✅ | ❌ | ❌ | ⚠️ |
| Prompt tuning | ⚠️ | ✅ | ✅ | ✅ |

---

## Recommendation

### Primary: Multi-Provider Adapter Support

Support adapters across providers with unified interface.

### CLI Commands

```bash
# Data preparation
persona finetune prepare ./training-data/ --output ./prepared.jsonl

# Training (provider-specific)
persona finetune train --provider openai --data ./prepared.jsonl --name healthcare-v1

# Local training with Ollama
persona finetune train --provider ollama --base llama3.2:8b --data ./prepared.jsonl

# Register existing adapter
persona finetune register ./my-adapter.gguf --name healthcare-v1

# List adapters
persona finetune list

# Use adapter
persona generate --adapter healthcare-v1 --from ./data/

# Compare adapters
persona finetune compare healthcare-v1 healthcare-v2 --test-data ./test.jsonl
```

### Configuration

```yaml
finetuning:
  data:
    format: jsonl
    validation_split: 0.1
    min_examples: 100

  openai:
    model: gpt-4o-mini
    epochs: 3
    batch_size: auto

  ollama:
    base_model: llama3.2:8b
    lora_rank: 16
    lora_alpha: 16

  adapters:
    directory: ~/.persona/adapters
    registry: ~/.persona/adapter-registry.json
```

### Provider Abstraction

```python
class FineTuningProvider(Protocol):
    def prepare_data(self, data: list[dict]) -> Path:
        """Prepare data in provider format."""

    def train(self, data_path: Path, config: TrainingConfig) -> AdapterMetadata:
        """Train adapter and return metadata."""

    def load_adapter(self, name: str) -> Adapter:
        """Load trained adapter."""

class OpenAIFineTuning(FineTuningProvider):
    async def train(self, data_path: Path, config: TrainingConfig) -> AdapterMetadata:
        # Upload training file
        file = await self.client.files.create(
            file=open(data_path, "rb"),
            purpose="fine-tune"
        )

        # Create fine-tuning job
        job = await self.client.fine_tuning.jobs.create(
            training_file=file.id,
            model=config.base_model,
            hyperparameters={"n_epochs": config.epochs}
        )

        # Wait for completion
        while job.status not in ["succeeded", "failed"]:
            await asyncio.sleep(60)
            job = await self.client.fine_tuning.jobs.retrieve(job.id)

        return AdapterMetadata(
            name=config.name,
            version="1.0",
            base_model=config.base_model,
            provider="openai",
            model_id=job.fine_tuned_model
        )
```

---

## Implementation Priority

1. **Data preparation pipeline** - Format training data
2. **OpenAI fine-tuning integration** - API-based training
3. **Adapter registry** - Track and manage adapters
4. **Ollama LoRA support** - Local adapter loading
5. **Quality comparison tooling** - Evaluate adapters

---

## References

1. [OpenAI Fine-Tuning Guide](https://platform.openai.com/docs/guides/fine-tuning)
2. [LoRA: Low-Rank Adaptation](https://arxiv.org/abs/2106.09685)
3. [QLoRA Paper](https://arxiv.org/abs/2305.14314)
4. [Unsloth](https://github.com/unslothai/unsloth)
5. [Ollama Modelfile](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)

---

## Related Documentation

- [F-112: Native Ollama Provider](../roadmap/features/completed/F-112-native-ollama-provider.md)
- [ADR-0025: Ollama Provider Integration](../decisions/adrs/ADR-0025-ollama-provider-integration.md)
- [R-013: Local Model Assessment](R-013-local-model-assessment.md)

---

**Status**: Complete
