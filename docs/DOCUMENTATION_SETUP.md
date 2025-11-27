# Documentation Architecture Setup

**Date**: November 27, 2025  
**Project**: markdown-vault  
**Configuration**: `.withcontextconfig.jsonc`

## Overview

This document explains the documentation architecture for markdown-vault, following the **Diátaxis framework** and documentation best practices.

## Documentation Philosophy

### LOCAL (Repository) = Essential & Self-Contained

**Purpose**: Files critical for getting started, must work without vault access

**Characteristics**:
- Quick to read (1-10 minutes)
- Self-contained (no dependencies on vault)
- Essential for onboarding
- Version controlled with code
- Accessible to anyone who clones the repo

**Examples in markdown-vault**:
- `README.md` - Project overview, installation, quick start
- `CONTRIBUTING.md` - How to contribute
- `STATUS.md` - Current project status
- `config/*.yaml` - Configuration examples
- `src/**/README.md` - Component documentation
- Quick reference guides

### VAULT (Obsidian) = Deep Research & Exploration

**Purpose**: Detailed exploration, architecture decisions, research notes

**Characteristics**:
- In-depth content (10+ minutes to read)
- Interconnected with other knowledge
- Research and decision history
- Can evolve independently of code
- Benefits from Obsidian's linking and graph

**Examples in markdown-vault**:
- `docs/RESEARCH.md` - Complete API analysis (13KB)
- `docs/PLAN.md` - Detailed implementation plan (23KB)
- `docs/PROJECT_SUMMARY.md` - Executive summary
- Future: API docs, architecture decisions, guides

## Diátaxis Framework Application

The Diátaxis framework organizes documentation into four types:

### 1. Tutorials (Learning-Oriented) → VAULT

**Location**: `docs/tutorials/`

**Purpose**: Help newcomers learn by doing

**Examples for markdown-vault**:
- Building your first markdown vault API client
- Creating custom PATCH operations
- Setting up Obsidian integration

### 2. How-To Guides (Task-Oriented) → VAULT

**Location**: `docs/guides/`

**Purpose**: Solve specific problems

**Examples for markdown-vault**:
- How to configure periodic notes
- How to secure your vault API
- How to deploy with Docker
- How to integrate with Obsidian

### 3. Reference (Information-Oriented) → VAULT + LOCAL

**VAULT**: `docs/reference/`, `docs/API.md`  
**LOCAL**: Quick reference cards, `docs/quick-reference.md`

**Purpose**: Provide accurate technical information

**Examples for markdown-vault**:
- Complete API endpoint reference (vault)
- Configuration option reference (vault)
- Quick reference card (local, 1-2 pages)

### 4. Explanation (Understanding-Oriented) → VAULT

**Location**: `docs/architecture/`, `docs/design/`

**Purpose**: Clarify and illuminate topics

**Examples for markdown-vault**:
- Why we chose FastAPI over Express
- Architecture decisions (ADRs)
- PATCH engine design philosophy
- Security model explanation

## Current Documentation Status

### Files Created (All LOCAL)

```
markdown-vault/
├── README.md                     ✅ LOCAL - Self-contained overview
├── STATUS.md                     ✅ LOCAL - Project status
├── CONTRIBUTING.md               ✅ LOCAL - Contribution guide
├── CHANGELOG.md                  🔄 VAULT - Detailed history
├── LICENSE                       ✅ LOCAL - Legal requirement
│
├── docs/
│   ├── RESEARCH.md               🔄 VAULT - Deep API analysis
│   ├── PLAN.md                   🔄 VAULT - Detailed roadmap
│   └── PROJECT_SUMMARY.md        🔄 VAULT - Executive summary
│
└── config/
    ├── config.example.yaml       ✅ LOCAL - Stays with code
    └── obsidian-integration.example.yaml  ✅ LOCAL
```

✅ = Stays LOCAL (repository)  
🔄 = Moves to VAULT (Obsidian) when synced

### README Health Analysis

**Current Status**: ✅ **HEALTHY** (Self-Contained)

**Strengths**:
- ✅ Clear project description
- ✅ Installation instructions
- ✅ Quick start section
- ✅ Configuration examples
- ✅ API overview
- ✅ No broken links to vault files
- ✅ Self-contained (works without vault)

**Recommendations**:
- Consider adding badges (build status, version, license)
- Could add a "Status" section linking to STATUS.md
- Consider adding "Contributing" section with link to CONTRIBUTING.md

### Files That Will Move to Vault

When you run `/sync-notes` or `/ingest-notes`, these files will be delegated:

1. **RESEARCH.md** (13KB)
   - Comprehensive API analysis
   - Technical specifications
   - Implementation details

2. **PLAN.md** (23KB)
   - 6-phase implementation roadmap
   - Detailed architecture
   - Timeline and milestones

