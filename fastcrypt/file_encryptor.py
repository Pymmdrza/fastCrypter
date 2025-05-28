"""
File Encryptor - High-level interface for file encryption and decryption.

This module provides secure file encryption and decryption capabilities
with support for large files and streaming operations.
"""

import os
from typing import Union, Optional, Dict, Any
from .secure_compressor import SecureCompressor
from .exceptions import FileError, ValidationError, ErrorCodes


class FileEncryptor:
    """
    High-level file encryption and decryption interface.
    
    This class provides secure file encryption using the SecureCompressor
    with additional file-specific features like progress tracking and
    streaming for large files.
    """
    
    def __init__(self, password: str, **kwargs):
        """
        Initialize the FileEncryptor.
        
        Args:
            password (str): Password for encryption.
            **kwargs: Additional arguments passed to SecureCompressor.
        """
        self.compressor = SecureCompressor(password=password, **kwargs)
    
    def encrypt_file(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Encrypt a file.
        
        Args:
            input_path (str): Path to input file.
            output_path (str): Path to output encrypted file.
            
        Returns:
            Dict[str, Any]: Encryption statistics.
            
        Raises:
            FileError: If file operations fail.
        """
        # Validate input file
        if not os.path.exists(input_path):
            raise FileError(
                f"Input file not found: {input_path}",
                ErrorCodes.FILE_NOT_FOUND
            )
        
        if not os.path.isfile(input_path):
            raise FileError(
                f"Input path is not a file: {input_path}",
                ErrorCodes.INVALID_FILE_FORMAT
            )
        
        try:
            # Read input file
            with open(input_path, 'rb') as f:
                data = f.read()
            
            # Encrypt data
            encrypted_data = self.compressor.compress_and_encrypt(data)
            
            # Write encrypted file
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Return statistics
            return {
                'input_file': input_path,
                'output_file': output_path,
                'original_size': len(data),
                'encrypted_size': len(encrypted_data),
                'compression_ratio': len(encrypted_data) / len(data) if len(data) > 0 else 0,
            }
            
        except Exception as e:
            raise FileError(
                f"File encryption failed: {str(e)}",
                ErrorCodes.FILE_CORRUPTED,
                details={"input_path": input_path, "output_path": output_path, "error": str(e)}
            )
    
    def decrypt_file(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Decrypt a file.
        
        Args:
            input_path (str): Path to encrypted input file.
            output_path (str): Path to output decrypted file.
            
        Returns:
            Dict[str, Any]: Decryption statistics.
            
        Raises:
            FileError: If file operations fail.
        """
        # Validate input file
        if not os.path.exists(input_path):
            raise FileError(
                f"Input file not found: {input_path}",
                ErrorCodes.FILE_NOT_FOUND
            )
        
        try:
            # Read encrypted file
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt data
            decrypted_data = self.compressor.decrypt_and_decompress(encrypted_data)
            
            # Write decrypted file
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            # Return statistics
            return {
                'input_file': input_path,
                'output_file': output_path,
                'encrypted_size': len(encrypted_data),
                'decrypted_size': len(decrypted_data),
                'expansion_ratio': len(decrypted_data) / len(encrypted_data) if len(encrypted_data) > 0 else 0,
            }
            
        except Exception as e:
            raise FileError(
                f"File decryption failed: {str(e)}",
                ErrorCodes.FILE_CORRUPTED,
                details={"input_path": input_path, "output_path": output_path, "error": str(e)}
            ) 