"""
Tests for PATCH endpoint in vault routes.
"""

from fastapi.testclient import TestClient


def test_patch_append_to_heading(test_app: TestClient, api_headers: dict) -> None:
    """Test PATCH endpoint with append to heading."""
    # Create a test file
    content = """# Main Heading

Some content.

## Section 1

Section content.
"""
    test_app.put(
        "/vault/test-patch.md",
        content=content,
        headers=api_headers,
    )

    # Patch: append to Section 1
    response = test_app.patch(
        "/vault/test-patch.md",
        content="\nAppended content.",
        headers={
            **api_headers,
            "Operation": "append",
            "Target-Type": "heading",
            "Target": "Main Heading::Section 1",
        },
    )

    assert response.status_code == 204

    # Verify the change
    get_response = test_app.get("/vault/test-patch.md", headers=api_headers)
    assert get_response.status_code == 200
    assert "Appended content." in get_response.text
    assert "Section content." in get_response.text


def test_patch_prepend_to_heading(test_app: TestClient, api_headers: dict) -> None:
    """Test PATCH endpoint with prepend to heading."""
    content = """# Main

## Section

Original content.
"""
    test_app.put(
        "/vault/test-patch2.md",
        content=content,
        headers=api_headers,
    )

    # Patch: prepend to Section
    response = test_app.patch(
        "/vault/test-patch2.md",
        content="Prepended content.\n",
        headers={
            **api_headers,
            "Operation": "prepend",
            "Target-Type": "heading",
            "Target": "Section",
        },
    )

    assert response.status_code == 204

    # Verify the order
    get_response = test_app.get("/vault/test-patch2.md", headers=api_headers)
    assert get_response.status_code == 200
    text = get_response.text
    prepend_pos = text.index("Prepended content.")
    original_pos = text.index("Original content.")
    assert prepend_pos < original_pos


def test_patch_replace_heading(test_app: TestClient, api_headers: dict) -> None:
    """Test PATCH endpoint with replace heading content."""
    content = """# Document

## Old Section

This should be replaced.
"""
    test_app.put(
        "/vault/test-patch3.md",
        content=content,
        headers=api_headers,
    )

    # Patch: replace section content
    response = test_app.patch(
        "/vault/test-patch3.md",
        content="Brand new content.",
        headers={
            **api_headers,
            "Operation": "replace",
            "Target-Type": "heading",
            "Target": "Old Section",
        },
    )

    assert response.status_code == 204

    # Verify replacement
    get_response = test_app.get("/vault/test-patch3.md", headers=api_headers)
    assert get_response.status_code == 200
    assert "Brand new content." in get_response.text
    assert "This should be replaced." not in get_response.text


def test_patch_block_reference(test_app: TestClient, api_headers: dict) -> None:
    """Test PATCH endpoint with block reference targeting."""
    content = """# Document

This is a line with a block ref. ^myblock

More content.
"""
    test_app.put(
        "/vault/test-patch4.md",
        content=content,
        headers=api_headers,
    )

    # Patch: append to block
    response = test_app.patch(
        "/vault/test-patch4.md",
        content="Extra text.",
        headers={
            **api_headers,
            "Operation": "append",
            "Target-Type": "block",
            "Target": "myblock",
        },
    )

    assert response.status_code == 204

    # Verify
    get_response = test_app.get("/vault/test-patch4.md", headers=api_headers)
    assert get_response.status_code == 200
    assert "Extra text." in get_response.text
    assert "^myblock" in get_response.text  # Block ref should still be there


