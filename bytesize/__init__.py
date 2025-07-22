"""
Bytesize: A unified storage unit library for Python.

This library provides a simple, unified interface for working with storage units
such as bytes, kilobytes, megabytes, etc. It supports arithmetic operations,
comparisons, and conversion between different units without requiring any
third-party dependencies.

Key Features:
- Enum-based unit definitions
- Cross-platform file size retrieval
- String parsing with flexible formats
- Type-safe operations with full annotations
- Platform-specific optimizations

Example:
    >>> from bytesize import Storage, StorageUnit
    >>> size = Storage(1, StorageUnit.KIB)
    >>> print(size.convert_to_bytes())
    1024
    >>> parsed = Storage.parse("1.5 MB")
    >>> print(parsed)
    1.5 MB
"""

from .storage_unit import StorageUnit
from .storage import Storage
from .platform_storage import WindowsStorage, LinuxStorage, MacStorage

__version__ = "0.1.0"
__author__ = "PythonImporter"
__all__ = [
    "Storage",
    "StorageUnit", 
    "WindowsStorage",
    "LinuxStorage", 
    "MacStorage"
]