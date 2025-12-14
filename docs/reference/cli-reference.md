# CLI Reference

Complete command-line interface documentation for Persona.

## Quick Reference Card

```
persona generate    Generate personas from data
persona check       Verify installation and configuration
persona demo        Try with sample data
persona help        Show help for any command
```

## Command Groups

### Core Commands

Always visible, primary functionality.

| Command | Description |
|---------|-------------|
| `generate` | Generate personas from data |
| `check` | Verify installation |
| `demo` | Try with sample data |
| `help` | Show help |
| `version` | Show version |

### Experiment Commands

Manage experiments and projects.

| Command | Description |
|---------|-------------|
| `experiment create` | Create new experiment |
| `experiment list` | List all experiments |
| `experiment show` | Show experiment details |
| `experiment delete` | Delete experiment |
| `experiment export` | Export experiment |

### Persona Commands

Work with generated personas.

| Command | Description |
|---------|-------------|
| `persona list` | List generated personas |
| `persona show` | Display persona details |
| `persona validate` | Validate against source |
| `persona compare` | Compare personas |
| `persona export` | Export to external format |
| `persona refine` | Interactively refine |

### Data Commands

Work with source data.

| Command | Description |
|---------|-------------|
| `data preview` | Preview data before processing |
| `data formats` | Show supported formats |
| `data validate` | Validate data quality |

### Configuration Commands

Manage configuration.

| Command | Description |
|---------|-------------|
| `config show` | Show current configuration |
| `config set` | Set configuration value |
| `config provider` | Manage LLM providers |
| `config template` | Manage prompt templates |

---

## Core Commands

### generate

Generate personas from research data.

```bash
persona generate [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--from`, `-f` | PATH | Required | Data source (file or folder) |
| `--output`, `-o` | PATH | Auto | Output directory |
| `--count`, `-n` | INT | 3 | Number of personas |
| `--provider` | STRING | Config | LLM provider |
| `--model` | STRING | Config | Model name |
| `--template` | STRING | default | Prompt template |
| `--temperature` | FLOAT | 0.7 | Generation temperature |
| `--format` | STRING | json | Output format |
| `--no-confirm` | FLAG | False | Skip confirmation |
| `--dry-run` | FLAG | False | Preview without generating |

**Examples:**

```bash
# Basic generation
persona generate --from experiments/my-experiment/data/

# Specify provider and count
persona generate -f data/ -n 5 --provider anthropic --model claude-3-sonnet

# Batch processing
persona generate --from ./interviews/ --batch

# Dry run (preview only)
persona generate -f data/ --dry-run
```

### check

Verify installation and configuration.

```bash
persona check [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--verbose`, `-v` | FLAG | Show detailed output |
| `--providers` | FLAG | Check all providers |
| `--fix` | FLAG | Attempt to fix issues |

**Example output:**

```
System Check
───────────────────────────────────
Python      ✓ 3.12.1
Config      ✓ Valid
Storage     ✓ 2.1 GB available

Providers
───────────────────────────────────
OpenAI      ✓ API key configured
            Models: gpt-4o, gpt-4-turbo
Anthropic   ✓ API key configured
            Models: claude-3-opus, claude-3-sonnet

Templates
───────────────────────────────────
System      ✓ 5 templates available
User        ✓ 2 custom templates
```

### demo

Try Persona with sample data.

```bash
persona demo [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--domain` | STRING | general | Demo domain |
| `--provider` | STRING | Config | LLM provider |
| `--clean` | FLAG | False | Remove demo data after |

**Available domains:**
- `general` - General user research
- `saas` - SaaS product personas
- `ecommerce` - E-commerce customers
- `healthcare` - Healthcare users

**Example:**

```bash
persona demo --domain saas --provider anthropic
```

---

## Experiment Commands

### experiment create

Create a new experiment.

```bash
persona experiment create [NAME] [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--description`, `-d` | STRING | Experiment description |
| `--provider` | STRING | Default provider |
| `--model` | STRING | Default model |
| `--template` | STRING | Default template |
| `--count` | INT | Default persona count |

**Example:**

```bash
persona experiment create "Q4 Research" \
  --description "Customer interviews Q4 2024" \
  --provider anthropic \
  --model claude-3-sonnet \
  --count 5
```

### experiment list

List all experiments.

```bash
persona experiment list [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--format` | STRING | Output format (table/json) |
| `--all` | FLAG | Include archived |

**Example output:**

```
Experiments
───────────────────────────────────
Name             Status    Personas  Updated
q4-research      active    5         2 days ago
product-testing  active    3         1 week ago
legacy-study     archived  8         2 months ago
```

### experiment show

Show experiment details.

```bash
persona experiment show <NAME> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--format` | STRING | Output format |
| `--full` | FLAG | Show all details |

### experiment delete

Delete an experiment.

```bash
persona experiment delete <NAME> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--force` | FLAG | Skip confirmation |
| `--keep-outputs` | FLAG | Keep output files |

### experiment export

Export experiment for sharing.

```bash
persona experiment export <NAME> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--output`, `-o` | PATH | Output path |
| `--include-data` | FLAG | Include source data |
| `--include-outputs` | FLAG | Include generated outputs |

