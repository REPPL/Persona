# Configuration Reference

Complete reference for Persona configuration files and options.

## Configuration Hierarchy

Persona uses a layered configuration system:

```
1. Command-line arguments (highest priority)
2. Environment variables
3. Experiment configuration (experiments/<name>/config.yaml)
4. User configuration (~/.persona/config.yaml)
5. System defaults (lowest priority)
```

---

## Environment Variables

### Required API Keys

| Variable | Provider | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | OpenAI | API key for GPT models |
| `ANTHROPIC_API_KEY` | Anthropic | API key for Claude models |
| `GOOGLE_API_KEY` | Google | API key for Gemini models |

### Optional Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PERSONA_HOME` | `~/.persona` | User configuration directory |
| `PERSONA_EXPERIMENTS` | `./experiments` | Default experiments location |
| `PERSONA_OUTPUT` | `./outputs` | Default output location |
| `PERSONA_LOG_LEVEL` | `INFO` | Logging verbosity |
| `PERSONA_NO_COLOR` | `false` | Disable coloured output |

---

## Global Configuration (~/.persona/config.yaml)

User-wide default settings.

### Schema

```yaml
# ~/.persona/config.yaml

# Default provider settings
provider:
  default: anthropic  # openai | anthropic | google | ollama

  openai:
    model: gpt-4o
    temperature: 0.7

  anthropic:
    model: claude-sonnet-4-5-20250929
    temperature: 0.7

  google:
    model: gemini-3.0-pro
    temperature: 0.7

  ollama:
    model: llama3:70b
    base_url: http://localhost:11434

# Output preferences
output:
  format: both  # json | markdown | both
  include_metadata: true
  include_reasoning: true

# Cost settings
cost:
  budget_warning: 5.00  # Warn when estimated cost exceeds this (USD)
  budget_limit: 20.00   # Hard limit (USD)

# Logging
logging:
  level: INFO
  file: ~/.persona/logs/persona.log
  format: json  # json | text
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `provider.default` | string | No | Default LLM provider |
| `provider.<name>.model` | string | No | Default model for provider |
| `provider.<name>.temperature` | float | No | Sampling temperature (0.0-1.0) |
| `output.format` | enum | No | Output format preference |
| `output.include_metadata` | bool | No | Include generation metadata |
| `output.include_reasoning` | bool | No | Include LLM reasoning trace |
| `cost.budget_warning` | float | No | Cost warning threshold (USD) |
| `cost.budget_limit` | float | No | Maximum allowed cost (USD) |

---

## Experiment Configuration (experiments/<name>/config.yaml)

Per-experiment settings that override global configuration.

### Schema

```yaml
# experiments/my-experiment/config.yaml

name: my-experiment
description: User persona generation from interview data
created: 2025-12-14T10:30:00Z

# Data sources
data:
  sources:
    - path: data/interviews.csv
      format: csv
    - path: data/feedback.json
      format: json
  encoding: utf-8

# Generation settings
generation:
  provider: anthropic
  model: claude-sonnet-4-5-20250929
  temperature: 0.7
  max_tokens: 8192
  personas: 3-5  # Can be number or range

# Prompt configuration
prompt:
  template: default  # Template name or path
  variables:
    product_context: "B2B SaaS platform for project management"
    target_audience: "Small to medium businesses"

# Workflow (for multi-step generation)
workflow:
  type: single  # single | multi-step
  steps: []     # Only for multi-step

# Output settings
output:
  directory: ./outputs  # Relative to experiment or absolute
  formats:
    - json
    - markdown
  include:
    - personas
    - metadata
    - reasoning

# Cost controls
cost:
  budget_limit: 10.00
  estimate_before_run: true
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique experiment identifier |
| `description` | string | No | Human-readable description |
| `created` | datetime | Auto | Creation timestamp |
| `data.sources` | array | Yes | List of data source paths |
| `data.sources[].path` | string | Yes | Path to data file |
| `data.sources[].format` | enum | No | File format (auto-detected if omitted) |
| `data.encoding` | string | No | Character encoding (default: utf-8) |
| `generation.provider` | string | No | LLM provider override |
| `generation.model` | string | No | Model override |
| `generation.temperature` | float | No | Temperature (0.0-1.0) |
| `generation.max_tokens` | int | No | Maximum output tokens |
| `generation.personas` | string/int | No | Number of personas to generate |
| `prompt.template` | string | No | Template name or custom path |
| `prompt.variables` | object | No | Template variable values |
| `workflow.type` | enum | No | Workflow type |
| `workflow.steps` | array | No | Workflow step definitions |
| `output.directory` | string | No | Output directory |
| `output.formats` | array | No | Output format list |
| `output.include` | array | No | Components to include |
| `cost.budget_limit` | float | No | Maximum cost (USD) |
| `cost.estimate_before_run` | bool | No | Show estimate before running |

