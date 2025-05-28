#!/usr/bin/env python3
"""
File encryption testing

This file tests file encryption and decryption capabilities.
"""

import sys
import os
import tempfile

# Add the parent directory to the path so we can import encrypter
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from encrypter import FileEncryptor


def main():
    """Main file encryption test."""
    print("📁 File Encryption Testing")
    print("=" * 40)
    
    # Create temporary test file
    test_content = """
    This is a test file for encryption.
    The content includes both English and various text.
    
    This is a test file for encryption.
    The content includes both English and various text.
    
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
    """ * 5  # Repeat to increase volume
    
    password = "FileTestPassword123!"
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        original_file = f.name
    
    encrypted_file = original_file + '.enc'
    decrypted_file = original_file + '.dec'
    
    try:
        print(f"📝 Original file: {os.path.basename(original_file)}")
        print(f"   Size: {len(test_content.encode('utf-8'))} bytes")
        print()
        
        # Create FileEncryptor
        encryptor = FileEncryptor(password=password)
        
        # Encrypt file
        print("🔐 Encrypting file...")
        encrypt_stats = encryptor.encrypt_file(original_file, encrypted_file)
        
        print("✅ Encryption successful:")
        print(f"   Encrypted file: {os.path.basename(encrypted_file)}")
        print(f"   Original size: {encrypt_stats['original_size']} bytes")
        print(f"   Encrypted size: {encrypt_stats['encrypted_size']} bytes")
        print(f"   Compression ratio: {encrypt_stats['compression_ratio']:.2f}")
        print()
        
        # Decrypt file
        print("🔓 Decrypting file...")
        decrypt_stats = encryptor.decrypt_file(encrypted_file, decrypted_file)
        
        print("✅ Decryption successful:")
        print(f"   Decrypted file: {os.path.basename(decrypted_file)}")
        print(f"   Encrypted size: {decrypt_stats['encrypted_size']} bytes")
        print(f"   Decrypted size: {decrypt_stats['decrypted_size']} bytes")
        print(f"   Expansion ratio: {decrypt_stats['expansion_ratio']:.2f}")
        print()
        
        # Verify content integrity
        print("🔍 Verifying content integrity...")
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()
        
        if original_content == decrypted_content:
            print("✅ File content successfully recovered!")
        else:
            print("❌ Error: File content does not match!")
            return 1
        
        print()
        
        # Test with wrong password
        print("🚫 Testing wrong password...")
        wrong_encryptor = FileEncryptor(password="WrongPassword123!")
        
        try:
            wrong_encryptor.decrypt_file(encrypted_file, decrypted_file + '.wrong')
            print("❌ Error: Wrong password was accepted!")
            return 1
        except Exception as e:
            print("✅ Wrong password correctly rejected")
        
        print()
        
        # Display file information
        print("📊 Results summary:")
        print(f"   Original file: {os.path.getsize(original_file)} bytes")
        print(f"   Encrypted file: {os.path.getsize(encrypted_file)} bytes")
        print(f"   Decrypted file: {os.path.getsize(decrypted_file)} bytes")
        
        # Calculate efficiency
        efficiency = (1 - os.path.getsize(encrypted_file) / os.path.getsize(original_file)) * 100
        print(f"   Compression efficiency: {efficiency:.1f}%")
        
        print()
        print("🎉 File encryption test completed successfully!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    finally:
        # Clean up temporary files
        for file_path in [original_file, encrypted_file, decrypted_file, decrypted_file + '.wrong']:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except:
                pass


if __name__ == "__main__":
    exit(main()) 