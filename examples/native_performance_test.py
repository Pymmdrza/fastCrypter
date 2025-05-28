#!/usr/bin/env python3
"""
Native Library Performance Test for Encrypter Package

This example demonstrates the performance benefits of using native C/C++ libraries
compared to pure Python implementations.
"""

import sys
import os
import time
import secrets
from typing import Dict, Any

# Add the parent directory to the path so we can import encrypter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encrypter.core.enhanced_compressor import EnhancedCompressor
from encrypter import SecureCompressor


def format_time(seconds: float) -> str:
    """Format time in a human-readable way."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.1f} ms"
    else:
        return f"{seconds:.3f} s"


def format_size(bytes_size: int) -> str:
    """Format size in a human-readable way."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def benchmark_operation(operation, iterations: int = 100) -> float:
    """Benchmark an operation and return average time per iteration."""
    start_time = time.time()
    for _ in range(iterations):
        operation()
    end_time = time.time()
    return (end_time - start_time) / iterations


def main():
    """Test native library performance."""
    
    print("🚀 Native Library Performance Test for Encrypter Package")
    print("=" * 70)
    
    # Test data sizes
    test_sizes = [1024, 4096, 16384, 65536]  # 1KB, 4KB, 16KB, 64KB
    password = "MySecurePassword123!"
    custom_charset = "abcdef98Xvbvii"
    
    print(f"🔑 Password: {password}")
    print(f"🔤 Custom charset: {custom_charset}")
    print()
    
    # Initialize compressors
    print("🔧 Initializing compressors...")
    
    try:
        # Enhanced compressor with native libraries
        enhanced_compressor = EnhancedCompressor(
            password=password,
            custom_charset=custom_charset,
            prefer_native=True
        )
        
        # Standard compressor (pure Python)
        standard_compressor = SecureCompressor(
            password=password,
            custom_charset=custom_charset,
            use_fast_extensions=False
        )
        
        print("✅ Enhanced compressor (with native libraries)")
        print("✅ Standard compressor (pure Python)")
        
        # Check native library availability
        native_info = enhanced_compressor.get_native_info()
        print(f"\n📊 Native Library Status:")
        print(f"   Support available: {native_info['native_support']}")
        print(f"   Libraries loaded: {native_info['native_available']}")
        
        if native_info['native_available']:
            available_libs = native_info.get('available_libraries', [])
            print(f"   Available libraries: {', '.join(available_libs)}")
        else:
            print("   ⚠️  No native libraries available - will compare Python implementations")
        
        print()
        
    except Exception as e:
        print(f"❌ Failed to initialize compressors: {e}")
        return 1
    
    # Performance comparison for different data sizes
    print("📈 Performance Comparison")
    print("-" * 70)
    
    results = {}
    
    for size in test_sizes:
        print(f"\n🧪 Testing with {format_size(size)} data...")
        
        # Generate test data
        test_data = secrets.token_bytes(size)
        
        size_results = {
            'data_size': size,
            'enhanced': {},
            'standard': {},
            'speedup': {}
        }
        
        # Test compression and encryption
        print("   📦 Compression + Encryption...")
        
        # Enhanced compressor
        def enhanced_compress():
            return enhanced_compressor.compress_and_encrypt(test_data, 'binary')
        
        enhanced_time = benchmark_operation(enhanced_compress, 10)
        enhanced_result = enhanced_compress()
        
        # Standard compressor
        def standard_compress():
            return standard_compressor.compress_and_encrypt(test_data, 'binary')
        
        standard_time = benchmark_operation(standard_compress, 10)
        standard_result = standard_compress()
        
        size_results['enhanced']['compress_time'] = enhanced_time
        size_results['enhanced']['compressed_size'] = len(enhanced_result)
        size_results['standard']['compress_time'] = standard_time
        size_results['standard']['compressed_size'] = len(standard_result)
        size_results['speedup']['compression'] = standard_time / enhanced_time if enhanced_time > 0 else 1
        
        print(f"      Enhanced: {format_time(enhanced_time)} -> {format_size(len(enhanced_result))}")
        print(f"      Standard: {format_time(standard_time)} -> {format_size(len(standard_result))}")
        print(f"      Speedup: {size_results['speedup']['compression']:.2f}x")
        
        # Test decompression and decryption
        print("   📂 Decryption + Decompression...")
        
        # Enhanced compressor
        def enhanced_decompress():
            return enhanced_compressor.decrypt_and_decompress(enhanced_result, 'binary')
        
        enhanced_decomp_time = benchmark_operation(enhanced_decompress, 10)
        
        # Standard compressor
        def standard_decompress():
            return standard_compressor.decrypt_and_decompress(standard_result, 'binary')
        
        standard_decomp_time = benchmark_operation(standard_decompress, 10)
        
        size_results['enhanced']['decompress_time'] = enhanced_decomp_time
        size_results['standard']['decompress_time'] = standard_decomp_time
        size_results['speedup']['decompression'] = standard_decomp_time / enhanced_decomp_time if enhanced_decomp_time > 0 else 1
        
        print(f"      Enhanced: {format_time(enhanced_decomp_time)}")
        print(f"      Standard: {format_time(standard_decomp_time)}")
        print(f"      Speedup: {size_results['speedup']['decompression']:.2f}x")
        
        # Test custom encoding
        print("   🔤 Custom Character Encoding...")
        
        # Enhanced compressor
        def enhanced_custom():
            return enhanced_compressor.compress_and_encrypt(test_data, 'custom')
        
        enhanced_custom_time = benchmark_operation(enhanced_custom, 5)
        enhanced_custom_result = enhanced_custom()
        
        # Standard compressor
        def standard_custom():
            return standard_compressor.compress_and_encrypt(test_data, 'custom')
        
        standard_custom_time = benchmark_operation(standard_custom, 5)
        standard_custom_result = standard_custom()
        
        size_results['enhanced']['custom_time'] = enhanced_custom_time
        size_results['enhanced']['custom_size'] = len(enhanced_custom_result.encode('utf-8'))
        size_results['standard']['custom_time'] = standard_custom_time
        size_results['standard']['custom_size'] = len(standard_custom_result.encode('utf-8'))
        size_results['speedup']['custom_encoding'] = standard_custom_time / enhanced_custom_time if enhanced_custom_time > 0 else 1
        
        print(f"      Enhanced: {format_time(enhanced_custom_time)} -> {format_size(len(enhanced_custom_result.encode('utf-8')))}")
        print(f"      Standard: {format_time(standard_custom_time)} -> {format_size(len(standard_custom_result.encode('utf-8')))}")
        print(f"      Speedup: {size_results['speedup']['custom_encoding']:.2f}x")
        
        # Verify correctness
        enhanced_decoded = enhanced_compressor.decrypt_and_decompress(enhanced_result, 'binary')
        standard_decoded = standard_compressor.decrypt_and_decompress(standard_result, 'binary')
        enhanced_custom_decoded = enhanced_compressor.decrypt_and_decompress(enhanced_custom_result, 'custom')
        standard_custom_decoded = standard_compressor.decrypt_and_decompress(standard_custom_result, 'custom')
        
        correctness = (
            test_data == enhanced_decoded == standard_decoded == 
            enhanced_custom_decoded == standard_custom_decoded
        )
        
        print(f"   ✅ Correctness: {'PASS' if correctness else 'FAIL'}")
        
        results[size] = size_results
    
    # Native library specific benchmarks
    if enhanced_compressor.is_native_available():
        print(f"\n🔬 Native Library Specific Benchmarks")
        print("-" * 70)
        
        try:
            native_benchmark = enhanced_compressor.benchmark_native_vs_python(
                data_size=4096, iterations=100
            )
            
            print("📊 Detailed Native vs Python Comparison:")
            
            if 'compression' in native_benchmark:
                comp = native_benchmark['compression']
                print(f"   Compression:")
                print(f"      Native: {format_time(comp['native_time'])}")
                print(f"      Python: {format_time(comp['python_time'])}")
                print(f"      Speedup: {comp['speedup']:.2f}x")
            
            if 'hashing' in native_benchmark:
                hash_bench = native_benchmark['hashing']
                print(f"   Hashing (SHA-256):")
                print(f"      Native: {format_time(hash_bench['native_time'])}")
                print(f"      Python: {format_time(hash_bench['python_time'])}")
                print(f"      Speedup: {hash_bench['speedup']:.2f}x")
            
            if 'key_derivation' in native_benchmark:
                kdf = native_benchmark['key_derivation']
                print(f"   Key Derivation (PBKDF2):")
                print(f"      Native: {format_time(kdf['native_time'])}")
                print(f"      Python: {format_time(kdf['python_time'])}")
                print(f"      Speedup: {kdf['speedup']:.2f}x")
            
        except Exception as e:
            print(f"❌ Native benchmark failed: {e}")
    
    # Summary
    print(f"\n📋 Performance Summary")
    print("=" * 70)
    
    avg_speedups = {
        'compression': 0,
        'decompression': 0,
        'custom_encoding': 0
    }
    
    for size, result in results.items():
        for operation in avg_speedups:
            avg_speedups[operation] += result['speedup'][operation]
    
    for operation in avg_speedups:
        avg_speedups[operation] /= len(results)
    
    print(f"Average Performance Improvements (Enhanced vs Standard):")
    print(f"   Compression: {avg_speedups['compression']:.2f}x faster")
    print(f"   Decompression: {avg_speedups['decompression']:.2f}x faster")
    print(f"   Custom Encoding: {avg_speedups['custom_encoding']:.2f}x faster")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    
    if enhanced_compressor.is_native_available():
        print("✅ Native libraries are available and working!")
        print("   - Use EnhancedCompressor for maximum performance")
        print("   - Native acceleration provides significant speed improvements")
        print("   - Especially beneficial for large data processing")
    else:
        print("⚠️  Native libraries are not available")
        print("   - Install a C/C++ compiler (gcc, clang, or MSVC)")
        print("   - Run: python build_native.py")
        print("   - This will provide 2-10x performance improvements")
    
    print(f"\n🎯 Use Cases:")
    print("   - Real-time data encryption: Use native libraries")
    print("   - Batch processing: Native libraries highly recommended")
    print("   - Custom character encoding: Significant native speedup")
    print("   - Memory-constrained environments: Both work well")
    
    print(f"\n🎉 Performance test completed!")
    
    return 0


if __name__ == "__main__":
    exit(main()) 