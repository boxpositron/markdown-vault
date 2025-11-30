# Agent Guidelines for markdown-vault

## Build/Test Commands

### Local Development (with uv - PREFERRED)
- **Run all tests**: `make local-test` or `uv run pytest`
- **Run single test**: `uv run pytest tests/test_file.py::test_function_name -v`
- **Run with coverage**: `make local-test-cov` or `uv run pytest --cov=markdown_vault --cov-report=term-missing`
- **Lint code**: `make local-lint` or `uv run ruff check src/ tests/`
- **Auto-fix lint**: `make local-lint-fix` or `uv run ruff check --fix src/ tests/`
- **Format code**: `make local-format` or `uv run black src/ tests/`
- **Type check (mypy)**: `make local-typecheck` or `uv run mypy src/markdown_vault`
- **Type check (pyright)**: `make local-typecheck-pyright` or `uv run pyright src/markdown_vault`
- **Type check (both)**: `make local-typecheck-all`
- **Run all QA**: `make local-qa` (runs lint, format, typecheck, test in clean env)
- **Run server**: `make local-run` or `uv run python -m markdown_vault start --reload`

### Docker Development
- **Run all tests**: `make test` or `pytest`
- **Lint code**: `make lint` or `ruff check src/ tests/`
- **Format code**: `make format` or `black src/ tests/`
- **Type check (mypy)**: `make typecheck` or `mypy src/markdown_vault`
- **Type check (pyright)**: `make typecheck-pyright` or `pyright src/markdown_vault`
- **Type check (both)**: `make typecheck-all`
- **Run all QA**: `make qa` (runs lint, format, typecheck, test)
- **Docker shell**: `make shell` (for Docker development)

## Code Style
- **Python**: 3.10+ with type hints required on all functions (mypy strict mode)
- **Formatting**: Black (88 char line length), imports sorted with isort via ruff
- **Imports**: Standard library → third-party → local (use `from` for specific imports)
- **Types**: Use `from typing import` for generics, use `Type | None` (PEP 604) not `Optional[Type]`
- **Async**: Use `async def` for I/O operations, always type annotate return as `-> ReturnType`
- **Docstrings**: Google style with Args/Returns/Raises sections (triple quotes on separate lines)
- **Naming**: `snake_case` for functions/vars, `PascalCase` for classes, `UPPER_CASE` for constants
- **Errors**: Custom exceptions inherit from base (e.g., `ConfigError(Exception)`), use HTTPException in routes
- **FastAPI**: Use dependency injection via `Depends()`, type aliases like `ConfigDep = Annotated[AppConfig, Depends(get_config)]`
- **Config**: Pydantic v2 models with `BaseModel` or `BaseSettings`, use `Field()` for defaults/validation
- **Files**: Use `pathlib.Path` not strings, `async with aiofiles.open()` for async file I/O
- **Testing**: Pytest with async support (`pytest-asyncio`), use `TestClient` for FastAPI routes
