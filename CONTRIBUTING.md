# Contributing to markdown-vault

Thank you for your interest in contributing to markdown-vault! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- A markdown editor (optional but helpful)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/markdown-vault.git
   cd markdown-vault
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Copy example configuration**
   ```bash
   cp config/config.example.yaml config/config.yaml
   # Edit config.yaml with your settings
   ```

6. **Run tests to verify setup**
   ```bash
   pytest
   ```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or updates

### 2. Make Your Changes

- Write code following our style guidelines (see below)
- Add or update tests for your changes
- Update documentation as needed
- Keep commits focused and atomic

### 3. Run Tests and Linting

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=markdown_vault --cov-report=html

# Type checking
mypy src/markdown_vault

# Linting
ruff check src/

# Formatting
black src/ tests/
```

### 4. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add heading navigation to PATCH engine"
git commit -m "fix: correct frontmatter parsing for nested fields"
git commit -m "docs: update API documentation for periodic notes"
```

Commit types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Adding or updating tests
- `refactor:` - Code change that neither fixes a bug nor adds a feature
- `perf:` - Performance improvement
- `chore:` - Changes to build process or auxiliary tools

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Style

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Formatting**: Use Black for automatic formatting
- **Linting**: Use Ruff for linting
- **Type hints**: Required for all public APIs
- **Docstrings**: Required for all public modules, classes, and functions

Example:

```python
from typing import Optional

async def read_note(
    file_path: str,
    include_metadata: bool = False
) -> Optional[dict]:
    """
    Read a markdown note from the vault.
    
    Args:
        file_path: Path to the note relative to vault root
        include_metadata: Whether to include file metadata
        
    Returns:
        Dictionary containing note content and metadata, or None if not found
        
    Raises:
        ValueError: If file_path is invalid
        IOError: If file cannot be read
    """
    # Implementation here
    pass
```

### Type Hints

Use type hints throughout:

```python
from typing import Optional, List, Dict, Any
from pathlib import Path

def parse_frontmatter(content: str) -> Dict[str, Any]:
    """Parse YAML frontmatter from markdown content."""
    pass

async def list_notes(folder: Optional[Path] = None) -> List[str]:
    """List all notes in the specified folder."""
    pass
```

### Testing

- Write tests for all new functionality
- Maintain or improve code coverage (target: 90%+)
- Use descriptive test names
- Use fixtures for common test data

Example:

```python
import pytest
from markdown_vault.core.markdown_parser import parse_frontmatter

def test_parse_frontmatter_with_valid_yaml():
    """Test that valid YAML frontmatter is correctly parsed."""
    content = """---
title: Test Note
tags: [test, example]
---

# Content here
"""
    result = parse_frontmatter(content)
    
    assert result["title"] == "Test Note"
    assert result["tags"] == ["test", "example"]

@pytest.mark.asyncio
async def test_read_note_returns_none_for_missing_file(vault_manager):
    """Test that reading a non-existent note returns None."""
    result = await vault_manager.read_note("nonexistent.md")
    assert result is None
```

## Project Structure

Understanding the project structure helps you know where to make changes:

```
src/markdown_vault/
├── api/              # FastAPI routes and dependencies
│   └── routes/       # Individual route modules
├── core/             # Core business logic
├── models/           # Pydantic models
├── utils/            # Utility functions
└── cli/              # CLI commands
```

Add new features in the appropriate module:
- API endpoints → `api/routes/`
- Core logic → `core/`
- Data models → `models/`
- Helper functions → `utils/`

## Running the Development Server

```bash
# Start server with auto-reload
markdown-vault start --config config/config.yaml --reload

# Or use uvicorn directly for more control
uvicorn markdown_vault.main:app --reload --port 27123 --ssl-keyfile certs/server.key --ssl-certfile certs/server.crt
```

## Documentation

### Code Documentation

- All public APIs must have docstrings
- Use Google-style docstrings
- Include type information in docstrings
- Provide examples where helpful

### User Documentation

When adding new features, update:
- `README.md` - If it affects quick start or main features
- `docs/API.md` - For new API endpoints
- `docs/CONFIGURATION.md` - For new configuration options
- `CHANGELOG.md` - Document all changes

## Pull Request Process

1. **Ensure tests pass**: All tests must pass before PR is merged
2. **Maintain coverage**: Code coverage should not decrease
3. **Update documentation**: Include relevant documentation updates
4. **Describe changes**: Provide clear PR description
5. **Link issues**: Reference related issues with `Fixes #123`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] Tests pass locally
- [ ] Added/updated tests
- [ ] Updated documentation
- [ ] Code follows style guidelines
- [ ] No new warnings from linter
```

## Issue Reporting

### Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment (OS, Python version, etc.)
- Relevant logs or error messages

### Feature Requests

Include:
- Clear description of the feature
- Use case / motivation
- Proposed implementation (if you have ideas)
- Alternatives considered

## Development Tips

### Testing PATCH Operations

PATCH operations are complex. Test thoroughly:

```python
@pytest.fixture
def sample_note():
    return """---
tags: [example]
---

# Heading 1

Content here

## Subheading 1:1

More content

^block123
"""

def test_patch_append_to_heading(vault_manager, sample_note):
    """Test appending content to a specific heading."""
    result = vault_manager.patch_content(
        content=sample_note,
        operation="append",
        target_type="heading",
        target="Heading 1::Subheading 1:1",
        new_content="New paragraph"
    )
    
    assert "New paragraph" in result
    # More assertions...
```

### Debugging

Enable debug logging:

```yaml
# config.yaml
logging:
  level: "DEBUG"
  format: "text"  # More readable than JSON during debugging
```

Or use environment variable:
```bash
MARKDOWN_VAULT_LOG_LEVEL=DEBUG markdown-vault start
```

### Working with Obsidian Vaults

Create a test Obsidian vault:

```bash
mkdir -p tests/fixtures/test_vault
cd tests/fixtures/test_vault

# Create sample files
echo "# Test Note" > note1.md
echo "---\ntags: [test]\n---\n\n# Note 2" > note2.md

# Create .obsidian directory for integration testing
mkdir .obsidian
```

## Getting Help

- Check [PLAN.md](docs/PLAN.md) for implementation details
- Review [RESEARCH.md](docs/RESEARCH.md) for API specifications
- Ask questions in GitHub Discussions
- Join our community chat (link TBD)

## Code of Conduct

Be respectful, inclusive, and constructive. This is an open-source project and everyone is here to learn and contribute.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to markdown-vault!
