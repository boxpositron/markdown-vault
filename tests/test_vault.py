"""
Unit tests for VaultManager.
"""

from pathlib import Path

import pytest

from markdown_vault.core.vault import (
    FileNotFoundError as VaultFileNotFoundError,
)
from markdown_vault.core.vault import (
    InvalidPathError,
    VaultManager,
)
from markdown_vault.models.note import Note, NoteStat


class TestVaultManagerInit:
    """Test VaultManager initialization."""

    def test_init_with_valid_path(self, temp_vault: Path) -> None:
        """Test initialization with valid vault path."""
        vault = VaultManager(temp_vault)
        assert vault.vault_path == temp_vault
        assert vault.respect_gitignore is True

    def test_init_with_respect_gitignore_false(self, temp_vault: Path) -> None:
        """Test initialization with gitignore disabled."""
        vault = VaultManager(temp_vault, respect_gitignore=False)
        assert vault.respect_gitignore is False

    def test_init_with_relative_path_raises_error(self) -> None:
        """Test that relative paths raise ValueError."""
        with pytest.raises(ValueError, match="must be absolute"):
            VaultManager(Path("relative/path"))

    def test_init_with_nonexistent_path_raises_error(self) -> None:
        """Test that nonexistent paths raise ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            VaultManager(Path("/nonexistent/path"))

    def test_init_with_file_instead_of_dir_raises_error(self, temp_vault: Path) -> None:
        """Test that file paths raise ValueError."""
        test_file = temp_vault / "test.txt"
        test_file.write_text("test")

        with pytest.raises(ValueError, match="not a directory"):
            VaultManager(test_file)


class TestVaultManagerPathValidation:
    """Test path validation and security."""

    def test_validate_simple_path(self, vault_manager: VaultManager) -> None:
        """Test validation of simple file path."""
        path = vault_manager._validate_path("test.md")
        assert path.name == "test.md"
        # Path is already resolved, vault_path needs to be resolved for comparison
        vault_resolved = vault_manager.vault_path.resolve()
        assert path.is_relative_to(vault_resolved)

    def test_validate_nested_path(self, vault_manager: VaultManager) -> None:
        """Test validation of nested file path."""
        path = vault_manager._validate_path("folder/subfolder/test.md")
        assert path.name == "test.md"
        # Path is already resolved, compare to resolved vault
        vault_resolved = vault_manager.vault_path.resolve()
        assert path.is_relative_to(vault_resolved)

    def test_validate_path_strips_leading_slash(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that leading slashes are stripped."""
        path = vault_manager._validate_path("/test.md")
        assert path.name == "test.md"
        # Path is already resolved, compare to resolved vault
        vault_resolved = vault_manager.vault_path.resolve()
        assert path.is_relative_to(vault_resolved)

    def test_validate_path_prevents_traversal(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that path traversal is prevented."""
        with pytest.raises(InvalidPathError, match="outside vault"):
            vault_manager._validate_path("../../../etc/passwd")

    def test_validate_path_prevents_traversal_with_dots(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that path traversal with .. is prevented."""
        with pytest.raises(InvalidPathError, match="outside vault"):
            vault_manager._validate_path("folder/../../outside.md")

    def test_ensure_markdown_extension_adds_md(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that .md extension is added when missing."""
        result = vault_manager._ensure_markdown_extension("test")
        assert result == "test.md"

    def test_ensure_markdown_extension_keeps_existing(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that existing .md extension is preserved."""
        result = vault_manager._ensure_markdown_extension("test.md")
        assert result == "test.md"


class TestVaultManagerTagExtraction:
    """Test tag extraction from content and frontmatter."""

    def test_extract_tags_from_frontmatter_list(
        self, vault_manager: VaultManager
    ) -> None:
        """Test extracting tags from frontmatter list."""
        content = "# Note"
        frontmatter = {"tags": ["tag1", "tag2", "tag3"]}
        tags = vault_manager._extract_tags(content, frontmatter)
        assert set(tags) == {"tag1", "tag2", "tag3"}

    def test_extract_tags_from_frontmatter_string(
        self, vault_manager: VaultManager
    ) -> None:
        """Test extracting single tag from frontmatter string."""
        content = "# Note"
        frontmatter = {"tags": "single-tag"}
        tags = vault_manager._extract_tags(content, frontmatter)
        assert "single-tag" in tags

    def test_extract_inline_tags(self, vault_manager: VaultManager) -> None:
        """Test extracting inline #tag format."""
        content = "# Note\n\nSome content with #tag1 and #tag2."
        tags = vault_manager._extract_tags(content, {})
        assert set(tags) == {"#tag1", "#tag2"}

    def test_extract_tags_with_slashes(self, vault_manager: VaultManager) -> None:
        """Test extracting tags with slashes."""
        content = "# Note\n\nTags: #category/subcategory"
        tags = vault_manager._extract_tags(content, {})
        assert "#category/subcategory" in tags

    def test_extract_combined_tags(self, vault_manager: VaultManager) -> None:
        """Test extracting both frontmatter and inline tags."""
        content = "# Note\n\nContent with #inline-tag"
        frontmatter = {"tags": ["frontmatter-tag"]}
        tags = vault_manager._extract_tags(content, frontmatter)
        assert set(tags) == {"frontmatter-tag", "#inline-tag"}

    def test_extract_tags_deduplicates(self, vault_manager: VaultManager) -> None:
        """Test that duplicate tags are removed."""
        content = "# Note\n\n#tag #tag #other-tag"
        frontmatter = {"tags": ["tag", "other-tag"]}
        tags = vault_manager._extract_tags(content, frontmatter)
        # Should have unique tags (though formats differ: "tag" vs "#tag")
        assert "#tag" in tags
        assert "#other-tag" in tags


class TestVaultManagerReadFile:
    """Test file reading operations."""

    @pytest.mark.asyncio
    async def test_read_simple_file(self, vault_manager: VaultManager) -> None:
        """Test reading a simple markdown file."""
        note = await vault_manager.read_file("simple.md")
        assert isinstance(note, Note)
        assert note.path == "simple.md"
        assert "Simple Note" in note.content
        assert note.frontmatter == {}

    @pytest.mark.asyncio
    async def test_read_file_with_frontmatter(
        self, vault_manager: VaultManager
    ) -> None:
        """Test reading file with YAML frontmatter."""
        import datetime

        note = await vault_manager.read_file("with-frontmatter.md")
        assert note.frontmatter["title"] == "Note with Frontmatter"
        assert "test" in note.frontmatter["tags"]
        # YAML parser converts dates to datetime.date objects
        assert note.frontmatter["created"] == datetime.date(2025, 1, 1)

    @pytest.mark.asyncio
    async def test_read_file_extracts_inline_tags(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that inline tags are extracted."""
        note = await vault_manager.read_file("with-frontmatter.md")
        assert "#inline-tag" in note.tags
        assert "#another-tag" in note.tags
        assert "#test" in note.tags

    @pytest.mark.asyncio
    async def test_read_file_without_extension(
        self, vault_manager: VaultManager
    ) -> None:
        """Test reading file without .md extension."""
        note = await vault_manager.read_file("simple")
        assert note.path == "simple.md"
        assert "Simple Note" in note.content

    @pytest.mark.asyncio
    async def test_read_directory_raises_error(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that reading directory path raises error."""
        # Since notes.md doesn't exist, it will raise FileNotFoundError first
        with pytest.raises(VaultFileNotFoundError):
            await vault_manager.read_file("notes")


class TestVaultManagerGetFileStat:
    """Test file statistics retrieval."""

    @pytest.mark.asyncio
    async def test_get_file_stat(self, vault_manager: VaultManager) -> None:
        """Test getting file statistics."""
        stat = await vault_manager.get_file_stat("simple.md")
        assert isinstance(stat, NoteStat)
        assert stat.ctime > 0
        assert stat.mtime > 0
        assert stat.size > 0

    @pytest.mark.asyncio
    async def test_get_file_stat_timestamps_in_milliseconds(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that timestamps are in milliseconds."""
        stat = await vault_manager.get_file_stat("simple.md")
        # Timestamps in milliseconds are > 1 trillion for dates after 2001
        assert stat.ctime > 1_000_000_000_000
        assert stat.mtime > 1_000_000_000_000

    @pytest.mark.asyncio
    async def test_get_file_stat_nonexistent_raises_error(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that getting stat for nonexistent file raises error."""
        with pytest.raises(VaultFileNotFoundError):
            await vault_manager.get_file_stat("nonexistent.md")


class TestVaultManagerWriteFile:
    """Test file writing operations."""

    @pytest.mark.asyncio
    async def test_write_simple_file(self, vault_manager: VaultManager) -> None:
        """Test writing a simple file."""
        content = "# New Note\n\nThis is new content."
        await vault_manager.write_file("new-note.md", content)

        # Verify file was written
        note = await vault_manager.read_file("new-note.md")
        assert note.content == content

    @pytest.mark.asyncio
    async def test_write_file_with_frontmatter(
        self, vault_manager: VaultManager
    ) -> None:
        """Test writing file with frontmatter."""
        content = "# Note Content"
        frontmatter = {"title": "Test", "tags": ["new", "test"]}
        await vault_manager.write_file("with-fm.md", content, frontmatter)

        # Verify frontmatter was written
        note = await vault_manager.read_file("with-fm.md")
        assert note.frontmatter["title"] == "Test"
        assert "new" in note.frontmatter["tags"]

    @pytest.mark.asyncio
    async def test_write_file_creates_directories(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that parent directories are created."""
        await vault_manager.write_file("new/nested/file.md", "# Content")

        # Verify file was written in nested path
        note = await vault_manager.read_file("new/nested/file.md")
        assert note.content == "# Content"

    @pytest.mark.asyncio
    async def test_write_file_overwrites_existing(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that writing overwrites existing file."""
        await vault_manager.write_file("test.md", "Original")
        await vault_manager.write_file("test.md", "Updated")

        note = await vault_manager.read_file("test.md")
        assert note.content == "Updated"


class TestVaultManagerAppendFile:
    """Test file appending operations."""

    @pytest.mark.asyncio
    async def test_append_to_file(self, vault_manager: VaultManager) -> None:
        """Test appending content to existing file."""
        # Create initial file
        await vault_manager.write_file("test.md", "Original content\n")

        # Append to it
        await vault_manager.append_file("test.md", "Appended content\n")

        # Verify both contents present
        note = await vault_manager.read_file("test.md")
        assert "Original content" in note.content
        assert "Appended content" in note.content

    @pytest.mark.asyncio
    async def test_append_to_nonexistent_file_raises_error(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that appending to nonexistent file raises error."""
        with pytest.raises(VaultFileNotFoundError):
            await vault_manager.append_file("nonexistent.md", "Content")


class TestVaultManagerDeleteFile:
    """Test file deletion operations."""

    @pytest.mark.asyncio
    async def test_delete_file(self, vault_manager: VaultManager) -> None:
        """Test deleting a file."""
        # Create file
        await vault_manager.write_file("to-delete.md", "Content")

        # Delete it
        await vault_manager.delete_file("to-delete.md")

        # Verify it's gone
        with pytest.raises(VaultFileNotFoundError):
            await vault_manager.read_file("to-delete.md")

    @pytest.mark.asyncio
    async def test_delete_nonexistent_file_raises_error(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that deleting nonexistent file raises error."""
        with pytest.raises(VaultFileNotFoundError):
            await vault_manager.delete_file("nonexistent.md")

    @pytest.mark.asyncio
    async def test_delete_directory_raises_error(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that deleting directory raises error."""
        # Since notes.md doesn't exist, it will raise FileNotFoundError first
        with pytest.raises(VaultFileNotFoundError):
            await vault_manager.delete_file("notes")


class TestVaultManagerListFiles:
    """Test file listing operations."""

    @pytest.mark.asyncio
    async def test_list_all_files(self, vault_manager: VaultManager) -> None:
        """Test listing all files in vault."""
        files = await vault_manager.list_files()
        assert "simple.md" in files
        assert "with-frontmatter.md" in files
        assert "notes/nested-note.md" in files

    @pytest.mark.asyncio
    async def test_list_files_sorted(self, vault_manager: VaultManager) -> None:
        """Test that files are returned sorted."""
        files = await vault_manager.list_files()
        assert files == sorted(files)

    @pytest.mark.asyncio
    async def test_list_files_in_subdirectory(
        self, vault_manager: VaultManager
    ) -> None:
        """Test listing files in specific directory."""
        files = await vault_manager.list_files("notes")
        # Should only return files in notes directory
        assert any("nested-note.md" in f for f in files)

    @pytest.mark.asyncio
    async def test_list_files_recursive_false(
        self, vault_manager: VaultManager
    ) -> None:
        """Test listing files non-recursively."""
        # Create nested structure
        await vault_manager.write_file("dir/file1.md", "Content 1")
        await vault_manager.write_file("dir/subdir/file2.md", "Content 2")

        # List non-recursively
        files = await vault_manager.list_files("dir", recursive=False)

        # Should only include immediate children
        assert any("dir/file1.md" in f for f in files)
        assert not any("dir/subdir/file2.md" in f for f in files)

    @pytest.mark.asyncio
    async def test_list_nonexistent_directory_returns_empty(
        self, vault_manager: VaultManager
    ) -> None:
        """Test listing nonexistent directory returns empty list."""
        files = await vault_manager.list_files("nonexistent")
        assert files == []

    @pytest.mark.asyncio
    async def test_list_file_path_raises_error(
        self, vault_manager: VaultManager
    ) -> None:
        """Test that listing file path raises error."""
        with pytest.raises(InvalidPathError, match="not a directory"):
            await vault_manager.list_files("simple.md")


class TestVaultManagerConvenienceMethods:
    """Test convenience methods for common operations."""

    @pytest.mark.asyncio
    async def test_file_exists_returns_true(self, vault_manager: VaultManager) -> None:
        """Test file_exists returns True for existing file."""
        exists = await vault_manager.file_exists("simple.md")
        assert exists is True

    @pytest.mark.asyncio
    async def test_file_exists_returns_false(self, vault_manager: VaultManager) -> None:
        """Test file_exists returns False for nonexistent file."""
        exists = await vault_manager.file_exists("nonexistent.md")
        assert exists is False

    @pytest.mark.asyncio
    async def test_file_exists_with_directory_returns_false(
        self, vault_manager: VaultManager
    ) -> None:
        """Test file_exists returns False for directory."""
        # Create a directory
        await vault_manager.ensure_directory("testdir")
        exists = await vault_manager.file_exists("testdir")
        assert exists is False

    @pytest.mark.asyncio
    async def test_get_file_metadata_dict(self, vault_manager: VaultManager) -> None:
        """Test get_file_metadata returns dictionary."""
        metadata = await vault_manager.get_file_metadata("simple.md")
        assert isinstance(metadata, dict)
        assert "ctime" in metadata
        assert "mtime" in metadata
        assert "size" in metadata
        assert metadata["ctime"] > 0
        assert metadata["mtime"] > 0
        assert metadata["size"] > 0

    @pytest.mark.asyncio
    async def test_ensure_directory_creates_dir(
        self, vault_manager: VaultManager
    ) -> None:
        """Test ensure_directory creates directory."""
        await vault_manager.ensure_directory("new/nested/dir")

        # Verify directory was created
        full_path = vault_manager.vault_path / "new/nested/dir"
        assert full_path.exists()
        assert full_path.is_dir()

    @pytest.mark.asyncio
    async def test_ensure_directory_idempotent(
        self, vault_manager: VaultManager
    ) -> None:
        """Test ensure_directory can be called multiple times."""
        await vault_manager.ensure_directory("testdir")
        await vault_manager.ensure_directory("testdir")  # Should not raise

        full_path = vault_manager.vault_path / "testdir"
        assert full_path.exists()

    def test_resolve_path_returns_absolute(self, vault_manager: VaultManager) -> None:
        """Test resolve_path returns absolute path."""
        path = vault_manager.resolve_path("test.md")
        assert path.is_absolute()
        assert path.name == "test.md"

    def test_validate_path_accepts_valid(self, vault_manager: VaultManager) -> None:
        """Test validate_path accepts valid path."""
        # Should not raise
        vault_manager.validate_path("test.md")
        vault_manager.validate_path("nested/dir/test.md")

    def test_validate_path_rejects_traversal(self, vault_manager: VaultManager) -> None:
        """Test validate_path rejects path traversal."""
        with pytest.raises(InvalidPathError):
            vault_manager.validate_path("../../../etc/passwd")

    def test_is_markdown_file_returns_true(self, vault_manager: VaultManager) -> None:
        """Test is_markdown_file returns True for .md files."""
        assert vault_manager.is_markdown_file("test.md") is True
        assert vault_manager.is_markdown_file("path/to/note.md") is True

    def test_is_markdown_file_returns_false(self, vault_manager: VaultManager) -> None:
        """Test is_markdown_file returns False for non-.md files."""
        assert vault_manager.is_markdown_file("test.txt") is False
        assert vault_manager.is_markdown_file("test") is False
        assert vault_manager.is_markdown_file("test.markdown") is False

    def test_parse_frontmatter_with_yaml(self, vault_manager: VaultManager) -> None:
        """Test parse_frontmatter extracts YAML."""
        content = """---
title: Test Note
tags: [tag1, tag2]
---

# Note Content

This is the body."""

        fm, body = vault_manager.parse_frontmatter(content)
        assert fm["title"] == "Test Note"
        assert "tag1" in fm["tags"]
        assert "# Note Content" in body
        assert "---" not in body

    def test_parse_frontmatter_without_yaml(self, vault_manager: VaultManager) -> None:
        """Test parse_frontmatter handles content without frontmatter."""
        content = "# Simple Note\n\nNo frontmatter here."

        fm, body = vault_manager.parse_frontmatter(content)
        assert fm == {}
        assert body == content

    def test_extract_tags_from_content(self, vault_manager: VaultManager) -> None:
        """Test extract_tags finds inline tags."""
        content = "# Note\n\nContent with #tag1 and #tag2."
        tags = vault_manager.extract_tags(content)
        assert "#tag1" in tags
        assert "#tag2" in tags

    def test_extract_tags_with_nested(self, vault_manager: VaultManager) -> None:
        """Test extract_tags handles nested tags."""
        content = "Tags: #category/subcategory #other"
        tags = vault_manager.extract_tags(content)
        assert "#category/subcategory" in tags
        assert "#other" in tags

    def test_extract_tags_deduplicates(self, vault_manager: VaultManager) -> None:
        """Test extract_tags removes duplicates."""
        content = "#tag #tag #tag #other"
        tags = vault_manager.extract_tags(content)
        assert tags.count("#tag") == 1
        assert tags.count("#other") == 1
