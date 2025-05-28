# 🔐 Encrypter - Professional Compression and Encryption Package

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Military%20Grade-red.svg)](docs/security.md)

A powerful and secure Python package for data compression and encryption using modern and secure algorithms.

## ✨ Key Features

- 🔒 **Military-grade Encryption**: AES-256-GCM, ChaCha20-Poly1305, RSA-4096
- 🗜️ **Advanced Compression**: ZLIB, LZMA, Brotli
- ⚡ **High Performance**: Optimized for speed and memory
- 🛡️ **Multi-layer Security**: PBKDF2, HMAC, Secure Random
- 🔧 **Simple API**: Easy to use with advanced capabilities
- 📦 **Extensible**: Modular and scalable architecture

## 🚀 Quick Installation

```bash
pip install encrypter
```

Or from source:

```bash
git clone https://github.com/yourusername/encrypter.git
cd encrypter
pip install -e .
```

## 📖 Quick Usage

### Simple Compression and Encryption

```python
from encrypter import SecureCompressor

# Create instance
compressor = SecureCompressor(password="your_secure_password")

# Compress and encrypt
data = "Your important data"
encrypted_data = compressor.compress_and_encrypt(data)

# Decrypt and decompress
decrypted_data = compressor.decrypt_and_decompress(encrypted_data)
print(decrypted_data)  # "Your important data"
```

### Working with Files

```python
from encrypter import FileEncryptor

# Encrypt file
encryptor = FileEncryptor(password="secure_password")
encryptor.encrypt_file("document.pdf", "document.pdf.enc")

# Decrypt file
encryptor.decrypt_file("document.pdf.enc", "document_decrypted.pdf")
```

### Advanced Usage

```python
from encrypter import AdvancedEncryptor
from encrypter.algorithms import AESEncryption, LZMACompression

# Custom settings
encryptor = AdvancedEncryptor(
    encryption_algorithm=AESEncryption(),
    compression_algorithm=LZMACompression(level=9),
    key_derivation_iterations=100000
)

# Process large data
with encryptor.stream_processor() as processor:
    for chunk in large_data_chunks:
        encrypted_chunk = processor.process(chunk)
        # Save or send chunk
```

## 🔧 Supported Algorithms

### Encryption
- **AES-256-GCM**: Gold standard for symmetric encryption
- **ChaCha20-Poly1305**: Modern and fast encryption
- **RSA-4096**: Asymmetric encryption for keys

### Compression
- **ZLIB**: Fast and efficient
- **LZMA**: High compression ratio
- **Brotli**: Modern and optimized

### Security
- **PBKDF2**: Key derivation from password
- **Argon2**: Advanced password hashing
- **HMAC-SHA256**: Authentication

## 📊 Performance Comparison

| Algorithm | Speed | Compression Ratio | Security |
|----------|-------|------------------|----------|
| AES+ZLIB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| ChaCha20+LZMA | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| AES+Brotli | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 🛡️ Security Features

- **Zero-Knowledge**: No information is stored
- **Perfect Forward Secrecy**: Future-proof security
- **Side-Channel Resistance**: Resistant to side-channel attacks
- **Memory Protection**: Secure memory cleanup
- **Constant-Time Operations**: Timing attack resistant

## 📁 Project Structure

```
encrypter/
├── core/                  # Core components
│   ├── compressor.py      # Compression
│   ├── encryptor.py       # Encryption
│   └── key_manager.py     # Key management
├── algorithms/            # Algorithms
│   ├── compression/       # Compression
│   └── encryption/        # Encryption
├── utils/                 # Utilities
└── exceptions.py          # Custom exceptions
```

## 🧪 Testing and Quality

```bash
# Run tests
pytest tests/

# Check code coverage
pytest --cov=encrypter tests/

# Security tests
python -m encrypter.security_tests
```

## 📚 Complete Documentation

- [API Reference](docs/api_reference.md)
- [Usage Examples](examples/)
- [Security Guide](docs/security.md)
- [Performance Optimization](docs/performance.md)

## 🤝 Contributing

We welcome your contributions! Please:

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Submit a Pull Request

## 📄 License

This project is released under the MIT License. See [LICENSE](LICENSE) file for details.

## ⚠️ Security Warning

This package is designed for serious use. Please:
- Use strong passwords
- Store keys securely
- Test thoroughly before production use

## 📞 Support

- 🐛 [Report Bug](https://github.com/yourusername/encrypter/issues)
- 💡 [Feature Request](https://github.com/yourusername/encrypter/issues)
- 📧 [Direct Contact](mailto:support@encrypter.dev)

---

**Built with ❤️ for your data security** 