#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <math.h>

// Platform-specific includes
#ifdef _WIN32
    #include <windows.h>
    #include <wincrypt.h>
#else
    #include <unistd.h>
    #include <fcntl.h>
#endif

// Export macros for different platforms
#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT __attribute__((visibility("default")))
#endif

// Fast XOR operation optimized for large data
EXPORT void fast_xor_inplace(uint8_t* data, size_t data_len, const uint8_t* key, size_t key_len) {
    if (!data || !key || data_len == 0 || key_len == 0) return;
    
    // Process 8 bytes at a time for better performance
    size_t i = 0;
    const size_t block_size = 8;
    
    // Process full 8-byte blocks
    for (; i + block_size <= data_len; i += block_size) {
        uint64_t* data_block = (uint64_t*)(data + i);
        uint64_t key_block = 0;
        
        // Build 8-byte key block
        for (size_t j = 0; j < block_size; j++) {
            key_block |= ((uint64_t)key[(i + j) % key_len]) << (j * 8);
        }
        
        *data_block ^= key_block;
    }
    
    // Process remaining bytes
    for (; i < data_len; i++) {
        data[i] ^= key[i % key_len];
    }
}

// Fast memory clearing with multiple passes
EXPORT void secure_memclear(void* ptr, size_t len) {
    if (!ptr || len == 0) return;
    
    volatile uint8_t* vptr = (volatile uint8_t*)ptr;
    
    // Multiple overwrite passes for security
    for (int pass = 0; pass < 3; pass++) {
        for (size_t i = 0; i < len; i++) {
            vptr[i] = (uint8_t)(rand() & 0xFF);
        }
    }
    
    // Final zero pass
    for (size_t i = 0; i < len; i++) {
        vptr[i] = 0;
    }
    
    // Memory barrier to prevent optimization
    __asm__ __volatile__("" ::: "memory");
}

// Fast entropy calculation
EXPORT double calculate_entropy(const uint8_t* data, size_t len) {
    if (!data || len == 0) return 0.0;
    
    uint32_t freq[256] = {0};
    
    // Count byte frequencies
    for (size_t i = 0; i < len; i++) {
        freq[data[i]]++;
    }
    
    // Calculate Shannon entropy
    double entropy = 0.0;
    for (int i = 0; i < 256; i++) {
        if (freq[i] > 0) {
            double p = (double)freq[i] / len;
            entropy -= p * log2(p);
        }
    }
    
    return entropy;
}

// Secure random number generation
EXPORT int secure_random_bytes(uint8_t* buffer, size_t len) {
    if (!buffer || len == 0) return -1;
    
#ifdef _WIN32
    HCRYPTPROV hProv;
    if (!CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_FULL, CRYPT_VERIFYCONTEXT)) {
        return -1;
    }
    
    BOOL result = CryptGenRandom(hProv, (DWORD)len, buffer);
    CryptReleaseContext(hProv, 0);
    
    return result ? 0 : -1;
#else
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd < 0) return -1;
    
    ssize_t bytes_read = read(fd, buffer, len);
    close(fd);
    
    return (bytes_read == (ssize_t)len) ? 0 : -1;
#endif
}

// Fast PBKDF2-like key derivation
EXPORT void fast_key_derive(const uint8_t* password, size_t pwd_len,
                           const uint8_t* salt, size_t salt_len,
                           uint32_t iterations, uint8_t* output, size_t out_len) {
    if (!password || !salt || !output || pwd_len == 0 || salt_len == 0 || out_len == 0) return;
    
    // Simple but fast key derivation (not cryptographically secure - use for demo)
    uint8_t* temp = malloc(pwd_len + salt_len);
    if (!temp) return;
    
    memcpy(temp, password, pwd_len);
    memcpy(temp + pwd_len, salt, salt_len);
    
    // Multiple rounds of hashing
    for (uint32_t i = 0; i < iterations; i++) {
        // Simple hash function (replace with proper crypto hash in production)
        uint32_t hash = 0x811c9dc5; // FNV-1a initial value
        
        for (size_t j = 0; j < pwd_len + salt_len; j++) {
            hash ^= temp[j];
            hash *= 0x01000193; // FNV-1a prime
        }
        
        // Update temp with hash result
        for (size_t j = 0; j < pwd_len + salt_len && j < 4; j++) {
            temp[j] ^= (hash >> (j * 8)) & 0xFF;
        }
    }
    
    // Generate output
    for (size_t i = 0; i < out_len; i++) {
        output[i] = temp[i % (pwd_len + salt_len)];
    }
    
    secure_memclear(temp, pwd_len + salt_len);
    free(temp);
}

