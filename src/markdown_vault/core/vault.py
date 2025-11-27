"""
Vault management for markdown file operations.

This module provides the VaultManager class which handles:
- File reading/writing with async I/O
- Directory listing with gitignore support
- Frontmatter and tag extraction
- Path validation and security
- File metadata (ctime, mtime, size)
"""

import logging
import re
from pathlib import Path
from typing import List, Optional

import aiofiles
import frontmatter

from markdown_vault.models.note import Note, NoteStat

logger = logging.getLogger(__name__)


class VaultError(Exception):
    """Base exception for vault operations."""

    pass


class FileNotFoundError(VaultError):
    """Raised when a file is not found in the vault."""

    pass


class InvalidPathError(VaultError):
    """Raised when a path is invalid or represents a security risk."""

    pass


class VaultManager:
    """
    Manages markdown vault operations.

    Handles file I/O, directory listing, frontmatter parsing, and
    ensures secure path handling with traversal prevention.
    """

    def __init__(self, vault_path: Path, respect_gitignore: bool = True) -> None:
        """
        Initialize vault manager.

        Args:
            vault_path: Absolute path to the vault directory
            respect_gitignore: Whether to honor .gitignore files when listing

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
        self.respect_gitignore = respect_gitignore
        logger.info(f"Initialized VaultManager for: {vault_path}")

    def _validate_path(self, filepath: str) -> Path:
        """
        Validate and resolve a file path within the vault.

        Prevents path traversal attacks by ensuring the resolved path
        is within the vault directory.

        Args:
            filepath: Relative path within the vault

        Returns:
            Absolute resolved path within vault

        Raises:
            InvalidPathError: If path is invalid or outside vault
        """
        # Remove leading slashes
        filepath = filepath.lstrip("/")

        # Resolve path relative to vault
        full_path = (self.vault_path / filepath).resolve()

        # Ensure path is within vault (prevent traversal)
        try:
            full_path.relative_to(self.vault_path)
        except ValueError:
            logger.warning(f"Path traversal attempt: {filepath}")
            raise InvalidPathError(f"Path is outside vault: {filepath}")

        return full_path

    def _ensure_markdown_extension(self, filepath: str) -> str:
        """
        Ensure filepath ends with .md extension.

        Args:
            filepath: File path to check

        Returns:
            File path with .md extension
        """
        if not filepath.endswith(".md"):
            return f"{filepath}.md"
        return filepath

    def _extract_tags(self, content: str, frontmatter_data: dict) -> List[str]:
        """
        Extract tags from frontmatter and inline content.

        Args:
            content: Markdown content
            frontmatter_data: Parsed frontmatter dictionary

        Returns:
            List of unique tags (both frontmatter and inline)
        """
        tags = set()

        # Extract from frontmatter
        fm_tags = frontmatter_data.get("tags", [])
        if isinstance(fm_tags, list):
            tags.update(fm_tags)
        elif isinstance(fm_tags, str):
            tags.add(fm_tags)

        # Extract inline tags (#tag format)
        inline_tag_pattern = r"#[\w/-]+"
        inline_tags = re.findall(inline_tag_pattern, content)
        tags.update(inline_tags)

        return sorted(list(tags))

    async def read_file(self, filepath: str) -> Note:
        """
        Read a markdown file and parse its content.

        Args:
            filepath: Path to file relative to vault root

        Returns:
            Note object with parsed content and metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            InvalidPathError: If path is invalid
        """
        # Ensure .md extension
        filepath = self._ensure_markdown_extension(filepath)

        # Validate and resolve path
        full_path = self._validate_path(filepath)

        # Check if file exists
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        if not full_path.is_file():
            raise InvalidPathError(f"Path is not a file: {filepath}")

        # Read file asynchronously
        async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
            raw_content = await f.read()

        # Parse frontmatter
        post = frontmatter.loads(raw_content)
        content = post.content
        frontmatter_data = dict(post.metadata)

        # Extract tags
        tags = self._extract_tags(content, frontmatter_data)

        logger.debug(f"Read file: {filepath}")

        return Note(
            path=filepath,
            content=content,
            frontmatter=frontmatter_data,
            tags=tags,
        )

    async def get_file_stat(self, filepath: str) -> NoteStat:
        """
        Get file statistics.

        Args:
            filepath: Path to file relative to vault root

        Returns:
            NoteStat with ctime, mtime, and size

        Raises:
            FileNotFoundError: If file doesn't exist
            InvalidPathError: If path is invalid
        """
        # Ensure .md extension
        filepath = self._ensure_markdown_extension(filepath)

        # Validate and resolve path
        full_path = self._validate_path(filepath)

        # Check if file exists
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Get file stats
        stat = full_path.stat()

        return NoteStat(
            ctime=int(stat.st_ctime * 1000),  # Convert to milliseconds
            mtime=int(stat.st_mtime * 1000),  # Convert to milliseconds
            size=stat.st_size,
        )

    async def write_file(
        self, filepath: str, content: str, frontmatter_data: Optional[dict] = None
    ) -> None:
        """
        Write content to a markdown file.

        Creates parent directories if they don't exist.

        Args:
            filepath: Path to file relative to vault root
            content: Markdown content to write
            frontmatter_data: Optional frontmatter dictionary

        Raises:
            InvalidPathError: If path is invalid
        """
        # Ensure .md extension
        filepath = self._ensure_markdown_extension(filepath)

        # Validate and resolve path
        full_path = self._validate_path(filepath)

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Prepare content with frontmatter if provided
        if frontmatter_data:
            post = frontmatter.Post(content, **frontmatter_data)
            final_content = frontmatter.dumps(post)
        else:
            final_content = content

        # Write file asynchronously
        async with aiofiles.open(full_path, "w", encoding="utf-8") as f:
            await f.write(final_content)

        logger.info(f"Wrote file: {filepath}")

    async def append_file(self, filepath: str, content: str) -> None:
        """
        Append content to an existing markdown file.

        Args:
            filepath: Path to file relative to vault root
            content: Content to append

        Raises:
            FileNotFoundError: If file doesn't exist
            InvalidPathError: If path is invalid
        """
        # Ensure .md extension
        filepath = self._ensure_markdown_extension(filepath)

        # Validate and resolve path
        full_path = self._validate_path(filepath)

        # Check if file exists
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Append content asynchronously
        async with aiofiles.open(full_path, "a", encoding="utf-8") as f:
            await f.write(content)

        logger.info(f"Appended to file: {filepath}")

    async def delete_file(self, filepath: str) -> None:
        """
        Delete a markdown file.

        Args:
            filepath: Path to file relative to vault root

        Raises:
            FileNotFoundError: If file doesn't exist
            InvalidPathError: If path is invalid
        """
        # Ensure .md extension
        filepath = self._ensure_markdown_extension(filepath)

        # Validate and resolve path
        full_path = self._validate_path(filepath)

        # Check if file exists
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        if not full_path.is_file():
            raise InvalidPathError(f"Path is not a file: {filepath}")

        # Delete file
        full_path.unlink()

        logger.info(f"Deleted file: {filepath}")

    async def list_files(self, directory: str = "") -> List[str]:
        """
        List all markdown files in a directory.

        Args:
            directory: Directory path relative to vault root (empty for root)

        Returns:
            List of file paths relative to vault root

        Raises:
            InvalidPathError: If path is invalid
        """
        # Validate and resolve path
        if directory:
            full_path = self._validate_path(directory)
        else:
            full_path = self.vault_path

        # Check if directory exists
        if not full_path.exists():
            return []

        if not full_path.is_dir():
            raise InvalidPathError(f"Path is not a directory: {directory}")

        # List all .md files recursively
        files = []
        for md_file in full_path.rglob("*.md"):
            # Get relative path from vault root
            rel_path = md_file.relative_to(self.vault_path)
            files.append(str(rel_path))

        # Sort for consistent ordering
        files.sort()

        logger.debug(f"Listed {len(files)} files in: {directory or 'vault root'}")

        return files


__all__ = ["VaultManager", "VaultError", "FileNotFoundError", "InvalidPathError"]
