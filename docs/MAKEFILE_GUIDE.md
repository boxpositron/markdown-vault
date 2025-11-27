# Makefile Quick Reference Guide

This guide provides a comprehensive overview of all available Makefile commands for markdown-vault development.

## Quick Start

```bash
# Initial setup for new developers
make setup

# Start development environment
make up

# Open shell in container
make shell

# Run the server
make run-server

# Run tests
make test

# Run all quality checks
make qa
```

## Docker Development Environment

### Container Management

| Command | Description |
|---------|-------------|
| `make build` | Build development Docker image |
| `make build-prod` | Build production Docker image |
| `make up` | Start development environment (detached) |
| `make up-prod` | Start production environment |
| `make down` | Stop development environment |
| `make down-prod` | Stop production environment |
| `make restart` | Restart development environment |
| `make restart-prod` | Restart production environment |
| `make rebuild` | Rebuild and restart development |
| `make rebuild-prod` | Rebuild and restart production |

### Container Access

| Command | Description |
|---------|-------------|
| `make shell` | Open bash shell in dev container |
| `make shell-root` | Open bash shell as root |
| `make shell-prod` | Open shell in production container |
| `make logs` | View and follow container logs |
| `make logs-prod` | View production container logs |
| `make logs-tail` | View last 50 lines of logs |
| `make ps` | Show running containers |

### Container Monitoring

| Command | Description |
|---------|-------------|
| `make stats` | Show container resource usage |
| `make inspect` | Inspect development container |
| `make env` | Show environment variables |

## Server Management

| Command | Description |
|---------|-------------|
| `make run-server` | Run server in development mode with auto-reload |
| `make run-server-config` | Run server with custom config file |
| `make version` | Show version information |

**Example - Starting the server:**

```bash
# Start development environment
make up

# In another terminal, run the server
make run-server

# Or run with custom config
make run-server-config
```

## Testing

| Command | Description |
|---------|-------------|
| `make test` | Run all tests with verbose output |
| `make test-cov` | Run tests with coverage report |
| `make test-watch` | Run tests in watch mode (auto-rerun) |
| `make test-failed` | Run only previously failed tests |
| `make test-file FILE=<name>` | Run tests in specific file |

**Example - Running specific tests:**

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
make test-file FILE=test_config.py

# Run only failed tests
make test-failed
```

## Code Quality

| Command | Description |
|---------|-------------|
| `make lint` | Run linters (ruff) |
| `make lint-fix` | Run linters with auto-fix |
| `make format` | Format code with black |
| `make format-check` | Check formatting without changes |
| `make typecheck` | Run type checking with mypy |
| `make qa` | Run all quality assurance checks |

**Recommended workflow:**

```bash
# Before committing code
make format      # Format code
make lint-fix    # Fix linting issues
make typecheck   # Check types
make test        # Run tests

# Or run all at once
make qa
```

## Package Management

| Command | Description |
|---------|-------------|
| `make install` | Install package in development mode |
| `make install-prod` | Install package in production mode |
| `make pip-list` | Show installed packages |
| `make pip-outdated` | Show outdated packages |

## Vault Management

| Command | Description |
|---------|-------------|
| `make init-vault` | Initialize test vault directory |
| `make clean-vault` | Clean test vault directory |
| `make backup-vault` | Backup test vault with timestamp |

**Example:**

```bash
# Create test vault with sample files
make init-vault

# Backup before making changes
make backup-vault

