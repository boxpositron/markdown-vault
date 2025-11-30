"""
Pydantic models for markdown-vault.

This module contains all data models used throughout the application,
providing type safety and validation.
"""

from markdown_vault.models.api import (
    APIError,
    CommandInfo,
    PatchOperation,
    ServerStatus,
    TargetType,
)
from markdown_vault.models.config import (
    ActiveFileConfig,
    AppConfig,
    CommandsConfig,
    LoggingConfig,
    ObsidianConfig,
    PerformanceConfig,
    PeriodicNoteConfig,
    SearchConfig,
    SecurityConfig,
    ServerConfig,
    VaultConfig,
)
from markdown_vault.models.note import Note, NoteJson, NoteStat

__all__ = [
    "APIError",
    "ActiveFileConfig",
    "AppConfig",
    "CommandInfo",
    "CommandsConfig",
    "LoggingConfig",
    # Note models
    "Note",
    "NoteJson",
    "NoteStat",
    "ObsidianConfig",
    "PatchOperation",
    "PerformanceConfig",
    "PeriodicNoteConfig",
    "SearchConfig",
    "SecurityConfig",
    # Config models
    "ServerConfig",
    # API models
    "ServerStatus",
    "TargetType",
    "VaultConfig",
]
