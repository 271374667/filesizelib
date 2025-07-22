<center><h1>📏 ByteUnit</h1>

A unified storage unit library for Python with cross-platform file size support
</center>

## 🚀 What is ByteUnit?

ByteUnit is a powerful and intuitive Python storage unit library that makes it easy to handle calculations, conversions, and operations with various storage sizes. Whether you're working with file sizes, network bandwidth, or storage capacity, ByteUnit makes these tasks simple and elegant.

## ✨ Core Features

<div class="grid cards" markdown>

-   :material-scale-balance:{ .lg .middle } **🧮 Full Arithmetic Support**

    ---

    Support for addition, subtraction, multiplication, and division with automatic unit conversion

    [:octicons-arrow-right-24: View arithmetic operations](api/storage.md#arithmetic-operations)

-   :material-format-text:{ .lg .middle } **📝 Flexible String Parsing**

    ---

    Parse multiple string formats with case-insensitive support and various separators

    [:octicons-arrow-right-24: Learn string parsing](api/storage.md#class-methods)

-   :material-harddisk:{ .lg .middle } **🔗 Cross-Platform File Operations**

    ---

    Get file and directory sizes using pathlib with platform-specific optimizations

    [:octicons-arrow-right-24: File operations guide](api/storage.md#file-operations)

-   :material-lightning-bolt:{ .lg .middle } **⚡ Platform Optimizations**

    ---

    Platform-specific performance optimizations for Windows, Linux, and macOS

    [:octicons-arrow-right-24: Platform support details](api/platform-storage.md)

-   :material-shield-check:{ .lg .middle } **🔒 Type Safety**

    ---

    Complete type annotations for better IDE support and code safety

    [:octicons-arrow-right-24: API Reference](api/index.md)

-   :material-package-variant:{ .lg .middle } **🎯 Zero Dependencies**

    ---

    Uses only Python standard library, no external dependencies required

    [:octicons-arrow-right-24: Quick Start](getting-started/quick-start.md)

</div>

## 🎯 Quick Example

```python
from byteunit import Storage, StorageUnit, ByteUnit

# Create storage values
file_size = Storage(1.5, StorageUnit.GB)
backup_size = Storage.parse("2.5 TB")

# Arithmetic operations
total = file_size + backup_size
print(f"Total size: {total.auto_scale()}")  # Output: Total size: 2.502 TB

# Convenient conversion methods
print(f"File size (MB): {file_size.convert_to_mb()}")  # 1500.0 MB
print(f"Backup size (GiB): {backup_size.convert_to_gib()}")  # 2328.31 GiB

# File operations
dir_size = Storage.get_size_from_path("/path/to/directory")
print(f"Directory size: {dir_size.auto_scale()}")
```

## 🛠️ Supported Unit Types

```mermaid
graph TD
    A[Storage Units] --> B[Binary Units]
    A --> C[Decimal Units]
    A --> D[Bit Units]
    
    B --> B1[BYTES]
    B --> B2[KiB, MiB, GiB]
    B --> B3[TiB, PiB, EiB]
    B --> B4[ZiB, YiB]
    
    C --> C1[KB, MB, GB]
    C --> C2[TB, PB, EB]
    C --> C3[ZB, YB]
    
    D --> D1[BITS]
    D --> D2[KILOBITS]
    D --> D3[MEGABITS]
    D --> D4[GIGABITS]
    D --> D5[TERABITS]
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
```

## 🌟 Why Choose ByteUnit?

### Simple to Use
ByteUnit's API is designed to be intuitive and follows Python best practices. You can accomplish complex storage unit operations with minimal code.

### Performance Optimized
Built-in platform-specific optimizations ensure optimal performance across different operating systems.

### Type Safe
Complete type annotation support makes your code more reliable and provides better IDE support.

### Zero Dependencies
No third-party dependencies reduce project complexity and potential security risks.

## 🔄 Architecture Overview

```mermaid
graph LR
    A[User Code] --> B[Storage Class]
    B --> C[StorageUnit Enum]
    B --> D[Arithmetic Ops]
    B --> E[Conversion Methods]
    B --> F[String Parsing]
    B --> G[File Operations]
    
    G --> H[PlatformStorage]
    H --> I[WindowsStorage]
    H --> J[LinuxStorage]
    H --> K[MacStorage]
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
    style E fill:#fce4ec
    style F fill:#f1f8e9
    style G fill:#e0f2f1
    style H fill:#e8eaf6
```

## 📚 Next Steps

<div class="grid cards" markdown>

-   [:material-rocket-launch: **Quick Start**](getting-started/quick-start.md)
    
    Learn ByteUnit basics in 5 minutes

-   [:material-book-open-page-variant: **User Guide**](user-guide/index.md)
    
    Deep dive into all features and best practices

-   [:material-code-tags: **API Reference**](api/index.md)
    
    Complete API documentation and method reference

-   [:material-lightbulb-on: **Examples**](examples/index.md)
    
    Real-world scenarios and code examples

</div>

---

**Start your ByteUnit journey** [Install Now :material-download:](getting-started/installation.md){ .md-button .md-button--primary }