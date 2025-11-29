# Markdown-Vault Rebranding Plan

**Goal**: Transform markdown-vault into a white-label REST API solution that is **compatible with** Obsidian Local REST API, without using Obsidian branding.

**Date**: 2025-11-29  
**Status**: Planning Phase

---

## Executive Summary

This document outlines a comprehensive plan to rebrand markdown-vault from "drop-in replacement for Obsidian Local REST API" to "REST API for markdown vaults with Obsidian compatibility". The key principle is to maintain 100% API compatibility while removing Obsidian branding from user-facing elements.

### Key Changes
- Remove Obsidian branding from API paths, environment variables, and responses
- Maintain backward compatibility for existing users
- Keep internal references to Obsidian where appropriate for compatibility documentation
- Update all user-facing documentation to emphasize white-label nature

---

## Complete Obsidian Reference Audit

### 1. Environment Variables ✅ CLARIFIED

**Important Distinction**: There are TWO sets of environment variables with different purposes:

**SERVER Variables** (used BY markdown-vault server) - ✅ Already white-labeled:
- `MARKDOWN_VAULT_API_KEY` - Server's API key
- `MARKDOWN_VAULT_PATH` - Vault directory path
- `MARKDOWN_VAULT_PORT` - Server port
- `MARKDOWN_VAULT_HOST` - Server host
- `MARKDOWN_VAULT_OBSIDIAN__ENABLED` - Internal Obsidian compatibility config

**CLIENT Variables** (used by MCP clients TO connect to our server):
- `OBSIDIAN_API_URL` / `VAULT_API_URL` - Server URL (client-side)
- `OBSIDIAN_API_KEY` / `VAULT_API_KEY` - API key for authentication (client-side)
- `OBSIDIAN_VAULT` / `VAULT_NAME` - Vault name (client-side)

**Action Taken (Phase 1b)**:
- ✅ Documentation updated to clarify server vs client variables
- ✅ Recommend `VAULT_*` for new client integrations (white-label)
- ✅ Keep `OBSIDIAN_*` for backward compatibility with existing Obsidian-based clients
- ✅ Server variables remain `MARKDOWN_VAULT_*` (already correct)

**Result**: No breaking changes needed. Our server variables are already white-labeled. Client variables are chosen by the client (not our concern).

---

### 2. API Endpoint Paths ⚠️ MUST CHANGE

#### File: `src/markdown_vault/api/routes/system.py`

**Lines 131, 204, 206:**
```python
# CURRENT - Obsidian branding
@router.get("/obsidian-local-rest-api.crt")
# Returns: filename="obsidian-local-rest-api.crt"

# PROPOSED - White-label
@router.get("/server.crt")
# Returns: filename="markdown-vault.crt"

# BACKWARD COMPATIBILITY - Keep old endpoint as alias
@router.get("/obsidian-local-rest-api.crt")  # Deprecated, redirects to /server.crt
```

**Priority**: HIGH - User-facing API endpoint

---

### 3. Configuration Model Names ⚠️ CAN KEEP (Internal)

#### File: `src/markdown_vault/models/config.py`

**Lines 73-83:**
```python
class ObsidianConfig(BaseModel):
    """Obsidian vault compatibility configuration."""
    
    enabled: bool = Field(default=True, description="Enable Obsidian-specific features")
```

**Current Status**: Internal model name  
**Proposed Action**: 
- **Option A (Conservative)**: Keep as `ObsidianConfig` - it's literally for Obsidian compatibility features
- **Option B (White-label)**: Rename to `CompatibilityConfig` or `VaultCompatConfig`

**Recommendation**: **Keep as-is**. The config section is explicitly for Obsidian vault compatibility features. Renaming would reduce clarity.

**YAML Config Key**: 
```yaml
# CURRENT
obsidian:
  enabled: true
  config_sync: true

# PROPOSED - More generic
vault_compatibility:
  obsidian_enabled: true    # Still mention Obsidian for clarity
  import_config: true       # More generic
  respect_exclusions: true
```

**Environment Variables**:
```bash
# CURRENT
MARKDOWN_VAULT_OBSIDIAN__ENABLED=true

# PROPOSED
MARKDOWN_VAULT_VAULT_COMPATIBILITY__OBSIDIAN_ENABLED=true
# OR keep as-is since it's explicitly Obsidian compat
```

