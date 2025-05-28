"""
Enhanced Compressor with Native Library Integration

This module provides an enhanced version of the compressor that automatically
uses native C/C++ libraries when available for maximum performance.
"""

from typing import Union, Optional, Dict, Any
from .compressor import Compressor, CompressionAlgorithmType, CompressionLevel
from .encryptor import Encryptor, EncryptionAlgorithmType
from .key_manager import KeyManager
from .custom_encoder import CustomEncoder
from ..exceptions import EncrypterError, ValidationError, ErrorCodes

# Import native library support
try:
    from ..native.native_loader import (
        get_native_manager, get_crypto_core, get_hash_algorithms, is_native_available
    )
    NATIVE_SUPPORT = True
except ImportError:
    NATIVE_SUPPORT = False


class EnhancedCompressor:
    """
    Enhanced compressor with native library integration for maximum performance.
    
    This class automatically detects and uses native C/C++ libraries when available,
    falling back to pure Python implementations when necessary.
    """
    
    def __init__(self,
                 password: str,
                 compression_algorithm: Union[CompressionAlgorithmType, str] = CompressionAlgorithmType.ZLIB,
                 compression_level: Union[CompressionLevel, int] = CompressionLevel.BALANCED,
                 encryption_algorithm: Union[EncryptionAlgorithmType, str] = EncryptionAlgorithmType.AES_256_GCM,
                 auto_select_compression: bool = True,
                 kdf_algorithm: str = 'pbkdf2',
                 kdf_iterations: int = 100000,
                 custom_charset: Optional[str] = None,
                 prefer_native: bool = True):
        """
        Initialize the EnhancedCompressor.
        
        Args:
            password (str): Password for encryption key derivation.
            compression_algorithm: Compression algorithm to use.
            compression_level: Compression level (1-9).
            encryption_algorithm: Encryption algorithm to use.
            auto_select_compression (bool): Auto-select best compression algorithm.
            kdf_algorithm (str): Key derivation function algorithm.
            kdf_iterations (int): Number of KDF iterations.
            custom_charset (str, optional): Custom character set for encoding output.
            prefer_native (bool): Prefer native libraries when available.
        """
        # Validate password
        if not password or len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long",
                ErrorCodes.KEY_TOO_WEAK
            )
        
        self.password = password
        self.prefer_native = prefer_native and NATIVE_SUPPORT
        
        # Initialize native library manager
        if self.prefer_native:
            self.native_manager = get_native_manager()
            self.crypto_core = get_crypto_core()
            self.hash_algorithms = get_hash_algorithms()
        else:
            self.native_manager = None
            self.crypto_core = None
            self.hash_algorithms = None
        
        # Initialize standard components
        self.compressor = Compressor(
            algorithm=compression_algorithm,
            level=compression_level,
            auto_select=auto_select_compression
        )
        
        self.encryptor = Encryptor(
            algorithm=encryption_algorithm,
            derive_key=True
        )
        
        self.key_manager = KeyManager(
            kdf_algorithm=kdf_algorithm,
            iterations=kdf_iterations
        )
        
        # Initialize custom encoder if charset provided
        self.custom_encoder = None
        if custom_charset:
            self.custom_encoder = CustomEncoder(charset=custom_charset)
        
        # Store configuration
        self.config = {
            'compression_algorithm': compression_algorithm,
            'compression_level': compression_level,
            'encryption_algorithm': encryption_algorithm,
            'auto_select_compression': auto_select_compression,
            'kdf_algorithm': kdf_algorithm,
            'kdf_iterations': kdf_iterations,
            'custom_charset': custom_charset,
            'prefer_native': self.prefer_native,
            'native_available': self.is_native_available(),
        }
    
    def is_native_available(self) -> bool:
        """Check if native libraries are available."""
        return self.prefer_native and (self.crypto_core is not None or self.hash_algorithms is not None)
    
    def _fast_key_derivation(self, password: str, salt: bytes, iterations: int, key_length: int) -> bytes:
        """Use native key derivation if available."""
        if self.hash_algorithms:
            try:
                password_bytes = password.encode('utf-8')
                return self.hash_algorithms.fast_pbkdf2(password_bytes, salt, iterations, key_length)
            except Exception:
                pass
        
        # Fallback to standard key manager
        return self.key_manager.derive_key(password, salt, key_length)
    
    def _fast_compression(self, data: bytes) -> bytes:
        """Use native compression if available."""
        if self.crypto_core:
            try:
                # Try native RLE compression first
                compressed = self.crypto_core.fast_compress_rle(data)
                if len(compressed) < len(data):
                    return compressed
            except Exception:
                pass
        
        # Fallback to standard compressor
        return self.compressor.compress(data)
    
    def _fast_decompression(self, data: bytes) -> bytes:
        """Use native decompression if available."""
        if self.crypto_core:
            try:
                # Check if this looks like RLE compressed data
                if len(data) > 0 and data[0] == 0xFF:
                    return self.crypto_core.fast_decompress_rle(data)
            except Exception:
                pass
        
        # Fallback to standard compressor
        return self.compressor.decompress(data)
    
    def _fast_xor_encryption(self, data: bytes, key: bytes) -> bytes:
        """Use native XOR if available for additional obfuscation."""
        if self.crypto_core:
            try:
                return self.crypto_core.fast_xor(data, key)
            except Exception:
                pass
        
        # Fallback to Python XOR
        result = bytearray(data)
        for i in range(len(result)):
            result[i] ^= key[i % len(key)]
        return bytes(result)
    
    def _fast_hash(self, data: bytes) -> bytes:
        """Use native SHA-256 if available."""
        if self.hash_algorithms:
            try:
                return self.hash_algorithms.fast_sha256(data)
            except Exception:
                pass
        
        # Fallback to standard hash
        import hashlib
        return hashlib.sha256(data).digest()
    
    def _fast_hmac(self, key: bytes, data: bytes) -> bytes:
        """Use native HMAC if available."""
        if self.hash_algorithms:
            try:
                return self.hash_algorithms.fast_hmac_sha256(key, data)
            except Exception:
                pass
        
        # Fallback to standard HMAC
        import hmac
        import hashlib
        return hmac.new(key, data, hashlib.sha256).digest()
    
    def _fast_custom_encoding(self, data: bytes, charset: str) -> str:
        """Use native base conversion if available."""
        if self.crypto_core:
            try:
                return self.crypto_core.base_convert_encode(data, charset)
            except Exception:
                pass
        
        # Fallback to custom encoder
        if self.custom_encoder and self.custom_encoder.charset == charset:
            return self.custom_encoder.encode(data)
        
        temp_encoder = CustomEncoder(charset=charset)
        return temp_encoder.encode(data)
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate data entropy using native library if available."""
        if self.crypto_core:
            try:
                return self.crypto_core.calculate_entropy(data)
            except Exception:
                pass
        
        # Fallback to Python implementation
        if not data:
            return 0.0
        
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1
        
        entropy = 0.0
        length = len(data)
        for count in freq.values():
            p = count / length
            if p > 0:
                # Use approximation: log2(p) ≈ (p.bit_length() - 1) for integers
                # For floats, we'll use a simple approximation
                import math
                entropy -= p * math.log2(p)
        
        return entropy
    
    def compress_and_encrypt(self, data: Union[str, bytes], 
                           output_format: str = 'binary',
                           use_native_optimizations: bool = True) -> Union[bytes, str]:
        """
        Compress and encrypt data with native optimizations.
        
        Args:
            data: Data to compress and encrypt.
            output_format: Output format ('binary', 'custom', 'steganographic').
            use_native_optimizations: Use native libraries for optimization.
            
        Returns:
            Union[bytes, str]: Encrypted compressed data.
        """
        try:
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Step 1: Analyze data for optimal compression
            entropy = self._calculate_entropy(data_bytes)
            
            # Step 2: Compress data (with native optimization if available)
            if use_native_optimizations and self.is_native_available():
                compressed_data = self._fast_compression(data_bytes)
            else:
                compressed_data = self.compressor.compress(data_bytes)
            
            # Step 3: Generate encryption key with native optimization
            salt = self._generate_salt()
            if use_native_optimizations and self.hash_algorithms:
                key = self._fast_key_derivation(self.password, salt, self.key_manager.iterations, 32)
            else:
                key = self.key_manager.derive_key(self.password, salt, 32)
            
            # Step 4: Apply additional XOR obfuscation with native optimization
            if use_native_optimizations and self.crypto_core:
                xor_key = self._fast_hash(key + salt)[:16]  # 16-byte XOR key
                obfuscated_data = self._fast_xor_encryption(compressed_data, xor_key)
            else:
                obfuscated_data = compressed_data
            
            # Step 5: Encrypt data
            encrypted_data = self.encryptor.encrypt(obfuscated_data, self.password)
            
            # Step 6: Apply custom encoding if requested
            if output_format == 'binary':
                return encrypted_data
            elif output_format == 'custom' and self.custom_encoder:
                if use_native_optimizations and self.crypto_core:
                    return self._fast_custom_encoding(encrypted_data, self.custom_encoder.charset)
                else:
                    return self.custom_encoder.encode(encrypted_data)
            elif output_format == 'steganographic' and self.custom_encoder:
                return self.custom_encoder.create_steganographic_text(encrypted_data)
            else:
                return encrypted_data
            
        except Exception as e:
            raise EncrypterError(
                f"Enhanced compression failed: {str(e)}",
                details={
                    "operation": "compress_and_encrypt",
                    "native_used": use_native_optimizations and self.is_native_available(),
                    "error": str(e)
                }
            )
    
    def decrypt_and_decompress(self, data: Union[bytes, str], 
                             input_format: str = 'binary',
                             use_native_optimizations: bool = True) -> bytes:
        """
        Decrypt and decompress data with native optimizations.
        
        Args:
            data: Encrypted compressed data to decrypt and decompress.
            input_format: Input format ('binary', 'custom', 'steganographic').
            use_native_optimizations: Use native libraries for optimization.
            
        Returns:
            bytes: Original decompressed data.
        """
        try:
            # Step 1: Decode from custom format if necessary
            if input_format == 'custom' and self.custom_encoder and isinstance(data, str):
                encrypted_data = self.custom_encoder.decode(data)
            elif input_format == 'binary':
                encrypted_data = data
            else:
                encrypted_data = data
            
            # Step 2: Decrypt data
            decrypted_data = self.encryptor.decrypt(encrypted_data, self.password)
            
            # Step 3: Remove XOR obfuscation if it was applied
            if use_native_optimizations and self.crypto_core:
                # Try to detect if XOR was applied by checking entropy
                entropy = self._calculate_entropy(decrypted_data)
                if entropy > 7.0:  # High entropy suggests XOR was applied
                    # Reconstruct XOR key
                    salt = encrypted_data[:16]  # Assume salt is in first 16 bytes
                    key = self._fast_key_derivation(self.password, salt, self.key_manager.iterations, 32)
                    xor_key = self._fast_hash(key + salt)[:16]
                    deobfuscated_data = self._fast_xor_encryption(decrypted_data, xor_key)
                else:
                    deobfuscated_data = decrypted_data
            else:
                deobfuscated_data = decrypted_data
            
            # Step 4: Decompress data (with native optimization if available)
            if use_native_optimizations and self.is_native_available():
                decompressed_data = self._fast_decompression(deobfuscated_data)
            else:
                decompressed_data = self.compressor.decompress(deobfuscated_data)
            
            return decompressed_data
            
        except Exception as e:
            raise EncrypterError(
                f"Enhanced decompression failed: {str(e)}",
                details={
                    "operation": "decrypt_and_decompress",
                    "native_used": use_native_optimizations and self.is_native_available(),
                    "error": str(e)
                }
            )
    
    def _generate_salt(self) -> bytes:
        """Generate cryptographically secure salt."""
        if self.crypto_core:
            try:
                return self.crypto_core.secure_random_bytes(16)
            except Exception:
                pass
        
        # Fallback to standard random
        import secrets
        return secrets.token_bytes(16)
    
    def benchmark_native_vs_python(self, data_size: int = 1024, iterations: int = 100) -> Dict[str, Any]:
        """
        Benchmark native vs Python implementations.
        
        Args:
            data_size: Size of test data in bytes.
            iterations: Number of iterations for benchmarking.
            
        Returns:
            Dict[str, Any]: Benchmark results.
        """
        import time
        import secrets
        
        # Generate test data
        test_data = secrets.token_bytes(data_size)
        
        results = {
            'data_size': data_size,
            'iterations': iterations,
            'native_available': self.is_native_available()
        }
        
        if not self.is_native_available():
            results['error'] = 'Native libraries not available'
            return results
        
        # Benchmark compression
        if self.crypto_core:
            # Native compression
            start_time = time.time()
            for _ in range(iterations):
                compressed = self.crypto_core.fast_compress_rle(test_data)
            native_compress_time = time.time() - start_time
            
            # Python compression
            start_time = time.time()
            for _ in range(iterations):
                compressed = self.compressor.compress(test_data)
            python_compress_time = time.time() - start_time
            
            results['compression'] = {
                'native_time': native_compress_time,
                'python_time': python_compress_time,
                'speedup': python_compress_time / native_compress_time if native_compress_time > 0 else 0
            }
        
        # Benchmark hashing
        if self.hash_algorithms:
            # Native hashing
            start_time = time.time()
            for _ in range(iterations):
                hash_result = self.hash_algorithms.fast_sha256(test_data)
            native_hash_time = time.time() - start_time
            
            # Python hashing
            import hashlib
            start_time = time.time()
            for _ in range(iterations):
                hash_result = hashlib.sha256(test_data).digest()
            python_hash_time = time.time() - start_time
            
            results['hashing'] = {
                'native_time': native_hash_time,
                'python_time': python_hash_time,
                'speedup': python_hash_time / native_hash_time if native_hash_time > 0 else 0
            }
        
        # Benchmark key derivation
        if self.hash_algorithms:
            password = b"test_password"
            salt = b"test_salt_16bytes"
            
            # Native PBKDF2
            start_time = time.time()
            for _ in range(10):  # Fewer iterations for expensive operation
                key = self.hash_algorithms.fast_pbkdf2(password, salt, 1000, 32)
            native_kdf_time = time.time() - start_time
            
            # Python PBKDF2
            start_time = time.time()
            for _ in range(10):
                key = self.key_manager.derive_key("test_password", salt, 32)
            python_kdf_time = time.time() - start_time
            
            results['key_derivation'] = {
                'native_time': native_kdf_time,
                'python_time': python_kdf_time,
                'speedup': python_kdf_time / native_kdf_time if native_kdf_time > 0 else 0
            }
        
        return results
    
    def get_native_info(self) -> Dict[str, Any]:
        """Get information about native library availability and performance."""
        info = {
            'native_support': NATIVE_SUPPORT,
            'prefer_native': self.prefer_native,
            'native_available': self.is_native_available(),
            'libraries': {}
        }
        
        if self.native_manager:
            manager_info = self.native_manager.get_info()
            info.update(manager_info)
            
            # Add performance info
            if self.hash_algorithms:
                try:
                    perf_time = self.hash_algorithms.benchmark_hash_performance(1024, 100)
                    info['hash_performance'] = {
                        'time_seconds': perf_time,
                        'throughput_mbps': (1024 * 100 / (1024 * 1024)) / perf_time if perf_time > 0 else 0
                    }
                except Exception as e:
                    info['hash_performance'] = {'error': str(e)}
        
        return info
    
    def get_info(self) -> Dict[str, Any]:
        """Get comprehensive information about the EnhancedCompressor."""
        base_info = {
            'version': '2.0.0',
            'type': 'EnhancedCompressor',
            'configuration': self.config,
        }
        
        # Add native library info
        base_info['native'] = self.get_native_info()
        
        # Add standard component info
        base_info['compressor_info'] = self.compressor.get_info()
        base_info['encryptor_info'] = self.encryptor.get_info()
        base_info['key_manager_info'] = self.key_manager.get_info()
        
        if self.custom_encoder:
            base_info['custom_encoder_info'] = self.custom_encoder.get_charset_info()
        
        return base_info
    
    def __repr__(self) -> str:
        """String representation of the EnhancedCompressor."""
        native_status = "native" if self.is_native_available() else "python"
        charset_info = f", charset={self.custom_encoder.charset}" if self.custom_encoder else ""
        
        return (f"EnhancedCompressor("
                f"compression={self.compressor.algorithm.value}, "
                f"encryption={self.encryptor.algorithm.value}, "
                f"mode={native_status}"
                f"{charset_info})")
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        base_str = (f"Enhanced Compressor with {self.compressor.algorithm.value.upper()} compression "
                   f"and {self.encryptor.algorithm.value.upper()} encryption")
        
        if self.is_native_available():
            base_str += " (native acceleration enabled)"
        else:
            base_str += " (pure Python mode)"
        
        if self.custom_encoder:
            base_str += f" using custom charset '{self.custom_encoder.charset}'"
        
        return base_str 