# Docker Deployment Guide

## Quick Start

### Pull and Run

```bash
# Pull latest image
docker pull ghcr.io/boxpositron/markdown-vault:latest

# Run with minimal config
docker run -d \
  --name markdown-vault \
  -p 27123:27123 \
  -v $(pwd)/vault:/vault \
  -e MARKDOWN_VAULT_VAULT__PATH=/vault \
  -e MARKDOWN_VAULT_SECURITY__API_KEY=$(openssl rand -hex 32) \
  ghcr.io/boxpositron/markdown-vault:latest
```

### Available Tags

```bash
# Latest release
ghcr.io/boxpositron/markdown-vault:latest

# Specific version
ghcr.io/boxpositron/markdown-vault:0.0.1
ghcr.io/boxpositron/markdown-vault:0.0

# By commit SHA
ghcr.io/boxpositron/markdown-vault:main-abc1234
```

## Docker Compose

### Basic Setup

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  markdown-vault:
    image: ghcr.io/boxpositron/markdown-vault:latest
    container_name: markdown-vault
    ports:
      - "27123:27123"
    volumes:
      - ./vault:/vault
      - ./config:/config
      - ./certs:/certs
    environment:
      - MARKDOWN_VAULT_VAULT__PATH=/vault
      - MARKDOWN_VAULT_SECURITY__API_KEY=${API_KEY:-change-me}
      - MARKDOWN_VAULT_SERVER__HTTPS=true
      - MARKDOWN_VAULT_SECURITY__AUTO_GENERATE_CERT=true
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "https://localhost:27123/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Start

```bash
# Create .env file
echo "API_KEY=$(openssl rand -hex 32)" > .env

# Start service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## Configuration

### Environment Variables

All configuration can be passed via environment variables:

```bash
docker run -d \
  -e MARKDOWN_VAULT_SERVER__HOST=0.0.0.0 \
  -e MARKDOWN_VAULT_SERVER__PORT=27123 \
  -e MARKDOWN_VAULT_SERVER__HTTPS=true \
  -e MARKDOWN_VAULT_VAULT__PATH=/vault \
  -e MARKDOWN_VAULT_VAULT__AUTO_CREATE=true \
  -e MARKDOWN_VAULT_SECURITY__API_KEY=your-key \
  -e MARKDOWN_VAULT_SECURITY__AUTO_GENERATE_CERT=true \
  -e MARKDOWN_VAULT_LOGGING__LEVEL=INFO \
  ghcr.io/boxpositron/markdown-vault:latest
```

### Config File

Mount a config file:

```bash
docker run -d \
  -v $(pwd)/config.yaml:/config/config.yaml \
  ghcr.io/boxpositron/markdown-vault:latest
```

## Volumes

### Recommended Mounts

```bash
docker run -d \
  -v /path/to/vault:/vault \          # Your markdown vault
  -v /path/to/config:/config \        # Configuration files
  -v /path/to/certs:/certs \          # SSL certificates
  -v /path/to/logs:/logs \            # Application logs
  ghcr.io/boxpositron/markdown-vault:latest
```

## Production Deployment

### With SSL Certificates

```yaml
version: '3.8'

services:
  markdown-vault:
    image: ghcr.io/boxpositron/markdown-vault:latest
    ports:
      - "27123:27123"
    volumes:
      - /data/vaults/my-vault:/vault:ro  # Read-only vault
      - /etc/markdown-vault/config.yaml:/config/config.yaml:ro
      - /etc/ssl/certs/markdown-vault:/certs:ro
    environment:
      - MARKDOWN_VAULT_VAULT__PATH=/vault
      - MARKDOWN_VAULT_SECURITY__API_KEY=${API_KEY}
      - MARKDOWN_VAULT_SECURITY__CERT_PATH=/certs/server.crt
      - MARKDOWN_VAULT_SECURITY__KEY_PATH=/certs/server.key
      - MARKDOWN_VAULT_LOGGING__LEVEL=WARNING
    restart: always
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Behind Reverse Proxy (Nginx)

