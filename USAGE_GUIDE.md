# fastcrypter Usage Guide

This comprehensive guide covers all aspects of using the fastcrypter library for secure data compression and encryption.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Core Components](#core-components)
4. [Compression](#compression)
5. [Encryption](#encryption)
6. [Key Management](#key-management)
7. [Custom Encoding](#custom-encoding)
8. [File Operations](#file-operations)
9. [Advanced Usage](#advanced-usage)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

## Installation

### Basic Installation

Install fastcrypter from PyPI:

```bash
pip install fastcrypter
```

### Installation with Optional Features

```bash
# Development dependencies
pip install fastcrypter[dev]

# Native compilation support
pip install fastcrypter[native]

# Documentation generation
pip install fastcrypter[docs]

# All features
pip install fastcrypter[dev,native,docs]
```

### Verify Installation

```python
import fastcrypter
print(fastcrypter.__version__)
print(fastcrypter.get_version_info())
```

## Quick Start

### Basic Encryption and Compression

```python
import fastcrypter

# Create a secure compressor
compressor = fastcrypter.SecureCompressor(password="your_secure_password")

# Encrypt and compress data
data = b"Your sensitive data here"
encrypted = compressor.compress_and_encrypt(data)

# Decrypt and decompress
decrypted = compressor.decrypt_and_decompress(encrypted)

assert data == decrypted  # Verify data integrity
```

### Working with Text

```python
# Encrypt text
text = "Hello, World!"
encrypted = compressor.compress_and_encrypt_string(text)

# Decrypt to text
decrypted_text = compressor.decrypt_and_decompress_to_string(encrypted)

assert text == decrypted_text
```

## Core Components

### SecureCompressor

The main high-level interface combining compression and encryption:

```python
from fastcrypter import SecureCompressor, CompressionAlgorithmType, EncryptionAlgorithmType

compressor = SecureCompressor(
    password="strong_password",
    compression_algorithm=CompressionAlgorithmType.BROTLI,
    compression_level=6,
    encryption_algorithm=EncryptionAlgorithmType.AES_256_GCM,
    kdf_algorithm='pbkdf2',
    kdf_iterations=100000
)
```

### Getting Recommended Compressor

```python
# Automatically selects the best available compressor
# (EnhancedCompressor with native acceleration if available)
compressor = fastcrypter.get_recommended_compressor(
    password="your_password"
)
```

## Compression

### Using Different Compression Algorithms

```python
from fastcrypter.core import Compressor, CompressionAlgorithmType, CompressionLevel

# ZLIB (fast, balanced)
compressor = Compressor(
    algorithm=CompressionAlgorithmType.ZLIB,
    level=CompressionLevel.BALANCED
)

# LZMA (best compression)
compressor = Compressor(
    algorithm=CompressionAlgorithmType.LZMA,
    level=CompressionLevel.BEST
)

# Brotli (modern, efficient)
compressor = Compressor(
    algorithm=CompressionAlgorithmType.BROTLI,
    level=6
)

# Compress data
data = b"Data to compress"
compressed = compressor.compress(data)
decompressed = compressor.decompress(compressed)
```

### Automatic Algorithm Selection

```python
# Enable auto-select for best compression based on data characteristics
compressor = Compressor(auto_select=True)

# The compressor will automatically choose the best algorithm
compressed = compressor.compress(data)
```

### Checking Compression Ratio

```python
ratio = compressor.get_compression_ratio(original_data, compressed_data)
print(f"Compression ratio: {ratio:.2%}")
```

## Encryption

### Using Different Encryption Algorithms

```python
from fastcrypter.core import Encryptor, EncryptionAlgorithmType

# AES-256-GCM (recommended)
encryptor = Encryptor(algorithm=EncryptionAlgorithmType.AES_256_GCM)
encrypted = encryptor.encrypt(data, "password")
decrypted = encryptor.decrypt(encrypted, "password")

# ChaCha20-Poly1305 (modern, fast)
encryptor = Encryptor(algorithm=EncryptionAlgorithmType.CHACHA20_POLY1305)
encrypted = encryptor.encrypt(data, "password")

# AES-256-CBC with HMAC
encryptor = Encryptor(algorithm=EncryptionAlgorithmType.AES_256_CBC)
encrypted = encryptor.encrypt(data, "password")
```

### RSA Encryption

```python
# Generate RSA key pair
encryptor = Encryptor(algorithm=EncryptionAlgorithmType.RSA_4096)
private_key, public_key = encryptor.generate_rsa_keypair()

# Load keys
encryptor.load_rsa_keys(private_key_pem=private_key, public_key_pem=public_key)

# Encrypt with public key
encrypted = encryptor.encrypt(data, None)

# Decrypt with private key
decrypted = encryptor.decrypt(encrypted, None)
```

## Key Management

### Generating Keys

```python
from fastcrypter import KeyManager

key_manager = KeyManager()

# Generate random salt
salt = key_manager.generate_salt(length=32)

# Generate random key
random_key = key_manager.generate_key(length=32)
```

### Deriving Keys from Password

```python
# Using PBKDF2
key_manager = KeyManager(kdf_algorithm='pbkdf2', iterations=100000)
key, salt = key_manager.derive_key("user_password")

# Using Scrypt
key_manager = KeyManager(kdf_algorithm='scrypt')
key, salt = key_manager.derive_key("user_password")

# Using Argon2 (most secure)
key_manager = KeyManager(kdf_algorithm='argon2')
key, salt = key_manager.derive_key("user_password")
```

### Deriving Multiple Keys

```python
# Derive master key
master_key, salt = key_manager.derive_key("master_password")

# Derive sub-keys from master key
encryption_key = key_manager.derive_key(master_key, b"encryption", 32)
signing_key = key_manager.derive_key(master_key, b"signing", 32)
```

### Validating Key Strength

```python
is_strong = key_manager.validate_key_strength(key, min_entropy=4.0)
if not is_strong:
    print("Warning: Key may be weak")
```

## Custom Encoding

### Basic Custom Encoding

```python
from fastcrypter import CustomEncoder

# Create encoder with custom character set
encoder = CustomEncoder(charset="abcdef98Xvbvii")

# Encode binary data
data = b"Hello, World!"
encoded = encoder.encode(data)  # Returns string using only specified characters

# Decode back to binary
decoded = encoder.decode(encoded)

assert data == decoded
```

### Using Custom Encoding with Compression

```python
compressor = SecureCompressor(
    password="password",
    custom_charset="abcdefghijklmnop"
)

# Encrypt and encode with custom charset
encrypted = compressor.compress_and_encrypt(data, output_format='custom')

# Decrypt from custom format
decrypted = compressor.decrypt_and_decompress(encrypted, input_format='custom')
```

### Creating Steganographic Text

```python
encoder = CustomEncoder(charset="abcdefghij0123456789")

# Hide data in text
hidden_text = encoder.create_steganographic_text(
    data,
    template="The quick brown fox jumps over the lazy dog"
)
```

### Charset Information

```python
info = encoder.get_charset_info()
print(f"Base: {info['base']}")
print(f"Characters: {info['characters']}")
print(f"Efficiency: {info['efficiency']}")
```

## File Operations

### Encrypting Files

```python
from fastcrypter import FileEncryptor

# Create file encryptor
encryptor = FileEncryptor(password="file_password")

# Encrypt a file
stats = encryptor.encrypt_file(
    input_path="document.pdf",
    output_path="document.pdf.encrypted"
)

print(f"Original size: {stats['original_size']} bytes")
print(f"Encrypted size: {stats['encrypted_size']} bytes")
print(f"Compression ratio: {stats['compression_ratio']:.2%}")
```

### Decrypting Files

```python
# Decrypt a file
stats = encryptor.decrypt_file(
    input_path="document.pdf.encrypted",
    output_path="document_restored.pdf"
)

print(f"Decryption successful!")
print(f"Decrypted size: {stats['decrypted_size']} bytes")
```

### Batch File Operations

```python
import glob

# Encrypt multiple files
for file_path in glob.glob("*.txt"):
    encryptor.encrypt_file(file_path, f"{file_path}.encrypted")

# Decrypt multiple files
for file_path in glob.glob("*.encrypted"):
    original_name = file_path.replace(".encrypted", "")
    encryptor.decrypt_file(file_path, f"{original_name}.decrypted")
```

## Advanced Usage

### Enhanced Compressor with Native Acceleration

```python
from fastcrypter import EnhancedCompressor

# Create enhanced compressor
compressor = EnhancedCompressor(
    password="password",
    use_native=True,
    compression_level=6
)

# Check if native libraries are available
if compressor.is_native_available():
    print("Native acceleration enabled!")
    
# Use as normal
encrypted = compressor.compress_and_encrypt(data)
```

### Password Strength Validation

```python
compressor = SecureCompressor(password="password123")

# Validate password strength
strength = compressor.validate_password_strength()

print(f"Strength: {strength['strength']}")
print(f"Score: {strength['score']}/{strength['max_score']}")
print(f"Checks: {strength['checks']}")
print(f"Recommendations: {strength['recommendations']}")
```

### Changing Password

```python
# Change the password for future operations
compressor.change_password("new_stronger_password")
```

### Estimating Output Size

```python
estimates = compressor.estimate_output_size(input_size=1000000)  # 1MB

print(f"Estimated compressed size: {estimates['estimated_compressed_size']}")
print(f"Estimated encrypted size: {estimates['estimated_encrypted_size']}")
print(f"Estimated compression ratio: {estimates['estimated_compression_ratio']:.2%}")
```

### Benchmarking Performance

```python
# Benchmark different operations
results = compressor.benchmark_performance(data_size=1024*1024)  # 1MB

print(f"Encryption time: {results['binary']['encrypt_time']:.4f}s")
print(f"Decryption time: {results['binary']['decrypt_time']:.4f}s")
print(f"Throughput: {results['binary']['throughput_mbps']:.2f} MB/s")
print(f"Correctness: {results['binary']['correctness']}")
```

### Getting Component Information

```python
# Get comprehensive configuration info
info = compressor.get_info()

print(f"Compression: {info['compressor_info']['algorithm']}")
print(f"Encryption: {info['encryptor_info']['algorithm']}")
print(f"KDF: {info['key_manager_info']['kdf_algorithm']}")
print(f"Fast extensions: {info['fast_extensions']}")
```

## Best Practices

### Password Security

1. Use strong passwords (minimum 12 characters)
2. Include uppercase, lowercase, numbers, and special characters
3. Never hardcode passwords in source code
4. Use environment variables or secure key stores

```python
import os

# Good practice: read from environment
password = os.environ.get('ENCRYPTION_PASSWORD')
if not password:
    raise ValueError("ENCRYPTION_PASSWORD not set")

compressor = SecureCompressor(password=password)
```

### Memory Security

```python
# Clear sensitive data from memory when done
key_manager = KeyManager()
sensitive_data = bytearray(b"secret key material")

# ... use the data ...

# Clear it when done
key_manager.clear_memory(sensitive_data)
```

### Error Handling

```python
from fastcrypter.exceptions import (
    EncrypterError, CompressionError, EncryptionError,
    ValidationError, KeyError, ErrorCodes
)

try:
    encrypted = compressor.compress_and_encrypt(data)
except ValidationError as e:
    print(f"Validation error: {e} (Code: {e.error_code})")
except EncryptionError as e:
    print(f"Encryption error: {e} (Code: {e.error_code})")
except CompressionError as e:
    print(f"Compression error: {e} (Code: {e.error_code})")
except EncrypterError as e:
    print(f"General error: {e}")
```

### Algorithm Selection

- **For speed**: ZLIB compression + AES-GCM encryption
- **For size**: LZMA compression + AES-GCM encryption  
- **For balance**: Brotli compression + ChaCha20-Poly1305 encryption
- **For maximum security**: LZMA + AES-256-GCM + Argon2 KDF

```python
# Fast configuration
fast_compressor = SecureCompressor(
    password="password",
    compression_algorithm=CompressionAlgorithmType.ZLIB,
    encryption_algorithm=EncryptionAlgorithmType.AES_256_GCM,
    kdf_algorithm='pbkdf2'
)

# Maximum security configuration
secure_compressor = SecureCompressor(
    password="very_strong_password",
    compression_algorithm=CompressionAlgorithmType.LZMA,
    encryption_algorithm=EncryptionAlgorithmType.AES_256_GCM,
    kdf_algorithm='argon2',
    kdf_iterations=200000
)
```

## Troubleshooting

### Import Errors

```python
# Check if native features are available
import fastcrypter

print(f"Enhanced available: {fastcrypter.ENHANCED_AVAILABLE}")
print(f"Native support: {fastcrypter.NATIVE_SUPPORT}")

# If native features are missing, install build dependencies
# pip install fastcrypter[native]
```

### Decryption Failures

1. **Wrong password**: Most common cause
2. **Corrupted data**: Check file integrity
3. **Different algorithm**: Ensure same configuration

```python
try:
    decrypted = compressor.decrypt_and_decompress(encrypted)
except EncryptionError as e:
    if e.error_code == ErrorCodes.DECRYPTION_FAILED:
        print("Check password and data integrity")
    elif e.error_code == ErrorCodes.TAMPERING_DETECTED:
        print("Data may have been modified")
```

### Performance Issues

1. Try using enhanced compressor with native acceleration
2. Adjust compression level (lower = faster, higher = smaller)
3. Use ZLIB for speed, LZMA for size
4. For large files, process in chunks

```python
# For better performance
compressor = fastcrypter.get_recommended_compressor(
    password="password"
)

# Check if native acceleration is active
info = compressor.get_info()
if info['fast_extensions']['enabled']:
    print("Native acceleration active")
```

### Memory Issues with Large Files

```python
# For very large files, process in chunks
def encrypt_large_file(input_path, output_path, password, chunk_size=1024*1024):
    compressor = SecureCompressor(password=password)
    
    with open(input_path, 'rb') as fin:
        with open(output_path, 'wb') as fout:
            while True:
                chunk = fin.read(chunk_size)
                if not chunk:
                    break
                encrypted = compressor.compress_and_encrypt(chunk)
                # Write chunk size first for later reconstruction
                fout.write(len(encrypted).to_bytes(4, 'big'))
                fout.write(encrypted)
```

## Additional Resources

- **API Reference**: See API_REFERENCE.md for detailed API documentation
- **Examples**: Check the examples/ directory for more examples
- **Issues**: Report bugs at https://github.com/Pymmdrza/fastCrypter/issues
- **Discussions**: Ask questions at https://github.com/Pymmdrza/fastCrypter/discussions
