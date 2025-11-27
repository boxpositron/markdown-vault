# markdown-vault

A drop-in replacement for the Obsidian Local REST API plugin that can run as a standalone service. Interact with your markdown vaults programmatically with a secure, reliable REST API - whether or not Obsidian is running.

## Overview

**markdown-vault** is a standalone service that provides a REST API for managing markdown files with full compatibility with the [Obsidian Local REST API plugin](https://github.com/coddingtonbear/obsidian-local-rest-api). It operates in two modes:

1. **Standalone Mode**: Manage any markdown vault independently - no Obsidian required
2. **Drop-in Replacement Mode**: Point it at an Obsidian vault to replace the Obsidian REST API plugin with a more reliable service

**Key Distinction**: This is not an Obsidian plugin - it's a standalone service that can work with or without Obsidian.

## Key Features

- Full Obsidian REST API compatibility - drop-in replacement
- CRUD operations on markdown files
- Advanced PATCH operations (heading/block/frontmatter targeting)
- Periodic notes support (daily, weekly, monthly, quarterly, yearly)
- Search functionality with JSONLogic queries
- Vault-wide file listing and management
- Secure HTTPS with API key authentication
- No dependency on Obsidian being open
- Docker and standalone deployment options

## Why Replace the Obsidian Plugin?

| Feature | Obsidian Plugin | markdown-vault |
|---------|----------------|----------------|
| **Requires Obsidian** | ✅ Yes - must be running | ❌ No - fully standalone |
| **Always Available** | ❌ Only when Obsidian is open | ✅ 24/7 service |
| **Server Deployment** | ❌ Desktop only | ✅ Servers, containers, cloud |
| **Performance** | Limited by Obsidian | Dedicated, optimized service |
| **Multiple Vaults** | One at a time | Concurrent access |
| **Automation** | Requires Obsidian running | Independent automation |
| **API Compatibility** | ✅ Original | ✅ 100% compatible |

**Key Difference**: The Obsidian plugin requires Obsidian to be running. **markdown-vault is a standalone service** that works with or without Obsidian installed.

## Advantages Over Plugin

- **True Independence**: No dependency on Obsidian being installed or running
- **Always Available**: 24/7 API access, even when Obsidian is closed
- **Server Deployment**: Run on servers, containers, cloud platforms
- **Better Performance**: Dedicated service optimized for API operations
- **Easier Automation**: No need to keep Obsidian open for scripts/integrations
- **Multiple Vaults**: Can manage multiple vaults concurrently
- **Extensibility**: Easy to add features like webhooks, sync, etc.

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

## Using with Obsidian Vaults

You can use markdown-vault as a **drop-in replacement** for the Obsidian Local REST API plugin:

1. **Point to your Obsidian vault**:
   ```yaml
   vault:
     path: "/Users/you/Documents/MyObsidianVault"
   ```

2. **Configure to respect Obsidian structure**:
   ```yaml
   obsidian:
     enabled: true              # Respect .obsidian/ directory
     config_sync: true          # Read periodic notes settings from Obsidian
   ```

3. **Replace the Obsidian plugin**:
   - Disable the Obsidian Local REST API plugin
   - Use markdown-vault's API at the same port (27123)
   - All existing clients work without changes

4. **Benefits of replacement**:
   - Works even when Obsidian is closed
   - Better performance and reliability
   - Can run on servers/containers
   - Easier to automate and integrate

**Migrating from the plugin?** See our [Migration Guide](./docs/MIGRATION_FROM_PLUGIN.md) for step-by-step instructions.

## Project Status

This project is currently in active development. See [PLAN.md](./PLAN.md) for the implementation roadmap.

## Documentation

- [Migration Guide](./docs/MIGRATION_FROM_PLUGIN.md) - Replace Obsidian plugin with markdown-vault
- [Implementation Plan](./docs/PLAN.md) - Detailed development roadmap
- [Research Notes](./docs/RESEARCH.md) - Original API analysis
- [Project Summary](./docs/PROJECT_SUMMARY.md) - Executive overview
- [Documentation Setup](./docs/DOCUMENTATION_SETUP.md) - Documentation architecture
- [Configuration Guide](./docs/CONFIGURATION.md) - (Coming soon)
- [API Reference](./docs/API.md) - (Coming soon)

## Contributing

Contributions welcome! This is an open-source project aimed at improving markdown vault automation.

## License

MIT License - See [LICENSE](./LICENSE) for details

## Credits

Inspired by and compatible with [obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api) by [@coddingtonbear](https://github.com/coddingtonbear).
