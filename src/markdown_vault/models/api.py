"""
Pydantic models for API requests and responses.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field


class PatchOperation(str, Enum):
    """PATCH operation types."""

    APPEND = "append"
    PREPEND = "prepend"
    REPLACE = "replace"


class TargetType(str, Enum):
    """PATCH target types."""

    HEADING = "heading"
    BLOCK = "block"
    FRONTMATTER = "frontmatter"


class ServerStatus(BaseModel):
    """
    Server status response for GET /.

    This is the only endpoint that doesn't require authentication.
    """

    ok: str = Field(default="OK", description="Status indicator")
    service: str = Field(default="markdown-vault", description="Service name")
    authenticated: bool = Field(..., description="Whether the request is authenticated")
    versions: Dict[str, str] = Field(..., description="Version information")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ok": "OK",
                "service": "markdown-vault",
                "authenticated": False,
                "versions": {
                    "self": "0.1.0",
                    "api": "1.0",
                },
            }
        }
    )


class APIError(BaseModel):
    """
    Standard error response format.

    Matches Obsidian Local REST API error format with 5-digit error codes.
    """

    errorCode: int = Field(
        ..., description="5-digit error code uniquely identifying the error type"
    )
    message: str = Field(..., description="Human-readable error message")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "errorCode": 40401,
                "message": "File not found: notes/missing.md",
            }
        }
    )


class CommandInfo(BaseModel):
    """Information about an available command."""

    id: str = Field(..., description="Unique command identifier")
    name: str = Field(..., description="Human-readable command name")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "create-note",
                "name": "Create new note",
            }
        }
    )


class CommandList(BaseModel):
    """List of available commands."""

    commands: List[CommandInfo] = Field(
        default_factory=list, description="Available commands"
    )


class SearchQuery(BaseModel):
    """Search query request."""

    query: str = Field(..., description="Search query string")
    max_results: Optional[int] = Field(
        None, description="Maximum number of results to return"
    )


class SearchResult(BaseModel):
    """Search result item."""

    path: str = Field(..., description="Path to the matching file")
    matches: int = Field(default=0, description="Number of matches in file")


class SearchResults(BaseModel):
    """Search results response."""

    results: List[SearchResult] = Field(
        default_factory=list, description="Search results"
    )
    total: int = Field(..., description="Total number of results")