---

## Vendors Configuration (config/vendors.yaml)

LLM provider definitions. Typically system-managed, but can be customised.

### Schema

```yaml
# config/vendors.yaml

vendors:
  openai:
    name: OpenAI
    api_base: https://api.openai.com/v1
    auth_type: bearer
    auth_env: OPENAI_API_KEY
    rate_limit:
      requests_per_minute: 500
      tokens_per_minute: 150000
    endpoints:
      chat: /chat/completions

  anthropic:
    name: Anthropic
    api_base: https://api.anthropic.com/v1
    auth_type: header
    auth_header: x-api-key
    auth_env: ANTHROPIC_API_KEY
    rate_limit:
      requests_per_minute: 1000
      tokens_per_minute: 100000
    endpoints:
      messages: /messages
    headers:
      anthropic-version: "2024-01-01"

  google:
    name: Google AI
    api_base: https://generativelanguage.googleapis.com/v1beta
    auth_type: query
    auth_param: key
    auth_env: GOOGLE_API_KEY
    rate_limit:
      requests_per_minute: 60
      tokens_per_minute: 60000
    endpoints:
      generate: /models/{model}:generateContent

  ollama:
    name: Ollama
    api_base: http://localhost:11434
    auth_type: none
    rate_limit: null
    endpoints:
      generate: /api/generate
      chat: /api/chat
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vendors.<id>.name` | string | Yes | Display name |
| `vendors.<id>.api_base` | string | Yes | Base URL for API |
| `vendors.<id>.auth_type` | enum | Yes | Authentication method |
| `vendors.<id>.auth_env` | string | No | Environment variable for key |
| `vendors.<id>.auth_header` | string | No | Header name (if auth_type=header) |
| `vendors.<id>.auth_param` | string | No | Query param (if auth_type=query) |
| `vendors.<id>.rate_limit` | object | No | Rate limiting configuration |
| `vendors.<id>.endpoints` | object | Yes | API endpoint paths |
| `vendors.<id>.headers` | object | No | Additional required headers |

### Authentication Types

| Type | Description | Example Provider |
|------|-------------|------------------|
| `bearer` | Authorization: Bearer <key> | OpenAI |
| `header` | Custom header with key | Anthropic |
| `query` | API key in query string | Google |
| `none` | No authentication | Ollama (local) |

---

## Models Configuration (config/models.yaml)

Model capabilities and pricing.

### Schema

```yaml
# config/models.yaml

models:
  # Anthropic Models
  claude-opus-4-5-20251101:
    provider: anthropic
    name: Claude Opus 4.5
    context_window: 200000
    max_output: 8192
    pricing:
      input: 15.00   # per 1M tokens
      output: 75.00
    capabilities:
      structured_output: true
      vision: true
      function_calling: true
    recommended_for:
      - maximum_quality
      - complex_reasoning
      - agentic_tasks

  claude-sonnet-4-5-20250929:
    provider: anthropic
    name: Claude Sonnet 4.5
    context_window: 200000
    max_output: 8192
    pricing:
      input: 3.00
      output: 15.00
    capabilities:
      structured_output: true
      vision: true
      function_calling: true
    recommended_for:
      - default
      - coding
      - general_use
    default: true  # Recommended default model

  # OpenAI Models
  gpt-5-20250807:
    provider: openai
    name: GPT-5
    context_window: 256000
    max_output: 16384
    pricing:
      input: 10.00
      output: 30.00
    capabilities:
      structured_output: true
      vision: true
      function_calling: true

  # Google Models
  gemini-3.0-pro:
    provider: google
    name: Gemini 3.0 Pro
    context_window: 2000000
    max_output: 8192
    pricing:
      input: 1.25
      output: 5.00
    capabilities:
      structured_output: true
      vision: true
      function_calling: true
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `models.<id>.provider` | string | Yes | Vendor ID |
| `models.<id>.name` | string | Yes | Display name |
| `models.<id>.context_window` | int | Yes | Maximum input tokens |
| `models.<id>.max_output` | int | Yes | Maximum output tokens |
| `models.<id>.pricing.input` | float | Yes | Cost per 1M input tokens |
| `models.<id>.pricing.output` | float | Yes | Cost per 1M output tokens |
| `models.<id>.capabilities` | object | No | Model capability flags |
| `models.<id>.recommended_for` | array | No | Use case recommendations |
| `models.<id>.default` | bool | No | Mark as default model |

---

## Workflows Configuration (config/workflows.yaml)

Multi-step workflow definitions.

### Schema

```yaml
# config/workflows.yaml

