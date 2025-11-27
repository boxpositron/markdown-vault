"""
Configuration loading and management for markdown-vault.

This module handles:
- Loading configuration from YAML files
- Environment variable overrides (MARKDOWN_VAULT_* prefix)
- API key management (file-based or direct)
- Configuration validation via Pydantic models
- Auto-generation of API keys and SSL certificates
"""

import os
import secrets
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from pydantic import ValidationError

from markdown_vault.models.config import (
    ActiveFileConfig,
    AppConfig,
    CommandsConfig,
    LoggingConfig,
    ObsidianConfig,
    PerformanceConfig,
    PeriodicNotesConfig,
    SearchConfig,
    SecurityConfig,
    ServerConfig,
    VaultConfig,
)


class ConfigError(Exception):
    """Raised when configuration loading or validation fails."""

    pass


def generate_api_key() -> str:
    """
    Generate a secure random API key.

    Returns:
        A 64-character hexadecimal API key
    """
    return secrets.token_hex(32)


def load_api_key_from_file(api_key_file: str) -> str:
    """
    Load API key from a file.

    Args:
        api_key_file: Path to the file containing the API key

    Returns:
        The API key string (stripped of whitespace)

    Raises:
        ConfigError: If the file cannot be read or is empty
    """
    try:
        key_path = Path(api_key_file).expanduser().resolve()
        if not key_path.exists():
            raise ConfigError(f"API key file not found: {api_key_file}")

        api_key = key_path.read_text().strip()
        if not api_key:
            raise ConfigError(f"API key file is empty: {api_key_file}")

        return api_key
    except OSError as e:
        raise ConfigError(f"Failed to read API key file {api_key_file}: {e}")


