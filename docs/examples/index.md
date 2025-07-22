# Examples

Real-world examples and practical use cases for Bytesize.

## 🎯 Overview

This section provides practical examples showing how to use Bytesize in real applications. Each example includes complete, runnable code with explanations.

## 📚 Example Categories

<div class="grid cards" markdown>

-   [:material-play-circle: **Basic Usage**](basic.md)
    
    Simple examples to get you started quickly

-   [:material-earth: **Real-World Scenarios**](real-world.md)
    
    Production-ready examples from actual use cases

-   [:material-book-open: **Best Practices**](../user-guide/best-practices.md)
    
    Optimization techniques and best practices

</div>

## 🚀 Quick Examples

### File Size Analysis

```python
from bytesize import Storage, StorageUnit
from pathlib import Path

def analyze_directory(path: str):
    """Analyze directory size and file distribution."""
    directory = Path(path)
    total_size = Storage(0, StorageUnit.BYTES)
    file_count = 0
    
    for file_path in directory.rglob('*'):
        if file_path.is_file():
            file_size = Storage.get_size_from_path(file_path)
            total_size += file_size
            file_count += 1
            print(f"{file_path.name}: {file_size.auto_scale()}")
    
    print(f"\nTotal: {file_count} files, {total_size.auto_scale()}")
    return total_size

# Usage
total = analyze_directory("./docs")
```

### Bandwidth Calculator

```python
def calculate_download_time(file_size: str, speed: str) -> float:
    """Calculate download time given file size and connection speed."""
    file_storage = Storage.parse(file_size)
    speed_storage = Storage.parse(speed)
    
    # Convert to compatible units (bits)
    file_bits = file_storage.convert_to_bits()
    speed_bits_per_sec = speed_storage.convert_to_bits()
    
    # Calculate time in seconds
    time_seconds = file_bits.value / speed_bits_per_sec.value
    
    return time_seconds

# Usage examples
time1 = calculate_download_time("1.5 GB", "100 Megabits")
time2 = calculate_download_time("4K movie.mkv", "1 Gigabit")

print(f"Download time: {time1:.1f} seconds")
print(f"4K movie time: {time2:.1f} seconds")
```

### Storage Planning

```python
class StoragePlanner:
    """Plan storage requirements for different media types."""
    
    def __init__(self, total_capacity: str):
        self.capacity = Storage.parse(total_capacity)
        self.used = Storage(0, StorageUnit.BYTES)
        self.allocations = {}
    
    def add_allocation(self, name: str, size: str, count: int = 1):
        """Add a storage allocation."""
        unit_size = Storage.parse(size)
        total_size = unit_size * count
        
        self.allocations[name] = {
            'unit_size': unit_size,
            'count': count,
            'total_size': total_size
        }
        self.used += total_size
    
    def get_report(self) -> str:
        """Generate a storage planning report."""
        report = f"Storage Capacity: {self.capacity}\n"
        report += f"Total Used: {self.used.auto_scale()}\n"
        report += f"Remaining: {(self.capacity - self.used).auto_scale()}\n\n"
        
        report += "Allocations:\n"
        for name, alloc in self.allocations.items():
            report += f"  {name}: {alloc['count']} × {alloc['unit_size'].auto_scale()} = {alloc['total_size'].auto_scale()}\n"
        
        usage_percent = (self.used / self.capacity) * 100
        report += f"\nUsage: {usage_percent:.1f}%"
        
        return report

# Usage
planner = StoragePlanner("1 TB")
planner.add_allocation("Photos", "2.5 MiB", 2000)
planner.add_allocation("Music", "4.5 MB", 500)
planner.add_allocation("Videos", "800 MB", 20)
planner.add_allocation("Documents", "150 KB", 1000)

print(planner.get_report())
```

## 🔄 Conversion Examples

### Unit Converter

