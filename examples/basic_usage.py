#!/usr/bin/env python3
"""
Basic usage example of the Encrypter package

This file demonstrates how to use the main features of the package.
"""

import sys
import os

# Add the parent directory to the path so we can import encrypter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encrypter import SecureCompressor


def main():
    """Basic usage example of SecureCompressor."""
    
    print("🔐 Encrypter Package Usage Example")
    print("=" * 50)
    
    # Create SecureCompressor instance
    password = "MySecurePassword123!"
    compressor = SecureCompressor(password=password)
    
    print(f"✅ SecureCompressor created: {compressor}")
    print()
    
    # Sample data
    sample_data = """
    This is a sample text for testing compression and encryption.
    This text contains both Persian and English characters.
    
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
    
    Additional text to increase data volume for better testing of
    compression algorithms. This section includes various words and
    phrases that can be used in different tests.
    """
    
    print("📝 Original data:")
    print(f"   Length: {len(sample_data)} bytes")
    print(f"   Content: {sample_data[:100]}...")
    print()
    
    try:
        # Compression and encryption
        print("🔄 Compressing and encrypting...")
        encrypted_data = compressor.compress_and_encrypt(sample_data)
        
        print(f"✅ Compression and encryption successful:")
        print(f"   Final length: {len(encrypted_data)} bytes")
        
        # Calculate compression ratio
        ratio = compressor.get_compression_ratio(sample_data, encrypted_data)
        print(f"   Compression ratio: {ratio:.2f} ({ratio*100:.1f}%)")
        print()
        
        # Decryption and decompression
        print("🔄 Decrypting and decompressing...")
        decrypted_data = compressor.decrypt_and_decompress_to_string(encrypted_data)
        
        print("✅ Decryption and decompression successful:")
        print(f"   Recovered length: {len(decrypted_data)} bytes")
        print(f"   Content: {decrypted_data[:100]}...")
        print()
        
        # Verify data integrity
        if sample_data.strip() == decrypted_data.strip():
            print("✅ Data successfully recovered!")
        else:
            print("❌ Error: Recovered data does not match original!")
        
        print()
        
        # Display configuration information
        print("📊 Configuration information:")
        info = compressor.get_info()
        print(f"   Compression algorithm: {info['compressor_info']['algorithm']}")
        print(f"   Encryption algorithm: {info['encryptor_info']['algorithm']}")
        print(f"   Password strength: {info['password_strength']['strength']}")
        print()
        
        # Test with different data types
        print("🧪 Testing with different data types:")
        
        # Short text
        short_text = "Hello World!"
        encrypted_short = compressor.compress_and_encrypt(short_text)
        decrypted_short = compressor.decrypt_and_decompress_to_string(encrypted_short)
        print(f"   Short text: '{short_text}' -> {len(encrypted_short)} bytes -> '{decrypted_short}'")
        
        # Binary data
        binary_data = b'\x00\x01\x02\x03\x04\x05' * 100
        encrypted_binary = compressor.compress_and_encrypt(binary_data)
        decrypted_binary = compressor.decrypt_and_decompress(encrypted_binary)
        print(f"   Binary data: {len(binary_data)} bytes -> {len(encrypted_binary)} bytes -> {len(decrypted_binary)} bytes")
        
        # JSON data
        import json
        json_data = json.dumps({
            "name": "John Doe",
            "age": 30,
            "city": "New York",
            "hobbies": ["programming", "reading", "sports"]
        }, indent=2)
        
        encrypted_json = compressor.compress_and_encrypt(json_data)
        decrypted_json = compressor.decrypt_and_decompress_to_string(encrypted_json)
        print(f"   JSON: {len(json_data)} bytes -> {len(encrypted_json)} bytes")
        
        print()
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 