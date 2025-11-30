# Makefile for markdown-vault development
# Provides commands for Docker-based and local development workflows

.PHONY: help build up down shell logs test lint format clean
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Docker Compose files
DEV_COMPOSE := docker-compose.dev.yml
PROD_COMPOSE := docker-compose.yml

help: ## Show this help message
	@echo '$(GREEN)markdown-vault Development Commands$(RESET)'
	@echo ''
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}'

# ==========================================
# Docker Development Environment
# ==========================================

build: ## Build development Docker image
	@echo "$(YELLOW)Building development Docker image...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) build
	@echo "$(GREEN)✓ Build complete!$(RESET)"

build-prod: ## Build production Docker image
	@echo "$(YELLOW)Building production Docker image...$(RESET)"
	docker-compose -f $(PROD_COMPOSE) build
	@echo "$(GREEN)✓ Production build complete!$(RESET)"

up: ## Start development environment
	@echo "$(YELLOW)Starting development environment...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) up -d
	@echo ""
	@echo "$(GREEN)✓ Development environment started!$(RESET)"
	@echo ""
	@echo "Useful commands:"
	@echo "  $(BLUE)make shell$(RESET)      - Open shell in container"
	@echo "  $(BLUE)make logs$(RESET)       - View container logs"
	@echo "  $(BLUE)make run-server$(RESET) - Start the server"
	@echo "  $(BLUE)make test$(RESET)       - Run tests"

up-prod: ## Start production environment
	@echo "$(YELLOW)Starting production environment...$(RESET)"
	docker-compose -f $(PROD_COMPOSE) up -d
	@echo "$(GREEN)✓ Production environment started!$(RESET)"

down: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) down
	@echo "$(GREEN)✓ Stopped$(RESET)"

down-prod: ## Stop production environment
	@echo "$(YELLOW)Stopping production environment...$(RESET)"
	docker-compose -f $(PROD_COMPOSE) down
	@echo "$(GREEN)✓ Stopped$(RESET)"

restart: down up ## Restart development environment

restart-prod: down-prod up-prod ## Restart production environment

rebuild: down build up ## Rebuild and restart development environment

rebuild-prod: down-prod build-prod up-prod ## Rebuild and restart production environment

# ==========================================
# Container Access
# ==========================================

shell: ## Open bash shell in development container
	@echo "$(BLUE)Opening shell in development container...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev bash

shell-root: ## Open bash shell as root in development container
	@echo "$(BLUE)Opening root shell in development container...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec -u root markdown-vault-dev bash

shell-prod: ## Open shell in production container
	@echo "$(BLUE)Opening shell in production container...$(RESET)"
	docker-compose -f $(PROD_COMPOSE) exec markdown-vault bash

logs: ## View development container logs (follow)
	docker-compose -f $(DEV_COMPOSE) logs -f

logs-prod: ## View production container logs (follow)
	docker-compose -f $(PROD_COMPOSE) logs -f

logs-tail: ## View last 50 lines of development logs
	docker-compose -f $(DEV_COMPOSE) logs --tail=50

ps: ## Show running containers
	@echo "$(YELLOW)Development containers:$(RESET)"
	@docker-compose -f $(DEV_COMPOSE) ps
	@echo ""
	@echo "$(YELLOW)Production containers:$(RESET)"
	@docker-compose -f $(PROD_COMPOSE) ps

# ==========================================
# Server Management
# ==========================================

run-server: ## Run the server in development mode
	@echo "$(GREEN)Starting markdown-vault server in development mode...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		python -m markdown_vault start --reload

run-server-config: ## Run server with custom config file
	@echo "$(GREEN)Starting server with custom config...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		python -m markdown_vault start --config /config/config.yaml

stop-server: ## Stop the running server (if started with run-server)
	@echo "$(YELLOW)Stopping server (send Ctrl+C in the terminal running the server)$(RESET)"

# ==========================================
# Testing
# ==========================================

test: ## Run all tests in container
	@echo "$(YELLOW)Running tests...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev pytest -v
	@echo "$(GREEN)✓ Tests complete!$(RESET)"

test-cov: ## Run tests with coverage report
	@echo "$(YELLOW)Running tests with coverage...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		pytest --cov=markdown_vault --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(RESET)"

test-watch: ## Run tests in watch mode
	@echo "$(YELLOW)Running tests in watch mode...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		pytest-watch

test-failed: ## Run only failed tests
	@echo "$(YELLOW)Running only failed tests...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		pytest --lf -v

test-file: ## Run tests in specific file (usage: make test-file FILE=test_api.py)
	@echo "$(YELLOW)Running tests in $(FILE)...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		pytest tests/$(FILE) -v

# ==========================================
# Code Quality
# ==========================================

lint: ## Run linters (ruff)
	@echo "$(YELLOW)Running linters...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		ruff check src/ tests/
	@echo "$(GREEN)✓ Linting complete!$(RESET)"

lint-fix: ## Run linters and auto-fix issues
	@echo "$(YELLOW)Running linters with auto-fix...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		ruff check --fix src/ tests/
	@echo "$(GREEN)✓ Auto-fix complete!$(RESET)"

format: ## Format code with black
	@echo "$(YELLOW)Formatting code...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		black src/ tests/
	@echo "$(GREEN)✓ Formatting complete!$(RESET)"

format-check: ## Check code formatting without changes
	@echo "$(YELLOW)Checking code format...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		black --check src/ tests/

typecheck: ## Run type checking with mypy
	@echo "$(YELLOW)Running type checks...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		mypy src/markdown_vault
	@echo "$(GREEN)✓ Type checking complete!$(RESET)"

qa: lint format typecheck test ## Run all quality assurance checks

# ==========================================
# Package Management
# ==========================================

