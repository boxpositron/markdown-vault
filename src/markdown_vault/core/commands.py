"""
Command system for markdown vault.

Provides a registry for commands that can be executed via the API.
Includes built-in commands for common vault operations.
"""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from markdown_vault.core.search_engine import SearchEngine
from markdown_vault.core.vault import VaultManager
from markdown_vault.models.api import CommandInfo

logger = logging.getLogger(__name__)


class CommandError(Exception):
    """Base exception for command operations."""

    pass


class CommandNotFoundError(CommandError):
    """Raised when a command is not found."""

    pass


@dataclass
class Command:
    """
    A registered command.

    Attributes:
        id: Unique command identifier
        name: Human-readable command name
        handler: Async function that executes the command
    """

    id: str
    name: str
    handler: Callable[..., Awaitable[Any]]


class CommandRegistry:
    """
    Registry for commands that can be executed via the API.

    Maintains an in-memory registry of commands and provides
    methods to register, list, and execute them.
    """

    def __init__(self) -> None:
        """Initialize command registry with built-in commands."""
        self._commands: dict[str, Command] = {}
        logger.info("Initialized CommandRegistry")

    def register_command(
        self,
        id: str,
        name: str,
        handler: Callable[..., Awaitable[Any]],
    ) -> None:
        """
        Register a new command.

        Args:
            id: Unique command identifier (e.g., "vault.list")
            name: Human-readable command name
            handler: Async function that executes the command

        Raises:
            CommandError: If command ID is already registered
        """
        if id in self._commands:
            raise CommandError(f"Command '{id}' is already registered")

        self._commands[id] = Command(id=id, name=name, handler=handler)
        logger.info(f"Registered command: {id} ({name})")

    def get_command(self, id: str) -> Command | None:
        """
        Get a command by ID.

        Args:
            id: Command identifier

        Returns:
            Command if found, None otherwise
        """
        return self._commands.get(id)

    def list_commands(self) -> list[CommandInfo]:
        """
        List all available commands.

        Returns:
            List of command info objects
        """
        return [
            CommandInfo(id=cmd.id, name=cmd.name)
            for cmd in sorted(self._commands.values(), key=lambda c: c.id)
        ]

    async def execute_command(
        self,
        id: str,
        vault_manager: VaultManager,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Execute a command by ID.

        Args:
            id: Command identifier
            vault_manager: Vault manager instance
            params: Optional command parameters

        Returns:
            Command execution result

        Raises:
            CommandNotFoundError: If command is not found
            CommandError: If command execution fails
        """
        command = self.get_command(id)
        if not command:
            raise CommandNotFoundError(f"Command not found: {id}")

        try:
            logger.info(f"Executing command: {id}")
            return await command.handler(vault_manager, params or {})
        except Exception as e:
            logger.error(f"Command execution failed for '{id}': {e}")
            raise CommandError(f"Command execution failed: {e}") from e


# Built-in command handlers


async def _vault_list_handler(
    vault_manager: VaultManager,
    params: dict[str, Any],
) -> dict[str, Any]:
    """
    List all files in the vault.

    Args:
        vault_manager: Vault manager instance
        params: Optional parameters (not used)

    Returns:
        Dict with 'files' key containing list of file paths
    """
    files = await vault_manager.list_files()
    return {"files": files}


async def _vault_create_handler(
    vault_manager: VaultManager,
    params: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a new file in the vault.

    Args:
        vault_manager: Vault manager instance
        params: Parameters with 'path' and 'content' keys

    Returns:
        Dict with 'path' and 'created' keys

    Raises:
        CommandError: If required parameters are missing
    """
    path = params.get("path")
    content = params.get("content", "")

    if not path:
        raise CommandError("Missing required parameter: path")

    await vault_manager.write_file(path, content)
    return {"path": path, "created": True}


async def _vault_search_handler(
    vault_manager: VaultManager,
    params: dict[str, Any],
) -> dict[str, Any]:
    """
    Search the vault.

    Args:
        vault_manager: Vault manager instance
        params: Parameters with 'query' and optional 'max_results' keys

    Returns:
        Dict with 'results' and 'total' keys

    Raises:
        CommandError: If required parameters are missing
    """
    query = params.get("query")
    max_results = params.get("max_results")

    if not query:
        raise CommandError("Missing required parameter: query")

    search_engine = SearchEngine()
    results = await search_engine.simple_search(
        query=query,
        vault_manager=vault_manager,
        max_results=max_results,
    )

    return {
        "results": [
            {
                "path": r.path,
                "matches": r.matches,
            }
            for r in results
        ],
        "total": len(results),
    }


def create_default_registry() -> CommandRegistry:
    """
    Create a command registry with built-in commands.

    Returns:
        CommandRegistry with built-in commands registered
    """
    registry = CommandRegistry()

    # Register built-in commands
    registry.register_command(
        id="vault.list",
        name="List all files",
        handler=_vault_list_handler,
    )

    registry.register_command(
        id="vault.create",
        name="Create new file",
        handler=_vault_create_handler,
    )

    registry.register_command(
        id="vault.search",
        name="Search vault",
        handler=_vault_search_handler,
    )

    logger.info(f"Created default registry with {len(registry._commands)} commands")
    return registry


__all__ = [
    "Command",
    "CommandError",
    "CommandNotFoundError",
    "CommandRegistry",
    "create_default_registry",
]
