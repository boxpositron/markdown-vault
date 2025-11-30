"""Tests for SSL certificate generation utilities."""

import datetime
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtensionOID, NameOID

from markdown_vault.utils.crypto import (
    certificate_exists,
    generate_and_save_certificate,
    generate_self_signed_certificate,
    save_certificate_and_key,
)


class TestGenerateSelfSignedCertificate:
    """Tests for generate_self_signed_certificate function."""

    def test_generates_certificate_and_key(self) -> None:
        """Test that function returns certificate and private key."""
        cert, key = generate_self_signed_certificate()

        assert isinstance(cert, x509.Certificate)
        assert isinstance(key, rsa.RSAPrivateKey)

    def test_certificate_has_correct_key_size(self) -> None:
        """Test that private key is 2048 bits."""
        _, key = generate_self_signed_certificate()

        assert key.key_size == 2048

    def test_certificate_uses_sha256(self) -> None:
        """Test that certificate uses SHA-256 signature algorithm."""
        cert, _ = generate_self_signed_certificate()

        # Check signature algorithm
        assert cert.signature_hash_algorithm is not None
        assert cert.signature_hash_algorithm.name == "sha256"

    def test_certificate_has_correct_subject(self) -> None:
        """Test that certificate has correct subject fields."""
        common_name = "test-vault"
        organization = "test-org"

        cert, _ = generate_self_signed_certificate(
            common_name=common_name, organization=organization
        )

        # Check Common Name
        cn_attrs = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        assert len(cn_attrs) == 1
        assert cn_attrs[0].value == common_name

        # Check Organization
        o_attrs = cert.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)
        assert len(o_attrs) == 1
        assert o_attrs[0].value == organization

    def test_certificate_is_self_signed(self) -> None:
        """Test that certificate is self-signed (subject == issuer)."""
        cert, _ = generate_self_signed_certificate()

        assert cert.subject == cert.issuer

    def test_certificate_has_san_extension(self) -> None:
        """Test that certificate has Subject Alternative Names."""
        cert, _ = generate_self_signed_certificate()

        san_ext = cert.extensions.get_extension_for_oid(
            ExtensionOID.SUBJECT_ALTERNATIVE_NAME
        )
        san = san_ext.value

        # Extract DNS names and IP addresses
        dns_names = [name.value for name in san if isinstance(name, x509.DNSName)]
        ip_addresses = [
            str(addr.value) for addr in san if isinstance(addr, x509.IPAddress)
        ]

        # Verify expected values
        assert "localhost" in dns_names
        assert "*.localhost" in dns_names
        assert "127.0.0.1" in ip_addresses
        assert "::1" in ip_addresses

    def test_certificate_validity_period(self) -> None:
        """Test that certificate has correct validity period."""
        validity_days = 730
        cert, _ = generate_self_signed_certificate(validity_days=validity_days)

        now = datetime.datetime.now(datetime.timezone.utc)

        # Check not_valid_before is recent (within last minute)
        assert cert.not_valid_before_utc <= now
        assert (now - cert.not_valid_before_utc).total_seconds() < 60

        # Check not_valid_after is approximately validity_days from now
        expected_expiry = now + datetime.timedelta(days=validity_days)
        time_diff = abs((cert.not_valid_after_utc - expected_expiry).total_seconds())
        assert time_diff < 60  # Within 1 minute

    def test_certificate_has_basic_constraints(self) -> None:
        """Test that certificate has BasicConstraints extension with ca=False."""
        cert, _ = generate_self_signed_certificate()

        bc_ext = cert.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS)
        assert bc_ext.critical is True
        assert bc_ext.value.ca is False

    def test_certificate_has_key_usage(self) -> None:
        """Test that certificate has KeyUsage extension."""
        cert, _ = generate_self_signed_certificate()

        ku_ext = cert.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE)
        key_usage = ku_ext.value

        assert ku_ext.critical is True
        assert key_usage.digital_signature is True
        assert key_usage.key_encipherment is True

    def test_certificate_has_extended_key_usage(self) -> None:
        """Test that certificate has ExtendedKeyUsage for server auth."""
        cert, _ = generate_self_signed_certificate()

        eku_ext = cert.extensions.get_extension_for_oid(ExtensionOID.EXTENDED_KEY_USAGE)
        assert x509.oid.ExtendedKeyUsageOID.SERVER_AUTH in eku_ext.value


