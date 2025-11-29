# markdown-vault

A REST API server for markdown vaults with comprehensive vault management, search, and automation capabilities. Built for CI/CD pipelines, cloud deployments, and programmatic markdown workflows with optional Obsidian compatibility.

## Overview

**markdown-vault** is a standalone HTTP service that provides a secure REST API for managing markdown files and vaults. Whether you're building automation tools, integrating markdown into your CI/CD pipeline, or need programmatic access to your notes, markdown-vault provides a robust, production-ready solution.

**What it is**: An independent REST API server for markdown vault operations
**What it's not**: Not an Obsidian plugin - runs as a standalone service with optional Obsidian vault support

### Operating Modes

1. **Standalone Mode**: Manage any markdown vault independently with full API control
2. **Obsidian Compatibility Mode**: Point it at an Obsidian vault for API-compatible access to existing vaults

## Key Features

### Core Capabilities
- **Full CRUD Operations**: Create, read, update, and delete markdown files via REST API
- **Advanced PATCH Operations**: Targeted updates with heading, block reference, and frontmatter selectors
- **Periodic Notes**: Built-in support for daily, weekly, monthly, quarterly, and yearly notes
- **Search Engine**: Simple text search and complex JSONLogic-based queries
- **Vault Management**: File listing, metadata access, and vault-wide operations

### Production Ready
- **Secure by Default**: HTTPS with API key authentication
- **Always Available**: 24/7 service independent of desktop applications
- **Docker Support**: Container images for easy deployment
- **Cloud Native**: Deploy to any server, container platform, or cloud provider
- **High Performance**: Dedicated service optimized for API operations
- **Concurrent Access**: Manage multiple vaults simultaneously

### Extensibility
- **Clean API Design**: RESTful endpoints with comprehensive OpenAPI documentation
- **Flexible Configuration**: YAML-based configuration with environment variable support
- **Format Support**: JSON and Markdown response formats
- **Webhook Ready**: Architecture designed for easy feature additions

## Use Cases

- **CI/CD Integration**: Automate documentation updates in your build pipeline
- **Cloud Automation**: Run as a microservice for markdown-based workflows
- **Script Integration**: Programmatic note creation and updates from any language
- **Content Management**: Headless CMS for markdown-based content
- **Knowledge Base API**: REST API for documentation and wiki systems
- **Development Tools**: Backend for markdown editor integrations
- **Obsidian Automation**: API access to Obsidian vaults without desktop dependency

## Quick Start

### Installation

```bash
# Using pip (when available)
pip install markdown-vault

# Using Docker
docker pull markdown-vault:latest

# From source
git clone https://github.com/yourusername/markdown-vault.git
cd markdown-vault
pip install -e .
```

### Configuration

Create a `config.yaml`:

```yaml
server:
  host: "127.0.0.1"
  port: 27123
  https: true

vault:
  path: "/path/to/your/vault"
  
security:
  api_key: "your-api-key-here"
```

### Running

```bash
# Start the server
markdown-vault start --config config.yaml

# Generate an API key
markdown-vault generate-key

# Initialize a new vault configuration
markdown-vault init --vault /path/to/vault
```

## API Documentation

Once running, visit `https://localhost:27123/docs` for interactive API documentation.

### Core Endpoints

```
# Vault Operations
GET    /vault/{filepath}        # Read file
PUT    /vault/{filepath}        # Create/update file
POST   /vault/{filepath}        # Append to file
PATCH  /vault/{filepath}        # Partial update
DELETE /vault/{filepath}        # Delete file
GET    /vault/                  # List files

# Active File (Obsidian compatibility)
GET    /active/                 # Get currently active file
PUT    /active/                 # Update active file
POST   /active/                 # Append to active file
PATCH  /active/                 # Partial update
DELETE /active/                 # Delete active file

# Periodic Notes
GET    /periodic/{period}/      # Get periodic note
PUT    /periodic/{period}/      # Update periodic note
POST   /periodic/{period}/      # Append to periodic note
PATCH  /periodic/{period}/      # Partial update
DELETE /periodic/{period}/      # Delete periodic note

# Search
POST   /search/simple/          # Simple text search
POST   /search/                 # Complex JSONLogic search
```

## PATCH Operations

Advanced content targeting for precise updates:

### Heading Targeting
```bash
# Append content under a specific heading
curl -X PATCH https://localhost:27123/vault/note.md \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Operation: append" \
  -H "Target-Type: heading" \
  -H "Target: Heading 1::Subheading 1:1" \
  -d "New content here"
```

