# Development Environment Setup

This guide explains how to set up the Docker-based development environment for markdown-vault.

## Prerequisites

- Docker Desktop (for macOS/Windows) or Docker Engine + Docker Compose (for Linux)
- Git
- Make (optional, but recommended)

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

## Running the Server (When Ready)

Once we've built the FastAPI app:

```bash
# Inside container
uvicorn markdown_vault.main:app --reload --host 0.0.0.0 --port 27123

# Or from host (after we add a start script)
make run
```

Access the API at: `http://localhost:27123`

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

## Local Development (Without Docker)

If you prefer to develop without Docker:

### Setup

```bash
make venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Development

```bash
make local-test
make local-lint
make local-format
make local-typecheck
```

## Tips

1. **Keep container running**: The dev container stays running with `tail -f /dev/null`
2. **Live reloading**: Source code changes are immediately available
3. **Multiple shells**: Open multiple shells with `make shell`
4. **Watch mode**: Use `pytest --watch` for continuous testing (install pytest-watch)
5. **Debugging**: Add `import pdb; pdb.set_trace()` in your code

## Next Steps

After setting up the environment:

1. Run `make test` to verify everything works
2. Start implementing features
3. Run tests frequently with `make test`
4. Check code quality with `make lint && make typecheck`
5. Format before committing with `make format`

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
