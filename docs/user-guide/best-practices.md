# Best Practices

Guidelines and recommendations for using Bytesize effectively in production applications.

## 🎯 Core Principles

### 1. Choose the Right Unit Type

**Binary Units** for system resources and file systems:
```python
# ✅ Good - Binary units for memory
ram = Storage(16, StorageUnit.GIB)
cache_size = Storage(512, StorageUnit.MIB)

# ✅ Good - Binary units for file operations
file_size = Storage.get_size_from_path("large_file.bin")
if file_size.convert_to_gib().value > 4:
    print("Large file detected")
```

**Decimal Units** for user-facing displays and storage devices:
```python
# ✅ Good - Decimal units for storage devices
disk_capacity = Storage(500, StorageUnit.GB)
available_space = Storage(234.5, StorageUnit.GB)

# ✅ Good - Decimal units for download sizes
download_size = Storage.parse("1.2 GB")
```

**Bit Units** for network and bandwidth:
```python
# ✅ Good - Bit units for network speeds
connection_speed = Storage(100, StorageUnit.MEGABITS)
throughput = Storage(1, StorageUnit.GIGABITS)
```

### 2. Consistent Error Handling

Always handle potential exceptions:

```python
# ✅ Good - Comprehensive error handling
def get_directory_size(path: str) -> Optional[Storage]:
    """Get directory size with proper error handling."""
    try:
        return Storage.get_size_from_path(path)
    except FileNotFoundError:
        logging.warning(f"Directory not found: {path}")
        return None
    except PermissionError:
        logging.warning(f"Permission denied: {path}")
        return None
    except OSError as e:
        logging.error(f"OS error for {path}: {e}")
        return None

# ✅ Good - Safe parsing with validation
def parse_user_input(size_string: str) -> Storage:
    """Parse user input with validation."""
    if not size_string.strip():
        raise ValueError("Size string cannot be empty")
    
    try:
        storage = Storage.parse(size_string)
        if storage.convert_to_bytes() < 0:
            raise ValueError("Size cannot be negative")
        return storage
    except ValueError as e:
        raise ValueError(f"Invalid size format '{size_string}': {e}")
```

### 3. Use Auto-Scaling for Display

Always use `auto_scale()` for human-readable output:

```python
# ✅ Good - Auto-scaling for display
def display_file_info(file_path: str):
    """Display file information in readable format."""
    size = Storage.get_size_from_path(file_path)
    print(f"File: {file_path}")
    print(f"Size: {size.auto_scale()}")  # Automatically chooses best unit

# ❌ Bad - Fixed unit might be inappropriate
def bad_display(file_path: str):
    size = Storage.get_size_from_path(file_path)
    print(f"Size: {size.convert_to_mb()}")  # Always MB, even for KB files
```

## 🛡️ Error Handling Patterns

### Defensive Programming

```python
class SafeStorageCalculator:
    """Calculator with defensive programming practices."""
    
    @staticmethod
    def safe_addition(*storages: Storage) -> Storage:
        """Add storages with overflow protection."""
        if not storages:
            return Storage(0, StorageUnit.BYTES)
        
        total = Storage(0, StorageUnit.BYTES)
        for storage in storages:
            if not isinstance(storage, Storage):
                raise TypeError(f"Expected Storage, got {type(storage)}")
            total += storage
        
        return total
    
    @staticmethod
    def safe_division(dividend: Storage, divisor: Union[Storage, float]) -> float:
        """Divide with zero-division protection."""
        if isinstance(divisor, Storage):
            divisor_value = divisor.convert_to_bytes()
        else:
            divisor_value = float(divisor)
        
        if divisor_value == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        
        return dividend.convert_to_bytes() / divisor_value
    
    @staticmethod
    def validate_storage_range(
        storage: Storage, 
        min_size: Storage, 
        max_size: Storage
    ) -> bool:
        """Validate storage is within acceptable range."""
        if min_size > max_size:
            raise ValueError("min_size cannot be greater than max_size")
        
        return min_size <= storage <= max_size
```

### Graceful Degradation

```python
def get_disk_usage(path: str) -> Dict[str, Optional[Storage]]:
    """Get disk usage with graceful degradation."""
    result = {
        'total': None,
        'used': None,
        'free': None,
        'error': None
    }
    
    try:
        # Try platform-optimized approach first
        platform_storage = Storage.get_platform_storage()
        total = platform_storage.get_size_from_path(path)
        result['total'] = total
        
        # Calculate other metrics if possible
        # ... additional logic
        
    except Exception as e:
        result['error'] = str(e)
        logging.warning(f"Could not get disk usage for {path}: {e}")
        
        # Fallback to basic approach
        try:
            import shutil
            total, used, free = shutil.disk_usage(path)
            result['total'] = Storage.parse_from_bytes(total)
            result['used'] = Storage.parse_from_bytes(used)
            result['free'] = Storage.parse_from_bytes(free)
        except Exception as fallback_error:
            result['error'] = f"Primary: {e}, Fallback: {fallback_error}"
    
    return result
```

