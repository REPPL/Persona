# Acknowledgements

Persona builds upon the work of many researchers, developers, and open source projects. This document acknowledges the key resources and inspirations that have shaped the project.

---

## Academic Research

### AI-Generated Personas

| Source | Authors | Contribution |
|--------|---------|--------------|
| [Generating User Experience Based on Personas with AI Assistants](https://arxiv.org/abs/2405.01051) | Shin et al. | IEEE/ACM ICSE 2024 paper providing theoretical framework for LLM + persona combination in adaptive UX development. Core inspiration for Persona's methodology. |
| [Vector Personas for UX Research](https://uxpajournal.org/leveraging-ai-toward-the-development-of-vector-personas-for-ux-research/) | JUX 2024 | Research on mathematical representations of personas for programmatic analysis. |

---

## Frameworks & Libraries

### Core Dependencies

| Library | Maintainers | Licence | How Used |
|---------|-------------|---------|----------|
| [Typer](https://typer.tiangolo.com/) | Sebastián Ramírez | MIT | CLI framework with type hints |
| [Rich](https://rich.readthedocs.io/) | Will McGugan | MIT | Beautiful terminal output, progress bars, tables |
| [Pydantic](https://docs.pydantic.dev/) | Samuel Colvin et al. | MIT | Data validation and settings management |
| [Jinja2](https://jinja.palletsprojects.com/) | Pallets Projects | BSD-3-Clause | Prompt templating engine |
| [httpx](https://www.python-httpx.org/) | Encode | BSD-3-Clause | Async HTTP client for API requests |

### LLM Integration

| Library | Maintainers | Licence | How Used |
|---------|-------------|---------|----------|
| [LiteLLM](https://docs.litellm.ai/) | BerriAI | MIT | Multi-provider LLM abstraction |
| [Instructor](https://python.useinstructor.com/) | Jason Liu (567 Labs) | MIT | Structured output extraction |
| [tiktoken](https://github.com/openai/tiktoken) | OpenAI | MIT | Token counting for cost estimation |

### Development Tools

| Library | Maintainers | Licence | How Used |
|---------|-------------|---------|----------|
| [pytest](https://pytest.org/) | pytest-dev | MIT | Testing framework |
| [Ruff](https://docs.astral.sh/ruff/) | Astral | MIT | Fast Python linter |
| [mypy](https://mypy-lang.org/) | Python Community | MIT | Static type checking |

---

## Predecessor Projects

### PersonaZero

| Project | Author | Contribution |
|---------|--------|--------------|
| [PersonaZero](https://github.com/REPPL/PersonaZero) | REPPL | Original persona generation tool (v3.7.4). Persona is a clean rewrite applying lessons learned. See [PersonaZero Analysis](./personazero-analysis.md) for details. |

### ragd Methodology

| Project | Source | Contribution |
|---------|--------|--------------|
| [ragd](https://github.com/REPPL/ragd) | REPPL | Development methodology and hybrid specification approach. ADR-0004 from ragd provides the Use Cases → Features → Tutorials framework used in Persona. |

---

## Industry Resources

### Best Practices & Patterns

| Resource | Source | Contribution |
|----------|--------|--------------|
| [7 Typer CLI Patterns](https://medium.com/@connect.hashblock/7-typer-cli-patterns-that-feel-like-real-tools-ecbe72720828) | Hash Block | CLI design patterns |
| [Structured Output Comparison](https://medium.com/@rosgluk/structured-output-comparison-across-popular-llm-providers-openai-gemini-anthropic-mistral-and-1a5d42fa612a) | Rost Glukhov | Provider-specific structured output analysis |
| [Jinja2 Prompting Guide](https://medium.com/@alecgg27895/jinja2-prompting-a-guide-on-using-jinja2-templates-for-prompt-management-in-genai-applications-e36e5c1243cf) | Alex Gonzalez | Prompt templating best practices |

---

## Adding New Acknowledgements

When adding a new acknowledgement, use this template:

```markdown
| [Name](URL) | Authors/Organisation | Contribution description. |
```

**Categories:**
- **Academic Research** - Papers, studies, theoretical frameworks
- **Frameworks & Libraries** - Code dependencies with licence info
- **Predecessor Projects** - Projects that directly influenced Persona
- **Industry Resources** - Blog posts, guides, best practices

---

## Licence Compatibility

All acknowledged libraries use licences compatible with GPLv3:

| Licence | Compatibility |
|---------|--------------|
| MIT | ✅ Compatible |
| BSD-3-Clause | ✅ Compatible |
| Apache 2.0 | ✅ Compatible |
| GPLv3 | ✅ Same licence |

---

## Related Documentation

- [PersonaZero Analysis](./personazero-analysis.md)
- [Research Notes](../research/)
- [Architecture Decisions](../decisions/adrs/)
