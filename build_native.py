#!/usr/bin/env python3
"""
Build Script for fastcrypt Native Libraries

This script automatically compiles C/C++ native libraries for the fastcrypt package
to provide maximum performance for cryptographic operations.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


class NativeLibraryBuilder:
    """Builder for native C/C++ libraries."""
    
    def __init__(self):
        """Initialize the builder."""
        self.project_root = Path(__file__).parent
        self.native_dir = self.project_root / 'fastcrypt' / 'native'
        self.libs_dir = self.native_dir / 'libs'
        self.platform = self._detect_platform()
        self.platform_dir = self.libs_dir / self.platform
        
        # Compiler settings
        self.compilers = self._detect_compilers()
        self.lib_extension = self._get_lib_extension()
        
    def _detect_platform(self) -> str:
        """Detect current platform."""
        system = platform.system()
        if system == 'Windows':
            return 'windows'
        elif system == 'Darwin':
            return 'macos'
        else:
            return 'linux'
    
    def _detect_compilers(self) -> dict:
        """Detect available compilers."""
        compilers = {}
        
        # C compiler
        for cc in ['gcc', 'clang', 'cc']:
            if shutil.which(cc):
                compilers['c'] = cc
                break
        
        # C++ compiler
        for cxx in ['g++', 'clang++', 'c++']:
            if shutil.which(cxx):
                compilers['cxx'] = cxx
                break
        
        # Windows-specific
        if self.platform == 'windows':
            if shutil.which('x86_64-w64-mingw32-gcc'):
                compilers['c'] = 'x86_64-w64-mingw32-gcc'
            if shutil.which('x86_64-w64-mingw32-g++'):
                compilers['cxx'] = 'x86_64-w64-mingw32-g++'
        
        return compilers
    
    def _get_lib_extension(self) -> str:
        """Get library extension for current platform."""
        extensions = {
            'windows': '.dll',
            'linux': '.so',
            'macos': '.dylib'
        }
        return extensions.get(self.platform, '.so')
    
    def _get_compile_flags(self, language: str) -> list:
        """Get compilation flags for the language."""
        base_flags = [
            '-O3',           # Maximum optimization
            '-fPIC',         # Position independent code
            '-Wall',         # All warnings
            '-Wextra',       # Extra warnings
            '-march=native', # Optimize for current CPU
            '-ffast-math',   # Fast math operations
            '-DNDEBUG',      # Release mode
        ]
        
        if language == 'cxx':
            base_flags.append('-std=c++17')
        
        # Platform-specific flags
        if self.platform == 'linux':
            base_flags.extend(['-DLINUX', '-flto', '-funroll-loops'])
        elif self.platform == 'macos':
            base_flags.extend(['-DMACOS', '-flto', '-funroll-loops'])
        elif self.platform == 'windows':
            base_flags.extend(['-DWINDOWS'])
        
        return base_flags
    
    def _get_link_flags(self) -> list:
        """Get linking flags."""
        flags = ['-shared']
        
        if self.platform in ['linux', 'macos']:
            flags.extend(['-lm', '-flto'])
        elif self.platform == 'windows':
            flags.append('-Wl,--out-implib,lib$@.a')
        
        return flags
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        print("Checking build dependencies...")
        
        # Check compilers
        if 'c' not in self.compilers:
            print("C compiler not found. Please install gcc, clang, or equivalent.")
            return False
        
        if 'cxx' not in self.compilers:
            print("C++ compiler not found. Please install g++, clang++, or equivalent.")
            return False
        
        print(f"C compiler: {self.compilers['c']}")
        print(f"C++ compiler: {self.compilers['cxx']}")
        print(f"Platform: {self.platform}")
        print(f"Library extension: {self.lib_extension}")
        
        return True
    
    def create_directories(self):
        """Create necessary directories."""
        print("Creating directories...")
        self.platform_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created: {self.platform_dir}")
    
    def compile_crypto_core(self) -> bool:
        """Compile crypto_core library."""
        print("Compiling crypto_core library...")
        
        source_file = self.native_dir / 'crypto_core.c'
        output_file = self.platform_dir / f'libcrypto_core{self.lib_extension}'
        
        if not source_file.exists():
            print(f"Source file not found: {source_file}")
            return False
        
        # Build command
        cmd = [
            self.compilers['c'],
            *self._get_compile_flags('c'),
            *self._get_link_flags(),
            '-o', str(output_file),
            str(source_file)
        ]
        
        try:
            print(f"   Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.native_dir)
            
            if result.returncode == 0:
                print(f"crypto_core library built: {output_file}")
                return True
            else:
                print(f"Compilation failed:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Compilation error: {e}")
            return False
    
    def compile_hash_algorithms(self) -> bool:
        """Compile hash_algorithms library."""
        print("Compiling hash_algorithms library...")
        
        source_file = self.native_dir / 'hash_algorithms.cpp'
        output_file = self.platform_dir / f'libhash_algorithms{self.lib_extension}'
        
        if not source_file.exists():
            print(f"Source file not found: {source_file}")
            return False
        
        # Build command
        cmd = [
            self.compilers['cxx'],
            *self._get_compile_flags('cxx'),
            *self._get_link_flags(),
            '-o', str(output_file),
            str(source_file)
        ]
        
        try:
            print(f"   Command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.native_dir)
            
            if result.returncode == 0:
                print(f"hash_algorithms library built: {output_file}")
                return True
            else:
                print(f"Compilation failed:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Compilation error: {e}")
            return False
    
    def test_libraries(self) -> bool:
        """Test compiled libraries."""
        print("Testing compiled libraries...")
        
        try:
            # Try to load the libraries using Python
            sys.path.insert(0, str(self.project_root))
            
            from fastcrypt.native.native_loader import get_native_manager
            
            manager = get_native_manager()
            results = manager.load_all()
            
            success = True
            for lib_name, loaded in results.items():
                if loaded:
                    print(f"{lib_name}: loaded successfully")
                else:
                    print(f"{lib_name}: failed to load")
                    success = False
            
            if success:
                print("All libraries loaded successfully!")
                
                # Run basic functionality tests
                if manager.crypto_core:
                    try:
                        # Test XOR operation
                        test_data = b"Hello, World!"
                        test_key = b"key123"
                        result = manager.crypto_core.fast_xor(test_data, test_key)
                        print("XOR operation test passed")
                        
                        # Test entropy calculation
                        entropy = manager.crypto_core.calculate_entropy(test_data)
                        print(f"Entropy calculation test passed (entropy: {entropy:.2f})")
                        
                    except Exception as e:
                        print(f"Functionality test failed: {e}")
                        success = False
                
                if manager.hash_algorithms:
                    try:
                        # Test SHA-256
                        test_data = b"Hello, World!"
                        hash_result = manager.hash_algorithms.fast_sha256(test_data)
                        print(f"hash_algorithms: SHA-256 test passed (hash: {hash_result[:8].hex()}...)")
                        
                        # Test key generation
                        private_key, public_key = manager.hash_algorithms.generate_keypair()
                        print(f"hash_algorithms: Key generation test passed")
                        
                    except Exception as e:
                        print(f"hash_algorithms: Functionality test failed: {e}")
                        success = False
            
            return success
            
        except Exception as e:
            print(f"Library testing failed: {e}")
            return False
    
    def build_all(self) -> bool:
        """Build all native libraries."""
        print("Building fastcrypt Native Libraries")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Create directories
        self.create_directories()
        
        # Compile libraries
        success = True
        
        if not self.compile_crypto_core():
            success = False
        
        if not self.compile_hash_algorithms():
            success = False
        
        if success:
            print("\nAll libraries compiled successfully!")
            
            # Test libraries
            if self.test_libraries():
                print("\nBuild completed successfully!")
                print(f"Libraries available in: {self.platform_dir}")
                return True
            else:
                print("\nLibrary testing failed!")
                return False
        else:
            print("\nBuild failed!")
            return False
    
    def clean(self):
        """Clean build artifacts."""
        print("Cleaning build artifacts...")
        
        if self.libs_dir.exists():
            shutil.rmtree(self.libs_dir)
            print(f"Removed: {self.libs_dir}")
        else:
            print("No build artifacts to clean")
    
    def install_system_wide(self) -> bool:
        """Install libraries system-wide (optional)."""
        print("Installing libraries system-wide...")
        
        if self.platform == 'linux':
            try:
                for lib_file in self.platform_dir.glob('*.so'):
                    dest = Path('/usr/local/lib') / lib_file.name
                    subprocess.run(['sudo', 'cp', str(lib_file), str(dest)], check=True)
                    print(f"Installed: {dest}")
                
                subprocess.run(['sudo', 'ldconfig'], check=True)
                print("Updated library cache")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"Installation failed: {e}")
                return False
        
        elif self.platform == 'macos':
            try:
                for lib_file in self.platform_dir.glob('*.dylib'):
                    dest = Path('/usr/local/lib') / lib_file.name
                    subprocess.run(['sudo', 'cp', str(lib_file), str(dest)], check=True)
                    print(f"Installed: {dest}")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"Installation failed: {e}")
                return False
        
        else:
            print("System-wide installation not supported on Windows")
            return True


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build fastcrypt native libraries')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts')
    parser.add_argument('--install', action='store_true', help='Install libraries system-wide')
    parser.add_argument('--test-only', action='store_true', help='Only test existing libraries')
    
    args = parser.parse_args()
    
    builder = NativeLibraryBuilder()
    
    if args.clean:
        builder.clean()
        return 0
    
    if args.test_only:
        if builder.test_libraries():
            return 0
        else:
            return 1
    
    # Build libraries
    if builder.build_all():
        if args.install:
            builder.install_system_wide()
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main()) 