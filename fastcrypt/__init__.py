"""
🚀 fastCrypter - Professional Compression and Encryption Library

A powerful Python package for secure data compression and encryption
using modern cryptographic algorithms and compression techniques with
native C/C++ acceleration for maximum performance.

Author: Mmdrza
Version: 2.0.0
License: MIT
"""

__version__ = "2.0.6"
__author__ = "Mmdrza"
__email__ = "pymmdrza@gmail.com"
__license__ = "MIT"

# Core imports
from .core.compressor import Compressor, CompressionAlgorithmType, CompressionLevel
from .core.encryptor import Encryptor, EncryptionAlgorithmType
from .core.key_manager import KeyManager
from .core.custom_encoder import CustomEncoder

# High-level interfaces
from .secure_compressor import SecureCompressor
from .file_encryptor import FileEncryptor
from .advanced_encryptor import AdvancedEncryptor

# Enhanced components with native acceleration
try:
    from .core.enhanced_compressor import EnhancedCompressor
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

# Native library support
try:
    from .native.native_loader import (
        get_native_manager, get_crypto_core, get_hash_algorithms, 
        is_native_available, NativeLibraryManager
    )
    NATIVE_SUPPORT = True
except ImportError:
    NATIVE_SUPPORT = False

# Exceptions
from .exceptions import (
    EncrypterError,
    CompressionError,
    EncryptionError,
    ValidationError,
    KeyError,
    ErrorCodes,
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
    "CustomEncoder",
    
    # High-level interfaces
    "SecureCompressor",
    "FileEncryptor",
    "AdvancedEncryptor",
    
    # Algorithm types
    "CompressionAlgorithmType",
    "CompressionLevel",
    "EncryptionAlgorithmType",
    
    # Exceptions
    "EncrypterError",
    "CompressionError",
    "EncryptionError",
    "ValidationError",
    "KeyError",
    "ErrorCodes",
    
    # Feature flags
    "ENHANCED_AVAILABLE",
    "NATIVE_SUPPORT",
]

# Add enhanced components if available
if ENHANCED_AVAILABLE:
    __all__.append('EnhancedCompressor')

# Add native library components if available
if NATIVE_SUPPORT:
    __all__.extend([
        'get_native_manager',
        'get_crypto_core', 
        'get_hash_algorithms',
        'is_native_available',
        'NativeLibraryManager'
    ])

# Package metadata
PACKAGE_INFO = {
    "name": "fastCrypter",
    "version": __version__,
    "description": "Professional compression and encryption library with native C/C++ acceleration",
    "author": __author__,
    "email": __email__,
    "license": __license__,
    "url": "https://github.com/Pymmdrza/fastCrypter",
    "keywords": [
        "encryption", "compression", "security", "cryptography",
        "aes", "chacha20", "rsa", "zlib", "lzma", "brotli",
        "native", "performance", "c++", "custom-encoding", "fast"
    ],
    "features": {
        "enhanced_compressor": ENHANCED_AVAILABLE,
        "native_acceleration": NATIVE_SUPPORT,
        "custom_encoding": True,
        "multiple_algorithms": True,
        "file_encryption": True,
    }
}


def get_version_info():
    """Get comprehensive version and feature information."""
    info = PACKAGE_INFO.copy()
    
    if NATIVE_SUPPORT:
        try:
            manager = get_native_manager()
            native_info = manager.get_info()
            info['native_libraries'] = native_info
        except:
            info['native_libraries'] = {'error': 'Failed to load native library info'}
    
    return info


def get_recommended_compressor(password: str, **kwargs):
    """
    Get the recommended compressor based on available features.
    
    This function automatically selects the best available compressor:
    - EnhancedCompressor if native libraries are available
    - SecureCompressor as fallback
    
    Args:
        password (str): Password for encryption.
        **kwargs: Additional arguments passed to the compressor.
        
    Returns:
        Compressor instance (EnhancedCompressor or SecureCompressor).
    """
    if ENHANCED_AVAILABLE and NATIVE_SUPPORT:
        try:
            if is_native_available():
                return EnhancedCompressor(password=password, **kwargs)
        except:
            pass
    
    # Fallback to standard compressor
    return SecureCompressor(password=password, **kwargs)


def benchmark_available_features(data_size: int = 1024) -> dict:
    """
    Benchmark all available features and return performance information.
    
    Args:
        data_size (int): Size of test data in bytes.
        
    Returns:
        dict: Benchmark results for all available features.
    """
    import time
    import secrets
    
    results = {
        'data_size': data_size,
        'features_tested': [],
        'performance': {}
    }
    
    test_data = secrets.token_bytes(data_size)
    password = "BenchmarkPassword123!"
    
    # Test standard compressor
    try:
        compressor = SecureCompressor(password=password)
        
        start_time = time.time()
        encrypted = compressor.compress_and_encrypt(test_data)
        decrypted = compressor.decrypt_and_decompress(encrypted)
        end_time = time.time()
        
        results['features_tested'].append('SecureCompressor')
        results['performance']['standard'] = {
            'time': end_time - start_time,
            'correctness': test_data == decrypted,
            'compression_ratio': len(encrypted) / len(test_data)
        }
    except Exception as e:
        results['performance']['standard'] = {'error': str(e)}
    
    # Test enhanced compressor if available
    if ENHANCED_AVAILABLE:
        try:
            enhanced = EnhancedCompressor(password=password)
            
            start_time = time.time()
            encrypted = enhanced.compress_and_encrypt(test_data)
            decrypted = enhanced.decrypt_and_decompress(encrypted)
            end_time = time.time()
            
            results['features_tested'].append('EnhancedCompressor')
            results['performance']['enhanced'] = {
                'time': end_time - start_time,
                'correctness': test_data == decrypted,
                'compression_ratio': len(encrypted) / len(test_data),
                'native_available': enhanced.is_native_available()
            }
            
            # Compare performance
            if 'standard' in results['performance']:
                standard_time = results['performance']['standard'].get('time', 0)
                enhanced_time = results['performance']['enhanced']['time']
                if enhanced_time > 0:
                    results['performance']['speedup'] = standard_time / enhanced_time
            
        except Exception as e:
            results['performance']['enhanced'] = {'error': str(e)}
    
    # Test native libraries if available
    if NATIVE_SUPPORT:
        try:
            manager = get_native_manager()
            native_info = manager.get_info()
            
            results['features_tested'].append('NativeLibraries')
            results['performance']['native'] = {
                'available': native_info.get('crypto_core_loaded', False) or native_info.get('hash_algorithms_loaded', False),
                'crypto_core': native_info.get('crypto_core_loaded', False),
                'hash_algorithms': native_info.get('hash_algorithms_loaded', False),
                'platform': native_info.get('platform', 'unknown')
            }
            
        except Exception as e:
            results['performance']['native'] = {'error': str(e)}
    
    return results


# Package initialization message
def _show_startup_info():
    """Show package startup information."""
    features = []
    
    if ENHANCED_AVAILABLE:
        features.append("Enhanced Compressor")
    
    if NATIVE_SUPPORT:
        try:
            if is_native_available():
                features.append("Native Acceleration")
            else:
                features.append("Native Support (libraries not loaded)")
        except:
            features.append("Native Support (error)")
    
    if not features:
        features.append("Standard Features")
    
    # Only show in debug mode or if explicitly requested
    import os
    if os.environ.get('fastCrypter_SHOW_INFO', '').lower() in ('1', 'true', 'yes'):
        print(f"🚀 fastCrypter v{__version__} loaded with: {', '.join(features)}")

# Show startup info if requested
_show_startup_info() 