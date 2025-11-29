# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Documentation (README, PLAN, RESEARCH)
- Configuration system design
- Docker deployment support
- Project planning and roadmap
- Obsidian vault compatibility guide

### Changed
- Updated project positioning to white-label approach
- Renamed MIGRATION_FROM_PLUGIN.md to OBSIDIAN_VAULT_COMPATIBILITY.md
- Renamed config/obsidian-integration.example.yaml to config/obsidian-vault.example.yaml
- Updated all documentation to use "compatible with" instead of "drop-in replacement"
- Reframed "Obsidian Integration Mode" as "Obsidian Compatibility Mode"
- Updated package keywords for better discoverability

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet

## [0.2.0] - 2025-11-29

### Changed
- **BREAKING**: Rebranding to white-label positioning
  - Project now emphasizes standalone nature with Obsidian compatibility as a feature
  - All documentation, code comments, and docstrings updated to use neutral, professional language
  - Version bumped from 0.1.0 to 0.2.0 across all files
  - API and functionality remain 100% compatible with previous versions
  - Updated module docstrings to use "compatible with Obsidian API" instead of "drop-in replacement"
  - Updated CLI help text and FastAPI descriptions to reflect white-label positioning

### Added
- OBSIDIAN_VAULT_COMPATIBILITY.md guide for using with Obsidian vaults
- Comprehensive rebranding plan documentation (REBRANDING_PLAN.md)

### Removed
- Migration-focused documentation (replaced with compatibility guide)

## [0.1.0] - TBD

Initial planning and design phase.
