# Research: Obsidian Local REST API Analysis

**Date**: November 27, 2025  
**Source**: [obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api)  
**Version Analyzed**: 3.2.0

## Overview

The Obsidian Local REST API plugin provides a secure HTTPS interface (default port 27123) for programmatic interaction with Obsidian vaults. It enables automation and external tool integration through a well-documented REST API.

## Core Features

### 1. Authentication & Security

- **HTTPS Only**: Self-signed certificate generated on first run
- **Bearer Token Authentication**: API key-based access control
- **Certificate Access**: `/obsidian-local-rest-api.crt` endpoint for cert download

### 2. File Operations

#### Standard CRUD
- `GET /vault/{filepath}` - Read file content
- `PUT /vault/{filepath}` - Create or replace file
- `POST /vault/{filepath}` - Append content to file
- `DELETE /vault/{filepath}` - Delete file
- `GET /vault/` - List all files in vault

#### Response Formats
Two content negotiation options:

**Markdown** (`Accept: text/markdown`):
```markdown
# This is my document

something else here
```

**JSON** (`Accept: application/vnd.olrapi.note+json`):
```json
{
  "path": "path/to/note.md",
  "content": "# This is my document\n\nsomething else here",
  "frontmatter": {
    "tags": ["note"],
    "created": "2025-01-01"
  },
  "tags": ["#inline-tag"],
  "stat": {
    "ctime": 1234567890000,
    "mtime": 1234567891000,
    "size": 1024
  }
}
```

### 3. PATCH Operations (Most Complex Feature)

Advanced content targeting for surgical updates within markdown documents.

#### Target Types

**Heading Navigation**
- Navigate nested heading hierarchy
- Uses delimiter (default `::`) to specify path
- Example: `Heading 1::Subheading 1:1::Subsubheading 1:1:1`

**Block References**
- Target specific blocks using Obsidian's block ID syntax
- Example: `^abc123`

**Frontmatter Fields**
- Modify YAML frontmatter properties
- Supports nested field access
- Example: `metadata.author`

#### Operations

- **append**: Add content after target
- **prepend**: Add content before target
- **replace**: Replace target content

#### Required Headers

```http
Operation: append|prepend|replace
Target-Type: heading|block|frontmatter
Target: <identifier>
Target-Delimiter: :: (optional, default ::)
Trim-Target-Whitespace: true|false (optional)
Create-Target-If-Missing: true|false (optional, for frontmatter)
```

#### Content Types

- `text/markdown` - Raw markdown text
- `application/json` - Structured data (especially useful for frontmatter and tables)

#### PATCH Examples

**Append to Heading**
```http
PATCH /vault/note.md
Authorization: Bearer API_KEY
Operation: append
Target-Type: heading
Target: Meeting Notes::Action Items

- New action item
```

**Update Block Reference**
```http
PATCH /vault/note.md
Authorization: Bearer API_KEY
Operation: replace
Target-Type: block
Target: ^summary-123

Updated summary text
```

**Set Frontmatter Field**
```http
PATCH /vault/note.md
Authorization: Bearer API_KEY
Operation: replace
Target-Type: frontmatter
Target: status
Content-Type: application/json

"completed"
```

**Add Table Rows** (via Block Reference)
```http
PATCH /vault/note.md
Authorization: Bearer API_KEY
Operation: append
Target-Type: block
Target: ^table-ref
Content-Type: application/json

[["New Row", "Data 1", "Data 2"]]
```

### 4. Active File Operations

Tracks the "currently active" file in Obsidian's UI:

- `GET /active/` - Get active file content
- `PUT /active/` - Update active file
- `POST /active/` - Append to active file
- `PATCH /active/` - Partial update active file
- `DELETE /active/` - Delete active file
- `POST /open/{filename}` - Open file in Obsidian UI (sets as active)

**Query Parameters**:
- `newLeaf`: boolean - Open in new pane/tab

### 5. Periodic Notes

Support for time-based notes:

**Periods Supported**:
- `daily` - One note per day
- `weekly` - One note per week
- `monthly` - One note per month
- `quarterly` - One note per quarter
- `yearly` - One note per year

**Endpoints**:
- `GET /periodic/{period}/` - Get current period note
- `PUT /periodic/{period}/` - Update current period note
- `POST /periodic/{period}/` - Append to current period note
- `PATCH /periodic/{period}/` - Partial update current period note
- `DELETE /periodic/{period}/` - Delete current period note

**Auto-Creation**: If periodic note doesn't exist, it's created based on configured template.

### 6. Search

**Simple Search** (`POST /search/simple/`):
- Text-based search across vault
- Returns matching file paths

**Complex Search** (`POST /search/`):
- JSONLogic-based query language
- Filter by frontmatter, tags, content, dates
- Boolean combinations (AND, OR, NOT)

### 7. Commands

Obsidian-specific command execution:

