# Bytesize

A unified storage unit library for Python with cross-platform file size support.

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Type Checked](https://img.shields.io/badge/type--checked-mypy-blue.svg)](https://mypy.readthedocs.io/)

## Features

- =" **Comprehensive Unit Support**: Binary (KiB, MiB, GiB...), decimal (KB, MB, GB...), and bit units
- >î **Full Arithmetic Support**: Add, subtract, multiply, divide storage values with automatic unit handling
- = **Flexible String Parsing**: Case-insensitive parsing with support for various formats and separators
- =Á **Cross-Platform File Operations**: Get file and directory sizes using `pathlib` with platform-specific optimizations
- ¡ **Platform-Specific Optimizations**: Windows, Linux, and macOS-specific implementations for better performance
- <¯ **Type Safety**: Complete type annotations for better IDE support and code safety
- =« **Zero Dependencies**: Uses only Python standard library

## Installation

```bash
pip install bytesize
```

## Quick Start

```python
from bytesize import Storage, StorageUnit

# Create storage values
storage1 = Storage(1, StorageUnit.KIB)
storage2 = Storage(512, StorageUnit.BYTES)

# Arithmetic operations
total = storage1 + storage2  # 1536.0 BYTES
difference = storage1 - storage2  # 512.0 BYTES
doubled = storage1 * 2  # 2.0 KIB

# Comparisons
print(storage1 > storage2)  # True
print(storage1 == Storage(1024, StorageUnit.BYTES))  # True

# Unit conversion
print(storage1.convert_to_bytes())  # 1024.0
print(storage2.convert_to(StorageUnit.KIB))  # 0.5 KIB

# String parsing (flexible formats)
size1 = Storage.parse("1.5 MB")      # 1.5 MB
size2 = Storage.parse("1,024 KiB")   # 1024.0 KIB (comma as decimal separator)
size3 = Storage.parse("500GB")       # 500.0 GB (no space)
size4 = Storage.parse("2.5 tb")      # 2.5 TB (case insensitive)
size5 = Storage.parse("1024")        # 1024.0 BYTES (defaults to bytes)

# Auto-scaling for human-readable output
large_size = Storage(1536000000, StorageUnit.BYTES)
print(large_size.auto_scale())  # 1.43 GIB (binary) or 1.536 GB (decimal)

# File operations
file_size = Storage.get_size_from_path("/path/to/file.txt")
dir_size = Storage.get_size_from_path("/path/to/directory")
print(f"Directory size: {dir_size.auto_scale()}")
```

## Supported Units

### Binary Units (Base 1024)
- `BYTES` (1 byte)
- `KIB` (1,024 bytes)
- `MIB` (1,048,576 bytes)
- `GIB`, `TIB`, `PIB`, `EIB`, `ZIB`, `YIB`

### Decimal Units (Base 1000)
- `KB` (1,000 bytes)
- `MB` (1,000,000 bytes)
- `GB` (1,000,000,000 bytes)
- `TB`, `PB`, `EB`, `ZB`, `YB`

### Bit Units
- `BITS` (1/8 byte)
- `KILOBITS`, `MEGABITS`, `GIGABITS`, `TERABITS`, `PETABITS`, `EXABITS`, `ZETTABITS`, `YOTTABITS`

## Advanced Usage

### Platform-Specific Optimizations

```python
from bytesize import Storage

# Automatically detect and use platform-specific optimizations
platform_storage = Storage.get_platform_storage()
size = platform_storage.get_size_from_path("/large/directory")

# Platform info
info = platform_storage.get_platform_info()
print(f"Platform: {info['platform']}")
print(f"Optimizations: {info.get('api_optimization', 'none')}")
```

### String Parsing Features

The `parse()` method supports various input formats:

```python
# Case insensitive
Storage.parse("1.5 mb")      # Works
Storage.parse("1.5 MB")      # Works
Storage.parse("1.5 Mb")      # Works

# Decimal separators
Storage.parse("1.5 MB")      # Dot separator
Storage.parse("1,5 MB")      # Comma separator

# Spacing
Storage.parse("1.5 MB")      # With space
Storage.parse("1.5MB")       # Without space

# Default unit
Storage.parse("1024")        # Defaults to bytes
Storage.parse("1024", StorageUnit.KIB)  # Custom default

# Comprehensive unit aliases
Storage.parse("1 kilobyte")  # Full name
Storage.parse("1 kb")        # Abbreviation
Storage.parse("1 k")         # Single letter
```

### Error Handling

```python
from bytesize import Storage, StorageUnit

# Invalid values raise appropriate exceptions
try:
    Storage(-1, StorageUnit.BYTES)  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")

try:
    Storage.parse("invalid")  # Raises ValueError
except ValueError as e:
    print(f"Parsing error: {e}")

try:
    storage = Storage(1, StorageUnit.KIB)
    result = storage / 0  # Raises ZeroDivisionError
except ZeroDivisionError as e:
    print(f"Division error: {e}")
```

## Real-World Examples

### Download Time Calculator

```python
from bytesize import Storage, StorageUnit

# File sizes
movie = Storage.parse("1.4 GB")
song = Storage.parse("4.5 MB")

# Network speeds (in bits per second)
broadband = Storage.parse("50 Megabits")  # 50 Mbps
fiber = Storage.parse("1 Gigabit")        # 1 Gbps

# Calculate download times
movie_time_broadband = movie / broadband  # seconds
movie_time_fiber = movie / fiber          # seconds

print(f"Movie download time:")
print(f"  Broadband (50 Mbps): {movie_time_broadband:.1f} seconds")
print(f"  Fiber (1 Gbps): {movie_time_fiber:.1f} seconds")
```

### Storage Capacity Planning

```python
# Calculate total storage needs
photos = Storage.parse("2.8 MiB") * 2000      # 2000 photos
music = Storage.parse("4.5 MB") * 500         # 500 songs
videos = Storage.parse("1.2 GB") * 50         # 50 videos
documents = Storage.parse("250 KB") * 1000    # 1000 documents

total_needed = photos + music + videos + documents
print(f"Total storage needed: {total_needed.auto_scale()}")

# Available storage
available = Storage.parse("500 GB")
remaining = available - total_needed
print(f"Remaining space: {remaining.auto_scale()}")
```

## Development

### Running Tests

```bash
# Run basic functionality tests
python test_basic_functionality.py

# Run demonstration
python demo.py
```

### Building and Installation

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run type checking
mypy bytesize/

# Run code formatting
black bytesize/
isort bytesize/

# Build package
python -m build
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### 0.1.0 (Initial Release)
- Complete storage unit enumeration system
- Full arithmetic and comparison operations
- Flexible string parsing with multiple format support
- Cross-platform file size operations using pathlib
- Platform-specific optimizations for Windows, Linux, and macOS
- Comprehensive type annotations and documentation
- Zero external dependencies