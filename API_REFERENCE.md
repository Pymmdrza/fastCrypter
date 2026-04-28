# fastcrypter API Reference

Complete API reference for the fastcrypter library.

## Table of Contents

1. [Core Classes](#core-classes)
2. [High-Level Interfaces](#high-level-interfaces)
3. [Algorithms](#algorithms)
4. [Exceptions](#exceptions)
5. [Utility Functions](#utility-functions)

## Core Classes

### SecureCompressor

High-level interface combining compression and encryption.

```python
class SecureCompressor:
    def __init__(
        self,
        password: str,
        compression_algorithm: Union[CompressionAlgorithmType, str] = CompressionAlgorithmType.ZLIB,
        compression_level: Union[CompressionLevel, int] = CompressionLevel.BALANCED,
        encryption_algorithm: Union[EncryptionAlgorithmType, str] = EncryptionAlgorithmType.AES_256_GCM,
        auto_select_compression: bool = True,
        kdf_algorithm: str = 'pbkdf2',
        kdf_iterations: int = 100000,
        custom_charset: Optional[str] = None,
        use_fast_extensions: bool = True
    )
```

**Parameters:**
- `password` (str): Password for encryption (minimum 8 characters)
- `compression_algorithm`: Compression algorithm to use
- `compression_level`: Compression level (1-9 or CompressionLevel enum)
- `encryption_algorithm`: Encryption algorithm to use
- `auto_select_compression` (bool): Auto-select best compression algorithm
- `kdf_algorithm` (str): Key derivation function ('pbkdf2', 'scrypt', or 'argon2')
- `kdf_iterations` (int): Number of KDF iterations
- `custom_charset` (str, optional): Custom character set for encoding
- `use_fast_extensions` (bool): Use C/C++ extensions if available

**Methods:**

#### compress_and_encrypt
```python
def compress_and_encrypt(
    self,
    data: Union[str, bytes],
    output_format: str = 'binary'
) -> Union[bytes, str]
```
Compress and encrypt data.

**Parameters:**
- `data`: Data to process (string or bytes)
- `output_format` (str): Output format ('binary', 'custom', 'steganographic')

**Returns:**
- Union[bytes, str]: Encrypted compressed data

**Raises:**
- `ValidationError`: If input is invalid
- `EncrypterError`: If operation fails

#### decrypt_and_decompress
```python
def decrypt_and_decompress(
    self,
    data: Union[bytes, str],
    input_format: str = 'binary'
) -> bytes
```
Decrypt and decompress data.

**Parameters:**
- `data`: Encrypted data to process
- `input_format` (str): Input format ('binary', 'custom', 'steganographic')

**Returns:**
- bytes: Original decompressed data

#### compress_and_encrypt_string
```python
def compress_and_encrypt_string(
    self,
    text: str,
    output_format: str = 'binary'
) -> Union[bytes, str]
```
Convenience method for encrypting strings.

#### decrypt_and_decompress_to_string
```python
def decrypt_and_decompress_to_string(
    self,
    data: Union[bytes, str],
    input_format: str = 'binary',
    encoding: str = 'utf-8'
) -> str
```
Convenience method for decrypting to strings.

#### validate_password_strength
```python
def validate_password_strength(
    self,
    password: Optional[str] = None
) -> Dict[str, Any]
```
Validate password strength.

**Returns:**
- dict: Dictionary with 'strength', 'score', 'checks', and 'recommendations'

#### get_info
```python
def get_info(self) -> Dict[str, Any]
```
Get comprehensive configuration information.

#### benchmark_performance
```python
def benchmark_performance(
    self,
    data_size: int = 1024
) -> Dict[str, Any]
```
Benchmark performance with given data size.

### Compressor

Low-level compression interface.

```python
class Compressor:
    def __init__(
        self,
        algorithm: Union[CompressionAlgorithmType, str] = CompressionAlgorithmType.ZLIB,
        level: Union[CompressionLevel, int] = CompressionLevel.BALANCED,
        auto_select: bool = False
    )
```

**Methods:**

#### compress
```python
def compress(self, data: Union[str, bytes]) -> bytes
```
Compress data with metadata header.

#### decompress
```python
def decompress(self, data: bytes) -> bytes
```
Decompress data.

#### get_compression_ratio
```python
def get_compression_ratio(
    self,
    original_data: bytes,
    compressed_data: bytes
) -> float
```
Calculate compression ratio.

### Encryptor

Low-level encryption interface.

```python
class Encryptor:
    def __init__(
        self,
        algorithm: Union[EncryptionAlgorithmType, str] = EncryptionAlgorithmType.AES_256_GCM,
        derive_key: bool = True
    )
```

**Methods:**

#### encrypt
```python
def encrypt(
    self,
    data: Union[str, bytes],
    key: Union[str, bytes]
) -> bytes
```
Encrypt data with metadata header.

#### decrypt
```python
def decrypt(
    self,
    data: bytes,
    key: Union[str, bytes]
) -> bytes
```
Decrypt data.

#### generate_rsa_keypair
```python
def generate_rsa_keypair(self) -> Tuple[bytes, bytes]
```
Generate RSA-4096 key pair (only for RSA algorithm).

**Returns:**
- Tuple[bytes, bytes]: (private_key_pem, public_key_pem)

#### load_rsa_keys
```python
def load_rsa_keys(
    self,
    private_key_pem: Optional[bytes] = None,
    public_key_pem: Optional[bytes] = None
)
```
Load RSA keys from PEM format.

### KeyManager

Key generation and derivation.

```python
class KeyManager:
    def __init__(
        self,
        kdf_algorithm: str = 'pbkdf2',
        iterations: int = 100000,
        memory_cost: int = 65536,
        parallelism: int = 1
    )
```

**Methods:**

#### generate_salt
```python
def generate_salt(self, length: int = 16) -> bytes
```
Generate cryptographically secure random salt.

#### generate_key
```python
def generate_key(self, length: int = 32) -> bytes
```
Generate cryptographically secure random key.

#### derive_key
```python
def derive_key(
    self,
    password: str,
    salt: Optional[bytes] = None,
    key_length: int = 32
) -> Tuple[bytes, bytes]
```
Derive key from password using configured KDF.

**Returns:**
- Tuple[bytes, bytes]: (derived_key, salt_used)

#### validate_key_strength
```python
def validate_key_strength(
    self,
    key: bytes,
    min_entropy: float = 4.0
) -> bool
```
Validate key strength based on entropy.

#### secure_compare
```python
def secure_compare(self, a: bytes, b: bytes) -> bool
```
Constant-time comparison of byte strings.

#### clear_memory
```python
def clear_memory(self, data: bytearray) -> None
```
Securely clear sensitive data from memory.

### CustomEncoder

Custom character set encoding.

```python
class CustomEncoder:
    def __init__(
        self,
        charset: str = "abcdef98Xvbvii",
        padding_char: Optional[str] = None
    )
```

**Methods:**

#### encode
```python
def encode(self, data: Union[bytes, bytearray]) -> str
```
Encode binary data to custom character set.

#### decode
```python
def decode(self, encoded: str) -> bytes
```
Decode custom encoded string back to binary.

#### encode_with_noise
```python
def encode_with_noise(
    self,
    data: Union[bytes, bytearray],
    noise_ratio: float = 0.1
) -> str
```
Encode with random noise characters.

#### create_steganographic_text
```python
def create_steganographic_text(
    self,
    data: Union[bytes, bytearray],
    template: str = "The quick brown fox jumps over the lazy dog"
) -> str
```
Create text with hidden data.

#### get_charset_info
```python
def get_charset_info(self) -> dict
```
Get information about current charset.

### FileEncryptor

File encryption operations.

```python
class FileEncryptor:
    def __init__(self, password: str, **kwargs)
```

**Methods:**

#### encrypt_file
```python
def encrypt_file(
    self,
    input_path: str,
    output_path: str
) -> Dict[str, Any]
```
Encrypt a file.

**Returns:**
- dict: Statistics including sizes and compression ratio

#### decrypt_file
```python
def decrypt_file(
    self,
    input_path: str,
    output_path: str
) -> Dict[str, Any]
```
Decrypt a file.

**Returns:**
- dict: Statistics including sizes

### EnhancedCompressor

Enhanced compressor with native acceleration.

```python
class EnhancedCompressor(SecureCompressor):
    def __init__(
        self,
        password: str,
        use_native: bool = True,
        **kwargs
    )
```

**Additional Methods:**

#### is_native_available
```python
def is_native_available(self) -> bool
```
Check if native libraries are loaded and available.

## High-Level Interfaces

### get_recommended_compressor
```python
def get_recommended_compressor(password: str, **kwargs)
```
Get the best available compressor (EnhancedCompressor if available, otherwise SecureCompressor).

### get_version_info
```python
def get_version_info() -> dict
```
Get comprehensive version and feature information.

### benchmark_available_features
```python
def benchmark_available_features(data_size: int = 1024) -> dict
```
Benchmark all available features.

## Algorithms

### CompressionAlgorithmType
```python
class CompressionAlgorithmType(Enum):
    ZLIB = "zlib"           # Fast, balanced
    LZMA = "lzma"           # Best compression
    BROTLI = "brotli"       # Modern, efficient
```

### CompressionLevel
```python
class CompressionLevel(Enum):
    FASTEST = 1             # Fastest compression
    FAST = 3                # Fast compression
    BALANCED = 6            # Balanced speed/ratio
    BEST = 9                # Best compression
```

### EncryptionAlgorithmType
```python
class EncryptionAlgorithmType(Enum):
    AES_256_GCM = "aes-256-gcm"                 # Recommended
    AES_256_CBC = "aes-256-cbc"                 # With HMAC
    CHACHA20_POLY1305 = "chacha20-poly1305"     # Modern, fast
    RSA_4096 = "rsa-4096"                       # Asymmetric
```

## Exceptions

All exceptions inherit from `EncrypterError`.

### EncrypterError
Base exception class.

```python
class EncrypterError(Exception):
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Any] = None
    )
```

**Attributes:**
- `message` (str): Human-readable error message
- `error_code` (str): Machine-readable error code
- `details`: Additional error details

### Specific Exceptions

- **CompressionError**: Compression/decompression errors
- **EncryptionError**: Encryption/decryption errors
- **KeyError**: Key management errors
- **ValidationError**: Input validation errors
- **SecurityError**: Security-related errors
- **FileError**: File operation errors
- **AlgorithmError**: Algorithm-specific errors
- **ConfigurationError**: Configuration errors

### Error Codes

```python
class ErrorCodes:
    # Compression
    COMPRESSION_FAILED = "COMP_001"
    DECOMPRESSION_FAILED = "COMP_002"
    UNSUPPORTED_COMPRESSION = "COMP_003"
    
    # Encryption
    ENCRYPTION_FAILED = "ENC_001"
    DECRYPTION_FAILED = "ENC_002"
    UNSUPPORTED_ENCRYPTION = "ENC_003"
    INVALID_CIPHERTEXT = "ENC_004"
    
    # Keys
    KEY_GENERATION_FAILED = "KEY_001"
    KEY_DERIVATION_FAILED = "KEY_002"
    INVALID_KEY_FORMAT = "KEY_003"
    KEY_TOO_WEAK = "KEY_004"
    
    # Validation
    INVALID_INPUT_FORMAT = "VAL_001"
    INVALID_INPUT_SIZE = "VAL_002"
    CHECKSUM_MISMATCH = "VAL_003"
    INTEGRITY_CHECK_FAILED = "VAL_004"
    
    # Security
    AUTHENTICATION_FAILED = "SEC_001"
    TAMPERING_DETECTED = "SEC_003"
    
    # Configuration
    INVALID_CONFIGURATION = "CFG_001"
    
    # Files
    FILE_NOT_FOUND = "FILE_001"
    FILE_PERMISSION_DENIED = "FILE_002"
    FILE_CORRUPTED = "FILE_003"
```

## Utility Functions

### Package Metadata

```python
__version__: str          # Package version
__author__: str           # Author name
__email__: str            # Contact email
__license__: str          # License type

ENHANCED_AVAILABLE: bool  # Enhanced compressor available
NATIVE_SUPPORT: bool      # Native libraries available

PACKAGE_INFO: dict        # Complete package metadata
```

## Type Hints

The library uses type hints throughout. Key types:

```python
from typing import Union, Optional, Dict, Any, Tuple, List

# Common type aliases
Data = Union[str, bytes]
Key = Union[str, bytes]
Path = str
```

## Constants

### Key Sizes
- AES-256: 32 bytes (256 bits)
- ChaCha20: 32 bytes (256 bits)
- RSA-4096: 512 bytes (4096 bits)

### IV/Nonce Sizes
- AES-GCM: 12 bytes (96 bits)
- AES-CBC: 16 bytes (128 bits)
- ChaCha20: 12 bytes (96 bits)

### Tag Sizes
- GCM Tag: 16 bytes (128 bits)
- Poly1305 Tag: 16 bytes (128 bits)
- HMAC-SHA256: 32 bytes (256 bits)

### Recommended Settings

**Fast Performance:**
```python
SecureCompressor(
    password="...",
    compression_algorithm=CompressionAlgorithmType.ZLIB,
    compression_level=3,
    encryption_algorithm=EncryptionAlgorithmType.AES_256_GCM,
    kdf_algorithm='pbkdf2',
    kdf_iterations=100000
)
```

**Maximum Compression:**
```python
SecureCompressor(
    password="...",
    compression_algorithm=CompressionAlgorithmType.LZMA,
    compression_level=9,
    encryption_algorithm=EncryptionAlgorithmType.AES_256_GCM,
    kdf_algorithm='pbkdf2',
    kdf_iterations=100000
)
```

**Maximum Security:**
```python
SecureCompressor(
    password="...",
    compression_algorithm=CompressionAlgorithmType.LZMA,
    compression_level=6,
    encryption_algorithm=EncryptionAlgorithmType.AES_256_GCM,
    kdf_algorithm='argon2',
    kdf_iterations=200000
)
```

## Examples

### Basic Usage
```python
import fastcrypter

compressor = fastcrypter.SecureCompressor(password="secure_password")
encrypted = compressor.compress_and_encrypt(b"data")
decrypted = compressor.decrypt_and_decompress(encrypted)
```

### File Encryption
```python
from fastcrypter import FileEncryptor

encryptor = FileEncryptor(password="password")
encryptor.encrypt_file("input.txt", "output.encrypted")
encryptor.decrypt_file("output.encrypted", "restored.txt")
```

### Custom Encoding
```python
from fastcrypter import CustomEncoder

encoder = CustomEncoder(charset="0123456789abcdef")
encoded = encoder.encode(b"Hello")
decoded = encoder.decode(encoded)
```

### Advanced Configuration
```python
from fastcrypter import SecureCompressor, CompressionAlgorithmType, EncryptionAlgorithmType

compressor = SecureCompressor(
    password="very_secure_password",
    compression_algorithm=CompressionAlgorithmType.BROTLI,
    compression_level=6,
    encryption_algorithm=EncryptionAlgorithmType.CHACHA20_POLY1305,
    kdf_algorithm='argon2',
    kdf_iterations=150000
)
```

## Performance Considerations

1. **Compression Speed**: ZLIB > Brotli > LZMA
2. **Compression Ratio**: LZMA > Brotli > ZLIB
3. **Encryption Speed**: ChaCha20 ≈ AES-GCM (with hardware) > AES-CBC
4. **KDF Security**: Argon2 > Scrypt > PBKDF2
5. **KDF Speed**: PBKDF2 > Scrypt > Argon2

Enable native acceleration for best performance:
```python
compressor = fastcrypter.get_recommended_compressor(password="...")
```

## Thread Safety

- `SecureCompressor`: Not thread-safe, create separate instances per thread
- `Compressor`: Not thread-safe
- `Encryptor`: Not thread-safe
- `KeyManager`: Thread-safe for read operations, not for write operations
- `CustomEncoder`: Thread-safe

## Memory Usage

Typical memory usage:
- Small data (<1MB): ~2-3x data size
- Large data (>10MB): ~1.5x data size (streaming)
- Native acceleration: Slightly higher memory usage for better speed

For very large files, consider processing in chunks to limit memory usage.
