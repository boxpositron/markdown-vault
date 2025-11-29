"""
Periodic notes API routes.

This module provides endpoints for periodic notes operations:
- GET /periodic/{period} - Read periodic note
- PUT /periodic/{period} - Create/update periodic note
- POST /periodic/{period} - Append to periodic note
- PATCH /periodic/{period} - Apply patches to periodic note
- DELETE /periodic/{period} - Delete periodic note

Supports all period types: daily, weekly, monthly, quarterly, yearly
All endpoints support the ?offset= query parameter (e.g., ?offset=+1, ?offset=-1, ?offset=today)
"""

import logging
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response, status
from fastapi.responses import PlainTextResponse

from markdown_vault.api.deps import ApiKeyDep, ConfigDep, VaultPathDep
from markdown_vault.core.patch_engine import (
    InvalidTargetError,
    PatchEngine,
    PatchError,
    TargetNotFoundError,
)
from markdown_vault.core.periodic_notes import PeriodicNotesManager, PeriodType
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


async def _get_periodic_note_path(
    period: PeriodType,
    offset: str,
    config: ConfigDep,
    vault_path: Path,
) -> Path:
    """
    Get the path for a periodic note based on period and offset.

    Args:
        period: Period type (daily, weekly, monthly, quarterly, yearly)
        offset: Offset string (e.g., "today", "+1", "-1")
        config: Application configuration
        vault_path: Vault root path

    Returns:
        Relative path to the periodic note (from vault root)

    Raises:
        HTTPException: If period is disabled or configuration is invalid
    """
    # Get period configuration
    period_configs = {
        "daily": config.periodic_notes.daily,
        "weekly": config.periodic_notes.weekly,
        "monthly": config.periodic_notes.monthly,
        "quarterly": config.periodic_notes.quarterly,
        "yearly": config.periodic_notes.yearly,
    }

    period_config = period_configs[period]

    # Check if period is enabled
    if not period_config.enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Periodic notes for '{period}' are disabled in configuration",
        )

    # Get note path
    manager = PeriodicNotesManager(vault_path)
    note_path = manager.get_note_path(period, offset, period_config)

    # Convert to relative path
    try:
        relative_path = note_path.relative_to(vault_path)
        return relative_path
    except ValueError:
        # Should never happen, but handle gracefully
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Note path is outside vault: {note_path}",
        )


