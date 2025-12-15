# License Compliance Analysis

Persona is licensed under **GPL-3.0-or-later**. All dependencies must be compatible with this license.

## Compliance Summary

**Status:** ✅ All dependencies GPL3-compatible

**Analysis Date Context:** v1.7.0 release preparation

## License Categories

### Permissive Licenses (GPL3 Compatible)

| License | Count | Examples |
|---------|-------|----------|
| MIT | 70+ | typer, rich, pydantic, textual, spacy |
| BSD-3-Clause | 20+ | jinja2, httpx, click, starlette, torch |
| Apache-2.0 | 15+ | transformers, huggingface-hub, requests |
| ISC | 5 | griffe, mkdocstrings, shellingham |
| MPL-2.0 | 2 | certifi, pathspec |
| Unlicense | 1 | filelock |
| PSF-2.0 | 2 | typing_extensions, matplotlib |

### Core Dependencies

| Package | License | Compatibility |
|---------|---------|---------------|
| typer | MIT | ✅ |
| rich | MIT | ✅ |
| questionary | MIT | ✅ |
| pyyaml | MIT | ✅ |
| jinja2 | BSD-3-Clause | ✅ |
| pydantic | MIT | ✅ |
| httpx | BSD-3-Clause | ✅ |
| tiktoken | MIT | ✅ |
| python-dotenv | BSD-3-Clause | ✅ |
| textual | MIT | ✅ |

### Optional Dependencies

| Group | Package | License | Compatibility |
|-------|---------|---------|---------------|
| academic | bert-score | MIT | ✅ |
| academic | rouge-score | Apache-2.0 | ✅ |
| academic | transformers | Apache-2.0 | ✅ |
| privacy | presidio-analyzer | MIT | ✅ |
| privacy | spacy | MIT | ✅ |
| api | fastapi | MIT | ✅ |
| api | uvicorn | BSD-3-Clause | ✅ |

### Deep Learning Stack

| Package | License | Compatibility |
|---------|---------|---------------|
| torch | BSD-3-Clause | ✅ |
| transformers | Apache-2.0 | ✅ |
| huggingface-hub | Apache-2.0 | ✅ |
| tokenizers | Apache-2.0 | ✅ |
| safetensors | Apache-2.0 | ✅ |

## License Compatibility Notes

### Why These Licenses Are Compatible

1. **MIT, BSD, ISC**: Permissive licenses allow incorporation into GPL projects
2. **Apache-2.0**: Compatible with GPL-3.0 (not GPL-2.0)
3. **MPL-2.0**: Weak copyleft, compatible with GPL-3.0
4. **Unlicense/Public Domain**: No restrictions
5. **PSF**: Python-specific permissive license

### Licenses to Avoid

The following license types would be **incompatible** with GPL-3.0:
- GPL-2.0-only (without "or later" clause)
- CDDL (Common Development and Distribution License)
- CC-BY-NC (Creative Commons Non-Commercial)
- Proprietary/Commercial licenses

## Verification Command

To regenerate this analysis:

```bash
source .venv/bin/activate
pip install pip-licenses
pip-licenses --format=markdown
```

## Maintenance

- Review licenses when adding new dependencies
- Run `pip-licenses` before each release
- Update this document if new license types are introduced

---

**Status**: Verified for v1.7.0
