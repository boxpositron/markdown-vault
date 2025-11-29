"""
Vault API routes for markdown file operations.

This module provides all vault-level endpoints:
- GET /vault/ - List all files
- GET /vault/{filepath} - Read file (markdown or JSON)
- PUT /vault/{filepath} - Create/update file
- POST /vault/{filepath} - Append to file
- DELETE /vault/{filepath} - Delete file
"""

import logging

from fastapi import APIRouter, Header, HTTPException, Request, Response, status
from fastapi.responses import PlainTextResponse

from markdown_vault.api.deps import ApiKeyDep, VaultPathDep
from markdown_vault.core.patch_engine import (
    InvalidTargetError,
    PatchEngine,
    PatchError,
    TargetNotFoundError,
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


@router.get(
    "/vault/",
    response_model=list[str],
    summary="List all files",
    description="Returns a list of all markdown files in the vault.",
    tags=["vault"],
)
async def list_vault_files(
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
) -> list[str]:
    """
    List all markdown files in the vault.

    Args:
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)

    Returns:
        List of file paths relative to vault root
    """
    vault = VaultManager(vault_path)
    files = await vault.list_files()
    logger.info(f"Listed {len(files)} files")
    return files


@router.get(
    "/vault/{filepath:path}",
    response_model=None,  # Disable automatic response model
    summary="Read file",
    description=(
        "Read a markdown file. Returns either raw markdown (text/markdown) or "
        "JSON format with metadata (application/vnd.olrapi.note+json) based on "
        "Accept header."
    ),
    tags=["vault"],
    responses={
        200: {
            "description": "File content",
            "content": {
                CONTENT_TYPE_MARKDOWN: {"schema": {"type": "string"}},
                CONTENT_TYPE_JSON: {
                    "schema": {"$ref": "#/components/schemas/NoteJson"}
                },
            },
        },
        404: {"description": "File not found"},
    },
)
async def read_vault_file(
    filepath: str,
    request: Request,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
    accept: str = Header(default=CONTENT_TYPE_MARKDOWN),
) -> PlainTextResponse | NoteJson:
    """
    Read a markdown file from the vault.

    Supports content negotiation via Accept header:
    - text/markdown: Returns raw markdown content
    - application/vnd.olrapi.note+json: Returns JSON with metadata

    Args:
        filepath: Path to file relative to vault root
        request: HTTP request
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)
        accept: Accept header for content negotiation

    Returns:
        File content in requested format

    Raises:
        HTTPException: 404 if file not found
        HTTPException: 400 if path is invalid
    """
    vault = VaultManager(vault_path)

    try:
        # Read the file
        note = await vault.read_file(filepath)

        # Determine response format based on Accept header
        if CONTENT_TYPE_JSON in accept:
            # Return JSON format with metadata
            stat = await vault.get_file_stat(filepath)
            note_json = note.to_json_format(stat)
            logger.info(f"Read file (JSON): {filepath}")
            return note_json
        else:
            # Return raw markdown (rebuild with frontmatter if present)
            if note.frontmatter:
                import frontmatter

                post = frontmatter.Post(note.content, **note.frontmatter)
                content = frontmatter.dumps(post)
            else:
                content = note.content

            logger.info(f"Read file (markdown): {filepath}")
            return PlainTextResponse(
                content=content,
                media_type=CONTENT_TYPE_MARKDOWN,
            )

    except VaultFileNotFoundError as e:
        logger.warning(f"File not found: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/vault/{filepath:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Create or update file",
    description="Create a new file or completely replace an existing file.",
    tags=["vault"],
    responses={
        204: {"description": "File created or updated successfully"},
        400: {"description": "Invalid path or content"},
    },
)
async def create_or_update_file(
    filepath: str,
    request: Request,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
) -> Response:
    """
    Create or update a markdown file.

    The entire file content is replaced. If the file doesn't exist,
    it will be created along with any necessary parent directories.

    Args:
        filepath: Path to file relative to vault root
        request: HTTP request with body content
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 400 if path is invalid
    """
    vault = VaultManager(vault_path)

    # Read request body
    content = await request.body()
    content_str = content.decode("utf-8")

    try:
        # Write the file (VaultManager handles frontmatter parsing)
        await vault.write_file(filepath, content_str)
        logger.info(f"Created/updated file: {filepath}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/vault/{filepath:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Append to file",
    description="Append content to an existing file.",
    tags=["vault"],
    responses={
        204: {"description": "Content appended successfully"},
        404: {"description": "File not found"},
        400: {"description": "Invalid path"},
    },
)
async def append_to_file(
    filepath: str,
    request: Request,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
) -> Response:
    """
    Append content to an existing markdown file.

    The content is appended to the end of the file without any
    additional formatting or newlines.

    Args:
        filepath: Path to file relative to vault root
        request: HTTP request with body content
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if file not found
        HTTPException: 400 if path is invalid
    """
    vault = VaultManager(vault_path)

    # Read request body
    content = await request.body()
    content_str = content.decode("utf-8")

    try:
        # Append to the file
        await vault.append_file(filepath, content_str)
        logger.info(f"Appended to file: {filepath}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except VaultFileNotFoundError as e:
        logger.warning(f"File not found: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/vault/{filepath:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete file",
    description="Delete a markdown file from the vault.",
    tags=["vault"],
    responses={
        204: {"description": "File deleted successfully"},
        404: {"description": "File not found"},
        400: {"description": "Invalid path"},
    },
)
async def delete_file(
    filepath: str,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
) -> Response:
    """
    Delete a markdown file from the vault.

    Args:
        filepath: Path to file relative to vault root
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if file not found
        HTTPException: 400 if path is invalid
    """
    vault = VaultManager(vault_path)

    try:
        # Delete the file
        await vault.delete_file(filepath)
        logger.info(f"Deleted file: {filepath}")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except VaultFileNotFoundError as e:
        logger.warning(f"File not found: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.patch(
    "/vault/{filepath:path}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Partially update file",
    description=(
        "Apply a partial update to a markdown file using targeted operations. "
        "Supports heading-based targeting, block references, and frontmatter updates."
    ),
    tags=["vault"],
    responses={
        204: {"description": "File updated successfully"},
        404: {"description": "File or target not found"},
        400: {"description": "Invalid operation or target"},
    },
)
async def patch_file(
    filepath: str,
    request: Request,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
    operation: str = Header(..., description="Operation: append, prepend, or replace"),
    target_type: str = Header(
        ...,
        alias="Target-Type",
        description="Target type: heading, block, or frontmatter",
    ),
    target: str = Header(..., description="Target specifier"),
    create_target_if_missing: bool = Header(
        default=False,
        alias="Create-Target-If-Missing",
        description="Create target if it doesn't exist (headings only)",
    ),
) -> Response:
    """
    Apply a partial update to a markdown file.

    Uses custom headers to specify the operation:
    - Operation: append, prepend, or replace
    - Target-Type: heading, block, or frontmatter
    - Target: Target specifier (format depends on Target-Type)
    - Create-Target-If-Missing: Create heading if not found (optional)

    Target formats:
    - heading: "Heading::Subheading:N" (:: separates hierarchy, :N is 1-based index)
    - block: "blockid" (without ^ prefix)
    - frontmatter: "field_name"

    Args:
        filepath: Path to file relative to vault root
        request: HTTP request with body content
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)
        operation: Operation to perform
        target_type: Type of target
        target: Target specifier
        create_target_if_missing: Whether to create target if missing

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 404 if file or target not found
        HTTPException: 400 if operation or target is invalid
    """
    vault = VaultManager(vault_path)
    engine = PatchEngine()

    # Read request body
    content = await request.body()
    new_content = content.decode("utf-8")

    try:
        # Read the file
        note = await vault.read_file(filepath)

        # Rebuild full content with frontmatter
        if note.frontmatter:
            import frontmatter as fm

            post = fm.Post(note.content, **note.frontmatter)
            original_content = fm.dumps(post)
        else:
            original_content = note.content

        # Apply patch
        updated_content = engine.apply_patch(
            content=original_content,
            operation=operation.lower(),
            target_type=target_type.lower(),
            target=target,
            new_content=new_content,
            create_if_missing=create_target_if_missing,
        )

        # Write back to file
        await vault.write_file(filepath, updated_content)
        logger.info(
            f"Patched file: {filepath} (op={operation}, type={target_type}, target={target})"
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except VaultFileNotFoundError as e:
        logger.warning(f"File not found: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except TargetNotFoundError as e:
        logger.warning(f"Target not found in {filepath}: {target}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except (InvalidTargetError, PatchError) as e:
        logger.warning(f"Invalid patch operation on {filepath}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InvalidPathError as e:
        logger.warning(f"Invalid path: {filepath}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


__all__ = ["router"]
