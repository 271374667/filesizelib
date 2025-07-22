"""
Shared test configuration and fixtures for the filesizelib test suite.

This module provides common fixtures, test utilities, and configuration
for all filesizelib tests.
"""

import platform
import tempfile
import os
from pathlib import Path
from typing import Generator, List, Tuple, Any
import pytest

from filesizelib import Storage, StorageUnit
from filesizelib.platform_storage import WindowsStorage, LinuxStorage, MacStorage


# Platform detection fixture
@pytest.fixture(scope="session")
def current_platform() -> str:
    """Get the current platform name."""
    return platform.system()


@pytest.fixture(scope="session")
def is_windows(current_platform: str) -> bool:
    """Check if running on Windows."""
    return current_platform == "Windows"


@pytest.fixture(scope="session")
def is_linux(current_platform: str) -> bool:
    """Check if running on Linux."""
    return current_platform == "Linux"


@pytest.fixture(scope="session")
def is_macos(current_platform: str) -> bool:
    """Check if running on macOS."""
    return current_platform == "Darwin"


# Platform-specific storage fixtures
@pytest.fixture
def platform_storage_class(current_platform: str):
    """Get the appropriate platform storage class."""
    if current_platform == "Windows":
        return WindowsStorage
    elif current_platform == "Linux":
        return LinuxStorage
    elif current_platform == "Darwin":
        return MacStorage
    else:
        pytest.skip(f"Unsupported platform: {current_platform}")


# Test data fixtures
@pytest.fixture
def sample_storage_values() -> List[Tuple[float, StorageUnit]]:
    """Provide sample storage values for testing."""
    return [
        (0, StorageUnit.BYTES),
        (1, StorageUnit.BYTES),
        (1024, StorageUnit.BYTES),
        (1, StorageUnit.KIB),
        (1, StorageUnit.MIB),
        (1, StorageUnit.GIB),
        (1, StorageUnit.KB),
        (1, StorageUnit.MB),
        (1, StorageUnit.GB),
        (8, StorageUnit.BITS),
        (1000, StorageUnit.KILOBITS),
        (0.5, StorageUnit.KIB),
        (1.5, StorageUnit.MB),
        (2.75, StorageUnit.GIB),
    ]


@pytest.fixture
def binary_units() -> List[StorageUnit]:
    """Provide list of binary storage units."""
    return [
        StorageUnit.BYTES,
        StorageUnit.KIB,
        StorageUnit.MIB,
        StorageUnit.GIB,
        StorageUnit.TIB,
        StorageUnit.PIB,
        StorageUnit.EIB,
        StorageUnit.ZIB,
        StorageUnit.YIB,
    ]


@pytest.fixture
def decimal_units() -> List[StorageUnit]:
    """Provide list of decimal storage units."""
    return [
        StorageUnit.KB,
        StorageUnit.MB,
        StorageUnit.GB,
        StorageUnit.TB,
        StorageUnit.PB,
        StorageUnit.EB,
        StorageUnit.ZB,
        StorageUnit.YB,
    ]


@pytest.fixture
def bit_units() -> List[StorageUnit]:
    """Provide list of bit storage units."""
    return [
        StorageUnit.BITS,
        StorageUnit.KILOBITS,
        StorageUnit.MEGABITS,
        StorageUnit.GIGABITS,
        StorageUnit.TERABITS,
        StorageUnit.PETABITS,
        StorageUnit.EXABITS,
        StorageUnit.ZETTABITS,
        StorageUnit.YOTTABITS,
    ]


# File system test fixtures
@pytest.fixture
def temp_file_with_content() -> Generator[Tuple[Path, int], None, None]:
    """Create a temporary file with known content size."""
    content = b"Hello, World! " * 100  # 1400 bytes
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(content)
        temp_file_path = Path(temp_file.name)
    
    try:
        yield temp_file_path, len(content)
    finally:
        try:
            temp_file_path.unlink()
        except FileNotFoundError:
            pass


