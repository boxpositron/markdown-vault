# markdown-vault: Implementation Plan

**Project Name**: markdown-vault  
**Description**: Drop-in replacement for Obsidian Local REST API plugin with standalone service capabilities  
**Status**: Planning Phase  
**Last Updated**: November 27, 2025

## Project Goals

Build a reliable, standalone REST API service for markdown vault management that:

1. **Full Compatibility**: Drop-in replacement for Obsidian Local REST API plugin
2. **Dual Mode Operation**:
   - **Standalone Mode**: Independent markdown vault management
   - **Obsidian Integration Mode**: Work alongside Obsidian vaults
3. **Reliability**: No dependency on Obsidian being open
4. **Performance**: Optimized for concurrent API operations
5. **Extensibility**: Easy to add new features and integrations

## Operating Modes

### Standalone Mode
- Manages any directory of markdown files
- Full API functionality independent of Obsidian
- Ideal for automation, scripts, and non-Obsidian workflows
- Can create and manage vault structure

### Obsidian Integration Mode
- Points to existing Obsidian vault directory
- Respects `.obsidian/` configuration
- Compatible with Obsidian plugin simultaneously (with proper locking)
- Reads Obsidian plugin settings for periodic notes, templates, etc.
- Optional: Sync active file state with Obsidian

## Technology Stack

### Core Framework
**FastAPI (Python 3.10+)**
- Native OpenAPI 3.0 generation
- Type safety with Pydantic models
- Async/await for performance
- Excellent testing support
- Automatic validation and serialization

### Key Dependencies

**Markdown & Content Processing**:
- `python-frontmatter` - YAML frontmatter parsing
- `markdown-it-py` - Markdown parsing
- `pyyaml` - YAML manipulation
- `jsonlogic` - Search query processing

**File Operations**:
- `aiofiles` - Async file I/O
- `watchdog` - File system monitoring (optional)

**Security & Networking**:
- `cryptography` - SSL certificate generation
- `uvicorn` - ASGI server with SSL support
- `python-jose` - Token handling

**Configuration**:
- `pydantic-settings` - Configuration management
- `pyyaml` - YAML config file parsing

**Testing**:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - Async HTTP client for testing

## Project Structure

