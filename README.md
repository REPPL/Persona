[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Status: Planning](https://img.shields.io/badge/status-planning-yellow.svg)]()
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet?logo=anthropic)](https://claude.ai/code)

![Persona logo](docs/assets/img/persona-logo.png)

## Generate realistic user personas from your data using AI

`Persona` is an AI-powered tool that generates realistic user personas from qualitative research data. It supports multiple LLM providers *(incl. OpenAI, Anthropic, Gemini)* and provides an experiment-centric workflow for reproducible persona generation.

## Features

- **Multi-format data loading** - Support for txt, csv, json, md, yaml, and org files
- **Multi-provider LLM support** - OpenAI, Anthropic, and Google Gemini
- **Experiment workflow** - Organised, reproducible persona generation
- **Cost estimation** - Know costs before running expensive operations
- **Structured output** - JSON personas with timestamped organisation
- **Rich CLI** - Beautiful terminal interface with progress tracking

## Quick Start

```bash
# Install
pip install persona

# Check system health
persona check

# Create an experiment
persona create experiment

# Generate personas
persona generate my-experiment
```

## Documentation

| Section | Description |
|---------|-------------|
| [Tutorials](docs/tutorials/) | Step-by-step learning guides |
| [Use Cases](docs/use-cases/) | What you can do with Persona |
| [Reference](docs/reference/) | Configuration and API reference |
| [Development](docs/development/) | Contributing and architecture |

### Key Documents

- [Getting Started Tutorial](docs/tutorials/01-getting-started.md)
- [System Design](docs/development/planning/architecture/system-design.md)
- [Roadmap](docs/development/roadmap/)
- [Architecture Decisions](docs/development/decisions/adrs/)

## Requirements

- Python 3.12+
- API key for at least one LLM provider:
  - OpenAI API key
  - Anthropic API key
  - Google AI API key

## Installation

```bash
# From PyPI (when released)
pip install persona

# From source (development)
git clone https://github.com/REPPL/Persona.git
cd Persona
pip install -e ".[all]"
```

## Basic Usage

### 1. Create an Experiment

```bash
persona create experiment
```

This creates a new experiment directory with configuration template.

### 2. Add Your Data

Place your research data files in the experiment's `data/` directory:

```
experiments/my-experiment/
├── config.yaml
├── data/
│   ├── interviews.txt
│   └── survey-responses.csv
└── outputs/
```

### 3. Configure and Generate

Edit `config.yaml` to specify your LLM provider and settings, then:

```bash
persona generate my-experiment
```

### 4. Review Results

Personas are saved to timestamped output folders:

```
experiments/my-experiment/outputs/
└── 20241215_143022/
    ├── personas.json
    └── README.md
```

## Configuration

### Environment Variables

```bash
# Set your preferred provider's API key
export OPENAI_API_KEY="sk-..."
# or
export ANTHROPIC_API_KEY="sk-ant-..."
# or
export GOOGLE_AI_API_KEY="..."
```

### Experiment Configuration

```yaml
# config.yaml
vendor: openai
model: gpt-4o
persona_count: 5
```

See [Configuration Reference](docs/reference/) for all options.

## Development

```bash
# Install with development dependencies
pip install -e ".[all]"

# Run tests
pytest tests/

# Run linting
ruff check src/

# Run type checking
mypy src/
```

See [Development Documentation](docs/development/) for contributing guidelines.

## Lineage

Persona is a clean rewrite of [PersonaZero](https://github.com/REPPL/PersonaZero), applying lessons learned during the development of [ragd](https://github.com/REPPL/ragd).

## AI Transparency

This project is developed with AI assistance. See the [AI Contributions Statement](docs/development/ai-contributions.md).