3. **PROJECT_SUMMARY.md** (8KB)
   - Executive overview
   - Documentation index
   - Status tracking

4. **CHANGELOG.md**
   - Detailed change history
   - Version notes

These files are perfect for vault delegation because:
- They're deep research/planning documents
- They benefit from Obsidian's linking and graph
- They'll evolve with the project
- They're not needed for quick onboarding

## Configuration Details

### .withcontextconfig.jsonc Structure

```jsonc
{
  "version": "2.1",
  "defaultBehavior": "local",  // Safe default: keep in repo unless specified
  
  "vault": [
    // Files that move to Obsidian vault
    "docs/RESEARCH.md",
    "docs/PLAN.md",
    "docs/PROJECT_SUMMARY.md",
    "CHANGELOG.md",
    // ... and patterns for future docs
  ],
  
  "local": [
    // Files that stay in repository
    "/README.md",
    "/CONTRIBUTING.md",
    "/STATUS.md",
    "config/**",
    "src/**/README.md",
    // ... essential repository files
  ],
  
  "conflictResolution": "local-wins"  // When in doubt, keep local
}
```

## Recommended Vault Folder Structure

When you sync documentation to vault, create this structure:

```
vault/projects/markdown-vault/
├── index.md                      # Project hub (links to all docs)
│
├── research/
│   └── obsidian-api-analysis.md  # From RESEARCH.md
│
├── planning/
│   ├── implementation-plan.md    # From PLAN.md
│   └── project-summary.md        # From PROJECT_SUMMARY.md
│
├── guides/                       # Future how-to guides
│   ├── configuration-guide.md
│   ├── deployment-guide.md
│   └── obsidian-integration.md
│
├── tutorials/                    # Future tutorials
│   └── getting-started.md
│
├── reference/                    # Future API reference
│   ├── api-endpoints.md
│   └── configuration-options.md
│
├── architecture/                 # Future design docs
│   ├── decisions/                # ADRs
│   └── design-philosophy.md
│
└── changelog.md                  # From CHANGELOG.md
```

## Next Steps

### 1. Review Configuration

```bash
# Validate the configuration
cat .withcontextconfig.jsonc
```

### 2. Preview What Will Move

Use with-context commands to preview:

```bash
# Preview which files will be delegated (if command available)
# This would show RESEARCH.md, PLAN.md, PROJECT_SUMMARY.md, CHANGELOG.md
```

### 3. Sync to Vault (When Ready)

```bash
# Sync files to vault
# /sync-notes

# Or copy to vault and delete local copies
# /ingest-notes --delete
```

### 4. Create Vault Structure

Organize documentation in vault:
- Create folder structure
- Create index/hub note
- Link documents together
- Add tags and metadata

### 5. Keep README Self-Contained

**Critical**: README.md must always work without vault access!

**Never link from README to vault files**:
```markdown
<!-- ❌ BAD - Link will break when file moves to vault -->
See [detailed plan](docs/PLAN.md) for implementation details.

<!-- ✅ GOOD - Link to file that stays local -->
See [contributing guide](CONTRIBUTING.md) for how to help.

<!-- ✅ GOOD - External link -->
See our [detailed documentation](https://docs.markdown-vault.io) for more info.
```

## Best Practices

### For Repository Documentation (LOCAL)

1. **Keep it concise**: 1-10 minutes to read
2. **Self-contained**: No dependencies on vault
3. **Version controlled**: Committed with code
4. **Quick reference**: Getting started, quick wins
5. **No broken links**: Only link to files that stay local

### For Vault Documentation

1. **Go deep**: 10+ minutes, comprehensive coverage
2. **Interconnected**: Link to related vault notes
3. **Evolving**: Can change independently of code
4. **Discoverable**: Use tags, graphs, backlinks
5. **Organized**: Follow Diátaxis framework

### Migration Guidelines

When moving docs to vault:
1. Update README if it linked to moved files
2. Consider creating brief summary in repo
3. Add "See vault for detailed docs" note if needed
4. Ensure vault docs link back to repo README

## Tools & Commands

### with-context MCP Commands

- `/setup-notes` - Initialize configuration (already done!)
- `/validate-config` - Validate .withcontextconfig.jsonc
- `/preview-delegation` - See what will move to vault
- `/sync-notes` - Bidirectional sync
- `/ingest-notes` - Copy to vault (optionally delete local)
- `/teleport-notes` - Download from vault to local

## References

- **Diátaxis Framework**: https://diataxis.fr/
- **with-context MCP**: Configuration for documentation delegation
- **Architecture Decision Records**: Michael Nygard's ADR format
- **Docs-as-Code**: https://www.writethedocs.org/guide/docs-as-code/

---

**Configuration Status**: ✅ Ready  
**README Status**: ✅ Self-Contained  
**Next Step**: Review configuration and sync when ready
