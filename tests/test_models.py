"""
Tests for Pydantic models.
"""

import pytest
from markdown_vault.models import (
    Note,
    NoteStat,
    NoteJson,
    ServerStatus,
    APIError,
    PatchOperation,
    TargetType,
)
from markdown_vault.models.config import (
    ServerConfig,
    VaultConfig,
    AppConfig,
)


class TestNoteModels:
    """Test note-related models."""

    def test_note_stat_creation(self):
        """Test NoteStat model creation."""
        stat = NoteStat(
            ctime=1234567890000,
            mtime=1234567891000,
            size=1024,
        )
        assert stat.ctime == 1234567890000
        assert stat.mtime == 1234567891000
        assert stat.size == 1024

    def test_note_json_creation(self):
        """Test NoteJson model creation."""
        stat = NoteStat(ctime=1234567890000, mtime=1234567891000, size=1024)
        note = NoteJson(
            path="notes/test.md",
            content="# Test",
            frontmatter={"title": "Test"},
            tags=["test"],
            stat=stat,
        )
        assert note.path == "notes/test.md"
        assert note.content == "# Test"
        assert note.frontmatter["title"] == "Test"
        assert "test" in note.tags

    def test_note_to_json_format(self):
        """Test Note conversion to JSON format."""
        note = Note(
            path="test.md",
            content="# Content",
            frontmatter={"key": "value"},
            tags=["tag1"],
        )
        stat = NoteStat(ctime=1000, mtime=2000, size=100)
        note_json = note.to_json_format(stat)
        
        assert isinstance(note_json, NoteJson)
        assert note_json.path == "test.md"
        assert note_json.stat == stat


class TestAPIModels:
    """Test API-related models."""

    def test_server_status(self):
        """Test ServerStatus model."""
        status = ServerStatus(
            authenticated=False,
            versions={"self": "0.1.0"},
        )
        assert status.ok == "OK"
        assert status.service == "markdown-vault"
        assert not status.authenticated

    def test_api_error(self):
        """Test APIError model."""
        error = APIError(
            errorCode=40401,
            message="File not found",
        )
        assert error.errorCode == 40401
        assert error.message == "File not found"

    def test_patch_operation_enum(self):
        """Test PatchOperation enum."""
        assert PatchOperation.APPEND == "append"
        assert PatchOperation.PREPEND == "prepend"
        assert PatchOperation.REPLACE == "replace"

    def test_target_type_enum(self):
        """Test TargetType enum."""
        assert TargetType.HEADING == "heading"
        assert TargetType.BLOCK == "block"
        assert TargetType.FRONTMATTER == "frontmatter"


class TestConfigModels:
    """Test configuration models."""

    def test_server_config_defaults(self):
        """Test ServerConfig with defaults."""
        config = ServerConfig()
        assert config.host == "127.0.0.1"
        assert config.port == 27123
        assert config.https is True
        assert config.reload is False

    def test_server_config_validation(self):
        """Test ServerConfig port validation."""
        with pytest.raises(ValueError, match="Port must be between"):
            ServerConfig(port=99999)

    def test_vault_config_validation(self):
        """Test VaultConfig path validation."""
        # Valid absolute path
        config = VaultConfig(path="/valid/absolute/path")
        assert config.path == "/valid/absolute/path"
        
        # Invalid relative path
        with pytest.raises(ValueError, match="must be absolute"):
            VaultConfig(path="relative/path")

    def test_app_config_creation(self):
        """Test AppConfig creation with required fields."""
        config = AppConfig(
            vault=VaultConfig(path="/test/vault")
        )
        assert config.vault.path == "/test/vault"
        assert config.server.port == 27123
        assert config.security.auto_generate_cert is True