**Recommendation**: Keep YAML key as `obsidian:` - it's configuration specifically for Obsidian vault compatibility, not general vault compat.

---

### 4. Response Bodies - Service Name ✅ ALREADY CORRECT

#### File: `src/markdown_vault/models/api.py:57`
```python
service: str = Field(default="markdown-vault", description="Service name")
```

**Status**: ✅ Already white-labeled correctly

#### File: `src/markdown_vault/api/routes/system.py:71`
```python
return ServerStatus(
    ok="OK",
    service="markdown-vault",  # ✅ Already correct
    authenticated=is_authenticated,
    versions={
        "self": "0.1.0",
        "api": "1.0",
    },
)
```

**Status**: ✅ Already white-labeled correctly

---

### 5. Code Comments & Docstrings 💡 UPDATE FOR CLARITY

**Pattern**: "Drop-in replacement for Obsidian" → "Compatible with Obsidian REST API"

#### File: `src/markdown_vault/__init__.py:4-5`
```python
# CURRENT
"""
A drop-in replacement for the Obsidian Local REST API plugin that works
independently without requiring Obsidian to be installed or running.
"""

# PROPOSED
"""
A standalone REST API for markdown vaults with full compatibility with the
Obsidian Local REST API. Works independently without requiring Obsidian.
"""
```

#### File: `src/markdown_vault/__main__.py:26`
```python
# CURRENT
help="Drop-in replacement for Obsidian Local REST API",

# PROPOSED
help="REST API server for markdown vaults with Obsidian compatibility",
```

#### File: `src/markdown_vault/main.py:208-210`
```python
# CURRENT
"Drop-in replacement for Obsidian Local REST API with standalone "
"service capabilities for managing markdown notes..."

# PROPOSED
"REST API service for markdown vaults with Obsidian Local REST API "
"compatibility. Manages markdown notes independently..."
```

#### File: `src/markdown_vault/utils/crypto.py:4`
```python
# CURRENT
for HTTPS server operation, compatible with the Obsidian Local REST API

# PROPOSED
for HTTPS server operation with Obsidian Local REST API compatibility
```

#### File: `src/markdown_vault/models/note.py:4`
```python
# CURRENT
These models match the Obsidian Local REST API response format for

# PROPOSED
Response models compatible with Obsidian Local REST API format for
```

#### File: `src/markdown_vault/models/api.py:57`
```python
# CURRENT
Matches Obsidian Local REST API error format with 5-digit error codes.

# PROPOSED
Error format compatible with Obsidian Local REST API (5-digit error codes).
```

---

### 6. Configuration Files 📝 UPDATE MESSAGING

#### File: `config/config.example.yaml`

**Line 9:**
```yaml
# CURRENT
# Port (27123 is the default Obsidian Local REST API port)

# PROPOSED
# Port (27123 for Obsidian REST API compatibility)
```

**Lines 50-59:**
```yaml
# CURRENT
# Obsidian integration
obsidian:
  # Enable Obsidian-specific features
  enabled: true
  
  # Sync settings from .obsidian/ directory
  config_sync: true

# PROPOSED - Keep structure, update comments
# Obsidian vault compatibility
obsidian:
  # Enable Obsidian vault compatibility features
  enabled: true
  
  # Import configuration from .obsidian/ directory
  config_sync: true
```

#### File: `config/obsidian-integration.example.yaml`

**Rename to**: `config/obsidian-vault.example.yaml`

**Lines 1-12:**
```yaml
# CURRENT
# markdown-vault Configuration as Drop-in Replacement for Obsidian Plugin
#
# Use this configuration to REPLACE the Obsidian Local REST API plugin
# with markdown-vault pointing to your existing Obsidian vault.

# PROPOSED
# markdown-vault Configuration for Obsidian Vault Compatibility
#
# This configuration enables compatibility with Obsidian vaults,
# allowing you to use markdown-vault with existing Obsidian directories.
```

---

### 7. Documentation Files 📚 MAJOR UPDATES NEEDED

#### README.md - Complete Rewrite

**Current Focus**: "Drop-in replacement for Obsidian"  
**New Focus**: "REST API for markdown vaults (Obsidian-compatible)"

**Key Changes**:

