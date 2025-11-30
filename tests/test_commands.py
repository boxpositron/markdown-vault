"""
Tests for command system.

Tests command registry functionality including:
- Registration and listing
- Command execution
- Built-in commands
- Error handling
"""

from pathlib import Path

import pytest

from markdown_vault.core.commands import (
    CommandError,
    CommandNotFoundError,
    CommandRegistry,
    create_default_registry,
)
from markdown_vault.core.vault import VaultManager


class TestCommandRegistry:
    """Test command registry functionality."""

    def test_init(self):
        """Test registry initialization."""
        registry = CommandRegistry()
        assert registry is not None
        assert registry.list_commands() == []

    async def test_register_command(self):
        """Test registering a command."""
        registry = CommandRegistry()

        async def handler(vault: VaultManager, params: dict) -> dict:
            return {"status": "ok"}

        registry.register_command("test.cmd", "Test Command", handler)

        commands = registry.list_commands()
        assert len(commands) == 1
        assert commands[0].id == "test.cmd"
        assert commands[0].name == "Test Command"

    async def test_register_duplicate_command(self):
        """Test that registering duplicate command raises error."""
        registry = CommandRegistry()

        async def handler(vault: VaultManager, params: dict) -> dict:
            return {"status": "ok"}

        registry.register_command("test.cmd", "Test Command", handler)

        with pytest.raises(CommandError, match="already registered"):
            registry.register_command("test.cmd", "Another Command", handler)

    async def test_get_command(self):
        """Test getting a command."""
        registry = CommandRegistry()

        async def handler(vault: VaultManager, params: dict) -> dict:
            return {"status": "ok"}

        registry.register_command("test.cmd", "Test Command", handler)

        cmd = registry.get_command("test.cmd")
        assert cmd is not None
        assert cmd.id == "test.cmd"
        assert cmd.name == "Test Command"

        # Test non-existent command
        assert registry.get_command("nonexistent") is None

    async def test_list_commands_sorted(self):
        """Test that commands are listed in sorted order."""
        registry = CommandRegistry()

        async def handler(vault: VaultManager, params: dict) -> dict:
            return {"status": "ok"}

        registry.register_command("z.cmd", "Z Command", handler)
        registry.register_command("a.cmd", "A Command", handler)
        registry.register_command("m.cmd", "M Command", handler)

        commands = registry.list_commands()
        assert len(commands) == 3
        assert commands[0].id == "a.cmd"
        assert commands[1].id == "m.cmd"
        assert commands[2].id == "z.cmd"

    async def test_execute_command(self, tmp_path: Path):
        """Test executing a command."""
        registry = CommandRegistry()
        vault = VaultManager(tmp_path)

        async def handler(vault: VaultManager, params: dict) -> dict:
            return {"echo": params.get("message", "default")}

        registry.register_command("test.echo", "Echo", handler)

        result = await registry.execute_command(
            "test.echo", vault, {"message": "hello"}
        )
        assert result == {"echo": "hello"}

    async def test_execute_command_no_params(self, tmp_path: Path):
        """Test executing a command without params."""
        registry = CommandRegistry()
        vault = VaultManager(tmp_path)

        async def handler(vault: VaultManager, params: dict) -> dict:
            return {"status": "ok"}

        registry.register_command("test.simple", "Simple", handler)

        result = await registry.execute_command("test.simple", vault)
        assert result == {"status": "ok"}

    async def test_execute_nonexistent_command(self, tmp_path: Path):
        """Test executing non-existent command raises error."""
        registry = CommandRegistry()
        vault = VaultManager(tmp_path)

        with pytest.raises(CommandNotFoundError, match="Command not found"):
            await registry.execute_command("nonexistent", vault)

    async def test_execute_command_error(self, tmp_path: Path):
        """Test that command errors are wrapped."""
        registry = CommandRegistry()
        vault = VaultManager(tmp_path)

        async def handler(vault: VaultManager, params: dict) -> dict:
            raise ValueError("Something went wrong")

        registry.register_command("test.error", "Error", handler)

        with pytest.raises(CommandError, match="Command execution failed"):
            await registry.execute_command("test.error", vault)


