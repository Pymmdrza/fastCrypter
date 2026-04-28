"""
Tests for KeyManager class.
"""

import pytest
from fastcrypter import KeyManager
from fastcrypter.exceptions import ValidationError, KeyError


class TestKeyManager:
    """Test suite for KeyManager class."""

    def test_init_default(self):
        """Test default initialization."""
        km = KeyManager()
        assert km.kdf_algorithm == 'pbkdf2'
        assert km.iterations >= 10000

    def test_generate_salt(self):
        """Test salt generation."""
        km = KeyManager()
        
        salt1 = km.generate_salt()
        salt2 = km.generate_salt()
        
        assert len(salt1) == 16
        assert len(salt2) == 16
        assert salt1 != salt2  # Should be random

    def test_generate_key(self):
        """Test key generation."""
        km = KeyManager()
        
        key1 = km.generate_key()
        key2 = km.generate_key()
        
        assert len(key1) == 32
        assert len(key2) == 32
        assert key1 != key2  # Should be random

    def test_derive_key_pbkdf2(self):
        """Test key derivation with PBKDF2."""
        km = KeyManager(kdf_algorithm='pbkdf2')
        
        key, salt = km.derive_key("test_password")
        
        assert len(key) == 32
        assert len(salt) >= 16

    def test_derive_key_scrypt(self):
        """Test key derivation with Scrypt."""
        km = KeyManager(kdf_algorithm='scrypt')
        
        key, salt = km.derive_key("test_password")
        
        assert len(key) == 32
        assert len(salt) >= 16

    def test_derive_key_argon2(self):
        """Test key derivation with Argon2."""
        km = KeyManager(kdf_algorithm='argon2')
        
        key, salt = km.derive_key("test_password")
        
        assert len(key) == 32
        assert len(salt) >= 16

    def test_derive_key_with_salt(self):
        """Test key derivation with provided salt."""
        km = KeyManager()
        salt = b"predefined_salt!"
        
        key1, _ = km.derive_key("password", salt=salt)
        key2, _ = km.derive_key("password", salt=salt)
        
        # Same password + salt should produce same key
        assert key1 == key2

    def test_weak_password_error(self):
        """Test that weak password raises error."""
        km = KeyManager()
        
        with pytest.raises(ValidationError):
            km.derive_key("weak")

    def test_validate_key_strength(self):
        """Test key strength validation."""
        km = KeyManager()
        
        strong_key = km.generate_key(32)
        weak_key = b"weak_key_12345"
        
        assert km.validate_key_strength(strong_key) is True
        assert km.validate_key_strength(weak_key) is False

    def test_secure_compare(self):
        """Test constant-time comparison."""
        km = KeyManager()
        
        key1 = b"test_key_123456"
        key2 = b"test_key_123456"
        key3 = b"different_key!!"
        
        assert km.secure_compare(key1, key2) is True
        assert km.secure_compare(key1, key3) is False

    def test_clear_memory(self):
        """Test secure memory clearing."""
        km = KeyManager()
        
        data = bytearray(b"sensitive_data")
        km.clear_memory(data)
        
        # Data should be zeroed
        assert all(b == 0 for b in data)

    def test_get_info(self):
        """Test get_info method."""
        km = KeyManager()
        info = km.get_info()
        
        assert 'kdf_algorithm' in info
        assert 'iterations' in info
        assert 'default_key_length' in info
