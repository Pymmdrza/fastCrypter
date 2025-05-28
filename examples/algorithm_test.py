#!/usr/bin/env python3
"""
Algorithm testing for the Encrypter package

This file tests all compression and encryption algorithms.
"""

import sys
import os
import time

# Add the parent directory to the path so we can import encrypter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encrypter import SecureCompressor
from encrypter.core.compressor import CompressionAlgorithmType
from encrypter.core.encryptor import EncryptionAlgorithmType


def test_algorithm_combination(comp_algo, enc_algo, test_data, password):
    """Test specific algorithm combination."""
    try:
        # Create compressor with specified algorithms
        compressor = SecureCompressor(
            password=password,
            compression_algorithm=comp_algo,
            encryption_algorithm=enc_algo
        )
        
        # Measure compression and encryption time
        start_time = time.time()
        encrypted_data = compressor.compress_and_encrypt(test_data)
        encrypt_time = time.time() - start_time
        
        # Measure decryption and decompression time
        start_time = time.time()
        decrypted_data = compressor.decrypt_and_decompress_to_string(encrypted_data)
        decrypt_time = time.time() - start_time
        
        # Check correctness
        success = test_data.strip() == decrypted_data.strip()
        
        # Calculate compression ratio
        ratio = len(encrypted_data) / len(test_data.encode('utf-8'))
        
        return {
            'success': success,
            'original_size': len(test_data.encode('utf-8')),
            'compressed_size': len(encrypted_data),
            'compression_ratio': ratio,
            'encrypt_time': encrypt_time,
            'decrypt_time': decrypt_time,
            'total_time': encrypt_time + decrypt_time,
            'throughput': len(test_data.encode('utf-8')) / max(encrypt_time + decrypt_time, 0.001) / 1024,  # KB/s, avoid division by zero
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    """Main test function."""
    print("🧪 Algorithm Testing for Encrypter Package")
    print("=" * 60)
    
    # Test data
    test_data = """
    This is a longer text for testing different algorithms.
    It contains both English and various characters and is designed
    to evaluate the performance of compression and encryption algorithms.
    
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod 
    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim 
    veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea 
    commodo consequat. Duis aute irure dolor in reprehenderit in voluptate 
    velit esse cillum dolore eu fugiat nulla pariatur.
    
    Additional English text to increase data volume and better evaluate
    compression algorithm performance. This section includes various words
    and phrases that can be used in different tests and evaluations.
    """ * 3  # Repeat to increase volume
    
    password = "TestPassword123!"
    
    print(f"📊 Test data size: {len(test_data.encode('utf-8'))} bytes")
    print()
    
    # Compression algorithms
    compression_algorithms = [
        CompressionAlgorithmType.ZLIB,
        CompressionAlgorithmType.LZMA,
        CompressionAlgorithmType.BROTLI,
    ]
    
    # Encryption algorithms
    encryption_algorithms = [
        EncryptionAlgorithmType.AES_256_GCM,
        EncryptionAlgorithmType.AES_256_CBC,
        EncryptionAlgorithmType.CHACHA20_POLY1305,
    ]
    
    results = []
    
    print("🔄 Testing different combinations...")
    print()
    
    for comp_algo in compression_algorithms:
        for enc_algo in encryption_algorithms:
            combo_name = f"{comp_algo.value.upper()} + {enc_algo.value.upper()}"
            print(f"   Testing {combo_name}...", end=" ")
            
            result = test_algorithm_combination(comp_algo, enc_algo, test_data, password)
            result['combination'] = combo_name
            result['compression_algorithm'] = comp_algo.value
            result['encryption_algorithm'] = enc_algo.value
            results.append(result)
            
            if result['success']:
                print(f"✅ Success ({result['compression_ratio']:.2f}x)")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    print()
    print("📈 Detailed results:")
    print("-" * 100)
    print(f"{'Combination':<25} {'Ratio':<8} {'Total Time':<10} {'Speed':<12} {'Status':<8}")
    print("-" * 100)
    
    successful_results = [r for r in results if r['success']]
    
    for result in successful_results:
        print(f"{result['combination']:<25} "
              f"{result['compression_ratio']:.2f}x    "
              f"{result['total_time']:.3f}s     "
              f"{result['throughput']:.1f} KB/s   "
              f"{'✅' if result['success'] else '❌'}")
    
    if successful_results:
        print()
        print("🏆 Best results:")
        
        # Best compression ratio
        best_compression = min(successful_results, key=lambda x: x['compression_ratio'])
        print(f"   Best compression: {best_compression['combination']} ({best_compression['compression_ratio']:.2f}x)")
        
        # Best speed
        best_speed = max(successful_results, key=lambda x: x['throughput'])
        print(f"   Best speed: {best_speed['combination']} ({best_speed['throughput']:.1f} KB/s)")
        
        # Best total time
        best_time = min(successful_results, key=lambda x: x['total_time'])
        print(f"   Fastest time: {best_time['combination']} ({best_time['total_time']:.3f}s)")
    
    print()
    
    # Password strength testing
    print("🔐 Password strength testing:")
    test_passwords = [
        "password",
        "MyPassword123",
        "MySecurePassword123!",
        "VeryLongAndSecurePassword123!@#$%"
    ]
    
    compressor = SecureCompressor(password="TempPassword123!")
    
    for pwd in test_passwords:
        try:
            compressor.change_password(pwd)
            strength = compressor.validate_password_strength()
            print(f"   '{pwd}': {strength['strength']} ({strength['score']}/{strength['max_score']})")
        except Exception as e:
            print(f"   '{pwd}': ❌ {str(e)}")
    
    # Test weak passwords
    print("\n   Weak password testing:")
    weak_passwords = ["123", "abc"]
    for pwd in weak_passwords:
        try:
            compressor.change_password(pwd)
            print(f"   '{pwd}': Should not be accepted!")
        except Exception as e:
            print(f"   '{pwd}': ❌ Rejected - {str(e)}")
    
    print()
    print("🎉 Tests completed!")
    
    return 0


if __name__ == "__main__":
    exit(main()) 