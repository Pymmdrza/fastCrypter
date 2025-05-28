"""
Native Library Loader for Encrypter Package

This module loads and provides Python interfaces to native C/C++ libraries
for high-performance cryptographic operations.
"""

import os
import sys
import ctypes
import platform
from typing import Optional, Tuple, Union
from pathlib import Path

# Platform detection
PLATFORM_MAP = {
    'Windows': 'windows',
    'Linux': 'linux', 
    'Darwin': 'macos'
}

LIBRARY_EXTENSIONS = {
    'windows': '.dll',
    'linux': '.so',
    'macos': '.dylib'
}

class NativeLibraryError(Exception):
    """Exception raised when native library operations fail."""
    pass

class CryptoCoreLib:
    """Wrapper for crypto_core native library."""
    
    def __init__(self, lib_path: str):
        """Initialize the crypto core library."""
        try:
            self.lib = ctypes.CDLL(lib_path)
            self._setup_function_signatures()
            
            # Initialize library
            init_result = self.lib.crypto_core_init()
            if init_result != 0:
                raise NativeLibraryError(f"Failed to initialize crypto_core library: {init_result}")
                
        except OSError as e:
            raise NativeLibraryError(f"Failed to load crypto_core library: {e}")
    
    def _setup_function_signatures(self):
        """Setup function signatures for type safety."""
        
        # fast_xor_inplace(data, data_len, key, key_len)
        self.lib.fast_xor_inplace.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t
        ]
        self.lib.fast_xor_inplace.restype = None
        
        # secure_memclear(ptr, len)
        self.lib.secure_memclear.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        self.lib.secure_memclear.restype = None
        
        # calculate_entropy(data, len) -> double
        self.lib.calculate_entropy.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.lib.calculate_entropy.restype = ctypes.c_double
        
        # secure_random_bytes(buffer, len) -> int
        self.lib.secure_random_bytes.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t]
        self.lib.secure_random_bytes.restype = ctypes.c_int
        
        # fast_key_derive(password, pwd_len, salt, salt_len, iterations, output, out_len)
        self.lib.fast_key_derive.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t
        ]
        self.lib.fast_key_derive.restype = None
        
        # base_convert_encode(input, input_len, output, output_max, charset, base) -> size_t
        self.lib.base_convert_encode.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.c_char_p, ctypes.c_size_t
        ]
        self.lib.base_convert_encode.restype = ctypes.c_size_t
        
        # fast_compress_rle(input, input_len, output, output_max) -> size_t
        self.lib.fast_compress_rle.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t
        ]
        self.lib.fast_compress_rle.restype = ctypes.c_size_t
        
        # fast_decompress_rle(input, input_len, output, output_max) -> size_t
        self.lib.fast_decompress_rle.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t
        ]
        self.lib.fast_decompress_rle.restype = ctypes.c_size_t
    
    def fast_xor(self, data: bytes, key: bytes) -> bytes:
        """Perform fast XOR operation."""
        if not data or not key:
            return data
        
        # Create mutable copy
        result = bytearray(data)
        data_ptr = (ctypes.c_uint8 * len(result)).from_buffer(result)
        key_ptr = (ctypes.c_uint8 * len(key)).from_buffer_copy(key)
        
        self.lib.fast_xor_inplace(data_ptr, len(result), key_ptr, len(key))
        return bytes(result)
    
    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if not data:
            return 0.0
        
        data_ptr = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        return self.lib.calculate_entropy(data_ptr, len(data))
    
    def secure_random_bytes(self, length: int) -> bytes:
        """Generate cryptographically secure random bytes."""
        if length <= 0:
            return b''
        
        buffer = (ctypes.c_uint8 * length)()
        result = self.lib.secure_random_bytes(buffer, length)
        
        if result != 0:
            raise NativeLibraryError("Failed to generate secure random bytes")
        
        return bytes(buffer)
    
    def fast_key_derive(self, password: bytes, salt: bytes, iterations: int, output_length: int) -> bytes:
        """Fast key derivation function."""
        if not password or not salt or iterations <= 0 or output_length <= 0:
            raise ValueError("Invalid parameters for key derivation")
        
        password_ptr = (ctypes.c_uint8 * len(password)).from_buffer_copy(password)
        salt_ptr = (ctypes.c_uint8 * len(salt)).from_buffer_copy(salt)
        output = (ctypes.c_uint8 * output_length)()
        
        self.lib.fast_key_derive(
            password_ptr, len(password),
            salt_ptr, len(salt),
            iterations,
            output, output_length
        )
        
        return bytes(output)
    
    def base_convert_encode(self, data: bytes, charset: str) -> str:
        """Convert binary data to custom character set."""
        if not data or not charset:
            return ""
        
        data_ptr = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        output_max = len(data) * 2 + 10  # Conservative estimate
        output = (ctypes.c_uint8 * output_max)()
        charset_bytes = charset.encode('utf-8')
        
        result_len = self.lib.base_convert_encode(
            data_ptr, len(data),
            output, output_max,
            charset_bytes, len(charset)
        )
        
        if result_len == 0:
            return ""
        
        return bytes(output[:result_len]).decode('utf-8', errors='ignore')
    
    def fast_compress_rle(self, data: bytes) -> bytes:
        """Fast RLE compression."""
        if not data:
            return b''
        
        data_ptr = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        output_max = len(data) + len(data) // 2  # Conservative estimate
        output = (ctypes.c_uint8 * output_max)()
        
        result_len = self.lib.fast_compress_rle(data_ptr, len(data), output, output_max)
        
        if result_len == 0:
            return data  # Return original if compression failed
        
        return bytes(output[:result_len])
    
    def fast_decompress_rle(self, data: bytes) -> bytes:
        """Fast RLE decompression."""
        if not data:
            return b''
        
        data_ptr = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        output_max = len(data) * 4  # Conservative estimate
        output = (ctypes.c_uint8 * output_max)()
        
        result_len = self.lib.fast_decompress_rle(data_ptr, len(data), output, output_max)
        
        if result_len == 0:
            raise NativeLibraryError("RLE decompression failed")
        
        return bytes(output[:result_len])
    
    def __del__(self):
        """Cleanup library resources."""
        if hasattr(self, 'lib'):
            try:
                self.lib.crypto_core_cleanup()
            except:
                pass

