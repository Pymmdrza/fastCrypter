"""
Advanced Encryption System for the Encrypter package.

This module provides military-grade encryption functionality with support
for multiple encryption algorithms and authenticated encryption modes.
"""

import secrets
import hashlib
import hmac
from typing import Union, Dict, Any, Optional, Tuple, List
from enum import Enum
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

from ..exceptions import EncryptionError, ValidationError, SecurityError, ErrorCodes
from ..algorithms import EncryptionAlgorithm


class EncryptionAlgorithmType(Enum):
    """Supported encryption algorithms."""
    AES_256_GCM = "aes-256-gcm"
    AES_256_CBC = "aes-256-cbc"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    RSA_4096 = "rsa-4096"


class Encryptor:
    """
    Military-grade encryption system.
    
    Provides authenticated encryption with support for multiple algorithms,
    key derivation, and integrity verification.
    """
    
    # Algorithm-specific settings
    ALGORITHM_SETTINGS = {
        EncryptionAlgorithmType.AES_256_GCM: {
            'key_size': 32,  # 256 bits
            'iv_size': 12,   # 96 bits for GCM
            'tag_size': 16,  # 128 bits
            'authenticated': True,
        },
        EncryptionAlgorithmType.AES_256_CBC: {
            'key_size': 32,  # 256 bits
            'iv_size': 16,   # 128 bits
            'tag_size': 32,  # HMAC-SHA256
            'authenticated': False,  # We add HMAC manually
        },
        EncryptionAlgorithmType.CHACHA20_POLY1305: {
            'key_size': 32,  # 256 bits
            'iv_size': 12,   # 96 bits
            'tag_size': 16,  # 128 bits
            'authenticated': True,
        },
        EncryptionAlgorithmType.RSA_4096: {
            'key_size': 512,  # 4096 bits
            'iv_size': 0,     # Not applicable
            'tag_size': 0,    # Not applicable
            'authenticated': True,  # Built-in with OAEP
        },
    }
    
    def __init__(self, 
                 algorithm: Union[EncryptionAlgorithmType, str] = EncryptionAlgorithmType.AES_256_GCM,
                 derive_key: bool = True):
        """
        Initialize the Encryptor.
        
        Args:
            algorithm: Encryption algorithm to use.
            derive_key: Whether to use key derivation for symmetric keys.
            
        Raises:
            ValidationError: If parameters are invalid.
        """
        # Handle string algorithm input
        if isinstance(algorithm, str):
            try:
                algorithm = EncryptionAlgorithmType(algorithm.lower())
            except ValueError:
                raise ValidationError(
                    f"Unsupported encryption algorithm: {algorithm}",
                    ErrorCodes.UNSUPPORTED_ENCRYPTION
                )
        
        self.algorithm = algorithm
        self.derive_key = derive_key
        self.settings = self.ALGORITHM_SETTINGS[algorithm]
        
        # Initialize RSA key pair if using RSA
        if algorithm == EncryptionAlgorithmType.RSA_4096:
            self._rsa_private_key = None
            self._rsa_public_key = None
    
    def generate_rsa_keypair(self) -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair for asymmetric encryption.
        
        Returns:
            Tuple[bytes, bytes]: (private_key_pem, public_key_pem)
            
        Raises:
            EncryptionError: If key generation fails.
        """
        if self.algorithm != EncryptionAlgorithmType.RSA_4096:
            raise EncryptionError(
                "RSA key generation only available for RSA algorithm",
                ErrorCodes.INVALID_CONFIGURATION
            )
        
        try:
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096,
                backend=default_backend()
            )
            
            # Get public key
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Store keys
            self._rsa_private_key = private_key
            self._rsa_public_key = public_key
            
            return private_pem, public_pem
            
        except Exception as e:
            raise EncryptionError(
                f"RSA key generation failed: {str(e)}",
                ErrorCodes.KEY_GENERATION_FAILED,
                details={"error": str(e)}
            )
    
    def load_rsa_keys(self, private_key_pem: Optional[bytes] = None, 
                      public_key_pem: Optional[bytes] = None):
        """
        Load RSA keys from PEM format.
        
        Args:
            private_key_pem: Private key in PEM format.
            public_key_pem: Public key in PEM format.
            
        Raises:
            EncryptionError: If key loading fails.
        """
        if self.algorithm != EncryptionAlgorithmType.RSA_4096:
            raise EncryptionError(
                "RSA key loading only available for RSA algorithm",
                ErrorCodes.INVALID_CONFIGURATION
            )
        
        try:
            if private_key_pem:
                self._rsa_private_key = serialization.load_pem_private_key(
                    private_key_pem,
                    password=None,
                    backend=default_backend()
                )
            
            if public_key_pem:
                self._rsa_public_key = serialization.load_pem_public_key(
                    public_key_pem,
                    backend=default_backend()
                )
                
        except Exception as e:
            raise EncryptionError(
                f"RSA key loading failed: {str(e)}",
                ErrorCodes.INVALID_KEY_FORMAT,
                details={"error": str(e)}
            )
    
    def encrypt(self, data: Union[str, bytes], key: Union[str, bytes]) -> bytes:
        """
        Encrypt data using the configured algorithm.
        
        Args:
            data: Data to encrypt (string or bytes).
            key: Encryption key (password or key bytes).
            
        Returns:
            bytes: Encrypted data with metadata header.
            
        Raises:
            EncryptionError: If encryption fails.
            ValidationError: If input data is invalid.
        """
        # Convert string to bytes if necessary
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if not isinstance(data, bytes):
            raise ValidationError(
                "Input data must be string or bytes",
                ErrorCodes.INVALID_INPUT_FORMAT
            )
        
        if len(data) == 0:
            raise ValidationError(
                "Cannot encrypt empty data",
                ErrorCodes.INVALID_INPUT_SIZE
            )
        
        try:
            if self.algorithm == EncryptionAlgorithmType.AES_256_GCM:
                return self._encrypt_aes_gcm(data, key)
            elif self.algorithm == EncryptionAlgorithmType.AES_256_CBC:
                return self._encrypt_aes_cbc(data, key)
            elif self.algorithm == EncryptionAlgorithmType.CHACHA20_POLY1305:
                return self._encrypt_chacha20(data, key)
            elif self.algorithm == EncryptionAlgorithmType.RSA_4096:
                return self._encrypt_rsa(data)
            else:
                raise EncryptionError(
                    f"Unsupported algorithm: {self.algorithm}",
                    ErrorCodes.UNSUPPORTED_ENCRYPTION
                )
                
        except EncryptionError:
            raise
        except Exception as e:
            raise EncryptionError(
                f"Encryption failed: {str(e)}",
                ErrorCodes.ENCRYPTION_FAILED,
                details={"algorithm": self.algorithm.value, "error": str(e)}
            )
    
    def decrypt(self, data: bytes, key: Union[str, bytes]) -> bytes:
        """
        Decrypt data.
        
        Args:
            data: Encrypted data with metadata header.
            key: Decryption key (password or key bytes).
            
        Returns:
            bytes: Decrypted data.
            
        Raises:
            EncryptionError: If decryption fails.
            ValidationError: If input data is invalid.
        """
        if not isinstance(data, bytes):
            raise ValidationError(
                "Input data must be bytes",
                ErrorCodes.INVALID_INPUT_FORMAT
            )
        
        if len(data) < 16:  # Minimum header size
            raise ValidationError(
                "Data too small to contain valid header",
                ErrorCodes.INVALID_INPUT_SIZE
            )
        
        try:
            # Parse header to determine algorithm
            algorithm = self._parse_algorithm_from_header(data)
            
            if algorithm == EncryptionAlgorithmType.AES_256_GCM:
                return self._decrypt_aes_gcm(data, key)
            elif algorithm == EncryptionAlgorithmType.AES_256_CBC:
                return self._decrypt_aes_cbc(data, key)
            elif algorithm == EncryptionAlgorithmType.CHACHA20_POLY1305:
                return self._decrypt_chacha20(data, key)
            elif algorithm == EncryptionAlgorithmType.RSA_4096:
                return self._decrypt_rsa(data)
            else:
                raise EncryptionError(
                    f"Unsupported algorithm in header: {algorithm}",
                    ErrorCodes.UNSUPPORTED_ENCRYPTION
                )
                
        except EncryptionError:
            raise
        except Exception as e:
            raise EncryptionError(
                f"Decryption failed: {str(e)}",
                ErrorCodes.DECRYPTION_FAILED,
                details={"error": str(e)}
            )
    
    def _encrypt_aes_gcm(self, data: bytes, key: Union[str, bytes]) -> bytes:
        """Encrypt data using AES-256-GCM."""
        # Derive or prepare key
        if isinstance(key, str):
            salt = secrets.token_bytes(16)
            derived_key = self._derive_key(key.encode('utf-8'), salt, 32)
        else:
            salt = b''
            derived_key = key[:32]  # Ensure 256-bit key
        
        # Generate IV
        iv = secrets.token_bytes(12)  # 96 bits for GCM
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(derived_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(data) + encryptor.finalize()
        tag = encryptor.tag
        
        # Create header and combine
        header = self._create_header(self.algorithm, len(salt), len(iv), len(tag))
        return header + salt + iv + tag + ciphertext
    
    def _decrypt_aes_gcm(self, data: bytes, key: Union[str, bytes]) -> bytes:
        """Decrypt AES-256-GCM data."""
        # Parse header
        header_size, salt_size, iv_size, tag_size = self._parse_header(data)
        
        # Extract components
        offset = header_size
        salt = data[offset:offset + salt_size] if salt_size > 0 else b''
        offset += salt_size
        iv = data[offset:offset + iv_size]
        offset += iv_size
        tag = data[offset:offset + tag_size]
        offset += tag_size
        ciphertext = data[offset:]
        
        # Derive or prepare key
        if isinstance(key, str) and salt:
            derived_key = self._derive_key(key.encode('utf-8'), salt, 32)
        else:
            derived_key = key[:32] if isinstance(key, bytes) else key.encode('utf-8')[:32]
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(derived_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt data
        return decryptor.update(ciphertext) + decryptor.finalize()
    
    def _encrypt_aes_cbc(self, data: bytes, key: Union[str, bytes]) -> bytes:
        """Encrypt data using AES-256-CBC with HMAC."""
        # Derive or prepare key
        if isinstance(key, str):
            salt = secrets.token_bytes(16)
            derived_key = self._derive_key(key.encode('utf-8'), salt, 64)  # 32 for AES + 32 for HMAC
        else:
            salt = b''
            derived_key = key[:64]  # Ensure we have enough key material
        
        aes_key = derived_key[:32]
        hmac_key = derived_key[32:64]
        
        # Pad data to AES block size
        padded_data = self._pad_pkcs7(data, 16)
        
        # Generate IV
        iv = secrets.token_bytes(16)  # 128 bits for CBC
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Encrypt data
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Calculate HMAC
        hmac_obj = hmac.new(hmac_key, iv + ciphertext, hashlib.sha256)
        tag = hmac_obj.digest()
        
        # Create header and combine
        header = self._create_header(self.algorithm, len(salt), len(iv), len(tag))
        return header + salt + iv + tag + ciphertext
    
    def _decrypt_aes_cbc(self, data: bytes, key: Union[str, bytes]) -> bytes:
        """Decrypt AES-256-CBC data with HMAC verification."""
        # Parse header
        header_size, salt_size, iv_size, tag_size = self._parse_header(data)
        
        # Extract components
        offset = header_size
        salt = data[offset:offset + salt_size] if salt_size > 0 else b''
        offset += salt_size
        iv = data[offset:offset + iv_size]
        offset += iv_size
        tag = data[offset:offset + tag_size]
        offset += tag_size
        ciphertext = data[offset:]
        
        # Derive or prepare key
        if isinstance(key, str) and salt:
            derived_key = self._derive_key(key.encode('utf-8'), salt, 64)
        else:
            key_bytes = key if isinstance(key, bytes) else key.encode('utf-8')
            derived_key = key_bytes[:64]
        
        aes_key = derived_key[:32]
        hmac_key = derived_key[32:64]
        
        # Verify HMAC
        expected_hmac = hmac.new(hmac_key, iv + ciphertext, hashlib.sha256).digest()
        if not hmac.compare_digest(tag, expected_hmac):
            raise SecurityError(
                "HMAC verification failed - data may be tampered",
                ErrorCodes.TAMPERING_DETECTED
            )
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        # Decrypt and unpad data
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        return self._unpad_pkcs7(padded_data)
    
    def _encrypt_chacha20(self, data: bytes, key: Union[str, bytes]) -> bytes:
        """Encrypt data using ChaCha20-Poly1305."""
        # Derive or prepare key
        if isinstance(key, str):
            salt = secrets.token_bytes(16)
            derived_key = self._derive_key(key.encode('utf-8'), salt, 32)
        else:
            salt = b''
            derived_key = key[:32]
        
        # Generate nonce
        nonce = secrets.token_bytes(12)  # 96 bits
        
        # Create cipher using ChaCha20Poly1305 from cryptography
        cipher = ChaCha20Poly1305(derived_key)
        
        # Encrypt data (this includes authentication tag)
        ciphertext_with_tag = cipher.encrypt(nonce, data, None)
        
        # Create header and combine
        header = self._create_header(self.algorithm, len(salt), len(nonce), 16)  # 16-byte tag
        return header + salt + nonce + ciphertext_with_tag
    
    def _decrypt_chacha20(self, data: bytes, key: Union[str, bytes]) -> bytes:
        """Decrypt ChaCha20-Poly1305 data."""
        # Parse header
        header_size, salt_size, nonce_size, tag_size = self._parse_header(data)
        
        # Extract components
        offset = header_size
        salt = data[offset:offset + salt_size] if salt_size > 0 else b''
        offset += salt_size
        nonce = data[offset:offset + nonce_size]
        offset += nonce_size
        ciphertext_with_tag = data[offset:]  # This includes the tag
        
        # Derive or prepare key
        if isinstance(key, str) and salt:
            derived_key = self._derive_key(key.encode('utf-8'), salt, 32)
        else:
            derived_key = key[:32] if isinstance(key, bytes) else key.encode('utf-8')[:32]
        
        # Create cipher using ChaCha20Poly1305 from cryptography
        cipher = ChaCha20Poly1305(derived_key)
        
        # Decrypt data (this verifies authentication tag)
        return cipher.decrypt(nonce, ciphertext_with_tag, None)
    
    def _encrypt_rsa(self, data: bytes) -> bytes:
        """Encrypt data using RSA-4096."""
        if not self._rsa_public_key:
            raise EncryptionError(
                "RSA public key not loaded",
                ErrorCodes.INVALID_KEY_FORMAT
            )
        
        # RSA can only encrypt small amounts of data
        max_chunk_size = 446  # 4096/8 - 2*32 - 2 (OAEP padding)
        
        if len(data) <= max_chunk_size:
            # Single chunk encryption
            ciphertext = self._rsa_public_key.encrypt(
                data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Create header
            header = self._create_header(self.algorithm, 0, 0, 0)
            return header + ciphertext
        else:
            # Multi-chunk encryption (hybrid approach)
            # Generate symmetric key for data encryption
            symmetric_key = secrets.token_bytes(32)
            
            # Encrypt data with AES-GCM
            temp_encryptor = Encryptor(EncryptionAlgorithmType.AES_256_GCM, derive_key=False)
            encrypted_data = temp_encryptor._encrypt_aes_gcm(data, symmetric_key)
            
            # Encrypt symmetric key with RSA
            encrypted_key = self._rsa_public_key.encrypt(
                symmetric_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Create header for hybrid encryption
            header = self._create_header(self.algorithm, len(encrypted_key), 0, 0)
            return header + encrypted_key + encrypted_data
    
    def _decrypt_rsa(self, data: bytes) -> bytes:
        """Decrypt RSA-4096 data."""
        if not self._rsa_private_key:
            raise EncryptionError(
                "RSA private key not loaded",
                ErrorCodes.INVALID_KEY_FORMAT
            )
        
        # Parse header
        header_size, key_size, _, _ = self._parse_header(data)
        
        if key_size == 0:
            # Single chunk decryption
            ciphertext = data[header_size:]
            return self._rsa_private_key.decrypt(
                ciphertext,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
        else:
            # Multi-chunk decryption (hybrid approach)
            offset = header_size
            encrypted_key = data[offset:offset + key_size]
            offset += key_size
            encrypted_data = data[offset:]
            
            # Decrypt symmetric key
            symmetric_key = self._rsa_private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Decrypt data with AES-GCM
            temp_encryptor = Encryptor(EncryptionAlgorithmType.AES_256_GCM, derive_key=False)
            return temp_encryptor._decrypt_aes_gcm(encrypted_data, symmetric_key)
    
    def _derive_key(self, password: bytes, salt: bytes, length: int) -> bytes:
        """Derive key using HKDF."""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            info=b'encrypter-encryption-key',
            backend=default_backend()
        )
        return hkdf.derive(password)
    
    def _pad_pkcs7(self, data: bytes, block_size: int) -> bytes:
        """Apply PKCS7 padding."""
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding
    
    def _unpad_pkcs7(self, data: bytes) -> bytes:
        """Remove PKCS7 padding."""
        padding_length = data[-1]
        return data[:-padding_length]
    
    def _create_header(self, algorithm: EncryptionAlgorithmType, 
                      salt_size: int, iv_size: int, tag_size: int) -> bytes:
        """
        Create metadata header for encrypted data.
        
        Header format (16 bytes):
        - 4 bytes: Magic number (0x454E4352 = "ENCR")
        - 1 byte: Algorithm ID
        - 1 byte: Salt size
        - 1 byte: IV/Nonce size
        - 1 byte: Tag size
        - 8 bytes: Reserved
        """
        algo_map = {
            EncryptionAlgorithmType.AES_256_GCM: 1,
            EncryptionAlgorithmType.AES_256_CBC: 2,
            EncryptionAlgorithmType.CHACHA20_POLY1305: 3,
            EncryptionAlgorithmType.RSA_4096: 4,
        }
        
        header = bytearray(16)
        header[0:4] = b'ENCR'  # Magic number
        header[4] = algo_map[algorithm]
        header[5] = min(salt_size, 255)
        header[6] = min(iv_size, 255)
        header[7] = min(tag_size, 255)
        header[8:16] = b'\x00' * 8  # Reserved
        
        return bytes(header)
    
    def _parse_header(self, data: bytes) -> Tuple[int, int, int, int]:
        """
        Parse metadata header from encrypted data.
        
        Returns:
            Tuple[int, int, int, int]: (header_size, salt_size, iv_size, tag_size)
        """
        if len(data) < 16:
            raise EncryptionError(
                "Invalid header: too small",
                ErrorCodes.INVALID_CIPHERTEXT
            )
        
        header = data[:16]
        
        # Check magic number
        if header[0:4] != b'ENCR':
            raise EncryptionError(
                "Invalid header: magic number mismatch",
                ErrorCodes.INVALID_CIPHERTEXT
            )
        
        salt_size = header[5]
        iv_size = header[6]
        tag_size = header[7]
        
        return 16, salt_size, iv_size, tag_size
    
    def _parse_algorithm_from_header(self, data: bytes) -> EncryptionAlgorithmType:
        """Parse algorithm from header."""
        if len(data) < 16:
            raise EncryptionError(
                "Invalid header: too small",
                ErrorCodes.INVALID_CIPHERTEXT
            )
        
        algo_id = data[4]
        algo_map = {
            1: EncryptionAlgorithmType.AES_256_GCM,
            2: EncryptionAlgorithmType.AES_256_CBC,
            3: EncryptionAlgorithmType.CHACHA20_POLY1305,
            4: EncryptionAlgorithmType.RSA_4096,
        }
        
        algorithm = algo_map.get(algo_id)
        if algorithm is None:
            raise EncryptionError(
                f"Unknown algorithm ID in header: {algo_id}",
                ErrorCodes.INVALID_CIPHERTEXT
            )
        
        return algorithm
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the encryptor configuration.
        
        Returns:
            Dict[str, Any]: Configuration information.
        """
        return {
            "algorithm": self.algorithm.value,
            "derive_key": self.derive_key,
            "key_size": self.settings['key_size'],
            "iv_size": self.settings['iv_size'],
            "tag_size": self.settings['tag_size'],
            "authenticated": self.settings['authenticated'],
            "supported_algorithms": [algo.value for algo in EncryptionAlgorithmType],
        } 