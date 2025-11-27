# Configuration Guide

This guide explains how to configure markdown-vault using YAML files and environment variables.

## Quick Start

1. Copy the example configuration:
   ```bash
   cp config/config.example.yaml config/config.yaml
   ```

2. Edit `config/config.yaml` and set your vault path:
   ```yaml
   vault:
     path: "/path/to/your/vault"
   ```

3. Load the configuration in your code:
   ```python
   from markdown_vault.core.config import load_config
   
   config = load_config("config/config.yaml")
   ```

## Configuration Methods

markdown-vault supports two ways to configure the application:

### 1. YAML Configuration File

Create a `config.yaml` file with your settings:

```yaml
server:
  host: "127.0.0.1"
  port: 27123
  https: true
  
vault:
  path: "/path/to/vault"
  auto_create: true
```

### 2. Environment Variables

Override any configuration value using environment variables with the `MARKDOWN_VAULT_` prefix:

```bash
export MARKDOWN_VAULT_SERVER__PORT=8080
export MARKDOWN_VAULT_VAULT__PATH=/path/to/vault
export MARKDOWN_VAULT_SECURITY__API_KEY=your-secret-key
```

Environment variables use double underscores (`__`) to separate sections and keys.

**Priority**: Environment variables override YAML file values.

## Configuration Sections

### Server Configuration

Controls the HTTP/HTTPS server settings.

```yaml
server:
  host: "127.0.0.1"      # Bind address (use 0.0.0.0 for all interfaces)
  port: 27123            # Port number (1-65535)
  https: true            # Enable HTTPS
  reload: false          # Auto-reload on code changes (dev only)
```

**Environment variables:**
- `MARKDOWN_VAULT_SERVER__HOST`
- `MARKDOWN_VAULT_SERVER__PORT`
- `MARKDOWN_VAULT_SERVER__HTTPS`
- `MARKDOWN_VAULT_SERVER__RELOAD`

### Vault Configuration

Defines the markdown vault location and behavior.

```yaml
vault:
  path: "/path/to/vault"       # Absolute path to vault (required)
  auto_create: true            # Create vault directory if missing
  watch_files: false           # Watch for external file changes
  respect_gitignore: true      # Honor .gitignore files
```

**Environment variables:**
- `MARKDOWN_VAULT_VAULT__PATH` (required)
- `MARKDOWN_VAULT_VAULT__AUTO_CREATE`
- `MARKDOWN_VAULT_VAULT__WATCH_FILES`
- `MARKDOWN_VAULT_VAULT__RESPECT_GITIGNORE`

**Note**: The vault path must be an absolute path.

### Security Configuration

Manages API keys and SSL certificates.

```yaml
security:
  api_key: null                      # API key (auto-generated if null)
  api_key_file: null                 # Path to file containing API key
  cert_path: "./certs/server.crt"    # SSL certificate path
  key_path: "./certs/server.key"     # SSL private key path
  auto_generate_cert: true           # Generate self-signed cert if missing
```

**Environment variables:**
- `MARKDOWN_VAULT_SECURITY__API_KEY`
- `MARKDOWN_VAULT_SECURITY__API_KEY_FILE`
- `MARKDOWN_VAULT_SECURITY__CERT_PATH`
- `MARKDOWN_VAULT_SECURITY__KEY_PATH`
- `MARKDOWN_VAULT_SECURITY__AUTO_GENERATE_CERT`

**API Key Resolution:**
1. If `api_key` is set, use that value
2. Else if `api_key_file` is set, load from file
3. Else generate a new random key

**SSL Certificates:**
- If HTTPS is enabled and certificates don't exist, they will be auto-generated (self-signed)
- Set `auto_generate_cert: false` to require existing certificates

### Obsidian Integration

Controls Obsidian-specific features.

```yaml
obsidian:
  enabled: true               # Enable Obsidian features
  config_sync: true           # Import settings from .obsidian/
  respect_exclusions: true    # Honor Obsidian's excluded files
```

**Environment variables:**
- `MARKDOWN_VAULT_OBSIDIAN__ENABLED`
- `MARKDOWN_VAULT_OBSIDIAN__CONFIG_SYNC`
- `MARKDOWN_VAULT_OBSIDIAN__RESPECT_EXCLUSIONS`

### Periodic Notes

Configure automatic periodic note management.

```yaml
periodic_notes:
  daily:
    enabled: true
    format: "YYYY-MM-DD"
    folder: "daily/"
    template: "templates/daily.md"  # optional
  
  weekly:
    enabled: true
    format: "YYYY-[W]WW"
    folder: "weekly/"
    template: null
  
  monthly:
    enabled: true
    format: "YYYY-MM"
    folder: "monthly/"
    template: null
  
  quarterly:
    enabled: true
    format: "YYYY-[Q]Q"
    folder: "quarterly/"
    template: null
  
  yearly:
    enabled: true
    format: "YYYY"
    folder: "yearly/"
    template: null
```

**Environment variables** (example for daily notes):
- `MARKDOWN_VAULT_PERIODIC_NOTES__DAILY__ENABLED`
- `MARKDOWN_VAULT_PERIODIC_NOTES__DAILY__FORMAT`
- `MARKDOWN_VAULT_PERIODIC_NOTES__DAILY__FOLDER`
- `MARKDOWN_VAULT_PERIODIC_NOTES__DAILY__TEMPLATE`