```yaml
version: '3.8'

services:
  markdown-vault:
    image: ghcr.io/boxpositron/markdown-vault:latest
    expose:
      - "27123"
    environment:
      - MARKDOWN_VAULT_SERVER__HTTPS=false  # SSL handled by nginx
      - MARKDOWN_VAULT_VAULT__PATH=/vault
      - MARKDOWN_VAULT_SECURITY__API_KEY=${API_KEY}
    networks:
      - internal

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/ssl/certs:/etc/ssl/certs:ro
    depends_on:
      - markdown-vault
    networks:
      - internal

networks:
  internal:
    driver: bridge
```

## Multi-Vault Setup

Run multiple instances for different vaults:

```yaml
version: '3.8'

services:
  vault-personal:
    image: ghcr.io/boxpositron/markdown-vault:latest
    ports:
      - "27123:27123"
    volumes:
      - /data/vaults/personal:/vault
    environment:
      - MARKDOWN_VAULT_VAULT__PATH=/vault
      - MARKDOWN_VAULT_SECURITY__API_KEY=${PERSONAL_API_KEY}

  vault-work:
    image: ghcr.io/boxpositron/markdown-vault:latest
    ports:
      - "27124:27123"
    volumes:
      - /data/vaults/work:/vault
    environment:
      - MARKDOWN_VAULT_VAULT__PATH=/vault
      - MARKDOWN_VAULT_SECURITY__API_KEY=${WORK_API_KEY}
```

## Building Custom Images

### From Source

```bash
# Clone repository
git clone https://github.com/boxpositron/markdown-vault.git
cd markdown-vault

# Build image
docker build -t markdown-vault:custom .

# Run custom build
docker run -d markdown-vault:custom
```

### With Custom Dependencies

Create `Dockerfile.custom`:

```dockerfile
FROM ghcr.io/boxpositron/markdown-vault:latest

# Install additional packages
RUN pip install --no-cache-dir your-extra-package

# Copy custom config
COPY custom-config.yaml /config/config.yaml
```

## Troubleshooting

### Check Container Logs

```bash
docker logs markdown-vault
docker logs -f markdown-vault  # Follow logs
```

### Access Container Shell

```bash
docker exec -it markdown-vault /bin/bash
```

### Verify Permissions

```bash
# Check vault directory permissions
docker exec markdown-vault ls -la /vault

# Fix permissions if needed
docker exec markdown-vault chmod -R u+w /vault
```

### Health Check

```bash
# Check if service is responding
curl -k https://localhost:27123/

# Check from inside container
docker exec markdown-vault curl -k https://localhost:27123/
```

## Security Best Practices

1. **Use Secret Management**
   ```bash
   # Docker Swarm secrets
   docker secret create api_key api_key.txt
   ```

2. **Run as Non-Root User**
   ```dockerfile
   FROM ghcr.io/boxpositron/markdown-vault:latest
   USER 1000:1000
   ```

3. **Read-Only Vault**
   ```bash
   -v /path/to/vault:/vault:ro
   ```

4. **Network Isolation**
   ```yaml
   networks:
     - internal  # No external access
   ```

## GitHub Container Registry

### Authentication

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Pull Private Images

```bash
docker pull ghcr.io/boxpositron/markdown-vault:latest
```

## Image Details

- **Base**: `python:3.10-slim`
- **Size**: ~200MB
- **Platforms**: `linux/amd64`, `linux/arm64`
- **Registry**: GitHub Container Registry (ghcr.io)
- **Auto-built**: On every git tag push

## Updates

### Automatic Updates (Watchtower)

```yaml
version: '3.8'

services:
  markdown-vault:
    image: ghcr.io/boxpositron/markdown-vault:latest
    labels:
      - "com.centurylinklabs.watchtower.enable=true"

  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    command: --interval 3600  # Check every hour
```

### Manual Update

```bash
# Pull latest
docker pull ghcr.io/boxpositron/markdown-vault:latest

# Recreate container
docker-compose up -d
```

## Links

- **Registry**: https://github.com/boxpositron/markdown-vault/pkgs/container/markdown-vault
- **Source**: https://github.com/boxpositron/markdown-vault
- **Issues**: https://github.com/boxpositron/markdown-vault/issues
