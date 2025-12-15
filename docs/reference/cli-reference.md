# CLI Reference

Complete command-line interface documentation for Persona.

## Quick Reference Card

```
persona generate    Generate personas from data
persona check       Verify installation and configuration
persona preview     Preview data before processing
persona validate    Validate personas against source
persona compare     Compare persona similarity
persona help        Show help for any command
```

## Command Groups

### Core Commands

Primary persona generation and analysis commands.

| Command | Description |
|---------|-------------|
| `generate` | Generate personas from data |
| `preview` | Preview data before processing |
| `validate` | Validate personas against source |
| `compare` | Compare persona similarity |
| `export` | Export personas to external formats |
| `cluster` | Cluster and consolidate personas |
| `refine` | Interactively refine personas |

### Utility Commands

System and configuration commands.

| Command | Description |
|---------|-------------|
| `check` | Verify installation and providers |
| `cost` | Estimate API costs before generation |
| `models` | List available models with pricing |
| `init` | Initialise a new Persona project |
| `help` | Show help for commands |

### Experiment Commands

Manage experiments and projects.

| Command | Description |
|---------|-------------|
| `experiment create` | Create new experiment |
| `experiment list` | List all experiments |
| `experiment show` | Show experiment details |
| `experiment delete` | Delete experiment |
| `experiment edit` | Edit experiment configuration |
| `experiment history` | View experiment run history |
| `experiment sources` | List data sources for an experiment |
| `experiment record-run` | Record a generation run in history |
| `experiment clear-history` | Clear run history for an experiment |

### Configuration Commands

Manage configuration.

| Command | Description |
|---------|-------------|
| `config init` | Initialise global configuration |
| `config show` | Show current configuration |
| `config get` | Get a specific configuration value |
| `config set` | Set configuration value |
| `config reset` | Reset to defaults |
| `config path` | Show configuration file paths |
| `config edit` | Open interactive configuration editor |

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
| `--from`, `-f` | PATH | Required | Data source (file, folder, or experiment name) |
| `--output`, `-o` | PATH | ./outputs | Output directory |
| `--count`, `-n` | INT | 3 | Number of personas |
| `--provider`, `-p` | STRING | anthropic | LLM provider (anthropic, openai, gemini) |
| `--model`, `-m` | STRING | Provider default | Model name |
| `--workflow`, `-w` | STRING | default | Workflow to use (default, research, quick) |
| `--experiment`, `-e` | STRING | - | Experiment name to save results under |
| `--dry-run` | FLAG | False | Preview without calling LLM |
| `--no-progress` | FLAG | False | Disable progress bar |

**Smart Path Resolution:**

The `--from` flag supports multiple input formats:
- Direct path: `persona generate --from ./data/interviews.csv`
- Experiment name: `persona generate --from my-experiment` (resolves to `experiments/my-experiment/data/`)

**Examples:**

```bash
# Basic generation from a file
persona generate --from ./data/interviews.csv

# Generate from an experiment (auto-resolves path)
persona generate --from my-experiment

# Specify provider and count
persona generate -f data/ -n 5 --provider anthropic --model claude-sonnet-4-20250514

# Dry run (preview only)
persona generate -f data/ --dry-run

# Interactive mode
persona generate -i
```

### check

Verify installation and configuration.

```bash
persona check [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--json` | FLAG | Output results as JSON |

**Example output:**

```
Persona Health Check
───────────────────────────────────
✓ Version: 1.0.0
✓ Installation: OK

Provider Status:
───────────────────────────────────
  ✓ anthropic: Configured
  ✓ openai: Configured
  ○ gemini: Not configured (GOOGLE_API_KEY)

Ready! 2 provider(s) available.
```

### cost

Estimate API costs before generating.

```bash
persona cost [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--from`, `-f` | PATH | Data file for token estimation |
| `--tokens`, `-t` | INT | Number of input tokens (if not using --from) |
| `--count`, `-n` | INT | Number of personas (default: 3) |
| `--provider`, `-p` | STRING | Filter by provider |
| `--model`, `-m` | STRING | Specific model to estimate |
| `--json` | FLAG | Output as JSON |

**Example:**

```bash
persona cost --from ./data/interviews.csv --count 5
persona cost --tokens 10000 --model gpt-4o
```

### models

List available models with pricing information.

```bash
persona models [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--provider`, `-p` | STRING | Filter by provider |
| `--json` | FLAG | Output as JSON |

### init

Initialise a new Persona project.

```bash
persona init [PATH]
```

Creates the recommended directory structure:
- `experiments/` - Experiment storage
- `data/` - Source data files
- `templates/` - Custom templates
- `persona.yaml` - Project configuration

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
| `--base-dir`, `-b` | PATH | Base directory for experiments |
| `--json` | FLAG | Output as JSON |

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

