"""
Custom Encoder for Encrypter package.

This module provides custom encoding functionality that converts binary data
to text using only specified characters for steganography and obfuscation.
"""

import secrets
from typing import Union, Optional, Tuple
from ..exceptions import ValidationError, ErrorCodes


class CustomEncoder:
    """
    Custom encoder that converts binary data to text using only specified characters.
    
    This encoder is useful for creating encrypted output that looks like normal text
    or follows specific character constraints.
    """
    
    # Default character set (can be customized)
    DEFAULT_CHARSET = "abcdef98Xvbvii"
    
    def __init__(self, charset: str = DEFAULT_CHARSET, padding_char: Optional[str] = None):
        """
        Initialize the CustomEncoder.
        
        Args:
            charset (str): Characters to use for encoding.
            padding_char (str, optional): Character for padding. Uses last char if None.
            
        Raises:
            ValidationError: If charset is invalid.
        """
        if not charset or len(charset) < 2:
            raise ValidationError(
                "Charset must contain at least 2 characters",
                ErrorCodes.INVALID_CONFIGURATION
            )
        
        # Remove duplicates while preserving order
        seen = set()
        self.charset = ''.join(char for char in charset if not (char in seen or seen.add(char)))
        
        if len(self.charset) < 2:
            raise ValidationError(
                "Charset must contain at least 2 unique characters",
                ErrorCodes.INVALID_CONFIGURATION
            )
        
        self.base = len(self.charset)
        self.padding_char = padding_char or self.charset[-1]
        
        # Create lookup tables for fast encoding/decoding
        self.char_to_value = {char: i for i, char in enumerate(self.charset)}
        self.value_to_char = {i: char for i, char in enumerate(self.charset)}
    
    def encode(self, data: Union[bytes, bytearray]) -> str:
        """
        Encode binary data to custom character set.
        
        Args:
            data: Binary data to encode.
            
        Returns:
            str: Encoded string using custom charset.
            
        Raises:
            ValidationError: If data is invalid.
        """
        if not isinstance(data, (bytes, bytearray)):
            raise ValidationError(
                "Data must be bytes or bytearray",
                ErrorCodes.INVALID_INPUT_FORMAT
            )
        
        if len(data) == 0:
            return ""
        
        # Convert bytes to big integer
        number = int.from_bytes(data, byteorder='big')
        
        if number == 0:
            return self.charset[0]
        
        # Convert to custom base
        result = []
        while number > 0:
            result.append(self.value_to_char[number % self.base])
            number //= self.base
        
        # Reverse to get correct order
        encoded = ''.join(reversed(result))
        
        # Add length prefix to handle leading zeros
        length_prefix = self._encode_length(len(data))
        
        return length_prefix + encoded
    
    def decode(self, encoded: str) -> bytes:
        """
        Decode custom encoded string back to binary data.
        
        Args:
            encoded: Encoded string to decode.
            
        Returns:
            bytes: Original binary data.
            
        Raises:
            ValidationError: If encoded string is invalid.
        """
        if not isinstance(encoded, str):
            raise ValidationError(
                "Encoded data must be string",
                ErrorCodes.INVALID_INPUT_FORMAT
            )
        
        if len(encoded) == 0:
            return b""
        
        # Validate characters
        for char in encoded:
            if char not in self.char_to_value:
                raise ValidationError(
                    f"Invalid character '{char}' in encoded data",
                    ErrorCodes.INVALID_INPUT_FORMAT
                )
        
        # Extract length prefix
        original_length, data_start = self._decode_length(encoded)
        encoded_data = encoded[data_start:]
        
        if len(encoded_data) == 0:
            return b'\x00' * original_length
        
        # Convert from custom base to integer
        number = 0
        for char in encoded_data:
            number = number * self.base + self.char_to_value[char]
        
        # Convert to bytes with correct length
        if number == 0:
            return b'\x00' * original_length
        
        # Calculate required bytes
        byte_length = (number.bit_length() + 7) // 8
        result = number.to_bytes(byte_length, byteorder='big')
        
        # Pad with leading zeros if necessary
        if len(result) < original_length:
            result = b'\x00' * (original_length - len(result)) + result
        
        return result
    
    def _encode_length(self, length: int) -> str:
        """Encode length as prefix using custom charset."""
        if length == 0:
            return self.charset[0] + self.padding_char
        
        result = []
        while length > 0:
            result.append(self.value_to_char[length % self.base])
            length //= self.base
        
        # Add separator
        return ''.join(reversed(result)) + self.padding_char
    
    def _decode_length(self, encoded: str) -> Tuple[int, int]:
        """Decode length prefix and return (length, data_start_index)."""
        separator_pos = encoded.find(self.padding_char)
        if separator_pos == -1:
            raise ValidationError(
                "Invalid encoded format: missing length separator",
                ErrorCodes.INVALID_INPUT_FORMAT
            )
        
        length_part = encoded[:separator_pos]
        if len(length_part) == 0:
            return 0, separator_pos + 1
        
        # Decode length
        length = 0
        for char in length_part:
            length = length * self.base + self.char_to_value[char]
        
        return length, separator_pos + 1
    
    def encode_with_noise(self, data: Union[bytes, bytearray], noise_ratio: float = 0.1) -> str:
        """
        Encode data with random noise characters for obfuscation.
        
        Args:
            data: Binary data to encode.
            noise_ratio: Ratio of noise characters to add (0.0 to 1.0).
            
        Returns:
            str: Encoded string with noise.
        """
        if not 0.0 <= noise_ratio <= 1.0:
            raise ValidationError(
                "Noise ratio must be between 0.0 and 1.0",
                ErrorCodes.INVALID_CONFIGURATION
            )
        
        # Encode normally
        encoded = self.encode(data)
        
        if noise_ratio == 0.0:
            return encoded
        
        # Add noise characters
        noise_count = int(len(encoded) * noise_ratio)
        result = list(encoded)
        
        for _ in range(noise_count):
            # Insert random character at random position
            pos = secrets.randbelow(len(result) + 1)
            noise_char = secrets.choice(self.charset)
            result.insert(pos, noise_char)
        
        # Mark noise positions (simple approach - use pattern)
        # In real implementation, you might want more sophisticated noise marking
        return ''.join(result)
    
    def create_steganographic_text(self, data: Union[bytes, bytearray], 
                                 template: str = "The quick brown fox jumps over the lazy dog") -> str:
        """
        Create steganographic text that hides data in character substitutions.
        
        Args:
            data: Binary data to hide.
            template: Template text to use as base.
            
        Returns:
            str: Text with hidden data.
        """
        encoded = self.encode(data)
        
        # Simple steganography: replace characters in template
        result = list(template.lower())
        encoded_pos = 0
        
        for i, char in enumerate(result):
            if char.isalpha() and encoded_pos < len(encoded):
                # Map alphabet to our charset
                if char in 'abcdef':
                    result[i] = encoded[encoded_pos]
                    encoded_pos += 1
                elif char in 'ghijklmnop':
                    # Map to numbers in our charset
                    if '9' in self.charset and '8' in self.charset:
                        result[i] = '9' if (ord(char) % 2) else '8'
                        if encoded_pos < len(encoded):
                            encoded_pos += 1
        
        return ''.join(result)
    
    def get_charset_info(self) -> dict:
        """
        Get information about the current charset.
        
        Returns:
            dict: Charset information.
        """
        return {
            'charset': self.charset,
            'base': self.base,
            'padding_char': self.padding_char,
            'efficiency': f"{(8 * 8) / (len(self.charset).bit_length() * 8):.2%}",
            'characters': list(self.charset),
            'unique_count': len(self.charset)
        }
    
    def benchmark_encoding(self, data_size: int = 1024) -> dict:
        """
        Benchmark encoding performance.
        
        Args:
            data_size: Size of test data in bytes.
            
        Returns:
            dict: Benchmark results.
        """
        import time
        
        # Generate test data
        test_data = secrets.token_bytes(data_size)
        
        # Benchmark encoding
        start_time = time.time()
        encoded = self.encode(test_data)
        encode_time = time.time() - start_time
        
        # Benchmark decoding
        start_time = time.time()
        decoded = self.decode(encoded)
        decode_time = time.time() - start_time
        
        return {
            'data_size': data_size,
            'encoded_size': len(encoded),
            'expansion_ratio': len(encoded) / data_size,
            'encode_time': encode_time,
            'decode_time': decode_time,
            'encode_speed_mbps': (data_size / (1024 * 1024)) / encode_time,
            'decode_speed_mbps': (data_size / (1024 * 1024)) / decode_time,
            'correctness': test_data == decoded
        } 