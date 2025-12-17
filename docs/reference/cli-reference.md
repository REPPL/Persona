# CLI Reference

Complete command-line interface documentation for Persona.

## Quick Reference Card

```
persona generate    Generate personas from data
persona check       Verify installation and configuration
persona preview     Preview data before processing
persona validate    Validate personas against source
persona compare     Compare persona similarity
persona project     Manage Persona projects
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

### Project Commands

Registry-based project management.

| Command | Description |
|---------|-------------|
| `project list` | List all registered projects |
| `project create` | Create a new project |
| `project register` | Register an existing project |
| `project unregister` | Remove a project from registry |
| `project show` | Show project details |
| `project add-source` | Add a data source to a project |
| `project remove-source` | Remove a data source |
| `project defaults` | Show or set global defaults |
| `project init-registry` | Initialise the project registry |

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

### Variant Commands (Advanced)

Manage experiment variants - named parameter sets for comparing configurations.

| Command | Description |
|---------|-------------|
| `variant create` | Create a variant for an experiment |
| `variant list` | List variants for an experiment |
| `variant show` | Show variant details |
| `variant update` | Update a variant's parameters |
| `variant delete` | Delete a variant |
| `variant compare` | Compare parameters between variants |

### Lineage Commands (Advanced)

Track and verify data lineage and provenance.

| Command | Description |
|---------|-------------|
| `lineage list` | List tracked entities |
| `lineage show` | Show entity details |
| `lineage trace` | Trace entity lineage |
| `lineage verify` | Verify entity integrity |
| `lineage export` | Export lineage as PROV-JSON |
| `lineage agents` | List registered agents |
| `lineage activities` | List tracked activities |

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

## Project Commands

### project list

List all registered projects.

```bash
persona project list [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--json` | FLAG | Output as JSON |

### project create

Create a new project.

```bash
persona project create <NAME> [OPTIONS]
```

**Arguments:**

- `NAME` - Name for the new project

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--path`, `-p` | PATH | Current directory | Directory to create project in |
| `--template`, `-t` | STRING | basic | Project template (basic or research) |
| `--description`, `-d` | STRING | - | Project description |
| `--no-register` | FLAG | False | Don't register in global registry |

**Templates:**
- **basic** - Minimal structure (data/, output/)
- **research** - Full structure with config/, templates/ directories

**Example:**

```bash
persona project create my-research
persona project create my-study --template research
persona project create demo --path ./projects --description "Demo project"
```

### project register

Register an existing project in the global registry.

```bash
persona project register <NAME> <PATH> [OPTIONS]
```

**Arguments:**

- `NAME` - Name to register the project as
- `PATH` - Path to existing project directory

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--force`, `-f` | FLAG | Update path if project already registered |

### project unregister

Remove a project from the global registry.

```bash
persona project unregister <NAME> [OPTIONS]
```

**Arguments:**

- `NAME` - Name of project to unregister

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--force`, `-f` | FLAG | Skip confirmation |

**Note:** This does not delete project files, only removes the registry entry.

### project show

Show project details.

```bash
persona project show [NAME] [OPTIONS]
```

**Arguments:**

- `NAME` (optional) - Project name or path. Uses current directory if not specified.

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--json` | FLAG | Output as JSON |

### project add-source

Add a data source to a project.

```bash
persona project add-source <NAME> <PATH> [OPTIONS]
```

**Arguments:**

- `NAME` - Name for the data source
- `PATH` - Relative path to data file from project root

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--project`, `-p` | STRING | Current directory | Project to add source to |
| `--type`, `-t` | STRING | raw | Data type (qualitative, quantitative, mixed, raw) |
| `--description`, `-d` | STRING | - | Description of the data source |

**Example:**

```bash
persona project add-source interviews data/interviews.csv
persona project add-source survey data/survey.json --type quantitative
```

### project remove-source

Remove a data source from a project.

```bash
persona project remove-source <NAME> [OPTIONS]
```

**Arguments:**

- `NAME` - Name of data source to remove

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--project`, `-p` | STRING | Project to remove source from |

### project defaults

Show or set global defaults.

```bash
persona project defaults [OPTIONS]
```

Without options, shows current defaults. With options, updates them.

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--provider` | STRING | Set default provider |
| `--model` | STRING | Set default model |
| `--count` | INT | Set default persona count |

**Example:**

```bash
persona project defaults
persona project defaults --provider openai
persona project defaults --count 5
```

### project init-registry

Initialise the project registry.

```bash
persona project init-registry [OPTIONS]
```

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--force`, `-f` | FLAG | Overwrite existing registry |

---

## Variant Commands (Advanced)

Variants are named parameter sets that allow comparing different configurations within the same experiment. These commands require an experiment to be created first.

### variant create

Create a variant for an experiment.

```bash
persona variant create <EXPERIMENT> <NAME> [OPTIONS]
```

**Arguments:**

- `EXPERIMENT` - Experiment name or ID
- `NAME` - Name for the variant

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--param`, `-p` | STRING | Parameter in key=value format (repeatable) |
| `--json`, `-j` | STRING | Parameters as JSON string |
| `--description`, `-d` | STRING | Description of the variant |

**Examples:**

```bash
# Create with individual parameters
persona variant create my-experiment high-temp --param temperature=0.9

# Create with multiple parameters
persona variant create my-experiment creative \
    --param temperature=0.9 \
    --param top_p=0.95 \
    --description "High creativity settings"

# Create with JSON parameters
persona variant create my-experiment precise \
    --json '{"temperature": 0.3, "top_p": 0.8}'
```

### variant list

List variants for an experiment.

```bash
persona variant list <EXPERIMENT> [OPTIONS]
```

**Arguments:**

- `EXPERIMENT` - Experiment name or ID

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--json` | FLAG | Output as JSON |

### variant show

Show variant details.

```bash
persona variant show <EXPERIMENT> <NAME> [OPTIONS]
```

**Arguments:**

- `EXPERIMENT` - Experiment name or ID
- `NAME` - Variant name

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--json` | FLAG | Output as JSON |

### variant update

Update a variant's parameters or description.

```bash
persona variant update <EXPERIMENT> <NAME> [OPTIONS]
```

**Arguments:**

- `EXPERIMENT` - Experiment name or ID
- `NAME` - Variant name

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--param`, `-p` | STRING | Parameter to add/update in key=value format |
| `--remove`, `-r` | STRING | Parameter key to remove |
| `--description`, `-d` | STRING | Update description |

**Examples:**

```bash
# Add or update a parameter
persona variant update my-experiment high-temp --param temperature=0.95

# Remove a parameter
persona variant update my-experiment high-temp --remove top_p

# Update description
persona variant update my-experiment high-temp -d "Very creative output"
```

### variant delete

Delete a variant.

```bash
persona variant delete <EXPERIMENT> <NAME> [OPTIONS]
```

**Arguments:**

- `EXPERIMENT` - Experiment name or ID
- `NAME` - Variant name

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--force`, `-f` | FLAG | Skip confirmation |

### variant compare

Compare parameters between two variants.

```bash
persona variant compare <EXPERIMENT> <VARIANT1> <VARIANT2> [OPTIONS]
```

**Arguments:**

- `EXPERIMENT` - Experiment name or ID
- `VARIANT1` - First variant name
- `VARIANT2` - Second variant name

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--json` | FLAG | Output as JSON |

**Example:**

```bash
persona variant compare my-experiment high-temp low-temp
```

---

## Lineage Commands (Advanced)

Data lineage commands track and verify provenance throughout the persona generation pipeline. These commands use the W3C PROV data model for tracking entities, activities, and agents.

### lineage list

List tracked entities.

```bash
persona lineage list [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--type`, `-t` | STRING | - | Filter by entity type (input_file, persona, etc.) |
| `--limit`, `-n` | INT | 20 | Maximum number of entities to show |
| `--json` | FLAG | False | Output as JSON |

**Example:**

```bash
persona lineage list
persona lineage list --type persona
persona lineage list --limit 50 --json
```

### lineage show

Show entity details.

```bash
persona lineage show <ENTITY_ID> [OPTIONS]
```

**Arguments:**

- `ENTITY_ID` - Entity ID to show

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--json` | FLAG | Output as JSON |

### lineage trace

Trace entity lineage.

```bash
persona lineage trace <ENTITY_ID> [OPTIONS]
```

Shows the provenance chain for an entity - what inputs were used to create it (ancestors) or what was derived from it (descendants).

**Arguments:**

- `ENTITY_ID` - Entity ID to trace

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--direction`, `-d` | STRING | up | Trace direction: up (ancestors), down (descendants), or both |
| `--depth` | INT | - | Maximum traversal depth |
| `--json` | FLAG | False | Output as JSON |

**Examples:**

```bash
persona lineage trace ent-abc123 --direction up
persona lineage trace ent-abc123 --direction down --depth 3
persona lineage trace ent-abc123 --direction both --json
```

### lineage verify

Verify entity integrity.

```bash
persona lineage verify <ENTITY_ID> [OPTIONS]
```

Checks that stored hashes match current file contents to detect tampering or modifications.

**Arguments:**

- `ENTITY_ID` - Entity ID to verify

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--chain`, `-c` | FLAG | Verify entire ancestor chain |
| `--json` | FLAG | Output as JSON |

**Examples:**

```bash
persona lineage verify ent-abc123
persona lineage verify ent-abc123 --chain
```

### lineage export

Export lineage as PROV-JSON.

```bash
persona lineage export [ENTITY_ID] [OPTIONS]
```

Exports lineage data in W3C PROV-JSON format for external tools or archival.

**Arguments:**

- `ENTITY_ID` (optional) - Entity ID (omit for all)

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output`, `-o` | PATH | - | Output file path |
| `--format`, `-f` | STRING | prov-json | Export format |

**Examples:**

```bash
persona lineage export --output lineage.json
persona lineage export ent-abc123 -o entity-lineage.json
```

### lineage agents

List registered agents.

```bash
persona lineage agents [OPTIONS]
```

Shows all agents (LLMs, tools, users) that have performed activities.

**Options:**

| Option | Type | Description |
|--------|------|-------------|
| `--type`, `-t` | STRING | Filter by agent type |
| `--json` | FLAG | Output as JSON |

**Example:**

```bash
persona lineage agents
persona lineage agents --type llm_model
```

### lineage activities

List tracked activities.

```bash
persona lineage activities [OPTIONS]
```

Shows transformations that have been performed on data.

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--type`, `-t` | STRING | - | Filter by activity type |
| `--run`, `-r` | STRING | - | Filter by experiment run ID |
| `--limit`, `-n` | INT | 20 | Maximum number to show |
| `--json` | FLAG | False | Output as JSON |

**Example:**

```bash
persona lineage activities
persona lineage activities --type llm_generation
persona lineage activities --run run-abc123
```

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
