"""Core functionality for markdown-vault."""

from markdown_vault.core.config import (
    ConfigError,
    generate_api_key,
    load_config,
    resolve_api_key,
)
from markdown_vault.core.vault import (
    FileNotFoundError,
    InvalidPathError,
    VaultError,
    VaultManager,
)

__all__ = [
    "ConfigError",
    "FileNotFoundError",
    "InvalidPathError",
    "VaultError",
    "VaultManager",
    "generate_api_key",
    "load_config",
    "resolve_api_key",
]
