"""
Tests for FileEncryptor class.
"""

import pytest
import tempfile
import os
from fastcrypter import FileEncryptor
from fastcrypter.exceptions import FileError


class TestFileEncryptor:
    """Test suite for FileEncryptor class."""

    def test_encrypt_decrypt_file(self):
        """Test file encryption and decryption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test file
            input_path = os.path.join(tmpdir, "test.txt")
            encrypted_path = os.path.join(tmpdir, "test.txt.encrypted")
            output_path = os.path.join(tmpdir, "test.txt.decrypted")
            
            test_data = b"Test file content for encryption"
            with open(input_path, 'wb') as f:
                f.write(test_data)
            
            # Encrypt
            encryptor = FileEncryptor(password="test_password")
            stats = encryptor.encrypt_file(input_path, encrypted_path)
            
            assert stats['original_size'] == len(test_data)
            assert os.path.exists(encrypted_path)
            
            # Decrypt
            decrypt_stats = encryptor.decrypt_file(encrypted_path, output_path)
            
            with open(output_path, 'rb') as f:
                decrypted_data = f.read()
            
            assert test_data == decrypted_data

    def test_file_not_found_error(self):
        """Test error when input file doesn't exist."""
        encryptor = FileEncryptor(password="test_password")
        
        with pytest.raises(FileError):
            encryptor.encrypt_file("/nonexistent/file.txt", "/tmp/output.txt")

    def test_large_file(self):
        """Test with larger file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "large.txt")
            encrypted_path = os.path.join(tmpdir, "large.encrypted")
            output_path = os.path.join(tmpdir, "large.decrypted")
            
            # Create ~1MB file
            test_data = b"Test data " * 100000
            with open(input_path, 'wb') as f:
                f.write(test_data)
            
            encryptor = FileEncryptor(password="test_password")
            encryptor.encrypt_file(input_path, encrypted_path)
            encryptor.decrypt_file(encrypted_path, output_path)
            
            with open(output_path, 'rb') as f:
                decrypted_data = f.read()
            
            assert test_data == decrypted_data
