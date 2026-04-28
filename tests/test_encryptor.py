"""
Tests for Encryptor class.
"""

import pytest
from fastcrypter.core import Encryptor, EncryptionAlgorithmType
from fastcrypter.exceptions import EncryptionError, ValidationError


class TestEncryptor:
    """Test suite for Encryptor class."""

    def test_init_default(self):
        """Test default initialization."""
        encryptor = Encryptor()
        assert encryptor.algorithm == EncryptionAlgorithmType.AES_256_GCM

    def test_init_custom(self):
        """Test custom initialization."""
        encryptor = Encryptor(algorithm=EncryptionAlgorithmType.CHACHA20_POLY1305)
        assert encryptor.algorithm == EncryptionAlgorithmType.CHACHA20_POLY1305

    def test_encrypt_decrypt_aes_gcm(self):
        """Test AES-256-GCM encryption and decryption."""
        encryptor = Encryptor(algorithm=EncryptionAlgorithmType.AES_256_GCM)
        data = b"Secret data"
        password = "test_password"
        
        encrypted = encryptor.encrypt(data, password)
        decrypted = encryptor.decrypt(encrypted, password)
        
        assert data == decrypted
        assert encrypted != data

    def test_encrypt_decrypt_aes_cbc(self):
        """Test AES-256-CBC encryption and decryption."""
        encryptor = Encryptor(algorithm=EncryptionAlgorithmType.AES_256_CBC)
        data = b"Test data for CBC"
        password = "password123"
        
        encrypted = encryptor.encrypt(data, password)
        decrypted = encryptor.decrypt(encrypted, password)
        
        assert data == decrypted

    def test_encrypt_decrypt_chacha20(self):
        """Test ChaCha20-Poly1305 encryption and decryption."""
        encryptor = Encryptor(algorithm=EncryptionAlgorithmType.CHACHA20_POLY1305)
        data = b"ChaCha20 test data"
        password = "strong_password"
        
        encrypted = encryptor.encrypt(data, password)
        decrypted = encryptor.decrypt(encrypted, password)
        
        assert data == decrypted

    def test_encrypt_string(self):
        """Test encryption of string data."""
        encryptor = Encryptor()
        text = "String encryption test"
        password = "test_pass"
        
        encrypted = encryptor.encrypt(text, password)
        decrypted = encryptor.decrypt(encrypted, password)
        
        assert text.encode('utf-8') == decrypted

    def test_wrong_password(self):
        """Test decryption with wrong password fails."""
        encryptor = Encryptor()
        data = b"Secure data"
        password = "correct_password"
        wrong_password = "wrong_password"
        
        encrypted = encryptor.encrypt(data, password)
        
        with pytest.raises(EncryptionError):
            encryptor.decrypt(encrypted, wrong_password)

    def test_empty_data_error(self):
        """Test that empty data raises error."""
        encryptor = Encryptor()
        
        with pytest.raises(ValidationError):
            encryptor.encrypt(b"", "password")

    def test_invalid_data_type_error(self):
        """Test that invalid data type raises error."""
        encryptor = Encryptor()
        
        with pytest.raises(ValidationError):
            encryptor.encrypt([1, 2, 3], "password")

    def test_header_preservation(self):
        """Test that encryption header is properly added and parsed."""
        encryptor = Encryptor()
        data = b"Test data"
        password = "test_password"
        
        encrypted = encryptor.encrypt(data, password)
        
        # Header should be at the beginning
        assert encrypted[:4] == b'ENCR'

    def test_get_info(self):
        """Test get_info method."""
        encryptor = Encryptor()
        info = encryptor.get_info()
        
        assert 'algorithm' in info
        assert 'key_size' in info
        assert 'authenticated' in info

    def test_rsa_keypair_generation(self):
        """Test RSA key pair generation."""
        encryptor = Encryptor(algorithm=EncryptionAlgorithmType.RSA_4096)
        
        private_key, public_key = encryptor.generate_rsa_keypair()
        
        assert private_key is not None
        assert public_key is not None
        assert b'PRIVATE KEY' in private_key
        assert b'PUBLIC KEY' in public_key

    def test_rsa_encryption_small_data(self):
        """Test RSA encryption with small data."""
        encryptor = Encryptor(algorithm=EncryptionAlgorithmType.RSA_4096)
        private_key, public_key = encryptor.generate_rsa_keypair()
        
        data = b"Small RSA test"
        encrypted = encryptor.encrypt(data, None)
        decrypted = encryptor.decrypt(encrypted, None)
        
        assert data == decrypted