## 🎯 Performance Optimization

### Efficient File Operations

```python
class EfficientFileAnalyzer:
    """File analyzer optimized for performance."""
    
    def __init__(self):
        # Cache platform storage instance
        self.platform_storage = Storage.get_platform_storage()
        self._size_cache = {}
    
    def analyze_directory_tree(self, root_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """Analyze directory tree efficiently."""
        results = {
            'total_size': Storage(0, StorageUnit.BYTES),
            'file_count': 0,
            'directory_count': 0,
            'file_sizes': []
        }
        
        for item_path in Path(root_path).rglob('*'):
            if item_path.is_file():
                # Use cache if enabled
                cache_key = str(item_path.absolute())
                if use_cache and cache_key in self._size_cache:
                    size = self._size_cache[cache_key]
                else:
                    size = self.platform_storage.get_size_from_path(item_path)
                    if use_cache:
                        self._size_cache[cache_key] = size
                
                results['total_size'] += size
                results['file_count'] += 1
                results['file_sizes'].append(size)
            
            elif item_path.is_dir():
                results['directory_count'] += 1
        
        return results
    
    def clear_cache(self):
        """Clear the size cache."""
        self._size_cache.clear()
```

### Batch Operations

```python
def process_files_efficiently(file_paths: List[str]) -> Dict[str, Storage]:
    """Process multiple files efficiently."""
    # Use single platform storage instance
    platform_storage = Storage.get_platform_storage()
    
    # Process in batches to manage memory
    batch_size = 1000
    results = {}
    
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i + batch_size]
        
        for file_path in batch:
            try:
                size = platform_storage.get_size_from_path(file_path)
                results[file_path] = size
            except (FileNotFoundError, PermissionError):
                # Skip inaccessible files
                continue
    
    return results
```

### Memory-Efficient Operations

```python
def calculate_large_directory_size(directory: str) -> Storage:
    """Calculate directory size without loading all paths into memory."""
    total_size = Storage(0, StorageUnit.BYTES)
    platform_storage = Storage.get_platform_storage()
    
    # Generator-based approach for memory efficiency
    def file_generator():
        for item_path in Path(directory).rglob('*'):
            if item_path.is_file():
                yield item_path
    
    # Process files one at a time
    for file_path in file_generator():
        try:
            size = platform_storage.get_size_from_path(file_path)
            total_size += size
        except (FileNotFoundError, PermissionError):
            continue  # Skip inaccessible files
    
    return total_size
```

## 🔧 Configuration Management

### Application Settings

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class StorageSettings:
    """Application storage settings."""
    default_unit_type: str = "binary"  # "binary", "decimal", "bits"
    display_precision: int = 2
    max_file_size: Storage = Storage(100, StorageUnit.MB)
    cache_enabled: bool = True
    platform_optimizations: bool = True
    
    def __post_init__(self):
        """Validate settings after initialization."""
        valid_unit_types = {"binary", "decimal", "bits"}
        if self.default_unit_type not in valid_unit_types:
            raise ValueError(f"Invalid unit type: {self.default_unit_type}")
        
        if self.display_precision < 0:
            raise ValueError("Display precision cannot be negative")

class StorageManager:
    """Centralized storage management with configuration."""
    
    def __init__(self, settings: Optional[StorageSettings] = None):
        self.settings = settings or StorageSettings()
        self._platform_storage = None
    
    @property
    def platform_storage(self):
        """Lazy-loaded platform storage."""
        if self._platform_storage is None:
            if self.settings.platform_optimizations:
                self._platform_storage = Storage.get_platform_storage()
            else:
                # Use basic storage implementation
                from bytesize.platform_storage import DefaultPlatformStorage
                self._platform_storage = DefaultPlatformStorage()
        return self._platform_storage
    
    def format_size(self, storage: Storage) -> str:
        """Format size according to settings."""
        scaled = storage.auto_scale(
            prefer_binary=(self.settings.default_unit_type == "binary")
        )
        return f"{scaled.value:.{self.settings.display_precision}f} {scaled.unit.name}"
    
    def validate_file_size(self, file_path: str) -> bool:
        """Validate file size against settings."""
        try:
            file_size = self.platform_storage.get_size_from_path(file_path)
            return file_size <= self.settings.max_file_size
        except (FileNotFoundError, PermissionError):
            return False
