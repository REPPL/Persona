# API Key Setup Guide

This guide explains how to configure API keys for Persona's LLM providers.

## Quick Start

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API keys:
   ```bash
   # Use your preferred editor
   nano .env
   ```

3. Verify configuration:
   ```bash
   persona check
   ```

## Provider Setup

### Anthropic (Recommended)

Claude models offer excellent evidence grounding for persona generation.

1. Go to [Anthropic Console](https://console.anthropic.com/settings/keys)
2. Click "Create Key"
3. Copy the key (starts with `sk-ant-`)
4. Add to `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   ```

### OpenAI

GPT models offer creative writing and multimodal capabilities.

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Click "Create new secret key"
3. Copy the key (starts with `sk-`)
4. Add to `.env`:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

### Google (Gemini)

Gemini offers massive context windows (up to 2M tokens).

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key (starts with `AIza`)
4. Add to `.env`:
   ```
   GOOGLE_API_KEY=AIza-your-key-here
   ```

### Ollama (Local)

Ollama runs models locally - no API key needed.

1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3:70b
   ```
3. Start Ollama:
   ```bash
   ollama serve
   ```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | For OpenAI | OpenAI API key |
| `ANTHROPIC_API_KEY` | For Anthropic | Anthropic API key |
| `GOOGLE_API_KEY` | For Google | Google AI API key |
| `OLLAMA_BASE_URL` | No | Ollama server URL (default: localhost:11434) |
| `PERSONA_DEFAULT_PROVIDER` | No | Default provider (anthropic, openai, google, ollama) |
| `PERSONA_LOG_LEVEL` | No | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `NO_COLOR` | No | Disable coloured output (set to 1) |
| `PERSONA_BUDGET_WARNING` | No | Cost warning threshold in USD |
| `PERSONA_BUDGET_LIMIT` | No | Maximum cost limit in USD |

## Security Best Practices

### Never Commit API Keys

Your `.env` file is already in `.gitignore`, but always verify:

```bash
# Check that .env is ignored
git check-ignore .env
# Should output: .env
```

### Use Environment-Specific Keys

Create separate API keys for:
- Development (rate-limited, lower quotas)
- Testing (dedicated test account)
- Production (full access)

### Rotate Keys Regularly

1. Create a new key in your provider's console
2. Update `.env` with the new key
3. Test with `persona check`
4. Revoke the old key

### Protect Your .env File

```bash
# Set restrictive permissions (Unix/macOS)
chmod 600 .env
```

## Verifying Configuration

### Check All Providers

```bash
persona check
```

Expected output:
```
✓ Anthropic: Configured (claude-sonnet-4-5-20250929)
✓ OpenAI: Configured (gpt-5-20250807)
✓ Google: Configured (gemini-3.0-pro)
✓ Ollama: Running (llama3:70b)
```

### Test a Specific Provider

```bash
persona check --provider anthropic
```

### Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `API key not found` | Missing environment variable | Check `.env` file exists and is loaded |
| `Invalid API key` | Incorrect or expired key | Verify key in provider console |
| `Rate limit exceeded` | Too many requests | Wait and retry, or upgrade plan |
| `Connection refused` | Network or Ollama not running | Check network/start Ollama |

## Using Multiple Providers

You can configure all providers and switch between them:

```bash
# Use default provider
persona generate --from my-data

# Override for specific generation
persona generate --from my-data --provider openai --model gpt-5

# Set default in experiment config
# experiments/my-experiment/config.yaml
generation:
  provider: anthropic
  model: claude-sonnet-4-5-20250929
```

## Cost Management

Set budget controls to prevent unexpected costs:

```bash
# In .env
PERSONA_BUDGET_WARNING=5.00
PERSONA_BUDGET_LIMIT=20.00
```

Persona will:
- Warn when estimated cost exceeds `BUDGET_WARNING`
- Refuse to run when estimated cost exceeds `BUDGET_LIMIT`

---

## Related Documentation

- [Model Cards](../reference/model-cards.md) - Model capabilities and pricing
- [Provider APIs](../reference/provider-apis.md) - API specifications
- [Configuration Reference](../reference/configuration-reference.md) - All configuration options
