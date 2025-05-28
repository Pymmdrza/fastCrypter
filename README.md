# 🚀 fastCrypter

**Professional Compression and Encryption Library with Native C/C++ Acceleration**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/fastCrypter.svg)](https://pypi.org/project/fastCrypter/)
[![Downloads](https://img.shields.io/pypi/dm/fastCrypter.svg)](https://pypi.org/project/fastCrypter/)

fastCrypter is a powerful Python library that combines advanced compression and encryption techniques with native C/C++ acceleration for maximum performance. It provides a comprehensive suite of tools for secure data handling, from simple file encryption to complex custom encoding schemes.

## ✨ Key Features

### 🔐 **Advanced Encryption**
- **Multiple Algorithms**: AES-256-GCM, ChaCha20-Poly1305, RSA
- **Secure Key Management**: PBKDF2, Argon2, secure random generation
- **Digital Signatures**: RSA and ECC-based signing
- **Custom Encoding**: User-defined character sets for obfuscation

### 🗜️ **High-Performance Compression**
- **Multiple Formats**: ZLIB, LZMA, Brotli, custom RLE
- **Adaptive Algorithms**: Automatic best-fit selection
- **Native Acceleration**: C/C++ libraries for critical operations
- **Memory Efficient**: Streaming support for large files

### ⚡ **Native Performance**
- **C/C++ Libraries**: Optimized crypto and hash operations
- **SIMD Instructions**: Vectorized operations where available
- **Cross-Platform**: Windows (.dll), Linux (.so), macOS (.dylib)
- **Automatic Fallback**: Pure Python when native libs unavailable

### 🛡️ **Security Features**
- **Secure Memory**: Protected key storage and cleanup
- **Entropy Analysis**: Data randomness validation
- **Side-Channel Protection**: Constant-time operations
- **Audit Trail**: Comprehensive logging and validation

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install fastCrypter

# Install with development dependencies
pip install fastCrypter[dev]

# Install with native compilation support
pip install fastCrypter[native]
```

### Basic Usage

```python
import fastCrypterer

# Get the recommended compressor (automatically uses native acceleration if available)
compressor = fastCrypterer.get_recommended_compressor(password="your_secure_password")

# Compress and encrypt data
data = b"Your sensitive data here"
encrypted = compressor.compress_and_encrypt(data)

# Decrypt and decompress
decrypted = compressor.decrypt_and_decompress(encrypted)
assert data == decrypted
```

### Custom Encoding Example

```python
from fastCrypterer import CustomEncoder

# Create custom encoder with your character set
encoder = CustomEncoder(charset="abcdef98Xvbvii")

# Encode data
original = b"Hello, World!"
encoded = encoder.encode(original)
print(f"Encoded: {encoded}")

# Decode back
decoded = encoder.decode(encoded)
assert original == decoded
```

### File Encryption

```python
from fastCrypterer import FileEncryptor

# Initialize file encryptor
encryptor = FileEncryptor(password="your_password")

# Encrypt a file
encryptor.encrypt_file("document.pdf", "document.pdf.encrypted")

# Decrypt the file
encryptor.decrypt_file("document.pdf.encrypted", "document_restored.pdf")
```

## 🏗️ Architecture

fastCrypter is built with a modular architecture:

```
fastCrypter/
├── core/                 # Core functionality
│   ├── compressor.py     # Compression algorithms
│   ├── encryptor.py      # Encryption algorithms
│   ├── key_manager.py    # Key derivation and management
│   └── custom_encoder.py # Custom encoding schemes
├── algorithms/           # Algorithm implementations
│   ├── compression/      # Compression algorithms
│   └── encryption/       # Encryption algorithms
├── native/              # Native C/C++ libraries
│   ├── libs/            # Compiled libraries (.so/.dll/.dylib)
│   └── native_loader.py # Python bindings
├── utils/               # Utility functions
└── exceptions.py        # Custom exceptions
```

## 🔧 Native Compilation

fastCrypter includes C/C++ libraries for performance-critical operations:

### Automatic Compilation

```bash
# Build native libraries
python build_native.py

# Build with specific compiler
python build_native.py --compiler gcc

# Build optimized release version
python build_native.py --release
```

### Manual Compilation

```bash
# Using Make (Linux/macOS)
cd fastCrypter/native
make all

# Using MinGW (Windows)
cd fastCrypter/native
mingw32-make all
```

### Performance Benefits

Native libraries provide significant performance improvements:

- **XOR Operations**: 3-5x faster with SIMD instructions
- **Hash Functions**: 2-3x faster SHA-256 and HMAC
- **Key Derivation**: 2-4x faster PBKDF2
- **Compression**: 1.5-2x faster RLE compression

## 📊 Performance Benchmarks

```python
# Run comprehensive benchmarks
results = fastCrypter.benchmark_available_features(data_size=1024*1024)
print(f"Native acceleration: {results['performance']['native']['available']}")
print(f"Speedup factor: {results['performance'].get('speedup', 'N/A')}")
```

Example results on modern hardware:
- **Standard Mode**: ~50 MB/s compression + encryption
- **Enhanced Mode**: ~150 MB/s with native acceleration
- **Memory Usage**: <100MB for 1GB files (streaming)

## 🔍 Advanced Features

### Enhanced Compressor

```python
from fastCrypterer import EnhancedCompressor

# Create enhanced compressor with native acceleration
compressor = EnhancedCompressor(
    password="secure_password",
    use_native=True,
    compression_level=6
)

# Check if native libraries are available
if compressor.is_native_available():
    print("🚀 Native acceleration enabled!")
```

### Custom Algorithms

```python
from fastCrypterer.core import Compressor, CompressionAlgorithmType

# Use specific compression algorithm
compressor = Compressor(
    algorithm=CompressionAlgorithmType.BROTLI,
    level=9  # Maximum compression
)
```

### Secure Key Management

```python
from fastCrypterer import KeyManager

# Generate secure keys
key_manager = KeyManager()
master_key = key_manager.generate_key(password="user_password", salt=b"unique_salt")

# Derive multiple keys from master key
encryption_key = key_manager.derive_key(master_key, b"encryption", 32)
signing_key = key_manager.derive_key(master_key, b"signing", 32)
```

## 🧪 Testing

fastCrypter includes comprehensive tests:

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=fastCrypter --cov-report=html

# Run performance tests
python -m pytest tests/test_performance.py -v

# Run native library tests
python final_test.py
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/Pymmdrza/fastCrypter.git
cd fastCrypter

# Install in development mode
pip install -e .[dev]

# Build native libraries
python build_native.py

# Run tests
python -m pytest
```

### Code Quality

```bash
# Format code
black fastCrypter/ tests/

# Lint code
flake8 fastCrypter/ tests/

# Type checking
mypy fastCrypter/
```

## 📚 Documentation

- **API Reference**: [docs.fastCrypter.dev](https://docs.fastCrypter.dev)
- **Examples**: See `examples/` directory
- **Performance Guide**: [Performance Optimization](docs/performance.md)
- **Security Guide**: [Security Best Practices](docs/security.md)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Cryptography**: Built on industry-standard libraries
- **Performance**: Inspired by high-performance computing practices
- **Security**: Following OWASP and NIST guidelines
- **Community**: Thanks to all contributors and users

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Pymmdrza/fastCrypter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Pymmdrza/fastCrypter/discussions)
- **Email**: pymmdrza@gmail.com

---

**fastCrypter** - Making encryption fast, secure, and accessible! 🚀🔐 