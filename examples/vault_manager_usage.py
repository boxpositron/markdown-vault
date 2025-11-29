"""
Example usage of VaultManager for markdown file operations.

This demonstrates the core functionality of the VaultManager class
including file operations, directory operations, and markdown parsing.
"""

import asyncio
from pathlib import Path
from markdown_vault.core.vault import VaultManager


async def main() -> None:
    """Demonstrate VaultManager functionality."""
    # Initialize vault manager
    vault_path = Path(__file__).parent.parent / "tests" / "fixtures" / "sample_vault"
    vault = VaultManager(vault_path)

    print("=== VaultManager Example Usage ===\n")

    # 1. Reading a file
    print("1. Reading a file:")
    note = await vault.read_file("simple.md")
    print(f"   Path: {note.path}")
    print(f"   Content preview: {note.content[:50]}...")
    print(f"   Frontmatter: {note.frontmatter}")
    print(f"   Tags: {note.tags}\n")

    # 2. Checking if file exists
    print("2. Checking file existence:")
    exists = await vault.file_exists("simple.md")
    print(f"   simple.md exists: {exists}")
    exists = await vault.file_exists("nonexistent.md")
    print(f"   nonexistent.md exists: {exists}\n")

    # 3. Getting file metadata
    print("3. Getting file metadata:")
    metadata = await vault.get_file_metadata("simple.md")
    print(f"   Created: {metadata['ctime']} ms")
    print(f"   Modified: {metadata['mtime']} ms")
    print(f"   Size: {metadata['size']} bytes\n")

    # 4. Listing files
    print("4. Listing files:")
    files = await vault.list_files()
    print(f"   All files (recursive): {files}")

    files_nonrecursive = await vault.list_files(recursive=False)
    print(f"   Root files only: {files_nonrecursive}\n")

    # 5. Path validation
    print("5. Path validation:")
    print(f"   Is 'note.md' a markdown file? {vault.is_markdown_file('note.md')}")
    print(f"   Is 'note.txt' a markdown file? {vault.is_markdown_file('note.txt')}")

    try:
        vault.validate_path("../../etc/passwd")
        print("   Path traversal allowed (BAD)")
    except Exception:
        print("   Path traversal prevented (GOOD)\n")

    # 6. Parsing frontmatter
    print("6. Parsing frontmatter:")
    content = """---
title: Example Note
tags: [example, demo]
---

# Example Content

This is the body.
"""
    frontmatter_data, body = vault.parse_frontmatter(content)
    print(f"   Frontmatter: {frontmatter_data}")
    print(f"   Body preview: {body[:30]}...\n")

    # 7. Extracting inline tags
    print("7. Extracting inline tags:")
    content_with_tags = "Content with #tag1 and #category/subcategory tags."
    tags = vault.extract_tags(content_with_tags)
    print(f"   Found tags: {tags}\n")

    # 8. Resolving paths
    print("8. Resolving paths:")
    resolved = vault.resolve_path("notes/example.md")
    print(f"   Resolved path: {resolved}")
    print(f"   Is absolute: {resolved.is_absolute()}\n")

    print("=== All examples completed successfully! ===")


if __name__ == "__main__":
    asyncio.run(main())
