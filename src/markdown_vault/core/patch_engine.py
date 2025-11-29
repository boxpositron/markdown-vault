"""
PATCH engine for partial content updates in markdown files.

Supports:
- Heading-based targeting with hierarchy (Heading::Subheading:N)
- Block reference targeting (^blockid)
- Frontmatter field updates
- Operations: append, prepend, replace
"""

import re
from dataclasses import dataclass
from typing import Any

import frontmatter


class PatchError(Exception):
    """Base exception for patch operations."""

    pass


class TargetNotFoundError(PatchError):
    """Target heading or block reference not found."""

    pass


class InvalidTargetError(PatchError):
    """Invalid target specification."""

    pass


@dataclass
class HeadingNode:
    """
    Represents a heading in the markdown hierarchy.

    Attributes:
        text: The heading text (without # markers)
        level: Heading level (1-6)
        start_line: Line number where heading starts (0-based)
        end_line: Line number where heading content ends (0-based)
        children: Child headings under this heading
    """

    text: str
    level: int
    start_line: int
    end_line: int
    children: list["HeadingNode"]


@dataclass
class BlockPosition:
    """
    Position of a block or target in the content.

    Attributes:
        start_line: Line number where block starts (0-based)
        end_line: Line number where block ends (0-based, inclusive)
        start_col: Column where block starts (0-based)
        end_col: Column where block ends (0-based, exclusive)
    """

    start_line: int
    end_line: int
    start_col: int = 0
    end_col: int = -1  # -1 means end of line


