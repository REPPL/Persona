# Advanced Features Guide

This guide covers Persona's advanced commands for power users and researchers.

## Overview

Persona includes many commands beyond the basics. These advanced features enable:

- **Quality Analysis** - Score, evaluate, and validate personas
- **Research Workflows** - Variants, lineage tracking, experiments
- **Data Privacy** - PII detection, anonymisation, synthetic data
- **Infrastructure** - REST API, TUI dashboard, audit trails

## Discovering Hidden Commands

Many advanced commands are hidden from `--help` to keep the interface simple. To see all available commands:

```bash
# Show hidden commands in CLI reference
persona help --all

# Or check specific command help
persona lineage --help
persona variant --help
```

---

## Quality & Validation Commands

### score - Quality Metrics

Calculate quality scores for generated personas.

```bash
persona score ./output/personas.json
persona score ./output/ --metrics completeness,consistency,realism
persona score ./output/personas.json --json > scores.json
```

**Metrics calculated:**
- **Completeness** - Required fields present
- **Consistency** - Internal coherence
- **Realism** - Plausibility of attributes
- **Distinctiveness** - Differentiation from other personas

### evaluate - LLM-as-Judge

Use an LLM to evaluate persona quality.

```bash
persona evaluate ./output/personas.json
persona evaluate ./output/ --model gpt-4o --criteria "realism,usefulness"
```

### academic - Research Metrics

Run academic validation metrics (BERTScore, ROUGE, etc.).

```bash
# Requires: pip install persona[academic]
persona academic ./output/personas.json --source ./data/interviews.csv
persona academic ./output/ --metrics bertscore,rouge --json
```

### faithfulness - Source Grounding

Check that personas accurately reflect source data.

```bash
persona faithfulness ./output/personas.json --source ./data/
persona faithfulness ./output/ --strict --threshold 0.7
```

### fidelity - Prompt Adherence

Score how well personas follow prompt constraints.

```bash
persona fidelity ./output/personas.json --template ./templates/custom.j2
```

### diversity - Lexical Analysis

Analyse lexical diversity across personas.

```bash
persona diversity ./output/personas.json
persona diversity ./output/ --metrics ttr,hapax,yule
```

### bias - Stereotype Detection

Detect bias and stereotypes in generated personas.

```bash
# Requires: pip install persona[bias]
persona bias ./output/personas.json
persona bias ./output/ --categories gender,age,occupation --json
```

### verify - Multi-Model Verification

Verify personas using multiple LLM models.

```bash
persona verify ./output/personas.json --models claude,gpt-4o,gemini
persona verify ./output/ --threshold 0.8
```

---

## Analysis Commands

### compare - Persona Comparison

Compare personas to identify similarities and differences.

```bash
persona compare ./output/personas.json
persona compare ./output/run1/ ./output/run2/ --diff
```

### cluster - Consolidation

Cluster personas and suggest consolidation opportunities.

```bash
persona cluster ./output/personas.json --algorithm kmeans --n 3
persona cluster ./output/ --visualise
```

### refine - Interactive Refinement

Interactively refine personas with natural language.

```bash
persona refine ./output/persona_001.json
persona refine ./output/ --instructions "make more technical"
```

---

## Research Workflow Commands

### Experiment Management

```bash
# Create experiment with defaults
persona experiment create "my-study" \
  --description "Q1 User Research" \
  --provider anthropic \
  --count 5

# List experiments
persona experiment list

# Show experiment details
persona experiment show my-study

# View run history
persona experiment history my-study
persona experiment runs my-study

# Record a manual run
persona experiment record-run my-study \
  --provider anthropic \
  --model claude-sonnet-4-20250514 \
  --personas 5 \
  --cost 0.15

# Manage data sources
persona experiment sources my-study
```

### Variant Management

Variants let you compare different parameter configurations.

