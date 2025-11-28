"""
Integration tests for vault API endpoints.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestVaultListFiles:
    """Test GET /vault/ endpoint."""

    def test_list_files_requires_auth(self, test_app: TestClient) -> None:
        """Test that listing files requires authentication."""
        response = test_app.get("/vault/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_files_with_valid_auth(
        self, test_app: TestClient, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test listing files with valid authentication."""
        # Need to create app with fixtures vault
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.get("/vault/", headers=api_headers)
        assert response.status_code == status.HTTP_200_OK
        files = response.json()
        assert isinstance(files, list)
        assert "simple.md" in files
        assert "with-frontmatter.md" in files

    def test_list_files_sorted(
        self, test_app: TestClient, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test that files are returned in sorted order."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.get("/vault/", headers=api_headers)
        files = response.json()
        assert files == sorted(files)


class TestVaultReadFile:
    """Test GET /vault/{filepath} endpoint."""

    def test_read_file_requires_auth(
        self, test_app: TestClient, vault_with_fixtures
    ) -> None:
        """Test that reading files requires authentication."""
        response = test_app.get("/vault/simple.md")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_read_file_markdown_format(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test reading file in markdown format."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.get(
            "/vault/simple.md",
            headers={**api_headers, "Accept": "text/markdown"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Simple Note" in response.text
        assert "text/markdown" in response.headers["content-type"]

    def test_read_file_json_format(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test reading file in JSON format."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.get(
            "/vault/with-frontmatter.md",
            headers={**api_headers, "Accept": "application/vnd.olrapi.note+json"},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["path"] == "with-frontmatter.md"
        assert "content" in data
        assert "frontmatter" in data
        assert data["frontmatter"]["title"] == "Note with Frontmatter"
        assert "tags" in data
        assert "stat" in data
        assert "ctime" in data["stat"]
        assert "mtime" in data["stat"]
        assert "size" in data["stat"]

    def test_read_file_without_extension(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test reading file without .md extension."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.get("/vault/simple", headers=api_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "Simple Note" in response.text

    def test_read_nonexistent_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test reading nonexistent file returns 404."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.get("/vault/nonexistent.md", headers=api_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_read_nested_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test reading file in subdirectory."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.get("/vault/notes/nested-note.md", headers=api_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "Nested Note" in response.text


class TestVaultCreateFile:
    """Test PUT /vault/{filepath} endpoint."""

    def test_create_file_requires_auth(self, test_app: TestClient) -> None:
        """Test that creating files requires authentication."""
        response = test_app.put("/vault/new-file.md", content=b"# New File")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_simple_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test creating a simple file."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        content = "# New File\n\nThis is new content."
        response = client.put(
            "/vault/new-file.md", headers=api_headers, content=content
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify file was created
        response = client.get("/vault/new-file.md", headers=api_headers)
        assert response.status_code == status.HTTP_200_OK
        assert "New File" in response.text

    def test_update_existing_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test updating an existing file."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Create initial file
        client.put("/vault/test.md", headers=api_headers, content="Original")

        # Update it
        response = client.put("/vault/test.md", headers=api_headers, content="Updated")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify update
        response = client.get("/vault/test.md", headers=api_headers)
        assert "Updated" in response.text
        assert "Original" not in response.text

    def test_create_file_with_frontmatter(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test creating file with frontmatter."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        content = """---
title: Test Note
tags: [test]
---

# Content
"""
        response = client.put("/vault/with-fm.md", headers=api_headers, content=content)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify frontmatter was parsed
        response = client.get(
            "/vault/with-fm.md",
            headers={**api_headers, "Accept": "application/vnd.olrapi.note+json"},
        )
        data = response.json()
        assert data["frontmatter"]["title"] == "Test Note"

    def test_create_nested_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test creating file in subdirectory."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.put(
            "/vault/new/nested/file.md", headers=api_headers, content="# Nested"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify file was created
        response = client.get("/vault/new/nested/file.md", headers=api_headers)
        assert response.status_code == status.HTTP_200_OK


class TestVaultAppendFile:
    """Test POST /vault/{filepath} endpoint."""

    def test_append_requires_auth(self, test_app: TestClient) -> None:
        """Test that appending requires authentication."""
        response = test_app.post("/vault/test.md", content=b"Appended")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_append_to_existing_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test appending content to existing file."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Create initial file
        client.put("/vault/test.md", headers=api_headers, content="Original\n")

        # Append to it
        response = client.post(
            "/vault/test.md", headers=api_headers, content="Appended\n"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify both contents present
        response = client.get("/vault/test.md", headers=api_headers)
        assert "Original" in response.text
        assert "Appended" in response.text

    def test_append_to_nonexistent_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test appending to nonexistent file returns 404."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.post(
            "/vault/nonexistent.md", headers=api_headers, content="Content"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestVaultDeleteFile:
    """Test DELETE /vault/{filepath} endpoint."""

    def test_delete_requires_auth(self, test_app: TestClient) -> None:
        """Test that deleting files requires authentication."""
        response = test_app.delete("/vault/test.md")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_existing_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test deleting an existing file."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Create file
        client.put("/vault/to-delete.md", headers=api_headers, content="Delete me")

        # Delete it
        response = client.delete("/vault/to-delete.md", headers=api_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        response = client.get("/vault/to-delete.md", headers=api_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test deleting nonexistent file returns 404."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.delete("/vault/nonexistent.md", headers=api_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