# Clean vault
make clean-vault
```

## Cleanup

| Command | Description |
|---------|-------------|
| `make clean` | Clean containers, volumes, and cache |
| `make clean-all` | Clean everything including Docker images |
| `make prune` | Prune Docker system (removes ALL unused resources) |

**Warning:** `make prune` will remove ALL unused Docker resources, not just markdown-vault!

## Local Development (without Docker)

For developers who prefer local development without Docker:

| Command | Description |
|---------|-------------|
| `make venv` | Create local virtual environment |
| `make local-test` | Run tests locally |
| `make local-test-cov` | Run tests with coverage locally |
| `make local-lint` | Run linters locally |
| `make local-lint-fix` | Run linters with auto-fix locally |
| `make local-format` | Format code locally |
| `make local-typecheck` | Run type checking locally |
| `make local-qa` | Run all QA checks locally |
| `make local-run` | Run server locally |

**Local setup workflow:**

```bash
# Create virtual environment
make venv

# Activate it
source venv/bin/activate

# Run locally
make local-run

# Run tests locally
make local-test
```

## Common Workflows

### New Developer Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd markdown-vault

# 2. Run setup (builds image, creates test vault)
make setup

# 3. Start environment
make up

# 4. Open shell and explore
make shell
```

### Daily Development

```bash
# Start environment (if not running)
make up

# Run server in development mode
make run-server

# In another terminal, run tests as you develop
make test-watch

# Before committing
make qa
```

### Running Tests

```bash
# Start environment
make up

# Run all tests
make test

# Run with coverage
make test-cov

# Run specific file
make test-file FILE=test_api.py
```

### Code Quality Checks

```bash
# Format and fix issues
make format
make lint-fix

# Check types
make typecheck

# Run all checks
make qa
```

### Debugging

```bash
# Open shell in container
make shell

# Run commands manually
python -m markdown_vault --help
pytest -v tests/
python -c "from markdown_vault.main import create_app; print('ok')"

# Check environment
make env

# View logs
make logs
```

### Production Testing

```bash
# Build production image
make build-prod

# Start production environment
make up-prod

# Check logs
make logs-prod

# Open shell to inspect
make shell-prod
```

### Cleanup

```bash
# Clean development environment
make clean

# Complete cleanup (removes images too)
make clean-all

# If you need to free up Docker space
make prune
```

## Tips and Tricks

### Running Multiple Commands

```bash
# Chain commands
make format && make lint && make test

# Or use qa target
make qa
```

### Accessing Container Files

```bash
# Copy file from container to host
docker cp markdown-vault-dev:/app/somefile.txt .

# Copy file from host to container
docker cp somefile.txt markdown-vault-dev:/app/
```

### Custom Docker Compose

```bash
# Run custom docker-compose commands
docker-compose -f docker-compose.dev.yml <command>

# Examples:
docker-compose -f docker-compose.dev.yml ps
docker-compose -f docker-compose.dev.yml exec markdown-vault-dev bash
```

### Environment Variables

Set environment variables for the container by editing `docker-compose.dev.yml`:

```yaml
environment:
  - MARKDOWN_VAULT_LOG_LEVEL=DEBUG
  - MARKDOWN_VAULT_VAULT__PATH=/vault
```

Or use `.env` file in project root:

```bash
# .env
MARKDOWN_VAULT_API_KEY=your-key-here
MARKDOWN_VAULT_LOG_LEVEL=DEBUG
```

## Troubleshooting

### Container won't start

```bash
# Check logs
make logs

# Rebuild from scratch
make clean-all
make build
make up
```

### Permission issues

```bash
# Open shell as root
make shell-root

# Fix permissions
chown -R $(id -u):$(id -g) /app
```

### Port already in use

Edit `docker-compose.dev.yml` and change port mapping:

```yaml
ports:
  - "27124:27123"  # Use different host port
```

### Out of disk space

```bash
# Clean up Docker resources
make prune

# Check Docker disk usage
docker system df
```

## Additional Resources

- **Main Documentation**: [README.md](../README.md)
- **Configuration Guide**: [CONFIGURATION.md](./CONFIGURATION.md)
- **Development Guide**: [README.dev.md](../README.dev.md)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)

## Getting Help

- Run `make help` to see all available commands
- Check container logs: `make logs`
- Open an issue on GitHub if you encounter problems
- Join our community discussions
