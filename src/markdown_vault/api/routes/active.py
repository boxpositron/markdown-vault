"""
Active file API routes for session-based file operations.

This module provides endpoints for managing and operating on the currently
active file without requiring the filepath in each request:
- GET /active/ - Get active file content
- PUT /active/ - Update active file content
- POST /active/ - Append to active file
- PATCH /active/ - Partial update to active file
- DELETE /active/ - Delete active file
- POST /open/{filename} - Set file as active
"""

import logging

from fastapi import APIRouter, Header, HTTPException, Request, Response, status
from fastapi.responses import PlainTextResponse

from markdown_vault.api.deps import (
    ActiveFileManagerDep,
    ApiKeyDep,
    SessionIdDep,
    VaultPathDep,
)
from markdown_vault.core.vault import (
    FileNotFoundError as VaultFileNotFoundError,
)
from markdown_vault.core.vault import (
    InvalidPathError,
    VaultManager,
)
from markdown_vault.models.note import NoteJson

logger = logging.getLogger(__name__)

router = APIRouter()

# Content type constants
CONTENT_TYPE_MARKDOWN = "text/markdown"
CONTENT_TYPE_JSON = "application/vnd.olrapi.note+json"


def _get_active_filepath(
    active_file_manager: ActiveFileManagerDep,
    session_id: str,
) -> str:
    """
    Get the active file path for the current session.

    Args:
        active_file_manager: Active file manager instance
        session_id: Current session ID

    Returns:
        Active file path

    Raises:
        HTTPException: 404 if no active file is set
    """
    filepath = active_file_manager.get_active_file(session_id)
    if not filepath:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active file set for this session. Use POST /open/{filename} to set one.",
        )
    return filepath


