# markdown-vault

A production-ready REST API server for markdown vault management with comprehensive search, automation, and optional Obsidian compatibility. Built for CI/CD pipelines, cloud deployments, and programmatic markdown workflows.

[![PyPI version](https://img.shields.io/pypi/v/markdown-vault.svg)](https://pypi.org/project/markdown-vault/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue)](https://github.com/boxpositron/markdown-vault/pkgs/container/markdown-vault)

## Overview

**markdown-vault** is a standalone HTTP service providing a secure REST API for managing markdown files and vaults. Perfect for automation tools, CI/CD pipelines, or programmatic note access.

**What it is**: Independent REST API server for markdown vault operations  
**What it's not**: Not an Obsidian plugin - runs as a standalone service with optional Obsidian vault support

### Key Features

- **Full CRUD Operations** - Create, read, update, delete markdown files via REST API
- **Advanced PATCH** - Targeted updates with heading/block/frontmatter selectors
- **Periodic Notes** - Daily, weekly, monthly, quarterly, yearly note support
- **Powerful Search** - Text search and JSONLogic-based complex queries
- **Secure by Default** - HTTPS with API key authentication
- **Production Ready** - Docker support, 24/7 availability, cloud-native
- **Obsidian Compatible** - API-compatible with Obsidian Local REST API plugin

## Quick Start

### Installation

**Using uvx (Recommended - No Installation Required)**
```bash
uvx markdown-vault start --reload
```

**Using pip**
```bash
pip install markdown-vault
markdown-vault start --reload
```

**Using uv (Development)**
```bash
git clone https://github.com/boxpositron/markdown-vault.git
cd markdown-vault
uv venv && uv sync
uv run markdown-vault start --reload
```

**Using Docker (from GitHub Container Registry)**
```bash
docker run -d \
  -p 27123:27123 \
  -v /path/to/vault:/vault \
  -e MARKDOWN_VAULT_VAULT__PATH=/vault \
  -e MARKDOWN_VAULT_SECURITY__API_KEY=your-key \
  ghcr.io/boxpositron/markdown-vault:latest
```

### Configuration

**Method 1: Config File**

Create `config.yaml`:
```yaml
server:
  host: "127.0.0.1"
  port: 27123
  https: true

vault:
  path: "/path/to/your/vault"
  auto_create: true

security:
  api_key: "your-secure-api-key-here"
  auto_generate_cert: true
```

**Method 2: Environment Variables**
```bash
export MARKDOWN_VAULT_SERVER__PORT=27123
export MARKDOWN_VAULT_VAULT__PATH=/path/to/vault
export MARKDOWN_VAULT_SECURITY__API_KEY=your-key
markdown-vault start
```

**Method 3: CLI Flags**
```bash
markdown-vault start --config config.yaml --reload
```

### First Run

```bash
# Generate an API key
markdown-vault generate-key

# Start with auto-generated cert
markdown-vault start --reload

# Access API docs
open https://localhost:27123/docs
```

## API Documentation

Visit `https://localhost:27123/docs` for interactive Swagger documentation.

### Core Endpoints

```
# Vault Operations
GET    /vault/{filepath}        # Read file
PUT    /vault/{filepath}        # Create/update
POST   /vault/{filepath}        # Append
PATCH  /vault/{filepath}        # Targeted update
DELETE /vault/{filepath}        # Delete
GET    /vault/                  # List files

# Periodic Notes
GET    /periodic/daily/         # Get today's note
GET    /periodic/weekly/        # Get this week's note
GET    /periodic/monthly/       # Get this month's note
PUT    /periodic/daily/         # Update today's note
POST   /periodic/daily/         # Append to today's note

# Search
POST   /search/simple/          # Text search
POST   /search/                 # JSONLogic search

# System
GET    /                        # Server status
GET    /_/server/status         # Detailed status
```

### Authentication

All requests require an API key:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://localhost:27123/vault/note.md
```

## Advanced Features

### PATCH Operations

**Heading Targeting**
```bash
# Append under specific heading
curl -X PATCH https://localhost:27123/vault/note.md \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Operation: append" \
  -H "Target-Type: heading" \
  -H "Target: Main Heading::Sub Heading:1" \
  -d "New content"
```

**Block Reference**
```bash
# Update at block reference
curl -X PATCH https://localhost:27123/vault/note.md \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Operation: replace" \
  -H "Target-Type: block" \
  -H "Target: ^abc123" \
  -d "Updated content"
```

**Frontmatter**
```bash
# Update YAML frontmatter
curl -X PATCH https://localhost:27123/vault/note.md \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Operation: replace" \
  -H "Target-Type: frontmatter" \
  -H "Target: tags" \
  -H "Content-Type: application/json" \
  -d '["new", "tags"]'
```

### Search Examples

**Simple Text Search**
```bash
curl -X POST https://localhost:27123/search/simple/ \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "search term"}'
```

**Complex JSONLogic Search**
```bash
curl -X POST https://localhost:27123/search/ \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "and": [
        {"in": ["tag1", {"var": "frontmatter.tags"}]},
        {">=": [{"var": "frontmatter.priority"}, 5]}
      ]
    }
  }'
