"""
Pydantic models for application configuration.

Uses pydantic-settings for environment variable support and validation.
"""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerConfig(BaseModel):
    """Server configuration."""

    host: str = Field(default="127.0.0.1", description="Server bind address")
    port: int = Field(default=27123, description="Server port")
    https: bool = Field(default=True, description="Enable HTTPS")
    reload: bool = Field(default=False, description="Auto-reload on code changes")

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port number."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v


class VaultConfig(BaseModel):
    """Vault configuration."""

    path: str = Field(..., description="Absolute path to vault directory")
    auto_create: bool = Field(
        default=True, description="Create vault directory if it doesn't exist"
    )
    watch_files: bool = Field(
        default=False, description="Watch for external file changes"
    )
    respect_gitignore: bool = Field(
        default=True, description="Respect .gitignore files"
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate vault path is absolute."""
        path = Path(v)
        if not path.is_absolute():
            raise ValueError("Vault path must be absolute")
        return v


class SecurityConfig(BaseModel):
    """Security configuration."""

    api_key: str | None = Field(
        default=None, description="API key for authentication (auto-generated if None)"
    )
    api_key_file: str | None = Field(
        default=None, description="Path to file containing API key"
    )
    cert_path: str = Field(
        default="./certs/server.crt", description="SSL certificate path"
    )
    key_path: str = Field(default="./certs/server.key", description="SSL key path")
    auto_generate_cert: bool = Field(
        default=True, description="Auto-generate self-signed cert if missing"
    )


class ObsidianConfig(BaseModel):
    """Obsidian vault compatibility configuration."""

    enabled: bool = Field(default=True, description="Enable Obsidian-specific features")
    config_sync: bool = Field(
        default=True, description="Import settings from .obsidian/ directory"
    )
    respect_exclusions: bool = Field(
        default=True, description="Respect Obsidian's excluded files"
    )


class PeriodicNoteConfig(BaseModel):
    """Configuration for a periodic note type."""

    enabled: bool = Field(default=True, description="Enable this periodic note type")
    format: str = Field(..., description="Date format string")
    folder: str = Field(..., description="Folder path relative to vault")
    template: str | None = Field(
        default=None, description="Template file path (optional)"
    )


class PeriodicNotesConfig(BaseModel):
    """Periodic notes configuration."""

    daily: PeriodicNoteConfig = Field(
        default_factory=lambda: PeriodicNoteConfig(
            enabled=True, format="YYYY-MM-DD", folder="daily/", template=None
        )
    )
    weekly: PeriodicNoteConfig = Field(
        default_factory=lambda: PeriodicNoteConfig(
            enabled=True, format="YYYY-[W]WW", folder="weekly/", template=None
        )
    )
    monthly: PeriodicNoteConfig = Field(
        default_factory=lambda: PeriodicNoteConfig(
            enabled=True, format="YYYY-MM", folder="monthly/", template=None
        )
    )
    quarterly: PeriodicNoteConfig = Field(
        default_factory=lambda: PeriodicNoteConfig(
            enabled=True, format="YYYY-[Q]Q", folder="quarterly/", template=None
        )
    )
    yearly: PeriodicNoteConfig = Field(
        default_factory=lambda: PeriodicNoteConfig(
            enabled=True, format="YYYY", folder="yearly/", template=None
        )
    )


class SearchConfig(BaseModel):
    """Search configuration."""

    max_results: int = Field(default=100, description="Maximum search results")
    enable_fuzzy: bool = Field(default=True, description="Enable fuzzy matching")
    cache_results: bool = Field(default=True, description="Cache search results")


class ActiveFileConfig(BaseModel):
    """Active file tracking configuration."""

    tracking_method: str = Field(
        default="session", description="Tracking method: session | cookie | redis"
    )
    default_file: str | None = Field(
        default=None, description="Default file if none active"
    )

    @field_validator("tracking_method")
    @classmethod
    def validate_tracking_method(cls, v: str) -> str:
        """Validate tracking method."""
        valid_methods = {"session", "cookie", "redis"}
        if v not in valid_methods:
            raise ValueError(f"tracking_method must be one of: {valid_methods}")
        return v


class CommandsConfig(BaseModel):
    """Commands API configuration."""

    enabled: bool = Field(default=True, description="Enable commands API")
    custom_commands_dir: str | None = Field(
        default=None, description="Directory for custom command plugins"
    )


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="INFO", description="Log level")
    format: str = Field(default="json", description="Log format: json | text")
    file: str | None = Field(default=None, description="Log file path")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"level must be one of: {valid_levels}")
        return v_upper

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate log format."""
        valid_formats = {"json", "text"}
        if v not in valid_formats:
            raise ValueError(f"format must be one of: {valid_formats}")
        return v


class PerformanceConfig(BaseModel):
    """Performance configuration."""

    max_file_size: int = Field(
        default=10485760, description="Maximum file size in bytes (10MB default)"
    )
    cache_ttl: int = Field(default=300, description="Cache TTL in seconds")
    worker_count: int = Field(default=1, description="Uvicorn worker processes")

    @field_validator("worker_count")
    @classmethod
    def validate_worker_count(cls, v: int) -> int:
        """Validate worker count."""
        if v < 1:
            raise ValueError("worker_count must be at least 1")
        return v


class AppConfig(BaseSettings):
    """
    Main application configuration.

    Supports both YAML file and environment variables.
    Environment variables use the format: MARKDOWN_VAULT_<SECTION>__<KEY>

    Examples:
        MARKDOWN_VAULT_SERVER__PORT=8080
        MARKDOWN_VAULT_VAULT__PATH=/path/to/vault
        MARKDOWN_VAULT_SECURITY__API_KEY=mykey
    """

    model_config = SettingsConfigDict(
        env_prefix="MARKDOWN_VAULT_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    server: ServerConfig = Field(default_factory=ServerConfig)
    vault: VaultConfig | None = None
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    obsidian: ObsidianConfig = Field(default_factory=ObsidianConfig)
    periodic_notes: PeriodicNotesConfig = Field(default_factory=PeriodicNotesConfig)
    search: SearchConfig = Field(default_factory=SearchConfig)
    active_file: ActiveFileConfig = Field(default_factory=ActiveFileConfig)
    commands: CommandsConfig = Field(default_factory=CommandsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
