# markdown-vault: Project Summary

**Date**: November 27, 2025  
**Status**: Planning & Design Phase  
**Version**: 0.1.0 (Pre-release)

## What is markdown-vault?

**markdown-vault** is a standalone REST API service that replaces the Obsidian Local REST API plugin. It provides full programmatic access to markdown vaults without requiring Obsidian to be installed or running.

### Key Value Propositions

1. **Drop-in Replacement**: 100% API-compatible with Obsidian Local REST API plugin
2. **Dual-Mode Operation**:
   - **Standalone Mode**: Manage any markdown vault - no Obsidian needed
   - **Replacement Mode**: Point at an Obsidian vault to replace the plugin entirely
3. **True Independence**: Works without Obsidian being installed or running
4. **Deployment Flexibility**: Docker, systemd, or standalone binary
5. **Extensibility**: Plugin system and custom commands
6. **Always Available**: Service runs 24/7, unlike plugin that requires Obsidian to be open

## Documentation Overview

### Core Documents

1. **[README.md](../README.md)** - Main project documentation
   - Quick start guide
   - Installation instructions
   - Basic usage examples
   - API overview

2. **[RESEARCH.md](./RESEARCH.md)** - Original API analysis
   - Complete Obsidian REST API specification
   - Endpoint documentation
   - Technical implementation details
   - Compatibility requirements

3. **[PLAN.md](./PLAN.md)** - Implementation roadmap
   - Project structure
   - Development phases (6-8 weeks)
   - Technology stack decisions
   - Success criteria and milestones

### Configuration Files

1. **[config.example.yaml](../config/config.example.yaml)** - Standard configuration
   - Server settings
   - Vault configuration
   - Security options
   - Feature toggles

2. **[obsidian-integration.example.yaml](../config/obsidian-integration.example.yaml)** - Obsidian-specific setup
   - Vault path configuration
   - Config sync settings
   - Periodic notes integration

## Current State

### Completed
- ✅ Project structure created
- ✅ Comprehensive research and API analysis
- ✅ Detailed implementation plan (6-8 week timeline)
- ✅ Configuration system designed
- ✅ Docker deployment setup
- ✅ Python project scaffolding (pyproject.toml)
- ✅ Documentation framework

### In Progress
- 🔄 Core implementation (Phase 1)
- 🔄 Setting up development environment

### Not Started
- ⏳ API endpoint implementation
- ⏳ PATCH engine development
- ⏳ Periodic notes system
- ⏳ Search functionality
- ⏳ CLI tool
- ⏳ Test suite
- ⏳ Package publishing

## Development Phases

### Phase 1: Foundation (Week 1-2)
**Goal**: Basic API + Authentication + File Operations

**Deliverables**:
- FastAPI application with HTTPS
- API key authentication
- Basic CRUD endpoints for vault files
- Configuration loading system

### Phase 2: Markdown Processing (Week 2-3)
**Goal**: Advanced parsing + JSON format + Basic PATCH

**Deliverables**:
- JSON response format matching Obsidian API
- Heading hierarchy parsing
- Block reference resolution
- Basic PATCH operations

### Phase 3: Advanced Features (Week 3-4)
**Goal**: Complete PATCH + Periodic Notes + Search

**Deliverables**:
- Full PATCH engine (heading/block/frontmatter)
- Periodic notes system
- Search API with JSONLogic
- Active file tracking

### Phase 4: Obsidian Vault Compatibility (Week 4-5)
**Goal**: Support for Obsidian vault structures + Commands

**Deliverables**:
- Obsidian vault auto-detection (`.obsidian/` directory)
- Configuration import from `.obsidian/` settings
- Commands API (extensible plugin system)
- File watching for external changes (optional)
- Respect Obsidian's file exclusions and settings

### Phase 5: CLI & Deployment (Week 5)
**Goal**: CLI + Docker + Packaging

**Deliverables**:
- Full-featured CLI tool
- Docker images
- PyPI package
- Deployment guides

### Phase 6: Testing & Polish (Week 6)
**Goal**: Test coverage + Documentation + Release

**Deliverables**:
- 90%+ test coverage
- Performance benchmarks
- Complete documentation
- v1.0.0 release

## API Coverage

### Implemented: 0/31 endpoints

#### System (0/3)
- [ ] `GET /` - Server status
- [ ] `GET /openapi.yaml` - API specification
- [ ] `GET /obsidian-local-rest-api.crt` - SSL certificate

#### Vault (0/9)
- [ ] `GET /vault/` - List files
- [ ] `GET /vault/{filepath}` - Read file
- [ ] `PUT /vault/{filepath}` - Create/update file
- [ ] `POST /vault/{filepath}` - Append to file
- [ ] `PATCH /vault/{filepath}` - Partial update
- [ ] `DELETE /vault/{filepath}` - Delete file