```

## Development

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Setup

```bash
# Clone repository
git clone https://github.com/boxpositron/markdown-vault.git
cd markdown-vault

# Install with uv (recommended)
uv venv
uv sync
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Or install with pip
pip install -e ".[dev]"
```

### Development Commands

```bash
# Run tests
make local-test                    # or: uv run pytest
make local-test-cov               # with coverage

# Code quality
make local-lint                    # ruff linting
make local-format                  # black formatting
make local-typecheck              # mypy type checking
make local-typecheck-pyright      # pyright type checking

# Run all QA checks
make local-qa                      # lint + format + typecheck + test

# Run server
make local-run                     # or: uv run markdown-vault start --reload
```

### Project Structure

```
markdown-vault/
├── src/markdown_vault/
│   ├── api/              # FastAPI routes and dependencies
│   ├── core/             # Business logic (vault, search, patch)
│   ├── models/           # Pydantic models
│   └── utils/            # Utilities (crypto, dates)
├── tests/                # 351 tests, 86% coverage
├── docs/                 # Additional documentation
├── config/               # Example configurations
└── examples/             # Usage examples
```

## Configuration Reference

### Server Configuration

```yaml
server:
  host: "127.0.0.1"          # Bind address
  port: 27123                 # Port number
  https: true                 # Enable HTTPS
  reload: false               # Auto-reload on changes (dev only)
```

### Vault Configuration

```yaml
vault:
  path: "/path/to/vault"      # Vault directory (required)
  auto_create: true            # Create directory if missing
  watch_files: false           # Watch for file changes
  respect_gitignore: true      # Honor .gitignore files
```

### Security Configuration

```yaml
security:
  api_key: "your-key"          # API authentication key
  cert_path: "./certs/server.crt"
  key_path: "./certs/server.key"
  auto_generate_cert: true     # Generate self-signed cert
```

### Periodic Notes

```yaml
periodic_notes:
  daily:
    enabled: true
    format: "YYYY-MM-DD"
    folder: "daily"
    template: "templates/daily.md"
  weekly:
    enabled: true
    format: "YYYY-[W]WW"
    folder: "weekly"
  monthly:
    enabled: true
    format: "YYYY-MM"
    folder: "monthly"
```

### Logging

```yaml
logging:
  level: "INFO"                # DEBUG, INFO, WARNING, ERROR
  format: "json"               # json or text
  file: null                   # Log file path (optional)
```

## Deployment

### Docker Compose

```yaml
version: '3.8'
services:
  markdown-vault:
    image: ghcr.io/boxpositron/markdown-vault:latest
    ports:
      - "27123:27123"
    volumes:
      - ./vault:/vault
      - ./config.yaml:/app/config.yaml
    environment:
      - MARKDOWN_VAULT_VAULT__PATH=/vault
      - MARKDOWN_VAULT_SECURITY__API_KEY=${API_KEY}
    restart: unless-stopped
```

### Systemd Service

```ini
[Unit]
Description=Markdown Vault REST API
After=network.target

[Service]
Type=simple
User=markdown
WorkingDirectory=/opt/markdown-vault
Environment="MARKDOWN_VAULT_VAULT__PATH=/data/vault"
Environment="MARKDOWN_VAULT_SECURITY__API_KEY=your-key"
ExecStart=/opt/markdown-vault/.venv/bin/markdown-vault start
Restart=always

[Install]
WantedBy=multi-user.target
```

### Environment Variables

All configuration can be set via environment variables with the prefix `MARKDOWN_VAULT_`:

```bash
MARKDOWN_VAULT_SERVER__HOST=0.0.0.0
MARKDOWN_VAULT_SERVER__PORT=8080
MARKDOWN_VAULT_SERVER__HTTPS=false
MARKDOWN_VAULT_VAULT__PATH=/data/vault
MARKDOWN_VAULT_SECURITY__API_KEY=your-secure-key
MARKDOWN_VAULT_LOGGING__LEVEL=DEBUG
```

## Obsidian Compatibility

markdown-vault is **fully compatible** with the Obsidian Local REST API plugin, allowing you to:

- Access Obsidian vaults via API without the desktop app running
- Use existing Obsidian-aware tools and integrations
- Deploy Obsidian vault access to servers
- Access multiple Obsidian vaults simultaneously

### Configuration for Obsidian

```yaml
vault:
  path: "/Users/you/Documents/MyObsidianVault"

