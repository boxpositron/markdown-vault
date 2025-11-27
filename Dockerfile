FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Create directories for vault, config, and certs
RUN mkdir -p /vault /config /certs /logs

# Expose default port
EXPOSE 27123

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["markdown-vault", "start", "--config", "/config/config.yaml"]