```markdown
# CURRENT (Line 3)
A drop-in replacement for the Obsidian Local REST API plugin that can run as a standalone service.

# PROPOSED
A standalone REST API server for markdown vaults with full Obsidian Local REST API compatibility.

---

# CURRENT (Lines 7-12)
**markdown-vault** is a standalone service that provides a REST API for managing 
markdown files with full compatibility with the Obsidian Local REST API plugin. 
It operates in two modes:

1. **Standalone Mode**: Manage any markdown vault independently - no Obsidian required
2. **Drop-in Replacement Mode**: Point it at an Obsidian vault to replace the plugin

# PROPOSED
**markdown-vault** is a standalone REST API server for managing markdown notes and vaults.
It provides full compatibility with the Obsidian Local REST API, allowing you to:

1. **Manage any markdown vault** - Works with any markdown directory structure
2. **Use with Obsidian vaults** - Compatible with Obsidian vault directories and configuration
3. **Run independently** - No Obsidian installation required

---

# CURRENT (Line 16)
- Full Obsidian REST API compatibility - drop-in replacement

# PROPOSED
- Full Obsidian Local REST API compatibility

---

# CURRENT (Line 26-38) - Entire comparison table
## Why Replace the Obsidian Plugin?
[Table comparing to Obsidian plugin]

# PROPOSED
## Key Advantages

- **Always Available**: Runs 24/7 as a service, independent of any desktop application
- **Server Deployment**: Deploy on servers, containers, cloud platforms
- **Multiple Vaults**: Manage multiple vaults concurrently
- **Automation-Ready**: Perfect for scripts, workflows, and integrations
- **Obsidian Compatible**: Works seamlessly with Obsidian vault structures

---

# CURRENT (Lines 40-48)
## Advantages Over Plugin

# PROPOSED - REMOVE THIS SECTION
# Keep focus on what markdown-vault IS, not what it replaces
```

#### docs/MIGRATION_FROM_PLUGIN.md

**Rename to**: `docs/OBSIDIAN_VAULT_COMPATIBILITY.md`

**Reframe**: Not "migration from plugin" but "using with Obsidian vaults"

```markdown
# CURRENT
# Migrating from Obsidian Local REST API Plugin
**Goal**: Replace the Obsidian Local REST API plugin with markdown-vault

# PROPOSED
# Using markdown-vault with Obsidian Vaults
**Goal**: Set up markdown-vault to work with your Obsidian vault directory
```

#### docs/PROJECT_SUMMARY.md

**Lines 9-20:**
```markdown
# CURRENT
**markdown-vault** is a standalone REST API service that replaces the Obsidian 
Local REST API plugin.

1. **Drop-in Replacement**: 100% API-compatible with Obsidian Local REST API plugin

# PROPOSED
**markdown-vault** is a standalone REST API service for markdown vault management.

1. **Obsidian Compatible**: 100% API-compatible with Obsidian Local REST API
```

#### pyproject.toml

**Line 8:**
```toml
# CURRENT
description = "Drop-in replacement for Obsidian Local REST API with standalone service capabilities"

# PROPOSED
description = "Standalone REST API server for markdown vaults with Obsidian compatibility"
```

**Line 15:**
```toml
# CURRENT
keywords = ["markdown", "obsidian", "api", "rest", "vault", "notes"]

# PROPOSED (keep obsidian for discoverability)
keywords = ["markdown", "vault", "api", "rest", "notes", "obsidian-compatible"]
```

---

### 8. Test Files 🧪 UPDATE REFERENCES

#### tests/test_api/test_system.py

**Lines 7, 216, 220, etc.:**
```python
# CURRENT
"""Tests for GET /obsidian-local-rest-api.crt endpoint."""
response = client.get("/obsidian-local-rest-api.crt")

# PROPOSED - Update to new endpoint, keep backward compat test
"""Tests for GET /server.crt endpoint."""
response = client.get("/server.crt")

# Add backward compatibility test
def test_legacy_cert_endpoint():
    """Test backward compatibility with /obsidian-local-rest-api.crt"""
    response = client.get("/obsidian-local-rest-api.crt")
    # Should redirect or alias to /server.crt
```

#### tests/test_patch_engine.py:529
```python
# CURRENT
# Obsidian only recognizes the last ^blockid on a line

# PROPOSED - Keep as-is (factual statement about Obsidian behavior)
# Obsidian only recognizes the last ^blockid on a line
```

---

### 9. File Names 📁 RENAME

