#!/usr/bin/env python3
"""
Setup script for Encrypter package.
Professional compression and encryption library.
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    """Read README.md file for long description."""
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    """Read requirements.txt file."""
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Package metadata
PACKAGE_NAME = "encrypter"
VERSION = "1.0.0"
AUTHOR = "Mmdrza"
AUTHOR_EMAIL = "pymmdrza@gmail.com"
DESCRIPTION = "Professional compression and encryption library"
URL = "https://github.com/pymmdrza/encrypter"

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url=URL,
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
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
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography",
        "pycryptodome",
        "brotli",
        "argon2-cffi",
        "bcrypt",
        "numpy",
    ],
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
        "performance": [
            "cython>=3.0.0",
            "psutil>=5.9.0",
            "tqdm>=4.66.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "encryption",
        "compression",
        "security",
        "cryptography",
        "aes",
        "chacha20",
        "rsa",
        "zlib",
        "lzma",
        "brotli",
        "privacy",
        "data-protection",
    ],
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
        "Documentation": f"{URL}/docs",
        "Funding": f"{URL}/sponsors",
    },
) 