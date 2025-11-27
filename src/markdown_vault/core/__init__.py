"""Core functionality for markdown-vault."""

from markdown_vault.core.config import (
    ConfigError,
    load_config,
    generate_api_key,
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
    "load_config",
    "generate_api_key",
    "resolve_api_key",
    "VaultManager",
    "VaultError",
    "FileNotFoundError",
    "InvalidPathError",
]
