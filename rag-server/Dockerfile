# Use Python 3.12 slim as base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_VERSION=0.1.25

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md LICENSE uv.lock ./
COPY src ./src

# Install dependencies using uv
RUN uv sync --frozen

# Create data directory for vector database
RUN mkdir -p /app/data/vector_db

# Default environment variables
ENV EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
    VECTOR_DB_PATH=/app/data/vector_db \
    LOG_LEVEL=INFO

# Expose port for HTTP mode
EXPOSE 8000

# Set entrypoint to allow both HTTP and stdio modes
ENTRYPOINT ["rag-mcp-server"]

# Default to HTTP mode if no arguments provided
CMD ["--mode", "http", "--host", "0.0.0.0", "--port", "8000"]