### Block Reference Targeting
```bash
# Update content at a block reference
curl -X PATCH https://localhost:27123/vault/note.md \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Operation: replace" \
  -H "Target-Type: block" \
  -H "Target: ^abc123" \
  -d "Updated content"
```

### Frontmatter Targeting
```bash
# Update YAML frontmatter field
curl -X PATCH https://localhost:27123/vault/note.md \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Operation: replace" \
  -H "Target-Type: frontmatter" \
  -H "Target: tags" \
  -H "Content-Type: application/json" \
  -d '["tag1", "tag2", "tag3"]'
```

## Response Formats

### Markdown Format
```bash
curl -H "Accept: text/markdown" https://localhost:27123/vault/note.md
```

### JSON Format (with metadata)
```bash
curl -H "Accept: application/vnd.olrapi.note+json" \
  https://localhost:27123/vault/note.md
```

Returns:
```json
{
  "path": "note.md",
  "content": "# My Note\n\nContent here",
  "frontmatter": {
    "tags": ["note"],
    "date": "2025-01-01"
  },
  "tags": ["#inline-tag"],
  "stat": {
    "ctime": 1234567890,
    "mtime": 1234567891,
    "size": 1024
  }
}
```

## Working with Obsidian Vaults

markdown-vault provides **full API compatibility** with the Obsidian Local REST API plugin, making it easy to work with existing Obsidian vaults or integrate with Obsidian-aware tools.

### Configuration for Obsidian Vaults

1. **Point to your Obsidian vault**:
   ```yaml
   vault:
     path: "/Users/you/Documents/MyObsidianVault"
   ```

2. **Enable Obsidian integration features**:
   ```yaml
   obsidian:
     enabled: true              # Respect .obsidian/ directory
     config_sync: true          # Read periodic notes settings from Obsidian
   ```

3. **Use the API**:
   - API runs on port 27123 (same as Obsidian Local REST API plugin)
   - All endpoints are API-compatible with existing clients
   - Works whether or not Obsidian is running

### Advantages for Obsidian Users

- **Continuous Availability**: Access your vault via API even when Obsidian is closed
- **Server Deployment**: Run on servers for remote access to your Obsidian vault
- **Automation**: Build scripts and integrations without desktop dependency
- **Performance**: Dedicated service optimized for API operations
- **Multiple Vaults**: Access multiple Obsidian vaults concurrently

**Migrating from the Obsidian plugin?** See our [Migration Guide](./docs/MIGRATION_FROM_PLUGIN.md) for step-by-step instructions.

## Deployment Options

### Docker Deployment
```bash
docker run -d \
  -p 27123:27123 \
  -v /path/to/vault:/vault \
  -e VAULT_PATH=/vault \
  -e API_KEY=your-key \
  markdown-vault:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  markdown-vault:
    image: markdown-vault:latest
    ports:
      - "27123:27123"
    volumes:
      - ./vault:/vault
      - ./config.yaml:/app/config.yaml
    environment:
      - CONFIG_PATH=/app/config.yaml
```

### Systemd Service
See [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) for production deployment guides.

## Project Status

This project is currently in active development. See [PLAN.md](./PLAN.md) for the implementation roadmap.

## Documentation

- [Configuration Guide](./docs/CONFIGURATION.md) - Complete configuration reference
- [Migration Guide](./docs/MIGRATION_FROM_PLUGIN.md) - Moving from Obsidian Local REST API plugin
- [Implementation Plan](./docs/PLAN.md) - Detailed development roadmap
- [Project Summary](./docs/PROJECT_SUMMARY.md) - Executive overview
- [Documentation Setup](./docs/DOCUMENTATION_SETUP.md) - Documentation architecture
- [API Reference](./docs/API.md) - (Coming soon)

## Contributing

Contributions welcome! This is an open-source project aimed at improving markdown vault automation and programmatic access.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License

MIT License - See [LICENSE](./LICENSE) for details

## Credits and Acknowledgments

This project implements API compatibility with the [Obsidian Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api) created by [@coddingtonbear](https://github.com/coddingtonbear). The plugin's excellent API design served as the foundation for this standalone implementation.

[Obsidian](https://obsidian.md) is a trademark of Dynalist Inc. This project is an independent implementation and is not affiliated with, endorsed by, or sponsored by Obsidian or Dynalist Inc.