Show experiment details and outputs.

```bash
persona experiment show <NAME> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--base-dir`, `-b` | PATH | Base directory for experiments |

### experiment delete

Delete an experiment and its data.

```bash
persona experiment delete <NAME> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--force`, `-f` | FLAG | Skip confirmation prompt |
| `--base-dir`, `-b` | PATH | Base directory for experiments |

### experiment sources

List data sources for an experiment.

```bash
persona experiment sources <NAME> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--base-dir`, `-b` | PATH | Base directory for experiments |

### experiment record-run

Record a generation run in history.

```bash
persona experiment record-run <NAME> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--model`, `-m` | STRING | Model used (required) |
| `--provider`, `-p` | STRING | Provider used (required) |
| `--personas`, `-n` | INT | Number of personas generated (default: 0) |
| `--cost` | FLOAT | Cost in USD (default: 0.0) |
| `--status` | STRING | Run status (default: completed) |
| `--output-dir` | PATH | Output directory path |
| `--base-dir`, `-b` | PATH | Base directory for experiments |

### experiment clear-history

Clear run history for an experiment.

```bash
persona experiment clear-history <NAME> [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--force`, `-f` | FLAG | Skip confirmation |
| `--base-dir`, `-b` | PATH | Base directory for experiments |

---

## Configuration Commands

### config show

Show effective configuration.

```bash
persona config show [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--json` | FLAG | Output as JSON |
| `--source`, `-s` | FLAG | Show configuration sources |

### config get

Get a configuration value.

```bash
persona config get <PATH>
```

**Arguments:**

- `path` - Configuration path (e.g., `defaults.provider`)

**Example:**

```bash
persona config get defaults.provider
persona config get budgets.per_run
```

### config set

Set a configuration value.

```bash
persona config set <PATH> <VALUE> [OPTIONS]
```

**Arguments:**

- `path` - Configuration path (e.g., `defaults.provider`)
- `value` - Value to set

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--project`, `-p` | FLAG | Set in project config instead of global |

**Examples:**

```bash
persona config set defaults.provider anthropic
persona config set defaults.model claude-sonnet-4-20250514
persona config set budgets.per_run 1.00
```

### config reset

Reset configuration to defaults.

```bash
persona config reset [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--project`, `-p` | FLAG | Reset project config instead of global |
| `--force`, `-f` | FLAG | Skip confirmation |

### config path

Show configuration file paths.

```bash
persona config path
```

Displays the locations of global and project configuration files.

### config edit

Open interactive configuration editor.

```bash
persona config edit [SECTION] [OPTIONS]
```

**Arguments:**

- `section` (optional) - Configuration section to edit (defaults, budgets, output, logging)

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--project`, `-p` | FLAG | Edit project config instead of global |

---

## Global Options

Available on all commands:

| Option | Description |
|--------|-------------|
| `--help` | Show help |
| `--version`, `-V` | Show version and exit |
| `--no-color` | Disable colour output |
| `--quiet`, `-q` | Minimal output (errors and results only) |
| `--verbose`, `-v` | Increase verbosity (-v verbose, -vv debug) |
| `--interactive`, `-i` | Run in interactive mode with guided prompts |

**Note:** The `--no-color` flag uses American spelling to comply with the [NO_COLOR](https://no-color.org/) standard, which specifies this exact spelling for cross-tool compatibility. The `NO_COLOR` environment variable is also supported.

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `GOOGLE_API_KEY` | Google Gemini API key | - |
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
# Clone and install
git clone https://github.com/REPPL/Persona.git
cd Persona
pip install -e ".[all]"

# Configure API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify installation
persona check

# Initialise a project
persona init ./my-project
```

### Basic Workflow

```bash
# Create experiment
persona experiment create "my-research"

# Add data
cp interviews.csv experiments/my-research/data/

# Preview data (check tokens and cost)
persona preview experiments/my-research/data/

# Generate from experiment name (auto-resolves path)
persona generate --from my-research

# Check cost before generating
persona cost --from experiments/my-research/data/ --count 5
```

### Validation Workflow

```bash
# Validate personas
persona validate ./outputs/personas.json

# Validate with strict mode
persona validate ./outputs/ --strict
```

### Export Workflow

```bash
# List available export formats
persona export formats

# Export to various formats
persona export ./outputs/personas.json --format markdown
persona export ./outputs/personas.json --format figma

# Preview export without writing
persona export ./outputs/personas.json --format csv --preview
```

---

## Related Documentation

- [G-01: Choosing a Provider](../guides/choosing-provider.md)
- [G-04: Troubleshooting](../guides/troubleshooting.md)
- [T-01: Getting Started](../tutorials/01-getting-started.md)

