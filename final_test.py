#!/usr/bin/env python3
"""
Final comprehensive test for fastCrypter package.
"""

import sys
if sys.platform.startswith("win"):
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        else:
            import os
            sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
    except Exception:
        pass

from fastCrypterer import SecureCompressor
import time

def test_basic_functionality():
    """Test basic compression and encryption functionality."""
    print("Testing basic functionality...")
    
    # Test data
    test_data = b"Hello, fastCrypter! This is a test message for compression and encryption."
    password = "TestPassword123!"
    
    # Create compressor
    compressor = SecureCompressor(password=password)
    
    # Compress and encrypt
    start_time = time.time()
    encrypted_data = compressor.compress_and_encrypt(test_data)
    encrypt_time = time.time() - start_time
    
    # Decrypt and decompress
    start_time = time.time()
    decrypted_data = compressor.decrypt_and_decompress(encrypted_data)
    decrypt_time = time.time() - start_time
    
    # Verify
    assert test_data == decrypted_data, "Data integrity check failed!"
    
    print(f"Basic test passed!")
    print(f"Original size: {len(test_data)} bytes")
    print(f"Encrypted size: {len(encrypted_data)} bytes")
    print(f"Compression ratio: {len(encrypted_data)/len(test_data):.2f}")
    print(f"Encrypt time: {encrypt_time*1000:.2f}ms")
    print(f"Decrypt time: {decrypt_time*1000:.2f}ms")

def test_custom_encoding():
    """Test custom encoding functionality."""
    print("\nTesting custom encoding...")
    
    try:
        from fastCrypterer import CustomEncoder
        
        # Test with custom charset
        charset = "abcdef98Xvbvii"
        encoder = CustomEncoder(charset=charset)
        
        test_data = b"Hello, World!"
        encoded = encoder.encode(test_data)
        decoded = encoder.decode(encoded)
        
        assert test_data == decoded, "Custom encoding integrity check failed!"
        
        # Verify only charset characters are used
        for char in encoded:
            assert char in charset, f"Invalid character '{char}' found in encoded output!"
        
        print(f"Custom encoding test passed!")
        print(f"   Charset: {charset}")
        print(f"   Original: {test_data}")
        print(f"   Encoded: {encoded}")
        print(f"   Decoded: {decoded}")
        
    except ImportError:
        print("CustomEncoder not available")

def test_enhanced_features():
    """Test enhanced compressor if available."""
    print("\nTesting enhanced features...")
    
    try:
        from fastCrypterer import EnhancedCompressor, ENHANCED_AVAILABLE, NATIVE_SUPPORT
        
        print(f"Enhanced compressor available: {ENHANCED_AVAILABLE}")
        print(f"Native support available: {NATIVE_SUPPORT}")
        
        if ENHANCED_AVAILABLE:
            compressor = EnhancedCompressor(password="TestPassword123!")
            print(f"Native libraries loaded: {compressor.is_native_available()}")
            
            # Test basic functionality
            test_data = b"Enhanced compressor test data"
            encrypted = compressor.compress_and_encrypt(test_data)
            decrypted = compressor.decrypt_and_decompress(encrypted)
            
            assert test_data == decrypted, "Enhanced compressor integrity check failed!"
            print("Enhanced compressor test passed!")
        else:
            print("Enhanced compressor not available")
            
    except ImportError as e:
        print(f"Enhanced features not available: {e}")

def test_package_info():
    """Test package information."""
    print("\nTesting package information...")
    
    import fastCrypterer
    
    print(f"   Package: {fastCrypterer.__name__}")
    print(f"   Version: {fastCrypterer.__version__}")
    print(f"   Author: {fastCrypterer.__author__}")
    print(f"   Email: {fastCrypterer.__email__}")
    print(f"   License: {fastCrypterer.__license__}")
    
    # Test package info
    info = fastCrypterer.get_version_info()
    print(f"   URL: {info['url']}")
    print(f"   Features: {list(info['features'].keys())}")
    
    print("Package information test passed!")

def main():
    """Run all tests."""
    print("fastCrypter Final Test Suite")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_custom_encoding()
        test_enhanced_features()
        test_package_info()
        
        print("\n" + "=" * 50)
        print("All tests passed! fastCrypter is ready to use!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 