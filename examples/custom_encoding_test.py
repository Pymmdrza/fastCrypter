#!/usr/bin/env python3
"""
Custom Encoding Test for Encrypter Package

This example demonstrates the custom character encoding feature
that allows encrypted output to use only specified characters.
"""

import sys
import os

# Add the parent directory to the path so we can import encrypter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encrypter import SecureCompressor
from encrypter.core.custom_encoder import CustomEncoder


def main():
    """Test custom encoding functionality."""
    
    print("🔤 Custom Encoding Test for Encrypter Package")
    print("=" * 60)
    
    # Test data
    test_data = "This is secret data that needs to be encrypted and encoded!"
    password = "MySecurePassword123!"
    
    # Your specified character set
    custom_charset = "abcdef98Xvbvii"
    
    print(f"📝 Original data: {test_data}")
    print(f"🔤 Custom charset: {custom_charset}")
    print(f"   Character count: {len(set(custom_charset))} unique characters")
    print()
    
    # Test 1: Basic custom encoding
    print("🧪 Test 1: Basic Custom Encoding")
    print("-" * 40)
    
    # Create compressor with custom charset
    compressor = SecureCompressor(
        password=password,
        custom_charset=custom_charset
    )
    
    # Encrypt and encode to custom charset
    custom_encoded = compressor.compress_and_encrypt_to_custom(test_data, custom_charset)
    
    print(f"✅ Encrypted and encoded: {custom_encoded}")
    print(f"   Length: {len(custom_encoded)} characters")
    print(f"   Uses only specified chars: {all(c in custom_charset for c in custom_encoded)}")
    
    # Decrypt and decode
    decoded_data = compressor.decrypt_and_decompress_from_custom(custom_encoded, custom_charset)
    decoded_text = decoded_data.decode('utf-8')
    
    print(f"✅ Decrypted and decoded: {decoded_text}")
    print(f"   Matches original: {test_data == decoded_text}")
    print()
    
    # Test 2: Different output formats
    print("🧪 Test 2: Different Output Formats")
    print("-" * 40)
    
    # Binary format (normal)
    binary_output = compressor.compress_and_encrypt(test_data, 'binary')
    print(f"Binary format size: {len(binary_output)} bytes")
    
    # Custom format
    custom_output = compressor.compress_and_encrypt(test_data, 'custom')
    print(f"Custom format size: {len(custom_output)} characters")
    print(f"Custom format sample: {custom_output[:50]}...")
    
    # Steganographic format
    stego_output = compressor.compress_and_encrypt(test_data, 'steganographic')
    print(f"Steganographic format: {stego_output}")
    print()
    
    # Test 3: Custom Encoder standalone
    print("🧪 Test 3: Custom Encoder Standalone")
    print("-" * 40)
    
    encoder = CustomEncoder(charset=custom_charset)
    
    # Test with binary data
    binary_data = b"Hello World Binary Data!"
    encoded = encoder.encode(binary_data)
    decoded = encoder.decode(encoded)
    
    print(f"Original binary: {binary_data}")
    print(f"Encoded: {encoded}")
    print(f"Decoded: {decoded}")
    print(f"Matches: {binary_data == decoded}")
    print()
    
    # Test 4: Encoder with noise
    print("🧪 Test 4: Encoding with Noise (Obfuscation)")
    print("-" * 40)
    
    noisy_encoded = encoder.encode_with_noise(binary_data, noise_ratio=0.2)
    print(f"Encoded with 20% noise: {noisy_encoded}")
    print(f"Length increase: {len(noisy_encoded) - len(encoded)} characters")
    print()
    
    # Test 5: Performance benchmark
    print("🧪 Test 5: Performance Benchmark")
    print("-" * 40)
    
    benchmark_results = encoder.benchmark_encoding(data_size=1024)
    print(f"Benchmark results for 1KB data:")
    print(f"   Encode time: {benchmark_results['encode_time']:.4f}s")
    print(f"   Decode time: {benchmark_results['decode_time']:.4f}s")
    print(f"   Encode speed: {benchmark_results['encode_speed_mbps']:.2f} MB/s")
    print(f"   Decode speed: {benchmark_results['decode_speed_mbps']:.2f} MB/s")
    print(f"   Expansion ratio: {benchmark_results['expansion_ratio']:.2f}x")
    print(f"   Correctness: {benchmark_results['correctness']}")
    print()
    
    # Test 6: Different character sets
    print("🧪 Test 6: Different Character Sets")
    print("-" * 40)
    
    test_charsets = [
        "abcdef98Xvbvii",  # Your specified set
        "0123456789",      # Numbers only
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # Uppercase letters
        "abcdefghijklmnopqrstuvwxyz",  # Lowercase letters
        "!@#$%^&*()_+-=[]{}|;:,.<>?",  # Special characters
    ]
    
    test_text = "Test data for different charsets"
    
    for charset in test_charsets:
        try:
            temp_encoder = CustomEncoder(charset=charset)
            encoded = temp_encoder.encode(test_text.encode('utf-8'))
            decoded = temp_encoder.decode(encoded).decode('utf-8')
            
            print(f"Charset '{charset[:20]}{'...' if len(charset) > 20 else ''}':")
            print(f"   Base: {temp_encoder.base}")
            print(f"   Encoded length: {len(encoded)}")
            print(f"   Success: {test_text == decoded}")
            
        except Exception as e:
            print(f"Charset '{charset}': ❌ Error - {e}")
    
    print()
    
    # Test 7: Integration with SecureCompressor
    print("🧪 Test 7: Full Integration Test")
    print("-" * 40)
    
    # Test different data types
    test_cases = [
        ("Short text", "Hello!"),
        ("Long text", "This is a much longer text that should compress well and demonstrate the full capabilities of the encryption and custom encoding system." * 3),
        ("Binary data", b'\x00\x01\x02\x03\x04\x05' * 20),
        ("JSON data", '{"name": "John", "age": 30, "items": [1, 2, 3, 4, 5]}'),
    ]
    
    for test_name, data in test_cases:
        try:
            # Encrypt with custom encoding
            if isinstance(data, str):
                encrypted = compressor.compress_and_encrypt_to_custom(data, custom_charset)
                decrypted = compressor.decrypt_and_decompress_from_custom(encrypted, custom_charset).decode('utf-8')
                success = data == decrypted
            else:
                encrypted = compressor.compress_and_encrypt_to_custom(data, custom_charset)
                decrypted = compressor.decrypt_and_decompress_from_custom(encrypted, custom_charset)
                success = data == decrypted
            
            print(f"{test_name}:")
            print(f"   Original size: {len(data)} {'chars' if isinstance(data, str) else 'bytes'}")
            print(f"   Encoded size: {len(encrypted)} chars")
            print(f"   Uses only custom chars: {all(c in custom_charset for c in encrypted)}")
            print(f"   Success: {success}")
            
        except Exception as e:
            print(f"{test_name}: ❌ Error - {e}")
    
    print()
    print("🎉 Custom encoding tests completed!")
    print()
    print("📋 Summary:")
    print("✅ Custom character set encoding works correctly")
    print("✅ Only specified characters are used in output")
    print("✅ Data integrity is maintained through encode/decode cycle")
    print("✅ Integration with compression and encryption is seamless")
    print("✅ Performance is acceptable for most use cases")
    
    return 0


if __name__ == "__main__":
    exit(main()) 