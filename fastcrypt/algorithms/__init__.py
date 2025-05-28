"""
Algorithm implementations for the Encrypter package.

This package contains various compression and encryption algorithms
that can be used with the core components.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class CompressionAlgorithm(ABC):
    """
    Abstract base class for compression algorithms.
    
    All compression algorithms must inherit from this class
    and implement the required methods.
    """
    
    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        """
        Compress the given data.
        
        Args:
            data (bytes): Data to compress.
            
        Returns:
            bytes: Compressed data.
        """
        pass
    
    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        """
        Decompress the given data.
        
        Args:
            data (bytes): Compressed data to decompress.
            
        Returns:
            bytes: Decompressed data.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the algorithm name."""
        pass
    
    @property
    @abstractmethod
    def settings(self) -> Dict[str, Any]:
        """Get the algorithm settings."""
        pass


class EncryptionAlgorithm(ABC):
    """
    Abstract base class for encryption algorithms.
    
    All encryption algorithms must inherit from this class
    and implement the required methods.
    """
    
    @abstractmethod
    def encrypt(self, data: bytes, key: bytes, **kwargs) -> bytes:
        """
        Encrypt the given data.
        
        Args:
            data (bytes): Data to encrypt.
            key (bytes): Encryption key.
            **kwargs: Additional algorithm-specific parameters.
            
        Returns:
            bytes: Encrypted data.
        """
        pass
    
    @abstractmethod
    def decrypt(self, data: bytes, key: bytes, **kwargs) -> bytes:
        """
        Decrypt the given data.
        
        Args:
            data (bytes): Encrypted data to decrypt.
            key (bytes): Decryption key.
            **kwargs: Additional algorithm-specific parameters.
            
        Returns:
            bytes: Decrypted data.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the algorithm name."""
        pass
    
    @property
    @abstractmethod
    def key_size(self) -> int:
        """Get the required key size in bytes."""
        pass
    
    @property
    @abstractmethod
    def settings(self) -> Dict[str, Any]:
        """Get the algorithm settings."""
        pass


__all__ = [
    "CompressionAlgorithm",
    "EncryptionAlgorithm",
] 