### Search Configuration

Controls search behavior and performance.

```yaml
search:
  max_results: 100        # Maximum search results to return
  enable_fuzzy: true      # Enable fuzzy matching
  cache_results: true     # Cache search results
```

**Environment variables:**
- `MARKDOWN_VAULT_SEARCH__MAX_RESULTS`
- `MARKDOWN_VAULT_SEARCH__ENABLE_FUZZY`
- `MARKDOWN_VAULT_SEARCH__CACHE_RESULTS`

### Active File Tracking

Controls how the "active file" is tracked across requests.

```yaml
active_file:
  tracking_method: "session"    # session | cookie | redis
  default_file: null            # Default file if none active
```

**Environment variables:**
- `MARKDOWN_VAULT_ACTIVE_FILE__TRACKING_METHOD`
- `MARKDOWN_VAULT_ACTIVE_FILE__DEFAULT_FILE`

### Commands Configuration

Controls the commands API.

```yaml
commands:
  enabled: true                    # Enable commands API
  custom_commands_dir: null        # Directory for custom command plugins
```

**Environment variables:**
- `MARKDOWN_VAULT_COMMANDS__ENABLED`
- `MARKDOWN_VAULT_COMMANDS__CUSTOM_COMMANDS_DIR`

### Logging

Controls application logging.

```yaml
logging:
  level: "INFO"        # DEBUG | INFO | WARNING | ERROR | CRITICAL
  format: "json"       # json | text
  file: null           # Log file path (null = stdout)
```

**Environment variables:**
- `MARKDOWN_VAULT_LOGGING__LEVEL`
- `MARKDOWN_VAULT_LOGGING__FORMAT`
- `MARKDOWN_VAULT_LOGGING__FILE`

### Performance

Performance tuning options.

```yaml
performance:
  max_file_size: 10485760    # Maximum file size in bytes (10MB)
  cache_ttl: 300             # Cache TTL in seconds
  worker_count: 1            # Uvicorn worker processes
```

**Environment variables:**
- `MARKDOWN_VAULT_PERFORMANCE__MAX_FILE_SIZE`
- `MARKDOWN_VAULT_PERFORMANCE__CACHE_TTL`
- `MARKDOWN_VAULT_PERFORMANCE__WORKER_COUNT`

## Usage Examples

### Example 1: Basic Configuration

```python
from markdown_vault.core.config import load_config

# Load from YAML file
config = load_config("config/config.yaml")

print(f"Server: {config.server.host}:{config.server.port}")
print(f"Vault: {config.vault.path}")
print(f"API Key: {config.security.api_key}")
```

### Example 2: Environment Override

```bash
# Set environment variables
export MARKDOWN_VAULT_SERVER__PORT=8080
export MARKDOWN_VAULT_VAULT__PATH=/path/to/vault

# Run your application
python -m markdown_vault
```

### Example 3: No Configuration File

```python
import os
from markdown_vault.core.config import load_config

# Configure entirely via environment
os.environ["MARKDOWN_VAULT_VAULT__PATH"] = "/path/to/vault"
os.environ["MARKDOWN_VAULT_SERVER__HTTPS"] = "false"

config = load_config()  # No file path needed
```

### Example 4: API Key from File

```yaml
security:
  api_key_file: "/etc/markdown-vault/api_key.txt"
```

The file should contain just the API key:
```
your-api-key-here
```

### Example 5: Docker Environment

```bash
docker run -e MARKDOWN_VAULT_VAULT__PATH=/vault \
           -e MARKDOWN_VAULT_SERVER__PORT=8080 \
           -e MARKDOWN_VAULT_SECURITY__API_KEY=your-key \
           -v /local/vault:/vault \
           markdown-vault
```

## Validation

The configuration system validates all values:

- **Port**: Must be between 1 and 65535
- **Vault Path**: Must be an absolute path
- **Tracking Method**: Must be one of: session, cookie, redis
- **Log Level**: Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Format**: Must be one of: json, text
- **Worker Count**: Must be at least 1

Validation errors will raise a `ConfigError` with details about what's wrong.

## Error Handling

```python
from markdown_vault.core.config import ConfigError, load_config

try:
    config = load_config("config.yaml")
except ConfigError as e:
    print(f"Configuration error: {e}")
    # Handle error (use defaults, exit, etc.)
```

## Security Best Practices

1. **API Key Storage**
   - Never commit API keys to version control
   - Use `api_key_file` to store keys separately
   - Or use environment variables for production

2. **SSL Certificates**
   - Auto-generated certificates are self-signed (for development)
   - Use proper certificates in production
   - Set `auto_generate_cert: false` in production

3. **File Permissions**
   - Protect configuration files (chmod 600)
   - Protect API key files (chmod 400)
   - Protect SSL private keys (chmod 400)

## See Also

- [config.example.yaml](../config/config.example.yaml) - Example configuration file
- [examples/config_demo.py](../examples/config_demo.py) - Configuration examples
- [PLAN.md](PLAN.md) - Full project plan and specification
