# Quick Start

This 5-minute tutorial will quickly introduce you to FileSizeLib's core features.

## 🎯 Goals

After completing this tutorial, you'll be able to:

- [x] Create Storage objects
- [x] Perform basic arithmetic operations
- [x] Use convenient conversion methods
- [x] Parse string-formatted storage sizes
- [x] Get file and directory sizes

## 💾 1. Creating Storage Objects

Storage (and its alias FileSizeLib) is FileSizeLib's core class, representing a storage size value:

```python
from filesizelib import Storage, StorageUnit, FileSizeLib

# Method 1: Using numeric values and unit enums
file_size = Storage(1.5, StorageUnit.GB)
photo_size = Storage(2.5, StorageUnit.MIB)

# Method 2: Using convenient string parsing
video_size = Storage.parse("4.2 GB")
music_size = Storage.parse("128 MB")

print(f"File size: {file_size}")    # 1.5 GB
print(f"Photo size: {photo_size}")  # 2.5 MIB
print(f"Video size: {video_size}")  # 4.2 GB
print(f"Music size: {music_size}")  # 128.0 MB
```

## 🧮 2. Arithmetic Operations

FileSizeLib supports intuitive arithmetic operations with smart unit preservation:

```python
# Addition: Smart unit preservation for same units
same_unit_1 = Storage(1, StorageUnit.GB)
same_unit_2 = Storage(2, StorageUnit.GB)
total_same = same_unit_1 + same_unit_2
print(f"Same unit result: {total_same}")  # 3 GB (preserves unit!)

# Different units still convert to bytes
total_mixed = video_size + music_size
print(f"Mixed units result: {total_mixed}")  # In bytes

# Subtraction: Calculate remaining space
disk_capacity = Storage.parse("500 GB")
remaining = disk_capacity - total_media
print(f"Remaining space: {remaining.auto_scale()}")  # 495.672 GB

# Multiplication: Batch calculations
photos_total = photo_size * 100  # 100 photos
print(f"100 photos total: {photos_total.auto_scale()}")  # 250.0 MIB

# Division: Calculate ratios or time
download_speed = Storage.parse("10 MB")  # per second
download_time = video_size / download_speed  # seconds
print(f"Download time: {download_time:.1f} seconds")  # 420.0 seconds
```

## 🔄 3. Unit Conversion

### Using Convenient Methods

```python
large_file = Storage(1.5, StorageUnit.GB)

# Binary unit conversions
print(f"Convert to MiB: {large_file.convert_to_mib()}")  # 1430.51 MiB
print(f"Convert to KiB: {large_file.convert_to_kib()}")  # 1465149.61 KiB

# Decimal unit conversions  
print(f"Convert to MB: {large_file.convert_to_mb()}")    # 1500.0 MB
print(f"Convert to KB: {large_file.convert_to_kb()}")    # 1500000.0 KB

# Bit unit conversions
print(f"Convert to bits: {large_file.convert_to_bits()}")  # 12000000000.0 BITS
print(f"Convert to megabits: {large_file.convert_to_megabits()}")  # 12000.0 MEGABITS
```

### Traditional Method

```python
# Using convert_to method
traditional = large_file.convert_to(StorageUnit.MIB)
print(f"Traditional conversion: {traditional}")  # 1430.51 MIB

# Both methods produce identical results
assert large_file.convert_to_mib() == traditional
```

## 📝 4. String Parsing

FileSizeLib supports multiple string formats with FileSizeLib alias:

```python
# Basic formats (Storage and FileSizeLib work identically)
size1 = Storage.parse("1.5 GB")
size2 = FileSizeLib.parse("2.5TB")         # FileSizeLib alias
size3 = Storage.parse("512 mb")         # Lowercase

# Different decimal separators
size4 = Storage.parse("1,5 GB")         # European format (comma)
size5 = Storage.parse("2.5 GB")         # US format (dot)

# Full unit names
size6 = Storage.parse("1 gigabyte")
size7 = Storage.parse("500 megabytes")
size8 = Storage.parse("1 kibibyte")

# Short forms
size9 = Storage.parse("1 g")            # Single letter
size10 = Storage.parse("500 m")

print("All formats parsed correctly!")
```

## 📁 5. File Operations

Get actual file and directory sizes:

