# ADR-0026: Hybrid Pipeline Strategy

## Status

Accepted

## Context

Persona v1.5.0 needed to balance cost and quality for persona generation:
- Cloud/frontier models provide highest quality but are expensive
- Local models are free but lower quality
- Many use cases don't require frontier-level quality
- Some personas may need refinement while others are good enough

The solution needed to:
- Reduce costs while maintaining quality
- Be configurable based on user needs
- Support automatic quality assessment
- Enable fully local operation when desired

## Decision

Implement a **hybrid local/frontier pipeline** with configurable quality thresholds:

### Pipeline Architecture

```
Input Data
    ↓
┌─────────────────────────────────────────┐
│ Stage 1: Local Draft Generation         │
│ (Ollama with qwen2.5:7b or similar)     │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Stage 2: Quality Assessment             │
│ (Local scoring metrics)                 │
└─────────────────────────────────────────┘
    ↓ (quality < threshold)
┌─────────────────────────────────────────┐
│ Stage 3: Frontier Refinement            │
│ (Claude/GPT-4 for low-quality drafts)   │
└─────────────────────────────────────────┘
    ↓
Output Personas
```

### Configuration

```yaml
hybrid:
  enabled: true
  local_model: qwen2.5:7b
  frontier_provider: anthropic
  frontier_model: claude-sonnet-4-20250514
  quality_threshold: 0.7  # 0.0-1.0
  max_cost: 5.00  # USD budget
  skip_frontier: false  # Force local-only
```

### CLI Integration

```bash
# Enable hybrid mode
persona generate --hybrid --from data/

# Configure threshold
persona generate --hybrid --quality-threshold 0.8

# Local-only mode (no frontier)
persona generate --hybrid --no-frontier

# Set budget limit
persona generate --hybrid --max-cost 2.00
```

### Quality Threshold Logic

```python
async def generate_hybrid(
    self,
    data: str,
    count: int,
    threshold: float = 0.7
) -> list[Persona]:
    # Stage 1: Generate drafts with local model
    drafts = await self.local_provider.generate(data, count * 2)

    # Stage 2: Score quality
    scored_drafts = []
    for draft in drafts:
        score = self.quality_scorer.score(draft, data)
        scored_drafts.append((draft, score))

    # Sort by quality
    scored_drafts.sort(key=lambda x: x[1], reverse=True)

    # Stage 3: Refine low-quality drafts if needed
    results = []
    for draft, score in scored_drafts[:count]:
        if score >= threshold:
            results.append(draft)  # Good enough
        else:
            refined = await self.frontier_provider.refine(draft)
            results.append(refined)

    return results
```

## Consequences

**Positive:**
- 50-80% cost reduction for typical workloads
- Quality maintained via selective refinement
- Budget control prevents runaway costs
- Privacy preserved for high-quality local results
- Graceful degradation when frontier unavailable

**Negative:**
- More complex pipeline logic
- Requires local model installation
- Quality assessment adds latency
- May produce inconsistent outputs (mixed sources)

## Alternatives Considered

### Fixed Ratio Split

**Description:** Always use local for X%, frontier for Y%.
**Pros:** Simple, predictable costs.
**Cons:** Ignores quality, may refine already-good or skip bad.
**Why Not Chosen:** Quality-based selection is more efficient.

### Frontier-First with Local Fallback

**Description:** Try frontier first, fall back to local on error/budget.
**Pros:** Prioritises quality.
**Cons:** Doesn't save costs for routine generation.
**Why Not Chosen:** Hybrid approach saves more for typical workloads.

### Separate Commands

**Description:** Different commands for local vs frontier.
**Pros:** Explicit user control.
**Cons:** Doesn't leverage hybrid benefits, manual selection.
**Why Not Chosen:** Unified command with flag is more ergonomic.

### Ensemble Generation

**Description:** Generate with multiple providers, select best.
**Pros:** Highest quality possible.
**Cons:** Multiplies costs, complex selection logic.
**Why Not Chosen:** Too expensive for typical use cases.

## Research Reference

See [R-013: Local Model Assessment](../../research/R-013-local-model-assessment.md) for quality comparison research.

## Implementation Details

### Stage Abstraction

Each stage is a separate, testable unit:

```python
class PipelineStage(ABC):
    @abstractmethod
    async def execute(self, input: StageInput) -> StageOutput: ...

class LocalDraftStage(PipelineStage):
    async def execute(self, input: StageInput) -> StageOutput:
        drafts = await self.provider.generate(input.data, input.count * 2)
        return StageOutput(personas=drafts)

class QualityAssessmentStage(PipelineStage):
    async def execute(self, input: StageInput) -> StageOutput:
        scored = [(p, self.scorer.score(p)) for p in input.personas]
        return StageOutput(scored_personas=scored)

class FrontierRefinementStage(PipelineStage):
    async def execute(self, input: StageInput) -> StageOutput:
        refined = []
        for persona, score in input.scored_personas:
            if score < self.threshold:
                persona = await self.frontier.refine(persona)
            refined.append(persona)
        return StageOutput(personas=refined)
```

### Cost Tracking

```python
class HybridCostTracker:
    def __init__(self, budget: float):
        self.budget = budget
        self.spent = 0.0

    def can_afford(self, estimated_cost: float) -> bool:
        return self.spent + estimated_cost <= self.budget

    def record(self, cost: float) -> None:
        self.spent += cost

    def remaining(self) -> float:
        return self.budget - self.spent
```

### Quality Metrics Used

The hybrid pipeline uses these metrics for threshold comparison:
- Coherence score (internal consistency)
- Faithfulness score (source alignment)
- Completeness score (required fields)

Combined into single 0-1 score for threshold comparison.

---

## Related Documentation

- [F-116: Hybrid Local/Frontier Pipeline](../../roadmap/features/completed/F-116-hybrid-local-frontier-pipeline.md)
- [F-112: Native Ollama Provider](../../roadmap/features/completed/F-112-native-ollama-provider.md)
- [F-106: Quality Metrics Scoring](../../roadmap/features/completed/F-106-quality-metrics.md)
- [R-013: Local Model Assessment](../../research/R-013-local-model-assessment.md)