| Current | Proposed | Priority |
|---------|----------|----------|
| `config/obsidian-integration.example.yaml` | `config/obsidian-vault.example.yaml` | Medium |
| `docs/MIGRATION_FROM_PLUGIN.md` | `docs/OBSIDIAN_VAULT_COMPATIBILITY.md` | Medium |

---

## Categorized Summary

### ⚠️ MUST CHANGE - User-Facing Branding

1. **API Endpoint**: `/obsidian-local-rest-api.crt` → `/server.crt`
   - Keep old endpoint as deprecated alias
   - Update filename in response: `markdown-vault.crt`
   
2. **Documentation Messaging**:
   - README.md: Remove "drop-in replacement" language
   - All docs: Change "replace Obsidian plugin" to "compatible with Obsidian"
   - Emphasize "white-label REST API for markdown vaults"

3. **Package Description** (pyproject.toml):
   - Update description and keywords

4. **CLI Help Text**:
   - Update help messages in `__main__.py`, `main.py`

### 💡 SHOULD UPDATE - Messaging Clarity

1. **Code Comments**: 142 instances
   - "Drop-in replacement" → "Compatible with"
   - "Obsidian plugin" → "Obsidian REST API"

2. **Docstrings**: 
   - Update module docstrings in `__init__.py`, `main.py`, etc.
   - Keep factual compatibility statements

3. **Configuration Comments**:
   - Update YAML comments to emphasize compatibility over replacement

### ✅ CAN KEEP - Internal/Compatibility

1. **Configuration Model Names**:
   - `ObsidianConfig` class name (internal, describes purpose)
   - `obsidian:` YAML key (explicitly for Obsidian compat features)
   - Environment variables with `OBSIDIAN` (explicitly for Obsidian compat)

2. **Test Comments**:
   - References to Obsidian behavior (factual statements)

3. **Documentation References**:
   - Links to Obsidian REST API project (attribution/compatibility)
   - Technical compatibility notes
   - `.obsidian/` directory references (factual)

4. **Service Name in Responses**:
   - Already correctly set to `"markdown-vault"` ✅

---

## Proposed Rebranding Changes

### Change Mapping Table

| Category | Current | Proposed | Files Affected |
|----------|---------|----------|----------------|
| **API Endpoint** | `/obsidian-local-rest-api.crt` | `/server.crt` (+ alias) | `src/markdown_vault/api/routes/system.py` |
| **Cert Filename** | `obsidian-local-rest-api.crt` | `markdown-vault.crt` | `src/markdown_vault/api/routes/system.py` |
| **Config File** | `obsidian-integration.example.yaml` | `obsidian-vault.example.yaml` | `config/` |
| **Doc File** | `MIGRATION_FROM_PLUGIN.md` | `OBSIDIAN_VAULT_COMPATIBILITY.md` | `docs/` |
| **Positioning** | "Drop-in replacement for Obsidian plugin" | "Obsidian-compatible markdown vault REST API" | All docs |
| **Primary Value** | "Replace the plugin" | "Standalone service with compatibility" | README.md |

### Terminology Changes

| Old Term | New Term | Context |
|----------|----------|---------|
| "Drop-in replacement for Obsidian Local REST API plugin" | "REST API server compatible with Obsidian Local REST API" | All documentation |
| "Replace the Obsidian plugin" | "Use with Obsidian vaults" | User guides |
| "Replacement mode" | "Obsidian vault mode" | Configuration docs |
| "Why replace the plugin?" | "Key advantages" | README.md |
| "Advantages over plugin" | (Remove section) | README.md |
| "Migration from plugin" | "Using with Obsidian vaults" | Guide title |

---

## Step-by-Step Rebranding Plan

### Phase 1: Core API Changes (Breaking Changes)

**Priority**: HIGH  
**Estimated Time**: 2-3 hours

1. **Update API endpoint** (`src/markdown_vault/api/routes/system.py`):
   ```python
   # Add new primary endpoint
   @router.get("/server.crt")
   async def get_ssl_certificate_new(...):
       return FileResponse(
           path=cert_path,
           filename="markdown-vault.crt",
           headers={"Content-Disposition": "attachment; filename=markdown-vault.crt"}
       )
   
   # Keep old endpoint as deprecated alias
   @router.get("/obsidian-local-rest-api.crt", deprecated=True)
   async def get_ssl_certificate_legacy(...):
       # Same implementation, different filename for compatibility
       return FileResponse(
           path=cert_path,
           filename="obsidian-local-rest-api.crt",  # Keep old name for compat
           headers={"Content-Disposition": "attachment; filename=obsidian-local-rest-api.crt"}
       )
   ```

