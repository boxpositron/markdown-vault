# Development Environment Setup

This guide explains how to set up your development environment for markdown-vault.

## Recommended Setup: uv

We recommend using **uv** for local development - it's a fast, modern Python package manager that makes dependency management a breeze. See [Local Development with uv](#local-development-with-uv-recommended) section below.

```bash
# Quick start with uv
uv venv && uv sync
source .venv/bin/activate
uv run pytest
```

Alternatively, you can use Docker for a containerized development environment.

## Prerequisites

- **uv** (recommended) - Fast Python package installer and resolver: `pip install uv`
- **OR** Docker Desktop (for macOS/Windows) or Docker Engine + Docker Compose (for Linux)
- Git
- Make (optional, but recommended)
- Python 3.10 or higher

## Quick Start

### Using Make (Recommended)

```bash
# Build development image
make build

# Start development environment
make up

# Open shell in container
make shell

# View logs
make logs

# Run tests
make test

# Stop environment
make down
```

### Without Make

```bash
# Build development image
docker-compose -f docker-compose.dev.yml build

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Open shell in container
docker-compose -f docker-compose.dev.yml exec markdown-vault-dev bash

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop environment
docker-compose -f docker-compose.dev.yml down
```

## Development Workflow

### 1. Start the Environment

```bash
make build  # First time only
make up
```

This starts a container with:
- Python 3.10
- All development dependencies installed
- Source code mounted for live editing
- Test vault directory
- Port 27123 exposed

### 2. Open a Shell

```bash
make shell
```

Inside the container, you have access to:
- `pytest` - Run tests
- `black` - Format code
- `ruff` - Lint code
- `mypy` - Type checking
- Python interpreter with your code

### 3. Make Code Changes

Edit files on your host machine. Changes are immediately reflected in the container due to volume mounts:

```
./src/markdown_vault/  → /app/src/markdown_vault/  (in container)
```

### 4. Run Tests

```bash
# Inside container
pytest

# Or from host
make test
```

### 5. Format and Lint

```bash
# Format code
make format

# Lint code
make lint

# Type check
make typecheck
```

## Directory Structure

```
markdown-vault/
├── src/                    # Source code (mounted)
├── tests/                  # Tests (mounted)
├── test_vault/             # Test vault directory (mounted)
├── config/                 # Config files (mounted)
├── certs/                  # SSL certificates (mounted)
├── logs/                   # Log files (mounted)
├── Dockerfile.dev          # Development Dockerfile
├── docker-compose.dev.yml  # Development compose file
└── Makefile               # Development commands
```

## Environment Variables

Set in `docker-compose.dev.yml`:

```yaml
environment:
  - MARKDOWN_VAULT_LOG_LEVEL=DEBUG
  - MARKDOWN_VAULT_VAULT__PATH=/vault
  - MARKDOWN_VAULT_SERVER__RELOAD=true
```

You can override these or add more as needed.

## Running the Server

The server is fully implemented with all 29 endpoints. Start it using:

```bash
# Using the CLI (recommended)
python -m markdown_vault start --config test_config.yaml

# Or using uvicorn directly
uvicorn markdown_vault.main:app --reload --host 0.0.0.0 --port 27125

# Using Docker
make run-server
```

Access the API at: `https://localhost:27125`
- API Documentation: `https://localhost:27125/docs`
- OpenAPI Spec: `https://localhost:27125/openapi.yaml`

**Note**: Server uses HTTPS with self-signed certificates by default.

## Testing

### Run All Tests

```bash
make test
```

### Run Specific Tests

```bash
# Inside container
pytest tests/test_vault.py
pytest tests/test_vault.py::test_specific_function
```

### Run with Coverage

```bash
make test-cov
```

Coverage report will be in `htmlcov/index.html`.

## Code Quality

### Format Code

```bash
make format
```

### Lint Code

```bash
make lint
```

### Type Check

```bash
make typecheck
```

### Run All Checks

```bash
make lint && make typecheck && make test
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
make logs

# Rebuild from scratch
make rebuild
```

### Port Already in Use

Stop any process using port 27123:

```bash
# Check what's using the port
lsof -i :27123

# Kill the process
kill -9 <PID>
```

Or change the port in `docker-compose.dev.yml`.

### Permission Issues

If you encounter permission issues with mounted volumes:

```bash
# Inside container, check user
whoami
id

# Fix ownership (if needed)
sudo chown -R $(whoami):$(whoami) ./src ./tests
```

### Clean Everything

```bash
make clean
```

This removes containers, volumes, and cache files.

## Local Development with uv (Recommended)

`uv` is a fast Python package installer and resolver that makes dependency management much faster and more reliable.

### Prerequisites

