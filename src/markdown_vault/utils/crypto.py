"""SSL certificate generation utilities for markdown-vault.

This module provides functions to generate self-signed SSL certificates
for HTTPS server operation, compatible with Obsidian vault requirements.
"""

import datetime
import ipaddress
from pathlib import Path
from typing import Tuple

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtensionOID, NameOID


def generate_self_signed_certificate(
    common_name: str = "markdown-vault",
    organization: str = "markdown-vault",
    validity_days: int = 365,
) -> Tuple[x509.Certificate, rsa.RSAPrivateKey]:
    """Generate a self-signed SSL certificate and private key.

    Creates a self-signed X.509 certificate with the following specifications:
    - 2048-bit RSA private key
    - SHA-256 signature algorithm
    - Subject Alternative Names (SAN) for localhost and 127.0.0.1
    - 1-year validity period (configurable)
    - Proper certificate fields (CN, O, etc.)

    Args:
        common_name: Common Name (CN) for the certificate. Defaults to "markdown-vault".
        organization: Organization (O) name for the certificate. Defaults to "markdown-vault".
        validity_days: Number of days the certificate should be valid. Defaults to 365.

    Returns:
        A tuple containing:
            - x509.Certificate: The generated certificate
            - rsa.RSAPrivateKey: The private key for the certificate

    Example:
        >>> cert, key = generate_self_signed_certificate()
        >>> # Use cert and key for HTTPS server
    """
    # Generate RSA private key (2048 bits)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Build certificate subject
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Development"),
        ]
    )

    # Define certificate validity period
    now = datetime.datetime.now(datetime.timezone.utc)
    valid_from = now
    valid_to = now + datetime.timedelta(days=validity_days)

    # Build the certificate
    cert_builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(valid_from)
        .not_valid_after(valid_to)
    )

    # Add Subject Alternative Names (SAN) for localhost
    san_list = [
        x509.DNSName("localhost"),
        x509.DNSName("*.localhost"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
        x509.IPAddress(ipaddress.IPv6Address("::1")),
    ]
    cert_builder = cert_builder.add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False,
    )

    # Add Basic Constraints to mark as CA=False (not a certificate authority)
    cert_builder = cert_builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )

    # Add Key Usage extension
    cert_builder = cert_builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            content_commitment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )

    # Add Extended Key Usage for server authentication
    cert_builder = cert_builder.add_extension(
        x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
        critical=False,
    )

    # Sign the certificate with the private key using SHA-256
    certificate = cert_builder.sign(
        private_key=private_key,
        algorithm=hashes.SHA256(),
    )

    return certificate, private_key


def save_certificate_and_key(
    certificate: x509.Certificate,
    private_key: rsa.RSAPrivateKey,
    cert_path: Path,
    key_path: Path,
) -> Tuple[Path, Path]:
    """Save certificate and private key to PEM files.

    Writes the certificate and private key to the specified paths in PEM format.
    Creates parent directories if they don't exist.

    Args:
        certificate: The X.509 certificate to save
        private_key: The RSA private key to save
        cert_path: Path where the certificate should be saved
        key_path: Path where the private key should be saved

    Returns:
        A tuple containing the resolved paths:
            - Path: Absolute path to the saved certificate file
            - Path: Absolute path to the saved private key file

    Raises:
        OSError: If there's an error creating directories or writing files
        PermissionError: If there's insufficient permission to write files

    Example:
        >>> cert, key = generate_self_signed_certificate()
        >>> cert_file, key_file = save_certificate_and_key(
        ...     cert, key,
        ...     Path("./certs/server.crt"),
        ...     Path("./certs/server.key")
        ... )
        >>> print(f"Certificate saved to {cert_file}")
    """
    # Convert to Path objects and resolve to absolute paths
    cert_path = Path(cert_path).resolve()
    key_path = Path(key_path).resolve()

    # Create parent directories if they don't exist
    cert_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.parent.mkdir(parents=True, exist_ok=True)

    # Serialize and write certificate to PEM file
    cert_pem = certificate.public_bytes(encoding=serialization.Encoding.PEM)
    cert_path.write_bytes(cert_pem)

    # Serialize and write private key to PEM file (unencrypted)
    # Note: For production use, consider encrypting the private key
    key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    key_path.write_bytes(key_pem)

    # Set restrictive permissions on the private key file (owner read/write only)
    try:
        key_path.chmod(0o600)
    except (OSError, NotImplementedError):
        # Some filesystems don't support chmod (e.g., Windows)
        pass

    return cert_path, key_path


def generate_and_save_certificate(
    cert_path: Path | str,
    key_path: Path | str,
    common_name: str = "markdown-vault",
    organization: str = "markdown-vault",
    validity_days: int = 365,
) -> Tuple[Path, Path]:
    """Generate a self-signed certificate and save it to files.

    Convenience function that combines certificate generation and file saving
    into a single operation.

    Args:
        cert_path: Path where the certificate should be saved
        key_path: Path where the private key should be saved
        common_name: Common Name (CN) for the certificate. Defaults to "markdown-vault".
        organization: Organization (O) name for the certificate. Defaults to "markdown-vault".
        validity_days: Number of days the certificate should be valid. Defaults to 365.

    Returns:
        A tuple containing the resolved paths:
            - Path: Absolute path to the saved certificate file
            - Path: Absolute path to the saved private key file

    Raises:
        OSError: If there's an error creating directories or writing files
        PermissionError: If there's insufficient permission to write files

    Example:
        >>> cert_file, key_file = generate_and_save_certificate(
        ...     "./certs/server.crt",
        ...     "./certs/server.key",
        ...     common_name="my-vault",
        ...     validity_days=730
        ... )
        >>> print(f"Generated certificate: {cert_file}")
        >>> print(f"Generated private key: {key_file}")
    """
    # Generate certificate and key
    certificate, private_key = generate_self_signed_certificate(
        common_name=common_name,
        organization=organization,
        validity_days=validity_days,
    )

    # Save to files
    return save_certificate_and_key(
        certificate=certificate,
        private_key=private_key,
        cert_path=Path(cert_path),
        key_path=Path(key_path),
    )


def certificate_exists(cert_path: Path | str, key_path: Path | str) -> bool:
    """Check if certificate and key files exist.

    Args:
        cert_path: Path to the certificate file
        key_path: Path to the private key file

    Returns:
        True if both files exist, False otherwise

    Example:
        >>> if not certificate_exists("./certs/server.crt", "./certs/server.key"):
        ...     generate_and_save_certificate("./certs/server.crt", "./certs/server.key")
    """
    cert_path = Path(cert_path)
    key_path = Path(key_path)
    return cert_path.is_file() and key_path.is_file()
