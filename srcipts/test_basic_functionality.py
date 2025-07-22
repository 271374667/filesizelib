#!/usr/bin/env python3
"""
Basic functionality test for the bytesize library.

This script tests the core functionality of the bytesize library
to ensure everything works correctly across different platforms.
"""

import tempfile
from pathlib import Path
import sys
import os

# Add the bytesize package to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from byteunit import Storage, StorageUnit, ByteUnit
from byteunit.platform_storage import WindowsStorage, LinuxStorage, MacStorage


def test_basic_storage_operations():
    """Test basic storage operations."""
    print("Testing basic storage operations...")
    
    # Test initialization
    storage = Storage(1, StorageUnit.KIB)
    assert storage.value == 1.0
    assert storage.unit == StorageUnit.KIB
    print("✓ Storage initialization works")
    
    # Test conversion to bytes
    bytes_value = storage.convert_to_bytes()
    assert bytes_value == 1024.0
    print("✓ Conversion to bytes works")
    
    # Test parse_from_bytes
    storage_from_bytes = Storage.parse_from_bytes(1024)
    assert storage_from_bytes.value == 1024.0
    assert storage_from_bytes.unit == StorageUnit.BYTES
    print("✓ parse_from_bytes works")
    
    # Test conversion between units
    converted = storage.convert_to(StorageUnit.BYTES)
    assert converted.value == 1024.0
    assert converted.unit == StorageUnit.BYTES
    print("✓ Unit conversion works")
    
    # Test ByteUnit alias
    byte_unit = ByteUnit(1, StorageUnit.KIB)
    assert byte_unit.value == storage.value
    assert byte_unit.unit == storage.unit
    assert ByteUnit is Storage  # Same class
    print("✓ ByteUnit alias works")


def test_arithmetic_operations():
    """Test arithmetic operations."""
    print("\nTesting arithmetic operations...")
    
    s1 = Storage(1, StorageUnit.KIB)
    s2 = Storage(512, StorageUnit.BYTES)
    
    # Test addition
    total = s1 + s2
    assert total.convert_to_bytes() == 1536.0
    print("✓ Addition works")
    
    # Test subtraction
    diff = s1 - s2
    assert diff.convert_to_bytes() == 512.0
    print("✓ Subtraction works")
    
    # Test multiplication
    doubled = s1 * 2
    assert doubled.value == 2.0
    assert doubled.unit == StorageUnit.KIB
    print("✓ Multiplication works")
    
    # Test division
    halved = s1 / 2
    assert halved.value == 0.5
    assert halved.unit == StorageUnit.KIB
    print("✓ Division works")
    
    # Test division by storage (ratio)
    ratio = s1 / s2
    assert ratio == 2.0
    print("✓ Storage ratio calculation works")


def test_comparison_operations():
    """Test comparison operations."""
    print("\nTesting comparison operations...")
    
    s1 = Storage(1, StorageUnit.KIB)
    s2 = Storage(1024, StorageUnit.BYTES)
    s3 = Storage(2, StorageUnit.KIB)
    
    # Test equality
    assert s1 == s2
    print("✓ Equality comparison works")
    
    # Test less than
    assert s1 < s3
    print("✓ Less than comparison works")
    
    # Test greater than
    assert s3 > s1
    print("✓ Greater than comparison works")
    
    # Test less than or equal
    assert s1 <= s2
    assert s1 <= s3
    print("✓ Less than or equal comparison works")
    
    # Test greater than or equal
    assert s3 >= s1
    assert s1 >= s2
    print("✓ Greater than or equal comparison works")


def test_string_parsing():
    """Test string parsing functionality."""
    print("\nTesting string parsing...")
    
    # Test basic parsing
    parsed = Storage.parse("1.5 MB")
    assert parsed.value == 1.5
    assert parsed.unit == StorageUnit.MB
    print("✓ Basic string parsing works")
    
    # Test case insensitive
    parsed_case = Storage.parse("1.5 mb")
    assert parsed_case.value == 1.5
    assert parsed_case.unit == StorageUnit.MB
    print("✓ Case insensitive parsing works")
    
    # Test comma as decimal separator
    parsed_comma = Storage.parse("1,5 MB")
    assert parsed_comma.value == 1.5
    assert parsed_comma.unit == StorageUnit.MB
    print("✓ Comma decimal separator works")
    
    # Test no spaces
    parsed_no_space = Storage.parse("1.5MB")
    assert parsed_no_space.value == 1.5
    assert parsed_no_space.unit == StorageUnit.MB
    print("✓ No space parsing works")
    
    # Test default unit (bytes)
    parsed_default = Storage.parse("1024")
    assert parsed_default.value == 1024.0
    assert parsed_default.unit == StorageUnit.BYTES
    print("✓ Default unit (bytes) works")
    
    # Test various units
    test_cases = [
        ("1 KiB", 1.0, StorageUnit.KIB),
        ("2 MiB", 2.0, StorageUnit.MIB),
        ("3 GiB", 3.0, StorageUnit.GIB),
        ("1 KB", 1.0, StorageUnit.KB),
        ("2 MB", 2.0, StorageUnit.MB),
        ("3 GB", 3.0, StorageUnit.GB),
        ("8 bits", 8.0, StorageUnit.BITS),
    ]
    
    for test_string, expected_value, expected_unit in test_cases:
        parsed = Storage.parse(test_string)
        assert parsed.value == expected_value
        assert parsed.unit == expected_unit
    
    print("✓ Various unit parsing works")