```python
# Get single file size
try:
    file_size = Storage.get_size_from_path("README.md")
    print(f"README file size: {file_size.auto_scale()}")
except FileNotFoundError:
    print("File not found")

# Get directory total size (recursive calculation)
try:
    dir_size = Storage.get_size_from_path("./docs")
    print(f"Documentation directory size: {dir_size.auto_scale()}")
except FileNotFoundError:
    print("Directory not found")

# Use platform-specific optimizations
platform_storage = Storage.get_platform_storage()
info = platform_storage.get_platform_info()
print(f"Current platform: {info['platform']}")
print(f"Available optimizations: {info.get('api_optimization', 'None')}")
```

## 🎯 6. Smart Scaling

The auto_scale() method automatically selects the most appropriate unit:

```python
# Large file auto-scaling
huge_file = Storage(1500000000, StorageUnit.BYTES)
print(f"Smart scaling: {huge_file.auto_scale()}")  # 1.4 GIB

# Small files keep original unit
small_file = Storage(500, StorageUnit.BYTES)
print(f"Small file: {small_file.auto_scale()}")   # 500.0 BYTES

# Choose binary or decimal
binary_scale = huge_file.auto_scale(prefer_binary=True)   # 1.4 GIB
decimal_scale = huge_file.auto_scale(prefer_binary=False) # 1.5 GB
```

## 🎨 7. Decimal Precision Control

FileSizeLib provides configurable decimal precision without scientific notation:

```python
# Default precision (20 decimal places)
small_value = Storage(9.872019291e-05, StorageUnit.GIB)
print(f"Default: {small_value}")  # 0.00009872019291 GIB (no scientific notation!)

# Configure precision
Storage.set_decimal_precision(5)
print(f"5 decimals: {small_value}")  # 0.0001 GIB

# Get current precision
print(f"Current precision: {Storage.get_decimal_precision()}")  # 5

# Reset to default
Storage.set_decimal_precision(20)
```

## 🔗 8. Method Chaining

FileSizeLib supports elegant chaining operations:

```python
# Complex conversion chain
result = (Storage.parse("2 TB")
          .convert_to_gib()      # Convert to GiB
          .convert_to_mb()       # Convert to MB
          .auto_scale())         # Smart scaling

print(f"Chain conversion result: {result}")

# Use in arithmetic operations
total = (Storage.parse("1.5 GB").convert_to_mb() + 
         Storage.parse("500 MB"))
print(f"Total size: {total.auto_scale()}")
```

## 💡 Real-World Example

Let's look at a complete real-world application scenario showcasing new features:

```python
def analyze_media_library(photos_count, video_count):
    """Analyze media library storage requirements with FileSizeLib"""
    
    # Estimate sizes using FileSizeLib alias
    avg_photo = FileSizeLib.parse("2.5 MiB")
    avg_video = FileSizeLib.parse("500 MB")
    
    # Same-unit arithmetic preserves units
    if photos_count > 1:
        photos_total = avg_photo * photos_count  # Still in MiB
    else:
        photos_total = avg_photo
    
    videos_total = avg_video * video_count  # Still in MB
    
    # Mixed units will convert to bytes
    total_needed = photos_total + videos_total
    
    # Available storage
    available = Storage.parse("1 TB")
    remaining = available - total_needed
    
    # Analysis results
    print(f"📸 {photos_count} photos: {photos_total.auto_scale()}")
    print(f"🎬 {video_count} videos: {videos_total.auto_scale()}")
    print(f"📦 Total needed: {total_needed.auto_scale()}")
    print(f"💾 Available space: {available}")
    print(f"✅ Remaining space: {remaining.auto_scale()}")
    
    if remaining.convert_to_bytes() > 0:
        usage_percent = (total_needed / available) * 100
        print(f"📊 Usage: {usage_percent:.1f}%")
    else:
        print("⚠️  Insufficient storage space!")

# Run analysis
analyze_media_library(photos_count=1000, video_count=50)
```

## 🎉 Congratulations!

You've mastered FileSizeLib's core features! Now you can:

- ✅ Create and manipulate Storage/FileSizeLib objects
- ✅ Perform smart arithmetic with unit preservation
- ✅ Control decimal precision and eliminate scientific notation
- ✅ Use convenient conversion methods
- ✅ Parse multiple string formats
- ✅ Handle file and directory sizes
- ✅ Use smart scaling and method chaining

## 📚 Next Steps

<div class="grid cards" markdown>

-   [:material-school: **Basic Concepts**](concepts.md)
    
    Deep dive into storage units and design principles

-   [:material-book: **User Guide**](../user-guide/index.md)
    
    Learn more advanced features and best practices

-   [:material-lightbulb: **Examples**](../examples/index.md)
    
    See more real-world application scenarios

-   [:material-api: **API Reference**](../api/index.md)
    
    Explore complete method and property documentation

</div>