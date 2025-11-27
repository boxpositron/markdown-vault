# Agent Guidelines for markdown-vault

## Build/Test Commands
- **Run all tests**: `make test` or `pytest`
- **Run single test**: `pytest tests/test_file.py::test_function_name -v`
- **Run with coverage**: `make test-cov` or `pytest --cov=markdown_vault --cov-report=term-missing`
- **Lint code**: `make lint` or `ruff check src/ tests/`
- **Format code**: `make format` or `black src/ tests/`
- **Type check**: `make typecheck` or `mypy src/markdown_vault`
- **Run all QA**: `make qa` (runs lint, format, typecheck, test)
- **Run server**: `make run-server` or `python -m markdown_vault start --reload`
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
