# Makefile for markdown-vault development

.PHONY: help build up down shell logs test lint format clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build development Docker image
	docker-compose -f docker-compose.dev.yml build

up: ## Start development environment
	docker-compose -f docker-compose.dev.yml up -d
	@echo ""
	@echo "Development environment started!"
	@echo "Access shell: make shell"
	@echo "View logs: make logs"

down: ## Stop development environment
	docker-compose -f docker-compose.dev.yml down

shell: ## Open shell in development container
	docker-compose -f docker-compose.dev.yml exec markdown-vault-dev bash

logs: ## View container logs
	docker-compose -f docker-compose.dev.yml logs -f

test: ## Run tests in container
	docker-compose -f docker-compose.dev.yml exec markdown-vault-dev pytest

test-cov: ## Run tests with coverage
	docker-compose -f docker-compose.dev.yml exec markdown-vault-dev pytest --cov=markdown_vault --cov-report=html --cov-report=term

lint: ## Run linters
	docker-compose -f docker-compose.dev.yml exec markdown-vault-dev ruff check src/

format: ## Format code
	docker-compose -f docker-compose.dev.yml exec markdown-vault-dev black src/ tests/

typecheck: ## Run type checking
	docker-compose -f docker-compose.dev.yml exec markdown-vault-dev mypy src/markdown_vault

install: ## Install package in development mode
	docker-compose -f docker-compose.dev.yml exec markdown-vault-dev pip install -e ".[dev]"

clean: ## Clean up containers and volumes
	docker-compose -f docker-compose.dev.yml down -v
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

restart: down up ## Restart development environment

rebuild: down build up ## Rebuild and restart

# Local development (without Docker)
venv: ## Create virtual environment
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -e ".[dev]"

local-test: ## Run tests locally
	pytest

local-lint: ## Run linters locally
	ruff check src/

local-format: ## Format code locally
	black src/ tests/

local-typecheck: ## Run type checking locally
	mypy src/markdown_vault
