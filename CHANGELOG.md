## [1.0.0] - 2025-11-29

### 🎉 Initial Release

**markdown-vault v1.0.0** - Production-ready REST API server for markdown vaults with Obsidian compatibility.

### Features

#### Core API (29/29 Endpoints)
- **System Endpoints** (3): Server status, OpenAPI spec, SSL certificate
- **Vault Operations** (6): Full CRUD operations on markdown files
- **Active File Tracking** (6): Session-based file management
- **Periodic Notes** (10): Daily, weekly, monthly, quarterly, yearly notes
- **Search** (2): Simple text search and JSONLogic queries
- **Commands** (2): Extensible command system

#### Advanced Capabilities
- **PATCH Operations**: Heading, block reference, and frontmatter targeting
- **Template Support**: Variable substitution for periodic notes
- **Full-Text Search**: Across content and frontmatter
- **Session Management**: Cookie-based active file tracking
- **Obsidian Compatibility**: 100% API compatible with Obsidian Local REST API

#### Security & Production Features
- **HTTPS**: Self-signed certificate auto-generation
- **Authentication**: API key-based security
- **Path Validation**: Protection against traversal attacks
- **Async I/O**: Non-blocking file operations throughout
- **Type Safety**: Full type hints with mypy validation

#### Deployment
- **Docker Support**: Production-ready containers
- **CLI Tool**: `markdown-vault` command with start/version
- **Configuration**: YAML-based with environment variable overrides
- **Logging**: Structured logging with configurable levels

### White-Label Positioning
- Professional, independent branding
- Positioned as standalone REST API server
- Obsidian compatibility as a feature, not primary purpose
- Suitable for diverse use cases (CI/CD, cloud, CMS, automation)

### Documentation
- Comprehensive README with use cases
- API documentation (OpenAPI/Swagger)
- MCP integration guide (tested with with-context-mcp)
- Development setup guide
- Configuration reference
- Obsidian compatibility guide

### Testing
- 312 comprehensive tests
- 86% code coverage
- Tested with production MCP tooling
- All CRUD operations validated

### Credits
- API compatibility inspired by Obsidian Local REST API plugin by @coddingtonbear
- Independent implementation, not affiliated with Obsidian or Dynalist Inc.

---