class HashAlgorithmsLib:
    """Wrapper for hash_algorithms native library."""
    
    def __init__(self, lib_path: str):
        """Initialize the hash algorithms library."""
        try:
            self.lib = ctypes.CDLL(lib_path)
            self._setup_function_signatures()
            
            # Initialize library
            init_result = self.lib.hash_algorithms_init()
            if init_result != 0:
                raise NativeLibraryError(f"Failed to initialize hash_algorithms library: {init_result}")
                
        except OSError as e:
            raise NativeLibraryError(f"Failed to load hash_algorithms library: {e}")
    
    def _setup_function_signatures(self):
        """Setup function signatures for type safety."""
        
        # fast_sha256(data, len, hash)
        self.lib.fast_sha256.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.fast_sha256.restype = None
        
        # fast_hmac_sha256(key, key_len, data, data_len, hmac)
        self.lib.fast_hmac_sha256.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.fast_hmac_sha256.restype = None
        
        # generate_keypair(private_key, public_key)
        self.lib.generate_keypair.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.generate_keypair.restype = None
        
        # fast_sign(private_key, message, msg_len, signature)
        self.lib.fast_sign.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.fast_sign.restype = None
        
        # fast_verify(public_key, message, msg_len, signature) -> int
        self.lib.fast_verify.argtypes = [
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8)
        ]
        self.lib.fast_verify.restype = ctypes.c_int
        
        # fast_pbkdf2(password, pwd_len, salt, salt_len, iterations, output, out_len)
        self.lib.fast_pbkdf2.argtypes = [
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t
        ]
        self.lib.fast_pbkdf2.restype = None
        
        # benchmark_hash_performance(data_size, iterations) -> double
        self.lib.benchmark_hash_performance.argtypes = [ctypes.c_size_t, ctypes.c_uint32]
        self.lib.benchmark_hash_performance.restype = ctypes.c_double
    
    def fast_sha256(self, data: bytes) -> bytes:
        """Fast SHA-256 hash."""
        if not data:
            return b'\x00' * 32
        
        data_ptr = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        hash_output = (ctypes.c_uint8 * 32)()
        
        self.lib.fast_sha256(data_ptr, len(data), hash_output)
        return bytes(hash_output)
    
    def fast_hmac_sha256(self, key: bytes, data: bytes) -> bytes:
        """Fast HMAC-SHA256."""
        if not key or not data:
            return b'\x00' * 32
        
        key_ptr = (ctypes.c_uint8 * len(key)).from_buffer_copy(key)
        data_ptr = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        hmac_output = (ctypes.c_uint8 * 32)()
        
        self.lib.fast_hmac_sha256(key_ptr, len(key), data_ptr, len(data), hmac_output)
        return bytes(hmac_output)
    
    def generate_keypair(self) -> Tuple[bytes, bytes]:
        """Generate ECC keypair."""
        private_key = (ctypes.c_uint8 * 32)()
        public_key = (ctypes.c_uint8 * 64)()
        
        self.lib.generate_keypair(private_key, public_key)
        return bytes(private_key), bytes(public_key)
    
    def fast_sign(self, private_key: bytes, message: bytes) -> bytes:
        """Fast digital signature."""
        if len(private_key) != 32:
            raise ValueError("Private key must be 32 bytes")
        
        private_key_ptr = (ctypes.c_uint8 * 32).from_buffer_copy(private_key)
        message_ptr = (ctypes.c_uint8 * len(message)).from_buffer_copy(message)
        signature = (ctypes.c_uint8 * 64)()
        
        self.lib.fast_sign(private_key_ptr, message_ptr, len(message), signature)
        return bytes(signature)
    
    def fast_verify(self, public_key: bytes, message: bytes, signature: bytes) -> bool:
        """Fast signature verification."""
        if len(public_key) != 64 or len(signature) != 64:
            return False
        
        public_key_ptr = (ctypes.c_uint8 * 64).from_buffer_copy(public_key)
        message_ptr = (ctypes.c_uint8 * len(message)).from_buffer_copy(message)
        signature_ptr = (ctypes.c_uint8 * 64).from_buffer_copy(signature)
        
        result = self.lib.fast_verify(public_key_ptr, message_ptr, len(message), signature_ptr)
        return result == 1
    
    def fast_pbkdf2(self, password: bytes, salt: bytes, iterations: int, output_length: int) -> bytes:
        """Fast PBKDF2 key derivation."""
        if not password or not salt or iterations <= 0 or output_length <= 0:
            raise ValueError("Invalid parameters for PBKDF2")
        
        password_ptr = (ctypes.c_uint8 * len(password)).from_buffer_copy(password)
        salt_ptr = (ctypes.c_uint8 * len(salt)).from_buffer_copy(salt)
        output = (ctypes.c_uint8 * output_length)()
        
        self.lib.fast_pbkdf2(
            password_ptr, len(password),
            salt_ptr, len(salt),
            iterations,
            output, output_length
        )
        
        return bytes(output)
    
    def benchmark_hash_performance(self, data_size: int = 1024, iterations: int = 1000) -> float:
        """Benchmark hash performance."""
        return self.lib.benchmark_hash_performance(data_size, iterations)
    
    def __del__(self):
        """Cleanup library resources."""
        if hasattr(self, 'lib'):
            try:
                self.lib.hash_algorithms_cleanup()
            except:
                pass