```
markdown-vault/
├── src/
│   └── markdown_vault/
│       ├── __init__.py
│       ├── __main__.py                 # CLI entry point
│       ├── main.py                      # FastAPI app
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py                  # Dependency injection
│       │   └── routes/
│       │       ├── __init__.py
│       │       ├── system.py            # /, /openapi.yaml, /cert
│       │       ├── vault.py             # /vault/** endpoints
│       │       ├── active.py            # /active/ endpoints
│       │       ├── periodic.py          # /periodic/** endpoints
│       │       ├── search.py            # /search/** endpoints
│       │       ├── commands.py          # /commands/** endpoints
│       │       └── open.py              # /open/** endpoints
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py                # Configuration management
│       │   ├── vault.py                 # Vault manager
│       │   ├── markdown_parser.py       # Markdown parsing
│       │   ├── patch_engine.py          # PATCH operations
│       │   ├── periodic_notes.py        # Periodic notes logic
│       │   ├── search_engine.py         # Search implementation
│       │   ├── active_file.py           # Active file tracking
│       │   └── commands.py              # Command system
│       │
│       ├── models/
│       │   ├── __init__.py
│       │   ├── api.py                   # API request/response models
│       │   ├── note.py                  # Note data models
│       │   ├── config.py                # Config models
│       │   └── errors.py                # Error models
│       │
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── crypto.py                # SSL cert generation
│       │   ├── file_ops.py              # File operation helpers
│       │   ├── path_utils.py            # Path manipulation
│       │   └── date_utils.py            # Date formatting for periodic notes
│       │
│       └── cli/
│           ├── __init__.py
│           └── commands.py              # CLI commands
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures
│   ├── test_vault.py
│   ├── test_patch_engine.py
│   ├── test_periodic_notes.py
│   ├── test_search.py
│   ├── test_api/
│   │   ├── test_vault_routes.py
│   │   ├── test_active_routes.py
│   │   ├── test_periodic_routes.py
│   │   └── test_search_routes.py
│   └── fixtures/
│       └── sample_vault/                # Test markdown files
│
├── docs/
│   ├── RESEARCH.md                      # Original API research
│   ├── PLAN.md                          # This file
│   ├── CONFIGURATION.md                 # Configuration guide (TBD)
│   ├── API.md                           # API reference (TBD)
│   └── DEVELOPMENT.md                   # Developer guide (TBD)
│
├── config/
│   ├── config.example.yaml              # Example configuration
│   └── obsidian-integration.example.yaml # Obsidian integration example
│
├── scripts/
│   ├── generate_cert.py                 # SSL cert generation script
│   └── setup_dev.sh                     # Development environment setup
│
├── .github/
│   └── workflows/
│       ├── test.yml                     # CI/CD tests
│       └── release.yml                  # Release automation
│
├── pyproject.toml                       # Project metadata & dependencies
├── README.md                            # Main documentation
├── LICENSE                              # MIT License
├── .gitignore
└── Dockerfile                           # Container deployment
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goals**: Core architecture, basic file operations, authentication

#### Tasks

1. **Project Setup**
   - Initialize Python project with `pyproject.toml`
   - Set up development environment
   - Configure linting (ruff/black) and type checking (mypy)
   - Set up pytest with coverage

2. **Configuration System**
   - Pydantic models for configuration
   - YAML config file loading
   - Environment variable support
   - Config validation

3. **Basic FastAPI App**
   - Application factory pattern
   - Router registration
   - CORS and middleware setup
   - Error handling middleware

4. **Authentication & Security**
   - SSL certificate generation
   - API key authentication middleware
   - Bearer token validation
   - HTTPS server configuration

5. **Basic Vault Operations**
   - File reading (GET)
   - File writing (PUT)
   - File appending (POST)
   - File deletion (DELETE)
   - Directory listing (GET)

6. **System Endpoints**
   - `GET /` - Server status
   - `GET /openapi.yaml` - API spec
   - `GET /obsidian-local-rest-api.crt` - Certificate

**Deliverables**:
- Working FastAPI server with HTTPS
- Basic CRUD operations on markdown files
- Configuration system
- Initial test suite

---

### Phase 2: Markdown Processing (Week 2-3)

**Goals**: Advanced markdown parsing, JSON response format, basic PATCH

#### Tasks

1. **Markdown Parser**
   - Frontmatter extraction and parsing
   - Inline tag detection (`#tag`)
   - File metadata (ctime, mtime, size)
   - Content and metadata separation

2. **JSON Response Format**
   - `NoteJson` model matching Obsidian API
   - Content negotiation (Accept header)
   - `text/markdown` response
   - `application/vnd.olrapi.note+json` response

3. **Heading Parser**
   - Parse markdown heading hierarchy
   - Build heading tree structure
   - Navigate nested headings with delimiter
   - Extract content under headings

4. **Block Reference Parser**
   - Detect block reference syntax (`^blockid`)
   - Map block IDs to content locations
   - Handle block references in various contexts

5. **Basic PATCH Engine**
   - Heading targeting (append/prepend/replace)
   - Block targeting (append/prepend/replace)
   - Header parsing and validation
   - Content insertion logic

**Deliverables**:
- JSON response format for notes
- Heading navigation system
- Block reference resolution
- Basic PATCH operations working

---

### Phase 3: Advanced Features (Week 3-4)

**Goals**: Complete PATCH engine, periodic notes, search

#### Tasks

1. **Advanced PATCH Operations**
   - Frontmatter targeting and modification
   - Table manipulation via block references
   - JSON content type handling for structured data
   - Whitespace preservation
   - `Create-Target-If-Missing` header support

2. **Periodic Notes System**
   - Date calculation for each period type
   - Template loading and application
   - Folder structure management
   - Auto-creation logic
   - All CRUD + PATCH endpoints

3. **Search Implementation**
   - Simple text search across vault
   - JSONLogic query engine
   - Frontmatter filtering
   - Tag filtering
   - Date range filtering
   - Result ranking and pagination

4. **Active File Tracking**
   - Server-side active file state
   - Session/cookie-based tracking
   - All CRUD + PATCH endpoints
   - `/open/{filename}` endpoint

**Deliverables**:
- Complete PATCH engine with all target types
- Periodic notes fully functional
- Search API working
- Active file tracking

---

### Phase 4: Obsidian Integration (Week 4-5)

**Goals**: Obsidian vault compatibility, configuration sync

#### Tasks

1. **Obsidian Vault Detection**
   - Detect `.obsidian/` directory
   - Read Obsidian configuration files
   - Parse periodic notes plugin settings
   - Parse template plugin settings