def generate_self_signed_cert(
    cert_path: Path, key_path: Path, hostname: str = "localhost"
) -> None:
    """
    Generate a self-signed SSL certificate.

    Args:
        cert_path: Path where the certificate will be saved
        key_path: Path where the private key will be saved
        hostname: Hostname for the certificate (default: localhost)

    Raises:
        ConfigError: If certificate generation fails
    """
    try:
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        # Create certificate
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "markdown-vault"),
                x509.NameAttribute(NameOID.COMMON_NAME, hostname),
            ]
        )

        import datetime

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName(hostname),
                        x509.DNSName("localhost"),
                        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256(), default_backend())
        )

        # Ensure directories exist
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        key_path.parent.mkdir(parents=True, exist_ok=True)

        # Write certificate
        cert_path.write_bytes(cert.public_bytes(encoding=serialization.Encoding.PEM))

        # Write private key
        key_path.write_bytes(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    except Exception as e:
        raise ConfigError(f"Failed to generate self-signed certificate: {e}")


def load_yaml_config(config_path: Path) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file

    Returns:
        Dictionary containing the configuration

    Raises:
        ConfigError: If the file cannot be read or parsed
    """
    try:
        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        if config_data is None:
            raise ConfigError(f"Configuration file is empty: {config_path}")

        if not isinstance(config_data, dict):
            raise ConfigError(
                f"Configuration file must contain a YAML object: {config_path}"
            )

        return config_data

    except yaml.YAMLError as e:
        raise ConfigError(f"Failed to parse YAML configuration: {e}")
    except OSError as e:
        raise ConfigError(f"Failed to read configuration file: {e}")


def merge_env_overrides(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge environment variable overrides into configuration.

    Environment variables use the format:
    MARKDOWN_VAULT_<SECTION>__<KEY>

    For example:
    - MARKDOWN_VAULT_SERVER__PORT=8080
    - MARKDOWN_VAULT_VAULT__PATH=/path/to/vault
    - MARKDOWN_VAULT_SECURITY__API_KEY=mykey

    Args:
        config_data: Base configuration dictionary

    Returns:
        Configuration dictionary with environment overrides applied
    """
    env_prefix = "MARKDOWN_VAULT_"

    for env_key, env_value in os.environ.items():
        if not env_key.startswith(env_prefix):
            continue

        # Remove prefix and split by delimiter
        key_path = env_key[len(env_prefix) :].lower().split("__")

        if len(key_path) < 2:
            continue

        section = key_path[0]
        setting = key_path[1]

        # Convert value to appropriate type
        value: Any = env_value
        if env_value.lower() in ("true", "false"):
            value = env_value.lower() == "true"
        elif env_value.isdigit():
            value = int(env_value)
        elif env_value.lower() == "null":
            value = None

        # Apply override
        if section not in config_data:
            config_data[section] = {}

        config_data[section][setting] = value

    return config_data


def resolve_api_key(security_config: SecurityConfig) -> str:
    """
    Resolve the API key from configuration.

    Priority:
    1. Direct api_key value
    2. Load from api_key_file
    3. Generate new key

    Args:
        security_config: Security configuration object

    Returns:
        The resolved API key

    Raises:
        ConfigError: If api_key_file is specified but cannot be read
    """
    # Check direct API key
    if security_config.api_key:
        return security_config.api_key

    # Check API key file
    if security_config.api_key_file:
        return load_api_key_from_file(security_config.api_key_file)

    # Generate new key
    api_key = generate_api_key()
    print(f"Generated new API key: {api_key}")
    print(
        "Save this key! Set it via api_key config or MARKDOWN_VAULT_SECURITY__API_KEY"
    )
    return api_key


def ensure_ssl_certificates(security_config: SecurityConfig, hostname: str) -> None:
    """
    Ensure SSL certificates exist, generating them if needed.

    Args:
        security_config: Security configuration object
        hostname: Hostname to use for certificate generation

    Raises:
        ConfigError: If certificates cannot be generated or accessed
    """
    cert_path = Path(security_config.cert_path).expanduser().resolve()
    key_path = Path(security_config.key_path).expanduser().resolve()

    # Check if both files exist
    if cert_path.exists() and key_path.exists():
        return

    # Auto-generate if enabled
    if security_config.auto_generate_cert:
        print(f"Generating self-signed SSL certificate for {hostname}...")
        generate_self_signed_cert(cert_path, key_path, hostname)
        print(f"Certificate saved to: {cert_path}")
        print(f"Private key saved to: {key_path}")
    else:
        raise ConfigError(
            f"SSL certificate files not found and auto_generate_cert is disabled.\n"
            f"Expected: {cert_path} and {key_path}"
        )


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load and validate application configuration.

    This function:
    1. Loads configuration from YAML file (if provided)
    2. Applies environment variable overrides
    3. Validates configuration using Pydantic models
    4. Resolves API key (from file, direct, or generates new)
    5. Ensures SSL certificates exist (if HTTPS enabled)

    Args:
        config_path: Path to YAML configuration file (optional)

    Returns:
        Validated AppConfig object

    Raises:
        ConfigError: If configuration is invalid or required files are missing
    """
    # Start with empty config
    config_data: Dict[str, Any] = {}

    # Load from YAML if provided
    if config_path:
        yaml_path = Path(config_path).expanduser().resolve()
        config_data = load_yaml_config(yaml_path)

    # Apply environment variable overrides
    config_data = merge_env_overrides(config_data)

    # Validate and create config object
    try:
        app_config = AppConfig(**config_data)
    except ValidationError as e:
        raise ConfigError(f"Configuration validation failed:\n{e}")

    # Resolve API key
    api_key = resolve_api_key(app_config.security)
    # Update the config with resolved API key
    app_config.security.api_key = api_key

    # Ensure SSL certificates if HTTPS is enabled
    if app_config.server.https:
        ensure_ssl_certificates(app_config.security, app_config.server.host)

    # Create vault directory if needed
    vault_path = Path(app_config.vault.path).expanduser().resolve()
    if app_config.vault.auto_create and not vault_path.exists():
        try:
            vault_path.mkdir(parents=True, exist_ok=True)
            print(f"Created vault directory: {vault_path}")
        except OSError as e:
            raise ConfigError(f"Failed to create vault directory: {e}")

    return app_config


# Import ipaddress for SSL cert generation
import ipaddress


__all__ = [
    "AppConfig",
    "ConfigError",
    "load_config",
    "generate_api_key",
    "load_api_key_from_file",
    "generate_self_signed_cert",
    "resolve_api_key",
    "ensure_ssl_certificates",
]
