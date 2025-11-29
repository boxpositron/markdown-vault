"""
Tests for periodic_notes module.

Tests the PeriodicNotesManager class for path generation,
template application, and note creation.
"""

from datetime import datetime
from pathlib import Path

import pytest

from markdown_vault.core.periodic_notes import (
    PeriodicNotesError,
    PeriodicNotesManager,
)
from markdown_vault.models.config import PeriodicNoteConfig


@pytest.fixture
def vault_path(tmp_path: Path) -> Path:
    """Create a temporary vault directory."""
    vault = tmp_path / "vault"
    vault.mkdir()
    return vault


@pytest.fixture
def manager(vault_path: Path) -> PeriodicNotesManager:
    """Create a PeriodicNotesManager instance."""
    return PeriodicNotesManager(vault_path)


@pytest.fixture
def daily_config() -> PeriodicNoteConfig:
    """Create a daily note configuration."""
    return PeriodicNoteConfig(
        enabled=True, format="YYYY-MM-DD", folder="daily/", template=None
    )


@pytest.fixture
def weekly_config() -> PeriodicNoteConfig:
    """Create a weekly note configuration."""
    return PeriodicNoteConfig(
        enabled=True, format="YYYY-[W]WW", folder="weekly/", template=None
    )


@pytest.fixture
def monthly_config() -> PeriodicNoteConfig:
    """Create a monthly note configuration."""
    return PeriodicNoteConfig(
        enabled=True, format="YYYY-MM", folder="monthly/", template=None
    )