2. **Configuration Sync**
   - Import periodic note settings from Obsidian
   - Respect Obsidian templates
   - Honor Obsidian file exclusions
   - Read custom date formats

3. **Commands API**
   - Command registry system
   - Built-in commands (search, create note, etc.)
   - Plugin interface for custom commands
   - Obsidian command compatibility layer (optional)

4. **File Watching (Optional)**
   - Detect external file changes
   - Invalidate caches on change
   - File locking for safe concurrent access
   - Conflict detection

**Deliverables**:
- Obsidian vault auto-detection
- Configuration import from Obsidian
- Commands API
- Optional file watching

---

### Phase 5: CLI & Deployment (Week 5)

**Goals**: Command-line interface, deployment options, documentation

#### Tasks

1. **CLI Development**
   - `markdown-vault start` - Start server
   - `markdown-vault init` - Initialize config
   - `markdown-vault generate-key` - Generate API key
   - `markdown-vault cert` - Manage SSL certificates
   - `markdown-vault validate` - Validate vault structure

2. **Docker Support**
   - Dockerfile for containerization
   - Docker Compose example
   - Volume mounting for vaults
   - Environment variable configuration

3. **Packaging**
   - PyPI package preparation
   - Entry point scripts
   - Platform-specific builds (optional)
   - Version management

4. **Documentation**
   - Configuration guide
   - API reference documentation
   - Integration examples
   - Deployment guides
   - Development setup guide

**Deliverables**:
- Full-featured CLI
- Docker deployment option
- PyPI package
- Complete documentation

---

### Phase 6: Testing & Polish (Week 6)

**Goals**: Comprehensive testing, performance optimization, release prep

#### Tasks

1. **Test Coverage**
   - Unit tests for all core modules
   - Integration tests for API endpoints
   - PATCH operation test suite
   - Edge case testing
   - Error handling tests

2. **Performance Optimization**
   - Async file I/O throughout
   - Response caching where appropriate
   - Large file handling
   - Concurrent request handling
   - Memory profiling

3. **Compatibility Testing**
   - Test against Obsidian plugin API spec
   - Verify all response formats match
   - Cross-platform testing (macOS, Linux, Windows)
   - Integration tests with real Obsidian vaults

4. **Security Audit**
   - Path traversal prevention
   - Input validation
   - Rate limiting (optional)
   - Secure defaults
   - Security documentation

5. **Release Preparation**
   - Changelog generation
   - Version tagging
   - GitHub release automation
   - PyPI publishing workflow

**Deliverables**:
- 90%+ test coverage
- Performance benchmarks
- Security audit report
- v1.0.0 release

---

## API Endpoint Implementation Checklist

### System Endpoints
- [ ] `GET /` - Server status and auth check
- [ ] `GET /openapi.yaml` - OpenAPI specification
- [ ] `GET /obsidian-local-rest-api.crt` - SSL certificate download

### Vault Endpoints
- [ ] `GET /vault/` - List all files
- [ ] `GET /vault/{filepath}` - Read file (markdown)
- [ ] `GET /vault/{filepath}` - Read file (JSON with metadata)
- [ ] `PUT /vault/{filepath}` - Create/update file
- [ ] `POST /vault/{filepath}` - Append to file
- [ ] `PATCH /vault/{filepath}` - Partial update (heading)
- [ ] `PATCH /vault/{filepath}` - Partial update (block)
- [ ] `PATCH /vault/{filepath}` - Partial update (frontmatter)
- [ ] `DELETE /vault/{filepath}` - Delete file

### Active File Endpoints
- [ ] `GET /active/` - Get active file
- [ ] `PUT /active/` - Update active file
- [ ] `POST /active/` - Append to active file
- [ ] `PATCH /active/` - Partial update active file
- [ ] `DELETE /active/` - Delete active file
- [ ] `POST /open/{filename}` - Open file (set as active)

### Periodic Notes Endpoints
- [ ] `GET /periodic/{period}/` - Get periodic note
- [ ] `PUT /periodic/{period}/` - Update periodic note
- [ ] `POST /periodic/{period}/` - Append to periodic note
- [ ] `PATCH /periodic/{period}/` - Partial update periodic note
- [ ] `DELETE /periodic/{period}/` - Delete periodic note

### Search Endpoints
- [ ] `POST /search/simple/` - Simple text search
- [ ] `POST /search/` - Complex JSONLogic search