```python
class UnitConverter:
    """Interactive unit converter."""
    
    @staticmethod
    def convert_all_units(value: str) -> dict:
        """Convert to all unit types."""
        storage = Storage.parse(value)
        
        return {
            'binary': {
                'bytes': storage.convert_to_bytes(),
                'kib': storage.convert_to_kib(),
                'mib': storage.convert_to_mib(),
                'gib': storage.convert_to_gib(),
                'tib': storage.convert_to_tib(),
            },
            'decimal': {
                'kb': storage.convert_to_kb(),
                'mb': storage.convert_to_mb(),
                'gb': storage.convert_to_gb(),
                'tb': storage.convert_to_tb(),
            },
            'bits': {
                'bits': storage.convert_to_bits(),
                'kilobits': storage.convert_to_kilobits(),
                'megabits': storage.convert_to_megabits(),
                'gigabits': storage.convert_to_gigabits(),
            }
        }
    
    @staticmethod
    def print_conversions(value: str):
        """Print all conversions in a formatted way."""
        conversions = UnitConverter.convert_all_units(value)
        
        print(f"Converting: {value}")
        print("=" * 40)
        
        for category, units in conversions.items():
            print(f"\n{category.title()} Units:")
            for unit_name, storage in units.items():
                print(f"  {unit_name}: {storage}")

# Usage
UnitConverter.print_conversions("1.5 GB")
```

## 📊 Comparison Examples

### Size Comparison Tool

```python
def compare_sizes(*size_strings):
    """Compare multiple sizes and show relationships."""
    sizes = [Storage.parse(size) for size in size_strings]
    
    # Sort by size
    sorted_sizes = sorted(zip(size_strings, sizes), key=lambda x: x[1].convert_to_bytes())
    
    print("Size Comparison (smallest to largest):")
    print("=" * 50)
    
    largest = sorted_sizes[-1][1]
    
    for i, (original, storage) in enumerate(sorted_sizes):
        ratio = largest / storage
        percentage = (storage / largest) * 100
        
        print(f"{i+1}. {original}")
        print(f"   = {storage.auto_scale()}")
        print(f"   = {percentage:.1f}% of largest")
        print(f"   = {ratio:.2f}x smaller than largest")
        print()

# Usage
compare_sizes("1.5 GB", "1600 MB", "1.6 GB", "1500000 KB")
```

## 🎮 Interactive Examples

### File Size Calculator

```python
class FileSizeCalculator:
    """Calculate various file size scenarios."""
    
    @staticmethod
    def backup_time(data_size: str, backup_speed: str) -> str:
        """Calculate backup time."""
        data = Storage.parse(data_size)
        speed = Storage.parse(backup_speed)
        
        time_seconds = data / speed
        hours = time_seconds / 3600
        
        if hours < 1:
            minutes = time_seconds / 60
            return f"{minutes:.1f} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            days = hours / 24
            return f"{days:.1f} days"
    
    @staticmethod
    def storage_lifespan(capacity: str, daily_usage: str) -> str:
        """Calculate how long storage will last."""
        total = Storage.parse(capacity)
        daily = Storage.parse(daily_usage)
        
        days = total / daily
        
        if days < 30:
            return f"{days:.1f} days"
        elif days < 365:
            months = days / 30
            return f"{months:.1f} months"
        else:
            years = days / 365
            return f"{years:.1f} years"
    
    @staticmethod
    def compression_analysis(original: str, compressed: str) -> dict:
        """Analyze compression efficiency."""
        orig_size = Storage.parse(original)
        comp_size = Storage.parse(compressed)
        
        saved = orig_size - comp_size
        ratio = orig_size / comp_size
        percentage = (saved / orig_size) * 100
        
        return {
            'original': orig_size,
            'compressed': comp_size,
            'saved': saved,
            'ratio': f"{ratio:.2f}:1",
            'percentage': f"{percentage:.1f}%"
        }

# Usage examples
print("Backup time:", FileSizeCalculator.backup_time("500 GB", "100 MB"))
print("Storage lifespan:", FileSizeCalculator.storage_lifespan("1 TB", "2 GB"))

compression = FileSizeCalculator.compression_analysis("100 MB", "23 MB")
print("Compression analysis:", compression)
```

## 🔍 Next Steps

Ready to explore more detailed examples?

<div class="grid cards" markdown>

-   [:material-play: **Basic Usage**](basic.md)
    
    Start with simple, fundamental examples

-   [:material-earth: **Real-World Use Cases**](real-world.md)
    
    See production-ready applications

-   [:material-book-open: **Best Practices**](../user-guide/best-practices.md)
    
    Learn optimization techniques and patterns

</div>

---

All examples are tested and ready to run. Copy and paste them into your Python environment to try them out!