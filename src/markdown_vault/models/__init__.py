"""
Pydantic models for markdown-vault.

This module contains all data models used throughout the application,
providing type safety and validation.
"""

from markdown_vault.models.note import Note, NoteStat, NoteJson
from markdown_vault.models.config import (
    ServerConfig,
    VaultConfig,
    SecurityConfig,
    ObsidianConfig,
    PeriodicNoteConfig,
    SearchConfig,
    ActiveFileConfig,
    CommandsConfig,
    LoggingConfig,
    PerformanceConfig,
    AppConfig,
)
from markdown_vault.models.api import (
    ServerStatus,
    APIError,
    CommandInfo,
    PatchOperation,
    TargetType,
)

__all__ = [
    # Note models
    "Note",
    "NoteStat",
    "NoteJson",
    # Config models
    "ServerConfig",
    "VaultConfig",
    "SecurityConfig",
    "ObsidianConfig",
    "PeriodicNoteConfig",
    "SearchConfig",
    "ActiveFileConfig",
    "CommandsConfig",
    "LoggingConfig",
    "PerformanceConfig",
    "AppConfig",
    # API models
    "ServerStatus",
    "APIError",
    "CommandInfo",
    "PatchOperation",
    "TargetType",
]