### Commands Endpoints
- [ ] `GET /commands/` - List available commands
- [ ] `POST /commands/{commandId}/` - Execute command

---

## Configuration Specification

### config.yaml Structure

```yaml
# Server configuration
server:
  host: "127.0.0.1"              # Bind address
  port: 27123                    # Default Obsidian plugin port
  https: true                    # Enable HTTPS
  reload: false                  # Auto-reload on code changes (dev only)

# Vault configuration
vault:
  path: "/path/to/vault"         # Absolute path to vault
  auto_create: true              # Create vault if doesn't exist
  watch_files: false             # Enable file watching
  respect_gitignore: true        # Honor .gitignore files

# Security configuration
security:
  api_key: null                  # API key (auto-generated if null)
  api_key_file: null             # Path to file containing API key
  cert_path: "./certs/server.crt"
  key_path: "./certs/server.key"
  auto_generate_cert: true       # Generate self-signed cert if missing

# Obsidian integration
obsidian:
  enabled: true                  # Enable Obsidian-specific features
  config_sync: true              # Sync settings from .obsidian/
  respect_exclusions: true       # Honor Obsidian's excluded files

# Periodic notes configuration
periodic_notes:
  daily:
    enabled: true
    format: "YYYY-MM-DD"         # Date format
    folder: "daily/"             # Folder path (relative to vault)
    template: "templates/daily.md" # Template file (optional)
  weekly:
    enabled: true
    format: "YYYY-[W]WW"
    folder: "weekly/"
    template: "templates/weekly.md"
  monthly:
    enabled: true
    format: "YYYY-MM"
    folder: "monthly/"
  quarterly:
    enabled: true
    format: "YYYY-[Q]Q"
    folder: "quarterly/"
  yearly:
    enabled: true
    format: "YYYY"
    folder: "yearly/"

# Search configuration
search:
  max_results: 100               # Maximum search results
  enable_fuzzy: true             # Enable fuzzy matching
  cache_results: true            # Cache search results

# Active file configuration
active_file:
  tracking_method: "session"     # session | cookie | redis
  default_file: null             # Default file if none active

# Commands configuration
commands:
  enabled: true                  # Enable commands API
  custom_commands_dir: null      # Directory for custom command plugins

# Logging
logging:
  level: "INFO"                  # DEBUG | INFO | WARNING | ERROR
  format: "json"                 # json | text
  file: null                     # Log file path (null = stdout)

# Performance
performance:
  max_file_size: 10485760        # 10MB max file size
  cache_ttl: 300                 # Cache TTL in seconds
  worker_count: 4                # Uvicorn workers
```

---

## Data Models

### NoteJson Model

```python
from pydantic import BaseModel
from typing import Optional, Dict, List, Any

class NoteStat(BaseModel):
    ctime: int  # Creation time (milliseconds since epoch)
    mtime: int  # Modification time (milliseconds since epoch)
    size: int   # File size in bytes

class NoteJson(BaseModel):
    path: str
    content: str
    frontmatter: Dict[str, Any]
    tags: List[str]
    stat: NoteStat
```

### Error Model

```python
class APIError(BaseModel):
    errorCode: int  # 5-digit error code
    message: str    # Human-readable error message
```

---

## Error Code System

Following Obsidian plugin's 5-digit error code pattern:

| Code Range | Category |
|------------|----------|
| 40000-40099 | Bad Request (validation errors) |
| 40100-40199 | Authentication errors |
| 40400-40499 | Not Found errors |
| 40500-40599 | Method Not Allowed |
| 50000-50099 | Internal Server Errors |

Example error codes:
- `40001` - Invalid file path
- `40002` - Invalid PATCH operation
- `40003` - Invalid target type
- `40101` - Missing API key
- `40102` - Invalid API key
- `40401` - File not found
- `40402` - Directory not found
- `40501` - Cannot POST to directory
- `50001` - Internal file system error

---

## Testing Strategy

### Unit Tests
- Configuration loading and validation
- Markdown parsing (frontmatter, tags, content)
- Heading navigation
- Block reference resolution
- PATCH engine operations
- Periodic note date calculations
- Search query processing

### Integration Tests
- Full API endpoint testing
- File system operations
- Multi-file operations
- Concurrent request handling
- Authentication flow

### Compatibility Tests
- Test against real Obsidian vaults
- Verify response format matches plugin
- Test with Obsidian REST API clients
- Cross-platform file path handling

### Performance Tests
- Large file handling
- Concurrent request load testing
- Search performance with large vaults
- Memory usage profiling

