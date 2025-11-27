"""
Tests for configuration loading and management.
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from markdown_vault.core.config import (
    ConfigError,
    generate_api_key,
    load_api_key_from_file,
    load_config,
    load_yaml_config,
    merge_env_overrides,
    resolve_api_key,
)
from markdown_vault.models.config import AppConfig, SecurityConfig, VaultConfig


class TestAPIKeyGeneration:
    """Test API key generation."""

    def test_generate_api_key(self):
        """Test API key generation."""
        key = generate_api_key()
        assert isinstance(key, str)
        assert len(key) == 64  # 32 bytes as hex = 64 characters
        assert all(c in "0123456789abcdef" for c in key)

    def test_generate_unique_keys(self):
        """Test that generated keys are unique."""
        key1 = generate_api_key()
        key2 = generate_api_key()
        assert key1 != key2


class TestAPIKeyFromFile:
    """Test loading API key from file."""

    def test_load_api_key_from_file(self, tmp_path):
        """Test loading API key from file."""
        key_file = tmp_path / "api_key.txt"
        test_key = "test-api-key-12345"
        key_file.write_text(test_key)

        loaded_key = load_api_key_from_file(str(key_file))
        assert loaded_key == test_key

    def test_load_api_key_strips_whitespace(self, tmp_path):
        """Test that loaded API key has whitespace stripped."""
        key_file = tmp_path / "api_key.txt"
        test_key = "test-api-key-12345"
        key_file.write_text(f"\n  {test_key}  \n")

        loaded_key = load_api_key_from_file(str(key_file))
        assert loaded_key == test_key

    def test_load_api_key_file_not_found(self):
        """Test error when API key file not found."""
        with pytest.raises(ConfigError, match="not found"):
            load_api_key_from_file("/nonexistent/api_key.txt")

    def test_load_api_key_empty_file(self, tmp_path):
        """Test error when API key file is empty."""
        key_file = tmp_path / "api_key.txt"
        key_file.write_text("")

        with pytest.raises(ConfigError, match="empty"):
            load_api_key_from_file(str(key_file))


class TestYAMLConfigLoading:
    """Test YAML configuration loading."""

    def test_load_valid_yaml_config(self, tmp_path):
        """Test loading valid YAML config."""
        config_file = tmp_path / "config.yaml"
        config_data = {
            "server": {"host": "0.0.0.0", "port": 8080},
            "vault": {"path": "/test/vault"},
        }
        config_file.write_text(yaml.dump(config_data))

        loaded = load_yaml_config(config_file)
        assert loaded["server"]["host"] == "0.0.0.0"
        assert loaded["server"]["port"] == 8080
        assert loaded["vault"]["path"] == "/test/vault"

    def test_load_yaml_file_not_found(self):
        """Test error when YAML file not found."""
        with pytest.raises(ConfigError, match="not found"):
            load_yaml_config(Path("/nonexistent/config.yaml"))

    def test_load_empty_yaml_file(self, tmp_path):
        """Test error when YAML file is empty."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        with pytest.raises(ConfigError, match="empty"):
            load_yaml_config(config_file)

    def test_load_invalid_yaml(self, tmp_path):
        """Test error when YAML is invalid."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ConfigError, match="Failed to parse"):
            load_yaml_config(config_file)


class TestEnvironmentOverrides:
    """Test environment variable override merging."""

    def test_merge_simple_overrides(self, monkeypatch):
        """Test merging simple environment overrides."""
        monkeypatch.setenv("MARKDOWN_VAULT_SERVER__PORT", "9090")
        monkeypatch.setenv("MARKDOWN_VAULT_SERVER__HOST", "0.0.0.0")

        config_data = {"server": {"port": 8080, "host": "127.0.0.1"}}
        merged = merge_env_overrides(config_data)

        assert merged["server"]["port"] == 9090
        assert merged["server"]["host"] == "0.0.0.0"

    def test_merge_boolean_overrides(self, monkeypatch):
        """Test merging boolean environment overrides."""
        monkeypatch.setenv("MARKDOWN_VAULT_SERVER__HTTPS", "false")
        monkeypatch.setenv("MARKDOWN_VAULT_VAULT__AUTO_CREATE", "true")

        config_data = {}
        merged = merge_env_overrides(config_data)

        assert merged["server"]["https"] is False
        assert merged["vault"]["auto_create"] is True

    def test_merge_null_overrides(self, monkeypatch):
        """Test merging null environment overrides."""
        monkeypatch.setenv("MARKDOWN_VAULT_SECURITY__API_KEY", "null")

        config_data = {"security": {"api_key": "existing"}}
        merged = merge_env_overrides(config_data)

        assert merged["security"]["api_key"] is None

    def test_merge_creates_new_sections(self, monkeypatch):
        """Test that env overrides create new sections if needed."""
        monkeypatch.setenv("MARKDOWN_VAULT_CUSTOM__VALUE", "test")

        config_data = {}
        merged = merge_env_overrides(config_data)

        assert "custom" in merged
        assert merged["custom"]["value"] == "test"

    def test_merge_ignores_non_prefixed_vars(self, monkeypatch):
        """Test that non-prefixed env vars are ignored."""
        monkeypatch.setenv("RANDOM_VAR", "value")
        monkeypatch.setenv("SERVER__PORT", "9999")

        config_data = {"server": {"port": 8080}}
        merged = merge_env_overrides(config_data)

        assert merged["server"]["port"] == 8080


class TestAPIKeyResolution:
    """Test API key resolution logic."""

    def test_resolve_direct_api_key(self):
        """Test resolving direct API key."""
        config = SecurityConfig(api_key="direct-key")
        resolved = resolve_api_key(config)
        assert resolved == "direct-key"

    def test_resolve_api_key_from_file(self, tmp_path):
        """Test resolving API key from file."""
        key_file = tmp_path / "api_key.txt"
        key_file.write_text("file-key")

        config = SecurityConfig(api_key=None, api_key_file=str(key_file))
        resolved = resolve_api_key(config)
        assert resolved == "file-key"

    def test_resolve_generates_key_when_none(self, capsys):
        """Test that a key is generated when none provided."""
        config = SecurityConfig(api_key=None, api_key_file=None)
        resolved = resolve_api_key(config)

        assert isinstance(resolved, str)
        assert len(resolved) == 64

        # Check that message was printed
        captured = capsys.readouterr()
        assert "Generated new API key" in captured.out

    def test_resolve_prefers_direct_over_file(self, tmp_path):
        """Test that direct API key is preferred over file."""
        key_file = tmp_path / "api_key.txt"
        key_file.write_text("file-key")

        config = SecurityConfig(api_key="direct-key", api_key_file=str(key_file))
        resolved = resolve_api_key(config)
        assert resolved == "direct-key"


class TestFullConfigLoading:
    """Test complete configuration loading."""

    def test_load_config_from_yaml(self, tmp_path):
        """Test loading complete config from YAML."""
        config_file = tmp_path / "config.yaml"
        vault_path = tmp_path / "vault"

        config_data = {
            "server": {"host": "0.0.0.0", "port": 8080, "https": False},
            "vault": {"path": str(vault_path), "auto_create": True},
            "security": {"api_key": "test-key"},
        }
        config_file.write_text(yaml.dump(config_data))

        config = load_config(str(config_file))

        assert config.server.host == "0.0.0.0"
        assert config.server.port == 8080
        assert config.server.https is False
        assert config.vault.path == str(vault_path)
        assert config.security.api_key == "test-key"

    def test_load_config_with_env_override(self, tmp_path, monkeypatch):
        """Test loading config with environment override."""
        config_file = tmp_path / "config.yaml"
        vault_path = tmp_path / "vault"

        config_data = {
            "server": {"port": 8080},
            "vault": {"path": str(vault_path)},
            "security": {"api_key": "yaml-key"},
        }
        config_file.write_text(yaml.dump(config_data))

        monkeypatch.setenv("MARKDOWN_VAULT_SERVER__PORT", "9090")

        config = load_config(str(config_file))

        assert config.server.port == 9090
        assert config.security.api_key == "yaml-key"

    def test_load_config_without_yaml(self, tmp_path, monkeypatch):
        """Test loading config without YAML file (env vars only)."""
        vault_path = tmp_path / "vault"

        monkeypatch.setenv("MARKDOWN_VAULT_VAULT__PATH", str(vault_path))
        monkeypatch.setenv("MARKDOWN_VAULT_SERVER__HTTPS", "false")

        config = load_config()

        assert config.vault.path == str(vault_path)
        assert config.server.https is False

    def test_load_config_validation_error(self, tmp_path):
        """Test that validation errors are caught."""
        config_file = tmp_path / "config.yaml"

        # Invalid port number
        config_data = {
            "server": {"port": 99999},
            "vault": {"path": str(tmp_path)},
        }
        config_file.write_text(yaml.dump(config_data))

        with pytest.raises(ConfigError, match="validation failed"):
            load_config(str(config_file))

    def test_load_config_auto_creates_vault(self, tmp_path):
        """Test that vault directory is auto-created."""
        config_file = tmp_path / "config.yaml"
        vault_path = tmp_path / "vault"

        config_data = {
            "vault": {"path": str(vault_path), "auto_create": True},
            "security": {"api_key": "test-key"},
            "server": {"https": False},
        }
        config_file.write_text(yaml.dump(config_data))

        assert not vault_path.exists()

        config = load_config(str(config_file))

        assert vault_path.exists()
        assert vault_path.is_dir()

    def test_load_config_generates_api_key(self, tmp_path, capsys):
        """Test that API key is generated when not provided."""
        config_file = tmp_path / "config.yaml"
        vault_path = tmp_path / "vault"

        config_data = {
            "vault": {"path": str(vault_path)},
            "server": {"https": False},
        }
        config_file.write_text(yaml.dump(config_data))

        config = load_config(str(config_file))

        assert config.security.api_key is not None
        assert len(config.security.api_key) == 64

        captured = capsys.readouterr()
        assert "Generated new API key" in captured.out

    def test_load_config_with_all_sections(self, tmp_path):
        """Test loading config with all configuration sections."""
        config_file = tmp_path / "config.yaml"
        vault_path = tmp_path / "vault"

        config_data = {
            "server": {"host": "127.0.0.1", "port": 27123, "https": False},
            "vault": {"path": str(vault_path), "auto_create": True},
            "security": {"api_key": "test-key"},
            "obsidian": {"enabled": True, "config_sync": False},
            "periodic_notes": {
                "daily": {"enabled": True, "format": "YYYY-MM-DD", "folder": "daily/"}
            },
            "search": {"max_results": 50, "enable_fuzzy": False},
            "active_file": {"tracking_method": "cookie"},
            "commands": {"enabled": False},
            "logging": {"level": "DEBUG", "format": "text"},
            "performance": {"max_file_size": 5242880, "cache_ttl": 600},
        }
        config_file.write_text(yaml.dump(config_data))

        config = load_config(str(config_file))

        # Verify all sections loaded correctly
        assert config.server.port == 27123
        assert config.vault.path == str(vault_path)
        assert config.obsidian.config_sync is False
        assert config.search.max_results == 50
        assert config.active_file.tracking_method == "cookie"
        assert config.commands.enabled is False
        assert config.logging.level == "DEBUG"
        assert config.performance.cache_ttl == 600