2. **Update tests**:
   - Add tests for `/server.crt`
   - Keep backward compatibility tests for `/obsidian-local-rest-api.crt`
   - Update test docstrings

3. **Version bump**: `0.1.0` → `0.2.0` (minor version for new endpoint)

### Phase 2: Documentation Overhaul (Non-Breaking)

**Priority**: HIGH  
**Estimated Time**: 4-6 hours

1. **README.md** - Complete rewrite:
   - [ ] Update title/tagline
   - [ ] Rewrite overview section
   - [ ] Remove "Why Replace the Obsidian Plugin?" comparison table
   - [ ] Replace with "Key Advantages" section
   - [ ] Update "Advantages Over Plugin" → Remove or reframe
   - [ ] Update "Using with Obsidian Vaults" section
   - [ ] Keep Obsidian attribution in Credits

2. **docs/MIGRATION_FROM_PLUGIN.md** → **docs/OBSIDIAN_VAULT_COMPATIBILITY.md**:
   - [ ] Rename file
   - [ ] Reframe as "how to use with Obsidian" not "how to migrate"
   - [ ] Update all "replace" language to "use with"
   - [ ] Keep technical compatibility info

3. **docs/PROJECT_SUMMARY.md**:
   - [ ] Update project description
   - [ ] Change "drop-in replacement" to "compatible with"
   - [ ] Update positioning statements

4. **docs/PLAN.md**:
   - [ ] Update project goals
   - [ ] Reframe "Obsidian Integration Mode" section

5. **docs/MCP_TESTING.md**:
   - [ ] Update intro to emphasize compatibility testing
   - [ ] Keep technical details as-is

6. **docs/CONFIGURATION.md**:
   - [ ] Update Obsidian section intro
   - [ ] Clarify it's for compatibility, not replacement

7. **pyproject.toml**:
   - [ ] Update description
   - [ ] Update keywords

### Phase 3: Code Comments & Docstrings (Non-Breaking)

**Priority**: MEDIUM  
**Estimated Time**: 2-3 hours

1. **Update module docstrings**:
   - [ ] `src/markdown_vault/__init__.py`
   - [ ] `src/markdown_vault/__main__.py`
   - [ ] `src/markdown_vault/main.py`
   - [ ] `src/markdown_vault/utils/crypto.py`
   - [ ] `src/markdown_vault/models/note.py`
   - [ ] `src/markdown_vault/models/api.py`

2. **Update CLI help text**:
   - [ ] `__main__.py` argument help
   - [ ] `main.py` command descriptions

3. **Update configuration examples**:
   - [ ] `config/config.example.yaml` comments
   - [ ] Rename `config/obsidian-integration.example.yaml`

### Phase 4: Configuration Model (Optional)

**Priority**: LOW  
**Estimated Time**: 1-2 hours (if done)

**Decision Point**: Keep `ObsidianConfig` or rename to `CompatibilityConfig`?

**Recommendation**: **Keep as-is** to maintain clarity. The config section is explicitly for Obsidian vault compatibility features.

If renaming:
1. Update `src/markdown_vault/models/config.py`
2. Update all imports
3. Update tests
4. Add deprecation warnings for old YAML keys

### Phase 5: Backward Compatibility Strategy

**Priority**: HIGH  
**Estimated Time**: 1 hour

1. **Environment Variables**:
   - Keep all current `MARKDOWN_VAULT_*` variables (already white-label ✅)
   - No changes needed (clients use their own `OBSIDIAN_*` vars)

2. **API Endpoints**:
   - ✅ Keep `/obsidian-local-rest-api.crt` as deprecated alias
   - ✅ Add deprecation warning in API docs
   - ✅ Add `Deprecated: true` to OpenAPI spec

3. **Configuration Files**:
   - ✅ Keep `obsidian:` YAML key (not changing)
   - ✅ No breaking config changes

4. **Documentation**:
   - ✅ Add "Backward Compatibility" section to CHANGELOG
   - ✅ Document old endpoint still works

---

