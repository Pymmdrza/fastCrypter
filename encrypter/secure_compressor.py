"""
Secure Compressor - High-level interface for compression and encryption.

This module provides a simple, secure interface that combines compression
and encryption in a single operation for maximum security and efficiency.
"""

from typing import Union, Optional, Dict, Any
from .core.compressor import Compressor, CompressionAlgorithmType, CompressionLevel
from .core.encryptor import Encryptor, EncryptionAlgorithmType
from .core.key_manager import KeyManager
from .exceptions import EncrypterError, ValidationError, ErrorCodes


class SecureCompressor:
    """
    High-level secure compressor that combines compression and encryption.
    
    This class provides a simple interface for securely compressing and
    encrypting data in a single operation, with automatic algorithm selection
    and key management.
    """
    
    def __init__(self,
                 password: str,
                 compression_algorithm: Union[CompressionAlgorithmType, str] = CompressionAlgorithmType.ZLIB,
                 compression_level: Union[CompressionLevel, int] = CompressionLevel.BALANCED,
                 encryption_algorithm: Union[EncryptionAlgorithmType, str] = EncryptionAlgorithmType.AES_256_GCM,
                 auto_select_compression: bool = True,
                 kdf_algorithm: str = 'pbkdf2',
                 kdf_iterations: int = 100000):
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
        
        # Store configuration
        self.config = {
            'compression_algorithm': compression_algorithm,
            'compression_level': compression_level,
            'encryption_algorithm': encryption_algorithm,
            'auto_select_compression': auto_select_compression,
            'kdf_algorithm': kdf_algorithm,
            'kdf_iterations': kdf_iterations,
        }
    
    def compress_and_encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Compress and encrypt data in a single operation.
        
        The process follows these steps:
        1. Compress the data using the configured compression algorithm
        2. Encrypt the compressed data using the configured encryption algorithm
        3. Return the encrypted compressed data with metadata
        
        Args:
            data: Data to compress and encrypt (string or bytes).
            
        Returns:
            bytes: Encrypted compressed data with metadata headers.
            
        Raises:
            EncrypterError: If compression or encryption fails.
            ValidationError: If input data is invalid.
        """
        try:
            # Step 1: Compress data
            compressed_data = self.compressor.compress(data)
            
            # Step 2: Encrypt compressed data
            encrypted_data = self.encryptor.encrypt(compressed_data, self.password)
            
            return encrypted_data
            
        except Exception as e:
            raise EncrypterError(
                f"Secure compression failed: {str(e)}",
                details={"operation": "compress_and_encrypt", "error": str(e)}
            )
    
    def decrypt_and_decompress(self, data: bytes) -> bytes:
        """
        Decrypt and decompress data in a single operation.
        
        The process follows these steps:
        1. Decrypt the data using the configured encryption algorithm
        2. Decompress the decrypted data using the appropriate compression algorithm
        3. Return the original data
        
        Args:
            data: Encrypted compressed data to decrypt and decompress.
            
        Returns:
            bytes: Original decompressed data.
            
        Raises:
            EncrypterError: If decryption or decompression fails.
            ValidationError: If input data is invalid.
        """
        try:
            # Step 1: Decrypt data
            decrypted_data = self.encryptor.decrypt(data, self.password)
            
            # Step 2: Decompress decrypted data
            decompressed_data = self.compressor.decompress(decrypted_data)
            
            return decompressed_data
            
        except Exception as e:
            raise EncrypterError(
                f"Secure decompression failed: {str(e)}",
                details={"operation": "decrypt_and_decompress", "error": str(e)}
            )
    
    def compress_and_encrypt_string(self, text: str) -> bytes:
        """
        Compress and encrypt a string, returning encrypted bytes.
        
        Args:
            text (str): Text to compress and encrypt.
            
        Returns:
            bytes: Encrypted compressed data.
        """
        return self.compress_and_encrypt(text)
    
    def decrypt_and_decompress_to_string(self, data: bytes, encoding: str = 'utf-8') -> str:
        """
        Decrypt and decompress data, returning a string.
        
        Args:
            data (bytes): Encrypted compressed data.
            encoding (str): Text encoding to use for decoding.
            
        Returns:
            str: Original text.
            
        Raises:
            UnicodeDecodeError: If data cannot be decoded as text.
        """
        decompressed_data = self.decrypt_and_decompress(data)
        return decompressed_data.decode(encoding)
    
    def get_compression_ratio(self, original_data: Union[str, bytes], 
                            compressed_encrypted_data: bytes) -> float:
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
        
        return len(compressed_encrypted_data) / len(original_data)
    
    def estimate_output_size(self, input_size: int) -> Dict[str, int]:
        """
        Estimate the output size for given input size.
        
        Args:
            input_size (int): Size of input data in bytes.
            
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
        
        return {
            'original_size': input_size,
            'estimated_compressed_size': compressed_size,
            'estimated_final_size': encrypted_size,
            'estimated_compression_ratio': comp_ratio,
            'estimated_total_ratio': encrypted_size / input_size if input_size > 0 else 0,
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
        return {
            'version': '1.0.0',
            'configuration': self.config,
            'compressor_info': self.compressor.get_info(),
            'encryptor_info': self.encryptor.get_info(),
            'key_manager_info': self.key_manager.get_info(),
            'password_strength': self.validate_password_strength(),
        }
    
    def __repr__(self) -> str:
        """String representation of the SecureCompressor."""
        return (f"SecureCompressor("
                f"compression={self.compressor.algorithm.value}, "
                f"encryption={self.encryptor.algorithm.value}, "
                f"kdf={self.key_manager.kdf_algorithm})")
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (f"Secure Compressor with {self.compressor.algorithm.value.upper()} compression "
                f"and {self.encryptor.algorithm.value.upper()} encryption") 