class TestSaveCertificateAndKey:
    """Tests for save_certificate_and_key function."""

    def test_saves_certificate_and_key(self, tmp_path: Path) -> None:
        """Test that certificate and key are saved to files."""
        cert, key = generate_self_signed_certificate()
        cert_path = tmp_path / "test.crt"
        key_path = tmp_path / "test.key"

        saved_cert_path, saved_key_path = save_certificate_and_key(
            cert, key, cert_path, key_path
        )

        assert saved_cert_path.exists()
        assert saved_key_path.exists()
        assert saved_cert_path == cert_path.resolve()
        assert saved_key_path == key_path.resolve()

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test that parent directories are created if they don't exist."""
        cert, key = generate_self_signed_certificate()
        cert_path = tmp_path / "nested" / "dir" / "test.crt"
        key_path = tmp_path / "nested" / "dir" / "test.key"

        save_certificate_and_key(cert, key, cert_path, key_path)

        assert cert_path.exists()
        assert key_path.exists()
        assert cert_path.parent.exists()

    def test_saved_certificate_is_valid_pem(self, tmp_path: Path) -> None:
        """Test that saved certificate is valid PEM format."""
        cert, key = generate_self_signed_certificate()
        cert_path = tmp_path / "test.crt"
        key_path = tmp_path / "test.key"

        save_certificate_and_key(cert, key, cert_path, key_path)

        # Read and verify certificate
        cert_data = cert_path.read_bytes()
        assert b"-----BEGIN CERTIFICATE-----" in cert_data
        assert b"-----END CERTIFICATE-----" in cert_data

    def test_saved_key_is_valid_pem(self, tmp_path: Path) -> None:
        """Test that saved private key is valid PEM format."""
        cert, key = generate_self_signed_certificate()
        cert_path = tmp_path / "test.crt"
        key_path = tmp_path / "test.key"

        save_certificate_and_key(cert, key, cert_path, key_path)

        # Read and verify private key
        key_data = key_path.read_bytes()
        assert b"-----BEGIN RSA PRIVATE KEY-----" in key_data
        assert b"-----END RSA PRIVATE KEY-----" in key_data

    def test_overwrites_existing_files(self, tmp_path: Path) -> None:
        """Test that existing files are overwritten."""
        cert1, key1 = generate_self_signed_certificate(common_name="first")
        cert2, key2 = generate_self_signed_certificate(common_name="second")

        cert_path = tmp_path / "test.crt"
        key_path = tmp_path / "test.key"

        # Save first certificate
        save_certificate_and_key(cert1, key1, cert_path, key_path)
        first_cert_data = cert_path.read_bytes()

        # Save second certificate (should overwrite)
        save_certificate_and_key(cert2, key2, cert_path, key_path)
        second_cert_data = cert_path.read_bytes()

        assert first_cert_data != second_cert_data


class TestGenerateAndSaveCertificate:
    """Tests for generate_and_save_certificate function."""

    def test_generates_and_saves_certificate(self, tmp_path: Path) -> None:
        """Test that certificate is generated and saved in one step."""
        cert_path = tmp_path / "test.crt"
        key_path = tmp_path / "test.key"

        saved_cert_path, saved_key_path = generate_and_save_certificate(
            cert_path, key_path
        )

        assert saved_cert_path.exists()
        assert saved_key_path.exists()

    def test_accepts_custom_parameters(self, tmp_path: Path) -> None:
        """Test that custom parameters are passed through correctly."""
        cert_path = tmp_path / "test.crt"
        key_path = tmp_path / "test.key"
        common_name = "custom-vault"
        organization = "custom-org"

        generate_and_save_certificate(
            cert_path,
            key_path,
            common_name=common_name,
            organization=organization,
            validity_days=180,
        )

        # Load and verify certificate

        cert_data = cert_path.read_bytes()
        from cryptography import x509

        cert = x509.load_pem_x509_certificate(cert_data)

        cn_attrs = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        assert cn_attrs[0].value == common_name

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Test that function accepts string paths."""
        cert_path = str(tmp_path / "test.crt")
        key_path = str(tmp_path / "test.key")

        saved_cert_path, saved_key_path = generate_and_save_certificate(
            cert_path, key_path
        )

        assert isinstance(saved_cert_path, Path)
        assert isinstance(saved_key_path, Path)
        assert saved_cert_path.exists()
        assert saved_key_path.exists()


class TestCertificateExists:
    """Tests for certificate_exists function."""

    def test_returns_true_when_both_files_exist(self, tmp_path: Path) -> None:
        """Test that function returns True when both files exist."""
        cert_path = tmp_path / "test.crt"
        key_path = tmp_path / "test.key"

        generate_and_save_certificate(cert_path, key_path)

        assert certificate_exists(cert_path, key_path) is True

    def test_returns_false_when_cert_missing(self, tmp_path: Path) -> None:
        """Test that function returns False when certificate is missing."""
        cert_path = tmp_path / "missing.crt"
        key_path = tmp_path / "test.key"

        # Create only the key file
        key_path.write_text("dummy key")

        assert certificate_exists(cert_path, key_path) is False

    def test_returns_false_when_key_missing(self, tmp_path: Path) -> None:
        """Test that function returns False when key is missing."""
        cert_path = tmp_path / "test.crt"
        key_path = tmp_path / "missing.key"

        # Create only the cert file
        cert_path.write_text("dummy cert")

        assert certificate_exists(cert_path, key_path) is False

    def test_returns_false_when_both_missing(self, tmp_path: Path) -> None:
        """Test that function returns False when both files are missing."""
        cert_path = tmp_path / "missing.crt"
        key_path = tmp_path / "missing.key"

        assert certificate_exists(cert_path, key_path) is False

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Test that function accepts string paths."""
        cert_path = tmp_path / "test.crt"
        key_path = tmp_path / "test.key"

        generate_and_save_certificate(cert_path, key_path)

        assert certificate_exists(str(cert_path), str(key_path)) is True
