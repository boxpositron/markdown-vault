"""
Tests for system API routes.

Tests the following endpoints:
- GET / - Server status
- GET /openapi.yaml - OpenAPI specification
- GET /server.crt - SSL certificate download
- GET /obsidian-local-rest-api.crt - SSL certificate download (legacy compatibility)
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from tempfile import TemporaryDirectory

from markdown_vault.core.config import (
    AppConfig,
    SecurityConfig,
    ServerConfig,
    VaultConfig,
    LoggingConfig,
)
from markdown_vault.main import create_app


@pytest.fixture
def test_api_key() -> str:
    """Return a test API key."""
    return "test-api-key-12345"


@pytest.fixture
def test_cert_file(tmp_path: Path) -> Path:
    """Create a temporary certificate file for testing."""
    cert_path = tmp_path / "test-server.crt"
    # Create a mock certificate content
    cert_content = """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKL0UG+mRvSfMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMjUwMTAxMDAwMDAwWhcNMjYwMTAxMDAwMDAwWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEA0+example+certificate+content+here0DAQAB
-----END CERTIFICATE-----
"""
    cert_path.write_text(cert_content)
    return cert_path


@pytest.fixture
def test_vault_dir(tmp_path: Path) -> Path:
    """Create a temporary vault directory."""
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    return vault_dir


@pytest.fixture
def test_config(
    test_api_key: str, test_cert_file: Path, test_vault_dir: Path
) -> AppConfig:
    """Create test configuration."""
    return AppConfig(
        server=ServerConfig(
            host="127.0.0.1",
            port=27123,
            https=True,
            reload=False,
        ),
        security=SecurityConfig(
            api_key=test_api_key,
            cert_path=str(test_cert_file),
            key_path=str(test_cert_file.parent / "test-server.key"),
            auto_generate_cert=False,
        ),
        vault=VaultConfig(
            path=str(test_vault_dir),
            auto_create=False,
            watch_files=False,
            respect_gitignore=True,
        ),
        logging=LoggingConfig(
            level="DEBUG",
            format="json",
        ),
    )


@pytest.fixture
def client(test_config: AppConfig) -> TestClient:
    """Create a test client with the configured app."""
    app = create_app(test_config)
    return TestClient(app)


class TestServerStatus:
    """Tests for GET / endpoint."""

    def test_server_status_no_auth(self, client: TestClient) -> None:
        """Test server status endpoint without authentication."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] == "OK"
        assert data["service"] == "markdown-vault"
        assert data["authenticated"] is False
        assert "versions" in data
        assert data["versions"]["self"] == "0.2.0"
        assert data["versions"]["api"] == "1.0"

    def test_server_status_with_valid_auth(
        self, client: TestClient, test_api_key: str
    ) -> None:
        """Test server status endpoint with valid authentication."""
        response = client.get(
            "/",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] == "OK"
        assert data["service"] == "markdown-vault"
        assert data["authenticated"] is True
        assert "versions" in data

    def test_server_status_with_invalid_auth(self, client: TestClient) -> None:
        """Test server status endpoint with invalid authentication."""
        response = client.get(
            "/",
            headers={"Authorization": "Bearer invalid-key"},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] == "OK"
        assert data["authenticated"] is False

    def test_server_status_with_direct_key(
        self, client: TestClient, test_api_key: str
    ) -> None:
        """Test server status endpoint with direct API key (no Bearer prefix)."""
        response = client.get(
            "/",
            headers={"Authorization": test_api_key},
        )
        assert response.status_code == 200

        data = response.json()
        assert data["authenticated"] is True

    def test_server_status_response_model(self, client: TestClient) -> None:
        """Test server status response follows ServerStatus model."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        # Check all required fields are present
        assert "ok" in data
        assert "service" in data
        assert "authenticated" in data
        assert "versions" in data
        assert isinstance(data["versions"], dict)


class TestOpenAPISpec:
    """Tests for GET /openapi.yaml endpoint."""

    def test_openapi_spec_requires_auth(self, client: TestClient) -> None:
        """Test that OpenAPI spec endpoint requires authentication."""
        response = client.get("/openapi.yaml")
        assert response.status_code == 401

    def test_openapi_spec_with_valid_auth(
        self, client: TestClient, test_api_key: str
    ) -> None:
        """Test OpenAPI spec endpoint with valid authentication."""
        response = client.get(
            "/openapi.yaml",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/yaml"

        # Check that the response is valid YAML
        content = response.text
        assert "openapi:" in content or "swagger:" in content
        assert "paths:" in content
        assert "info:" in content

    def test_openapi_spec_with_invalid_auth(self, client: TestClient) -> None:
        """Test OpenAPI spec endpoint with invalid authentication."""
        response = client.get(
            "/openapi.yaml",
            headers={"Authorization": "Bearer invalid-key"},
        )
        assert response.status_code == 401

    def test_openapi_spec_contains_system_endpoints(
        self, client: TestClient, test_api_key: str
    ) -> None:
        """Test that OpenAPI spec contains system endpoints."""
        response = client.get(
            "/openapi.yaml",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 200

        content = response.text
        # Check for system endpoints in the spec
        assert "/" in content or "paths" in content
        assert "openapi.yaml" in content or "paths" in content


class TestSSLCertificate:
    """Tests for GET /server.crt endpoint (primary)."""

    def test_certificate_download_requires_auth(self, client: TestClient) -> None:
        """Test that certificate download requires authentication."""
        response = client.get("/server.crt")
        assert response.status_code == 401

    def test_certificate_download_with_valid_auth(
        self, client: TestClient, test_api_key: str
    ) -> None:
        """Test certificate download with valid authentication."""
        response = client.get(
            "/server.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-pem-file"
        assert (
            "attachment; filename=markdown-vault.crt"
            in response.headers["content-disposition"]
        )

        # Check certificate content
        content = response.text
        assert "BEGIN CERTIFICATE" in content
        assert "END CERTIFICATE" in content

    def test_certificate_download_with_invalid_auth(self, client: TestClient) -> None:
        """Test certificate download with invalid authentication."""
        response = client.get(
            "/server.crt",
            headers={"Authorization": "Bearer invalid-key"},
        )
        assert response.status_code == 401


class TestSSLCertificateLegacy:
    """Tests for GET /obsidian-local-rest-api.crt endpoint (deprecated)."""

    def test_legacy_certificate_download_requires_auth(
        self, client: TestClient
    ) -> None:
        """Test that legacy certificate download requires authentication."""
        response = client.get("/obsidian-local-rest-api.crt")
        assert response.status_code == 401

    def test_legacy_certificate_download_with_valid_auth(
        self, client: TestClient, test_api_key: str
    ) -> None:
        """Test legacy certificate download with valid authentication."""
        response = client.get(
            "/obsidian-local-rest-api.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/x-pem-file"
        assert (
            "attachment; filename=obsidian-local-rest-api.crt"
            in response.headers["content-disposition"]
        )

        # Check certificate content
        content = response.text
        assert "BEGIN CERTIFICATE" in content
        assert "END CERTIFICATE" in content

    def test_legacy_certificate_download_with_invalid_auth(
        self, client: TestClient
    ) -> None:
        """Test legacy certificate download with invalid authentication."""
        response = client.get(
            "/obsidian-local-rest-api.crt",
            headers={"Authorization": "Bearer invalid-key"},
        )
        assert response.status_code == 401

    def test_both_endpoints_return_same_content(
        self, client: TestClient, test_api_key: str
    ) -> None:
        """Test that both new and legacy endpoints return the same certificate content."""
        headers = {"Authorization": f"Bearer {test_api_key}"}

        # Get certificate from new endpoint
        new_response = client.get("/server.crt", headers=headers)
        assert new_response.status_code == 200

        # Get certificate from legacy endpoint
        legacy_response = client.get("/obsidian-local-rest-api.crt", headers=headers)
        assert legacy_response.status_code == 200

        # Both should return the same certificate content
        assert new_response.text == legacy_response.text
        assert "BEGIN CERTIFICATE" in new_response.text
        assert "END CERTIFICATE" in new_response.text

    def test_certificate_not_found(
        self, test_api_key: str, test_vault_dir: Path
    ) -> None:
        """Test certificate download when file doesn't exist."""
        # Create config with non-existent certificate path
        config = AppConfig(
            server=ServerConfig(
                host="127.0.0.1",
                port=27123,
                https=True,
                reload=False,
            ),
            security=SecurityConfig(
                api_key=test_api_key,
                cert_path="/nonexistent/path/cert.crt",
                key_path="/nonexistent/path/key.key",
                auto_generate_cert=False,
            ),
            vault=VaultConfig(
                path=str(test_vault_dir),
                auto_create=False,
                watch_files=False,
                respect_gitignore=True,
            ),
            logging=LoggingConfig(
                level="DEBUG",
                format="json",
            ),
        )

        app = create_app(config)
        client = TestClient(app)

        response = client.get(
            "/server.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 404

    def test_certificate_path_not_configured(
        self, test_api_key: str, test_vault_dir: Path
    ) -> None:
        """Test certificate download when path is not configured."""
        # Create config with empty certificate path
        config = AppConfig(
            server=ServerConfig(
                host="127.0.0.1",
                port=27123,
                https=True,
                reload=False,
            ),
            security=SecurityConfig(
                api_key=test_api_key,
                cert_path="",  # Empty path
                key_path="",
                auto_generate_cert=False,
            ),
            vault=VaultConfig(
                path=str(test_vault_dir),
                auto_create=False,
                watch_files=False,
                respect_gitignore=True,
            ),
            logging=LoggingConfig(
                level="DEBUG",
                format="json",
            ),
        )

        app = create_app(config)
        client = TestClient(app)

        response = client.get(
            "/server.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 500

    def test_certificate_path_is_directory(
        self, test_api_key: str, test_vault_dir: Path, tmp_path: Path
    ) -> None:
        """Test certificate download when path is a directory instead of a file."""
        # Create a directory instead of a file
        cert_dir = tmp_path / "cert_dir"
        cert_dir.mkdir()

        config = AppConfig(
            server=ServerConfig(
                host="127.0.0.1",
                port=27123,
                https=True,
                reload=False,
            ),
            security=SecurityConfig(
                api_key=test_api_key,
                cert_path=str(cert_dir),
                key_path=str(tmp_path / "key.key"),
                auto_generate_cert=False,
            ),
            vault=VaultConfig(
                path=str(test_vault_dir),
                auto_create=False,
                watch_files=False,
                respect_gitignore=True,
            ),
            logging=LoggingConfig(
                level="DEBUG",
                format="json",
            ),
        )

        app = create_app(config)
        client = TestClient(app)

        response = client.get(
            "/server.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 500


class TestCertificateBackwardCompatibility:
    """Tests for backward compatibility between certificate endpoints."""

    def test_legacy_endpoint_not_found(
        self, test_api_key: str, test_vault_dir: Path
    ) -> None:
        """Test legacy certificate endpoint when file doesn't exist."""
        config = AppConfig(
            server=ServerConfig(
                host="127.0.0.1",
                port=27123,
                https=True,
                reload=False,
            ),
            security=SecurityConfig(
                api_key=test_api_key,
                cert_path="/nonexistent/path/cert.crt",
                key_path="/nonexistent/path/key.key",
                auto_generate_cert=False,
            ),
            vault=VaultConfig(
                path=str(test_vault_dir),
                auto_create=False,
                watch_files=False,
                respect_gitignore=True,
            ),
            logging=LoggingConfig(
                level="DEBUG",
                format="json",
            ),
        )

        app = create_app(config)
        client = TestClient(app)

        response = client.get(
            "/obsidian-local-rest-api.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 404

    def test_legacy_endpoint_path_not_configured(
        self, test_api_key: str, test_vault_dir: Path
    ) -> None:
        """Test legacy certificate endpoint when path is not configured."""
        config = AppConfig(
            server=ServerConfig(
                host="127.0.0.1",
                port=27123,
                https=True,
                reload=False,
            ),
            security=SecurityConfig(
                api_key=test_api_key,
                cert_path="",
                key_path="",
                auto_generate_cert=False,
            ),
            vault=VaultConfig(
                path=str(test_vault_dir),
                auto_create=False,
                watch_files=False,
                respect_gitignore=True,
            ),
            logging=LoggingConfig(
                level="DEBUG",
                format="json",
            ),
        )

        app = create_app(config)
        client = TestClient(app)

        response = client.get(
            "/obsidian-local-rest-api.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 500

    def test_legacy_endpoint_path_is_directory(
        self, test_api_key: str, test_vault_dir: Path, tmp_path: Path
    ) -> None:
        """Test legacy certificate endpoint when path is a directory."""
        cert_dir = tmp_path / "cert_dir"
        cert_dir.mkdir()

        config = AppConfig(
            server=ServerConfig(
                host="127.0.0.1",
                port=27123,
                https=True,
                reload=False,
            ),
            security=SecurityConfig(
                api_key=test_api_key,
                cert_path=str(cert_dir),
                key_path=str(tmp_path / "key.key"),
                auto_generate_cert=False,
            ),
            vault=VaultConfig(
                path=str(test_vault_dir),
                auto_create=False,
                watch_files=False,
                respect_gitignore=True,
            ),
            logging=LoggingConfig(
                level="DEBUG",
                format="json",
            ),
        )

        app = create_app(config)
        client = TestClient(app)

        response = client.get(
            "/obsidian-local-rest-api.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 500


class TestSystemIntegration:
    """Integration tests for system endpoints."""

    def test_all_endpoints_accessible(
        self, client: TestClient, test_api_key: str
    ) -> None:
        """Test that all system endpoints are accessible."""
        # Test status endpoint (no auth)
        response = client.get("/")
        assert response.status_code == 200

        # Test OpenAPI spec (with auth)
        response = client.get(
            "/openapi.yaml",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 200

        # Test new certificate download endpoint (with auth)
        response = client.get(
            "/server.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 200

        # Test legacy certificate download endpoint (with auth)
        response = client.get(
            "/obsidian-local-rest-api.crt",
            headers={"Authorization": f"Bearer {test_api_key}"},
        )
        assert response.status_code == 200

    def test_health_check_endpoint(self, client: TestClient) -> None:
        """Test that health check endpoint still works."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.2.0"