install: ## Install package in development mode (Docker)
	@echo "$(YELLOW)Installing package in development mode...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		uv sync
	@echo "$(GREEN)✓ Installation complete!$(RESET)"

install-prod: ## Install package in production mode (Docker)
	@echo "$(YELLOW)Installing package in production mode...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		uv sync --no-dev
	@echo "$(GREEN)✓ Installation complete!$(RESET)"

uv-list: ## Show installed packages (Docker)
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev uv pip list

uv-outdated: ## Show outdated packages (Docker)
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev uv pip list --outdated

uv-add: ## Add a new dependency (usage: make uv-add PKG=package-name)
	@echo "$(YELLOW)Adding package $(PKG)...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		uv add $(PKG)
	@echo "$(GREEN)✓ Package added!$(RESET)"

uv-add-dev: ## Add a new dev dependency (usage: make uv-add-dev PKG=package-name)
	@echo "$(YELLOW)Adding dev package $(PKG)...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		uv add --dev $(PKG)
	@echo "$(GREEN)✓ Dev package added!$(RESET)"

# ==========================================
# Database/Vault Management
# ==========================================

init-vault: ## Initialize test vault directory
	@echo "$(YELLOW)Initializing test vault...$(RESET)"
	mkdir -p test_vault
	@echo "# Test Note" > test_vault/test.md
	@echo "This is a test note." >> test_vault/test.md
	@echo "$(GREEN)✓ Test vault initialized at test_vault/$(RESET)"

clean-vault: ## Clean test vault directory
	@echo "$(YELLOW)Cleaning test vault...$(RESET)"
	rm -rf test_vault/*
	@echo "$(GREEN)✓ Test vault cleaned$(RESET)"

backup-vault: ## Backup test vault
	@echo "$(YELLOW)Backing up vault...$(RESET)"
	tar -czf vault-backup-$$(date +%Y%m%d-%H%M%S).tar.gz test_vault/
	@echo "$(GREEN)✓ Vault backed up$(RESET)"

# ==========================================
# Cleanup
# ==========================================

clean: ## Clean up containers, volumes, and cache files
	@echo "$(YELLOW)Cleaning up...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) down -v
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete!$(RESET)"

clean-all: clean ## Clean everything including Docker images
	@echo "$(YELLOW)Removing Docker images...$(RESET)"
	docker-compose -f $(DEV_COMPOSE) down -v --rmi all
	docker-compose -f $(PROD_COMPOSE) down -v --rmi all
	@echo "$(GREEN)✓ Complete cleanup done!$(RESET)"

prune: ## Prune Docker system (careful!)
	@echo "$(RED)This will remove all unused Docker resources!$(RESET)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker system prune -af --volumes; \
		echo "$(GREEN)✓ Docker system pruned$(RESET)"; \
	fi

# ==========================================
# Local Development (without Docker)
# ==========================================

venv: ## Create local virtual environment with uv
	@echo "$(YELLOW)Creating virtual environment with uv...$(RESET)"
	uv venv
	@echo "$(YELLOW)Installing dependencies...$(RESET)"
	uv sync
	@echo "$(GREEN)✓ Virtual environment created!$(RESET)"
	@echo "Activate with: source .venv/bin/activate"

sync: ## Sync dependencies with uv (local)
	@echo "$(YELLOW)Syncing dependencies...$(RESET)"
	uv sync
	@echo "$(GREEN)✓ Dependencies synced!$(RESET)"

local-test: ## Run tests locally
	uv run pytest -v

local-test-cov: ## Run tests with coverage locally
	uv run pytest --cov=markdown_vault --cov-report=html --cov-report=term-missing

local-lint: ## Run linters locally
	uv run ruff check src/ tests/

local-lint-fix: ## Run linters with auto-fix locally
	uv run ruff check --fix src/ tests/

local-format: ## Format code locally
	uv run black src/ tests/

local-typecheck: ## Run type checking locally
	uv run mypy src/markdown_vault

local-qa: local-lint local-format local-typecheck local-test ## Run all QA checks locally

local-run: ## Run server locally
	uv run python -m markdown_vault start --reload

local-add: ## Add a dependency locally (usage: make local-add PKG=package-name)
	@echo "$(YELLOW)Adding package $(PKG)...$(RESET)"
	uv add $(PKG)
	@echo "$(GREEN)✓ Package added!$(RESET)"

local-add-dev: ## Add a dev dependency locally (usage: make local-add-dev PKG=package-name)
	@echo "$(YELLOW)Adding dev package $(PKG)...$(RESET)"
	uv add --dev $(PKG)
	@echo "$(GREEN)✓ Dev package added!$(RESET)"

# ==========================================
# Utilities
# ==========================================

version: ## Show version information
	@docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev \
		python -m markdown_vault version

env: ## Show environment variables in container
	@docker-compose -f $(DEV_COMPOSE) exec markdown-vault-dev env | sort

inspect: ## Inspect development container
	@docker inspect markdown-vault-dev

stats: ## Show container resource usage
	docker stats markdown-vault-dev --no-stream

# ==========================================
# Documentation
# ==========================================

docs-serve: ## Serve documentation locally (if implemented)
	@echo "$(YELLOW)Documentation not yet implemented$(RESET)"

setup: build init-vault ## Initial setup for new developers
	@echo ""
	@echo "$(GREEN)✓ Setup complete!$(RESET)"
	@echo ""
	@echo "Quick start:"
	@echo "  1. $(BLUE)make up$(RESET)         - Start the development environment"
	@echo "  2. $(BLUE)make shell$(RESET)      - Open a shell in the container"
	@echo "  3. $(BLUE)make run-server$(RESET) - Start the server"
	@echo ""
	@echo "Run $(BLUE)make help$(RESET) to see all available commands"
