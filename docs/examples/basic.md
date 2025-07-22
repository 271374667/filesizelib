# Basic Usage Examples

Simple, fundamental examples to get you started with FileSizeLib quickly.

## 🚀 Getting Started

### Creating Storage Objects

The most basic way to work with storage values:

```python
from filesizelib import Storage, StorageUnit, FileSizeLib

# Method 1: Constructor with value and unit (Storage and FileSizeLib are identical)
file_size = Storage(1.5, StorageUnit.GB)
memory = FileSizeLib(8, StorageUnit.GIB)  # Using alias
small_file = Storage(512, StorageUnit.BYTES)

print(f"File: {file_size}")      # File: 1.5 GB
print(f"Memory: {memory}")       # Memory: 8.0 GIB
print(f"Small: {small_file}")    # Small: 512 BYTES (integers don't show .0)
```

### Parsing from Strings

Convert human-readable strings into Storage objects:

```python
# Method 2: Parse from strings (recommended for user input)
download = Storage.parse("150 MB")
backup = FileSizeLib.parse("2.3 TB")  # Using alias
cache = Storage.parse("512 MiB")

print(f"Download: {download}")   # Download: 150 MB
print(f"Backup: {backup}")       # Backup: 2.3 TB
print(f"Cache: {cache}")         # Cache: 512 MIB

# Flexible parsing formats
flexible_examples = [
    Storage.parse("1.5GB"),        # No space
    FileSizeLib.parse("1,5 GB"),      # European decimal separator (using alias)
    Storage.parse("1024 kb"),      # Lowercase units
    FileSizeLib.parse("2 terabytes"), # Full unit names (using alias)
]

for storage in flexible_examples:
    print(storage)
```

### Working with Files

Get file and directory sizes:

```python
from pathlib import Path

# Method 3: From file system
readme_size = Storage.get_size_from_path("README.md")
docs_size = FileSizeLib.get_size_from_path("./docs")  # Using alias

print(f"README size: {readme_size.auto_scale()}")
print(f"Documentation size: {docs_size.auto_scale()}")

# Works with Path objects too
config_path = Path("config.json")
config_size = Storage.get_size_from_path(config_path)
print(f"Config size: {config_size}")
```

## 🧮 Smart Arithmetic

### Same-Unit vs Mixed-Unit Operations

FileSizeLib now features intelligent arithmetic that preserves units when both operands have the same unit:

```python
# Same-unit operations preserve the unit
same_unit_1 = Storage(1, StorageUnit.GB)
same_unit_2 = Storage(2, StorageUnit.GB)
total_same = same_unit_1 + same_unit_2
print(f"Same units: {total_same}")  # 3 GB (unit preserved!)

# Mixed-unit operations convert to bytes
mixed_1 = Storage(1, StorageUnit.GB)
mixed_2 = Storage(500, StorageUnit.MB)
total_mixed = mixed_1 + mixed_2
print(f"Mixed units: {total_mixed}")  # 1500000000 BYTES

# Use auto_scale for readability
print(f"Readable: {total_mixed.auto_scale()}")  # 1.4 GIB
```

### Addition and Subtraction

```python
# File size calculations
video_file = Storage(4.7, StorageUnit.GB)    # DVD movie
subtitle_file = Storage(50, StorageUnit.KB)  # Subtitle file

# Mixed units convert to bytes
total_download = video_file + subtitle_file
print(f"Total download: {total_download.auto_scale()}")  # 4.37 GIB

# Same-unit subtraction preserves unit
disk_capacity = Storage(500, StorageUnit.GB)
used_space = Storage(387, StorageUnit.GB)
free_space = disk_capacity - used_space
print(f"Free space: {free_space}")  # 113 GB (unit preserved!)
```

### Multiplication and Division

```python
# Calculate space needed for multiple files
single_photo = Storage(2.5, StorageUnit.MB)
photo_count = 100

total_photos = single_photo * photo_count
print(f"100 photos: {total_photos.auto_scale()}")  # 250.0 MB

# Calculate ratios
large_file = Storage(1, StorageUnit.GB)
small_file = Storage(50, StorageUnit.MB)

ratio = large_file / small_file
print(f"Large file is {ratio}x bigger")  # 20.0x bigger

# Split storage
per_user = total_photos / 4
print(f"Per user: {per_user}")  # 62.5 MB
```

## 🔄 Unit Conversions

### Traditional Conversion Method

```python
# Using convert_to() with target unit
storage = Storage(1024, StorageUnit.BYTES)

# Convert to different units
kib_size = storage.convert_to(StorageUnit.KIB)
kb_size = storage.convert_to(StorageUnit.KB)

print(f"In KiB: {kib_size}")  # 1.0 KIB (binary)
print(f"In KB: {kb_size}")   # 1.024 KB (decimal)
```

### Convenient Conversion Methods

