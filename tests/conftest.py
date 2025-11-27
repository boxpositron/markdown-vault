"""
Pytest configuration and shared fixtures.
"""

import pytest
from pathlib import Path


@pytest.fixture
def test_vault_path() -> Path:
    """Return path to test vault."""
    return Path("/vault")


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

Some content here.

^block-123

## Section 2

More content here.
"""
