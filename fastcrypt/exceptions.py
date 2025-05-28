"""
Custom exceptions for the Encrypter package.

This module defines all custom exceptions used throughout the package
to provide clear error handling and debugging information.
"""

from typing import Optional, Any


class EncrypterError(Exception):
    """
    Base exception class for all Encrypter-related errors.
    
    This is the parent class for all custom exceptions in the package.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Any] = None):
        """
        Initialize the base exception.
        
        Args:
            message (str): Human-readable error message.
            error_code (str, optional): Machine-readable error code.
            details (Any, optional): Additional error details.
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class CompressionError(EncrypterError):
    """
    Exception raised for compression-related errors.
    
    This includes errors during compression, decompression,
    or algorithm selection.
    """
    pass


class EncryptionError(EncrypterError):
    """
    Exception raised for encryption-related errors.
    
    This includes errors during encryption, decryption,
    key generation, or algorithm operations.
    """
    pass


class KeyError(EncrypterError):
    """
    Exception raised for key management errors.
    
    This includes errors in key generation, derivation,
    storage, or validation.
    """
    pass


class ValidationError(EncrypterError):
    """
    Exception raised for data validation errors.
    
    This includes errors in input validation, format checking,
    or integrity verification.
    """
    pass


class AlgorithmError(EncrypterError):
    """
    Exception raised for algorithm-specific errors.
    
    This includes unsupported algorithms, configuration errors,
    or algorithm initialization failures.
    """
    pass


class SecurityError(EncrypterError):
    """
    Exception raised for security-related errors.
    
    This includes authentication failures, integrity check failures,
    or security policy violations.
    """
    pass


class ConfigurationError(EncrypterError):
    """
    Exception raised for configuration-related errors.
    
    This includes invalid settings, missing configuration,
    or incompatible options.
    """
    pass


class MemoryError(EncrypterError):
    """
    Exception raised for memory-related errors.
    
    This includes insufficient memory, memory allocation failures,
    or memory security issues.
    """
    pass


class FileError(EncrypterError):
    """
    Exception raised for file operation errors.
    
    This includes file not found, permission errors,
    or file format issues.
    """
    pass


class NetworkError(EncrypterError):
    """
    Exception raised for network-related errors.
    
    This includes connection failures, timeout errors,
    or protocol issues.
    """
    pass


# Error code constants
class ErrorCodes:
    """Constants for error codes used throughout the package."""
    
    # Compression errors
    COMPRESSION_FAILED = "COMP_001"
    DECOMPRESSION_FAILED = "COMP_002"
    UNSUPPORTED_COMPRESSION = "COMP_003"
    COMPRESSION_RATIO_LOW = "COMP_004"
    
    # Encryption errors
    ENCRYPTION_FAILED = "ENC_001"
    DECRYPTION_FAILED = "ENC_002"
    UNSUPPORTED_ENCRYPTION = "ENC_003"
    INVALID_CIPHERTEXT = "ENC_004"
    
    # Key errors
    KEY_GENERATION_FAILED = "KEY_001"
    KEY_DERIVATION_FAILED = "KEY_002"
    INVALID_KEY_FORMAT = "KEY_003"
    KEY_TOO_WEAK = "KEY_004"
    
    # Validation errors
    INVALID_INPUT_FORMAT = "VAL_001"
    INVALID_INPUT_SIZE = "VAL_002"
    CHECKSUM_MISMATCH = "VAL_003"
    INTEGRITY_CHECK_FAILED = "VAL_004"
    
    # Security errors
    AUTHENTICATION_FAILED = "SEC_001"
    AUTHORIZATION_FAILED = "SEC_002"
    TAMPERING_DETECTED = "SEC_003"
    WEAK_SECURITY_SETTINGS = "SEC_004"
    
    # Configuration errors
    INVALID_CONFIGURATION = "CFG_001"
    MISSING_CONFIGURATION = "CFG_002"
    INCOMPATIBLE_OPTIONS = "CFG_003"
    
    # File errors
    FILE_NOT_FOUND = "FILE_001"
    FILE_PERMISSION_DENIED = "FILE_002"
    FILE_CORRUPTED = "FILE_003"
    INVALID_FILE_FORMAT = "FILE_004"


def create_error(error_type: str, message: str, error_code: Optional[str] = None, 
                details: Optional[Any] = None) -> EncrypterError:
    """
    Factory function to create appropriate error instances.
    
    Args:
        error_type (str): Type of error to create.
        message (str): Error message.
        error_code (str, optional): Error code.
        details (Any, optional): Additional details.
        
    Returns:
        EncrypterError: Appropriate error instance.
        
    Raises:
        ValueError: If error_type is not recognized.
    """
    error_classes = {
        "compression": CompressionError,
        "encryption": EncryptionError,
        "key": KeyError,
        "validation": ValidationError,
        "algorithm": AlgorithmError,
        "security": SecurityError,
        "configuration": ConfigurationError,
        "memory": MemoryError,
        "file": FileError,
        "network": NetworkError,
    }
    
    error_class = error_classes.get(error_type.lower())
    if not error_class:
        raise ValueError(f"Unknown error type: {error_type}")
    
    return error_class(message, error_code, details) 