```python
# Using convenient conversion methods (recommended)
large_file = Storage(1.5, StorageUnit.GB)

# Binary conversions
print(f"GiB: {large_file.convert_to_gib()}")  # 1.396 GiB
print(f"MiB: {large_file.convert_to_mib()}")  # 1430.5 MiB

# Decimal conversions  
print(f"MB: {large_file.convert_to_mb()}")    # 1500.0 MB
print(f"KB: {large_file.convert_to_kb()}")    # 1500000.0 KB

# Bit conversions
print(f"Bits: {large_file.convert_to_bits()}")      # 12000000000.0 BITS
print(f"Megabits: {large_file.convert_to_megabits()}") # 12000.0 MEGABITS
```

### Auto-Scaling for Readability

```python
# Auto-scale to most appropriate unit
huge_number = Storage(1536000000, StorageUnit.BYTES)

print(f"Raw: {huge_number}")                              # 1536000000.0 BYTES
print(f"Auto-scaled: {huge_number.auto_scale()}")         # 1.43 GIB
print(f"Prefer decimal: {huge_number.auto_scale(prefer_binary=False)}")  # 1.536 GB
```

## 🔍 Comparisons

### Basic Comparisons

```python
file1 = Storage(1, StorageUnit.GB)
file2 = Storage(1000, StorageUnit.MB)
file3 = Storage(1.5, StorageUnit.GB)

# Equality (handles unit differences automatically)
print(f"1 GB == 1000 MB: {file1 == file2}")  # True
print(f"1 GB != 1.5 GB: {file1 != file3}")   # True

# Size comparisons
print(f"1.5 GB > 1 GB: {file3 > file1}")     # True
print(f"1 GB < 1.5 GB: {file1 < file3}")     # True
print(f"1 GB >= 1000 MB: {file1 >= file2}")  # True
```

### Finding Largest/Smallest

```python
file_sizes = [
    Storage(150, StorageUnit.MB),
    Storage(1.2, StorageUnit.GB),
    Storage(800, StorageUnit.MB),
    Storage(2.1, StorageUnit.GIB)
]

# Find largest and smallest
largest = max(file_sizes)
smallest = min(file_sizes)

print(f"Largest: {largest.auto_scale()}")   # 2.1 GIB
print(f"Smallest: {smallest.auto_scale()}") # 150.0 MB
```

## 📊 Practical Examples

### Download Time Calculator

```python
def calculate_download_time(file_size_str: str, speed_str: str) -> str:
    """Calculate download time for a file."""
    file_size = Storage.parse(file_size_str)
    speed = FileSizeLib.parse(speed_str)  # Using alias
    
    # Convert to bits for bandwidth calculation
    file_bits = file_size.convert_to_bits()
    speed_bits = speed.convert_to_bits()
    
    # Calculate time in seconds
    seconds = file_bits.value / speed_bits.value
    
    # Format output
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    else:
        return f"{seconds/3600:.1f} hours"

# Examples
print(calculate_download_time("100 MB", "10 Megabits"))   # 80.0 seconds
print(calculate_download_time("4.7 GB", "50 Megabits"))   # 12.5 minutes
print(calculate_download_time("25 GB", "1 Gigabit"))      # 3.3 minutes
```

### Disk Space Monitor

```python
def check_disk_space(path: str, warning_threshold: str = "1 GB"):
    """Check if disk space is getting low."""
    try:
        # Get directory size (this is a simple example)
        used_space = FileSizeLib.get_size_from_path(path)  # Using alias
        threshold = Storage.parse(warning_threshold)
        
        print(f"Directory: {path}")
        print(f"Used space: {used_space.auto_scale()}")
        
        if used_space > threshold:
            print(f"⚠️  Warning: Directory is larger than {threshold}")
        else:
            print(f"✅ OK: Directory is under {threshold}")
            
    except FileNotFoundError:
        print(f"❌ Error: Path '{path}' not found")

# Usage
check_disk_space("./docs", "10 MB")
check_disk_space("./tests", "5 MB")
```

### File Size Categorizer

```python
def categorize_file_size(file_path: str) -> str:
    """Categorize a file by its size."""
    try:
        size = FileSizeLib.get_size_from_path(file_path)  # Using alias
        size_bytes = size.convert_to_bytes()
        
        if size_bytes < 1024:  # < 1 KB
            return "tiny"
        elif size_bytes < 1024**2:  # < 1 MB
            return "small"
        elif size_bytes < 1024**3:  # < 1 GB
            return "medium"
        else:  # >= 1 GB
            return "large"
            
    except FileNotFoundError:
        return "not_found"

# Example usage
files = ["README.md", "setup.py", "docs/index.md"]
for file_path in files:
    category = categorize_file_size(file_path)
    size = Storage.get_size_from_path(file_path) if category != "not_found" else "N/A"
    print(f"{file_path}: {category} ({size})")
```

### Data Usage Tracker