## Migration Guide for Existing Users

### For End Users

**Good News**: Minimal changes required!

1. **API Endpoint Change** (Optional):
   ```bash
   # Old endpoint (still works, deprecated)
   curl -k https://localhost:27123/obsidian-local-rest-api.crt
   
   # New endpoint (recommended)
   curl -k https://localhost:27123/server.crt
   ```

2. **Configuration**: No changes needed
   - All YAML config keys remain the same
   - All environment variables remain the same

3. **Documentation Updates**:
   - Updated positioning (no functional changes)
   - Clearer messaging about compatibility

### For Developers/Contributors

1. **Code Comments**: 
   - Use "compatible with Obsidian" instead of "drop-in replacement"
   - Focus on white-label nature

2. **New Features**:
   - Should not assume Obsidian-only usage
   - Design for generic markdown vaults first
   - Add Obsidian compatibility as enhancement

3. **Documentation**:
   - Emphasize markdown-vault as standalone tool
   - Mention Obsidian compatibility as feature, not primary identity

---

## Backward Compatibility Strategy

### Deprecation Timeline

| Version | Changes | Backward Compatibility |
|---------|---------|------------------------|
| **0.2.0** | Add `/server.crt`, mark `/obsidian-local-rest-api.crt` deprecated | Both endpoints work |
| **0.3.0** | Update all docs, no API changes | Both endpoints work |
| **1.0.0** | Major release with rebranding complete | Both endpoints work |
| **2.0.0** | (Future) Consider removing deprecated endpoint | Deprecation warnings |

### What Gets Deprecated?

1. **API Endpoint**: `/obsidian-local-rest-api.crt`
   - Status: Deprecated but functional
   - Timeline: Keep indefinitely (minimal cost)
   - Warning: Add to API docs and OpenAPI spec

2. **Nothing Else**: All other references are internal or documentation

### What Stays Compatible?

1. **All YAML configuration keys** ✅
2. **All environment variables** ✅
3. **All API endpoints** (except cert has new primary endpoint) ✅
4. **All response formats** ✅
5. **All request formats** ✅

**Result**: Existing users can upgrade without any changes!

---

## Documentation Update Strategy

### Primary Messaging Shift

**Before**: "We replace Obsidian's plugin"  
**After**: "We're a standalone REST API for markdown vaults with Obsidian compatibility"

### Documentation Hierarchy

1. **What is markdown-vault?**
   - Standalone REST API server for markdown vaults
   - Works with any markdown directory structure
   - Full Obsidian Local REST API compatibility

2. **When to use it?**
   - Programmatic access to markdown notes
   - Server/cloud deployment scenarios
   - Automation and integrations
   - Works great with Obsidian vaults

3. **How is Obsidian related?**
   - 100% compatible with Obsidian Local REST API specification
   - Can read Obsidian vault configurations
   - Supports `.obsidian/` directory conventions
   - Can be used with or without Obsidian installation

### Documentation Structure Updates

```
README.md
├── Overview (white-label focus)
├── Key Features (generic + Obsidian compat)
├── Quick Start
├── API Documentation
├── Advanced Features
│   ├── Obsidian Vault Compatibility (NEW SECTION)
│   ├── Periodic Notes
│   └── PATCH Operations
└── Credits (acknowledge Obsidian REST API)

docs/
├── OBSIDIAN_VAULT_COMPATIBILITY.md (renamed from MIGRATION_FROM_PLUGIN.md)
├── CONFIGURATION.md
├── PLAN.md (update positioning)
├── PROJECT_SUMMARY.md (update positioning)
└── RESEARCH.md (keep as-is, technical reference)
```

### Key Documentation Principles

1. **Lead with white-label**: markdown-vault is for markdown vaults (any structure)
2. **Obsidian as feature**: Compatibility is a feature, not the identity
3. **Focus on value**: What you can do, not what you're replacing
4. **Keep attribution**: Credit Obsidian REST API project in relevant sections
5. **Technical honesty**: In code/technical docs, be explicit about Obsidian compat

---

## Proposed New Positioning

### Tagline
**Before**: "Drop-in replacement for Obsidian Local REST API"  
**After**: "REST API server for markdown vaults with Obsidian compatibility"

