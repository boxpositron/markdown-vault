"""
Commands API routes for markdown vault.

This module provides command execution endpoints:
- GET /commands/ - List available commands
- POST /commands/{id}/ - Execute a command
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from markdown_vault.api.deps import ApiKeyDep, VaultPathDep
from markdown_vault.core.commands import (
    CommandError,
    CommandNotFoundError,
    CommandRegistry,
    create_default_registry,
)
from markdown_vault.core.vault import VaultManager
from markdown_vault.models.api import CommandList

logger = logging.getLogger(__name__)

router = APIRouter()

# Global command registry
_registry: CommandRegistry | None = None


def get_registry() -> CommandRegistry:
    """
    Get or create the global command registry.

    Returns:
        CommandRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = create_default_registry()
    return _registry


class CommandRequest(BaseModel):
    """Command execution request."""

    params: dict[str, Any] = Field(
        default_factory=dict, description="Command parameters"
    )


class CommandResponse(BaseModel):
    """Command execution response."""

    result: Any = Field(..., description="Command execution result")


@router.get(
    "/commands/",
    response_model=CommandList,
    summary="List available commands",
    description="Get a list of all available commands that can be executed.",
    tags=["commands"],
    responses={
        200: {"description": "List of available commands"},
    },
)
async def list_commands(
    api_key: ApiKeyDep,
) -> CommandList:
    """
    List all available commands.

    Args:
        api_key: Validated API key (from dependency)

    Returns:
        List of command info objects
    """
    registry = get_registry()
    commands = registry.list_commands()

    logger.info(f"Listed {len(commands)} commands")
    return CommandList(commands=commands)


@router.post(
    "/commands/{command_id}/",
    response_model=CommandResponse,
    summary="Execute a command",
    description=(
        "Execute a command by ID with optional parameters. "
        "Returns the command execution result."
    ),
    tags=["commands"],
    responses={
        200: {"description": "Command executed successfully"},
        400: {"description": "Invalid parameters"},
        404: {"description": "Command not found"},
        500: {"description": "Command execution error"},
    },
)
async def execute_command(
    command_id: str,
    request: CommandRequest,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
) -> CommandResponse:
    """
    Execute a command.

    Args:
        command_id: Command identifier
        request: Command parameters
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)

    Returns:
        Command execution result

    Raises:
        HTTPException: 404 if command not found
        HTTPException: 400 if parameters are invalid
        HTTPException: 500 if command execution fails
    """
    registry = get_registry()

    try:
        # Initialize vault manager
        vault = VaultManager(vault_path)

        # Execute command
        result = await registry.execute_command(
            id=command_id,
            vault_manager=vault,
            params=request.params,
        )

        logger.info(f"Command '{command_id}' executed successfully")
        return CommandResponse(result=result)

    except CommandNotFoundError as e:
        logger.warning(f"Command not found: {command_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
    except CommandError as e:
        logger.error(f"Command execution failed for '{command_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error executing command '{command_id}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Command execution failed",
        ) from e


__all__ = ["router"]