class NativeLibraryManager:
    """Manager for loading and using native libraries."""
    
    def __init__(self):
        """Initialize the native library manager."""
        self.crypto_core: Optional[CryptoCoreLib] = None
        self.hash_algorithms: Optional[HashAlgorithmsLib] = None
        self._libs_path = self._find_libs_path()
        self._platform = self._detect_platform()
        
    def _detect_platform(self) -> str:
        """Detect current platform."""
        system = platform.system()
        return PLATFORM_MAP.get(system, 'linux')
    
    def _find_libs_path(self) -> Path:
        """Find the native libraries directory."""
        # Try different possible locations
        current_dir = Path(__file__).parent
        possible_paths = [
            current_dir / 'libs',
            current_dir.parent / 'libs',
            current_dir.parent.parent / 'libs',
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        # Create default path
        default_path = current_dir / 'libs'
        default_path.mkdir(exist_ok=True)
        return default_path
    
    def _get_library_path(self, lib_name: str) -> str:
        """Get full path to a native library."""
        platform_dir = self._libs_path / self._platform
        extension = LIBRARY_EXTENSIONS[self._platform]
        lib_filename = f"lib{lib_name}{extension}"
        return str(platform_dir / lib_filename)
    
    def load_crypto_core(self) -> bool:
        """Load crypto_core library."""
        try:
            lib_path = self._get_library_path('crypto_core')
            self.crypto_core = CryptoCoreLib(lib_path)
            return True
        except Exception as e:
            print(f"Warning: Could not load crypto_core library: {e}")
            return False
    
    def load_hash_algorithms(self) -> bool:
        """Load hash_algorithms library."""
        try:
            lib_path = self._get_library_path('hash_algorithms')
            self.hash_algorithms = HashAlgorithmsLib(lib_path)
            return True
        except Exception as e:
            print(f"Warning: Could not load hash_algorithms library: {e}")
            return False
    
    def load_all(self) -> dict:
        """Load all available libraries."""
        results = {
            'crypto_core': self.load_crypto_core(),
            'hash_algorithms': self.load_hash_algorithms()
        }
        return results
    
    def is_available(self, lib_name: str) -> bool:
        """Check if a library is available."""
        if lib_name == 'crypto_core':
            return self.crypto_core is not None
        elif lib_name == 'hash_algorithms':
            return self.hash_algorithms is not None
        return False
    
    def get_info(self) -> dict:
        """Get information about loaded libraries."""
        return {
            'platform': self._platform,
            'libs_path': str(self._libs_path),
            'crypto_core_loaded': self.crypto_core is not None,
            'hash_algorithms_loaded': self.hash_algorithms is not None,
            'available_libraries': [
                name for name in ['crypto_core', 'hash_algorithms']
                if self.is_available(name)
            ]
        }

# Global instance
_native_manager = None

def get_native_manager() -> NativeLibraryManager:
    """Get the global native library manager."""
    global _native_manager
    if _native_manager is None:
        _native_manager = NativeLibraryManager()
        _native_manager.load_all()
    return _native_manager

# Convenience functions
def get_crypto_core() -> Optional[CryptoCoreLib]:
    """Get crypto_core library if available."""
    manager = get_native_manager()
    return manager.crypto_core

def get_hash_algorithms() -> Optional[HashAlgorithmsLib]:
    """Get hash_algorithms library if available."""
    manager = get_native_manager()
    return manager.hash_algorithms

def is_native_available() -> bool:
    """Check if any native libraries are available."""
    manager = get_native_manager()
    return manager.crypto_core is not None or manager.hash_algorithms is not None 