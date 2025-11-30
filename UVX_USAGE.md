# Using markdown-vault with uvx

## What is uvx?

`uvx` is uv's command for running Python applications in isolated environments without permanent installation. It's like `npx` for Python - run tools directly without polluting your global environment.

## Quick Start

### ✅ Current Status: READY

The package is **fully compatible** with `uvx` right now!

### Local Testing (Before Publishing)

Run from the built wheel file:

```bash
# Build the package first
uv build

# Run with uvx from local wheel
uvx --from dist/markdown_vault-0.0.1-py3-none-any.whl markdown-vault --help
uvx --from dist/markdown_vault-0.0.1-py3-none-any.whl markdown-vault version
```

### After Publishing to PyPI

Once published, users can run it directly:

```bash
# Run the latest version
uvx markdown-vault start --help

# Run a specific version
uvx markdown-vault==0.0.1 start

# Start the server
uvx markdown-vault start --reload

# With a config file
uvx markdown-vault start --config /path/to/config.yaml
```

## Usage Examples

### 1. One-off Server Launch

```bash
# Quick test without installation
uvx markdown-vault start --reload
```

### 2. Generate API Key

```bash
# Generate a key without installing
uvx markdown-vault start --generate-key
```

### 3. Check Version

```bash
uvx markdown-vault version
```

### 4. With Environment Variables

```bash
# Set config via env vars
MARKDOWN_VAULT_SERVER__PORT=8080 \
MARKDOWN_VAULT_VAULT__PATH=/path/to/vault \
uvx markdown-vault start
```

## Configuration Options

### Method 1: Config File
```bash
uvx markdown-vault start --config config.yaml
```

### Method 2: Environment Variables
```bash
export MARKDOWN_VAULT_SERVER__HOST=0.0.0.0
export MARKDOWN_VAULT_SERVER__PORT=27124
export MARKDOWN_VAULT_VAULT__PATH=/path/to/vault
uvx markdown-vault start
```

### Method 3: Inline (with uvx env)
```bash
uvx --with markdown-vault markdown-vault start
```

## Entry Point Configuration

The package is configured with a CLI entry point in `pyproject.toml`:

```toml
[project.scripts]
markdown-vault = "markdown_vault.__main__:main"
```

This means:
- ✅ The `markdown-vault` command is available after installation
- ✅ `uvx` can find and run it automatically
- ✅ Works from PyPI once published
- ✅ Works from local wheel files now

## Advantages of uvx

1. **No Installation Required** - Run without `pip install`
2. **Isolated Environment** - Each run gets fresh dependencies
3. **Version Pinning** - Specify exact version to run
4. **Clean System** - No global package pollution
5. **Quick Testing** - Try before you buy

## For Users (After PyPI Publishing)

### Installation Methods Comparison

| Method | Command | Use Case |
|--------|---------|----------|
| **uvx** (recommended) | `uvx markdown-vault start` | Quick runs, testing, CI/CD |
| **uv pip** | `uv pip install markdown-vault` | Development, permanent install |
| **pipx** | `pipx install markdown-vault` | Global CLI tool |
| **pip** | `pip install markdown-vault` | Traditional installation |

### Recommended: Use uvx

```bash
# For most users - just run it!
uvx markdown-vault start --reload
```

### Why uvx is Great for This Tool

- **Server Application** - Often run temporarily for specific vaults
- **No Config Needed** - Can use env vars or CLI flags
- **Clean Environment** - Fresh dependencies every time
- **Easy Updates** - Just run `uvx markdown-vault@latest`

## Publishing to PyPI

To make this work for everyone:

```bash
# 1. Build the package
uv build

# 2. Upload to PyPI (requires account)
uv publish

# Or use twine
python -m twine upload dist/*
```

After publishing, anyone can:

```bash
uvx markdown-vault start
```

## Verification Checklist

- ✅ Package builds successfully (`uv build`)
- ✅ Entry point defined in `pyproject.toml`
- ✅ Works with local wheel (`uvx --from dist/...`)
- ✅ CLI commands work (`start`, `version`)
- ✅ Help text displays correctly
- ✅ All dependencies included

## Current Status

**Ready for uvx** ✅

```bash
# Works now (from local wheel)
uvx --from dist/markdown_vault-0.0.1-py3-none-any.whl markdown-vault start --help

# Will work after PyPI publish
uvx markdown-vault start
```

## Alternative: pipx (Similar Tool)

If users prefer `pipx`:

```bash
# Install once
pipx install markdown-vault

# Run anytime
markdown-vault start

# Upgrade
pipx upgrade markdown-vault
```

## Documentation for README

Add to README.md:

```markdown
## Quick Start with uvx (Recommended)

No installation needed! Run directly:

\`\`\`bash
uvx markdown-vault start --reload
\`\`\`

Or install permanently:

\`\`\`bash
pip install markdown-vault
markdown-vault start --reload
\`\`\`
```

---

**Status**: ✅ Fully compatible with uvx!  
**Tested**: Works with local wheel  
**Ready**: Publish to PyPI for global uvx access