@router.post(
    "/open/{filename:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Set active file",
    description="Set the specified file as active for the current session.",
    tags=["active"],
    responses={
        204: {"description": "File set as active successfully"},
        404: {"description": "File not found"},
        400: {"description": "Invalid path"},
    },
)
async def set_active_file(
    filename: str,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
    active_file_manager: ActiveFileManagerDep,
    session_id: SessionIdDep,
    response: Response,
) -> None:
    """
    Set a file as the active file for the current session.

    Verifies the file exists before setting it as active. The session ID
    is stored in a cookie and returned to the client.

    Args:
        filename: Path to file relative to vault root
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)
        active_file_manager: Active file manager instance
        session_id: Session ID (from cookie or generated)
        response: HTTP response object

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 404 if file not found
        HTTPException: 400 if path is invalid
    """
    vault = VaultManager(vault_path)

    try:
        # Verify file exists
        await vault.read_file(filename)

        # Set as active
        active_file_manager.set_active_file(session_id, filename)

        # Set session cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=86400 * 30,  # 30 days
        )

        logger.info(f"Set active file for session {session_id}: {filename}")

    except VaultFileNotFoundError as e:
        logger.warning(f"File not found: {filename}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/active/",
    response_model=None,
    summary="Get active file",
    description=(
        "Get the content of the active file. Returns either raw markdown or "
        "JSON format based on Accept header."
    ),
    tags=["active"],
    responses={
        200: {
            "description": "Active file content",
            "content": {
                CONTENT_TYPE_MARKDOWN: {"schema": {"type": "string"}},
                CONTENT_TYPE_JSON: {
                    "schema": {"$ref": "#/components/schemas/NoteJson"}
                },
            },
        },
        404: {"description": "No active file set or file not found"},
    },
)
async def get_active_file(
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
    active_file_manager: ActiveFileManagerDep,
    session_id: SessionIdDep,
    accept: str = Header(default=CONTENT_TYPE_MARKDOWN),
) -> PlainTextResponse | NoteJson:
    """
    Get the content of the currently active file.

    Supports content negotiation via Accept header:
    - text/markdown: Returns raw markdown content
    - application/vnd.olrapi.note+json: Returns JSON with metadata

    Args:
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)
        active_file_manager: Active file manager instance
        session_id: Session ID (from cookie)
        accept: Accept header for content negotiation

    Returns:
        File content in requested format

    Raises:
        HTTPException: 404 if no active file set or file not found
    """
    filepath = _get_active_filepath(active_file_manager, session_id)
    vault = VaultManager(vault_path)

    try:
        # Read the file
        note = await vault.read_file(filepath)

        # Determine response format based on Accept header
        if CONTENT_TYPE_JSON in accept:
            # Return JSON format with metadata
            stat = await vault.get_file_stat(filepath)
            note_json = note.to_json_format(stat)
            logger.info(f"Read active file (JSON): {filepath}")
            return note_json
        # Return raw markdown (rebuild with frontmatter if present)
        if note.frontmatter:
            import frontmatter

            post = frontmatter.Post(note.content, **note.frontmatter)
            content = frontmatter.dumps(post)
        else:
            content = note.content

        logger.info(f"Read active file (markdown): {filepath}")
        return PlainTextResponse(
            content=content,
            media_type=CONTENT_TYPE_MARKDOWN,
        )

    except VaultFileNotFoundError as e:
        logger.warning(f"Active file not found: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put(
    "/active/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Update active file",
    description="Replace the entire content of the active file.",
    tags=["active"],
    responses={
        204: {"description": "File updated successfully"},
        404: {"description": "No active file set"},
        400: {"description": "Invalid content"},
    },
)
async def update_active_file(
    request: Request,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
    active_file_manager: ActiveFileManagerDep,
    session_id: SessionIdDep,
) -> Response:
    """
    Update the content of the currently active file.

    The entire file content is replaced with the request body.

    Args:
        request: HTTP request with body content
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)
        active_file_manager: Active file manager instance
        session_id: Session ID (from cookie)

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if no active file set
    """
    filepath = _get_active_filepath(active_file_manager, session_id)
    vault = VaultManager(vault_path)

    # Read request body
    content = await request.body()
    content_str = content.decode("utf-8")

    try:
        # Write the file
        await vault.write_file(filepath, content_str)
        logger.info(f"Updated active file: {filepath}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/active/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Append to active file",
    description="Append content to the end of the active file.",
    tags=["active"],
    responses={
        204: {"description": "Content appended successfully"},
        404: {"description": "No active file set or file not found"},
    },
)
async def append_to_active_file(
    request: Request,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
    active_file_manager: ActiveFileManagerDep,
    session_id: SessionIdDep,
) -> Response:
    """
    Append content to the currently active file.

    The content is appended to the end of the file without any
    additional formatting or newlines.

    Args:
        request: HTTP request with body content
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)
        active_file_manager: Active file manager instance
        session_id: Session ID (from cookie)

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if no active file set or file not found
    """
    filepath = _get_active_filepath(active_file_manager, session_id)
    vault = VaultManager(vault_path)

    # Read request body
    content = await request.body()
    content_str = content.decode("utf-8")

    try:
        # Append to the file
        await vault.append_file(filepath, content_str)
        logger.info(f"Appended to active file: {filepath}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except VaultFileNotFoundError as e:
        logger.warning(f"Active file not found: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/active/",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
    summary="Partial update active file",
    description="Partial update to active file (not yet implemented).",
    tags=["active"],
    responses={
        501: {"description": "Not implemented yet"},
        404: {"description": "No active file set"},
    },
)
async def patch_active_file(
    request: Request,
    api_key: ApiKeyDep,
    active_file_manager: ActiveFileManagerDep,
    session_id: SessionIdDep,
) -> Response:
    """
    Perform a partial update on the currently active file.

    This endpoint is reserved for future implementation. Will delegate
    to VaultManager's PATCH functionality when available.

    Args:
        request: HTTP request with patch content
        api_key: Validated API key (from dependency)
        active_file_manager: Active file manager instance
        session_id: Session ID (from cookie)

    Returns:
        501 Not Implemented

    Raises:
        HTTPException: 404 if no active file set
    """
    # Verify active file exists
    _get_active_filepath(active_file_manager, session_id)

    # TODO: Implement partial update logic when vault PATCH is ready
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Partial update not yet implemented. Use PUT to replace entire file.",
    )


@router.delete(
    "/active/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete active file",
    description="Delete the active file and clear it from the session.",
    tags=["active"],
    responses={
        204: {"description": "File deleted successfully"},
        404: {"description": "No active file set or file not found"},
    },
)
async def delete_active_file(
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
    active_file_manager: ActiveFileManagerDep,
    session_id: SessionIdDep,
) -> Response:
    """
    Delete the currently active file.

    The file is deleted from the vault and cleared from the session.

    Args:
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)
        active_file_manager: Active file manager instance
        session_id: Session ID (from cookie)

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if no active file set or file not found
    """
    filepath = _get_active_filepath(active_file_manager, session_id)
    vault = VaultManager(vault_path)

    try:
        # Delete the file
        await vault.delete_file(filepath)

        # Clear from session
        active_file_manager.clear_active_file(session_id)

        logger.info(f"Deleted active file: {filepath}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except VaultFileNotFoundError as e:
        logger.warning(f"Active file not found: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


__all__ = ["router"]