class TestInitialization:
    """Test PeriodicNotesManager initialization."""

    def test_init_success(self, vault_path: Path) -> None:
        """Test successful initialization."""
        manager = PeriodicNotesManager(vault_path)
        assert manager.vault_path == vault_path

    def test_init_non_absolute(self, tmp_path: Path) -> None:
        """Test initialization with non-absolute path."""
        with pytest.raises(ValueError, match="must be absolute"):
            PeriodicNotesManager(Path("relative/path"))

    def test_init_non_existent(self, tmp_path: Path) -> None:
        """Test initialization with non-existent path."""
        non_existent = tmp_path / "does_not_exist"
        with pytest.raises(ValueError, match="does not exist"):
            PeriodicNotesManager(non_existent)

    def test_init_not_directory(self, tmp_path: Path) -> None:
        """Test initialization with file instead of directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")
        with pytest.raises(ValueError, match="not a directory"):
            PeriodicNotesManager(file_path)


class TestGetNotePath:
    """Test get_note_path method."""

    def test_daily_today(
        self,
        manager: PeriodicNotesManager,
        vault_path: Path,
        daily_config: PeriodicNoteConfig,
    ) -> None:
        """Test daily note path for today."""
        base_date = datetime(2025, 1, 15)
        path = manager.get_note_path("daily", "today", daily_config, base_date)
        expected = vault_path / "daily" / "2025-01-15.md"
        assert path == expected

    def test_daily_offset(
        self,
        manager: PeriodicNotesManager,
        vault_path: Path,
        daily_config: PeriodicNoteConfig,
    ) -> None:
        """Test daily note path with offset."""
        base_date = datetime(2025, 1, 15)

        # Tomorrow (+1)
        path = manager.get_note_path("daily", "+1", daily_config, base_date)
        expected = vault_path / "daily" / "2025-01-16.md"
        assert path == expected

        # Yesterday (-1)
        path = manager.get_note_path("daily", "-1", daily_config, base_date)
        expected = vault_path / "daily" / "2025-01-14.md"
        assert path == expected

    def test_weekly(
        self,
        manager: PeriodicNotesManager,
        vault_path: Path,
        weekly_config: PeriodicNoteConfig,
    ) -> None:
        """Test weekly note path."""
        base_date = datetime(2025, 1, 15)  # Week 3

        path = manager.get_note_path("weekly", "today", weekly_config, base_date)
        expected = vault_path / "weekly" / "2025-W03.md"
        assert path == expected

        # Next week
        path = manager.get_note_path("weekly", "+1", weekly_config, base_date)
        expected = vault_path / "weekly" / "2025-W04.md"
        assert path == expected

    def test_monthly(
        self,
        manager: PeriodicNotesManager,
        vault_path: Path,
        monthly_config: PeriodicNoteConfig,
    ) -> None:
        """Test monthly note path."""
        base_date = datetime(2025, 1, 15)

        path = manager.get_note_path("monthly", "today", monthly_config, base_date)
        expected = vault_path / "monthly" / "2025-01.md"
        assert path == expected

        # Next month
        path = manager.get_note_path("monthly", "+1", monthly_config, base_date)
        expected = vault_path / "monthly" / "2025-02.md"
        assert path == expected

    def test_quarterly(self, manager: PeriodicNotesManager, vault_path: Path) -> None:
        """Test quarterly note path."""
        config = PeriodicNoteConfig(
            enabled=True, format="YYYY-[Q]Q", folder="quarterly/", template=None
        )
        base_date = datetime(2025, 1, 15)  # Q1

        path = manager.get_note_path("quarterly", "today", config, base_date)
        expected = vault_path / "quarterly" / "2025-Q1.md"
        assert path == expected

        # Q3 (July)
        base_date = datetime(2025, 7, 1)
        path = manager.get_note_path("quarterly", "today", config, base_date)
        expected = vault_path / "quarterly" / "2025-Q3.md"
        assert path == expected

    def test_yearly(self, manager: PeriodicNotesManager, vault_path: Path) -> None:
        """Test yearly note path."""
        config = PeriodicNoteConfig(
            enabled=True, format="YYYY", folder="yearly/", template=None
        )
        base_date = datetime(2025, 1, 15)

        path = manager.get_note_path("yearly", "today", config, base_date)
        expected = vault_path / "yearly" / "2025.md"
        assert path == expected

        # Next year
        path = manager.get_note_path("yearly", "+1", config, base_date)
        expected = vault_path / "yearly" / "2026.md"
        assert path == expected

    def test_invalid_period(
        self, manager: PeriodicNotesManager, daily_config: PeriodicNoteConfig
    ) -> None:
        """Test with invalid period type."""
        with pytest.raises(PeriodicNotesError, match="Invalid period type"):
            # Type ignore because we're intentionally passing invalid type
            manager.get_note_path("invalid", "today", daily_config)  # type: ignore

    def test_invalid_offset(
        self, manager: PeriodicNotesManager, daily_config: PeriodicNoteConfig
    ) -> None:
        """Test with invalid offset."""
        with pytest.raises(ValueError, match="Invalid offset format"):
            manager.get_note_path("daily", "invalid", daily_config)


class TestCreateFromTemplate:
    """Test create_from_template method."""

    @pytest.mark.asyncio
    async def test_no_template(
        self, manager: PeriodicNotesManager, vault_path: Path
    ) -> None:
        """Test creating note without template."""
        path = vault_path / "daily" / "2025-01-15.md"
        content = await manager.create_from_template(path, None)
        assert content == ""

    @pytest.mark.asyncio
    async def test_with_template(
        self, manager: PeriodicNotesManager, vault_path: Path
    ) -> None:
        """Test creating note with template."""
        # Create a template file
        template_dir = vault_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "daily.md"
        template_path.write_text("# Daily Note\n\nDate: {{date}}\nTime: {{time}}\n")

        path = vault_path / "daily" / "2025-01-15.md"
        content = await manager.create_from_template(path, template_path)

        # Check that variables were replaced
        assert "# Daily Note" in content
        assert "Date: " in content
        assert "Time: " in content
        assert "{{date}}" not in content
        assert "{{time}}" not in content

    @pytest.mark.asyncio
    async def test_template_not_found(
        self, manager: PeriodicNotesManager, vault_path: Path
    ) -> None:
        """Test with non-existent template."""
        template_path = vault_path / "templates" / "missing.md"
        path = vault_path / "daily" / "2025-01-15.md"

        # Should return empty string when template not found
        content = await manager.create_from_template(path, template_path)
        assert content == ""

    @pytest.mark.asyncio
    async def test_relative_template_path(
        self, manager: PeriodicNotesManager, vault_path: Path
    ) -> None:
        """Test with relative template path."""
        # Create a template file
        template_dir = vault_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "daily.md"
        template_file.write_text("# Template Content\n")

        # Use relative path
        relative_template = Path("templates/daily.md")
        path = vault_path / "daily" / "2025-01-15.md"
        content = await manager.create_from_template(path, relative_template)

        assert content == "# Template Content\n"


class TestEnsureNoteExists:
    """Test ensure_note_exists method."""

    @pytest.mark.asyncio
    async def test_note_already_exists(
        self,
        manager: PeriodicNotesManager,
        vault_path: Path,
        daily_config: PeriodicNoteConfig,
    ) -> None:
        """Test when note already exists."""
        # Create the note file
        daily_dir = vault_path / "daily"
        daily_dir.mkdir()
        note_file = daily_dir / "2025-01-15.md"
        note_file.write_text("Existing content")

        base_date = datetime(2025, 1, 15)
        path = await manager.ensure_note_exists(
            "daily", "today", daily_config, base_date
        )

        assert path == note_file
        # Content should not be modified
        assert note_file.read_text() == "Existing content"

    @pytest.mark.asyncio
    async def test_create_without_template(
        self,
        manager: PeriodicNotesManager,
        vault_path: Path,
        daily_config: PeriodicNoteConfig,
    ) -> None:
        """Test creating note without template."""
        base_date = datetime(2025, 1, 15)
        path = await manager.ensure_note_exists(
            "daily", "today", daily_config, base_date
        )

        expected = vault_path / "daily" / "2025-01-15.md"
        assert path == expected
        assert path.exists()
        # Should be empty without template
        assert path.read_text() == ""

    @pytest.mark.asyncio
    async def test_create_with_template(
        self, manager: PeriodicNotesManager, vault_path: Path
    ) -> None:
        """Test creating note with template."""
        # Create template
        template_dir = vault_path / "templates"
        template_dir.mkdir()
        template_file = template_dir / "daily.md"
        template_file.write_text("# Daily Note\n\nDate: {{date}}\n")

        config = PeriodicNoteConfig(
            enabled=True,
            format="YYYY-MM-DD",
            folder="daily/",
            template="templates/daily.md",
        )

        base_date = datetime(2025, 1, 15)
        path = await manager.ensure_note_exists("daily", "today", config, base_date)

        assert path.exists()
        content = path.read_text()
        assert "# Daily Note" in content
        assert "Date: " in content

    @pytest.mark.asyncio
    async def test_create_parent_directories(
        self,
        manager: PeriodicNotesManager,
        vault_path: Path,
        daily_config: PeriodicNoteConfig,
    ) -> None:
        """Test that parent directories are created."""
        base_date = datetime(2025, 1, 15)
        path = await manager.ensure_note_exists(
            "daily", "today", daily_config, base_date
        )

        assert path.parent.exists()
        assert path.parent.is_dir()
        assert path.exists()