// Fast base conversion for custom encoding
EXPORT size_t base_convert_encode(const uint8_t* input, size_t input_len,
                                 uint8_t* output, size_t output_max,
                                 const char* charset, size_t base) {
    if (!input || !output || !charset || input_len == 0 || base < 2) return 0;
    
    // Convert input bytes to big integer (simplified)
    uint64_t number = 0;
    for (size_t i = 0; i < input_len && i < 8; i++) {
        number = (number << 8) | input[i];
    }
    
    if (number == 0) {
        if (output_max > 0) {
            output[0] = charset[0];
            return 1;
        }
        return 0;
    }
    
    // Convert to target base
    size_t pos = 0;
    uint8_t temp[64];
    
    while (number > 0 && pos < sizeof(temp)) {
        temp[pos++] = charset[number % base];
        number /= base;
    }
    
    // Reverse and copy to output
    size_t result_len = pos;
    if (result_len > output_max) result_len = output_max;
    
    for (size_t i = 0; i < result_len; i++) {
        output[i] = temp[pos - 1 - i];
    }
    
    return result_len;
}

// Fast compression using simple RLE
EXPORT size_t fast_compress_rle(const uint8_t* input, size_t input_len,
                               uint8_t* output, size_t output_max) {
    if (!input || !output || input_len == 0) return 0;
    
    size_t out_pos = 0;
    size_t i = 0;
    
    while (i < input_len && out_pos < output_max - 1) {
        uint8_t current = input[i];
        uint8_t count = 1;
        
        // Count consecutive identical bytes
        while (i + count < input_len && input[i + count] == current && count < 255) {
            count++;
        }
        
        if (count >= 3 || current == 0xFF) {
            // Use RLE encoding
            if (out_pos + 2 < output_max) {
                output[out_pos++] = 0xFF; // RLE marker
                output[out_pos++] = count;
                output[out_pos++] = current;
            }
        } else {
            // Copy literal bytes
            for (uint8_t j = 0; j < count && out_pos < output_max; j++) {
                output[out_pos++] = current;
            }
        }
        
        i += count;
    }
    
    return out_pos;
}

// Fast decompression for RLE
EXPORT size_t fast_decompress_rle(const uint8_t* input, size_t input_len,
                                 uint8_t* output, size_t output_max) {
    if (!input || !output || input_len == 0) return 0;
    
    size_t out_pos = 0;
    size_t i = 0;
    
    while (i < input_len && out_pos < output_max) {
        if (input[i] == 0xFF && i + 2 < input_len) {
            // RLE encoded sequence
            uint8_t count = input[i + 1];
            uint8_t value = input[i + 2];
            
            for (uint8_t j = 0; j < count && out_pos < output_max; j++) {
                output[out_pos++] = value;
            }
            
            i += 3;
        } else {
            // Literal byte
            output[out_pos++] = input[i++];
        }
    }
    
    return out_pos;
}

// Performance benchmark function
EXPORT double benchmark_operation(void (*operation)(void), uint32_t iterations) {
    if (!operation || iterations == 0) return 0.0;
    
    clock_t start = clock();
    
    for (uint32_t i = 0; i < iterations; i++) {
        operation();
    }
    
    clock_t end = clock();
    
    return ((double)(end - start)) / CLOCKS_PER_SEC;
}

// Library initialization
EXPORT int crypto_core_init(void) {
    // Initialize random seed
    srand((unsigned int)time(NULL));
    return 0;
}

// Library cleanup
EXPORT void crypto_core_cleanup(void) {
    // Cleanup operations if needed
} 