- `GET /commands/` - List all available Obsidian commands
- `POST /commands/{commandId}/` - Execute specific command

Example commands:
```json
{
  "commands": [
    {
      "id": "global-search:open",
      "name": "Search: Search in all files"
    },
    {
      "id": "graph:open",
      "name": "Graph view: Open graph view"
    }
  ]
}
```

### 8. System Endpoints

- `GET /` - Server status and authentication check
- `GET /openapi.yaml` - OpenAPI 3.0 specification
- `GET /obsidian-local-rest-api.crt` - Download SSL certificate

## Technical Implementation Details

### OpenAPI Specification

The plugin includes a complete OpenAPI 3.0 spec (`openapi.yaml`) with:
- All endpoints documented
- Request/response schemas
- Security requirements
- Example payloads

### Error Handling

Standard error response format:
```json
{
  "errorCode": 40149,
  "message": "A brief description of the error."
}
```

**5-digit error codes** uniquely identify error types.

### HTTP Status Codes

- `200` - Success with content
- `204` - Success without content
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found (file/resource doesn't exist)
- `405` - Method Not Allowed (e.g., trying to POST to a directory)

## Implementation Challenges

### 1. PATCH Engine Complexity

The PATCH operation requires:
- Markdown parsing and AST manipulation
- Heading hierarchy tracking
- Block reference resolution
- YAML frontmatter parsing/serialization
- Table structure understanding
- Whitespace preservation

### 2. Obsidian-Specific Features

Some features are tightly coupled to Obsidian:
- Commands API requires Obsidian command registry
- Active file tracking requires Obsidian UI state
- Periodic notes depend on Obsidian's periodic notes plugin configuration

### 3. File Watching

For real-time sync with Obsidian:
- Need file system watcher to detect external changes
- Handle concurrent access safely
- Avoid conflicts when both plugin and standalone service modify files

## Compatibility Requirements

For drop-in replacement compatibility:

1. **Exact API Match**: All endpoints must match signatures
2. **Response Format**: JSON structure must be identical
3. **Error Codes**: Use same 5-digit error code system
4. **OpenAPI Spec**: Should validate against original spec
5. **Header Handling**: Support all custom headers (Operation, Target-Type, etc.)
6. **Content Negotiation**: Support both markdown and JSON responses

## Standalone Service Adaptations

### Active File Tracking

Since standalone service lacks Obsidian UI:

**Option 1**: Maintain server-side "active file" state
- Track via session or cookie
- Default to most recently accessed file
- Expose `/active/set/{filepath}` endpoint

**Option 2**: Require explicit file paths
- Make active file endpoints optional
- Document as Obsidian-compatibility layer

### Commands API

**Option 1**: Plugin system for extensibility
- Define standard command interface
- Allow users to register custom commands
- Provide built-in commands (search, create note, etc.)

**Option 2**: Mark as optional
- Return empty command list
- Document as Obsidian-only feature

### Periodic Notes Configuration

Standalone service needs configuration for:
- Date format per period type
- Template file location
- Target folder structure

Example:
```yaml
periodic_notes:
  daily:
    format: "YYYY-MM-DD"
    folder: "daily/"
    template: "templates/daily.md"
  weekly:
    format: "YYYY-[W]WW"
    folder: "weekly/"
    template: "templates/weekly.md"
```

## Technology Recommendations

### Backend Framework

**FastAPI (Python)** - Recommended
- Native OpenAPI generation
- Type safety with Pydantic
- Async/await support
- Excellent performance
- Easy testing

**Express.js (TypeScript)** - Alternative
- JavaScript ecosystem
- Good OpenAPI integration
- Large plugin ecosystem

### Markdown Parsing

**Python**:
- `python-frontmatter` - YAML frontmatter extraction
- `markdown-it-py` - Markdown parsing
- `mistletoe` - Advanced AST manipulation

**Node.js**:
- `gray-matter` - Frontmatter parsing
- `unified`/`remark` - Markdown AST
- `mdast` - Markdown syntax tree

### File Operations

- **Python**: `aiofiles` for async I/O
- **Node.js**: `fs.promises` native async support

### SSL/TLS

- Self-signed cert generation: `cryptography` (Python) or `node-forge` (Node)
- HTTPS server: Built into FastAPI/Express

## Next Steps for Implementation

1. Set up FastAPI project structure
2. Implement basic file operations (GET/PUT/POST/DELETE)
3. Build markdown parser with frontmatter support
4. Implement PATCH engine with heading/block/frontmatter targeting
5. Add periodic notes logic
6. Implement search functionality
7. Create configuration system
8. Add authentication and SSL
9. Write comprehensive tests
10. Package for distribution

## References

- [Obsidian Local REST API GitHub](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [Interactive API Docs](https://coddingtonbear.github.io/obsidian-local-rest-api/)
- [OpenAPI Specification](https://github.com/coddingtonbear/obsidian-local-rest-api/blob/main/docs/openapi.yaml)
