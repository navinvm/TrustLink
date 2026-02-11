# TrustLink Dockerfile - Production-ready containerization
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app user
RUN groupadd -r trustlink && useradd -r -g trustlink trustlink

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=trustlink:trustlink . .

# Initialize models during build
RUN python init_models.py

# Create necessary directories
RUN mkdir -p /app/models /app/logs && \
    chown -R trustlink:trustlink /app

# Switch to non-root user
USER trustlink

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["gunicorn", "wsgi:application", "--config", "gunicorn_config.py", "--preload"]
