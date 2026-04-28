"""
Tests for example files in the examples/ directory.

This test suite ensures all example files run correctly without errors.
"""

import pytest
import subprocess
import sys
import os


# Path to examples directory
EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'examples')


class TestExamples:
    """Test suite for example files."""

    def run_example(self, filename, timeout=30):
        """Run an example file and return the result."""
        example_path = os.path.join(EXAMPLES_DIR, filename)
        
        # Run the example as a subprocess
        result = subprocess.run(
            [sys.executable, example_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        return result

    def test_basic_usage_example(self):
        """Test basic_usage.py example."""
        result = self.run_example('basic_usage.py')
        
        assert result.returncode == 0, f"Example failed with output:\n{result.stderr}"
        assert "All tests completed successfully" in result.stdout
        assert "Data successfully recovered" in result.stdout

    def test_algorithm_test_example(self):
        """Test algorithm_test.py example."""
        result = self.run_example('algorithm_test.py', timeout=60)
        
        assert result.returncode == 0, f"Example failed with output:\n{result.stderr}"
        assert "Tests completed" in result.stdout
        assert "Best compression" in result.stdout

    def test_file_test_example(self):
        """Test file_test.py example."""
        result = self.run_example('file_test.py')
        
        assert result.returncode == 0, f"Example failed with output:\n{result.stderr}"
        assert "File encryption test completed successfully" in result.stdout
        assert "File content successfully recovered" in result.stdout

    def test_custom_encoding_test_example(self):
        """Test custom_encoding_test.py example."""
        result = self.run_example('custom_encoding_test.py', timeout=45)
        
        assert result.returncode == 0, f"Example failed with output:\n{result.stderr}"
        assert "Custom encoding tests completed" in result.stdout
        assert "Data integrity is maintained" in result.stdout

    @pytest.mark.slow
    def test_native_performance_test_example(self):
        """Test native_performance_test.py example (slow test)."""
        # This test is marked as slow because it runs extensive benchmarks
        result = self.run_example('native_performance_test.py', timeout=120)
        
        # May fail if native libraries aren't available, but shouldn't crash
        assert result.returncode in [0, 1], f"Example crashed with output:\n{result.stderr}"
        assert "Native Library Performance Test" in result.stdout

    def test_examples_no_syntax_errors(self):
        """Test that all example files can be compiled (no syntax errors)."""
        example_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.py')]
        
        for filename in example_files:
            example_path = os.path.join(EXAMPLES_DIR, filename)
            
            # Try to compile the file
            with open(example_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            try:
                compile(code, example_path, 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {filename}: {e}")

    def test_examples_no_emojis(self):
        """Test that example files don't contain emojis (per project standards)."""
        import re
        
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001F900-\U0001F9FF"  # supplemental symbols
            u"\U00002600-\U000026FF"  # misc symbols
            "]+", flags=re.UNICODE)
        
        example_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.py')]
        
        for filename in example_files:
            example_path = os.path.join(EXAMPLES_DIR, filename)
            
            with open(example_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            emojis_found = emoji_pattern.findall(content)
            assert not emojis_found, f"Found emojis in {filename}: {emojis_found}"

    def test_examples_use_correct_imports(self):
        """Test that examples import from 'fastcrypter' not 'encrypter'."""
        example_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.py')]
        
        for filename in example_files:
            example_path = os.path.join(EXAMPLES_DIR, filename)
            
            with open(example_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for incorrect imports
            assert 'from encrypter import' not in content, \
                f"{filename} uses 'encrypter' instead of 'fastcrypter'"
            assert 'from encrypter.' not in content, \
                f"{filename} uses 'encrypter.' instead of 'fastcrypter.'"
            assert 'import encrypter' not in content, \
                f"{filename} uses 'import encrypter' instead of 'import fastcrypter'"


class TestExampleOutputQuality:
    """Test the quality and correctness of example outputs."""

    def test_basic_usage_encryption_correctness(self):
        """Test that basic_usage.py correctly encrypts and decrypts."""
        from fastcrypter import SecureCompressor
        
        compressor = SecureCompressor(password="TestPassword123!")
        test_data = "Test data for verification"
        
        encrypted = compressor.compress_and_encrypt(test_data)
        decrypted = compressor.decrypt_and_decompress_to_string(encrypted)
        
        assert test_data == decrypted

    def test_file_encryption_correctness(self):
        """Test that file encryption works as demonstrated in examples."""
        import tempfile
        from fastcrypter import FileEncryptor
        
        encryptor = FileEncryptor(password="TestPassword123!")
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test file content")
            original_file = f.name
        
        encrypted_file = original_file + '.enc'
        decrypted_file = original_file + '.dec'
        
        try:
            # Test encryption/decryption
            encryptor.encrypt_file(original_file, encrypted_file)
            encryptor.decrypt_file(encrypted_file, decrypted_file)
            
            # Verify content
            with open(original_file, 'r') as f:
                original_content = f.read()
            
            with open(decrypted_file, 'r') as f:
                decrypted_content = f.read()
            
            assert original_content == decrypted_content
            
        finally:
            # Cleanup
            for f in [original_file, encrypted_file, decrypted_file]:
                if os.path.exists(f):
                    os.unlink(f)

    def test_custom_encoding_correctness(self):
        """Test that custom encoding works as demonstrated."""
        from fastcrypter import SecureCompressor
        
        custom_charset = "abcdef98Xvbvii"
        compressor = SecureCompressor(
            password="TestPassword123!",
            custom_charset=custom_charset
        )
        
        test_data = "Test data"
        
        # Test custom encoding
        encoded = compressor.compress_and_encrypt_to_custom(test_data, custom_charset)
        
        # Verify only custom characters are used
        for char in encoded:
            assert char in custom_charset, f"Character '{char}' not in charset"
        
        # Decrypt and verify
        decoded = compressor.decrypt_and_decompress_from_custom(encoded, custom_charset).decode('utf-8')
        assert test_data == decoded

    def test_algorithm_combinations(self):
        """Test various algorithm combinations as shown in examples."""
        from fastcrypter import SecureCompressor
        from fastcrypter.core import CompressionAlgorithmType, EncryptionAlgorithmType
        
        test_data = "Test data for algorithm testing"
        password = "TestPassword123!"
        
        # Test a few combinations
        combinations = [
            (CompressionAlgorithmType.ZLIB, EncryptionAlgorithmType.AES_256_GCM),
            (CompressionAlgorithmType.LZMA, EncryptionAlgorithmType.CHACHA20_POLY1305),
        ]
        
        for comp_algo, enc_algo in combinations:
            compressor = SecureCompressor(
                password=password,
                compression_algorithm=comp_algo,
                encryption_algorithm=enc_algo
            )
            
            encrypted = compressor.compress_and_encrypt(test_data)
            decrypted = compressor.decrypt_and_decompress_to_string(encrypted)
            
            assert test_data == decrypted, \
                f"Failed for {comp_algo.value} + {enc_algo.value}"