class PatchEngine:
    """
    Engine for applying partial updates to markdown content.

    Handles targeting via headings, block references, and frontmatter,
    with support for append, prepend, and replace operations.
    """

    # Regex for markdown headings
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)(?:\s+\{[^}]*\})?\s*$")
    # Regex for block references at end of line
    BLOCK_PATTERN = re.compile(r"\^([a-zA-Z0-9-_]+)\s*$")

    def __init__(self) -> None:
        """Initialize the patch engine."""
        pass

    def apply_patch(
        self,
        content: str,
        operation: str,
        target_type: str,
        target: str,
        new_content: str,
        create_if_missing: bool = False,
    ) -> str:
        """
        Apply a patch operation to markdown content.

        Args:
            content: Original markdown content
            operation: One of 'append', 'prepend', 'replace'
            target_type: One of 'heading', 'block', 'frontmatter'
            target: Target specifier (depends on target_type)
            new_content: Content to insert/replace
            create_if_missing: Create target if it doesn't exist (headings only)

        Returns:
            Updated markdown content

        Raises:
            PatchError: If operation fails
            TargetNotFoundError: If target not found
            InvalidTargetError: If target specification is invalid
        """
        if target_type == "frontmatter":
            return self._update_frontmatter(content, target, new_content, operation)
        elif target_type == "block":
            position = self._find_block_target(content, target)
            return self._apply_at_position(content, position, new_content, operation)
        elif target_type == "heading":
            position = self._find_heading_target(content, target)
            if position is None and create_if_missing:
                # Create heading at end of document
                return self._create_heading(content, target, new_content)
            elif position is None:
                raise TargetNotFoundError(f"Heading not found: {target}")
            return self._apply_at_position(content, position, new_content, operation)
        else:
            raise InvalidTargetError(
                f"Invalid target type: {target_type}. "
                f"Must be 'heading', 'block', or 'frontmatter'"
            )

    def _parse_heading_hierarchy(self, content: str) -> list[HeadingNode]:
        """
        Parse markdown content into a heading hierarchy tree.

        Args:
            content: Markdown content to parse

        Returns:
            List of top-level heading nodes with nested children
        """
        lines = content.split("\n")
        root_nodes: list[HeadingNode] = []
        stack: list[HeadingNode] = []

        for i, line in enumerate(lines):
            match = self.HEADING_PATTERN.match(line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()

                # Close previous heading's content
                if stack:
                    stack[-1].end_line = i - 1

                # Create new heading node
                node = HeadingNode(
                    text=text,
                    level=level,
                    start_line=i,
                    end_line=len(lines) - 1,  # Default to end of file
                    children=[],
                )

                # Pop stack until we find parent level
                while stack and stack[-1].level >= level:
                    popped = stack.pop()
                    # Set end_line for popped node
                    if stack:
                        popped.end_line = i - 1

                # Add to parent or root
                if stack:
                    stack[-1].children.append(node)
                else:
                    root_nodes.append(node)

                stack.append(node)

        return root_nodes

    def _find_heading_in_tree(
        self, nodes: list[HeadingNode], path: list[str], index: int = 0
    ) -> HeadingNode | None:
        """
        Find a heading node by path through the tree.

        Args:
            nodes: List of heading nodes to search
            path: Path components (e.g., ["Section 1", "Subsection A"])
            index: Current index if multiple headings match (0-based)

        Returns:
            HeadingNode if found, None otherwise
        """
        if not path:
            return None

        target_text = path[0]
        remaining_path = path[1:]

        # Find all matching headings at this level
        matches = [node for node in nodes if node.text == target_text]

        if not matches:
            # If this is a single-component path, search recursively in children
            if not remaining_path:
                for node in nodes:
                    found = self._find_heading_in_tree(node.children, path, index)
                    if found:
                        return found
            return None

        # Apply index if this is the final path component
        if not remaining_path:
            if index >= len(matches):
                return None
            return matches[index]

        # Search in children of first match (index only applies to final component)
        return self._find_heading_in_tree(matches[0].children, remaining_path, index)

    def _find_heading_target(self, content: str, target: str) -> BlockPosition | None:
        """
        Find the position of a heading target.

        Target format: "Heading::Subheading::Deep:N"
        - "::" separates heading hierarchy
        - ":N" at the end specifies 1-based index for duplicate headings

        Args:
            content: Markdown content
            target: Heading path (e.g., "Meeting Notes::Action Items:2")

        Returns:
            BlockPosition of the heading's content area, or None if not found
        """
        # Parse index from end of target (e.g., "Heading:2" -> ("Heading", 1))
        parts = target.split("::")
        if not parts:
            return None

        last_part = parts[-1]
        index = 0

        # Check if last part has :N index
        if ":" in last_part:
            heading_text, index_str = last_part.rsplit(":", 1)
            try:
                # Convert from 1-based to 0-based index
                index = int(index_str) - 1
                if index < 0:
                    raise InvalidTargetError(f"Index must be >= 1, got: {index_str}")
                parts[-1] = heading_text
            except ValueError:
                # Not a valid index, treat whole thing as heading text
                pass

        # Build heading hierarchy
        tree = self._parse_heading_hierarchy(content)

        # Find the target heading
        node = self._find_heading_in_tree(tree, parts, index)

        if node is None:
            return None

        # Return position of heading's content (after heading line, before next heading)
        content_start = node.start_line + 1

        # Find actual end of this heading's content (before any child headings)
        content_end = node.end_line
        if node.children:
            content_end = node.children[0].start_line - 1

        return BlockPosition(
            start_line=content_start,
            end_line=content_end,
            start_col=0,
            end_col=-1,
        )

    def _find_block_target(self, content: str, block_id: str) -> BlockPosition:
        """
        Find a block reference in the content.

        Block references are in the format ^blockid at the end of a line.

        Args:
            content: Markdown content
            block_id: Block identifier (without the ^ prefix)

        Returns:
            BlockPosition of the line containing the block reference

        Raises:
            TargetNotFoundError: If block reference not found
        """
        lines = content.split("\n")

        for i, line in enumerate(lines):
            match = self.BLOCK_PATTERN.search(line)
            if match and match.group(1) == block_id:
                # Block reference found - target is this line
                # Remove the block reference from the line for replacement
                # Find the space before the ^ (we want to preserve text before it)
                block_start = match.start()
                # If there's a space before ^, include it in the exclusion
                if block_start > 0 and line[block_start - 1] == " ":
                    block_start -= 1
                return BlockPosition(
                    start_line=i,
                    end_line=i,
                    start_col=0,
                    end_col=block_start,
                )

        raise TargetNotFoundError(f"Block reference not found: ^{block_id}")

    def _update_frontmatter(
        self, content: str, field: str, value: Any, operation: str
    ) -> str:
        """
        Update a frontmatter field.

        Args:
            content: Markdown content with frontmatter
            field: Field name to update
            value: New value (can be string, number, list, dict)
            operation: 'replace' or 'append' (append for lists)

        Returns:
            Updated markdown content

        Raises:
            InvalidTargetError: If operation not supported for frontmatter
        """
        # Parse frontmatter
        post = frontmatter.loads(content)

        # For frontmatter, 'prepend' doesn't make sense
        if operation == "prepend":
            raise InvalidTargetError(
                "Operation 'prepend' not supported for frontmatter. Use 'replace' or 'append'."
            )

        # Parse value if it's a JSON string
        if isinstance(value, str):
            try:
                # Try to parse as YAML/JSON
                import json

                value = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                # Keep as string if not valid JSON
                pass

        if operation == "replace":
            post.metadata[field] = value
        elif operation == "append":
            # Append to list field
            if field not in post.metadata:
                post.metadata[field] = []
            if not isinstance(post.metadata[field], list):
                raise InvalidTargetError(f"Cannot append to non-list field: {field}")
            if isinstance(value, list):
                post.metadata[field].extend(value)
            else:
                post.metadata[field].append(value)
        else:
            raise InvalidTargetError(f"Invalid operation for frontmatter: {operation}")

        # Serialize back to markdown
        return frontmatter.dumps(post)

    def _apply_at_position(
        self, content: str, position: BlockPosition, new_content: str, operation: str
    ) -> str:
        """
        Apply operation at a specific position in content.

        Args:
            content: Original content
            position: Position to apply operation
            new_content: Content to insert/replace
            operation: 'append', 'prepend', or 'replace'

        Returns:
            Updated content

        Raises:
            InvalidTargetError: If operation is invalid
        """
        lines = content.split("\n")

        if operation == "replace":
            # Replace entire block/section
            # Remove old content
            before = lines[: position.start_line]
            after = lines[position.end_line + 1 :]

            # Insert new content
            new_lines = new_content.split("\n")
            result_lines = before + new_lines + after

        elif operation == "append":
            # Append to end of block/section
            before = lines[: position.end_line + 1]
            after = lines[position.end_line + 1 :]

            # For block references, append on same line before block ref
            if position.start_line == position.end_line and position.end_col > 0:
                # Append to same line before block reference
                line = lines[position.start_line]
                block_ref = line[position.end_col :]
                line_content = line[: position.end_col].rstrip()
                new_line = line_content + " " + new_content.strip() + block_ref
                before = lines[: position.start_line] + [new_line]
            else:
                # Append as new lines
                if not new_content.startswith("\n"):
                    new_content = "\n" + new_content

                new_lines = new_content.split("\n")
                result_lines = before + new_lines + after
                return "\n".join(result_lines)

            result_lines = before + after

        elif operation == "prepend":
            # Prepend to beginning of block/section
            before = lines[: position.start_line]
            after = lines[position.start_line :]

            new_lines = new_content.split("\n")
            if new_lines and not new_lines[-1]:
                new_lines = new_lines[:-1]

            result_lines = before + new_lines + after

        else:
            raise InvalidTargetError(
                f"Invalid operation: {operation}. Must be 'append', 'prepend', or 'replace'"
            )

        return "\n".join(result_lines)

    def _create_heading(self, content: str, target: str, new_content: str) -> str:
        """
        Create a new heading at the end of the document.

        Args:
            content: Original content
            target: Heading path (e.g., "New Section::Subsection")
            new_content: Content under the heading

        Returns:
            Updated content with new heading
        """
        # Parse hierarchy from target
        parts = target.split("::")

        # Remove index if present
        if ":" in parts[-1]:
            parts[-1] = parts[-1].rsplit(":", 1)[0]

        # Build heading structure
        lines = []
        if content and not content.endswith("\n"):
            lines.append("")  # Add blank line before new heading

        # Add headings
        for i, heading in enumerate(parts):
            level = i + 1
            lines.append(f"{'#' * level} {heading}")
            lines.append("")

        # Add content
        lines.append(new_content)

        if content:
            return content + "\n" + "\n".join(lines)
        else:
            return "\n".join(lines)


__all__ = [
    "PatchEngine",
    "PatchError",
    "TargetNotFoundError",
    "InvalidTargetError",
    "HeadingNode",
    "BlockPosition",
]
