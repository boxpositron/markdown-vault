"""
Dependency injection helpers for FastAPI routes.

This module provides reusable dependencies for:
- Configuration access
- API key authentication
- Vault path resolution
- Active file management
- Session handling
"""

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader

from markdown_vault.core.active_file import ActiveFileManager
from markdown_vault.core.config import AppConfig
from markdown_vault.main import get_active_file_manager, get_app_config

# API key header scheme
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def get_config() -> AppConfig:
    """
    Get the application configuration.

    This dependency provides access to the global application configuration
    in route handlers.

    Returns:
        Application configuration instance

    Raises:
        HTTPException: If configuration is not initialized (500)
    """
    try:
        return get_app_config()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
    config: AppConfig = Depends(get_config),
) -> str:
    """
    Verify API key authentication.

    Checks the Authorization header against the configured API key.
    Supports both "Bearer <key>" and direct key formats.

    Args:
        api_key: API key from Authorization header
        config: Application configuration

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is missing or invalid (401)
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Handle "Bearer <key>" format
    if api_key.startswith("Bearer "):
        api_key = api_key[7:]

    # Verify against configured key
    expected_key = config.security.api_key
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured",
        )

    if api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return api_key


async def get_vault_path(config: AppConfig = Depends(get_config)) -> Path:
    """
    Get the vault path from configuration.

    Returns the resolved absolute path to the markdown vault directory.

    Args:
        config: Application configuration

    Returns:
        Absolute path to the vault directory

    Raises:
        HTTPException: If vault is not configured (500)
        HTTPException: If vault path does not exist (404)
    """
    if not config.vault:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vault not configured",
        )

    vault_path = Path(config.vault.path).expanduser().resolve()

    if not vault_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vault directory not found: {vault_path}",
        )

    if not vault_path.is_dir():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vault path is not a directory: {vault_path}",
        )

    return vault_path


def get_active_file_manager_dep() -> ActiveFileManager:
    """
    Get the global active file manager instance.

    Returns:
        ActiveFileManager instance

    Raises:
        HTTPException: If active file manager is not initialized (500)
    """
    try:
        return get_active_file_manager()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


async def get_session_id(
    request: Request,
    session_id: str | None = Cookie(default=None, alias="session_id"),
) -> str:
    """
    Get or create a session ID for the client.

    Retrieves the session ID from cookies. If not present, generates
    a new UUID-based session ID.

    Args:
        request: HTTP request
        session_id: Session ID from cookie (if present)

    Returns:
        Session ID string
    """
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


# Type aliases for dependency injection
ConfigDep = Annotated[AppConfig, Depends(get_config)]
ApiKeyDep = Annotated[str, Depends(verify_api_key)]
VaultPathDep = Annotated[Path, Depends(get_vault_path)]
ActiveFileManagerDep = Annotated[
    ActiveFileManager, Depends(get_active_file_manager_dep)
]
SessionIdDep = Annotated[str, Depends(get_session_id)]


__all__ = [
    "get_config",
    "verify_api_key",
    "get_vault_path",
    "get_active_file_manager_dep",
    "get_session_id",
    "ConfigDep",
    "ApiKeyDep",
    "VaultPathDep",
    "ActiveFileManagerDep",
    "SessionIdDep",
]
