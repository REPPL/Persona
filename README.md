[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Status: Planning](https://img.shields.io/badge/status-planning-yellow.svg)]()
[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blueviolet?logo=anthropic)](https://claude.ai/code)

![Persona logo](docs/assets/img/persona-logo.png)

## Generate realistic user personas from your data using AI

`Persona` is an AI-powered tool that generates realistic user personas from qualitative research data. It supports multiple LLM providers *(incl. OpenAI, Anthropic, Gemini)* and provides an experiment-centric workflow for reproducible persona generation.

### Who is this for?

- **UX Researchers** synthesising interview and survey data
- **Product Managers** understanding user segments
- **Academic Researchers** analysing qualitative data at scale
- **Design Teams** creating data-driven personas

### Why Persona?

| Traditional Approach | With Persona |
|---------------------|--------------|
| Days of manual analysis | Minutes of processing |
| Subjective pattern recognition | Consistent, reproducible results |
| Limited by analyst capacity | Scales to any dataset size |
| Persona quality varies | Evidence-linked outputs |

## Quick Start

### Prerequisites

- Python 3.12 or higher
- API key from OpenAI, Anthropic, or Google

### Installation

```bash
# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install from source (development)
git clone https://github.com/REPPL/Persona.git
cd Persona
pip install -e ".[all]"
```

### Your First Persona

```bash
# 1. Verify your setup
persona check

# 2. Create an experiment
persona create experiment "My Research"

# 3. Add your data files to experiments/my-research/data/

# 4. Generate personas
persona generate my-research
```

Your personas are saved as JSON and Markdown in timestamped output folders.

## Features

| Feature | Benefit |
|---------|---------|
| **Evidence-linked personas** | Every attribute traced to your source data |
| **Cost transparency** | Know exactly what you'll pay before generating |
| **Multiple AI providers** | Choose OpenAI, Claude, or Gemini based on your needs |
| **Reproducible experiments** | Re-run any generation with identical results |
| **Works with your data** | CSV, JSON, Markdown, and more - no reformatting needed |
| **Beautiful output** | Polished terminal UI and ready-to-share exports |

## Example Output

```json
{
  "name": "Research Rachel",
  "age": 34,
  "occupation": "UX Research Lead",
  "goals": [
    "Synthesise research faster without losing nuance",
    "Create personas that stakeholders actually use"
  ],
  "pain_points": [
    "Manual analysis takes weeks",
    "Difficulty tracking evidence back to source data"
  ],
  "evidence": {
    "goals[0]": "Interview 3, line 45: 'I spend more time writing reports than doing research'",
    "pain_points[1]": "Survey response 12: 'I can never remember which interview a quote came from'"
  }
}
```

## Documentation

| I want to... | Go to... |
|--------------|----------|
| Learn step-by-step | [Tutorials](docs/tutorials/) |
| Accomplish a specific task | [How-to Guides](docs/guides/) |
| Understand concepts | [Explanation](docs/explanation/) |
| Look up specifications | [Reference](docs/reference/) |

### Key Documents

- [Getting Started Tutorial](docs/tutorials/01-getting-started.md)
- [Use Cases](docs/use-cases/) - What you can do with Persona
- [System Design](docs/development/planning/architecture/system-design.md)
- [Roadmap](docs/development/roadmap/)

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

## Comparison with Similar Tools

| Tool | Approach | Persona's Advantage |
|------|----------|---------------------|
| Manual synthesis | Time-consuming, subjective | Faster, consistent, evidence-linked |
| Generic LLM prompting | No structure, hallucination risk | Structured output, source validation |
| [Persona Hub](https://github.com/tencent-ailab/persona-hub) | Pre-built synthetic personas | Generated from YOUR data |
| [PersonaCraft](https://www.sciencedirect.com/science/article/abs/pii/S1071581925000023) | Academic methodology | Open source, CLI-first |

## Lineage

Persona is a clean rewrite of [PersonaZero](https://github.com/REPPL/PersonaZero), applying lessons learned during the development of [ragd](https://github.com/REPPL/ragd).

## AI Transparency

This project is developed with AI assistance. See the [AI Contributions Statement](docs/development/ai-contributions.md).

---

**GPLv3+** - See [LICENCE](LICENCE) for details.
