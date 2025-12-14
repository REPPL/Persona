# Provider APIs Reference

Technical specifications for LLM provider integrations.

## Overview

Persona supports four LLM providers:

| Provider | API Type | Authentication | Status |
|----------|----------|----------------|--------|
| [OpenAI](#openai) | REST | Bearer token | Supported |
| [Anthropic](#anthropic) | REST | API key header | Supported |
| [Google (Gemini)](#google-gemini) | REST | Query parameter | Supported |
| [Ollama](#ollama) | REST | None (local) | Supported |

---

## OpenAI

### Authentication

```bash
export OPENAI_API_KEY="sk-..."
```

**Header Format:**
```
Authorization: Bearer sk-...
```

### Endpoint

```
POST https://api.openai.com/v1/chat/completions
```

### Request Format

```json
{
  "model": "gpt-5-20250807",
  "messages": [
    {
      "role": "system",
      "content": "You are a UX researcher..."
    },
    {
      "role": "user",
      "content": "Generate personas from: ..."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 8192,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "personas",
      "strict": true,
      "schema": { ... }
    }
  }
}
```

### Response Format

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1734177600,
  "model": "gpt-5-20250807",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{ \"personas\": [...] }"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 1500,
    "completion_tokens": 2000,
    "total_tokens": 3500
  }
}
```

### Supported Models

| Model ID | Context | Input $/M | Output $/M |
|----------|---------|-----------|------------|
| `gpt-5-20250807` | 256K | $10.00 | $30.00 |
| `gpt-5-mini` | 128K | $2.50 | $7.50 |
| `gpt-5.2-20251201` | 256K | $12.00 | $36.00 |
| `gpt-4.5-turbo` | 128K | $5.00 | $15.00 |
| `gpt-4.1` | 128K | $2.00 | $6.00 |
| `gpt-4o` | 128K | $2.50 | $10.00 |
| `gpt-4o-mini` | 128K | $0.15 | $0.60 |
| `o4-mini` | 128K | $1.50 | $4.50 |

### Rate Limits

| Tier | Requests/min | Tokens/min |
|------|--------------|------------|
| Tier 1 | 500 | 30,000 |
| Tier 2 | 5,000 | 150,000 |
| Tier 3 | 5,000 | 600,000 |
| Tier 4 | 10,000 | 2,000,000 |

### Error Codes

| Code | Status | Description | Retry |
|------|--------|-------------|-------|
| `invalid_api_key` | 401 | Invalid or missing API key | No |
| `rate_limit_exceeded` | 429 | Too many requests | Yes (backoff) |
| `context_length_exceeded` | 400 | Input too long | No (reduce input) |
| `server_error` | 500 | OpenAI server error | Yes (backoff) |
| `model_not_found` | 404 | Model unavailable | No |

---

## Anthropic

### Authentication

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Header Format:**
```
x-api-key: sk-ant-...
anthropic-version: 2024-01-01
```

### Endpoint

```
POST https://api.anthropic.com/v1/messages
```

### Request Format

```json
{
  "model": "claude-opus-4-5-20251101",
  "max_tokens": 8192,
  "messages": [
    {
      "role": "user",
      "content": "Generate personas from: ..."
    }
  ],
  "system": "You are a UX researcher...",
  "temperature": 0.7
}
```

### Response Format

```json
{
  "id": "msg_...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "{ \"personas\": [...] }"
    }
  ],
  "model": "claude-opus-4-5-20251101",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 1500,
    "output_tokens": 2000
  }
}
```

### Supported Models

| Model ID | Context | Input $/M | Output $/M |
|----------|---------|-----------|------------|
| `claude-opus-4-5-20251101` | 200K | $15.00 | $75.00 |
| `claude-sonnet-4-5-20250929` | 200K (1M beta) | $3.00 | $15.00 |
| `claude-opus-4-1-20250805` | 200K | $15.00 | $75.00 |
| `claude-sonnet-4-20250514` | 200K | $3.00 | $15.00 |
| `claude-haiku-3-5-20241022` | 200K | $0.80 | $4.00 |
| `claude-3-opus-20240229` | 200K | $15.00 | $75.00 |
| `claude-3-sonnet-20240229` | 200K | $3.00 | $15.00 |
| `claude-3-haiku-20240307` | 200K | $0.25 | $1.25 |

### Rate Limits

| Tier | Requests/min | Input tokens/min | Output tokens/min |
|------|--------------|------------------|-------------------|
| Tier 1 | 50 | 40,000 | 8,000 |
| Tier 2 | 1,000 | 80,000 | 16,000 |
| Tier 3 | 2,000 | 160,000 | 32,000 |
| Tier 4 | 4,000 | 400,000 | 80,000 |

### Error Codes

| Code | Status | Description | Retry |
|------|--------|-------------|-------|
| `authentication_error` | 401 | Invalid API key | No |
| `rate_limit_error` | 429 | Rate limit exceeded | Yes (backoff) |
| `overloaded_error` | 529 | API overloaded | Yes (backoff) |
| `invalid_request_error` | 400 | Malformed request | No |
| `api_error` | 500 | Server error | Yes (backoff) |

---

## Google (Gemini)

### Authentication

```bash
export GOOGLE_API_KEY="AIza..."
```

**Query Parameter:**
```
?key=AIza...
```

### Endpoint

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}
```

### Request Format

```json
{
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "Generate personas from: ..."
        }
      ]
    }
  ],
  "systemInstruction": {
    "parts": [
      {
        "text": "You are a UX researcher..."
      }
    ]
  },
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 8192,
    "responseMimeType": "application/json"
  }
}
```

### Response Format

```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "{ \"personas\": [...] }"
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP"
    }
  ],
  "usageMetadata": {
    "promptTokenCount": 1500,
    "candidatesTokenCount": 2000,
    "totalTokenCount": 3500
  }
}
```

### Supported Models

| Model ID | Context | Input $/M | Output $/M |
|----------|---------|-----------|------------|
| `gemini-3.0-pro` | 2M | $1.25 | $5.00 |
| `gemini-3.0-deep-think` | 2M | $2.50 | $10.00 |
| `gemini-2.5-pro` | 2M | $1.00 | $4.00 |
| `gemini-2.5-flash` | 1M | $0.075 | $0.30 |
| `gemini-2.5-flash-lite` | 1M | $0.02 | $0.08 |
| `gemini-1.5-pro` | 2M | $1.25 | $5.00 |
| `gemini-1.5-flash` | 1M | $0.075 | $0.30 |

### Rate Limits

| Model | Requests/min | Tokens/min |
|-------|--------------|------------|
| Gemini 3.0 Pro | 60 | 60,000 |
| Gemini 3.0 Deep Think | 15 | 15,000 |
| Gemini 2.5 Pro | 60 | 60,000 |
| Gemini 2.5 Flash | 1,000 | 1,000,000 |
| Gemini 2.5 Flash-Lite | 2,000 | 4,000,000 |

### Error Codes

| Code | Status | Description | Retry |
|------|--------|-------------|-------|
| `INVALID_ARGUMENT` | 400 | Invalid request | No |
| `PERMISSION_DENIED` | 403 | Invalid API key | No |
| `RESOURCE_EXHAUSTED` | 429 | Rate limit exceeded | Yes (backoff) |
| `INTERNAL` | 500 | Server error | Yes (backoff) |
| `UNAVAILABLE` | 503 | Service unavailable | Yes (backoff) |

---

## Ollama

### Overview

Ollama provides local LLM inference. No API key required.

### Endpoint

```
POST http://localhost:11434/api/chat
```

### Request Format

```json
{
  "model": "llama3:70b",
  "messages": [
    {
      "role": "system",
      "content": "You are a UX researcher..."
    },
    {
      "role": "user",
      "content": "Generate personas from: ..."
    }
  ],
  "stream": false,
  "options": {
    "temperature": 0.7,
    "num_predict": 8192
  }
}
```

### Response Format

```json
{
  "model": "llama3:70b",
  "created_at": "2025-12-14T10:30:00Z",
  "message": {
    "role": "assistant",
    "content": "{ \"personas\": [...] }"
  },
  "done": true,
  "total_duration": 15000000000,
  "prompt_eval_count": 1500,
  "eval_count": 2000
}
```

### Supported Models

| Model ID | Parameters | RAM Required | Context |
|----------|------------|--------------|---------|
| `llama3:70b` | 70B | 48GB+ | 8K |
| `llama3:8b` | 8B | 8GB+ | 8K |
| `llama3.2:3b` | 3B | 4GB+ | 128K |
| `mistral:7b` | 7B | 8GB+ | 32K |
| `mixtral:8x7b` | 47B | 32GB+ | 32K |
| `qwen2.5:72b` | 72B | 48GB+ | 128K |

### Configuration

```yaml
# ~/.persona/config.yaml
provider:
  ollama:
    base_url: http://localhost:11434
    model: llama3:70b
    keep_alive: 5m  # Keep model in memory
```

### Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Connection refused | Ollama not running | Start Ollama: `ollama serve` |
| Model not found | Model not pulled | Pull model: `ollama pull llama3:70b` |
| Out of memory | Insufficient RAM | Use smaller model |

---

## Common Retry Strategy

Persona implements exponential backoff for retryable errors:

```python
# Retry configuration
max_retries = 3
base_delay = 1.0  # seconds
max_delay = 60.0  # seconds

for attempt in range(max_retries):
    try:
        response = call_api()
        break
    except RetryableError:
        delay = min(base_delay * (2 ** attempt), max_delay)
        delay *= (0.5 + random())  # Jitter
        sleep(delay)
```

### Retryable vs Non-Retryable

| Retryable | Non-Retryable |
|-----------|---------------|
| Rate limit (429) | Authentication (401) |
| Server error (500, 502, 503) | Invalid request (400) |
| Timeout | Context too long |
| Overloaded (529) | Model not found (404) |

---

## Structured Output

Persona uses provider-specific mechanisms for JSON output:

| Provider | Method |
|----------|--------|
| OpenAI | `response_format.json_schema` |
| Anthropic | System prompt + Instructor library |
| Google | `responseMimeType: application/json` |
| Ollama | System prompt + JSON mode |

---

## Related Documentation

- [Model Cards](model-cards.md) - Model capabilities and pricing
- [Configuration Reference](configuration-reference.md) - Configuration options
- [F-002: LLM Provider Abstraction](../development/roadmap/features/completed/F-002-llm-provider-abstraction.md)
- [F-011: Multi-Provider Support](../development/roadmap/features/completed/F-011-multi-provider-llm-support.md)

