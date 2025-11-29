"""
Tests for the PATCH engine.
"""

import pytest

from markdown_vault.core.patch_engine import (
    InvalidTargetError,
    PatchEngine,
    TargetNotFoundError,
)


@pytest.fixture
def engine() -> PatchEngine:
    """Create a PatchEngine instance."""
    return PatchEngine()


@pytest.fixture
def sample_content() -> str:
    """Sample markdown content with headings and blocks."""
    return """---
title: Test Document
tags:
  - test
  - sample
---

# Main Heading

Introduction paragraph.

## Section 1

Content in section 1. ^block-1

### Subsection 1.1

Nested content here.

### Subsection 1.2

More nested content.

## Section 2

Content in section 2. ^block-2

## Section 1

Duplicate heading content. ^block-3

# Another Top Level

Final section.
"""


class TestHeadingHierarchy:
    """Test heading hierarchy parsing and targeting."""

    def test_parse_simple_heading(self, engine: PatchEngine) -> None:
        """Test parsing a simple heading structure."""
        content = "# Heading 1\n\nContent\n\n## Heading 2\n\nMore content"
        tree = engine._parse_heading_hierarchy(content)

        assert len(tree) == 1
        assert tree[0].text == "Heading 1"
        assert tree[0].level == 1
        assert len(tree[0].children) == 1
        assert tree[0].children[0].text == "Heading 2"
        assert tree[0].children[0].level == 2

    def test_parse_multiple_top_level(self, engine: PatchEngine) -> None:
        """Test parsing multiple top-level headings."""
        content = "# Heading 1\n\nContent\n\n# Heading 2\n\nMore content"
        tree = engine._parse_heading_hierarchy(content)

        assert len(tree) == 2
        assert tree[0].text == "Heading 1"
        assert tree[1].text == "Heading 2"

    def test_parse_nested_hierarchy(self, engine: PatchEngine) -> None:
        """Test parsing deeply nested headings."""
        content = """# Level 1
## Level 2
### Level 3
#### Level 4
Content"""
        tree = engine._parse_heading_hierarchy(content)

        assert len(tree) == 1
        assert tree[0].level == 1
        assert len(tree[0].children) == 1
        assert tree[0].children[0].level == 2
        assert len(tree[0].children[0].children) == 1
        assert tree[0].children[0].children[0].level == 3

    def test_find_heading_simple(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test finding a simple heading."""
        position = engine._find_heading_target(sample_content, "Main Heading")

        assert position is not None
        assert position.start_line > 0  # After heading line

    def test_find_heading_nested(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test finding a nested heading using :: syntax."""
        position = engine._find_heading_target(
            sample_content, "Main Heading::Section 1"
        )

        assert position is not None
        assert position.start_line > 0

    def test_find_heading_deeply_nested(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test finding a deeply nested heading."""
        position = engine._find_heading_target(
            sample_content, "Main Heading::Section 1::Subsection 1.1"
        )

        assert position is not None

    def test_find_heading_with_index(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test finding duplicate heading using :N index."""
        # First occurrence (index 1)
        position1 = engine._find_heading_target(
            sample_content, "Main Heading::Section 1:1"
        )
        assert position1 is not None

        # Second occurrence (index 2)
        position2 = engine._find_heading_target(
            sample_content, "Main Heading::Section 1:2"
        )
        assert position2 is not None

        # Positions should be different
        assert position1.start_line != position2.start_line

    def test_find_heading_not_found(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test that None is returned for non-existent heading."""
        position = engine._find_heading_target(sample_content, "Nonexistent")

        assert position is None

    def test_find_heading_invalid_index(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test that invalid index raises error."""
        with pytest.raises(InvalidTargetError):
            engine._find_heading_target(sample_content, "Main Heading::Section 1:0")


class TestBlockReferences:
    """Test block reference targeting."""

    def test_find_block_simple(self, engine: PatchEngine, sample_content: str) -> None:
        """Test finding a simple block reference."""
        position = engine._find_block_target(sample_content, "block-1")

        assert position is not None
        assert position.start_line == position.end_line  # Same line

    def test_find_block_not_found(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test that missing block raises error."""
        with pytest.raises(TargetNotFoundError):
            engine._find_block_target(sample_content, "nonexistent")

    def test_block_position_excludes_reference(self, engine: PatchEngine) -> None:
        """Test that block position excludes the ^blockid itself."""
        content = "This is content. ^myblock"
        position = engine._find_block_target(content, "myblock")

        # Should point to content before the block reference
        assert position.end_col == content.index(" ^myblock")


class TestFrontmatterUpdates:
    """Test frontmatter field updates."""

    def test_update_frontmatter_replace_string(self, engine: PatchEngine) -> None:
        """Test replacing a string field in frontmatter."""
        content = """---
title: Old Title
tags: [test]
---

Content here."""

        result = engine._update_frontmatter(content, "title", "New Title", "replace")

        assert "title: New Title" in result or "title: 'New Title'" in result
        assert "Old Title" not in result

    def test_update_frontmatter_replace_list(self, engine: PatchEngine) -> None:
        """Test replacing a list field."""
        content = """---
title: Test
tags:
  - old
---

Content."""

        result = engine._update_frontmatter(
            content, "tags", ["new1", "new2"], "replace"
        )

        assert "new1" in result
        assert "new2" in result
        assert "old" not in result

    def test_update_frontmatter_append_to_list(self, engine: PatchEngine) -> None:
        """Test appending to a list field."""
        content = """---
title: Test
tags:
  - existing
---

Content."""

        result = engine._update_frontmatter(content, "tags", "new-tag", "append")

        assert "existing" in result
        assert "new-tag" in result

    def test_update_frontmatter_append_list_to_list(self, engine: PatchEngine) -> None:
        """Test appending a list to a list field."""
        content = """---
tags:
  - tag1
---

Content."""

        result = engine._update_frontmatter(content, "tags", ["tag2", "tag3"], "append")

        assert "tag1" in result
        assert "tag2" in result
        assert "tag3" in result

    def test_update_frontmatter_create_new_field(self, engine: PatchEngine) -> None:
        """Test creating a new frontmatter field."""
        content = """---
title: Test
---

Content."""

        result = engine._update_frontmatter(content, "status", "draft", "replace")

        assert "status: draft" in result or "status: 'draft'" in result

    def test_update_frontmatter_no_existing(self, engine: PatchEngine) -> None:
        """Test updating content without existing frontmatter."""
        content = "# Just Content\n\nNo frontmatter here."

        result = engine._update_frontmatter(content, "title", "New Title", "replace")

        # Should create frontmatter
        assert "---" in result
        assert "title:" in result

    def test_update_frontmatter_prepend_not_allowed(self, engine: PatchEngine) -> None:
        """Test that prepend operation is not allowed for frontmatter."""
        content = """---
title: Test
---

Content."""

        with pytest.raises(InvalidTargetError, match="prepend.*not supported"):
            engine._update_frontmatter(content, "title", "value", "prepend")

    def test_update_frontmatter_append_to_non_list(self, engine: PatchEngine) -> None:
        """Test that appending to non-list field raises error."""
        content = """---
title: Test
---

Content."""

        with pytest.raises(InvalidTargetError, match="non-list"):
            engine._update_frontmatter(content, "title", "value", "append")

    def test_update_frontmatter_json_value(self, engine: PatchEngine) -> None:
        """Test updating frontmatter with JSON value."""
        content = """---
title: Test
---

Content."""

        # Pass JSON string that should be parsed
        result = engine._update_frontmatter(
            content, "metadata", '{"key": "value"}', "replace"
        )

        # Should parse the JSON
        assert "metadata:" in result
        assert "key:" in result or "'key':" in result


class TestPatchOperations:
    """Test full patch operations."""

    def test_append_to_heading(self, engine: PatchEngine, sample_content: str) -> None:
        """Test appending content to a heading section."""
        result = engine.apply_patch(
            content=sample_content,
            operation="append",
            target_type="heading",
            target="Main Heading::Section 1",
            new_content="\nNew appended content.",
        )

        assert "New appended content." in result
        # Original content should still be there
        assert "Content in section 1." in result

    def test_prepend_to_heading(self, engine: PatchEngine, sample_content: str) -> None:
        """Test prepending content to a heading section."""
        result = engine.apply_patch(
            content=sample_content,
            operation="prepend",
            target_type="heading",
            target="Main Heading::Section 2",
            new_content="Prepended content.\n",
        )

        assert "Prepended content." in result
        # Check order: prepended content should come before original
        prepend_pos = result.index("Prepended content.")
        original_pos = result.index("Content in section 2.")
        assert prepend_pos < original_pos

    def test_replace_heading_content(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test replacing entire heading section content."""
        result = engine.apply_patch(
            content=sample_content,
            operation="replace",
            target_type="heading",
            target="Main Heading::Section 2",
            new_content="Completely new content for section 2.",
        )

        assert "Completely new content for section 2." in result
        # Original content should be gone
        assert "Content in section 2." not in result
        # Block reference should be gone too
        assert "^block-2" not in result

    def test_append_to_block(self, engine: PatchEngine, sample_content: str) -> None:
        """Test appending to a block reference."""
        result = engine.apply_patch(
            content=sample_content,
            operation="append",
            target_type="block",
            target="block-1",
            new_content="Extra text.",
        )

        # Should append before the block reference
        assert "Extra text." in result
        assert "^block-1" in result  # Block ref should still be there

        # Find the line with block-1
        lines = result.split("\n")
        block_line = [line for line in lines if "^block-1" in line][0]
        assert "Extra text." in block_line

    def test_replace_block(self, engine: PatchEngine, sample_content: str) -> None:
        """Test replacing a block."""
        result = engine.apply_patch(
            content=sample_content,
            operation="replace",
            target_type="block",
            target="block-2",
            new_content="Replaced block content.",
        )

        assert "Replaced block content." in result
        # Original content should be gone
        assert "Content in section 2." not in result

    def test_update_frontmatter_via_patch(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test updating frontmatter via patch operation."""
        result = engine.apply_patch(
            content=sample_content,
            operation="replace",
            target_type="frontmatter",
            target="title",
            new_content="Updated Title",
        )

        assert "title: Updated Title" in result or "title: 'Updated Title'" in result

    def test_create_heading_if_missing(self, engine: PatchEngine) -> None:
        """Test creating a new heading when it doesn't exist."""
        content = "# Existing\n\nContent."

        result = engine.apply_patch(
            content=content,
            operation="append",
            target_type="heading",
            target="New Section",
            new_content="New content here.",
            create_if_missing=True,
        )

        assert "# New Section" in result
        assert "New content here." in result

    def test_create_nested_heading_if_missing(self, engine: PatchEngine) -> None:
        """Test creating nested heading structure."""
        content = "# Existing\n\nContent."

        result = engine.apply_patch(
            content=content,
            operation="append",
            target_type="heading",
            target="New Section::Subsection",
            new_content="Nested content.",
            create_if_missing=True,
        )

        assert "# New Section" in result
        assert "## Subsection" in result
        assert "Nested content." in result

    def test_error_on_missing_heading_without_create(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test that missing heading raises error when create_if_missing=False."""
        with pytest.raises(TargetNotFoundError):
            engine.apply_patch(
                content=sample_content,
                operation="append",
                target_type="heading",
                target="Nonexistent Section",
                new_content="Content.",
                create_if_missing=False,
            )

    def test_invalid_operation(self, engine: PatchEngine, sample_content: str) -> None:
        """Test that invalid operation raises error."""
        with pytest.raises(InvalidTargetError, match="Invalid operation"):
            engine.apply_patch(
                content=sample_content,
                operation="invalid_op",
                target_type="heading",
                target="Main Heading",
                new_content="Content.",
            )

    def test_invalid_target_type(
        self, engine: PatchEngine, sample_content: str
    ) -> None:
        """Test that invalid target type raises error."""
        with pytest.raises(InvalidTargetError, match="Invalid target type"):
            engine.apply_patch(
                content=sample_content,
                operation="append",
                target_type="invalid_type",
                target="something",
                new_content="Content.",
            )


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_content(self, engine: PatchEngine) -> None:
        """Test patching empty content."""
        result = engine.apply_patch(
            content="",
            operation="append",
            target_type="heading",
            target="New Heading",
            new_content="Content.",
            create_if_missing=True,
        )

        assert "# New Heading" in result
        assert "Content." in result

    def test_content_without_frontmatter(self, engine: PatchEngine) -> None:
        """Test patching content without frontmatter."""
        content = "# Heading\n\nContent."

        result = engine.apply_patch(
            content=content,
            operation="append",
            target_type="heading",
            target="Heading",
            new_content="\nMore content.",
        )

        assert "More content." in result

    def test_heading_with_special_characters(self, engine: PatchEngine) -> None:
        """Test heading with special characters."""
        content = "# Heading: With Colon!\n\nContent."

        position = engine._find_heading_target(content, "Heading: With Colon!")

        assert position is not None

    def test_multiple_block_refs_same_line(self, engine: PatchEngine) -> None:
        """Test that only the last block ref on a line is recognized."""
        # Obsidian only recognizes the last ^blockid on a line
        content = "Text ^first and more ^second"

        # Should find 'second' (the last one)
        position = engine._find_block_target(content, "second")
        assert position is not None

        # Should not find 'first' (not at end of line)
        with pytest.raises(TargetNotFoundError):
            engine._find_block_target(content, "first")

    def test_heading_with_attributes(self, engine: PatchEngine) -> None:
        """Test heading with attributes like {#id}."""
        content = "# Heading {#my-id}\n\nContent."

        position = engine._find_heading_target(content, "Heading")

        assert position is not None

    def test_preserve_trailing_newlines(self, engine: PatchEngine) -> None:
        """Test that operations preserve document structure."""
        content = "# Heading\n\nContent.\n\n## Section\n\nMore.\n"

        result = engine.apply_patch(
            content=content,
            operation="append",
            target_type="heading",
            target="Section",
            new_content="\nAppended.\n",
        )

        # Should maintain structure
        assert "## Section" in result
        assert "Appended." in result
