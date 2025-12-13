# Source Code

Python source code for Persona.

## Structure

```
src/
└── persona/
    ├── __init__.py
    ├── core/                 # Business logic
    │   ├── data_loaders/     # Data loading
    │   ├── llm_providers/    # LLM abstraction
    │   ├── prompts/          # Prompt templating
    │   ├── experiment/       # Experiment management
    │   └── utils/            # Utilities
    └── ui/
        └── cli/              # CLI interface
```

## Development

```bash
# Install in development mode
pip install -e ".[all]"

# Run tests
pytest tests/

# Run CLI
persona --help
```

*Source code will be added during v0.1.0 implementation.*

---

## Related Documentation

- [System Design](../docs/development/planning/architecture/system-design.md)
- [Development Hub](../docs/development/README.md)
