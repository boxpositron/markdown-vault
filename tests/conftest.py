"""
Pytest configuration and shared fixtures.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
from markdown_vault.core.vault import VaultManager
from markdown_vault.main import create_app


@pytest.fixture
def sample_vault_path() -> Path:
    """Return path to sample vault fixtures."""
    return Path(__file__).parent / "fixtures" / "sample_vault"


@pytest.fixture
def temp_vault() -> Generator[Path, None, None]:
    """Create a temporary vault directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def vault_with_fixtures(
    sample_vault_path: Path, temp_vault: Path
) -> Generator[Path, None, None]:
    """Create a temporary vault pre-populated with fixture files."""
    # Copy all fixture files to temp vault
    for item in sample_vault_path.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(sample_vault_path)
            dest = temp_vault / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest)

    yield temp_vault


@pytest.fixture
def vault_manager(vault_with_fixtures: Path) -> VaultManager:
    """Create a VaultManager instance for testing."""
    return VaultManager(vault_with_fixtures)


@pytest.fixture
def test_app_config(temp_vault: Path) -> AppConfig:
    """Create test application configuration."""
    return AppConfig(
        vault=VaultConfig(path=str(temp_vault)),
        security=SecurityConfig(api_key="test-api-key-123"),
    )


@pytest.fixture
def test_app(test_app_config: AppConfig) -> TestClient:
    """Create FastAPI test client."""
    app = create_app(test_app_config)
    return TestClient(app)


@pytest.fixture
def api_headers() -> dict[str, str]:
    """Return headers with valid API key."""
    return {"Authorization": "Bearer test-api-key-123"}


@pytest.fixture
def sample_note_content() -> str:
    """Return sample note content for testing."""
    return """---
title: Test Note
tags: [test, example]
created: 2025-01-01
---

# Test Note

This is a test note for development.

## Section 1

Some content here with #inline-tag.

^block-123

## Section 2

More content here.
"""
