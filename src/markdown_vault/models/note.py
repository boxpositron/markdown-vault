"""
Pydantic models for notes and note metadata.

These models match the Obsidian Local REST API response format for
full compatibility.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class NoteStat(BaseModel):
    """File statistics for a note."""

    ctime: int = Field(..., description="Creation time in milliseconds since epoch")
    mtime: int = Field(
        ..., description="Modification time in milliseconds since epoch"
    )
    size: int = Field(..., description="File size in bytes")


class NoteJson(BaseModel):
    """
    JSON representation of a note with metadata.
    
    This matches the response format when using:
    Accept: application/vnd.olrapi.note+json
    """

    path: str = Field(..., description="Path to the note relative to vault root")
    content: str = Field(..., description="Raw markdown content of the note")
    frontmatter: Dict[str, Any] = Field(
        default_factory=dict, description="Parsed YAML frontmatter"
    )
    tags: List[str] = Field(
        default_factory=list, description="List of tags (both frontmatter and inline)"
    )
    stat: NoteStat = Field(..., description="File statistics")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "path": "notes/example.md",
                "content": "# Example Note\n\nThis is the content.",
                "frontmatter": {"tags": ["example"], "created": "2025-01-01"},
                "tags": ["#inline-tag", "example"],
                "stat": {"ctime": 1234567890000, "mtime": 1234567891000, "size": 1024},
            }
        }


class Note(BaseModel):
    """
    Internal note representation.
    
    Used for processing notes before converting to API response format.
    """

    path: str = Field(..., description="Path to the note relative to vault root")
    content: str = Field(..., description="Raw markdown content")
    frontmatter: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)

    def to_json_format(self, stat: NoteStat) -> NoteJson:
        """Convert to JSON API response format."""
        return NoteJson(
            path=self.path,
            content=self.content,
            frontmatter=self.frontmatter,
            tags=self.tags,
            stat=stat,
        )
