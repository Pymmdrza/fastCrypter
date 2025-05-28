"""
🔐 Encrypter - Professional Compression and Encryption Library

A powerful Python package for secure data compression and encryption
using modern cryptographic algorithms and compression techniques.

Author: Encrypter Team
Version: 1.0.0
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Encrypter Team"
__email__ = "team@encrypter.dev"
__license__ = "MIT"

# Core imports
from .core.compressor import Compressor
from .core.encryptor import Encryptor
from .core.key_manager import KeyManager

# High-level interfaces
from .secure_compressor import SecureCompressor
from .file_encryptor import FileEncryptor
from .advanced_encryptor import AdvancedEncryptor

# Exceptions
from .exceptions import (
    EncrypterError,
    CompressionError,
    EncryptionError,
    KeyError,
    ValidationError,
)

# Algorithm imports
from .algorithms import (
    CompressionAlgorithm,
    EncryptionAlgorithm,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # Core classes
    "Compressor",
    "Encryptor", 
    "KeyManager",
    
    # High-level interfaces
    "SecureCompressor",
    "FileEncryptor",
    "AdvancedEncryptor",
    
    # Exceptions
    "EncrypterError",
    "CompressionError",
    "EncryptionError",
    "KeyError",
    "ValidationError",
    
    # Algorithm base classes
    "CompressionAlgorithm",
    "EncryptionAlgorithm",
]

# Package metadata
PACKAGE_INFO = {
    "name": "encrypter",
    "version": __version__,
    "description": "Professional compression and encryption library",
    "author": __author__,
    "email": __email__,
    "license": __license__,
    "url": "https://github.com/yourusername/encrypter",
    "keywords": [
        "encryption", "compression", "security", "cryptography",
        "aes", "chacha20", "rsa", "zlib", "lzma", "brotli"
    ],
} 