---

## Persona Commands

### persona list

List generated personas.

```bash
persona persona list [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--experiment` | STRING | Filter by experiment |
| `--format` | STRING | Output format |

### persona show

Display persona details.

```bash
persona persona show <ID> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--format` | STRING | Output format (rich/json/md) |
| `--evidence` | FLAG | Show evidence links |

### persona validate

Validate persona against source data.

```bash
persona validate <ID> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--source` | PATH | Source data path |
| `--threshold` | INT | Minimum score (0-100) |
| `--report` | FLAG | Generate report |
| `--output` | PATH | Report output path |

**Example:**

```bash
persona validate persona-001 \
  --source experiments/my-experiment/data/ \
  --threshold 80 \
  --report \
  --output validation-report.md
```

### persona compare

Compare two or more personas.

```bash
persona compare <ID1> <ID2> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--format` | STRING | Output format |
| `--metrics` | FLAG | Show similarity metrics |

### persona export

Export persona to external format.

```bash
persona export <ID> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--format` | STRING | Export format (figma/miro/pdf/html) |
| `--output` | PATH | Output path |
| `--all` | FLAG | Export all personas |

### persona refine

Interactively refine a persona.

```bash
persona refine <ID> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--instruction` | STRING | Refinement instruction |
| `--preserve-evidence` | FLAG | Keep evidence links |

---

## Data Commands

### data preview

Preview data before processing.

```bash
persona data preview <PATH> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--tokens` | FLAG | Show token counts |
| `--cost` | FLAG | Show cost estimate |
| `--sample` | INT | Sample lines to show |

**Example output:**

```
Data Preview: experiments/my-experiment/data/
───────────────────────────────────
Files: 4
  interviews.csv      1,200 tokens
  survey.json           800 tokens
  notes.md             500 tokens
  observations.txt      200 tokens
───────────────────────────────────
Total: 2,700 tokens
Estimated cost: $0.09 (claude-3-sonnet)

Sample content:
  "I check the dashboard every morning..."
  "Export takes too many steps..."
```

### data validate

Validate data quality.

```bash
persona data validate <PATH> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--strict` | FLAG | Strict validation |
| `--fix` | FLAG | Attempt fixes |

---

## Configuration Commands

### config show

Show current configuration.

```bash
persona config show [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--all` | FLAG | Show all settings |
| `--section` | STRING | Show specific section |

### config set

Set a configuration value.

```bash
persona config set <KEY> <VALUE>
```

**Examples:**

```bash
persona config set provider.default anthropic
persona config set provider.anthropic.model claude-3-sonnet
persona config set generation.temperature 0.5
persona config set output.format json
```

### config provider

Manage LLM providers.

```bash
persona config provider <ACTION> [OPTIONS]
```

**Actions:**
- `list` - List configured providers
- `add` - Add new provider
- `remove` - Remove provider
- `test` - Test provider connection

### config template

Manage prompt templates.

```bash
persona config template <ACTION> [OPTIONS]
```

**Actions:**
- `list` - List available templates
- `show` - Show template content
- `copy` - Copy template for editing
- `validate` - Validate template syntax

---

## Global Options

Available on all commands:

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help |
| `--version`, `-v` | Show version |
| `--format`, `-f` | Output format: rich\|plain\|json |
| `--no-color` | Disable colour output |
| `--verbose`, `-V` | Detailed output |
| `--quiet`, `-q` | Minimal output |
| `--config` | Config file path |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `PERSONA_PROVIDER` | Default provider | - |
| `PERSONA_MODEL` | Default model | - |
| `PERSONA_CONFIG` | Config file path | `~/.config/persona/config.yaml` |
| `PERSONA_EXPERIMENTS` | Experiments directory | `./experiments` |
| `NO_COLOR` | Disable colour output | - |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Data error |
| 4 | API error |
| 5 | Validation error |
| 130 | Interrupted (Ctrl+C) |

---

## Examples by Task

### First-Time Setup

```bash
# Install
pip install persona-cli

# Configure
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify
persona check

# Try demo
persona demo
```

### Basic Workflow

```bash
# Create experiment
persona experiment create "my-research"

# Add data
cp interviews.csv experiments/my-research/data/

# Preview
persona data preview experiments/my-research/data/

# Generate
persona generate --from experiments/my-research/

# View results
persona persona show persona-001
```

### Validation Workflow

```bash
# Validate single persona
persona validate persona-001 --source data/

# Validate all with report
persona validate --all --report --output report.md

# Check thresholds
persona validate --all --threshold 80
```

### Export Workflow

```bash
# Export to Figma
persona export --all --format figma --output personas.fig

# Export to PDF
persona export persona-001 --format pdf --output sarah.pdf

# Export for sharing
persona experiment export my-research --include-outputs
```

---

## Related Documentation

- [G-01: Choosing a Provider](../guides/choosing-provider.md)
- [G-04: Troubleshooting](../guides/troubleshooting.md)
- [T-01: Getting Started](../tutorials/01-getting-started.md)