def test_string_representations():
    """Test string representations."""
    print("\nTesting string representations...")
    
    storage = Storage(1.5, StorageUnit.MB)
    
    # Test __str__
    str_repr = str(storage)
    assert str_repr == "1.5 MB"
    print("✓ String representation works")
    
    # Test __repr__
    repr_str = repr(storage)
    assert "Storage" in repr_str
    assert "1.5" in repr_str
    assert "MB" in repr_str
    print("✓ Repr representation works")
    
    # Test formatting
    formatted = f"{storage:.2f}"
    assert formatted == "1.50 MB"
    print("✓ String formatting works")


def test_auto_scaling():
    """Test auto scaling functionality."""
    print("\nTesting auto scaling...")
    
    # Test binary scaling
    storage_bytes = Storage(1536, StorageUnit.BYTES)
    scaled_binary = storage_bytes.auto_scale(prefer_binary=True)
    assert scaled_binary.value == 1.5
    assert scaled_binary.unit == StorageUnit.KIB
    print("✓ Binary auto scaling works")
    
    # Test decimal scaling
    storage_large = Storage(1500000, StorageUnit.BYTES)
    scaled_decimal = storage_large.auto_scale(prefer_binary=False)
    assert scaled_decimal.value == 1.5
    assert scaled_decimal.unit == StorageUnit.MB
    print("✓ Decimal auto scaling works")


def test_file_operations():
    """Test file size operations."""
    print("\nTesting file operations...")
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Hello, World!" * 100)  # Write some data
        temp_file_path = temp_file.name
    
    try:
        # Test file size retrieval
        file_size = Storage.get_size_from_path(temp_file_path)
        assert file_size.value > 0
        assert file_size.unit == StorageUnit.BYTES
        print("✓ File size retrieval works")
        
        # Test with Path object
        file_size_path = Storage.get_size_from_path(Path(temp_file_path))
        assert file_size == file_size_path
        print("✓ Path object support works")
        
    finally:
        # Clean up
        os.unlink(temp_file_path)
    
    # Test directory size (use current directory)
    current_dir = Path(".")
    dir_size = Storage.get_size_from_path(current_dir)
    assert dir_size.value > 0
    print("✓ Directory size retrieval works")


def test_platform_storage():
    """Test platform-specific storage."""
    print("\nTesting platform storage...")
    
    # Test platform detection
    try:
        platform_storage = Storage.get_platform_storage()
        assert platform_storage is not None
        print("✓ Platform storage detection works")
        
        # Test platform info
        info = platform_storage.get_platform_info()
        assert isinstance(info, dict)
        assert 'platform' in info
        print("✓ Platform info retrieval works")
        
    except ValueError as e:
        # Unsupported platform
        print(f"✓ Platform detection handled unsupported platform: {e}")


def test_error_handling():
    """Test error handling."""
    print("\nTesting error handling...")
    
    # Test negative values
    try:
        Storage(-1, StorageUnit.BYTES)
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ Negative value error handling works")
    
    # Test invalid types
    try:
        Storage("invalid", StorageUnit.BYTES)
        assert False, "Should have raised TypeError"
    except TypeError:
        print("✓ Invalid type error handling works")
    
    # Test invalid string parsing
    try:
        Storage.parse("invalid format")
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ Invalid string parsing error handling works")
    
    # Test division by zero
    try:
        storage = Storage(1, StorageUnit.KIB)
        result = storage / 0
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError:
        print("✓ Division by zero error handling works")
    
    # Test subtraction resulting in negative
    try:
        s1 = Storage(1, StorageUnit.BYTES)
        s2 = Storage(2, StorageUnit.BYTES)
        result = s1 - s2
        assert False, "Should have raised ValueError"
    except ValueError:
        print("✓ Negative subtraction error handling works")


def test_edge_cases():
    """Test edge cases."""
    print("\nTesting edge cases...")
    
    # Test zero values
    zero_storage = Storage(0, StorageUnit.BYTES)
    assert zero_storage.convert_to_bytes() == 0.0
    print("✓ Zero value handling works")
    
    # Test very large values
    large_storage = Storage(1e15, StorageUnit.BYTES)
    assert large_storage.convert_to_bytes() == 1e15
    print("✓ Large value handling works")
    
    # Test very small values
    small_storage = Storage(0.001, StorageUnit.BYTES)
    assert small_storage.convert_to_bytes() == 0.001
    print("✓ Small value handling works")
    
    # Test bit operations
    bits_storage = Storage(8, StorageUnit.BITS)
    assert bits_storage.convert_to_bytes() == 1.0
    print("✓ Bit operations work")


def run_all_tests():
    """Run all tests."""
    print("Running bytesize library tests...\n")
    
    try:
        test_basic_storage_operations()
        test_arithmetic_operations()
        test_comparison_operations()
        test_string_parsing()
        test_string_representations()
        test_auto_scaling()
        test_file_operations()
        test_platform_storage()
        test_error_handling()
        test_edge_cases()
        
        print("\n🎉 All tests passed! The bytesize library is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)