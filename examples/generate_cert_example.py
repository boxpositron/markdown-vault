#!/usr/bin/env python3
"""Example script demonstrating SSL certificate generation.

This script shows how to use the crypto utilities to generate
self-signed SSL certificates for markdown-vault.
"""

from pathlib import Path

from markdown_vault.utils.crypto import (
    certificate_exists,
    generate_and_save_certificate,
)


def main() -> None:
    """Generate SSL certificate for markdown-vault."""
    # Define certificate paths
    cert_dir = Path("./certs")
    cert_path = cert_dir / "server.crt"
    key_path = cert_dir / "server.key"

    print("SSL Certificate Generation Example")
    print("=" * 50)
    print()

    # Check if certificates already exist
    if certificate_exists(cert_path, key_path):
        print(f"✓ Certificates already exist:")
        print(f"  - Certificate: {cert_path}")
        print(f"  - Private Key: {key_path}")
        print()
        print("To regenerate, delete the existing files and run again.")
        return

    # Generate new certificates
    print("Generating new SSL certificate...")
    print(f"  - Common Name: markdown-vault")
    print(f"  - Validity: 365 days")
    print(f"  - Key Size: 2048 bits")
    print(f"  - Algorithm: SHA-256")
    print()

    try:
        cert_file, key_file = generate_and_save_certificate(
            cert_path=cert_path,
            key_path=key_path,
            common_name="markdown-vault",
            organization="markdown-vault",
            validity_days=365,
        )

        print("✓ Certificate generated successfully!")
        print()
        print(f"Certificate saved to: {cert_file}")
        print(f"Private key saved to:  {key_file}")
        print()
        print("Next steps:")
        print("1. Configure your markdown-vault server to use these certificates")
        print("2. Add the certificate to your system's trust store (optional)")
        print("3. Start the server with HTTPS enabled")
        print()
        print("Example configuration (config.yaml):")
        print("---")
        print("security:")
        print(f"  cert_path: {cert_file}")
        print(f"  key_path: {key_file}")
        print("  auto_generate_cert: false")

    except Exception as e:
        print(f"✗ Error generating certificate: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main() or 0)