```bash
# Create variants for A/B testing
persona variant create my-study baseline \
  --param temperature=0.7 \
  --param top_p=0.9

persona variant create my-study creative \
  --param temperature=0.95 \
  --param top_p=0.95 \
  --description "High creativity settings"

# List variants
persona variant list my-study

# Compare variants
persona variant compare my-study baseline creative

# Update variant
persona variant update my-study creative --param temperature=0.9

# Delete variant
persona variant delete my-study creative
```

### Lineage Tracking

Track data provenance through the pipeline.

```bash
# List tracked entities
persona lineage list
persona lineage list --type persona

# Show entity details
persona lineage show ent-abc123

# Trace ancestry
persona lineage trace ent-abc123 --direction up
persona lineage trace ent-abc123 --direction both --depth 5

# Verify integrity
persona lineage verify ent-abc123
persona lineage verify ent-abc123 --chain  # Verify entire chain

# Export lineage
persona lineage export --output lineage.json
persona lineage export ent-abc123 -o entity-lineage.json

# List agents and activities
persona lineage agents
persona lineage activities --type llm_generation
```

---

## Data & Privacy Commands

### privacy scan - PII Detection

Scan data for personally identifiable information.

```bash
# Requires: pip install persona[privacy]
persona privacy scan ./data/interviews.csv
persona privacy scan ./data/ --entities email,phone,ssn
```

### privacy anonymise - Data Anonymisation

Anonymise PII in data files.

```bash
persona privacy anonymise ./data/interviews.csv --output ./data/anon/
persona privacy anonymise ./data/ --strategy redact
persona privacy anonymise ./data/ --strategy replace --locale en_GB
```

**Strategies:**
- `redact` - Replace with [REDACTED]
- `replace` - Replace with fake data
- `hash` - Replace with hash values

### synthesise - Synthetic Data Generation

Generate synthetic research data for testing.

```bash
persona synthesise --type interviews --count 20 --output ./data/synthetic/
persona synthesise --type survey --count 100 --schema ./schema.json
```

---

## Infrastructure Commands

### serve - REST API Server

Start a REST API server for programmatic access.

```bash
persona serve --port 8000
persona serve --host 0.0.0.0 --port 8080 --workers 4
persona serve --auth-token secret123 --reload
```

See the [REST API Reference](rest-api.md) for full API documentation.

### dashboard - TUI Dashboard

Launch the terminal user interface dashboard.

```bash
persona dashboard
persona dashboard --experiment my-study
```

### audit - Audit Trail

View and export audit records.

```bash
persona audit list
persona audit list --type generation --limit 50
persona audit show audit-abc123
persona audit export --output audit.json
```

---

## Configuration Discovery

### vendor & model Discovery

```bash
# List available vendors
persona vendor list
persona vendor discover  # Find configured vendors

# List models
persona model list
persona model list --provider anthropic
persona model discover  # Find available models
```

### template & workflow Discovery

```bash
# List templates
persona template list

# List workflows
persona workflow list

# List plugins
persona plugin list
```

### script Generation

```bash
# Generate conversation scripts
persona script generate ./output/persona_001.json --scenarios 5
```

---

## Command Cheatsheet

| Task | Command |
|------|---------|
| Score quality | `persona score ./output/` |
| Detect bias | `persona bias ./output/` |
| Compare runs | `persona compare ./run1/ ./run2/` |
| Create variant | `persona variant create exp-1 test --param temp=0.9` |
| Trace lineage | `persona lineage trace ent-123 --direction up` |
| Scan for PII | `persona privacy scan ./data/` |
| Start API | `persona serve --port 8000` |
| View audit | `persona audit list` |

---

## Related Documentation

- [CLI Reference](../reference/cli-reference.md) - Complete command documentation
- [REST API Reference](rest-api.md) - HTTP API documentation
- [Deployment Guide](deployment.md) - Server and container deployment
- [Privacy Setup](privacy-setup.md) - PII detection configuration