### Elevator Pitch
```markdown
markdown-vault is a standalone REST API server for managing markdown notes and vaults. 
It provides a secure, reliable HTTP interface for programmatic access to your markdown 
files, with full compatibility with the Obsidian Local REST API specification.

Perfect for automation, integrations, server deployments, and any scenario where you 
need programmatic access to markdown content - whether you use Obsidian or not.
```

### Value Propositions (Reordered)

1. **Standalone Service**: Run anywhere - servers, containers, cloud
2. **Always Available**: 24/7 API access, independent of desktop applications
3. **Markdown-First**: Works with any markdown directory structure
4. **Obsidian Compatible**: Seamless integration with Obsidian vaults
5. **Automation Ready**: Perfect for scripts, workflows, and integrations
6. **Secure**: HTTPS with API key authentication
7. **Feature-Rich**: Periodic notes, advanced search, PATCH operations

---

## Implementation Checklist

### Pre-Implementation
- [ ] Review this plan with stakeholders
- [ ] Decide on `ObsidianConfig` rename (recommendation: keep as-is)
- [ ] Finalize new tagline and positioning
- [ ] Create backup branch

### Phase 1: API Changes (v0.2.0)

#### Phase 1a: API Endpoint Updates
- [ ] Add `/server.crt` endpoint with new filename
- [ ] Mark `/obsidian-local-rest-api.crt` as deprecated (but keep functional)
- [ ] Add deprecation warning to OpenAPI spec
- [ ] Update tests for both endpoints
- [ ] Add backward compatibility tests

#### Phase 1b: Environment Variable Documentation ✅ COMPLETE
- [x] Clarify server vs client environment variable distinction
- [x] Update `docs/MCP_TESTING.md` with clear explanations
- [x] Update `opencode.jsonc` with comments explaining client-side variables
- [x] Update `.env.example` with server vs client sections
- [x] Update `REBRANDING_PLAN.md` environment variables section
- [x] Document recommended `VAULT_*` naming for new integrations
- [x] Document `OBSIDIAN_*` as legacy/compatibility option

#### Phase 1c: Finalize
- [ ] Update CHANGELOG with Phase 1a and 1b changes

### Phase 2: Documentation (v0.2.0 or v0.3.0)
- [ ] Rewrite README.md
- [ ] Rename `MIGRATION_FROM_PLUGIN.md` → `OBSIDIAN_VAULT_COMPATIBILITY.md`
- [ ] Update `PROJECT_SUMMARY.md`
- [ ] Update `PLAN.md`
- [ ] Update `MCP_TESTING.md`
- [ ] Update `CONFIGURATION.md`
- [ ] Update `pyproject.toml`
- [ ] Rename `config/obsidian-integration.example.yaml`
- [ ] Update all doc cross-references

### Phase 3: Code Comments
- [ ] Update `src/markdown_vault/__init__.py`
- [ ] Update `src/markdown_vault/__main__.py`
- [ ] Update `src/markdown_vault/main.py`
- [ ] Update `src/markdown_vault/utils/crypto.py`
- [ ] Update `src/markdown_vault/models/note.py`
- [ ] Update `src/markdown_vault/models/api.py`
- [ ] Update `config/config.example.yaml`

### Phase 4: Testing & Validation
- [ ] Run full test suite
- [ ] Test backward compatibility
- [ ] Test with real Obsidian vault
- [ ] Test with generic markdown vault
- [ ] Validate API docs render correctly
- [ ] Check all internal links in documentation

### Phase 5: Release
- [ ] Update version to 0.2.0
- [ ] Generate comprehensive CHANGELOG
- [ ] Tag release
- [ ] Update any external references (if applicable)

---

## Risks & Mitigation

### Risk 1: Confusion Among Existing Users
**Risk**: Users who found markdown-vault as "Obsidian replacement" might be confused  
**Mitigation**: 
- Clear CHANGELOG explaining positioning change
- Backward compatibility maintained
- Update docs to clarify Obsidian compatibility remains 100%

### Risk 2: SEO/Discoverability Impact
**Risk**: Removing "Obsidian replacement" from docs might hurt discoverability  
**Mitigation**:
- Keep "Obsidian compatible" in descriptions
- Keep "obsidian" in package keywords
- Add "Obsidian Vault Compatibility" dedicated section
- Clear attribution to original Obsidian REST API project

