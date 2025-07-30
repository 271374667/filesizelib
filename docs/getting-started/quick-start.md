# Quick Start

This 5-minute tutorial will quickly introduce you to FileSizeLib's core features, including the latest enhancements.

## 🎯 Goals

After completing this tutorial, you'll be able to:

- [x] Create Storage objects using multiple approaches
- [x] Use the new FileSize alias and direct string initialization
- [x] Access conversions via properties (storage.MB, storage.GiB, etc.)
- [x] Use int() and float() magic methods for byte operations
- [x] Understand the differences between .value, int(), and float()
- [x] Perform basic arithmetic operations
- [x] Use convenient conversion methods
- [x] Parse string-formatted storage sizes
- [x] Get file and directory sizes

## 💾 1. Creating Storage Objects

Storage has multiple aliases and initialization methods - choose what feels most natural!

```python
from filesizelib import Storage, StorageUnit, FileSizeLib, FileSize

# 🆕 NEW: Multiple aliases - all functionally identical
storage_obj = Storage("1.5 GB")           # Main class
filesizelib_obj = FileSizeLib("1.5 GB")   # Original alias
filesize_obj = FileSize("1.5 GB")         # 🆕 New alias

print(storage_obj == filesizelib_obj == filesize_obj)  # True

# Method 1: 🆕 NEW - Direct string initialization (recommended!)
file_size = Storage("1.5 GB")             # No .parse() needed!
photo_size = FileSize("2.5 MiB")          # Works with any alias
document_size = Storage("500")             # No unit = bytes

# Method 2: Traditional numeric values and unit enums
video_size = Storage(4.2, StorageUnit.GB) # Classic approach
music_size = FileSizeLib(128, StorageUnit.MB)

# Method 3: Traditional string parsing (still works!)
legacy_size = Storage.parse("1 TB")       # .parse() method

print(f"File size: {file_size}")          # 1.5 GB
print(f"Photo size: {photo_size}")        # 2.5 MIB
print(f"Document: {document_size}")       # 500 BYTES
print(f"Video size: {video_size}")        # 4.2 GB
print(f"Music size: {music_size}")        # 128.0 MB
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

### 🆕 NEW: Property-Based Conversions (Recommended!)

The easiest way to convert units - just access them as properties:

```python
large_file = Storage("1.5 GB")  # Using string initialization

# 🆕 Binary unit properties - instant access!
print(f"MiB: {large_file.MIB}")    # 1430.51 MiB
print(f"KiB: {large_file.KIB}")    # 1465149.61 KiB
print(f"GiB: {large_file.GIB}")    # 1.396 GiB

# 🆕 Decimal unit properties  
print(f"MB: {large_file.MB}")      # 1500.0 MB
print(f"KB: {large_file.KB}")      # 1500000.0 KB
print(f"TB: {large_file.TB}")      # 0.0015 TB

# 🆕 Bit unit properties
print(f"Bits: {large_file.BITS}")             # 12000000000.0 BITS
print(f"Megabits: {large_file.MEGABITS}")     # 12000.0 MEGABITS
print(f"Gigabits: {large_file.GIGABITS}")     # 12.0 GIGABITS

# 🆕 Property chaining works too!
result = Storage("1 GiB").MIB.KIB
print(f"Chained conversion: {result}")        # 1048576.0 KIB
```

### Traditional Methods (Still Available)

```python
# Using convert_to_* methods
print(f"Method call: {large_file.convert_to_mib()}")  # 1430.51 MiB

# Using convert_to method
traditional = large_file.convert_to(StorageUnit.MIB)
print(f"Traditional: {traditional}")                  # 1430.51 MIB

# All approaches produce identical results
assert large_file.MIB == large_file.convert_to_mib() == traditional
```

### 🔍 Understanding .value vs int() vs float()

**Critical difference** - these return different values:

```python
size = Storage("1.5 GB")

# .value - Returns original value in original unit
print(f"size.value = {size.value}")         # 1.5 (GB value)
print(f"size.unit = {size.unit}")           # StorageUnit.GB

# int() - Returns total bytes as integer  
print(f"int(size) = {int(size)}")           # 1500000000 (bytes)

# float() - Returns total bytes as float
print(f"float(size) = {float(size)}")       # 1500000000.0 (bytes)

# Properties return Storage objects (not raw numbers)
print(f"size.MB = {size.MB}")               # 1500.0 MB (Storage object)
print(f"int(size.MB) = {int(size.MB)}")     # 1500000000 (still bytes!)
```

## 📝 4. String Parsing

🆕 **Major improvement**: Direct string initialization makes parsing effortless!

```python
# 🆕 NEW: Direct initialization (recommended approach)
size1 = Storage("1.5 GB")              # No .parse() needed!
size2 = FileSize("2.5TB")              # Works with all aliases
size3 = FileSizeLib("512 mb")          # Case insensitive

