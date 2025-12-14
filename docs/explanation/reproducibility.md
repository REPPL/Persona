# Experiment Reproducibility

Understanding how to achieve consistent, reproducible persona generation.

## Overview

Reproducibility is essential for research credibility. Persona captures all parameters needed to recreate identical experiments, with caveats for inherent LLM variability.

## What's Captured

Every generation records complete metadata:

```json
{
  "experiment": {
    "name": "q4-research",
    "version": "1.0"
  },
  "generation": {
    "timestamp": "2024-12-15T14:30:22Z",
    "persona_version": "0.1.0"
  },
  "provider": {
    "name": "anthropic",
    "model": "claude-3-sonnet-20241022",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 4096,
      "top_p": 1.0
    }
  },
  "template": {
    "name": "default",
    "version": "1.0.0",
    "hash": "sha256:abc123..."
  },
  "data": {
    "files": [
      {
        "path": "interviews.csv",
        "hash": "sha256:def456...",
        "tokens": 1200
      }
    ],
    "total_tokens": 2500
  },
  "output": {
    "personas_generated": 3,
    "tokens_used": 1800,
    "cost": 0.0345
  }
}
```

## Achieving Identical Re-runs

### Perfect Reproducibility

To achieve identical output:

1. **Same data** - File hashes must match
2. **Same template** - Including version
3. **Same model** - Exact model version (e.g., `claude-3-sonnet-20241022`)
4. **Same parameters** - Temperature, max_tokens, etc.
5. **Temperature = 0** - Eliminates randomness

```bash
# Force deterministic output
persona generate \
  --from my-experiment \
  --temperature 0 \
  --seed 42  # If provider supports
```

### Near-Reproducibility

With default settings (temperature > 0):

- Structure will be consistent
- Specific wording may vary
- Overall themes preserved
- Suitable for most use cases

## Temperature and Randomness

### How Temperature Affects Output

| Temperature | Behaviour | Use Case |
|-------------|-----------|----------|
| 0.0 | Deterministic | Research, validation |
| 0.3-0.5 | Low variation | Consistent quality |
| 0.7 | Balanced (default) | General use |
| 1.0+ | High variation | Exploration |

### Example Comparison

**Temperature 0:**
```
Run 1: "Sarah Chen, 32, Marketing Manager"
Run 2: "Sarah Chen, 32, Marketing Manager"  # Identical
```

**Temperature 0.7:**
```
Run 1: "Sarah Chen, 32, Marketing Manager"
Run 2: "Sarah C., early 30s, Marketing Lead"  # Similar but varied
```

## Versioning Experiments

### Experiment Versioning

Track changes to your experiment over time:

```yaml
# experiments/my-experiment/config.yaml
name: my-experiment
version: "2.1"  # Increment when parameters change

history:
  - version: "1.0"
    date: "2024-11-01"
    changes: "Initial experiment"
  - version: "2.0"
    date: "2024-12-01"
    changes: "Added interview round 2"
  - version: "2.1"
    date: "2024-12-15"
    changes: "Increased persona count to 5"
```

### Git Integration

```bash
# Track experiment changes
git add experiments/my-experiment/
git commit -m "Experiment v2.1: increase persona count"

# Tag specific versions
git tag -a "experiment/my-experiment/v2.1" -m "5 personas from rounds 1-2"
```

## Re-running Experiments

### From Metadata

```bash
# Re-run using saved metadata
persona generate --replay outputs/20241215_143022/

# This restores:
# - Same provider/model
# - Same template
# - Same parameters
# - Same data files
```

### Verification

```bash
# Compare outputs
persona compare \
  outputs/20241215_143022/personas/ \
  outputs/20241216_091500/personas/

# Output:
# Similarity: 98% (with temperature=0)
# Similarity: 85% (with temperature=0.7)
```

## Provider-Specific Notes

### OpenAI

- Model versions change over time
- Use exact version strings (e.g., `gpt-4-0125-preview`)
- Seed parameter available for reproducibility

```bash
persona generate --model gpt-4-0125-preview --seed 42
```

### Anthropic

- Model versions are date-stamped
- Temperature 0 is most consistent
- No seed parameter currently

```bash
persona generate --model claude-3-sonnet-20241022 --temperature 0
```

### Google

- Model versions evolve
- Specify exact version when possible
- Some inherent variability

## Sharing Experiments

### Export for Sharing

```bash
# Export complete experiment bundle
persona experiment export my-experiment \
  --include-data \
  --include-outputs \
  --output my-experiment-bundle.tar.gz
```

Bundle includes:
- `config.yaml` - All settings
- `data/` - Source files
- `outputs/` - Generated outputs
- `metadata/` - Full generation details

### Import Shared Experiment

```bash
# Import on another machine
persona experiment import my-experiment-bundle.tar.gz

# Reproduce
persona generate --replay experiments/my-experiment/outputs/latest/
```

## Documentation for Replication

### Research Paper Format

When publishing research using Persona:

```markdown
## Methodology

Personas were generated using Persona v0.1.0 with the following
configuration:

| Parameter | Value |
|-----------|-------|
| Provider | Anthropic |
| Model | claude-3-sonnet-20241022 |
| Temperature | 0.7 |
| Persona count | 3 |
| Template | default (v1.0.0) |

Input data comprised 15 interview transcripts (n=15 participants)
totalling approximately 2,500 tokens.

Full experiment metadata and outputs are available at:
[DOI/repository link]
```

### Replication Package

For academic reproducibility:

```
replication-package/
├── README.md           # Replication instructions
├── requirements.txt    # Persona version
├── experiments/
│   └── study/
│       ├── config.yaml
│       └── data/       # Anonymised
├── outputs/            # Generated personas
└── analysis/           # Analysis scripts
```

## Handling Changes

### When Providers Update Models

```bash
# Check for model changes
persona check --providers

# Pin specific version
persona config set provider.anthropic.model "claude-3-sonnet-20241022"
```

### When Templates Change

```bash
# Lock template version
persona config set templates.default.version "1.0.0"

# Or copy template locally
persona template copy default my-locked-default
```

### When Data Changes

1. New data should create new experiment version
2. Document changes in experiment history
3. Compare outputs to track impact

```bash
# Compare before/after data change
persona compare \
  --before outputs/v1/personas/ \
  --after outputs/v2/personas/ \
  --report data-impact.md
```

## Best Practices

### Do

- Record all parameters in metadata
- Use version control for experiments
- Document changes between versions
- Use temperature 0 for research validation
- Share complete replication packages

### Don't

- Assume outputs will be identical without temperature 0
- Rely on latest model versions for reproducibility
- Discard metadata after generation
- Skip documentation for informal experiments

---

## Related Documentation

- [How Generation Works](how-generation-works.md)
- [T-05: Building a Library](../tutorials/05-building-library.md)
- [F-006: Experiment Management](../development/roadmap/features/completed/F-006-experiment-management.md)

