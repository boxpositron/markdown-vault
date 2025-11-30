"""
Search engine for markdown vault.

Provides full-text search across markdown files with support for:
- Simple text search (case-insensitive)
- Content and frontmatter searching
- JSONLogic filtering (basic implementation)
"""

import logging
import re
from typing import Any

from markdown_vault.core.vault import VaultManager
from markdown_vault.models.api import SearchResult

logger = logging.getLogger(__name__)


class SearchError(Exception):
    """Base exception for search operations."""

    pass


class SearchEngine:
    """
    Search engine for markdown files.

    Provides simple text search and basic JSONLogic filtering.
    """

    def __init__(self) -> None:
        """Initialize search engine."""
        logger.info("Initialized SearchEngine")

    async def simple_search(
        self,
        query: str,
        vault_manager: VaultManager,
        max_results: int | None = None,
    ) -> list[SearchResult]:
        """
        Perform simple full-text search across all files.

        Searches in both file content and frontmatter fields.
        Search is case-insensitive.

        Args:
            query: Search query string
            vault_manager: VaultManager instance
            max_results: Maximum number of results to return (None for unlimited)

        Returns:
            List of SearchResult objects sorted by match count (descending)

        Raises:
            SearchError: If search fails
        """
        if not query or not query.strip():
            return []

        query_lower = query.lower()
        results: list[SearchResult] = []

        try:
            # Get all markdown files
            files = await vault_manager.list_files()
            logger.debug(f"Searching {len(files)} files for query: {query}")

            # Search each file
            for filepath in files:
                try:
                    # Read file
                    note = await vault_manager.read_file(filepath)

                    # Count matches in content (case-insensitive)
                    content_lower = note.content.lower()
                    content_matches = content_lower.count(query_lower)

                    # Count matches in frontmatter
                    frontmatter_matches = 0
                    if note.frontmatter:
                        frontmatter_str = str(note.frontmatter).lower()
                        frontmatter_matches = frontmatter_str.count(query_lower)

                    # Total matches
                    total_matches = content_matches + frontmatter_matches

                    # Add to results if we have matches
                    if total_matches > 0:
                        results.append(
                            SearchResult(
                                path=filepath,
                                matches=total_matches,
                            )
                        )

                except Exception as e:
                    # Log error but continue searching other files
                    logger.warning(f"Error searching file {filepath}: {e}")
                    continue

            # Sort by match count (descending)
            results.sort(key=lambda r: r.matches, reverse=True)

            # Apply max_results limit if specified
            if max_results is not None and max_results > 0:
                results = results[:max_results]

            logger.info(f"Search complete: {len(results)} results for query '{query}'")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise SearchError(f"Search failed: {e}") from e

    async def jsonlogic_search(
        self,
        query: dict[str, Any],
        vault_manager: VaultManager,
        max_results: int | None = None,
    ) -> list[SearchResult]:
        """
        Perform JSONLogic search filtering by frontmatter fields.

        This is a basic implementation that supports simple field filtering.
        For example:
        - {"field": "value"} - matches files where frontmatter.field == value
        - {"field": {"$regex": "pattern"}} - matches files where field matches regex

        Args:
            query: JSONLogic query dictionary
            vault_manager: VaultManager instance
            max_results: Maximum number of results to return (None for unlimited)

        Returns:
            List of SearchResult objects

        Raises:
            SearchError: If search fails
        """
        if not query:
            return []

        results: list[SearchResult] = []

        try:
            # Get all markdown files
            files = await vault_manager.list_files()
            logger.debug(f"JSONLogic search on {len(files)} files: {query}")

            # Search each file
            for filepath in files:
                try:
                    # Read file
                    note = await vault_manager.read_file(filepath)

                    # Check if frontmatter matches query
                    if self._matches_query(note.frontmatter, query):
                        results.append(
                            SearchResult(
                                path=filepath,
                                matches=1,  # JSONLogic is binary (match or not)
                            )
                        )

                except Exception as e:
                    # Log error but continue searching other files
                    logger.warning(f"Error searching file {filepath}: {e}")
                    continue

            # Apply max_results limit if specified
            if max_results is not None and max_results > 0:
                results = results[:max_results]

            logger.info(f"JSONLogic search complete: {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"JSONLogic search failed: {e}")
            raise SearchError(f"JSONLogic search failed: {e}") from e

    def _matches_query(
        self, frontmatter: dict[str, Any], query: dict[str, Any]
    ) -> bool:
        """
        Check if frontmatter matches a JSONLogic query.

        Basic implementation supporting:
        - Direct field equality: {"field": "value"}
        - Regex matching: {"field": {"$regex": "pattern"}}
        - Multiple fields (AND logic)

        Args:
            frontmatter: Frontmatter dictionary
            query: Query dictionary

        Returns:
            True if frontmatter matches query, False otherwise
        """
        if not frontmatter:
            return False

        # Check each field in query
        for field, expected in query.items():
            # Get field value from frontmatter
            value = frontmatter.get(field)

            # Handle different query types
            if isinstance(expected, dict):
                # Special operators
                if "$regex" in expected:
                    # Regex matching
                    pattern = expected["$regex"]
                    if value is None:
                        return False
                    try:
                        if not re.search(pattern, str(value), re.IGNORECASE):
                            return False
                    except re.error:
                        logger.warning(f"Invalid regex pattern: {pattern}")
                        return False
                # Unknown operator, treat as equality
                elif value != expected:
                    return False
            # Direct equality
            elif value != expected:
                return False

        # All fields matched
        return True


__all__ = ["SearchEngine", "SearchError"]
