"""
Tests for SecureCompressor class.
"""

import pytest
from fastcrypter import SecureCompressor
from fastcrypter.exceptions import ValidationError, EncrypterError


class TestSecureCompressor:
    """Test suite for SecureCompressor class."""

    def test_init_default(self):
        """Test default initialization."""
        compressor = SecureCompressor(password="test_password123")
        assert compressor.password == "test_password123"

    def test_weak_password_error(self):
        """Test that weak password raises error."""
        with pytest.raises(ValidationError):
            SecureCompressor(password="weak")

    def test_compress_and_encrypt_bytes(self):
        """Test compression and encryption of bytes."""
        compressor = SecureCompressor(password="secure_password123")
        data = b"Test data for compression and encryption"
        
        encrypted = compressor.compress_and_encrypt(data)
        decrypted = compressor.decrypt_and_decompress(encrypted)
        
        assert data == decrypted

    def test_compress_and_encrypt_string(self):
        """Test compression and encryption of string."""
        compressor = SecureCompressor(password="password12345678")
        text = "Test string data"
        
        encrypted = compressor.compress_and_encrypt_string(text)
        decrypted = compressor.decrypt_and_decompress_to_string(encrypted)
        
        assert text == decrypted

    def test_custom_charset_encoding(self):
        """Test custom charset encoding."""
        compressor = SecureCompressor(
            password="test_password",
            custom_charset="abcdef0123456789"
        )
        
        data = b"Test data"
        encrypted = compressor.compress_and_encrypt(data, output_format='custom')
        
        # Should be a string with only specified characters
        assert isinstance(encrypted, str)
        for char in encrypted:
            assert char in "abcdef0123456789"
        
        decrypted = compressor.decrypt_and_decompress(encrypted, input_format='custom')
        assert data == decrypted

    def test_password_strength_validation(self):
        """Test password strength validation."""
        compressor = SecureCompressor(password="WeakPass123!")
        
        strength = compressor.validate_password_strength()
        
        assert 'strength' in strength
        assert 'score' in strength
        assert 'checks' in strength
        assert 'recommendations' in strength

    def test_change_password(self):
        """Test changing password."""
        compressor = SecureCompressor(password="old_password123")
        data = b"Test data"
        
        # Encrypt with old password
        encrypted = compressor.compress_and_encrypt(data)
        
        # Change password
        compressor.change_password("new_password123")
        
        # Encrypt with new password
        new_encrypted = compressor.compress_and_encrypt(data)
        
        # Old encrypted data should not decrypt with new password
        with pytest.raises(EncrypterError):
            compressor.decrypt_and_decompress(encrypted)

    def test_get_compression_ratio(self):
        """Test compression ratio calculation."""
        compressor = SecureCompressor(password="test_password")
        data = b"Test " * 100
        
        encrypted = compressor.compress_and_encrypt(data)
        ratio = compressor.get_compression_ratio(data, encrypted)
        
        assert ratio > 0

    def test_estimate_output_size(self):
        """Test output size estimation."""
        compressor = SecureCompressor(password="test_password")
        
        estimates = compressor.estimate_output_size(input_size=1000)
        
        assert 'estimated_compressed_size' in estimates
        assert 'estimated_encrypted_size' in estimates
        assert 'estimated_final_size' in estimates

    def test_get_info(self):
        """Test get_info method."""
        compressor = SecureCompressor(password="test_password")
        info = compressor.get_info()
        
        assert 'configuration' in info
        assert 'compressor_info' in info
        assert 'encryptor_info' in info
        assert 'key_manager_info' in info
        assert 'password_strength' in info

    def test_benchmark_performance(self):
        """Test performance benchmarking."""
        compressor = SecureCompressor(password="test_password")
        
        results = compressor.benchmark_performance(data_size=1024)
        
        assert 'binary' in results
        assert 'encrypt_time' in results['binary']
        assert 'decrypt_time' in results['binary']
        assert 'correctness' in results['binary']
        assert results['binary']['correctness'] is True

    def test_large_data(self):
        """Test with larger data."""
        compressor = SecureCompressor(password="test_password")
        data = b"Large test data " * 10000  # ~160KB
        
        encrypted = compressor.compress_and_encrypt(data)
        decrypted = compressor.decrypt_and_decompress(encrypted)
        
        assert data == decrypted

    def test_unicode_text(self):
        """Test with Unicode text."""
        compressor = SecureCompressor(password="test_password")
        text = "Hello 你好 مرحبا"
        
        encrypted = compressor.compress_and_encrypt_string(text)
        decrypted = compressor.decrypt_and_decompress_to_string(encrypted)
        
        assert text == decrypted