def test_patch_frontmatter(test_app: TestClient, api_headers: dict) -> None:
    """Test PATCH endpoint with frontmatter update."""
    content = """---
title: Old Title
tags:
  - test
---

# Content

Body text.
"""
    test_app.put(
        "/vault/test-patch5.md",
        content=content,
        headers=api_headers,
    )

    # Patch: update frontmatter title
    response = test_app.patch(
        "/vault/test-patch5.md",
        content="New Title",
        headers={
            **api_headers,
            "Operation": "replace",
            "Target-Type": "frontmatter",
            "Target": "title",
        },
    )

    assert response.status_code == 204

    # Verify - use JSON format to check frontmatter
    get_response = test_app.get(
        "/vault/test-patch5.md",
        headers={
            **api_headers,
            "Accept": "application/vnd.olrapi.note+json",
        },
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["frontmatter"]["title"] == "New Title"


def test_patch_frontmatter_append_to_list(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test PATCH endpoint with frontmatter list append."""
    content = """---
title: Test
tags:
  - existing
---

# Content
"""
    test_app.put(
        "/vault/test-patch6.md",
        content=content,
        headers=api_headers,
    )

    # Patch: append to tags list
    response = test_app.patch(
        "/vault/test-patch6.md",
        content="new-tag",
        headers={
            **api_headers,
            "Operation": "append",
            "Target-Type": "frontmatter",
            "Target": "tags",
        },
    )

    assert response.status_code == 204

    # Verify
    get_response = test_app.get(
        "/vault/test-patch6.md",
        headers={
            **api_headers,
            "Accept": "application/vnd.olrapi.note+json",
        },
    )
    assert get_response.status_code == 200
    data = get_response.json()
    assert "existing" in data["frontmatter"]["tags"]
    assert "new-tag" in data["frontmatter"]["tags"]


def test_patch_create_heading_if_missing(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test PATCH endpoint with create-if-missing header."""
    content = """# Existing

Content.
"""
    test_app.put(
        "/vault/test-patch7.md",
        content=content,
        headers=api_headers,
    )

    # Patch: create new heading
    response = test_app.patch(
        "/vault/test-patch7.md",
        content="New section content.",
        headers={
            **api_headers,
            "Operation": "append",
            "Target-Type": "heading",
            "Target": "New Section",
            "Create-Target-If-Missing": "true",
        },
    )

    assert response.status_code == 204

    # Verify
    get_response = test_app.get("/vault/test-patch7.md", headers=api_headers)
    assert get_response.status_code == 200
    assert "# New Section" in get_response.text
    assert "New section content." in get_response.text


def test_patch_target_not_found(test_app: TestClient, api_headers: dict) -> None:
    """Test PATCH endpoint returns 404 when target not found."""
    content = """# Document

Content.
"""
    test_app.put(
        "/vault/test-patch8.md",
        content=content,
        headers=api_headers,
    )

    # Patch: target heading that doesn't exist
    response = test_app.patch(
        "/vault/test-patch8.md",
        content="Content.",
        headers={
            **api_headers,
            "Operation": "append",
            "Target-Type": "heading",
            "Target": "Nonexistent Section",
        },
    )

    assert response.status_code == 404


def test_patch_invalid_operation(test_app: TestClient, api_headers: dict) -> None:
    """Test PATCH endpoint returns 400 for invalid operation."""
    content = """# Document

Content.
"""
    test_app.put(
        "/vault/test-patch9.md",
        content=content,
        headers=api_headers,
    )

    # Patch: invalid operation
    response = test_app.patch(
        "/vault/test-patch9.md",
        content="Content.",
        headers={
            **api_headers,
            "Operation": "invalid_op",
            "Target-Type": "heading",
            "Target": "Document",
        },
    )

    assert response.status_code == 400


def test_patch_file_not_found(test_app: TestClient, api_headers: dict) -> None:
    """Test PATCH endpoint returns 404 for non-existent file."""
    response = test_app.patch(
        "/vault/nonexistent.md",
        content="Content.",
        headers={
            **api_headers,
            "Operation": "append",
            "Target-Type": "heading",
            "Target": "Section",
        },
    )

    assert response.status_code == 404


def test_patch_with_indexed_duplicate_heading(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test PATCH with indexed duplicate headings."""
    content = """# Main

## Section

First section content.

## Section

Second section content.
"""
    test_app.put(
        "/vault/test-patch10.md",
        content=content,
        headers=api_headers,
    )

    # Patch: target second occurrence of "Section"
    response = test_app.patch(
        "/vault/test-patch10.md",
        content="\nAppended to second section.",
        headers={
            **api_headers,
            "Operation": "append",
            "Target-Type": "heading",
            "Target": "Section:2",
        },
    )

    assert response.status_code == 204

    # Verify
    get_response = test_app.get("/vault/test-patch10.md", headers=api_headers)
    assert get_response.status_code == 200
    text = get_response.text

    # Find both sections
    second_section_idx = text.index("Second section content.")
    appended_idx = text.index("Appended to second section.")

    # Appended content should be after the second section
    assert appended_idx > second_section_idx
