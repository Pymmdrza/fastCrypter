"""
Data Compression System for the Encrypter package.

This module provides high-performance data compression functionality
with support for multiple compression algorithms and optimization levels.
"""

import zlib
import lzma
import brotli
import io
from typing import Union, Dict, Any, Optional, Tuple
from enum import Enum

from ..exceptions import CompressionError, ValidationError, ErrorCodes
from ..algorithms import CompressionAlgorithm


class CompressionLevel(Enum):
    """Compression level enumeration."""
    FASTEST = 1
    FAST = 3
    BALANCED = 6
    BEST = 9


class CompressionAlgorithmType(Enum):
    """Supported compression algorithms."""
    ZLIB = "zlib"
    LZMA = "lzma"
    BROTLI = "brotli"


class Compressor:
    """
    High-performance data compression system.
    
    Supports multiple compression algorithms with configurable compression
    levels and automatic algorithm selection based on data characteristics.
    """
    
    # Algorithm-specific settings
    ALGORITHM_SETTINGS = {
        CompressionAlgorithmType.ZLIB: {
            'min_level': 1,
            'max_level': 9,
            'default_level': 6,
            'chunk_size': 64 * 1024,  # 64KB
        },
        CompressionAlgorithmType.LZMA: {
            'min_level': 0,
            'max_level': 9,
            'default_level': 6,
            'chunk_size': 128 * 1024,  # 128KB
        },
        CompressionAlgorithmType.BROTLI: {
            'min_level': 0,
            'max_level': 11,
            'default_level': 6,
            'chunk_size': 64 * 1024,  # 64KB
        },
    }
    
    def __init__(self, 
                 algorithm: Union[CompressionAlgorithmType, str] = CompressionAlgorithmType.ZLIB,
                 level: Union[CompressionLevel, int] = CompressionLevel.BALANCED,
                 auto_select: bool = False):
        """
        Initialize the Compressor.
        
        Args:
            algorithm: Compression algorithm to use.
            level: Compression level (1-9 for most algorithms).
            auto_select: Whether to automatically select best algorithm.
            
        Raises:
            ValidationError: If parameters are invalid.
        """
        # Handle string algorithm input
        if isinstance(algorithm, str):
            try:
                algorithm = CompressionAlgorithmType(algorithm.lower())
            except ValueError:
                raise ValidationError(
                    f"Unsupported compression algorithm: {algorithm}",
                    ErrorCodes.UNSUPPORTED_COMPRESSION
                )
        
        # Handle integer level input
        if isinstance(level, int):
            level = min(max(level, 1), 9)  # Clamp to valid range
        elif isinstance(level, CompressionLevel):
            level = level.value
        
        self.algorithm = algorithm
        self.level = level
        self.auto_select = auto_select
        
        # Validate level for selected algorithm
        settings = self.ALGORITHM_SETTINGS[algorithm]
        if not (settings['min_level'] <= level <= settings['max_level']):
            raise ValidationError(
                f"Invalid compression level {level} for {algorithm.value}. "
                f"Must be between {settings['min_level']} and {settings['max_level']}",
                ErrorCodes.INVALID_CONFIGURATION
            )
        
        self.chunk_size = settings['chunk_size']
    
    def compress(self, data: Union[str, bytes]) -> bytes:
        """
        Compress data using the configured algorithm.
        
        Args:
            data: Data to compress (string or bytes).
            
        Returns:
            bytes: Compressed data with metadata header.
            
        Raises:
            CompressionError: If compression fails.
            ValidationError: If input data is invalid.
        """
        # Convert string to bytes if necessary
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if not isinstance(data, bytes):
            raise ValidationError(
                "Input data must be string or bytes",
                ErrorCodes.INVALID_INPUT_FORMAT
            )
        
        if len(data) == 0:
            raise ValidationError(
                "Cannot compress empty data",
                ErrorCodes.INVALID_INPUT_SIZE
            )
        
        # Auto-select algorithm if enabled
        if self.auto_select:
            algorithm = self._select_best_algorithm(data)
        else:
            algorithm = self.algorithm
        
        try:
            # Compress data
            if algorithm == CompressionAlgorithmType.ZLIB:
                compressed = self._compress_zlib(data)
            elif algorithm == CompressionAlgorithmType.LZMA:
                compressed = self._compress_lzma(data)
            elif algorithm == CompressionAlgorithmType.BROTLI:
                compressed = self._compress_brotli(data)
            else:
                raise CompressionError(
                    f"Unsupported algorithm: {algorithm}",
                    ErrorCodes.UNSUPPORTED_COMPRESSION
                )
            
            # Add metadata header
            header = self._create_header(algorithm, len(data))
            result = header + compressed
            
            # Validate compression ratio
            ratio = len(result) / len(data)
            if ratio > 1.1:  # If compressed size is more than 110% of original
                # Return original data with special header indicating no compression
                no_comp_header = self._create_header(None, len(data))
                result = no_comp_header + data
            
            return result
            
        except Exception as e:
            raise CompressionError(
                f"Compression failed: {str(e)}",
                ErrorCodes.COMPRESSION_FAILED,
                details={"algorithm": algorithm.value if algorithm else None, "error": str(e)}
            )
    
    def decompress(self, data: bytes) -> bytes:
        """
        Decompress data.
        
        Args:
            data: Compressed data with metadata header.
            
        Returns:
            bytes: Decompressed data.
            
        Raises:
            CompressionError: If decompression fails.
            ValidationError: If input data is invalid.
        """
        if not isinstance(data, bytes):
            raise ValidationError(
                "Input data must be bytes",
                ErrorCodes.INVALID_INPUT_FORMAT
            )
        
        if len(data) < 8:  # Minimum header size
            raise ValidationError(
                "Data too small to contain valid header",
                ErrorCodes.INVALID_INPUT_SIZE
            )
        
        try:
            # Parse header
            algorithm, original_size = self._parse_header(data)
            compressed_data = data[8:]  # Skip 8-byte header
            
            # Handle uncompressed data
            if algorithm is None:
                return compressed_data
            
            # Decompress data
            if algorithm == CompressionAlgorithmType.ZLIB:
                result = self._decompress_zlib(compressed_data)
            elif algorithm == CompressionAlgorithmType.LZMA:
                result = self._decompress_lzma(compressed_data)
            elif algorithm == CompressionAlgorithmType.BROTLI:
                result = self._decompress_brotli(compressed_data)
            else:
                raise CompressionError(
                    f"Unsupported algorithm in header: {algorithm}",
                    ErrorCodes.UNSUPPORTED_COMPRESSION
                )
            
            # Validate decompressed size
            if len(result) != original_size:
                raise CompressionError(
                    f"Decompressed size mismatch: expected {original_size}, got {len(result)}",
                    ErrorCodes.DECOMPRESSION_FAILED
                )
            
            return result
            
        except CompressionError:
            raise
        except Exception as e:
            raise CompressionError(
                f"Decompression failed: {str(e)}",
                ErrorCodes.DECOMPRESSION_FAILED,
                details={"error": str(e)}
            )
    
    def _compress_zlib(self, data: bytes) -> bytes:
        """Compress data using zlib."""
        return zlib.compress(data, level=self.level)
    
    def _decompress_zlib(self, data: bytes) -> bytes:
        """Decompress zlib data."""
        return zlib.decompress(data)
    
    def _compress_lzma(self, data: bytes) -> bytes:
        """Compress data using LZMA."""
        return lzma.compress(
            data,
            format=lzma.FORMAT_ALONE,
            preset=self.level
        )
    
    def _decompress_lzma(self, data: bytes) -> bytes:
        """Decompress LZMA data."""
        return lzma.decompress(data, format=lzma.FORMAT_ALONE)
    
    def _compress_brotli(self, data: bytes) -> bytes:
        """Compress data using Brotli."""
        return brotli.compress(data, quality=self.level)
    
    def _decompress_brotli(self, data: bytes) -> bytes:
        """Decompress Brotli data."""
        return brotli.decompress(data)
    
    def _select_best_algorithm(self, data: bytes) -> CompressionAlgorithmType:
        """
        Automatically select the best compression algorithm for the data.
        
        Args:
            data: Data to analyze.
            
        Returns:
            CompressionAlgorithmType: Best algorithm for the data.
        """
        # For small data, use zlib (fastest)
        if len(data) < 1024:
            return CompressionAlgorithmType.ZLIB
        
        # Analyze data characteristics
        entropy = self._calculate_entropy(data)
        
        # High entropy data (already compressed/encrypted) - use fastest
        if entropy > 7.5:
            return CompressionAlgorithmType.ZLIB
        
        # Low entropy data - use best compression
        if entropy < 4.0:
            return CompressionAlgorithmType.LZMA
        
        # Medium entropy - use balanced approach
        return CompressionAlgorithmType.BROTLI
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if not data:
            return 0.0
        
        # Count byte frequencies
        frequencies = {}
        for byte in data:
            frequencies[byte] = frequencies.get(byte, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(data)
        for count in frequencies.values():
            probability = count / length
            if probability > 0:
                import math
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _create_header(self, algorithm: Optional[CompressionAlgorithmType], original_size: int) -> bytes:
        """
        Create metadata header for compressed data.
        
        Header format (8 bytes):
        - 1 byte: Algorithm ID (0=none, 1=zlib, 2=lzma, 3=brotli)
        - 1 byte: Compression level
        - 2 bytes: Reserved
        - 4 bytes: Original size (little-endian)
        """
        if algorithm is None:
            algo_id = 0
        else:
            algo_map = {
                CompressionAlgorithmType.ZLIB: 1,
                CompressionAlgorithmType.LZMA: 2,
                CompressionAlgorithmType.BROTLI: 3,
            }
            algo_id = algo_map[algorithm]
        
        header = bytearray(8)
        header[0] = algo_id
        header[1] = self.level
        header[2:4] = b'\x00\x00'  # Reserved
        header[4:8] = original_size.to_bytes(4, 'little')
        
        return bytes(header)
    
    def _parse_header(self, data: bytes) -> Tuple[Optional[CompressionAlgorithmType], int]:
        """
        Parse metadata header from compressed data.
        
        Returns:
            Tuple[Optional[CompressionAlgorithmType], int]: (algorithm, original_size)
        """
        header = data[:8]
        
        algo_id = header[0]
        if algo_id == 0:
            algorithm = None
        else:
            algo_map = {
                1: CompressionAlgorithmType.ZLIB,
                2: CompressionAlgorithmType.LZMA,
                3: CompressionAlgorithmType.BROTLI,
            }
            algorithm = algo_map.get(algo_id)
            if algorithm is None:
                raise CompressionError(
                    f"Unknown algorithm ID in header: {algo_id}",
                    ErrorCodes.INVALID_INPUT_FORMAT
                )
        
        original_size = int.from_bytes(header[4:8], 'little')
        
        return algorithm, original_size
    
    def get_compression_ratio(self, original_data: bytes, compressed_data: bytes) -> float:
        """
        Calculate compression ratio.
        
        Args:
            original_data: Original uncompressed data.
            compressed_data: Compressed data.
            
        Returns:
            float: Compression ratio (compressed_size / original_size).
        """
        if len(original_data) == 0:
            return 0.0
        
        return len(compressed_data) / len(original_data)
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the compressor configuration.
        
        Returns:
            Dict[str, Any]: Configuration information.
        """
        return {
            "algorithm": self.algorithm.value,
            "level": self.level,
            "auto_select": self.auto_select,
            "chunk_size": self.chunk_size,
            "supported_algorithms": [algo.value for algo in CompressionAlgorithmType],
        } 