# 🆕 Different decimal separators work directly
size4 = Storage("1,5 GB")              # European format (comma)
size5 = FileSize("2.5 GB")             # US format (dot)

# 🆕 Full unit names in constructors
size6 = Storage("1 gigabyte")
size7 = FileSize("500 megabytes")  
size8 = Storage("1 kibibyte")

# 🆕 Short forms work directly
size9 = Storage("1 g")                 # Single letter
size10 = FileSize("500 m")

# 🆕 No unit defaults to bytes
size11 = Storage("1024")               # Automatically BYTES

print("All formats parsed correctly using direct initialization!")

# Traditional .parse() method still works
legacy1 = Storage.parse("1.5 GB")     # Old way
legacy2 = FileSizeLib.parse("2TB")    # Still supported

# Both approaches are identical
assert Storage("1 GB") == Storage.parse("1 GB")
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

Complete scenario showcasing all the new features together:

```python
def analyze_media_library(photos_count, video_count):
    """🆕 Enhanced media library analysis using new features"""
    
    # 🆕 Direct string initialization - no .parse() needed!
    avg_photo = FileSize("2.5 MiB")         # Using FileSize alias
    avg_video = Storage("500 MB")           # Using Storage with strings
    
    # Same-unit arithmetic preserves units
    photos_total = avg_photo * photos_count if photos_count > 1 else avg_photo
    videos_total = avg_video * video_count
    
    # Mixed units convert to bytes
    total_needed = photos_total + videos_total
    
    # 🆕 Available storage using direct initialization
    available = Storage("1 TB")
    remaining = available - total_needed
    
    # 🆕 Analysis results using new features
    print(f"📸 {photos_count} photos: {photos_total.auto_scale()}")
    print(f"🎬 {video_count} videos: {videos_total.auto_scale()}")
    print(f"📦 Total needed: {total_needed.auto_scale()}")
    
    # 🆕 Property-based conversions for detailed breakdown
    print(f"📊 Total needed breakdown:")
    print(f"   GB: {total_needed.GB}")
    print(f"   GiB: {total_needed.GIB}")
    print(f"   Bytes: {int(total_needed):,}")    # 🆕 int() for exact bytes
    
    print(f"💾 Available: {available}")
    print(f"✅ Remaining: {remaining.auto_scale()}")
    
    # 🆕 Usage calculation using float() for precision
    if int(remaining) > 0:                        # 🆕 int() for byte check
        usage_percent = (float(total_needed) / float(available)) * 100
        print(f"📊 Usage: {usage_percent:.1f}%")
        
        # 🆕 Different unit representations using properties
        print(f"📈 Usage in different units:")
        print(f"   {total_needed.GB.value:.1f} / {available.GB.value:.1f} GB")
        print(f"   {total_needed.GIB.value:.1f} / {available.GIB.value:.1f} GiB")
    else:
        print("⚠️  Insufficient storage space!")
    
    # 🆕 Return detailed info using all new features
    return {
        'total_needed': total_needed,
        'total_bytes': int(total_needed),         # 🆕 Exact byte count
        'total_gb': total_needed.GB.value,       # 🆕 GB value only
        'available': available,
        'remaining': remaining,
        'usage_percent': (float(total_needed) / float(available)) * 100
    }

# Run enhanced analysis
result = analyze_media_library(photos_count=1000, video_count=50)

# 🆕 Use the returned data with new features
print(f"\n🔍 Advanced analysis:")
print(f"Exact byte count: {result['total_bytes']:,}")
print(f"GB value only: {result['total_gb']:.2f}")
print(f"Usage percentage: {result['usage_percent']:.2f}%")
```

## 🎉 Congratulations!

You've mastered FileSizeLib's core features, including all the latest enhancements! Now you can:

- ✅ Create objects using multiple aliases (Storage, FileSizeLib, FileSize)
- ✅ 🆕 Use direct string initialization - `Storage("1.5 GB")`
- ✅ 🆕 Access any unit as a property - `storage.MB`, `storage.GiB`, etc.
- ✅ 🆕 Use int() and float() for precise byte operations
- ✅ 🆕 Understand the critical differences between .value, int(), and float()
- ✅ Perform smart arithmetic with unit preservation
- ✅ Control decimal precision and eliminate scientific notation
- ✅ Use convenient conversion methods (both old and new)
- ✅ Parse multiple string formats with flexible approaches
- ✅ Handle file and directory sizes
- ✅ Use smart scaling and method chaining
- ✅ 🆕 Chain property conversions for complex operations

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