#### Active File (0/6)
- [ ] `GET /active/` - Get active file
- [ ] `PUT /active/` - Update active file
- [ ] `POST /active/` - Append to active file
- [ ] `PATCH /active/` - Partial update
- [ ] `DELETE /active/` - Delete active file
- [ ] `POST /open/{filename}` - Open file

#### Periodic Notes (0/10)
- [ ] `GET /periodic/{period}/` - Get periodic note (5 periods)
- [ ] `PUT /periodic/{period}/` - Update periodic note (5 periods)
- [ ] `POST /periodic/{period}/` - Append (5 periods)
- [ ] `PATCH /periodic/{period}/` - Partial update (5 periods)
- [ ] `DELETE /periodic/{period}/` - Delete (5 periods)

#### Search (0/2)
- [ ] `POST /search/simple/` - Simple search
- [ ] `POST /search/` - JSONLogic search

#### Commands (0/2)
- [ ] `GET /commands/` - List commands
- [ ] `POST /commands/{commandId}/` - Execute command

## Technology Decisions

### Core Framework: FastAPI (Python 3.10+)
**Rationale**:
- Native OpenAPI 3.0 generation
- Excellent type safety with Pydantic
- High performance async/await support
- Great developer experience
- Strong ecosystem

### Key Libraries

| Purpose | Library | Reason |
|---------|---------|--------|
| Markdown parsing | python-frontmatter, markdown-it-py | Battle-tested, comprehensive |
| File I/O | aiofiles | Async file operations |
| Config | pydantic-settings, pyyaml | Type-safe configuration |
| SSL/TLS | cryptography | Industry standard |
| CLI | typer | Modern, intuitive CLI framework |
| Testing | pytest, httpx | Async testing support |

## Operating Modes

### Mode 1: Standalone Service
```yaml
vault:
  path: "/path/to/any/markdown/directory"
  auto_create: true

obsidian:
  enabled: false  # No Obsidian-specific features needed
```

**Use Cases**:
- Headless markdown management (no Obsidian required)
- CI/CD integration
- Server-side automation
- Custom markdown workflows
- Managing non-Obsidian vaults

**Key Point**: Obsidian is **not required** - this is a completely independent service.

### Mode 2: Drop-in Replacement for Obsidian Plugin
```yaml
vault:
  path: "/Users/me/ObsidianVault"
  auto_create: false

obsidian:
  enabled: true       # Respect .obsidian/ structure
  config_sync: true   # Import settings from Obsidian config
```

**Use Cases**:
- Replace Obsidian Local REST API plugin
- API access when Obsidian is closed
- Server/container deployment with Obsidian vaults
- More reliable API service than plugin
- Remote access to Obsidian vault

**Key Point**: Replaces the plugin - Obsidian **does not need to be running**. The service reads Obsidian's configuration files but operates independently.

## Deployment Options

### Docker (Recommended for Production)
```bash
docker-compose up -d
```

### Python Package
```bash
pip install markdown-vault
markdown-vault start --config config.yaml
```

### Systemd Service (Linux)
```bash
sudo systemctl enable markdown-vault
sudo systemctl start markdown-vault
```

## Next Steps

### For Developers
1. Set up development environment
2. Review [PLAN.md](./PLAN.md) for detailed implementation guide
3. Start with Phase 1: Foundation
4. Follow test-driven development (TDD)
5. Maintain >90% code coverage

### For Users (Once Released)
1. Install via pip or Docker
2. Copy `config.example.yaml` to `config.yaml`
3. Configure vault path and settings
4. Run `markdown-vault start`
5. Access API at `https://localhost:27123/docs`

## Contributing

See [PLAN.md](./PLAN.md) for development guidelines:
- Code standards (Black, Ruff, Mypy)
- Testing requirements
- Commit message conventions
- Pull request process

## Timeline

**Estimated Time to v1.0.0**: 6-8 weeks

- Week 1-2: Foundation
- Week 2-3: Markdown processing
- Week 3-4: Advanced features
- Week 4-5: Obsidian integration
- Week 5: CLI & deployment
- Week 6: Testing & release

**Target v1.0.0 Release**: Q1 2025

## Questions?

- Check [README.md](../README.md) for quick start
- Read [RESEARCH.md](./RESEARCH.md) for API details
- See [PLAN.md](./PLAN.md) for implementation specifics
- Review [config.example.yaml](../config/config.example.yaml) for configuration options

## License

MIT License - See [LICENSE](../LICENSE) for details

---

**Last Updated**: November 27, 2025  
**Project Status**: 📋 Planning Complete, 🚀 Ready for Development