class TestDefaultRegistry:
    """Test default registry with built-in commands."""

    def test_create_default_registry(self):
        """Test creating default registry."""
        registry = create_default_registry()
        assert registry is not None

        commands = registry.list_commands()
        assert len(commands) == 3

        command_ids = {cmd.id for cmd in commands}
        assert "vault.list" in command_ids
        assert "vault.create" in command_ids
        assert "vault.search" in command_ids

    async def test_vault_list_command(self, tmp_path: Path):
        """Test vault.list command."""
        registry = create_default_registry()
        vault = VaultManager(tmp_path)

        # Create test files
        (tmp_path / "note1.md").write_text("# Note 1")
        (tmp_path / "note2.md").write_text("# Note 2")

        result = await registry.execute_command("vault.list", vault)
        assert "files" in result
        assert len(result["files"]) == 2
        assert "note1.md" in result["files"]
        assert "note2.md" in result["files"]

    async def test_vault_create_command(self, tmp_path: Path):
        """Test vault.create command."""
        registry = create_default_registry()
        vault = VaultManager(tmp_path)

        result = await registry.execute_command(
            "vault.create",
            vault,
            {"path": "new.md", "content": "# New Note"},
        )

        assert result == {"path": "new.md", "created": True}
        assert (tmp_path / "new.md").exists()
        assert (tmp_path / "new.md").read_text() == "# New Note"

    async def test_vault_create_command_no_path(self, tmp_path: Path):
        """Test vault.create command without path raises error."""
        registry = create_default_registry()
        vault = VaultManager(tmp_path)

        with pytest.raises(CommandError, match="Missing required parameter: path"):
            await registry.execute_command("vault.create", vault, {})

    async def test_vault_create_command_no_content(self, tmp_path: Path):
        """Test vault.create command without content creates empty file."""
        registry = create_default_registry()
        vault = VaultManager(tmp_path)

        result = await registry.execute_command(
            "vault.create",
            vault,
            {"path": "empty.md"},
        )

        assert result == {"path": "empty.md", "created": True}
        assert (tmp_path / "empty.md").exists()
        assert (tmp_path / "empty.md").read_text() == ""

    async def test_vault_search_command(self, tmp_path: Path):
        """Test vault.search command."""
        registry = create_default_registry()
        vault = VaultManager(tmp_path)

        # Create test files
        (tmp_path / "note1.md").write_text("# Python Tutorial\nLearn Python here")
        (tmp_path / "note2.md").write_text("# JavaScript Guide\nLearn JS here")

        result = await registry.execute_command(
            "vault.search",
            vault,
            {"query": "Python"},
        )

        assert "results" in result
        assert "total" in result
        assert result["total"] == 1
        assert len(result["results"]) == 1
        assert result["results"][0]["path"] == "note1.md"

    async def test_vault_search_command_no_query(self, tmp_path: Path):
        """Test vault.search command without query raises error."""
        registry = create_default_registry()
        vault = VaultManager(tmp_path)

        with pytest.raises(CommandError, match="Missing required parameter: query"):
            await registry.execute_command("vault.search", vault, {})

    async def test_vault_search_command_max_results(self, tmp_path: Path):
        """Test vault.search command with max_results."""
        registry = create_default_registry()
        vault = VaultManager(tmp_path)

        # Create test files
        (tmp_path / "note1.md").write_text("# Test 1\ntest content")
        (tmp_path / "note2.md").write_text("# Test 2\ntest content")
        (tmp_path / "note3.md").write_text("# Test 3\ntest content")

        result = await registry.execute_command(
            "vault.search",
            vault,
            {"query": "test", "max_results": 2},
        )

        assert result["total"] == 2
        assert len(result["results"]) == 2