### Risk 3: Breaking Changes
**Risk**: Users might rely on `/obsidian-local-rest-api.crt` endpoint  
**Mitigation**:
- Keep old endpoint as deprecated alias (indefinitely)
- Both endpoints functional
- Clear deprecation notice in docs

---

## Success Metrics

After rebranding, markdown-vault should be:

1. **Clearly positioned** as white-label solution ✅
2. **100% backward compatible** with existing deployments ✅
3. **Fully compatible** with Obsidian REST API spec ✅
4. **Documentation** emphasizes markdown-first, Obsidian-compatible nature ✅
5. **User-facing elements** free of Obsidian branding ✅
6. **Internal references** clearly marked as compatibility features ✅

---

## Recommended Next Steps

1. **Review this plan** - Get feedback on proposed changes
2. **Make decision** on `ObsidianConfig` rename (recommend: keep as-is)
3. **Create implementation branch** - `feature/rebrand-white-label`
4. **Start with Phase 1** - API changes (breaking but backward compatible)
5. **Follow with Phase 2** - Documentation overhaul
6. **Complete with Phase 3** - Code comment updates
7. **Test thoroughly** - Especially backward compatibility
8. **Release as v0.2.0** - Minor version bump for new endpoint

---

## Questions for Decision

1. **ObsidianConfig class**: Keep or rename to `CompatibilityConfig`?
   - **Recommendation**: Keep - it's explicitly for Obsidian compatibility

2. **Deprecation timeline**: Keep old endpoint forever or plan removal?
   - **Recommendation**: Keep indefinitely - minimal maintenance cost

3. **Documentation migration**: Update all at once or gradual?
   - **Recommendation**: All at once in v0.2.0 release

4. **Version numbering**: Release as 0.2.0 or 0.3.0?
   - **Recommendation**: 0.2.0 - it's a minor change with new endpoint

---

## Appendix: Complete File List

### Files Requiring Changes

**High Priority** (User-facing):
1. `src/markdown_vault/api/routes/system.py` - API endpoint
2. `README.md` - Complete rewrite
3. `docs/MIGRATION_FROM_PLUGIN.md` - Rename + reframe
4. `pyproject.toml` - Description + keywords
5. `config/obsidian-integration.example.yaml` - Rename + update

**Medium Priority** (Developer-facing):
6. `src/markdown_vault/__init__.py` - Docstring
7. `src/markdown_vault/__main__.py` - Help text
8. `src/markdown_vault/main.py` - Description
9. `docs/PROJECT_SUMMARY.md` - Positioning
10. `docs/PLAN.md` - Goals
11. `docs/CONFIGURATION.md` - Comments
12. `config/config.example.yaml` - Comments

**Low Priority** (Code comments):
13. `src/markdown_vault/utils/crypto.py` - Comment
14. `src/markdown_vault/models/note.py` - Comment
15. `src/markdown_vault/models/api.py` - Comment
16. `docs/MCP_TESTING.md` - Intro
17. All other doc files with minor references

**Test Files**:
18. `tests/test_api/test_system.py` - Update + add tests
19. Other test files - Update docstrings only

### Files Requiring Minimal/No Changes

**Keep As-Is** (Internal):
- `src/markdown_vault/models/config.py` - Keep `ObsidianConfig` class name
- `src/markdown_vault/core/config.py` - Internal implementation
- Test implementation files (only update docstrings)

**Keep As-Is** (Reference):
- `docs/RESEARCH.md` - Technical analysis of original API
- `docs/SESSION_COMPLETE.md` - Historical record
- `LICENSE` - No changes

**Keep As-Is** (Attribution):
- Credits section in README.md - Keep Obsidian attribution
- Links to original Obsidian REST API project

---

## Summary

This rebranding plan transforms markdown-vault from an "Obsidian plugin replacement" to a "white-label markdown vault REST API with Obsidian compatibility". 

**Key Principles**:
- ✅ Maintain 100% backward compatibility
- ✅ Keep 100% Obsidian REST API compatibility
- ✅ Remove Obsidian branding from user-facing elements
- ✅ Keep internal references for clarity
- ✅ Lead with white-label positioning
- ✅ Treat Obsidian compatibility as feature, not identity

**Impact**:
- Minimal breaking changes (one new primary endpoint)
- Major documentation updates
- Clear, honest positioning
- Better long-term sustainability as white-label solution

**Timeline**: 8-12 hours of focused work across 3 phases