@router.get(
    "/periodic/{period}",
    response_model=None,
    summary="Read periodic note",
    description=(
        "Read a periodic note. Returns either raw markdown (text/markdown) or "
        "JSON format with metadata (application/vnd.olrapi.note+json) based on "
        "Accept header. Supports offset query parameter."
    ),
    tags=["periodic"],
    responses={
        200: {
            "description": "Note content",
            "content": {
                CONTENT_TYPE_MARKDOWN: {"schema": {"type": "string"}},
                CONTENT_TYPE_JSON: {
                    "schema": {"$ref": "#/components/schemas/NoteJson"}
                },
            },
        },
        404: {"description": "Note not found"},
    },
)
async def read_periodic_note(
    period: PeriodType,
    request: Request,
    api_key: ApiKeyDep,
    config: ConfigDep,
    vault_path: VaultPathDep,
    offset: str = Query(default="today", description="Period offset (today, +1, -1)"),
    accept: str = Header(default=CONTENT_TYPE_MARKDOWN),
) -> PlainTextResponse | NoteJson:
    """
    Read a periodic note.

    Supports content negotiation via Accept header:
    - text/markdown: Returns raw markdown content
    - application/vnd.olrapi.note+json: Returns JSON with metadata

    Args:
        period: Period type (daily, weekly, monthly, quarterly, yearly)
        request: HTTP request
        api_key: Validated API key (from dependency)
        config: Application configuration
        vault_path: Vault root path (from dependency)
        offset: Period offset (default: "today")
        accept: Accept header for content negotiation

    Returns:
        Note content in requested format

    Raises:
        HTTPException: 404 if note not found
        HTTPException: 403 if period is disabled
    """
    # Get note path
    filepath = await _get_periodic_note_path(period, offset, config, vault_path)
    vault = VaultManager(vault_path)

    try:
        # Read the file
        note = await vault.read_file(str(filepath))

        # Determine response format based on Accept header
        if CONTENT_TYPE_JSON in accept:
            # Return JSON format with metadata
            stat = await vault.get_file_stat(str(filepath))
            note_json = note.to_json_format(stat)
            logger.info(f"Read periodic note (JSON): {period} offset={offset}")
            return note_json
        else:
            # Return raw markdown (rebuild with frontmatter if present)
            if note.frontmatter:
                import frontmatter

                post = frontmatter.Post(note.content, **note.frontmatter)
                content = frontmatter.dumps(post)
            else:
                content = note.content

            logger.info(f"Read periodic note (markdown): {period} offset={offset}")
            return PlainTextResponse(
                content=content,
                media_type=CONTENT_TYPE_MARKDOWN,
            )

    except VaultFileNotFoundError:
        logger.warning(f"Periodic note not found: {period} offset={offset}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Periodic note not found: {period} with offset {offset}",
        )
    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/periodic/{period}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Create or update periodic note",
    description="Create a new periodic note or completely replace an existing one. Supports offset query parameter.",
    tags=["periodic"],
    responses={
        204: {"description": "Note created or updated successfully"},
        400: {"description": "Invalid path or content"},
    },
)
async def create_or_update_periodic_note(
    period: PeriodType,
    request: Request,
    api_key: ApiKeyDep,
    config: ConfigDep,
    vault_path: VaultPathDep,
    offset: str = Query(default="today", description="Period offset (today, +1, -1)"),
) -> Response:
    """
    Create or update a periodic note.

    The entire note content is replaced. If the note doesn't exist,
    it will be created along with any necessary parent directories.

    Args:
        period: Period type (daily, weekly, monthly, quarterly, yearly)
        request: HTTP request with body content
        api_key: Validated API key (from dependency)
        config: Application configuration
        vault_path: Vault root path (from dependency)
        offset: Period offset (default: "today")

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 400 if path is invalid
        HTTPException: 403 if period is disabled
    """
    # Get note path
    filepath = await _get_periodic_note_path(period, offset, config, vault_path)
    vault = VaultManager(vault_path)

    # Read request body
    content = await request.body()
    content_str = content.decode("utf-8")

    try:
        # Write the file (VaultManager handles frontmatter parsing)
        await vault.write_file(str(filepath), content_str)
        logger.info(f"Created/updated periodic note: {period} offset={offset}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/periodic/{period}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Append to periodic note",
    description="Append content to an existing periodic note. Supports offset query parameter.",
    tags=["periodic"],
    responses={
        204: {"description": "Content appended successfully"},
        404: {"description": "Note not found"},
        400: {"description": "Invalid path"},
    },
)
async def append_to_periodic_note(
    period: PeriodType,
    request: Request,
    api_key: ApiKeyDep,
    config: ConfigDep,
    vault_path: VaultPathDep,
    offset: str = Query(default="today", description="Period offset (today, +1, -1)"),
) -> Response:
    """
    Append content to an existing periodic note.

    The content is appended to the end of the note without any
    additional formatting or newlines.

    Args:
        period: Period type (daily, weekly, monthly, quarterly, yearly)
        request: HTTP request with body content
        api_key: Validated API key (from dependency)
        config: Application configuration
        vault_path: Vault root path (from dependency)
        offset: Period offset (default: "today")

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if note not found
        HTTPException: 400 if path is invalid
        HTTPException: 403 if period is disabled
    """
    # Get note path
    filepath = await _get_periodic_note_path(period, offset, config, vault_path)
    vault = VaultManager(vault_path)

    # Read request body
    content = await request.body()
    content_str = content.decode("utf-8")

    try:
        # Append to file
        await vault.append_file(str(filepath), content_str)
        logger.info(f"Appended to periodic note: {period} offset={offset}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except VaultFileNotFoundError:
        logger.warning(f"Periodic note not found: {period} offset={offset}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Periodic note not found: {period} with offset {offset}",
        )
    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/periodic/{period}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Patch periodic note",
    description=(
        "Apply content patches to a periodic note. Uses operation-based patching "
        "with headers: Operation (append/prepend/replace/update), Target-Type "
        "(heading/block/line), and Target (identifier). Supports offset query parameter."
    ),
    tags=["periodic"],
    responses={
        204: {"description": "Patches applied successfully"},
        404: {"description": "Note or target not found"},
        400: {"description": "Invalid patch format or target"},
    },
)
async def patch_periodic_note(
    period: PeriodType,
    request: Request,
    api_key: ApiKeyDep,
    config: ConfigDep,
    vault_path: VaultPathDep,
    offset: str = Query(default="today", description="Period offset (today, +1, -1)"),
    operation: str = Header(default="replace", alias="Operation"),
    target_type: str = Header(default="heading", alias="Target-Type"),
    target: str = Header(..., alias="Target"),
    create_target_if_missing: bool = Header(
        default=False, alias="Create-Target-If-Missing"
    ),
) -> Response:
    """
    Apply patches to a periodic note.

    Uses operation-based patching via headers:
    - Operation: append, prepend, replace, update
    - Target-Type: heading, block, line
    - Target: identifier for the target location
    - Create-Target-If-Missing: create target if it doesn't exist

    Args:
        period: Period type (daily, weekly, monthly, quarterly, yearly)
        request: HTTP request with patch content
        api_key: Validated API key (from dependency)
        config: Application configuration
        vault_path: Vault root path (from dependency)
        offset: Period offset (default: "today")
        operation: Patch operation
        target_type: Type of target (heading, block, line)
        target: Target identifier
        create_target_if_missing: Create target if missing

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if note or target not found
        HTTPException: 400 if patch is invalid
        HTTPException: 403 if period is disabled
    """
    # Get note path
    filepath = await _get_periodic_note_path(period, offset, config, vault_path)
    vault = VaultManager(vault_path)

    # Read new content
    new_content = await request.body()
    new_content_str = new_content.decode("utf-8")

    try:
        # Read current file
        note = await vault.read_file(str(filepath))

        # Rebuild original content with frontmatter if present
        if note.frontmatter:
            import frontmatter as fm

            post = fm.Post(note.content, **note.frontmatter)
            original_content = fm.dumps(post)
        else:
            original_content = note.content

        # Apply patch
        engine = PatchEngine()
        updated_content = engine.apply_patch(
            content=original_content,
            operation=operation.lower(),
            target_type=target_type.lower(),
            target=target,
            new_content=new_content_str,
            create_if_missing=create_target_if_missing,
        )

        # Write updated content
        await vault.write_file(str(filepath), updated_content)
        logger.info(
            f"Patched periodic note: {period} offset={offset} "
            f"(op={operation}, type={target_type}, target={target})"
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except VaultFileNotFoundError:
        logger.warning(f"Periodic note not found: {period} offset={offset}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Periodic note not found: {period} with offset {offset}",
        )
    except TargetNotFoundError as e:
        logger.warning(f"Patch target not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (InvalidTargetError, PatchError) as e:
        logger.warning(f"Invalid patch: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/periodic/{period}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete periodic note",
    description="Delete a periodic note. Supports offset query parameter.",
    tags=["periodic"],
    responses={
        204: {"description": "Note deleted successfully"},
        404: {"description": "Note not found"},
    },
)
async def delete_periodic_note(
    period: PeriodType,
    api_key: ApiKeyDep,
    config: ConfigDep,
    vault_path: VaultPathDep,
    offset: str = Query(default="today", description="Period offset (today, +1, -1)"),
) -> Response:
    """
    Delete a periodic note.

    Args:
        period: Period type (daily, weekly, monthly, quarterly, yearly)
        api_key: Validated API key (from dependency)
        config: Application configuration
        vault_path: Vault root path (from dependency)
        offset: Period offset (default: "today")

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if note not found
        HTTPException: 403 if period is disabled
    """
    # Get note path
    filepath = await _get_periodic_note_path(period, offset, config, vault_path)
    vault = VaultManager(vault_path)

    try:
        # Delete the file
        await vault.delete_file(str(filepath))
        logger.info(f"Deleted periodic note: {period} offset={offset}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except VaultFileNotFoundError:
        logger.warning(f"Periodic note not found: {period} offset={offset}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Periodic note not found: {period} with offset {offset}",
        )


__all__ = ["router"]
