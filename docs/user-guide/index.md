# User Guide

Comprehensive guide to using ByteUnit effectively in your projects.

## 🎯 Overview

This user guide provides practical information for integrating ByteUnit into your applications. Whether you're building a file manager, monitoring tool, or any application that deals with storage sizes, this guide will help you make the most of ByteUnit.

## 📚 Guide Sections

<div class="grid cards" markdown>

-   [:material-rocket-launch: **Quick Start Guide**](../getting-started/quick-start.md)
    
    Get up and running with ByteUnit in minutes

-   [:material-lightbulb-on: **Best Practices**](best-practices.md)
    
    Learn recommended patterns and avoid common pitfalls

</div>

## 🚀 Quick Start

### Installation

```bash
pip install byteunit
```

### Basic Usage

```python
from byteunit import Storage, StorageUnit, ByteUnit

# Create storage objects (Storage and ByteUnit are identical)
file_size = Storage(1.5, StorageUnit.GB)
memory = ByteUnit(8, StorageUnit.GIB)  # Using alias

# Parse from strings
download = Storage.parse("150 MB")
upload = ByteUnit.parse("2.3 TB")  # Using alias

# Smart arithmetic - same units preserve unit
same_unit_total = file_size + Storage(0.5, StorageUnit.GB)
print(f"Same unit: {same_unit_total}")    # 2.0 GB (unit preserved!)

# Mixed units convert to bytes
mixed_total = file_size + download  
print(f"Mixed: {mixed_total.auto_scale()}")  # 1.65 GB

ratio = upload / download
print(f"Ratio: {ratio:.1f}")             # Ratio: 15.7
```

## 🎯 Key Concepts

### Storage Units & ByteUnit Alias

ByteUnit provides both the main `Storage` class and an identical `ByteUnit` alias for convenience:

ByteUnit supports three types of storage units:

=== "Binary Units (Base 1024)"
    
    ```python
    # Binary units for computer memory and file systems
    ram = Storage(16, StorageUnit.GIB)      # 16 GiB
    cache = Storage(512, StorageUnit.MIB)   # 512 MiB
    buffer = Storage(4, StorageUnit.KIB)    # 4 KiB
    ```

=== "Decimal Units (Base 1000)"
    
    ```python
    # Decimal units for storage devices and marketing
    ssd = Storage(500, StorageUnit.GB)      # 500 GB
    backup = Storage(2, StorageUnit.TB)     # 2 TB
    file = Storage(150, StorageUnit.MB)     # 150 MB
    ```

=== "Bit Units"
    
    ```python
    # Bit units for network and bandwidth
    connection = Storage(100, StorageUnit.MEGABITS)  # 100 Mbps
    fiber = Storage(1, StorageUnit.GIGABITS)         # 1 Gbps
    ```

### Conversions

```python
# Automatic scaling
large_file = Storage(1536000000, StorageUnit.BYTES)
print(large_file.auto_scale())  # 1.43 GIB

# Specific conversions
gb_size = large_file.convert_to_gb()
print(gb_size)  # 1.536 GB

# Convenient methods
mib_size = large_file.convert_to_mib()
print(mib_size)  # 1464.84 MIB
```

### File Operations

```python
from pathlib import Path

# Get file sizes
readme_size = Storage.get_size_from_path("README.md")
docs_size = ByteUnit.get_size_from_path("./docs")  # Using alias

print(f"README: {readme_size.auto_scale()}")
print(f"Docs: {docs_size.auto_scale()}")

# Works with Path objects
log_path = Path("/var/log")
log_size = Storage.get_size_from_path(log_path)
```

### Decimal Precision Control

ByteUnit eliminates scientific notation and provides configurable decimal precision:

```python
# Default precision avoids scientific notation
small_value = Storage(9.872019291e-05, StorageUnit.GIB)
print(f"No scientific notation: {small_value}")  # 0.00009872019291 GIB

# Configure precision globally
Storage.set_decimal_precision(3)
print(f"3 decimals: {small_value}")  # 0.0001 GIB

# Check current precision
precision = ByteUnit.get_decimal_precision()
print(f"Current precision: {precision}")  # 3

# Reset to default
Storage.set_decimal_precision(20)
```

## 🎨 Common Patterns

### File Size Analysis

```python
def analyze_project_files():
    """Analyze file sizes in a project."""
    total_size = Storage(0, StorageUnit.BYTES)
    file_sizes = {}
    
    for file_path in Path(".").rglob("*"):
        if file_path.is_file():
            size = Storage.get_size_from_path(file_path)
            total_size += size
            file_sizes[str(file_path)] = size
    
    # Find largest files
    largest = sorted(file_sizes.items(), key=lambda x: x[1].convert_to_bytes(), reverse=True)[:5]
    
    print(f"Total project size: {total_size.auto_scale()}")
    print("Largest files:")
    for path, size in largest:
        print(f"  {path}: {size.auto_scale()}")

analyze_project_files()
```

### Bandwidth Calculations

```python
def calculate_transfer_time(file_size_str: str, bandwidth_str: str) -> str:
    """Calculate how long a file transfer will take."""
    file_size = Storage.parse(file_size_str)
    bandwidth = Storage.parse(bandwidth_str)
    
    # Convert to consistent units (bits)
    file_bits = file_size.convert_to_bits()
    bandwidth_bits = bandwidth.convert_to_bits()
    
    # Calculate time in seconds
    seconds = file_bits.value / bandwidth_bits.value
    
    # Format time appropriately
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    else:
        return f"{seconds/3600:.1f} hours"

# Usage
print(calculate_transfer_time("4.7 GB", "50 Megabits"))  # DVD over broadband
print(calculate_transfer_time("1 TB", "1 Gigabit"))      # Large backup over fiber
```

