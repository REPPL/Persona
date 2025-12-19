# Deployment Guide

This guide covers deploying Persona for team and production environments.

## Deployment Options

| Option | Best For | Complexity |
|--------|----------|------------|
| Direct Install | Single user, development | Low |
| Virtual Environment | Team development | Low |
| Docker Container | Production, isolation | Medium |
| Docker Compose | Multi-service deployment | Medium |
| Kubernetes | Enterprise, scaling | High |

---

## Quick Start: Docker Deployment

```bash
# Build the image
docker build -t persona:latest .

# Run with API key
docker run -d \
  --name persona \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  persona:latest serve --host 0.0.0.0

# Verify
curl http://localhost:8000/api/v1/health
```

---

## Direct Installation

### System Requirements

- Python 3.12 or higher
- 2GB RAM minimum (4GB recommended)
- 500MB disk space

### Installation Steps

```bash
# Clone repository
git clone https://github.com/REPPL/Persona.git
cd Persona

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install with all dependencies
pip install -e ".[all]"

# Verify installation
persona check
```

### Environment Configuration

Create a `.env` file:

```bash
# Required: At least one provider
ANTHROPIC_API_KEY=sk-ant-your-key
OPENAI_API_KEY=sk-your-key
GOOGLE_API_KEY=AIza-your-key

# Optional: Defaults
PERSONA_DEFAULT_PROVIDER=anthropic
PERSONA_LOG_LEVEL=INFO

# Optional: Budget controls
PERSONA_BUDGET_WARNING=5.00
PERSONA_BUDGET_LIMIT=20.00

# Optional: API server
PERSONA_API_AUTH_TOKEN=your-secret-token
```

---

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install persona with API support
RUN pip install --no-cache-dir -e ".[api]"

# Create non-root user
RUN useradd -m -u 1000 persona
USER persona

# Default environment
ENV PERSONA_LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command: start API server
EXPOSE 8000
CMD ["persona", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

### Building and Running

```bash
# Build image
docker build -t persona:latest .

# Run container
docker run -d \
  --name persona-api \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e PERSONA_API_AUTH_TOKEN="your-secret" \
  persona:latest

# View logs
docker logs -f persona-api

# Stop container
docker stop persona-api
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  persona:
    build: .
    container_name: persona-api
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - PERSONA_API_AUTH_TOKEN=${PERSONA_API_AUTH_TOKEN}
      - PERSONA_LOG_LEVEL=INFO
    volumes:
      - persona-data:/app/data
      - persona-output:/app/output
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Ollama for local models
  ollama:
    image: ollama/ollama:latest
    container_name: persona-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-models:/root/.ollama
    restart: unless-stopped

volumes:
  persona-data:
  persona-output:
  ollama-models:
```

Usage:

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f persona

# Stop services
docker-compose down
```

---

## Production Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `GOOGLE_API_KEY` | Google AI API key | - |
| `PERSONA_DEFAULT_PROVIDER` | Default LLM provider | anthropic |
| `PERSONA_LOG_LEVEL` | Log level (DEBUG, INFO, WARNING, ERROR) | INFO |
| `PERSONA_API_HOST` | API server host | 127.0.0.1 |
| `PERSONA_API_PORT` | API server port | 8000 |
| `PERSONA_API_WORKERS` | Number of worker processes | 1 |
| `PERSONA_API_AUTH_ENABLED` | Enable authentication | false |
| `PERSONA_API_AUTH_TOKEN` | API authentication token | - |
| `PERSONA_BUDGET_WARNING` | Cost warning threshold (USD) | - |
| `PERSONA_BUDGET_LIMIT` | Maximum cost limit (USD) | - |

### Security Best Practices

1. **Never expose API keys in images**
   ```bash
   # Good: Use environment variables
   docker run -e ANTHROPIC_API_KEY="$KEY" persona

   # Bad: Baked into image
   ENV ANTHROPIC_API_KEY=sk-ant-... # DON'T DO THIS
   ```

2. **Enable authentication for production**
   ```bash
   docker run \
     -e PERSONA_API_AUTH_TOKEN="strong-random-token" \
     persona serve --host 0.0.0.0
   ```

3. **Use secrets management**
   ```yaml
   # docker-compose.yml with Docker secrets
   services:
     persona:
       secrets:
         - anthropic_key
       environment:
         - ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_key

   secrets:
     anthropic_key:
       external: true
   ```

4. **Run as non-root user**
   ```dockerfile
   RUN useradd -m -u 1000 persona
   USER persona
   ```

5. **Limit network exposure**
   ```yaml
   # Only expose to internal network
   ports:
     - "127.0.0.1:8000:8000"
   ```

### Reverse Proxy with Nginx

```nginx
upstream persona {
    server 127.0.0.1:8000;
}

server {
    listen 443 ssl;
    server_name persona.example.com;

    ssl_certificate /etc/ssl/certs/persona.crt;
    ssl_certificate_key /etc/ssl/private/persona.key;

    location / {
        proxy_pass http://persona;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-running generation
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /api/v1/health {
        proxy_pass http://persona;
        access_log off;
    }
}
```

---

## Scaling

### Horizontal Scaling with Workers

```bash
# Multiple workers in single container
persona serve --host 0.0.0.0 --workers 4
```

### Load Balancing with Docker Compose

```yaml
version: '3.8'

services:
  persona:
    build: .
    deploy:
      replicas: 3
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - persona
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: persona
spec:
  replicas: 3
  selector:
    matchLabels:
      app: persona
  template:
    metadata:
      labels:
        app: persona
    spec:
      containers:
      - name: persona
        image: persona:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: persona-secrets
              key: anthropic-api-key
        - name: PERSONA_API_AUTH_TOKEN
          valueFrom:
            secretKeyRef:
              name: persona-secrets
              key: api-auth-token
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: persona
spec:
  selector:
    app: persona
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

---

## Monitoring

### Health Checks

```bash
# CLI health check
persona check

# API health check
curl http://localhost:8000/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.9.6",
  "timestamp": "2025-12-19T10:30:00Z"
}
```

### Logging

Configure log level:

```bash
# Environment variable
export PERSONA_LOG_LEVEL=DEBUG

# CLI option
persona serve --log-level debug
```

**Log levels:**
- `DEBUG` - Detailed debugging information
- `INFO` - General operational information
- `WARNING` - Warning messages
- `ERROR` - Error messages only

### Metrics (Prometheus)

The API exposes metrics at `/metrics` when enabled:

```bash
persona serve --metrics
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs persona-api

# Common issues:
# - Missing API key: Set ANTHROPIC_API_KEY
# - Port conflict: Change -p 8000:8000 to another port
# - Permission denied: Check volume permissions
```

### API Returns 401 Unauthorised

```bash
# Ensure auth token matches
curl -H "Authorization: Bearer your-token" \
  http://localhost:8000/api/v1/generate
```

### High Memory Usage

```bash
# Limit container memory
docker run -m 2g persona serve

# Reduce workers
persona serve --workers 1
```

### Slow Response Times

1. Check LLM provider status
2. Reduce persona count
3. Use faster models (e.g., `gpt-4o-mini` vs `gpt-4o`)
4. Enable caching for repeated requests

---

## Related Documentation

- [REST API Reference](rest-api.md) - API endpoints and usage
- [API Key Setup](api-key-setup.md) - Provider configuration
- [Advanced Features](advanced-features.md) - Server commands
- [CI/CD Integration](ci-cd-integration.md) - Pipeline integration