```

## 📊 Logging and Monitoring

### Structured Logging

```python
import logging
import json
from datetime import datetime

class StorageLogger:
    """Structured logging for storage operations."""
    
    def __init__(self, logger_name: str = "bytesize"):
        self.logger = logging.getLogger(logger_name)
        
    def log_file_operation(self, operation: str, file_path: str, 
                          size: Optional[Storage] = None, 
                          duration: Optional[float] = None,
                          error: Optional[str] = None):
        """Log file operation with structured data."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'file_path': file_path,
            'size_bytes': size.convert_to_bytes() if size else None,
            'size_readable': str(size.auto_scale()) if size else None,
            'duration_seconds': duration,
            'error': error,
            'success': error is None
        }
        
        if error:
            self.logger.error(f"Storage operation failed: {json.dumps(log_data)}")
        else:
            self.logger.info(f"Storage operation completed: {json.dumps(log_data)}")
    
    def log_performance_metrics(self, operation: str, file_count: int, 
                               total_size: Storage, duration: float):
        """Log performance metrics."""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'operation': operation,
            'file_count': file_count,
            'total_size_bytes': total_size.convert_to_bytes(),
            'total_size_readable': str(total_size.auto_scale()),
            'duration_seconds': duration,
            'files_per_second': file_count / duration if duration > 0 else 0,
            'bytes_per_second': total_size.convert_to_bytes() / duration if duration > 0 else 0
        }
        
        self.logger.info(f"Performance metrics: {json.dumps(metrics)}")

# Usage example
def monitored_file_scan(directory: str) -> Dict[str, Any]:
    """File scan with comprehensive monitoring."""
    logger = StorageLogger()
    start_time = time.time()
    
    try:
        total_size = Storage(0, StorageUnit.BYTES)
        file_count = 0
        
        for file_path in Path(directory).rglob('*'):
            if file_path.is_file():
                operation_start = time.time()
                try:
                    size = Storage.get_size_from_path(file_path)
                    total_size += size
                    file_count += 1
                    
                    operation_duration = time.time() - operation_start
                    logger.log_file_operation(
                        'scan', str(file_path), size, operation_duration
                    )
                    
                except Exception as e:
                    operation_duration = time.time() - operation_start
                    logger.log_file_operation(
                        'scan', str(file_path), None, operation_duration, str(e)
                    )
        
        total_duration = time.time() - start_time
        logger.log_performance_metrics(
            'directory_scan', file_count, total_size, total_duration
        )
        
        return {
            'total_size': total_size,
            'file_count': file_count,
            'duration': total_duration
        }
        
    except Exception as e:
        logger.logger.error(f"Directory scan failed: {e}")
        raise
```

## 🧪 Testing Best Practices

### Comprehensive Test Coverage

```python
import unittest
import tempfile
import os
from pathlib import Path

class TestStorageOperations(unittest.TestCase):
    """Comprehensive storage operation tests."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Create test files of various sizes
        sizes = [100, 1024, 1048576, 10485760]  # 100B, 1KB, 1MB, 10MB
        for i, size in enumerate(sizes):
            file_path = Path(self.temp_dir) / f"test_file_{i}.bin"
            with open(file_path, 'wb') as f:
                f.write(b'0' * size)
            self.test_files.append(file_path)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_file_size_accuracy(self):
        """Test that file sizes are reported accurately."""
        expected_sizes = [100, 1024, 1048576, 10485760]
        
        for file_path, expected_size in zip(self.test_files, expected_sizes):
            with self.subTest(file=file_path, expected=expected_size):
                storage = Storage.get_size_from_path(file_path)
                self.assertEqual(storage.convert_to_bytes(), expected_size)
    
    def test_error_handling(self):
        """Test error handling for various scenarios."""
        # Non-existent file
        with self.assertRaises(FileNotFoundError):
            Storage.get_size_from_path("nonexistent_file.txt")
        
        # Invalid parsing
        with self.assertRaises(ValueError):
            Storage.parse("invalid size")
        
        # Negative values
        with self.assertRaises(ValueError):
            Storage(-1, StorageUnit.BYTES)
    
    def test_arithmetic_operations(self):
        """Test arithmetic operations comprehensively."""
        storage1 = Storage(1, StorageUnit.GB)
        storage2 = Storage(500, StorageUnit.MB)
        
        # Addition
        result = storage1 + storage2
        self.assertAlmostEqual(result.convert_to_gb().value, 1.5, places=6)
        
        # Subtraction
        result = storage1 - storage2
        self.assertAlmostEqual(result.convert_to_mb().value, 500, places=6)
        
        # Multiplication
        result = storage1 * 2
        self.assertEqual(result.convert_to_gb().value, 2.0)
        
        # Division
        ratio = storage1 / storage2
        self.assertEqual(ratio, 2.0)
    
    def test_conversion_accuracy(self):
        """Test conversion accuracy between units."""
        # Test binary conversions
        storage = Storage(1, StorageUnit.GIB)
        self.assertEqual(storage.convert_to_mib().value, 1024.0)
        self.assertEqual(storage.convert_to_kib().value, 1048576.0)
        
        # Test decimal conversions
        storage = Storage(1, StorageUnit.GB)
        self.assertEqual(storage.convert_to_mb().value, 1000.0)
        self.assertEqual(storage.convert_to_kb().value, 1000000.0)
        
        # Test bit conversions
        storage = Storage(1, StorageUnit.BYTES)
        self.assertEqual(storage.convert_to_bits().value, 8.0)