@pytest.fixture
def temp_directory_with_files() -> Generator[Tuple[Path, int], None, None]:
    """Create a temporary directory with multiple files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        total_size = 0
        
        # Create multiple files with known sizes
        for i in range(5):
            file_path = temp_path / f"file_{i}.txt"
            content = f"Content of file {i} " * (i + 1) * 10
            file_path.write_text(content, encoding="utf-8")
            total_size += len(content.encode("utf-8"))
        
        # Create a subdirectory with files
        subdir = temp_path / "subdir"
        subdir.mkdir()
        for i in range(3):
            file_path = subdir / f"subfile_{i}.txt"
            content = f"Subcontent {i} " * (i + 1) * 5
            file_path.write_text(content, encoding="utf-8")
            total_size += len(content.encode("utf-8"))
        
        yield temp_path, total_size


# String parsing test data fixture
@pytest.fixture
def parsing_test_cases() -> List[Tuple[str, float, StorageUnit]]:
    """Provide test cases for string parsing."""
    return [
        # Basic cases
        ("1 MB", 1.0, StorageUnit.MB),
        ("1.5 GB", 1.5, StorageUnit.GB),
        ("1024 bytes", 1024.0, StorageUnit.BYTES),
        
        # Case variations
        ("1 mb", 1.0, StorageUnit.MB),
        ("1 Mb", 1.0, StorageUnit.MB),
        ("1 mB", 1.0, StorageUnit.MB),
        
        # No spaces
        ("1MB", 1.0, StorageUnit.MB),
        ("1.5GB", 1.5, StorageUnit.GB),
        ("1024bytes", 1024.0, StorageUnit.BYTES),
        
        # Comma as decimal separator
        ("1,5 MB", 1.5, StorageUnit.MB),
        ("2,75 GB", 2.75, StorageUnit.GB),
        ("0,5 KiB", 0.5, StorageUnit.KIB),
        
        # Different units
        ("1 KiB", 1.0, StorageUnit.KIB),
        ("1 MiB", 1.0, StorageUnit.MIB),
        ("1 GiB", 1.0, StorageUnit.GIB),
        ("1 KB", 1.0, StorageUnit.KB),
        ("1 MB", 1.0, StorageUnit.MB),
        ("1 GB", 1.0, StorageUnit.GB),
        
        # Bit units
        ("8 bits", 8.0, StorageUnit.BITS),
        ("1 kilobit", 1.0, StorageUnit.KILOBITS),
        ("1 megabit", 1.0, StorageUnit.MEGABITS),
        
        # Numbers without units (default to bytes)
        ("1024", 1024.0, StorageUnit.BYTES),
        ("500", 500.0, StorageUnit.BYTES),
        ("0", 0.0, StorageUnit.BYTES),
        
        # Decimal values
        ("0.5", 0.5, StorageUnit.BYTES),
        ("3.14159", 3.14159, StorageUnit.BYTES),
        
        # Various aliases
        ("1 k", 1.0, StorageUnit.KB),
        ("1 m", 1.0, StorageUnit.MB),
        ("1 g", 1.0, StorageUnit.GB),
        ("1 ki", 1.0, StorageUnit.KIB),
        ("1 mi", 1.0, StorageUnit.MIB),
        ("1 gi", 1.0, StorageUnit.GIB),
    ]


@pytest.fixture
def invalid_parsing_cases() -> List[str]:
    """Provide invalid string cases for parsing error tests."""
    return [
        "",
        "   ",
        "abc",
        "1.2.3 MB",
        "MB 1",
        "1 2 MB",
        "invalid format",
        "1..5 MB",
        "1,2,3 GB",
        "-1 MB",  # This should be handled as ValueError in parsing
    ]


# Arithmetic test data
@pytest.fixture
def arithmetic_test_cases() -> List[Tuple[Storage, Storage, str, Any]]:
    """Provide test cases for arithmetic operations."""
    s1 = Storage(1, StorageUnit.KIB)
    s2 = Storage(512, StorageUnit.BYTES)
    s3 = Storage(2, StorageUnit.KIB)
    s4 = Storage(0, StorageUnit.BYTES)
    
    return [
        # Addition
        (s1, s2, "add", Storage(1536, StorageUnit.BYTES)),
        (s2, s1, "add", Storage(1536, StorageUnit.BYTES)),
        (s1, s3, "add", Storage(3072, StorageUnit.BYTES)),
        (s4, s1, "add", Storage(1024, StorageUnit.BYTES)),
        
        # Subtraction
        (s1, s2, "sub", Storage(512, StorageUnit.BYTES)),
        (s3, s1, "sub", Storage(1024, StorageUnit.BYTES)),
        (s1, s4, "sub", s1),
        
        # Multiplication
        (s1, 2, "mul", Storage(2, StorageUnit.KIB)),
        (s1, 0.5, "mul", Storage(0.5, StorageUnit.KIB)),
        (s1, 0, "mul", Storage(0, StorageUnit.KIB)),
        (s1, 1, "mul", s1),
        
        # Division by number
        (s1, 2, "truediv_num", Storage(0.5, StorageUnit.KIB)),
        (s1, 0.5, "truediv_num", Storage(2, StorageUnit.KIB)),
        (s1, 1, "truediv_num", s1),
        
        # Division by storage (ratio)
        (s1, s2, "truediv_storage", 2.0),
        (s3, s1, "truediv_storage", 2.0),
        (s1, s1, "truediv_storage", 1.0),
        
        # Floor division
        (Storage(5, StorageUnit.KIB), 2, "floordiv", Storage(2, StorageUnit.KIB)),
        (Storage(7, StorageUnit.KIB), 3, "floordiv", Storage(2, StorageUnit.KIB)),
        
        # Modulo
        (Storage(5, StorageUnit.KIB), 2, "mod", Storage(1, StorageUnit.KIB)),
        (Storage(7, StorageUnit.KIB), 3, "mod", Storage(1, StorageUnit.KIB)),
    ]


# Comparison test data
@pytest.fixture
def comparison_test_cases() -> List[Tuple[Storage, Storage, str, bool]]:
    """Provide test cases for comparison operations."""
    s1 = Storage(1, StorageUnit.KIB)
    s2 = Storage(1024, StorageUnit.BYTES)
    s3 = Storage(2, StorageUnit.KIB)
    s4 = Storage(512, StorageUnit.BYTES)
    
    return [
        # Equality
        (s1, s2, "eq", True),
        (s1, s3, "eq", False),
        (s1, s4, "eq", False),
        
        # Less than
        (s4, s1, "lt", True),
        (s1, s3, "lt", True),
        (s1, s2, "lt", False),
        (s3, s1, "lt", False),
        
        # Less than or equal
        (s4, s1, "le", True),
        (s1, s2, "le", True),
        (s1, s3, "le", True),
        (s3, s1, "le", False),
        
        # Greater than
        (s1, s4, "gt", True),
        (s3, s1, "gt", True),
        (s1, s2, "gt", False),
        (s1, s3, "gt", False),
        
        # Greater than or equal
        (s1, s4, "ge", True),
        (s1, s2, "ge", True),
        (s3, s1, "ge", True),
        (s1, s3, "ge", False),
        
        # Not equal
        (s1, s3, "ne", True),
        (s1, s4, "ne", True),
        (s1, s2, "ne", False),
    ]


# Error test cases
@pytest.fixture
def error_test_cases() -> List[Tuple[Any, Any, type, str]]:
    """Provide test cases for error conditions."""
    return [
        # Storage initialization errors
        (-1, StorageUnit.BYTES, ValueError, "negative value"),
        ("invalid", StorageUnit.BYTES, TypeError, "invalid type for value"),
        (1, "invalid", TypeError, "invalid type for unit"),
        
        # Division errors
        (Storage(1, StorageUnit.KIB), 0, ZeroDivisionError, "division by zero"),
        (Storage(1, StorageUnit.KIB), Storage(0, StorageUnit.BYTES), ZeroDivisionError, "division by zero storage"),
        
        # Subtraction errors
        (Storage(1, StorageUnit.BYTES), Storage(2, StorageUnit.BYTES), ValueError, "negative result"),
        
        # Multiplication errors
        (Storage(1, StorageUnit.KIB), -1, ValueError, "negative factor"),
    ]


# Auto-scaling test data
@pytest.fixture
def auto_scaling_test_cases() -> List[Tuple[Storage, bool, Storage]]:
    """Provide test cases for auto-scaling functionality."""
    return [
        # Binary scaling
        (Storage(1024, StorageUnit.BYTES), True, Storage(1, StorageUnit.KIB)),
        (Storage(1536, StorageUnit.BYTES), True, Storage(1.5, StorageUnit.KIB)),
        (Storage(1048576, StorageUnit.BYTES), True, Storage(1, StorageUnit.MIB)),
        (Storage(1073741824, StorageUnit.BYTES), True, Storage(1, StorageUnit.GIB)),
        
        # Decimal scaling
        (Storage(1000, StorageUnit.BYTES), False, Storage(1, StorageUnit.KB)),
        (Storage(1500, StorageUnit.BYTES), False, Storage(1.5, StorageUnit.KB)),
        (Storage(1000000, StorageUnit.BYTES), False, Storage(1, StorageUnit.MB)),
        (Storage(1000000000, StorageUnit.BYTES), False, Storage(1, StorageUnit.GB)),
        
        # Edge cases
        (Storage(0, StorageUnit.BYTES), True, Storage(0, StorageUnit.BYTES)),
        (Storage(0, StorageUnit.BYTES), False, Storage(0, StorageUnit.BYTES)),
        (Storage(512, StorageUnit.BYTES), True, Storage(512, StorageUnit.BYTES)),
        (Storage(500, StorageUnit.BYTES), False, Storage(500, StorageUnit.BYTES)),
    ]


# Platform-specific test markers
@pytest.fixture(autouse=True)
def skip_if_platform_unavailable(request, current_platform: str):
    """Skip tests if they require a different platform."""
    if request.node.get_closest_marker("windows_only") and current_platform != "Windows":
        pytest.skip("Test requires Windows platform")
    elif request.node.get_closest_marker("linux_only") and current_platform != "Linux":
        pytest.skip("Test requires Linux platform")
    elif request.node.get_closest_marker("macos_only") and current_platform != "Darwin":
        pytest.skip("Test requires macOS platform")


# Custom pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "windows_only: marks tests that only run on Windows")
    config.addinivalue_line("markers", "linux_only: marks tests that only run on Linux")
    config.addinivalue_line("markers", "macos_only: marks tests that only run on macOS")
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "platform_specific: marks tests as platform-specific")


# Test utilities
class TestUtils:
    """Utility class for common test operations."""
    
    @staticmethod
    def create_temp_file_with_size(size_bytes: int) -> Path:
        """Create a temporary file with specific size."""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(b"0" * size_bytes)
        temp_file.close()
        return Path(temp_file.name)
    
    @staticmethod
    def assert_storage_equal(actual: Storage, expected: Storage, tolerance: float = 1e-10):
        """Assert that two Storage objects are equal within tolerance."""
        assert abs(actual.convert_to_bytes() - expected.convert_to_bytes()) < tolerance
    
    @staticmethod
    def assert_storage_approximately_equal(actual: Storage, expected: Storage, 
                                         relative_tolerance: float = 1e-9):
        """Assert that two Storage objects are approximately equal."""
        actual_bytes = actual.convert_to_bytes()
        expected_bytes = expected.convert_to_bytes()
        
        if expected_bytes == 0:
            assert actual_bytes == 0
        else:
            relative_error = abs(actual_bytes - expected_bytes) / expected_bytes
            assert relative_error < relative_tolerance


@pytest.fixture
def test_utils():
    """Provide test utilities."""
    return TestUtils