obsidian:
  enabled: true               # Respect .obsidian/ directory
  config_sync: true           # Read Obsidian's periodic notes config
```

### API Endpoints

Uses the same default port (27123) and endpoints as the Obsidian plugin:
- Compatible with all Obsidian Local REST API clients
- Drop-in replacement for automation scripts
- Works whether Obsidian is running or not

## Use Cases

- **CI/CD Integration** - Auto-update documentation in build pipelines
- **Cloud Automation** - Run as microservice for markdown workflows
- **Content Management** - Headless CMS for markdown content
- **Knowledge Base API** - REST API for documentation systems
- **Script Integration** - Programmatic notes from any language
- **Obsidian Automation** - API access without desktop dependency
- **Multi-Vault Management** - Access multiple vaults concurrently

## Testing

```bash
# Run all tests
make local-test

# With coverage
make local-test-cov

# Single test file
uv run pytest tests/test_vault.py -v

# Single test
uv run pytest tests/test_vault.py::test_create_file -v

# Watch mode (requires pytest-watch)
pytest-watch
```

**Test Stats**: 351 tests, 86% coverage

## Troubleshooting

### SSL Certificate Issues

```bash
# Generate new self-signed certificate
markdown-vault start --generate-cert

# Use HTTP instead (development only)
markdown-vault start --no-https
```

### Permission Errors

```bash
# Ensure vault directory is writable
chmod -R u+w /path/to/vault

# Or set auto_create in config
vault:
  auto_create: true
```

### Port Already in Use

```bash
# Use different port
markdown-vault start --port 8080

# Or set in config
server:
  port: 8080
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run QA checks (`make local-qa`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Publishing & Releases

This project uses automated publishing with **OIDC Trusted Publishing** for security and convenience.

### For Maintainers: Setting Up PyPI Trusted Publishing

**One-time setup** (requires PyPI account with project ownership):

1. **Go to PyPI Project Settings**
   - Visit: https://pypi.org/manage/project/markdown-vault/settings/publishing/
   - Or create pending publisher: https://pypi.org/manage/account/publishing/

2. **Add GitHub as Trusted Publisher**
   - **PyPI Project Name**: `markdown-vault`
   - **Owner**: `boxpositron`
   - **Repository name**: `markdown-vault`
   - **Workflow name**: `pypi-publish.yml`
   - **Environment name**: `pypi` (optional but recommended)

3. **Repeat for TestPyPI** (for testing)
   - Visit: https://test.pypi.org/manage/account/publishing/
   - Use same settings but with environment name: `testpypi`

### Creating a Release

Releases are fully automated via GitHub Actions:

```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.0.2"

# 4. Create and push tag
git tag v0.0.2
git push origin main --tags

# 5. Create GitHub Release (triggers publishing)
gh release create v0.0.2 \
  --title "v0.0.2" \
  --notes "See CHANGELOG.md for details" \
  dist/*.whl dist/*.tar.gz
```

This automatically:
- ✅ Builds Docker images (multi-platform: amd64/arm64)
- ✅ Pushes to `ghcr.io/boxpositron/markdown-vault`
- ✅ Publishes to TestPyPI (for verification)
- ✅ Publishes to PyPI (production)
- ✅ Generates SBOM and provenance attestations

### Manual Publishing (Alternative)

If you need to publish manually:

```bash
# Build the package
uv build

# Publish using trusted publishing (no token needed!)
uv publish

# Or publish to TestPyPI first
uv publish --publish-url https://test.pypi.org/legacy/
```

**Note**: Manual publishing still uses OIDC when run from GitHub Actions, or requires API token when run locally.

### Verification

After publishing, verify the release:

```bash
# Test PyPI installation
pip install markdown-vault==0.0.2

# Test Docker image
docker pull ghcr.io/boxpositron/markdown-vault:0.0.2

# Verify attestations
docker buildx imagetools inspect ghcr.io/boxpositron/markdown-vault:0.0.2
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Author

**David Ibia** - [pypi@boxpositron.dev](mailto:pypi@boxpositron.dev)

## Credits

API compatibility with [Obsidian Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin by [@coddingtonbear](https://github.com/coddingtonbear).

[Obsidian](https://obsidian.md) is a trademark of Dynalist Inc. This project is independent and not affiliated with Obsidian or Dynalist Inc.

## Links

- **Repository**: https://github.com/boxpositron/markdown-vault
- **Issues**: https://github.com/boxpositron/markdown-vault/issues
- **PyPI**: https://pypi.org/project/markdown-vault/
- **Docker**: https://github.com/boxpositron/markdown-vault/pkgs/container/markdown-vault