---

## Deployment Options

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install .

COPY src/ ./src/

EXPOSE 27123

CMD ["markdown-vault", "start", "--config", "/config/config.yaml"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  markdown-vault:
    image: markdown-vault:latest
    ports:
      - "27123:27123"
    volumes:
      - ./vault:/vault
      - ./config:/config
      - ./certs:/certs
    environment:
      - MARKDOWN_VAULT_API_KEY=${API_KEY}
```

### Systemd Service

```ini
[Unit]
Description=markdown-vault API Server
After=network.target

[Service]
Type=simple
User=markdownvault
WorkingDirectory=/opt/markdown-vault
ExecStart=/usr/local/bin/markdown-vault start --config /etc/markdown-vault/config.yaml
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/markdown-vault.git
cd markdown-vault

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Start development server with auto-reload
markdown-vault start --config config/config.example.yaml --reload
```

---

## Success Criteria

### Minimum Viable Product (MVP)
- [ ] All vault endpoints functional (GET, PUT, POST, DELETE)
- [ ] Authentication working (API key + HTTPS)
- [ ] JSON response format matching Obsidian API
- [ ] Basic PATCH operations (heading and block targeting)
- [ ] Configuration system working
- [ ] CLI for starting server
- [ ] Basic documentation

### Feature Complete (v1.0)
- [ ] All endpoints implemented
- [ ] Complete PATCH engine (heading, block, frontmatter)
- [ ] Periodic notes fully functional
- [ ] Search API working
- [ ] Active file tracking
- [ ] Commands API (basic)
- [ ] Obsidian vault auto-detection
- [ ] Docker deployment option
- [ ] Comprehensive test suite (90%+ coverage)
- [ ] Full documentation
- [ ] PyPI package published

### Future Enhancements (v2.0+)
- [ ] Webhooks for file changes
- [ ] GraphQL API option
- [ ] Real-time collaboration features
- [ ] Plugin system for extensibility
- [ ] Web UI for vault browsing
- [ ] Git integration (auto-commit)
- [ ] Multi-vault support
- [ ] Redis-backed caching
- [ ] Metrics and monitoring (Prometheus)
- [ ] Link graph API (backlinks, forward links)

---

## Development Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Foundation | 1-2 weeks | Basic API + auth + file ops |
| Phase 2: Markdown Processing | 1 week | JSON format + basic PATCH |
| Phase 3: Advanced Features | 1-2 weeks | Full PATCH + periodic + search |
| Phase 4: Obsidian Integration | 1 week | Obsidian compat + commands |
| Phase 5: CLI & Deployment | 1 week | CLI + Docker + packaging |
| Phase 6: Testing & Polish | 1 week | Tests + docs + release |
| **Total** | **6-8 weeks** | **v1.0.0 Release** |

---

## Risk Mitigation

### Technical Risks

**Risk**: PATCH engine complexity  
**Mitigation**: Build incrementally, extensive test coverage, reference Obsidian plugin implementation

**Risk**: Markdown parsing edge cases  
**Mitigation**: Use battle-tested libraries, comprehensive test fixtures, fuzz testing

**Risk**: File system race conditions  
**Mitigation**: Proper locking mechanisms, atomic operations, transaction-like semantics

**Risk**: Obsidian configuration parsing  
**Mitigation**: Graceful fallbacks, extensive Obsidian vault testing, clear error messages

### Project Risks

**Risk**: Scope creep  
**Mitigation**: Strict MVP definition, phase-gated development, feature prioritization

**Risk**: Compatibility breaking changes  
**Mitigation**: Comprehensive compatibility tests, semantic versioning, changelog discipline

**Risk**: Performance issues with large vaults  
**Mitigation**: Performance testing early, caching strategy, async I/O throughout

---

## Contributing Guidelines

### Development Workflow
1. Fork repository
2. Create feature branch (`feature/amazing-feature`)
3. Write tests for new functionality
4. Implement feature
5. Ensure tests pass and coverage maintained
6. Update documentation
7. Submit pull request

### Code Standards
- Python 3.10+ type hints throughout
- Black formatting (line length 88)
- Ruff linting
- Mypy type checking
- Docstrings for all public APIs
- Test coverage > 90%

### Commit Messages
Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements

---

## License

MIT License - See LICENSE file for details

---

## References

- [Obsidian Local REST API Plugin](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Research Notes](./RESEARCH.md)
