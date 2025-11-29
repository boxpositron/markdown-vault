"""
Tests for search API routes.
"""

from fastapi.testclient import TestClient


def test_simple_search_success(test_app: TestClient, api_headers: dict) -> None:
    """Test simple search returns results."""
    # Create a test file first
    test_app.put(
        "/vault/search-test.md",
        content="# Test Note\n\nThis is a searchable note with unique content.",
        headers=api_headers,
    )

    # Search for unique content
    response = test_app.post(
        "/search/simple/",
        json={"query": "searchable"},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert isinstance(data["results"], list)
    assert data["total"] >= 0


def test_simple_search_empty_query(test_app: TestClient, api_headers: dict) -> None:
    """Test simple search with empty query returns error."""
    response = test_app.post(
        "/search/simple/",
        json={"query": ""},
        headers=api_headers,
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_simple_search_whitespace_query(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test simple search with whitespace query returns error."""
    response = test_app.post(
        "/search/simple/",
        json={"query": "   "},
        headers=api_headers,
    )

    assert response.status_code == 400


def test_simple_search_no_matches(test_app: TestClient, api_headers: dict) -> None:
    """Test simple search with no matches returns empty results."""
    response = test_app.post(
        "/search/simple/",
        json={"query": "veryuniquestring12345xyz"},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["results"]) == 0


def test_simple_search_with_max_results(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test simple search respects max_results parameter."""
    # Create multiple test files
    for i in range(5):
        test_app.put(
            f"/vault/test-{i}.md",
            content=f"# Test {i}\n\nCommon search term here.",
            headers=api_headers,
        )

    # Search with limit
    response = test_app.post(
        "/search/simple/",
        json={"query": "common search term", "max_results": 2},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 2


def test_simple_search_case_insensitive(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test simple search is case-insensitive."""
    # Create test file
    test_app.put(
        "/vault/case-test.md",
        content="# Case Test\n\nMixed CaSe CoNtEnT here.",
        headers=api_headers,
    )

    # Search with different cases
    response_lower = test_app.post(
        "/search/simple/",
        json={"query": "mixed case content"},
        headers=api_headers,
    )

    response_upper = test_app.post(
        "/search/simple/",
        json={"query": "MIXED CASE CONTENT"},
        headers=api_headers,
    )

    assert response_lower.status_code == 200
    assert response_upper.status_code == 200

    # Both should find the file
    data_lower = response_lower.json()
    data_upper = response_upper.json()
    assert data_lower["total"] == data_upper["total"]


def test_simple_search_frontmatter(test_app: TestClient, api_headers: dict) -> None:
    """Test simple search finds matches in frontmatter."""
    # Create file with frontmatter
    content = """---
title: Frontmatter Test
author: Unique Author Name
tags: [search, test]
---

# Frontmatter Test

Content here.
"""
    test_app.put("/vault/frontmatter-search.md", content=content, headers=api_headers)

    # Search for frontmatter content
    response = test_app.post(
        "/search/simple/",
        json={"query": "Unique Author Name"},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0

    # Check that our file is in results
    paths = [r["path"] for r in data["results"]]
    assert any("frontmatter-search.md" in path for path in paths)


def test_simple_search_unauthorized(test_app: TestClient) -> None:
    """Test simple search requires authentication."""
    response = test_app.post(
        "/search/simple/",
        json={"query": "test"},
    )

    assert response.status_code == 401


def test_jsonlogic_search_success(test_app: TestClient, api_headers: dict) -> None:
    """Test JSONLogic search returns results."""
    # Create test file with frontmatter
    content = """---
status: published
category: tutorial
---

# Published Tutorial

Content here.
"""
    test_app.put("/vault/jsonlogic-test.md", content=content, headers=api_headers)

    # Search by frontmatter field
    response = test_app.post(
        "/search/",
        json={"query": {"status": "published"}},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data


def test_jsonlogic_search_empty_query(test_app: TestClient, api_headers: dict) -> None:
    """Test JSONLogic search with empty query returns error."""
    response = test_app.post(
        "/search/",
        json={"query": {}},
        headers=api_headers,
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_jsonlogic_search_field_equality(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test JSONLogic search with field equality."""
    # Create test file
    content = """---
status: draft
author: Test User
priority: high
---

# Draft Note

Content.
"""
    test_app.put("/vault/draft-note.md", content=content, headers=api_headers)

    # Search for draft status
    response = test_app.post(
        "/search/",
        json={"query": {"status": "draft"}},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0


def test_jsonlogic_search_regex(test_app: TestClient, api_headers: dict) -> None:
    """Test JSONLogic search with regex matching."""
    # Create test file
    content = """---
author: John Smith
email: john@example.com
---

# User Note

Content.
"""
    test_app.put("/vault/user-note.md", content=content, headers=api_headers)

    # Search with regex
    response = test_app.post(
        "/search/",
        json={"query": {"author": {"$regex": "John.*"}}},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0


def test_jsonlogic_search_multiple_fields(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test JSONLogic search with multiple fields (AND logic)."""
    # Create test file
    content = """---
status: published
category: tutorial
difficulty: beginner
---

# Beginner Tutorial

Content.
"""
    test_app.put("/vault/tutorial.md", content=content, headers=api_headers)

    # Search with multiple conditions
    response = test_app.post(
        "/search/",
        json={"query": {"status": "published", "category": "tutorial"}},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0

    # Verify the file is in results
    paths = [r["path"] for r in data["results"]]
    assert any("tutorial.md" in path for path in paths)


def test_jsonlogic_search_no_match(test_app: TestClient, api_headers: dict) -> None:
    """Test JSONLogic search with no matching files."""
    response = test_app.post(
        "/search/",
        json={"query": {"nonexistent_field": "nonexistent_value"}},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


def test_jsonlogic_search_with_max_results(
    test_app: TestClient, api_headers: dict
) -> None:
    """Test JSONLogic search respects max_results parameter."""
    # Create multiple test files
    for i in range(5):
        content = f"""---
type: test
number: {i}
---

# Test {i}
"""
        test_app.put(f"/vault/json-test-{i}.md", content=content, headers=api_headers)

    # Search with limit
    response = test_app.post(
        "/search/",
        json={"query": {"type": "test"}, "max_results": 2},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) <= 2


def test_jsonlogic_search_unauthorized(test_app: TestClient) -> None:
    """Test JSONLogic search requires authentication."""
    response = test_app.post(
        "/search/",
        json={"query": {"status": "draft"}},
    )

    assert response.status_code == 401


def test_search_result_format(test_app: TestClient, api_headers: dict) -> None:
    """Test search results have correct format."""
    # Create test file
    test_app.put(
        "/vault/format-test.md",
        content="# Format Test\n\nTest content.",
        headers=api_headers,
    )

    # Search
    response = test_app.post(
        "/search/simple/",
        json={"query": "format test"},
        headers=api_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify structure
    assert "results" in data
    assert "total" in data
    assert isinstance(data["results"], list)
    assert isinstance(data["total"], int)

    # If we have results, verify result structure
    if data["results"]:
        result = data["results"][0]
        assert "path" in result
        assert "matches" in result
        assert isinstance(result["path"], str)
        assert isinstance(result["matches"], int)
        assert result["matches"] > 0
