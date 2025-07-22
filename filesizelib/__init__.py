"""
FileSizeLib: A unified storage unit library for Python.

This library provides a simple, unified interface for working with storage units
such as bytes, kilobytes, megabytes, etc. It supports arithmetic operations,
comparisons, and conversion between different units without requiring any
third-party dependencies.

Key Features:
- Enum-based unit definitions
- Cross-platform file size retrieval
- String parsing with flexible formats
- Configurable decimal precision (no scientific notation)
- Type-safe operations with full annotations
- Platform-specific optimizations

Example:
    >>> from filesizelib import Storage, StorageUnit, FileSizeLib
    >>> size = Storage(1, StorageUnit.KIB)
    >>> print(size.convert_to_bytes())
    1024
    >>> parsed = Storage.parse("1.5 MB")
    >>> print(parsed)
    1.5 MB
    >>> # FileSizeLib is an alias for Storage
    >>> filesize = FileSizeLib(1024, StorageUnit.BYTES)
    >>> print(filesize.convert_to_kib())
    1.0 KIB
    >>> # Configure decimal precision
    >>> Storage.set_decimal_precision(10)
    >>> small = Storage(9.872019291e-05, StorageUnit.GIB)
    >>> print(small)  # No scientific notation
    0.0000987202 GIB
"""

from .storage_unit import StorageUnit
from .storage import Storage
from .platform_storage import WindowsStorage, LinuxStorage, MacStorage

# FileSizeLib is an alias for Storage to match the package name
# Both classes are functionally identical
FileSizeLib = Storage

__version__ = "0.6.5"
__author__ = "PythonImporter"
__all__ = [
    "Storage",
    "StorageUnit", 
    "FileSizeLib",  # Alias for Storage
    "WindowsStorage",
    "LinuxStorage", 
    "MacStorage"
]