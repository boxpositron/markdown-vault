"""
Integration tests for active file API endpoints.
"""

from fastapi import status
from fastapi.testclient import TestClient


class TestOpenActiveFile:
    """Test POST /open/{filename} endpoint."""

    def test_open_requires_auth(self, test_app: TestClient) -> None:
        """Test that opening file requires authentication."""
        response = test_app.post("/open/simple.md")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_open_existing_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test opening an existing file sets it as active."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.post("/open/simple.md", headers=api_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify session cookie was set
        assert "session_id" in response.cookies

    def test_open_nonexistent_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test opening nonexistent file returns 404."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.post("/open/nonexistent.md", headers=api_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_open_nested_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test opening file in subdirectory."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.post("/open/notes/nested-note.md", headers=api_headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestGetActiveFile:
    """Test GET /active/ endpoint."""

    def test_get_active_requires_auth(self, test_app: TestClient) -> None:
        """Test that getting active file requires authentication."""
        response = test_app.get("/active/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_active_without_setting(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test getting active file without setting returns 404."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.get("/active/", headers=api_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No active file set" in response.json()["detail"]

    def test_get_active_markdown_format(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test getting active file in markdown format."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Set active file
        open_response = client.post("/open/simple.md", headers=api_headers)
        session_cookie = open_response.cookies.get("session_id")

        # Get active file
        response = client.get(
            "/active/",
            headers={**api_headers, "Accept": "text/markdown"},
            cookies={"session_id": session_cookie},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Simple Note" in response.text
        assert "text/markdown" in response.headers["content-type"]

    def test_get_active_json_format(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test getting active file in JSON format."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Set active file
        open_response = client.post("/open/with-frontmatter.md", headers=api_headers)
        session_cookie = open_response.cookies.get("session_id")

        # Get active file
        response = client.get(
            "/active/",
            headers={**api_headers, "Accept": "application/vnd.olrapi.note+json"},
            cookies={"session_id": session_cookie},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["path"] == "with-frontmatter.md"
        assert "content" in data
        assert "frontmatter" in data

    def test_session_persistence(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test that session persists across requests."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Set active file
        open_response = client.post("/open/simple.md", headers=api_headers)
        session_cookie = open_response.cookies.get("session_id")

        # Multiple requests with same session
        for _ in range(3):
            response = client.get(
                "/active/",
                headers=api_headers,
                cookies={"session_id": session_cookie},
            )
            assert response.status_code == status.HTTP_200_OK
            assert "Simple Note" in response.text


class TestUpdateActiveFile:
    """Test PUT /active/ endpoint."""

    def test_update_requires_auth(self, test_app: TestClient) -> None:
        """Test that updating active file requires authentication."""
        response = test_app.put("/active/", content=b"New content")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_without_active_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test updating without active file returns 404."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.put("/active/", headers=api_headers, content="New content")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_active_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test updating active file content."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Create and set active file
        client.put("/vault/test.md", headers=api_headers, content="Original")
        open_response = client.post("/open/test.md", headers=api_headers)
        session_cookie = open_response.cookies.get("session_id")

        # Update via active endpoint
        new_content = "# Updated Content\n\nThis is new."
        response = client.put(
            "/active/",
            headers=api_headers,
            content=new_content,
            cookies={"session_id": session_cookie},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify update
        response = client.get(
            "/active/",
            headers=api_headers,
            cookies={"session_id": session_cookie},
        )
        assert "Updated Content" in response.text
        assert "Original" not in response.text


class TestAppendToActiveFile:
    """Test POST /active/ endpoint."""

    def test_append_requires_auth(self, test_app: TestClient) -> None:
        """Test that appending to active file requires authentication."""
        response = test_app.post("/active/", content=b"Appended")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_append_without_active_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test appending without active file returns 404."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.post("/active/", headers=api_headers, content="Appended")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_append_to_active_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test appending to active file."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Create and set active file
        client.put("/vault/test.md", headers=api_headers, content="Original\n")
        open_response = client.post("/open/test.md", headers=api_headers)
        session_cookie = open_response.cookies.get("session_id")

        # Append via active endpoint
        response = client.post(
            "/active/",
            headers=api_headers,
            content="Appended\n",
            cookies={"session_id": session_cookie},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify both contents present
        response = client.get(
            "/active/",
            headers=api_headers,
            cookies={"session_id": session_cookie},
        )
        assert "Original" in response.text
        assert "Appended" in response.text


class TestPatchActiveFile:
    """Test PATCH /active/ endpoint."""

    def test_patch_requires_auth(self, test_app: TestClient) -> None:
        """Test that patching active file requires authentication."""
        response = test_app.patch("/active/", content=b"Patch")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_patch_not_implemented(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test that PATCH returns 501 not implemented."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Set active file
        open_response = client.post("/open/simple.md", headers=api_headers)
        session_cookie = open_response.cookies.get("session_id")

        # Try to patch
        response = client.patch(
            "/active/",
            headers=api_headers,
            content="Patch",
            cookies={"session_id": session_cookie},
        )
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED


class TestDeleteActiveFile:
    """Test DELETE /active/ endpoint."""

    def test_delete_requires_auth(self, test_app: TestClient) -> None:
        """Test that deleting active file requires authentication."""
        response = test_app.delete("/active/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_without_active_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test deleting without active file returns 404."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        response = client.delete("/active/", headers=api_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_active_file(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test deleting active file."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)
        client = TestClient(app)

        # Create and set active file
        client.put("/vault/to-delete.md", headers=api_headers, content="Delete me")
        open_response = client.post("/open/to-delete.md", headers=api_headers)
        session_cookie = open_response.cookies.get("session_id")

        # Delete via active endpoint
        response = client.delete(
            "/active/",
            headers=api_headers,
            cookies={"session_id": session_cookie},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify file is gone
        response = client.get("/vault/to-delete.md", headers=api_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify active file is cleared
        response = client.get(
            "/active/",
            headers=api_headers,
            cookies={"session_id": session_cookie},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestSessionIsolation:
    """Test that sessions are properly isolated."""

    def test_different_sessions_have_different_active_files(
        self, api_headers: dict[str, str], vault_with_fixtures
    ) -> None:
        """Test that different sessions maintain separate active files."""
        from markdown_vault.core.config import AppConfig, SecurityConfig, VaultConfig
        from markdown_vault.main import create_app

        config = AppConfig(
            vault=VaultConfig(path=str(vault_with_fixtures)),
            security=SecurityConfig(api_key="test-api-key-123"),
        )
        app = create_app(config)

        # Use two separate clients to simulate different sessions
        client1 = TestClient(app)
        client2 = TestClient(app)

        # Session 1 opens simple.md
        response1 = client1.post("/open/simple.md", headers=api_headers)
        session1_cookie = response1.cookies.get("session_id")

        # Session 2 opens with-frontmatter.md
        response2 = client2.post("/open/with-frontmatter.md", headers=api_headers)
        session2_cookie = response2.cookies.get("session_id")

        # Verify different cookies
        assert session1_cookie != session2_cookie

        # Verify session 1 gets simple.md
        response = client1.get(
            "/active/",
            headers=api_headers,
            cookies={"session_id": session1_cookie},
        )
        assert "Simple Note" in response.text

        # Verify session 2 gets with-frontmatter.md
        response = client2.get(
            "/active/",
            headers={**api_headers, "Accept": "application/vnd.olrapi.note+json"},
            cookies={"session_id": session2_cookie},
        )
        data = response.json()
        assert data["path"] == "with-frontmatter.md"
