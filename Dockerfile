# Persona Production Dockerfile
# Multi-stage build for minimal image size
#
# Build: docker build -t persona:latest .
# Run:   docker run -p 8000:8000 -e ANTHROPIC_API_KEY=sk-... persona:latest

# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only what's needed for install
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Build wheel
RUN pip wheel --no-cache-dir --wheel-dir /wheels -e ".[api]"

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install wheels from builder
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels

# Create non-root user
RUN useradd --create-home --shell /bin/bash --uid 1000 persona
USER persona

# Create directories for data and output
RUN mkdir -p /app/data /app/output

# Environment configuration
ENV PERSONA_LOG_LEVEL=INFO
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose API port
EXPOSE 8000

# Default command: start API server
CMD ["persona", "serve", "--host", "0.0.0.0", "--port", "8000"]