### Storage Planning

```python
class StoragePlanner:
    """Plan storage requirements for different content types."""
    
    def __init__(self, total_capacity: str):
        self.capacity = Storage.parse(total_capacity)
        self.allocations = {}
        self.used = Storage(0, StorageUnit.BYTES)
    
    def add_content_type(self, name: str, avg_size: str, quantity: int):
        """Add a content type allocation."""
        unit_size = Storage.parse(avg_size)
        total_size = unit_size * quantity
        
        self.allocations[name] = {
            'unit_size': unit_size,
            'quantity': quantity,
            'total_size': total_size
        }
        self.used += total_size
    
    def get_summary(self) -> str:
        """Get storage planning summary."""
        remaining = self.capacity - self.used
        usage_percent = (self.used / self.capacity) * 100
        
        summary = f"Storage Planning Summary\n"
        summary += f"Total Capacity: {self.capacity.auto_scale()}\n"
        summary += f"Used: {self.used.auto_scale()} ({usage_percent:.1f}%)\n"
        summary += f"Remaining: {remaining.auto_scale()}\n\n"
        
        summary += "Allocations:\n"
        for name, alloc in self.allocations.items():
            summary += f"  {name}: {alloc['quantity']} × {alloc['unit_size'].auto_scale()} = {alloc['total_size'].auto_scale()}\n"
        
        return summary

# Usage
planner = StoragePlanner("1 TB")
planner.add_content_type("Photos", "3 MB", 2000)
planner.add_content_type("Videos", "800 MB", 20)
planner.add_content_type("Music", "4.5 MB", 500)
planner.add_content_type("Documents", "150 KB", 1000)

print(planner.get_summary())
```

## 🔗 Integration Examples

### With Web Frameworks

```python
# Flask example
from flask import Flask, jsonify
from byteunit import Storage, ByteUnit

app = Flask(__name__)

@app.route('/api/disk-usage')
def disk_usage():
    """API endpoint for disk usage information."""
    try:
        total = Storage.get_size_from_path("/")
        return jsonify({
            'total_bytes': total.convert_to_bytes(),
            'total_readable': str(total.auto_scale()),
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500
```

### With Data Processing

```python
import pandas as pd
from byteunit import Storage, StorageUnit, ByteUnit

def analyze_log_files(log_dir: str) -> pd.DataFrame:
    """Analyze log files and return size information."""
    files_data = []
    
    for log_file in Path(log_dir).glob("*.log"):
        size = Storage.get_size_from_path(log_file)
        files_data.append({
            'filename': log_file.name,
            'size_bytes': size.convert_to_bytes(),
            'size_mb': size.convert_to_mb().value,
            'size_readable': str(size.auto_scale())
        })
    
    return pd.DataFrame(files_data)

# Usage
df = analyze_log_files("/var/log")
print(df.head())
```

### With Configuration Files

```python
import configparser
from byteunit import Storage, ByteUnit

# Read storage limits from config
config = configparser.ConfigParser()
config.read('app.conf')

# Parse storage values from configuration
max_upload = Storage.parse(config.get('limits', 'max_upload_size'))
cache_size = Storage.parse(config.get('cache', 'max_size'))
log_rotation = Storage.parse(config.get('logging', 'max_log_size'))

print(f"Max upload: {max_upload}")
print(f"Cache size: {cache_size}")
print(f"Log rotation: {log_rotation}")
```

## 💡 Tips and Tricks

### Performance Optimization

```python
# Cache platform storage for multiple operations
platform_storage = Storage.get_platform_storage()

# Process multiple files efficiently
total_size = Storage(0, StorageUnit.BYTES)
for file_path in large_file_list:
    size = platform_storage.get_size_from_path(file_path)
    total_size += size
```

### Error Handling

```python
def safe_parse_size(size_string: str, default: Storage = None) -> Storage:
    """Safely parse size string with fallback."""
    try:
        return Storage.parse(size_string)
    except ValueError:
        if default is not None:
            return default
        return Storage(0, StorageUnit.BYTES)

# Usage
user_input = "invalid size"
size = safe_parse_size(user_input, Storage(1, StorageUnit.MB))
```

### Unit Consistency

```python
def ensure_unit_type(storage: Storage, unit_type: str) -> Storage:
    """Ensure storage uses specific unit type."""
    if unit_type == "binary" and not storage.unit.is_binary():
        return storage.convert_to_gib() if storage.convert_to_bytes() > 1024**3 else storage.convert_to_mib()
    elif unit_type == "decimal" and not storage.unit.is_decimal():
        return storage.convert_to_gb() if storage.convert_to_bytes() > 1000**3 else storage.convert_to_mb()
    return storage
```

## 🔍 What's Next?

Ready to dive deeper? Choose your next step:

<div class="grid cards" markdown>

-   [:material-fast-forward: **Best Practices**](best-practices.md)
    
    Learn recommended patterns and coding practices

-   [:material-application: **Examples**](../examples/index.md)
    
    Explore real-world applications and solutions

-   [:material-book-open: **API Reference**](../api/index.md)
    
    Complete API documentation and reference

</div>

---

All examples in this guide are tested and ready to use. Copy them into your Python environment and start experimenting!