"""
Tests for search engine functionality.
"""

import pytest

from markdown_vault.core.search_engine import SearchEngine
from markdown_vault.core.vault import VaultManager


@pytest.mark.asyncio
async def test_simple_search_empty_query(vault_manager: VaultManager) -> None:
    """Test simple search with empty query returns no results."""
    engine = SearchEngine()
    results = await engine.simple_search("", vault_manager)
    assert len(results) == 0

    results = await engine.simple_search("   ", vault_manager)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_simple_search_no_matches(vault_manager: VaultManager) -> None:
    """Test simple search with no matches."""
    engine = SearchEngine()
    results = await engine.simple_search("nonexistentstring12345", vault_manager)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_simple_search_content_match(vault_manager: VaultManager) -> None:
    """Test simple search finds matches in content."""
    engine = SearchEngine()

    # Search for "simple" which appears in simple.md
    results = await engine.simple_search("simple", vault_manager)
    assert len(results) > 0

    # Check that simple.md is in results
    paths = [r.path for r in results]
    assert any("simple.md" in path for path in paths)

    # Check match count is positive
    for result in results:
        assert result.matches > 0


@pytest.mark.asyncio
async def test_simple_search_frontmatter_match(vault_manager: VaultManager) -> None:
    """Test simple search finds matches in frontmatter."""
    engine = SearchEngine()

    # Search for "Test User" which appears in frontmatter
    results = await engine.simple_search("Test User", vault_manager)
    assert len(results) > 0

    # Check that with-frontmatter.md is in results
    paths = [r.path for r in results]
    assert any("with-frontmatter.md" in path for path in paths)


@pytest.mark.asyncio
async def test_simple_search_case_insensitive(vault_manager: VaultManager) -> None:
    """Test simple search is case-insensitive."""
    engine = SearchEngine()

    # Search with different cases
    results_lower = await engine.simple_search("simple", vault_manager)
    results_upper = await engine.simple_search("SIMPLE", vault_manager)
    results_mixed = await engine.simple_search("SiMpLe", vault_manager)

    # All should return same results
    assert len(results_lower) == len(results_upper)
    assert len(results_lower) == len(results_mixed)


@pytest.mark.asyncio
async def test_simple_search_sorting(vault_manager: VaultManager) -> None:
    """Test simple search results are sorted by match count."""
    engine = SearchEngine()

    # Search for common word that appears multiple times
    results = await engine.simple_search("content", vault_manager)

    if len(results) > 1:
        # Verify sorting (descending by match count)
        for i in range(len(results) - 1):
            assert results[i].matches >= results[i + 1].matches


@pytest.mark.asyncio
async def test_simple_search_max_results(vault_manager: VaultManager) -> None:
    """Test simple search respects max_results limit."""
    engine = SearchEngine()

    # Search for common word
    all_results = await engine.simple_search("note", vault_manager)

    if len(all_results) > 2:
        # Limit to 2 results
        limited_results = await engine.simple_search(
            "note", vault_manager, max_results=2
        )
        assert len(limited_results) == 2

        # Should return top 2 results by match count
        assert limited_results[0].matches >= limited_results[1].matches


@pytest.mark.asyncio
async def test_jsonlogic_search_empty_query(vault_manager: VaultManager) -> None:
    """Test JSONLogic search with empty query returns no results."""
    engine = SearchEngine()
    results = await engine.jsonlogic_search({}, vault_manager)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_jsonlogic_search_field_equality(vault_manager: VaultManager) -> None:
    """Test JSONLogic search with field equality."""
    engine = SearchEngine()

    # Search for files with status=draft
    results = await engine.jsonlogic_search({"status": "draft"}, vault_manager)
    assert len(results) > 0

    # Check that with-frontmatter.md is in results
    paths = [r.path for r in results]
    assert any("with-frontmatter.md" in path for path in paths)


@pytest.mark.asyncio
async def test_jsonlogic_search_no_match(vault_manager: VaultManager) -> None:
    """Test JSONLogic search with no matching files."""
    engine = SearchEngine()

    # Search for non-existent field value
    results = await engine.jsonlogic_search({"status": "nonexistent"}, vault_manager)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_jsonlogic_search_regex(vault_manager: VaultManager) -> None:
    """Test JSONLogic search with regex matching."""
    engine = SearchEngine()

    # Search for author matching regex pattern
    results = await engine.jsonlogic_search(
        {"author": {"$regex": "Test.*"}}, vault_manager
    )
    assert len(results) > 0

    # Check that with-frontmatter.md is in results
    paths = [r.path for r in results]
    assert any("with-frontmatter.md" in path for path in paths)


@pytest.mark.asyncio
async def test_jsonlogic_search_multiple_fields(vault_manager: VaultManager) -> None:
    """Test JSONLogic search with multiple fields (AND logic)."""
    engine = SearchEngine()

    # Search for files matching both conditions
    results = await engine.jsonlogic_search(
        {"status": "draft", "author": "Test User"}, vault_manager
    )
    assert len(results) > 0

    # Check that with-frontmatter.md is in results
    paths = [r.path for r in results]
    assert any("with-frontmatter.md" in path for path in paths)


@pytest.mark.asyncio
async def test_jsonlogic_search_multiple_fields_no_match(
    vault_manager: VaultManager,
) -> None:
    """Test JSONLogic search with multiple fields where one doesn't match."""
    engine = SearchEngine()

    # Search for files matching contradictory conditions
    results = await engine.jsonlogic_search(
        {"status": "draft", "author": "Wrong Author"}, vault_manager
    )
    assert len(results) == 0


@pytest.mark.asyncio
async def test_jsonlogic_search_max_results(vault_manager: VaultManager) -> None:
    """Test JSONLogic search respects max_results limit."""
    engine = SearchEngine()

    # This should match multiple files
    all_results = await engine.jsonlogic_search(
        {"created": "2025-01-01"}, vault_manager
    )

    if len(all_results) > 1:
        # Limit to 1 result
        limited_results = await engine.jsonlogic_search(
            {"created": "2025-01-01"}, vault_manager, max_results=1
        )
        assert len(limited_results) == 1


@pytest.mark.asyncio
async def test_search_with_nested_files(vault_manager: VaultManager) -> None:
    """Test search works with nested directory structure."""
    engine = SearchEngine()

    # Search for content that might be in nested files
    results = await engine.simple_search("note", vault_manager)

    # Should find files in subdirectories
    # Just verify search doesn't crash with nested files
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_search_invalid_regex(vault_manager: VaultManager) -> None:
    """Test JSONLogic search handles invalid regex gracefully."""
    engine = SearchEngine()

    # Search with invalid regex pattern
    results = await engine.jsonlogic_search(
        {"title": {"$regex": "[invalid(regex"}}, vault_manager
    )
    # Should return no results rather than crashing
    assert len(results) == 0
