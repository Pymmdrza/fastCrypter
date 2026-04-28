"""
Tests for Compressor class.
"""

import pytest
from fastcrypter.core import Compressor, CompressionAlgorithmType, CompressionLevel
from fastcrypter.exceptions import CompressionError, ValidationError


class TestCompressor:
    """Test suite for Compressor class."""

    def test_init_default(self):
        """Test default initialization."""
        compressor = Compressor()
        assert compressor.algorithm == CompressionAlgorithmType.ZLIB
        assert compressor.level == CompressionLevel.BALANCED.value

    def test_init_custom(self):
        """Test custom initialization."""
        compressor = Compressor(
            algorithm=CompressionAlgorithmType.LZMA,
            level=CompressionLevel.BEST
        )
        assert compressor.algorithm == CompressionAlgorithmType.LZMA
        assert compressor.level == 9

    def test_compress_decompress_zlib(self):
        """Test ZLIB compression and decompression."""
        compressor = Compressor(algorithm=CompressionAlgorithmType.ZLIB)
        data = b"Hello, World! " * 100
        
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        assert data == decompressed
        assert len(compressed) < len(data)

    def test_compress_decompress_lzma(self):
        """Test LZMA compression and decompression."""
        compressor = Compressor(algorithm=CompressionAlgorithmType.LZMA)
        data = b"Test data " * 50
        
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        assert data == decompressed

    def test_compress_decompress_brotli(self):
        """Test Brotli compression and decompression."""
        compressor = Compressor(algorithm=CompressionAlgorithmType.BROTLI)
        data = b"Brotli test " * 50
        
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        
        assert data == decompressed

    def test_compress_string(self):
        """Test compression of string data."""
        compressor = Compressor()
        text = "String data test"
        
        compressed = compressor.compress(text)
        decompressed = compressor.decompress(compressed)
        
        assert text.encode('utf-8') == decompressed

    def test_empty_data_error(self):
        """Test that empty data raises error."""
        compressor = Compressor()
        
        with pytest.raises(ValidationError):
            compressor.compress(b"")

    def test_invalid_data_type_error(self):
        """Test that invalid data type raises error."""
        compressor = Compressor()
        
        with pytest.raises(ValidationError):
            compressor.compress(12345)

    def test_compression_ratio(self):
        """Test compression ratio calculation."""
        compressor = Compressor()
        data = b"Test " * 100
        
        compressed = compressor.compress(data)
        ratio = compressor.get_compression_ratio(data, compressed)
        
        assert 0 < ratio < 1  # Should be compressed

    def test_auto_select(self):
        """Test automatic algorithm selection."""
        compressor = Compressor(auto_select=True)
        
        # Small data
        small_data = b"Small"
        compressed_small = compressor.compress(small_data)
        assert len(compressed_small) > 0
        
        # Large data
        large_data = b"Large data " * 1000
        compressed_large = compressor.compress(large_data)
        assert compressor.decompress(compressed_large) == large_data

    def test_different_levels(self):
        """Test different compression levels."""
        data = b"Level test " * 100
        
        for level in [1, 3, 6, 9]:
            compressor = Compressor(level=level)
            compressed = compressor.compress(data)
            decompressed = compressor.decompress(compressed)
            assert data == decompressed

    def test_get_info(self):
        """Test get_info method."""
        compressor = Compressor()
        info = compressor.get_info()
        
        assert 'algorithm' in info
        assert 'level' in info
        assert 'supported_algorithms' in info
