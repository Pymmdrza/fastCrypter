"""
Pytest configuration and fixtures for fastcrypter tests.
"""

import pytest


@pytest.fixture
def test_password():
    """Standard test password."""
    return "TestPassword123!"


@pytest.fixture
def test_data():
    """Standard test data."""
    return b"Test data for encryption and compression"


@pytest.fixture
def large_test_data():
    """Large test data."""
    return b"Large test data " * 10000
