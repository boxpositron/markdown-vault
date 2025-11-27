#!/usr/bin/env python3
"""
Example demonstrating the markdown-vault configuration system.

This script shows how to:
1. Load configuration from a YAML file
2. Override values with environment variables
3. Access configuration values
"""

import os
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from markdown_vault.core.config import ConfigError, load_config


def example_load_from_yaml():
    """Example: Load configuration from YAML file."""
    print("=" * 60)
    print("Example 1: Load from YAML file")
    print("=" * 60)

    # Use the example config file
    config_path = Path(__file__).parent.parent / "config" / "config.example.yaml"

    try:
        # Note: This will fail with validation error because vault path is not absolute
        # That's expected for the example file
        config = load_config(str(config_path))
        print(f"✓ Configuration loaded successfully!")
        print(f"  Server: {config.server.host}:{config.server.port}")
        print(f"  HTTPS: {config.server.https}")
        print(f"  Vault: {config.vault.path}")
    except ConfigError as e:
        print(f"✗ Configuration error: {e}")
        print("\nThis is expected for the example config file.")
        print("The vault path needs to be an absolute path.\n")


def example_with_env_vars():
    """Example: Load configuration with environment variable overrides."""
    print("=" * 60)
    print("Example 2: Environment variable overrides")
    print("=" * 60)

    # Set environment variables
    os.environ["MARKDOWN_VAULT_SERVER__PORT"] = "9090"
    os.environ["MARKDOWN_VAULT_SERVER__HOST"] = "0.0.0.0"
    os.environ["MARKDOWN_VAULT_VAULT__PATH"] = "/tmp/test-vault"
    os.environ["MARKDOWN_VAULT_SERVER__HTTPS"] = "false"
    os.environ["MARKDOWN_VAULT_SECURITY__API_KEY"] = "my-secret-key"

    try:
        config = load_config()
        print(f"✓ Configuration loaded from environment variables!")
        print(f"  Server: {config.server.host}:{config.server.port}")
        print(f"  HTTPS: {config.server.https}")
        print(f"  Vault: {config.vault.path}")
        print(f"  API Key: {config.security.api_key[:10]}...")
        print(f"\nAll configuration sections:")
        print(f"  - Server: ✓")
        print(f"  - Vault: ✓")
        print(f"  - Security: ✓")
        print(f"  - Obsidian: ✓ (enabled={config.obsidian.enabled})")
        print(f"  - Search: ✓ (max_results={config.search.max_results})")
        print(f"  - Logging: ✓ (level={config.logging.level})")
        print(f"  - Performance: ✓ (worker_count={config.performance.worker_count})")
    except ConfigError as e:
        print(f"✗ Configuration error: {e}")
    finally:
        # Clean up environment variables
        for key in list(os.environ.keys()):
            if key.startswith("MARKDOWN_VAULT_"):
                del os.environ[key]


def example_api_key_generation():
    """Example: API key auto-generation."""
    print("=" * 60)
    print("Example 3: API key auto-generation")
    print("=" * 60)

    # Configure with no API key
    os.environ["MARKDOWN_VAULT_VAULT__PATH"] = "/tmp/test-vault"
    os.environ["MARKDOWN_VAULT_SERVER__HTTPS"] = "false"

    try:
        config = load_config()
        print(f"✓ API key was auto-generated!")
        print(f"  Key: {config.security.api_key}")
        print(f"\nThis key should be saved and reused for authentication.")
    except ConfigError as e:
        print(f"✗ Configuration error: {e}")
    finally:
        # Clean up
        for key in list(os.environ.keys()):
            if key.startswith("MARKDOWN_VAULT_"):
                del os.environ[key]


def example_periodic_notes_config():
    """Example: Access periodic notes configuration."""
    print("=" * 60)
    print("Example 4: Periodic notes configuration")
    print("=" * 60)

    os.environ["MARKDOWN_VAULT_VAULT__PATH"] = "/tmp/test-vault"
    os.environ["MARKDOWN_VAULT_SERVER__HTTPS"] = "false"
    os.environ["MARKDOWN_VAULT_SECURITY__API_KEY"] = "test-key"

    try:
        config = load_config()
        print(f"✓ Periodic notes configuration:")
        print(f"  Daily notes:")
        print(f"    - Enabled: {config.periodic_notes.daily.enabled}")
        print(f"    - Format: {config.periodic_notes.daily.format}")
        print(f"    - Folder: {config.periodic_notes.daily.folder}")
        print(f"  Weekly notes:")
        print(f"    - Enabled: {config.periodic_notes.weekly.enabled}")
        print(f"    - Format: {config.periodic_notes.weekly.format}")
        print(f"    - Folder: {config.periodic_notes.weekly.folder}")
        print(f"  Monthly notes:")
        print(f"    - Enabled: {config.periodic_notes.monthly.enabled}")
        print(f"    - Format: {config.periodic_notes.monthly.format}")
        print(f"    - Folder: {config.periodic_notes.monthly.folder}")
    except ConfigError as e:
        print(f"✗ Configuration error: {e}")
    finally:
        # Clean up
        for key in list(os.environ.keys()):
            if key.startswith("MARKDOWN_VAULT_"):
                del os.environ[key]


if __name__ == "__main__":
    example_load_from_yaml()
    print()
    example_with_env_vars()
    print()
    example_api_key_generation()
    print()
    example_periodic_notes_config()
    print("\n" + "=" * 60)
    print("Configuration examples complete!")
    print("=" * 60)
