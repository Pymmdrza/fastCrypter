#!/usr/bin/env python3
"""
Setup script for FastCrypt package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text(encoding="utf-8").strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="fastcrypt",
    version="2.0.0",
    author="Mmdrza",
    author_email="pymmdrza@gmail.com",
    description="Professional compression and encryption library with native C/C++ acceleration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Pymmdrza/fastcrypt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: System :: Archiving :: Compression",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-benchmark>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "native": [
            "numpy>=1.24.0",
            "cython>=3.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "fastcrypt=fastcrypt.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "fastcrypt": [
            "native/libs/*/*.so",
            "native/libs/*/*.dll", 
            "native/libs/*/*.dylib",
            "*.md",
        ],
    },
    keywords=[
        "encryption", "compression", "security", "cryptography",
        "aes", "chacha20", "rsa", "zlib", "lzma", "brotli",
        "native", "performance", "c++", "custom-encoding", "fast"
    ],
    project_urls={
        "Bug Reports": "https://github.com/Pymmdrza/fastcrypt/issues",
        "Source": "https://github.com/Pymmdrza/fastcrypt",
        "Documentation": "https://fastcrypt.readthedocs.io/",
    },
) 