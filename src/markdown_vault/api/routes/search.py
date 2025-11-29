"""
Search API routes for markdown vault.

This module provides search endpoints:
- POST /search/simple/ - Simple full-text search
- POST /search/ - JSONLogic search (basic filtering)
"""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from markdown_vault.api.deps import ApiKeyDep, ConfigDep, VaultPathDep
from markdown_vault.core.search_engine import SearchEngine, SearchError
from markdown_vault.core.vault import VaultManager
from markdown_vault.models.api import SearchQuery, SearchResults

logger = logging.getLogger(__name__)

router = APIRouter()


class JSONLogicQuery(BaseModel):
    """JSONLogic query request."""

    query: dict[str, Any] = Field(..., description="JSONLogic query object")
    max_results: int | None = Field(
        None, description="Maximum number of results to return"
    )


@router.post(
    "/search/simple/",
    response_model=SearchResults,
    summary="Simple text search",
    description=(
        "Perform full-text search across all markdown files. "
        "Searches in both file content and frontmatter. "
        "Case-insensitive."
    ),
    tags=["search"],
    responses={
        200: {"description": "Search results"},
        400: {"description": "Invalid query"},
        500: {"description": "Search error"},
    },
)
async def simple_search(
    query: SearchQuery,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
    config: ConfigDep,
) -> SearchResults:
    """
    Perform simple full-text search.

    Searches for the query string in file content and frontmatter.
    Results are sorted by match count (descending).

    Args:
        query: Search query request
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)
        config: Application configuration (from dependency)

    Returns:
        Search results with total count

    Raises:
        HTTPException: 400 if query is invalid
        HTTPException: 500 if search fails
    """
    # Validate query
    if not query.query or not query.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query string cannot be empty",
        )

    # Get max_results from query or config
    max_results = query.max_results or config.search.max_results

    try:
        # Initialize search engine and vault
        search_engine = SearchEngine()
        vault = VaultManager(vault_path)

        # Perform search
        results = await search_engine.simple_search(
            query=query.query,
            vault_manager=vault,
            max_results=max_results,
        )

        logger.info(f"Simple search for '{query.query}': {len(results)} results")

        return SearchResults(
            results=results,
            total=len(results),
        )

    except SearchError as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed",
        ) from e


@router.post(
    "/search/",
    response_model=SearchResults,
    summary="JSONLogic search",
    description=(
        "Filter files using JSONLogic query on frontmatter fields. "
        "Basic implementation supporting field equality and regex matching."
    ),
    tags=["search"],
    responses={
        200: {"description": "Search results"},
        400: {"description": "Invalid query"},
        500: {"description": "Search error"},
    },
)
async def jsonlogic_search(
    query: JSONLogicQuery,
    api_key: ApiKeyDep,
    vault_path: VaultPathDep,
    config: ConfigDep,
) -> SearchResults:
    """
    Perform JSONLogic search on frontmatter fields.

    Supports basic filtering:
    - Direct equality: {"field": "value"}
    - Regex matching: {"field": {"$regex": "pattern"}}
    - Multiple fields (AND logic)

    Args:
        query: JSONLogic query request
        api_key: Validated API key (from dependency)
        vault_path: Vault root path (from dependency)
        config: Application configuration (from dependency)

    Returns:
        Search results with total count

    Raises:
        HTTPException: 400 if query is invalid
        HTTPException: 500 if search fails
    """
    # Validate query
    if not query.query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query object cannot be empty",
        )

    # Get max_results from query or config
    max_results = query.max_results or config.search.max_results

    try:
        # Initialize search engine and vault
        search_engine = SearchEngine()
        vault = VaultManager(vault_path)

        # Perform search
        results = await search_engine.jsonlogic_search(
            query=query.query,
            vault_manager=vault,
            max_results=max_results,
        )

        logger.info(f"JSONLogic search: {len(results)} results")

        return SearchResults(
            results=results,
            total=len(results),
        )

    except SearchError as e:
        logger.error(f"JSONLogic search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error during JSONLogic search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed",
        ) from e


__all__ = ["router"]