workflows:
  single-step:
    name: Single-Step Generation
    description: Direct persona generation in one LLM call
    steps:
      - name: generate
        template: persona-generation
        output: personas

  extract-consolidate-validate:
    name: Extract-Consolidate-Validate
    description: Research-grade three-step workflow
    steps:
      - name: extract
        template: extract-themes
        model: claude-sonnet-4-5-20250929
        output: raw_themes

      - name: consolidate
        template: consolidate-personas
        model: claude-opus-4-5-20251101
        input: raw_themes
        output: draft_personas

      - name: validate
        template: validate-personas
        model: claude-sonnet-4-5-20250929
        input: draft_personas
        output: personas
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workflows.<id>.name` | string | Yes | Workflow display name |
| `workflows.<id>.description` | string | No | Human-readable description |
| `workflows.<id>.steps` | array | Yes | Ordered list of steps |
| `workflows.<id>.steps[].name` | string | Yes | Step identifier |
| `workflows.<id>.steps[].template` | string | Yes | Prompt template to use |
| `workflows.<id>.steps[].model` | string | No | Model override for step |
| `workflows.<id>.steps[].input` | string | No | Previous step output to use |
| `workflows.<id>.steps[].output` | string | Yes | Output key name |

---

## Prompt Templates (templates/)

Jinja2 templates for LLM prompts.

### Template Directory Structure

```
templates/
├── system/               # Built-in templates
│   ├── persona-generation.j2
│   ├── extract-themes.j2
│   ├── consolidate-personas.j2
│   └── validate-personas.j2
└── user/                 # User custom templates
    └── my-custom-template.j2
```

### Template Variables

| Variable | Type | Description |
|----------|------|-------------|
| `{{ data }}` | string | Combined input data |
| `{{ persona_count }}` | int/string | Requested persona count |
| `{{ product_context }}` | string | Product/service context |
| `{{ target_audience }}` | string | Target user description |
| `{{ custom.* }}` | any | Custom variables from config |

### Example Template

```jinja2
{# templates/user/my-template.j2 #}

You are an expert UX researcher creating user personas.

## Context
{{ product_context }}

## Target Audience
{{ target_audience }}

## Source Data
{{ data }}

## Instructions
Generate {{ persona_count }} detailed user personas based on the data above.

{% if custom.include_quotes %}
Include representative quotes from the source data.
{% endif %}
```

---

## Output Structure

### Default Output Directory Layout

```
outputs/
└── YYYYMMDD_HHMMSS/
    ├── metadata.json           # Generation metadata
    ├── prompt.json             # Prompt used
    ├── files.txt               # Input file list
    ├── full_output.txt         # Complete LLM response
    ├── raw/                    # Intermediate outputs (multi-step)
    │   ├── step_1_extract.json
    │   └── step_2_consolidate.json
    ├── reasoning/              # Reasoning traces
    │   ├── reasoning_trace.md
    │   └── metrics.json
    └── personas/
        ├── 01/
        │   ├── persona.json    # Structured data
        │   └── persona.md      # Human-readable
        ├── 02/
        └── 03/
```

---

## Validation

### Configuration Validation Command

```bash
# Validate all configuration files
persona config validate

# Validate specific file
persona config validate --file experiments/my-exp/config.yaml

# Show merged configuration
persona config show --merged
```

### Common Validation Errors

| Error | Cause | Resolution |
|-------|-------|------------|
| `missing_api_key` | API key not set | Set environment variable |
| `invalid_provider` | Unknown provider ID | Check vendors.yaml |
| `invalid_model` | Unknown model ID | Check models.yaml |
| `budget_exceeded` | Cost exceeds limit | Increase budget or use cheaper model |
| `invalid_template` | Template not found | Check template path |

---

## Related Documentation

- [Model Cards](model-cards.md) - Model capabilities and pricing
- [Provider APIs](provider-apis.md) - API specifications
- [CLI Reference](cli-reference.md) - Command-line usage
- [F-012: Experiment Configuration](../development/roadmap/features/completed/F-012-experiment-configuration.md)