```python
class DataUsageTracker:
    """Track data usage over time."""
    
    def __init__(self, monthly_limit: str):
        self.monthly_limit = FileSizeLib.parse(monthly_limit)  # Using alias
        self.current_usage = Storage(0, StorageUnit.BYTES)
        self.daily_usage = []
    
    def add_usage(self, amount: str):
        """Add data usage."""
        usage = FileSizeLib.parse(amount)  # Using alias
        self.current_usage += usage
        self.daily_usage.append(usage)
        print(f"Added {usage}, total: {self.current_usage.auto_scale()}")
    
    def get_remaining(self) -> Storage:
        """Get remaining data allowance."""
        return self.monthly_limit - self.current_usage
    
    def get_usage_percentage(self) -> float:
        """Get usage as percentage of limit."""
        return (self.current_usage / self.monthly_limit) * 100
    
    def status_report(self):
        """Print usage status."""
        remaining = self.get_remaining()
        percentage = self.get_usage_percentage()
        
        print(f"\n📊 Data Usage Report")
        print(f"Limit: {self.monthly_limit}")
        print(f"Used: {self.current_usage.auto_scale()} ({percentage:.1f}%)")
        print(f"Remaining: {remaining.auto_scale()}")
        
        if percentage > 90:
            print("🚨 Warning: Approaching data limit!")
        elif percentage > 75:
            print("⚠️  Caution: 75% of data used")
        else:
            print("✅ Usage within normal range")

# Usage example
tracker = DataUsageTracker("50 GB")
tracker.add_usage("1.2 GB")  # Video streaming
tracker.add_usage("500 MB")  # Web browsing
tracker.add_usage("2.1 GB")  # Software download
tracker.status_report()
```

## 🎯 String Formatting & Decimal Precision

### Configurable Precision (No Scientific Notation)

```python
# FileSizeLib eliminates scientific notation by default
small_value = Storage(9.872019291e-05, StorageUnit.GIB)
print(f"No scientific notation: {small_value}")  # 0.00009872019291 GIB

# Configure global precision
Storage.set_decimal_precision(5)
print(f"5 decimals: {small_value}")  # 0.0001 GIB

# Check current precision
print(f"Current: {FileSizeLib.get_decimal_precision()}")  # 5

# Reset to default
Storage.set_decimal_precision(20)
```

### Display Formatting

```python
storage = Storage(1234.5678, StorageUnit.MB)

# Default string representation (uses configured precision)
print(f"Default: {storage}")           # 1234.5678 MB

# Custom precision using format
print(f"2 decimals: {storage:.2f}")    # 1234.57 MB
print(f"No decimals: {storage:.0f}")   # 1235 MB
print(f"4 decimals: {storage:.4f}")    # 1234.5678 MB

# Auto-scaled formatting
print(f"Auto-scaled: {storage.auto_scale()}")  # 1.17 GIB
```

### Repr for Debugging

```python
storage = Storage(1.5, StorageUnit.GB)

# String representation (for users)
print(str(storage))   # 1.5 GB

# Repr representation (for developers)
print(repr(storage))  # Storage(1.5, StorageUnit.GB)

# Both in one
print(f"Value: {storage!s}, Debug: {storage!r}")
```

## ✅ Error Handling Basics

### Common Error Scenarios

```python
# Handle parsing errors
def safe_parse(size_string: str) -> Storage:
    """Safely parse size string."""
    try:
        return FileSizeLib.parse(size_string)  # Using alias
    except ValueError as e:
        print(f"Parse error: {e}")
        return Storage(0, StorageUnit.BYTES)  # Default fallback

# Examples
print(safe_parse("1.5 GB"))    # 1.5 GB
print(safe_parse("invalid"))   # 0.0 BYTES (with error message)

# Handle file operation errors
def safe_file_size(file_path: str) -> Storage:
    """Safely get file size."""
    try:
        return FileSizeLib.get_size_from_path(file_path)  # Using alias
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return Storage(0, StorageUnit.BYTES)
    except PermissionError:
        print(f"Permission denied: {file_path}")
        return Storage(0, StorageUnit.BYTES)

# Handle arithmetic errors
def safe_divide(dividend: Storage, divisor: Storage) -> float:
    """Safely divide two storage values."""
    try:
        return dividend / divisor
    except ZeroDivisionError:
        print("Cannot divide by zero")
        return 0.0
```

## 🔗 Next Steps

Ready to explore more advanced features?

<div class="grid cards" markdown>

-   [:material-earth: **Real-World Use Cases**](real-world.md)
    
    Production-ready examples and patterns

-   [:material-book-open: **Best Practices**](../user-guide/best-practices.md)
    
    Optimization techniques and best practices

-   [:material-book-open: **API Reference**](../api/index.md)
    
    Complete documentation of all methods

</div>

---

These basic examples provide a solid foundation for using FileSizeLib. All examples are tested and ready to run!