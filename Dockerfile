# ClearCraft Dockerfile
# Production-ready container for text clarity enhancement

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app user
RUN groupadd -r clearcraft && useradd -r -g clearcraft clearcraft

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY clearcraft/ ./clearcraft/
COPY rules/ ./rules/
COPY templates/ ./templates/
COPY static/ ./static/
COPY pyproject.toml .
COPY README.md .

# Create cache directories
RUN mkdir -p .cache/huggingface .cache/sentence-transformers && \
    chown -R clearcraft:clearcraft /app

# Switch to app user
USER clearcraft

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Run server
CMD ["python", "-m", "uvicorn", "clearcraft.server:app", "--host", "0.0.0.0", "--port", "8000"]
