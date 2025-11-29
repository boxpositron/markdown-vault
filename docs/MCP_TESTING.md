# Testing markdown-vault with Model Context Protocol (MCP)

This guide explains how to test markdown-vault using with-context-mcp, which validates our compatibility with the Obsidian Local REST API.

## Overview

**with-context-mcp** is an MCP server that provides AI agents with tools to manage markdown notes. It was designed for Obsidian's Local REST API, making it perfect for testing our drop-in replacement.

## Why This Matters

By testing with with-context-mcp, we:
- ✅ Validate API compatibility with real-world tooling
- ✅ Test all CRUD operations through a production MCP client
- ✅ Ensure we're a true drop-in replacement for Obsidian plugin
- ✅ Get practical testing instead of manual curl commands

## Setup

### 1. Install with-context-mcp

```bash
npm install -g with-context-mcp
```

### 2. Configure Environment

Load the test environment variables:

```bash
source .env.test
```

This sets:
- **Server variables** (used by markdown-vault server):
  - `MARKDOWN_VAULT_API_KEY` - API key for authentication
  - `MARKDOWN_VAULT_PATH` - Vault directory path
  - `MARKDOWN_VAULT_PORT` - Server port
- **Client variables** (used by MCP clients like with-context-mcp):
  - `VAULT_API_URL` or `OBSIDIAN_API_URL` - Points to server (e.g., https://127.0.0.1:27124)
  - `VAULT_API_KEY` or `OBSIDIAN_API_KEY` - API key for client authentication
  - `VAULT_NAME` or `OBSIDIAN_VAULT` - Vault name (e.g., test_vault)

**Note**: The `OBSIDIAN_*` client variables are for compatibility with existing MCP clients. New integrations should use `VAULT_*` variables.

### 3. Start markdown-vault Server

```bash
# Option 1: Using the convenience script
./scripts/start-test-server.sh

# Option 2: Direct command
python -m markdown_vault start --config test_config.yaml
```

The server will:
- Start on port 27124 (Obsidian's default port)
- Generate self-signed SSL certificates
- Use the API key from environment
- Create `test_vault/` directory if needed

### 4. Verify Server is Running

In another terminal:

```bash
# Check server status (no auth required)
curl -k https://127.0.0.1:27124/

# Should return:
# {
#   "ok": "OK",
#   "service": "markdown-vault",
#   "authenticated": false,
#   "versions": {"self": "0.1.0", "api": "1.0"}
# }

# Test authenticated endpoint
curl -k -H "Authorization: Bearer test-api-key-for-mcp-testing-12345" \
  https://127.0.0.1:27124/vault/

# Should return: []  (empty vault initially)
```

## Using with OpenCode

### 1. MCP Configuration

The `opencode.jsonc` file is already configured:

```jsonc
{
  "mcp": {
    "with-context": {
      "type": "local",
      "command": "npx",
      "args": ["-y", "with-context-mcp"],
      "environment": {
        // Client-side variables (used by with-context-mcp)
        // Using OBSIDIAN_* for backward compatibility with MCP client
        "OBSIDIAN_API_KEY": "{env:MARKDOWN_VAULT_API_KEY}",
        "OBSIDIAN_API_URL": "https://127.0.0.1:27124",
        "OBSIDIAN_VAULT": "test_vault",
        "PROJECT_BASE_PATH": "."
      },
      "enabled": true
    }
  }
}

// Note: For new integrations, you can use white-label variable names:
// "VAULT_API_KEY", "VAULT_API_URL", "VAULT_NAME"
// Both sets work with markdown-vault server.
```

### 2. Start OpenCode with MCP

```bash
# Ensure environment is loaded
source .env.test

# Start OpenCode (MCP will connect automatically)
opencode
```

### 3. Test MCP Tools

In OpenCode, you can now use with-context-mcp tools:

```
# Example prompts to test:
"Create a test note in the vault called hello.md with some content"
"List all files in the vault"
"Read the contents of hello.md"
"Append some text to hello.md"
"Delete hello.md"
```

## Available MCP Tools

with-context-mcp provides 33 tools, including:

**Core Operations:**
- `write_note` - Create/update files (PUT /vault/{path})
- `read_note` - Read files (GET /vault/{path})
- `list_files` - List vault files (GET /vault/)
- `delete_note` - Delete files (DELETE /vault/{path})

**Advanced:**
- `search_by_content` - Search files (POST /search/simple/)
- `update_frontmatter` - Modify YAML frontmatter (PATCH /vault/{path})
- `replace_section` - Edit specific sections (PATCH /vault/{path})

## Testing Checklist

- [ ] Server starts successfully on port 27124
- [ ] SSL certificate auto-generates
- [ ] API key authentication works
- [ ] MCP can connect to server
- [ ] Create note via MCP
- [ ] Read note via MCP
- [ ] List files via MCP
- [ ] Append to note via MCP
- [ ] Delete note via MCP
- [ ] Error handling works (invalid paths, etc.)

## Troubleshooting

### MCP Can't Connect

**Error:** Connection refused or SSL errors

**Solution:**
1. Verify server is running: `curl -k https://127.0.0.1:27124/`
2. Check environment variables are loaded: `echo $MARKDOWN_VAULT_API_KEY`
3. Ensure OpenCode has access to env vars

### Authentication Failures

**Error:** 401 Unauthorized

**Solution:**
1. Verify API key matches: Compare `$MARKDOWN_VAULT_API_KEY` with server config
2. Check Authorization header format
3. Look at server logs for authentication attempts

### Path Errors

**Error:** Path validation errors

**Solution:**
- MCP uses relative paths only
- All paths are relative to vault root
- No `../` or absolute paths allowed

## Next Steps

Once MCP testing works:
1. ✅ Validates basic CRUD operations
2. ⏳ Implement PATCH operations (heading/block targeting)
3. ⏳ Add periodic notes endpoints
4. ⏳ Implement search functionality
5. ⏳ Add active file tracking

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│  OpenCode   │  MCP    │ with-context │  HTTPS  │ markdown-vault  │
│  (AI Agent) │◄───────►│     -mcp     │◄───────►│     Server      │
└─────────────┘         └──────────────┘         └─────────────────┘
                        (expects Obsidian API)   (drop-in replacement)
                                                          │
                                                          ▼
                                                   ┌─────────────┐
                                                   │ test_vault/ │
                                                   │  *.md files │
                                                   └─────────────┘
```

## References

- [with-context-mcp GitHub](https://github.com/boxpositron/with-context-mcp)
- [Obsidian Local REST API Plugin](https://github.com/coddingtonbear/obsidian-local-rest-api)
- [Model Context Protocol](https://modelcontextprotocol.io/)
