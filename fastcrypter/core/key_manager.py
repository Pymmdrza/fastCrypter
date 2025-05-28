"""
Key Management System for the Encrypter package.

This module provides secure key generation, derivation, and management
functionality with support for various key derivation functions.
"""

import hashlib
import secrets
import os
from typing import Optional, Dict, Any, Tuple
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from ..exceptions import KeyError, SecurityError, ValidationError, ErrorCodes


class KeyManager:
    """
    Secure key management system.
    
    Provides functionality for key generation, derivation, and validation
    with support for multiple key derivation functions and security levels.
    """
    
    # Security constants
    MIN_PASSWORD_LENGTH = 8
    MIN_SALT_LENGTH = 16
    DEFAULT_ITERATIONS = 100000
    DEFAULT_KEY_LENGTH = 32  # 256 bits
    
    # Supported KDF algorithms
    KDF_ALGORITHMS = {
        'pbkdf2': 'PBKDF2-HMAC-SHA256',
        'scrypt': 'Scrypt',
        'argon2': 'Argon2id',
    }
    
    def __init__(self, 
                 kdf_algorithm: str = 'pbkdf2',
                 iterations: int = DEFAULT_ITERATIONS,
                 memory_cost: int = 65536,  # For Scrypt/Argon2
                 parallelism: int = 1):     # For Argon2
        """
        Initialize the KeyManager.
        
        Args:
            kdf_algorithm (str): Key derivation function to use.
            iterations (int): Number of iterations for KDF.
            memory_cost (int): Memory cost for Scrypt/Argon2.
            parallelism (int): Parallelism factor for Argon2.
            
        Raises:
            ValidationError: If parameters are invalid.
        """
        if kdf_algorithm not in self.KDF_ALGORITHMS:
            raise ValidationError(
                f"Unsupported KDF algorithm: {kdf_algorithm}",
                ErrorCodes.INVALID_CONFIGURATION
            )
        
        self.kdf_algorithm = kdf_algorithm
        self.iterations = max(iterations, 10000)  # Minimum security
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        
        # Initialize Argon2 hasher if needed
        if kdf_algorithm == 'argon2':
            self._argon2_hasher = PasswordHasher(
                time_cost=self.iterations // 1000,  # Convert to reasonable range
                memory_cost=self.memory_cost // 1024,  # Convert to KB
                parallelism=self.parallelism
            )
    
    def generate_salt(self, length: int = MIN_SALT_LENGTH) -> bytes:
        """
        Generate a cryptographically secure random salt.
        
        Args:
            length (int): Length of salt in bytes.
            
        Returns:
            bytes: Random salt.
            
        Raises:
            ValidationError: If length is too small.
        """
        if length < self.MIN_SALT_LENGTH:
            raise ValidationError(
                f"Salt length must be at least {self.MIN_SALT_LENGTH} bytes",
                ErrorCodes.INVALID_INPUT_SIZE
            )
        
        return secrets.token_bytes(length)
    
    def generate_key(self, length: int = DEFAULT_KEY_LENGTH) -> bytes:
        """
        Generate a cryptographically secure random key.
        
        Args:
            length (int): Length of key in bytes.
            
        Returns:
            bytes: Random key.
        """
        return secrets.token_bytes(length)
    
    def derive_key(self, 
                   password: str, 
                   salt: Optional[bytes] = None,
                   key_length: int = DEFAULT_KEY_LENGTH) -> Tuple[bytes, bytes]:
        """
        Derive a key from a password using the configured KDF.
        
        Args:
            password (str): Password to derive key from.
            salt (bytes, optional): Salt for key derivation. Generated if None.
            key_length (int): Desired key length in bytes.
            
        Returns:
            Tuple[bytes, bytes]: (derived_key, salt_used)
            
        Raises:
            ValidationError: If password is too weak.
            KeyError: If key derivation fails.
        """
        # Validate password strength
        if len(password) < self.MIN_PASSWORD_LENGTH:
            raise ValidationError(
                f"Password must be at least {self.MIN_PASSWORD_LENGTH} characters",
                ErrorCodes.KEY_TOO_WEAK
            )
        
        # Generate salt if not provided
        if salt is None:
            salt = self.generate_salt()
        
        try:
            if self.kdf_algorithm == 'pbkdf2':
                key = self._derive_pbkdf2(password, salt, key_length)
            elif self.kdf_algorithm == 'scrypt':
                key = self._derive_scrypt(password, salt, key_length)
            elif self.kdf_algorithm == 'argon2':
                key = self._derive_argon2(password, salt, key_length)
            else:
                raise KeyError(
                    f"Unsupported KDF algorithm: {self.kdf_algorithm}",
                    ErrorCodes.KEY_DERIVATION_FAILED
                )
            
            return key, salt
            
        except Exception as e:
            raise KeyError(
                f"Key derivation failed: {str(e)}",
                ErrorCodes.KEY_DERIVATION_FAILED,
                details={"algorithm": self.kdf_algorithm, "error": str(e)}
            )
    
    def _derive_pbkdf2(self, password: str, salt: bytes, key_length: int) -> bytes:
        """Derive key using PBKDF2-HMAC-SHA256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=self.iterations,
        )
        return kdf.derive(password.encode('utf-8'))
    
    def _derive_scrypt(self, password: str, salt: bytes, key_length: int) -> bytes:
        """Derive key using Scrypt."""
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            n=2**14,  # CPU/memory cost parameter
            r=8,      # Block size parameter
            p=1,      # Parallelization parameter
        )
        return kdf.derive(password.encode('utf-8'))
    
    def _derive_argon2(self, password: str, salt: bytes, key_length: int) -> bytes:
        """Derive key using Argon2id."""
        # Argon2 produces variable length output, we'll use HKDF to get exact length
        hash_result = self._argon2_hasher.hash(password, salt=salt)
        # Extract the hash part and use it as key material
        hash_bytes = hash_result.encode('utf-8')
        
        # Use HKDF to derive the exact key length needed
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            info=b'encrypter-key-derivation',
        )
        return hkdf.derive(hash_bytes)
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        """
        Verify a password against a stored hash (Argon2 only).
        
        Args:
            password (str): Password to verify.
            stored_hash (str): Stored Argon2 hash.
            
        Returns:
            bool: True if password matches.
        """
        if self.kdf_algorithm != 'argon2':
            raise SecurityError(
                "Password verification only supported with Argon2",
                ErrorCodes.UNSUPPORTED_ENCRYPTION
            )
        
        try:
            self._argon2_hasher.verify(stored_hash, password)
            return True
        except VerifyMismatchError:
            return False
    
    def validate_key_strength(self, key: bytes, min_entropy: float = 4.0) -> bool:
        """
        Validate the strength of a key based on entropy.
        
        Args:
            key (bytes): Key to validate.
            min_entropy (float): Minimum entropy per byte.
            
        Returns:
            bool: True if key is strong enough.
        """
        if len(key) < 16:  # Minimum 128 bits
            return False
        
        # Calculate Shannon entropy
        entropy = self._calculate_entropy(key)
        return entropy >= min_entropy
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if not data:
            return 0.0
        
        # Count byte frequencies
        frequencies = {}
        for byte in data:
            frequencies[byte] = frequencies.get(byte, 0) + 1
        
        # Calculate entropy
        entropy = 0.0
        length = len(data)
        for count in frequencies.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy
    
    def secure_compare(self, a: bytes, b: bytes) -> bool:
        """
        Constant-time comparison of two byte strings.
        
        Args:
            a (bytes): First byte string.
            b (bytes): Second byte string.
            
        Returns:
            bool: True if strings are equal.
        """
        if len(a) != len(b):
            return False
        
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        
        return result == 0
    
    def clear_memory(self, data: bytearray) -> None:
        """
        Securely clear sensitive data from memory.
        
        Args:
            data (bytearray): Data to clear.
        """
        if isinstance(data, bytearray):
            # Overwrite with random data multiple times
            for _ in range(3):
                for i in range(len(data)):
                    data[i] = secrets.randbits(8)
            
            # Final overwrite with zeros
            for i in range(len(data)):
                data[i] = 0
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the key manager configuration.
        
        Returns:
            Dict[str, Any]: Configuration information.
        """
        return {
            "kdf_algorithm": self.kdf_algorithm,
            "kdf_name": self.KDF_ALGORITHMS[self.kdf_algorithm],
            "iterations": self.iterations,
            "memory_cost": self.memory_cost,
            "parallelism": self.parallelism,
            "default_key_length": self.DEFAULT_KEY_LENGTH,
            "min_salt_length": self.MIN_SALT_LENGTH,
        } 