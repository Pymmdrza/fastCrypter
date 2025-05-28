"""
Secure Compressor - High-level interface for compression and encryption.

This module provides a simple, secure interface that combines compression
and encryption in a single operation for maximum security and efficiency.
"""

from typing import Union, Optional, Dict, Any
from .core.compressor import Compressor, CompressionAlgorithmType, CompressionLevel
from .core.encryptor import Encryptor, EncryptionAlgorithmType
from .core.key_manager import KeyManager
from .core.custom_encoder import CustomEncoder
from .exceptions import EncrypterError, ValidationError, ErrorCodes

# Try to import C/C++ extensions for speed
try:
    from .core import fast_crypto
    FAST_CRYPTO_AVAILABLE = True
except ImportError:
    FAST_CRYPTO_AVAILABLE = False

try:
    from .core import fast_compression
    FAST_COMPRESSION_AVAILABLE = True
except ImportError:
    FAST_COMPRESSION_AVAILABLE = False


class SecureCompressor:
    """
    High-level secure compressor that combines compression and encryption.
    
    This class provides a simple interface for securely compressing and
    encrypting data in a single operation, with automatic algorithm selection
    and key management. Now includes custom encoding for specified character sets.
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
                 use_fast_extensions: bool = True):
        """
        Initialize the SecureCompressor.
        
        Args:
            password (str): Password for encryption key derivation.
            compression_algorithm: Compression algorithm to use.
            compression_level: Compression level (1-9).
            encryption_algorithm: Encryption algorithm to use.
            auto_select_compression (bool): Auto-select best compression algorithm.
            kdf_algorithm (str): Key derivation function algorithm.
            kdf_iterations (int): Number of KDF iterations.
            custom_charset (str, optional): Custom character set for encoding output.
            use_fast_extensions (bool): Use C/C++ extensions if available.
            
        Raises:
            ValidationError: If parameters are invalid.
        """
        # Validate password
        if not password or len(password) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long",
                ErrorCodes.KEY_TOO_WEAK
            )
        
        self.password = password
        self.use_fast_extensions = use_fast_extensions and (FAST_CRYPTO_AVAILABLE or FAST_COMPRESSION_AVAILABLE)
        
        # Initialize components
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
            'use_fast_extensions': self.use_fast_extensions,
        }
    
    def compress_and_encrypt(self, data: Union[str, bytes], 
                           output_format: str = 'binary') -> Union[bytes, str]:
        """
        Compress and encrypt data in a single operation.
        
        The process follows these steps:
        1. Compress the data using the configured compression algorithm
        2. Encrypt the compressed data using the configured encryption algorithm
        3. Optionally encode to custom character set
        
        Args:
            data: Data to compress and encrypt (string or bytes).
            output_format: Output format ('binary', 'custom', 'steganographic').
            
        Returns:
            Union[bytes, str]: Encrypted compressed data.
            
        Raises:
            EncrypterError: If compression or encryption fails.
            ValidationError: If input data is invalid.
        """
        try:
            # Step 1: Compress data (with fast extension if available)
            if self.use_fast_extensions and FAST_COMPRESSION_AVAILABLE:
                if isinstance(data, str):
                    data = data.encode('utf-8')
                compressed_data = fast_compression.fast_compress(data)
            else:
                compressed_data = self.compressor.compress(data)
            
            # Step 2: Encrypt compressed data
            encrypted_data = self.encryptor.encrypt(compressed_data, self.password)
            
            # Step 3: Apply custom encoding if requested
            if output_format == 'binary':
                return encrypted_data
            elif output_format == 'custom' and self.custom_encoder:
                return self.custom_encoder.encode(encrypted_data)
            elif output_format == 'steganographic' and self.custom_encoder:
                return self.custom_encoder.create_steganographic_text(encrypted_data)
            else:
                return encrypted_data
            
        except Exception as e:
            raise EncrypterError(
                f"Secure compression failed: {str(e)}",
                details={"operation": "compress_and_encrypt", "error": str(e)}
            )
    
    def decrypt_and_decompress(self, data: Union[bytes, str], 
                             input_format: str = 'binary') -> bytes:
        """
        Decrypt and decompress data in a single operation.
        
        The process follows these steps:
        1. Decode from custom format if necessary
        2. Decrypt the data using the configured encryption algorithm
        3. Decompress the decrypted data using the appropriate compression algorithm
        4. Return the original data
        
        Args:
            data: Encrypted compressed data to decrypt and decompress.
            input_format: Input format ('binary', 'custom', 'steganographic').
            
        Returns:
            bytes: Original decompressed data.
            
        Raises:
            EncrypterError: If decryption or decompression fails.
            ValidationError: If input data is invalid.
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
            
            # Step 3: Decompress decrypted data (with fast extension if available)
            if self.use_fast_extensions and FAST_COMPRESSION_AVAILABLE:
                decompressed_data = fast_compression.fast_decompress(decrypted_data)
            else:
                decompressed_data = self.compressor.decompress(decrypted_data)
            
            return decompressed_data
            
        except Exception as e:
            raise EncrypterError(
                f"Secure decompression failed: {str(e)}",
                details={"operation": "decrypt_and_decompress", "error": str(e)}
            )
    
    def compress_and_encrypt_to_custom(self, data: Union[str, bytes], 
                                     charset: str = "abcdef98Xvbvii") -> str:
        """
        Compress, encrypt, and encode to custom character set.
        
        Args:
            data: Data to process.
            charset: Custom character set to use.
            
        Returns:
            str: Encoded string using only specified characters.
        """
        # Create temporary encoder if different charset
        if not self.custom_encoder or self.custom_encoder.charset != charset:
            temp_encoder = CustomEncoder(charset=charset)
        else:
            temp_encoder = self.custom_encoder
        
        # Compress and encrypt
        encrypted_data = self.compress_and_encrypt(data, output_format='binary')
        
        # Encode to custom charset
        return temp_encoder.encode(encrypted_data)
    
    def decrypt_and_decompress_from_custom(self, encoded_data: str, 
                                         charset: str = "abcdef98Xvbvii") -> bytes:
        """
        Decode from custom character set, decrypt, and decompress.
        
        Args:
            encoded_data: Data encoded with custom charset.
            charset: Custom character set used for encoding.
            
        Returns:
            bytes: Original data.
        """
        # Create temporary encoder if different charset
        if not self.custom_encoder or self.custom_encoder.charset != charset:
            temp_encoder = CustomEncoder(charset=charset)
        else:
            temp_encoder = self.custom_encoder
        
        # Decode from custom charset
        encrypted_data = temp_encoder.decode(encoded_data)
        
        # Decrypt and decompress
        return self.decrypt_and_decompress(encrypted_data, input_format='binary')
    
    def compress_and_encrypt_string(self, text: str, 
                                  output_format: str = 'binary') -> Union[bytes, str]:
        """
        Compress and encrypt a string, returning encrypted data.
        
        Args:
            text (str): Text to compress and encrypt.
            output_format: Output format ('binary', 'custom', 'steganographic').
            
        Returns:
            Union[bytes, str]: Encrypted compressed data.
        """
        return self.compress_and_encrypt(text, output_format)
    
    def decrypt_and_decompress_to_string(self, data: Union[bytes, str], 
                                       input_format: str = 'binary',
                                       encoding: str = 'utf-8') -> str:
        """
        Decrypt and decompress data, returning a string.
        
        Args:
            data: Encrypted compressed data.
            input_format: Input format ('binary', 'custom', 'steganographic').
            encoding (str): Text encoding to use for decoding.
            
        Returns:
            str: Original text.
            
        Raises:
            UnicodeDecodeError: If data cannot be decoded as text.
        """
        decompressed_data = self.decrypt_and_decompress(data, input_format)
        return decompressed_data.decode(encoding)
    
    def get_compression_ratio(self, original_data: Union[str, bytes], 
                            compressed_encrypted_data: Union[bytes, str]) -> float:
        """
        Calculate the overall compression ratio (including encryption overhead).
        
        Args:
            original_data: Original uncompressed data.
            compressed_encrypted_data: Final encrypted compressed data.
            
        Returns:
            float: Compression ratio (final_size / original_size).
        """
        if isinstance(original_data, str):
            original_data = original_data.encode('utf-8')
        
        if len(original_data) == 0:
            return 0.0
        
        if isinstance(compressed_encrypted_data, str):
            final_size = len(compressed_encrypted_data.encode('utf-8'))
        else:
            final_size = len(compressed_encrypted_data)
        
        return final_size / len(original_data)
    
    def estimate_output_size(self, input_size: int, output_format: str = 'binary') -> Dict[str, int]:
        """
        Estimate the output size for given input size.
        
        Args:
            input_size (int): Size of input data in bytes.
            output_format: Output format to estimate for.
            
        Returns:
            Dict[str, int]: Estimated sizes for different stages.
        """
        # Rough estimates based on typical compression ratios and encryption overhead
        compression_ratios = {
            CompressionAlgorithmType.ZLIB: 0.6,
            CompressionAlgorithmType.LZMA: 0.4,
            CompressionAlgorithmType.BROTLI: 0.5,
        }
        
        # Get compression ratio estimate
        comp_ratio = compression_ratios.get(self.compressor.algorithm, 0.6)
        compressed_size = int(input_size * comp_ratio) + 8  # Add header overhead
        
        # Encryption adds overhead (headers, IV, tag, etc.)
        encryption_overhead = 64  # Conservative estimate
        encrypted_size = compressed_size + encryption_overhead
        
        # Custom encoding overhead
        if output_format == 'custom' and self.custom_encoder:
            # Base conversion typically increases size
            custom_size = int(encrypted_size * 1.4)  # Rough estimate
        else:
            custom_size = encrypted_size
        
        return {
            'original_size': input_size,
            'estimated_compressed_size': compressed_size,
            'estimated_encrypted_size': encrypted_size,
            'estimated_final_size': custom_size,
            'estimated_compression_ratio': comp_ratio,
            'estimated_total_ratio': custom_size / input_size if input_size > 0 else 0,
        }
    
    def change_password(self, new_password: str) -> None:
        """
        Change the password used for encryption.
        
        Args:
            new_password (str): New password to use.
            
        Raises:
            ValidationError: If new password is too weak.
        """
        if not new_password or len(new_password) < 8:
            raise ValidationError(
                "New password must be at least 8 characters long",
                ErrorCodes.KEY_TOO_WEAK
            )
        
        self.password = new_password
    
    def set_custom_charset(self, charset: str) -> None:
        """
        Set or change the custom character set for encoding.
        
        Args:
            charset (str): New character set to use.
        """
        self.custom_encoder = CustomEncoder(charset=charset)
        self.config['custom_charset'] = charset
    
    def validate_password_strength(self, password: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate password strength.
        
        Args:
            password (str, optional): Password to validate. Uses current password if None.
            
        Returns:
            Dict[str, Any]: Password strength analysis.
        """
        pwd = password or self.password
        
        # Basic strength checks
        length_ok = len(pwd) >= 8
        has_upper = any(c.isupper() for c in pwd)
        has_lower = any(c.islower() for c in pwd)
        has_digit = any(c.isdigit() for c in pwd)
        has_special = any(not c.isalnum() for c in pwd)
        
        # Calculate strength score
        score = 0
        if length_ok:
            score += 1
        if len(pwd) >= 12:
            score += 1
        if has_upper:
            score += 1
        if has_lower:
            score += 1
        if has_digit:
            score += 1
        if has_special:
            score += 1
        
        # Determine strength level
        if score >= 5:
            strength = "Strong"
        elif score >= 3:
            strength = "Medium"
        else:
            strength = "Weak"
        
        return {
            'strength': strength,
            'score': score,
            'max_score': 6,
            'checks': {
                'length_ok': length_ok,
                'has_uppercase': has_upper,
                'has_lowercase': has_lower,
                'has_digits': has_digit,
                'has_special_chars': has_special,
            },
            'recommendations': self._get_password_recommendations(pwd)
        }
    
    def _get_password_recommendations(self, password: str) -> list:
        """Get password improvement recommendations."""
        recommendations = []
        
        if len(password) < 8:
            recommendations.append("Use at least 8 characters")
        elif len(password) < 12:
            recommendations.append("Consider using 12+ characters for better security")
        
        if not any(c.isupper() for c in password):
            recommendations.append("Add uppercase letters")
        
        if not any(c.islower() for c in password):
            recommendations.append("Add lowercase letters")
        
        if not any(c.isdigit() for c in password):
            recommendations.append("Add numbers")
        
        if not any(not c.isalnum() for c in password):
            recommendations.append("Add special characters (!@#$%^&*)")
        
        if not recommendations:
            recommendations.append("Password strength is good!")
        
        return recommendations
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the SecureCompressor configuration.
        
        Returns:
            Dict[str, Any]: Configuration and status information.
        """
        info = {
            'version': '1.0.0',
            'configuration': self.config,
            'compressor_info': self.compressor.get_info(),
            'encryptor_info': self.encryptor.get_info(),
            'key_manager_info': self.key_manager.get_info(),
            'password_strength': self.validate_password_strength(),
            'fast_extensions': {
                'crypto_available': FAST_CRYPTO_AVAILABLE,
                'compression_available': FAST_COMPRESSION_AVAILABLE,
                'enabled': self.use_fast_extensions,
            }
        }
        
        if self.custom_encoder:
            info['custom_encoder_info'] = self.custom_encoder.get_charset_info()
        
        return info
    
    def benchmark_performance(self, data_size: int = 1024) -> Dict[str, Any]:
        """
        Benchmark the performance of different operations.
        
        Args:
            data_size: Size of test data in bytes.
            
        Returns:
            Dict[str, Any]: Benchmark results.
        """
        import time
        import secrets
        
        # Generate test data
        test_data = secrets.token_bytes(data_size)
        
        results = {}
        
        # Benchmark binary format
        start_time = time.time()
        encrypted = self.compress_and_encrypt(test_data, 'binary')
        encrypt_time = time.time() - start_time
        
        start_time = time.time()
        decrypted = self.decrypt_and_decompress(encrypted, 'binary')
        decrypt_time = time.time() - start_time
        
        results['binary'] = {
            'encrypt_time': encrypt_time,
            'decrypt_time': decrypt_time,
            'total_time': encrypt_time + decrypt_time,
            'throughput_mbps': (data_size / (1024 * 1024)) / (encrypt_time + decrypt_time),
            'compression_ratio': len(encrypted) / data_size,
            'correctness': test_data == decrypted
        }
        
        # Benchmark custom encoding if available
        if self.custom_encoder:
            start_time = time.time()
            custom_encrypted = self.compress_and_encrypt(test_data, 'custom')
            custom_encrypt_time = time.time() - start_time
            
            start_time = time.time()
            custom_decrypted = self.decrypt_and_decompress(custom_encrypted, 'custom')
            custom_decrypt_time = time.time() - start_time
            
            results['custom'] = {
                'encrypt_time': custom_encrypt_time,
                'decrypt_time': custom_decrypt_time,
                'total_time': custom_encrypt_time + custom_decrypt_time,
                'throughput_mbps': (data_size / (1024 * 1024)) / (custom_encrypt_time + custom_decrypt_time),
                'expansion_ratio': len(custom_encrypted.encode('utf-8')) / data_size,
                'correctness': test_data == custom_decrypted
            }
        
        return results
    
    def __repr__(self) -> str:
        """String representation of the SecureCompressor."""
        charset_info = f", charset={self.custom_encoder.charset}" if self.custom_encoder else ""
        return (f"SecureCompressor("
                f"compression={self.compressor.algorithm.value}, "
                f"encryption={self.encryptor.algorithm.value}, "
                f"kdf={self.key_manager.kdf_algorithm}"
                f"{charset_info})")
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        base_str = (f"Secure Compressor with {self.compressor.algorithm.value.upper()} compression "
                   f"and {self.encryptor.algorithm.value.upper()} encryption")
        
        if self.custom_encoder:
            base_str += f" using custom charset '{self.custom_encoder.charset}'"
        
        if self.use_fast_extensions:
            base_str += " (fast extensions enabled)"
        
        return base_str 