# Performance benchmarks
class StoragePerformanceTests(unittest.TestCase):
    """Performance-focused tests."""
    
    def test_large_file_performance(self):
        """Test performance with large files."""
        import time
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write 100MB file
            temp_file.write(b'0' * (100 * 1024 * 1024))
            temp_file.flush()
            
            # Measure performance
            start_time = time.time()
            size = Storage.get_size_from_path(temp_file.name)
            duration = time.time() - start_time
            
            # Should complete in reasonable time (< 1 second)
            self.assertLess(duration, 1.0)
            self.assertEqual(size.convert_to_mb().value, 100.0)
            
            os.unlink(temp_file.name)
```

## 📈 Code Quality Guidelines

### Type Hints and Documentation

```python
from typing import List, Optional, Union, Dict, Any
from pathlib import Path

def analyze_storage_distribution(
    file_paths: List[Union[str, Path]],
    size_ranges: Optional[Dict[str, tuple]] = None
) -> Dict[str, Any]:
    """
    Analyze the distribution of file sizes across specified ranges.
    
    Args:
        file_paths: List of file paths to analyze
        size_ranges: Optional dict mapping range names to (min, max) tuples
                    in bytes. If None, uses default ranges.
    
    Returns:
        Dict containing:
        - 'distribution': Dict mapping range names to file counts
        - 'total_files': Total number of files processed
        - 'total_size': Total size of all files
        - 'average_size': Average file size
        - 'largest_file': Path and size of largest file
        - 'smallest_file': Path and size of smallest file
    
    Raises:
        ValueError: If size_ranges contains invalid ranges
        FileNotFoundError: If any file in file_paths doesn't exist
    
    Example:
        >>> files = ['file1.txt', 'file2.bin']
        >>> ranges = {'small': (0, 1024), 'large': (1024, float('inf'))}
        >>> result = analyze_storage_distribution(files, ranges)
        >>> print(result['distribution'])
        {'small': 1, 'large': 1}
    """
    if size_ranges is None:
        size_ranges = {
            'tiny': (0, 1024),                    # 0-1KB
            'small': (1024, 1024**2),            # 1KB-1MB
            'medium': (1024**2, 1024**3),        # 1MB-1GB
            'large': (1024**3, float('inf'))     # 1GB+
        }
    
    # Validate size ranges
    for name, (min_size, max_size) in size_ranges.items():
        if min_size < 0 or max_size <= min_size:
            raise ValueError(f"Invalid range '{name}': {min_size}-{max_size}")
    
    distribution = {name: 0 for name in size_ranges.keys()}
    file_sizes = []
    largest_file = None
    smallest_file = None
    
    for file_path in file_paths:
        size = Storage.get_size_from_path(file_path)
        size_bytes = size.convert_to_bytes()
        file_sizes.append((file_path, size))
        
        # Update largest/smallest tracking
        if largest_file is None or size > largest_file[1]:
            largest_file = (file_path, size)
        if smallest_file is None or size < smallest_file[1]:
            smallest_file = (file_path, size)
        
        # Categorize by size range
        for range_name, (min_size, max_size) in size_ranges.items():
            if min_size <= size_bytes < max_size:
                distribution[range_name] += 1
                break
    
    total_size = sum(size for _, size in file_sizes)
    average_size = total_size / len(file_sizes) if file_sizes else Storage(0, StorageUnit.BYTES)
    
    return {
        'distribution': distribution,
        'total_files': len(file_sizes),
        'total_size': total_size,
        'average_size': average_size,
        'largest_file': largest_file,
        'smallest_file': smallest_file
    }
```

---

These best practices will help you build robust, maintainable applications with Bytesize. Remember to adapt them to your specific use case and requirements.

[:material-arrow-left: Back to User Guide](index.md){ .md-button }
[:material-arrow-right: Examples](../examples/index.md){ .md-button .md-button--primary }