"""
Advanced Encryptor - Professional interface for advanced encryption scenarios.

This module provides advanced encryption capabilities with full control
over algorithms, parameters, and security settings.
"""

from typing import Union, Optional, Dict, Any, List
from .core.compressor import Compressor, CompressionAlgorithmType
from .core.encryptor import Encryptor, EncryptionAlgorithmType
from .core.key_manager import KeyManager
from .algorithms import CompressionAlgorithm, EncryptionAlgorithm
from .exceptions import EncrypterError, ValidationError, ErrorCodes


class AdvancedEncryptor:
    """
    Advanced encryption interface for professional use.
    
    This class provides full control over encryption and compression
    algorithms, security parameters, and advanced features like
    streaming encryption and custom algorithm implementations.
    """
    
    def __init__(self,
                 encryption_algorithm: Union[EncryptionAlgorithmType, str, EncryptionAlgorithm] = EncryptionAlgorithmType.AES_256_GCM,
                 compression_algorithm: Union[CompressionAlgorithmType, str, CompressionAlgorithm] = CompressionAlgorithmType.ZLIB,
                 key_derivation_algorithm: str = 'pbkdf2',
                 key_derivation_iterations: int = 100000,
                 memory_cost: int = 65536,
                 parallelism: int = 1,
                 auto_select_algorithms: bool = False):
        """
        Initialize the AdvancedEncryptor.
        
        Args:
            encryption_algorithm: Encryption algorithm to use.
            compression_algorithm: Compression algorithm to use.
            key_derivation_algorithm: Key derivation function algorithm.
            key_derivation_iterations: Number of KDF iterations.
            memory_cost: Memory cost for Scrypt/Argon2.
            parallelism: Parallelism factor for Argon2.
            auto_select_algorithms: Whether to automatically select best algorithms.
        """
        self.auto_select = auto_select_algorithms
        
        # Initialize key manager
        self.key_manager = KeyManager(
            kdf_algorithm=key_derivation_algorithm,
            iterations=key_derivation_iterations,
            memory_cost=memory_cost,
            parallelism=parallelism
        )
        
        # Initialize compressor
        if isinstance(compression_algorithm, CompressionAlgorithm):
            # Custom algorithm implementation
            self.custom_compressor = compression_algorithm
            self.compressor = None
        else:
            self.compressor = Compressor(
                algorithm=compression_algorithm,
                auto_select=auto_select_algorithms
            )
            self.custom_compressor = None
        
        # Initialize encryptor
        if isinstance(encryption_algorithm, EncryptionAlgorithm):
            # Custom algorithm implementation
            self.custom_encryptor = encryption_algorithm
            self.encryptor = None
        else:
            self.encryptor = Encryptor(
                algorithm=encryption_algorithm,
                derive_key=True
            )
            self.custom_encryptor = None
        
        # Store configuration
        self.config = {
            'encryption_algorithm': encryption_algorithm,
            'compression_algorithm': compression_algorithm,
            'key_derivation_algorithm': key_derivation_algorithm,
            'key_derivation_iterations': key_derivation_iterations,
            'memory_cost': memory_cost,
            'parallelism': parallelism,
            'auto_select_algorithms': auto_select_algorithms,
        }
    
    def process(self, data: Union[str, bytes], password: str, 
                operation: str = 'encrypt') -> bytes:
        """
        Process data with compression and encryption.
        
        Args:
            data: Data to process.
            password: Password for encryption.
            operation: Operation to perform ('encrypt' or 'decrypt').
            
        Returns:
            bytes: Processed data.
            
        Raises:
            EncrypterError: If processing fails.
            ValidationError: If parameters are invalid.
        """
        if operation not in ['encrypt', 'decrypt']:
            raise ValidationError(
                "Operation must be 'encrypt' or 'decrypt'",
                ErrorCodes.INVALID_CONFIGURATION
            )
        
        try:
            if operation == 'encrypt':
                return self._encrypt_process(data, password)
            else:
                return self._decrypt_process(data, password)
                
        except Exception as e:
            raise EncrypterError(
                f"Advanced processing failed: {str(e)}",
                details={"operation": operation, "error": str(e)}
            )
    
    def _encrypt_process(self, data: Union[str, bytes], password: str) -> bytes:
        """Internal encryption process."""
        # Convert string to bytes if necessary
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Step 1: Compress data
        if self.custom_compressor:
            compressed_data = self.custom_compressor.compress(data)
        else:
            compressed_data = self.compressor.compress(data)
        
        # Step 2: Encrypt compressed data
        if self.custom_encryptor:
            # For custom encryptors, we need to derive the key first
            key, salt = self.key_manager.derive_key(password)
            encrypted_data = self.custom_encryptor.encrypt(compressed_data, key)
            # Add salt to the beginning for custom encryptors
            return salt + encrypted_data
        else:
            return self.encryptor.encrypt(compressed_data, password)
    
    def _decrypt_process(self, data: bytes, password: str) -> bytes:
        """Internal decryption process."""
        # Step 1: Decrypt data
        if self.custom_encryptor:
            # For custom encryptors, extract salt and derive key
            salt = data[:16]  # Assume 16-byte salt
            encrypted_data = data[16:]
            key, _ = self.key_manager.derive_key(password, salt)
            decrypted_data = self.custom_encryptor.decrypt(encrypted_data, key)
        else:
            decrypted_data = self.encryptor.decrypt(data, password)
        
        # Step 2: Decompress decrypted data
        if self.custom_compressor:
            return self.custom_compressor.decompress(decrypted_data)
        else:
            return self.compressor.decompress(decrypted_data)
    
    def stream_processor(self, password: str, operation: str = 'encrypt'):
        """
        Create a streaming processor for large data.
        
        Args:
            password: Password for encryption.
            operation: Operation to perform ('encrypt' or 'decrypt').
            
        Returns:
            StreamProcessor: Streaming processor instance.
        """
        return StreamProcessor(self, password, operation)
    
    def benchmark_algorithms(self, test_data: bytes, password: str) -> Dict[str, Dict[str, Any]]:
        """
        Benchmark different algorithm combinations.
        
        Args:
            test_data: Data to use for benchmarking.
            password: Password for encryption.
            
        Returns:
            Dict[str, Dict[str, Any]]: Benchmark results.
        """
        import time
        
        results = {}
        
        # Test different compression algorithms
        compression_algos = [
            CompressionAlgorithmType.ZLIB,
            CompressionAlgorithmType.LZMA,
            CompressionAlgorithmType.BROTLI,
        ]
        
        # Test different encryption algorithms
        encryption_algos = [
            EncryptionAlgorithmType.AES_256_GCM,
            EncryptionAlgorithmType.AES_256_CBC,
            EncryptionAlgorithmType.CHACHA20_POLY1305,
        ]
        
        for comp_algo in compression_algos:
            for enc_algo in encryption_algos:
                combo_name = f"{comp_algo.value}+{enc_algo.value}"
                
                try:
                    # Create temporary encryptor
                    temp_encryptor = AdvancedEncryptor(
                        encryption_algorithm=enc_algo,
                        compression_algorithm=comp_algo
                    )
                    
                    # Measure encryption time
                    start_time = time.time()
                    encrypted = temp_encryptor.process(test_data, password, 'encrypt')
                    encrypt_time = time.time() - start_time
                    
                    # Measure decryption time
                    start_time = time.time()
                    decrypted = temp_encryptor.process(encrypted, password, 'decrypt')
                    decrypt_time = time.time() - start_time
                    
                    # Calculate metrics
                    compression_ratio = len(encrypted) / len(test_data)
                    
                    results[combo_name] = {
                        'compression_algorithm': comp_algo.value,
                        'encryption_algorithm': enc_algo.value,
                        'original_size': len(test_data),
                        'compressed_encrypted_size': len(encrypted),
                        'compression_ratio': compression_ratio,
                        'encrypt_time': encrypt_time,
                        'decrypt_time': decrypt_time,
                        'total_time': encrypt_time + decrypt_time,
                        'throughput_mbps': (len(test_data) / (1024 * 1024)) / (encrypt_time + decrypt_time),
                        'success': len(decrypted) == len(test_data),
                    }
                    
                except Exception as e:
                    results[combo_name] = {
                        'error': str(e),
                        'success': False,
                    }
        
        return results
    
    def get_security_analysis(self) -> Dict[str, Any]:
        """
        Get security analysis of current configuration.
        
        Returns:
            Dict[str, Any]: Security analysis results.
        """
        analysis = {
            'encryption_strength': 'Unknown',
            'compression_efficiency': 'Unknown',
            'key_derivation_strength': 'Unknown',
            'overall_security_level': 'Unknown',
            'recommendations': [],
        }
        
        # Analyze encryption algorithm
        if self.encryptor:
            algo = self.encryptor.algorithm
            if algo in [EncryptionAlgorithmType.AES_256_GCM, EncryptionAlgorithmType.CHACHA20_POLY1305]:
                analysis['encryption_strength'] = 'Military Grade'
            elif algo == EncryptionAlgorithmType.AES_256_CBC:
                analysis['encryption_strength'] = 'High'
            elif algo == EncryptionAlgorithmType.RSA_4096:
                analysis['encryption_strength'] = 'Very High'
        
        # Analyze key derivation
        kdf_algo = self.key_manager.kdf_algorithm
        iterations = self.key_manager.iterations
        
        if kdf_algo == 'argon2':
            analysis['key_derivation_strength'] = 'Excellent'
        elif kdf_algo == 'scrypt':
            analysis['key_derivation_strength'] = 'Very Good'
        elif kdf_algo == 'pbkdf2' and iterations >= 100000:
            analysis['key_derivation_strength'] = 'Good'
        else:
            analysis['key_derivation_strength'] = 'Weak'
            analysis['recommendations'].append('Increase KDF iterations or use Argon2')
        
        # Overall security assessment
        strengths = [analysis['encryption_strength'], analysis['key_derivation_strength']]
        if all(s in ['Military Grade', 'Excellent', 'Very High'] for s in strengths):
            analysis['overall_security_level'] = 'Maximum'
        elif all(s in ['High', 'Very Good', 'Good'] for s in strengths):
            analysis['overall_security_level'] = 'High'
        else:
            analysis['overall_security_level'] = 'Medium'
            analysis['recommendations'].append('Consider upgrading algorithms for better security')
        
        return analysis
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the AdvancedEncryptor.
        
        Returns:
            Dict[str, Any]: Configuration and analysis information.
        """
        info = {
            'version': '1.0.0',
            'configuration': self.config,
            'security_analysis': self.get_security_analysis(),
        }
        
        if self.compressor:
            info['compressor_info'] = self.compressor.get_info()
        
        if self.encryptor:
            info['encryptor_info'] = self.encryptor.get_info()
        
        info['key_manager_info'] = self.key_manager.get_info()
        
        return info


class StreamProcessor:
    """
    Streaming processor for large data encryption/decryption.
    
    This class allows processing of large data streams without
    loading everything into memory at once.
    """
    
    def __init__(self, advanced_encryptor: AdvancedEncryptor, 
                 password: str, operation: str):
        """
        Initialize the StreamProcessor.
        
        Args:
            advanced_encryptor: Parent AdvancedEncryptor instance.
            password: Password for encryption.
            operation: Operation to perform ('encrypt' or 'decrypt').
        """
        self.encryptor = advanced_encryptor
        self.password = password
        self.operation = operation
        self.chunk_size = 64 * 1024  # 64KB chunks
    
    def process(self, chunk: bytes) -> bytes:
        """
        Process a data chunk.
        
        Args:
            chunk: Data chunk to process.
            
        Returns:
            bytes: Processed chunk.
        """
        return self.encryptor.process(chunk, self.password, self.operation)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        pass 