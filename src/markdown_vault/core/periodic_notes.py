"""
Periodic notes manager for date-based note creation and management.

This module provides the PeriodicNotesManager class which handles:
- Generating note paths based on period type and offset
- Creating notes from templates
- Auto-creating notes with configured templates
- Supporting daily, weekly, monthly, quarterly, and yearly notes
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

import aiofiles

from markdown_vault.models.config import PeriodicNoteConfig
from markdown_vault.utils.date_utils import (
    apply_offset_daily,
    apply_offset_monthly,
    apply_offset_quarterly,
    apply_offset_weekly,
    apply_offset_yearly,
    format_daily,
    format_monthly,
    format_quarterly,
    format_weekly,
    format_yearly,
    parse_period_offset,
)

logger = logging.getLogger(__name__)

# Type alias for period types
PeriodType = Literal["daily", "weekly", "monthly", "quarterly", "yearly"]


class PeriodicNotesError(Exception):
    """Base exception for periodic notes operations."""

    pass


class PeriodicNotesManager:
    """
    Manages periodic note operations.

    Handles path generation, template application, and auto-creation
    of periodic notes based on configuration.
    """

    def __init__(self, vault_path: Path) -> None:
        """
        Initialize periodic notes manager.

        Args:
            vault_path: Absolute path to the vault directory

        Raises:
            ValueError: If vault_path is not absolute or doesn't exist
        """
        if not vault_path.is_absolute():
            raise ValueError(f"Vault path must be absolute: {vault_path}")

        if not vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")

        if not vault_path.is_dir():
            raise ValueError(f"Vault path is not a directory: {vault_path}")

        self.vault_path = vault_path
        logger.info(f"Initialized PeriodicNotesManager for: {vault_path}")

    def get_note_path(
        self,
        period: PeriodType,
        offset: str,
        config: PeriodicNoteConfig,
        base_date: datetime | None = None,
    ) -> Path:
        """
        Get the file path for a periodic note.

        Args:
            period: Type of period (daily, weekly, monthly, quarterly, yearly)
            offset: Offset string (e.g., "today", "+1", "-1")
            config: Configuration for this period type
            base_date: Base date to calculate from (defaults to now)

        Returns:
            Absolute path to the periodic note file

        Raises:
            ValueError: If offset format is invalid
            PeriodicNotesError: If period type is invalid

        Examples:
            >>> manager.get_note_path("daily", "today", config)
            Path("/vault/daily/2025-01-15.md")
            >>> manager.get_note_path("weekly", "+1", config)
            Path("/vault/weekly/2025-W04.md")
        """
        # Parse offset
        offset_value = parse_period_offset(offset)

        # Get base date
        if base_date is None:
            base_date = datetime.now()

        # Apply offset based on period type
        if period == "daily":
            target_date = apply_offset_daily(base_date, offset_value)
            filename = format_daily(target_date)
        elif period == "weekly":
            target_date = apply_offset_weekly(base_date, offset_value)
            filename = format_weekly(target_date)
        elif period == "monthly":
            target_date = apply_offset_monthly(base_date, offset_value)
            filename = format_monthly(target_date)
        elif period == "quarterly":
            target_date = apply_offset_quarterly(base_date, offset_value)
            filename = format_quarterly(target_date)
        elif period == "yearly":
            target_date = apply_offset_yearly(base_date, offset_value)
            filename = format_yearly(target_date)
        else:
            raise PeriodicNotesError(f"Invalid period type: {period}")

        # Build full path
        folder = config.folder.rstrip("/")
        note_path = self.vault_path / folder / f"{filename}.md"

        logger.debug(
            f"Generated path for {period} note with offset {offset}: {note_path}"
        )
        return note_path

    async def create_from_template(self, path: Path, template_path: Path | None) -> str:
        """
        Create note content from a template.

        If template_path is None, returns an empty string.
        Template variables are replaced:
        - {{date}}: Current date in YYYY-MM-DD format
        - {{time}}: Current time in HH:MM format

        Args:
            path: Path where the note will be created (for context)
            template_path: Path to template file (optional)

        Returns:
            Note content (from template or empty string)

        Raises:
            PeriodicNotesError: If template file cannot be read
        """
        if template_path is None:
            return ""

        # Resolve template path relative to vault
        if not template_path.is_absolute():
            template_path = self.vault_path / template_path

        # Check if template exists
        if not template_path.exists():
            logger.warning(f"Template file not found: {template_path}")
            return ""

        try:
            # Read template content
            async with aiofiles.open(template_path, encoding="utf-8") as f:
                content = await f.read()

            # Replace template variables
            now = datetime.now()
            content = content.replace("{{date}}", now.strftime("%Y-%m-%d"))
            content = content.replace("{{time}}", now.strftime("%H:%M"))

            logger.debug(f"Created content from template: {template_path}")
            return content

        except Exception as e:
            raise PeriodicNotesError(
                f"Failed to read template {template_path}: {e}"
            ) from e

    async def ensure_note_exists(
        self,
        period: PeriodType,
        offset: str,
        config: PeriodicNoteConfig,
        base_date: datetime | None = None,
    ) -> Path:
        """
        Ensure a periodic note exists, creating it if necessary.

        If the note doesn't exist and a template is configured, the note
        will be created from the template. Parent directories are created
        as needed.

        Args:
            period: Type of period (daily, weekly, monthly, quarterly, yearly)
            offset: Offset string (e.g., "today", "+1", "-1")
            config: Configuration for this period type
            base_date: Base date to calculate from (defaults to now)

        Returns:
            Absolute path to the note file

        Raises:
            ValueError: If offset format is invalid
            PeriodicNotesError: If note creation fails
        """
        # Get note path
        note_path = self.get_note_path(period, offset, config, base_date)

        # Check if note already exists
        if note_path.exists():
            logger.debug(f"Periodic note already exists: {note_path}")
            return note_path

        # Create parent directories
        note_path.parent.mkdir(parents=True, exist_ok=True)

        # Get template content
        template_path = None
        if config.template:
            template_path = Path(config.template)

        content = await self.create_from_template(note_path, template_path)

        # Write note
        try:
            async with aiofiles.open(note_path, "w", encoding="utf-8") as f:
                await f.write(content)

            logger.info(f"Created periodic note: {note_path}")
            return note_path

        except Exception as e:
            raise PeriodicNotesError(f"Failed to create note {note_path}: {e}") from e


__all__ = [
    "PeriodicNotesManager",
    "PeriodicNotesError",
    "PeriodType",
]
