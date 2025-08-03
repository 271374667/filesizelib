# Decimal Precision in filesizelib

## Overview

Starting from version 0.11.4, filesizelib implements exact decimal precision using Python's `Decimal` module. This eliminates floating-point precision errors that could occur with values that cannot be exactly represented in IEEE 754 floating-point format.

## Problem Solved

### Before (Floating-Point Issues)
```python
from filesizelib import FileSize

# Floating-point precision errors
print(FileSize.parse('6.682 MB'))  # Output: 6.68200000000000038369 MB
```

### After (Exact Decimal Precision)
```python
from filesizelib import FileSize

# Exact decimal precision
print(FileSize.parse('6.682 MB'))  # Output: 6.682 MB
```

## Key Features

### 1. Dual Property Access

The Storage class provides two ways to access the stored value:

- **`value`**: Returns `float` for backward compatibility
- **`decimal_value`**: Returns `Decimal` for exact precision

```python
from filesizelib import Storage, StorageUnit
from decimal import Decimal

storage = Storage("6.682", StorageUnit.MB)

# Backward compatibility
print(storage.value)         # 6.682 (float)
print(type(storage.value))   # <class 'float'>

# Exact precision
print(storage.decimal_value)         # Decimal('6.682')
print(type(storage.decimal_value))   # <class 'decimal.Decimal'>
```

### 2. Exact Arithmetic Operations

All arithmetic operations maintain exact decimal precision:

```python
a = Storage("1.1", StorageUnit.GB)
b = Storage("2.2", StorageUnit.GB)
result = a + b

print(result)                    # 3.3 GB (exact)
print(result.decimal_value)      # Decimal('3.3')

# Floating-point equivalent would show precision errors
import decimal
float_result = 1.1 + 2.2
print(f"{float_result:.17f}")    # 3.30000000000000027
```

### 3. String Parsing Precision

String parsing maintains exact precision from input:

```python
# Various precision levels
test_cases = [
    "6.682 MB",
    "1.234567890123456 GB", 
    "0.001 TB",
    "9.999999999999999 KB"
]

for case in test_cases:
    storage = Storage.parse(case)
    print(f"{case} -> {storage}")
    # All values are displayed exactly as input
```

### 4. Configurable Display Precision

Control how many decimal places are shown in string representations:

```python
# Set precision for display
Storage.set_decimal_precision(5)

storage = Storage("1.23456789012345", StorageUnit.GB)
print(storage)  # 1.23457 GB (limited to 5 decimal places)

# Reset to high precision
Storage.set_decimal_precision(15)
print(storage)  # 1.234567890123450 GB
```

## Input Type Support

The Storage class accepts multiple input types:

```python
from decimal import Decimal

# Integer input
storage1 = Storage(1024, StorageUnit.BYTES)

# Float input (converted to Decimal internally)
storage2 = Storage(1.5, StorageUnit.MB)

# String input (parsed to Decimal)
storage3 = Storage("6.682 MB")

# Direct Decimal input (exact precision)
storage4 = Storage(Decimal("6.682"), StorageUnit.MB)

# All maintain exact precision in internal representation
```

## Backward Compatibility

### Existing Code Continues to Work

```python
# This code from version < 0.11.4 still works identically
storage = Storage(1024, StorageUnit.BYTES)
print(storage.value)          # 1024.0 (float)
print(storage.convert_to_gb().value)  # 0.000001024 (float)

# Arithmetic operations maintain compatibility
total = storage + Storage(512, StorageUnit.BYTES)
print(total.value)            # 1536.0 (float)
```

### New Precision-Critical Code

```python
# Use decimal_value for applications requiring exact precision
storage = Storage("6.682", StorageUnit.MB)

# Financial calculations, scientific measurements, etc.
exact_bytes = storage.convert_to_bytes()  # Returns Decimal
print(type(exact_bytes))      # <class 'decimal.Decimal'>

# For compatibility with float-expecting code
compatible_bytes = float(storage.convert_to_bytes())
print(type(compatible_bytes)) # <class 'float'>
```

## Method Return Types

### Updated Return Types

- **`convert_to_bytes()`**: Now returns `Decimal` (was `float`)
- **`parse_from_bytes()`**: Now accepts `Decimal` input

### Conversion Handling

```python
storage = Storage("1.5", StorageUnit.KB)

# New: Returns Decimal
bytes_decimal = storage.convert_to_bytes()
print(bytes_decimal)          # Decimal('1500')

# For float compatibility
bytes_float = float(storage.convert_to_bytes())
print(bytes_float)            # 1500.0

# Type checking
assert isinstance(bytes_decimal, Decimal)
assert isinstance(bytes_float, float)
```

## Use Cases

### When to Use `decimal_value`

- Financial calculations involving storage costs
- Scientific applications requiring exact measurements
- Data integrity verification
- Precise capacity planning
- Any context where rounding errors are unacceptable

### When to Use `value`

- Legacy code integration
- Performance-critical applications where small precision loss is acceptable
- Interfacing with APIs expecting float values
- General-purpose storage calculations

## Performance Considerations

- Decimal operations are slightly slower than float operations
- Memory usage is marginally higher due to Decimal storage
- String formatting maintains high performance
- Conversion methods are optimized for common use cases

## Migration Guide

### For Existing Users

No changes needed - all existing code continues to work identically.

### For New Users Requiring Precision

```python
# Replace this pattern:
storage = Storage.parse("6.682 MB")
bytes_value = storage.convert_to_bytes()  # Now returns Decimal

# With this for float compatibility:
bytes_value = float(storage.convert_to_bytes())

# Or embrace exact precision:
exact_bytes = storage.convert_to_bytes()  # Keep as Decimal
exact_decimal = storage.decimal_value     # Access exact value
```

## Examples

### Complete Precision Example

```python
from filesizelib import Storage, StorageUnit
from decimal import Decimal

# Create storage with exact precision
storage = Storage("6.682", StorageUnit.MB)

print("String representation:", storage)
print("Float value:", storage.value)
print("Decimal value:", storage.decimal_value)
print("Exact bytes:", storage.convert_to_bytes())
print("Float bytes:", float(storage.convert_to_bytes()))

# Arithmetic maintains precision
doubled = storage * 2
print("Doubled:", doubled)
print("Doubled decimal:", doubled.decimal_value)

# Output:
# String representation: 6.682 MB
# Float value: 6.682
# Decimal value: Decimal('6.682')
# Exact bytes: Decimal('6682000')
# Float bytes: 6682000.0
# Doubled: 13.364 MB
# Doubled decimal: Decimal('13.364')
```

### Financial Calculation Example

```python
from filesizelib import Storage
from decimal import Decimal

# Calculate storage costs with exact precision
storage_used = Storage("1.5", StorageUnit.TB)
cost_per_gb = Decimal("0.023")  # $0.023 per GB per month

# Convert to GB for cost calculation
gb_used = storage_used.convert_to_gb().decimal_value
monthly_cost = gb_used * cost_per_gb

print(f"Storage used: {storage_used}")
print(f"GB used: {gb_used}")
print(f"Monthly cost: ${monthly_cost}")

# Output:
# Storage used: 1.5 TB
# GB used: 1500
# Monthly cost: 34.5
```

This implementation ensures that filesizelib can serve as a reliable foundation library for applications requiring exact decimal precision while maintaining full backward compatibility.