Install `uv` if you haven't already:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Or with homebrew
brew install uv
```

### Setup

```bash
# Create virtual environment and install dependencies
make venv

# Or manually
uv venv           # Creates .venv/
uv sync           # Installs all dependencies from lock file

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Development Workflow

```bash
# Sync dependencies (after pulling changes)
make sync
# or: uv sync

# Run tests
make local-test
# or: uv run pytest

# Run tests with coverage
make local-test-cov
# or: uv run pytest --cov=markdown_vault

# Lint code
make local-lint
# or: uv run ruff check src/ tests/

# Format code
make local-format
# or: uv run black src/ tests/

# Type check
make local-typecheck
# or: uv run mypy src/markdown_vault

# Run all QA checks
make local-qa

# Run the server
make local-run
# or: uv run python -m markdown_vault start --reload
```

### Adding Dependencies

```bash
# Add a runtime dependency
make local-add PKG=requests
# or: uv add requests

# Add a development dependency
make local-add-dev PKG=pytest-watch
# or: uv add --dev pytest-watch

# Remove a dependency
uv remove package-name
```

### Why uv?

- **Fast**: 10-100x faster than pip for installing packages
- **Reliable**: Produces consistent, reproducible environments with lock files
- **Simple**: Single tool for virtual environments and package management
- **Modern**: Built-in support for pyproject.toml
- **Compatible**: Works with existing pip/PyPI ecosystem

### uv Commands Reference

| Command | Description |
|---------|-------------|
| `uv venv` | Create a virtual environment in `.venv/` |
| `uv sync` | Install dependencies from lock file |
| `uv add <pkg>` | Add a dependency |
| `uv add --dev <pkg>` | Add a dev dependency |
| `uv remove <pkg>` | Remove a dependency |
| `uv run <cmd>` | Run a command in the virtual environment |
| `uv pip list` | List installed packages |
| `uv lock` | Update the lock file |

## Traditional Development (Without uv or Docker)

If you prefer traditional Python virtual environments:

### Setup

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Development

```bash
pytest -v
ruff check src/ tests/
black src/ tests/
mypy src/markdown_vault
```

## Tips

1. **Keep container running**: The dev container stays running with `tail -f /dev/null`
2. **Live reloading**: Source code changes are immediately available
3. **Multiple shells**: Open multiple shells with `make shell`
4. **Watch mode**: Use `pytest --watch` for continuous testing (install pytest-watch)
5. **Debugging**: Add `import pdb; pdb.set_trace()` in your code

## Development Workflow

Standard development cycle:

1. **Run tests**: `make test` - All 312 tests should pass
2. **Start server**: `python -m markdown_vault start --config test_config.yaml`
3. **Make changes**: Edit code, tests auto-mount via Docker volumes
4. **Test changes**: `pytest tests/test_your_feature.py -v`
5. **Check quality**: `make qa` (runs lint, format, typecheck, test)
6. **Commit**: Small, focused commits with conventional commit messages

## Testing with MCP

Test the server with with-context-mcp:

```bash
# Set environment
export OBSIDIAN_API_URL="https://127.0.0.1:27125"
export OBSIDIAN_API_KEY="your-api-key-here"
export OBSIDIAN_VAULT="test_vault"

# Start server
python -m markdown_vault start --config test_config.yaml

# In another terminal, use MCP tools in OpenCode
# See docs/MCP_TESTING.md for detailed instructions
```

## Make Commands Reference

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make build` | Build Docker image |
| `make up` | Start environment |
| `make down` | Stop environment |
| `make shell` | Open container shell |
| `make logs` | View container logs |
| `make test` | Run tests |
| `make test-cov` | Run tests with coverage |
| `make lint` | Run linter |
| `make format` | Format code |
| `make typecheck` | Run type checking |
| `make clean` | Clean up everything |
| `make restart` | Restart environment |
| `make rebuild` | Rebuild and restart |

---

**Happy coding!** 🚀

## Project Status

**Current State**: Feature Complete (v1.0.0-rc)

- ✅ **29/29 Endpoints Implemented**
  - System (3), Vault (6), Active File (6), Periodic Notes (10), Search (2), Commands (2)
- ✅ **312 Tests** (98% passing)
- ✅ **86% Code Coverage**
- ✅ **MCP Integration Validated**
- ✅ **Production Ready**

### What's Working

All core features are fully functional:
- File CRUD operations
- PATCH operations (heading/block/frontmatter targeting)
- Active file tracking with sessions
- Periodic notes (daily/weekly/monthly/quarterly/yearly)
- Full-text and JSONLogic search
- Command system with built-in commands

### Performance

- Average response time: <50ms for file operations
- Handles concurrent requests
- Async I/O throughout
- Efficient markdown parsing

See `docs/SESSION_COMPLETE.md` for full implementation details.

