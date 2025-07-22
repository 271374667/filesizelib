"""
Comprehensive tests for the Storage class.

This module tests all functionality of the Storage class including
initialization, arithmetic operations, comparisons, string parsing,
file operations, and utility methods.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Any, List, Tuple, Union

from byteunit import Storage, StorageUnit


class TestStorageInitialization:
    """Test Storage class initialization and basic properties."""
    
    def test_basic_initialization(self):
        """Test basic Storage initialization."""
        storage = Storage(1, StorageUnit.KIB)
        assert storage.value == 1.0
        assert storage.unit == StorageUnit.KIB
    
    def test_initialization_with_int(self):
        """Test Storage initialization with integer value."""
        storage = Storage(1024, StorageUnit.BYTES)
        assert storage.value == 1024.0
        assert storage.unit == StorageUnit.BYTES
    
    def test_initialization_with_float(self):
        """Test Storage initialization with float value."""
        storage = Storage(1.5, StorageUnit.MB)
        assert storage.value == 1.5
        assert storage.unit == StorageUnit.MB
    
    def test_initialization_with_zero(self):
        """Test Storage initialization with zero value."""
        storage = Storage(0, StorageUnit.BYTES)
        assert storage.value == 0.0
        assert storage.unit == StorageUnit.BYTES
    
    @pytest.mark.parametrize("value,unit", [
        (1, StorageUnit.BYTES),
        (1.5, StorageUnit.KIB),
        (1024, StorageUnit.MB),
        (0, StorageUnit.GIB),
        (999.999, StorageUnit.TB),
    ])
    def test_initialization_parametrized(self, value: Union[int, float], unit: StorageUnit):
        """Test Storage initialization with various values and units."""
        storage = Storage(value, unit)
        assert storage.value == float(value)
        assert storage.unit == unit
    
    def test_initialization_error_negative_value(self):
        """Test that negative values raise ValueError."""
        with pytest.raises(ValueError, match="Storage value cannot be negative"):
            Storage(-1, StorageUnit.BYTES)
    
    def test_initialization_error_invalid_value_type(self):
        """Test that invalid value type raises TypeError."""
        with pytest.raises(TypeError, match="Value must be a number"):
            Storage("invalid", StorageUnit.BYTES)
    
    def test_initialization_error_invalid_unit_type(self):
        """Test that invalid unit type raises TypeError."""
        with pytest.raises(TypeError, match="Unit must be a StorageUnit"):
            Storage(1, "invalid")


class TestStorageConversion:
    """Test Storage conversion methods."""
    
    def test_convert_to_bytes_basic(self):
        """Test basic conversion to bytes."""
        storage = Storage(1, StorageUnit.KIB)
        assert storage.convert_to_bytes() == 1024.0
    
    @pytest.mark.parametrize("value,unit,expected_bytes", [
        (1, StorageUnit.BYTES, 1.0),
        (1, StorageUnit.KIB, 1024.0),
        (1, StorageUnit.MIB, 1048576.0),
        (1, StorageUnit.KB, 1000.0),
        (1, StorageUnit.MB, 1000000.0),
        (8, StorageUnit.BITS, 1.0),
        (1000, StorageUnit.KILOBITS, 125000.0),
        (0, StorageUnit.GIB, 0.0),
        (2.5, StorageUnit.KIB, 2560.0),
    ])
    def test_convert_to_bytes_parametrized(self, value: float, unit: StorageUnit, expected_bytes: float):
        """Test conversion to bytes with various units."""
        storage = Storage(value, unit)
        assert storage.convert_to_bytes() == expected_bytes
    
    def test_convert_to_different_unit(self):
        """Test conversion to a different unit."""
        storage = Storage(1024, StorageUnit.BYTES)
        converted = storage.convert_to(StorageUnit.KIB)
        assert converted.value == 1.0
        assert converted.unit == StorageUnit.KIB
    
    @pytest.mark.parametrize("source_value,source_unit,target_unit,expected_value", [
        (1024, StorageUnit.BYTES, StorageUnit.KIB, 1.0),
        (1, StorageUnit.KIB, StorageUnit.BYTES, 1024.0),
        (1, StorageUnit.MB, StorageUnit.KB, 1000.0),
        (1000, StorageUnit.KB, StorageUnit.MB, 1.0),
        (8, StorageUnit.BITS, StorageUnit.BYTES, 1.0),
        (1, StorageUnit.BYTES, StorageUnit.BITS, 8.0),
        (2, StorageUnit.KIB, StorageUnit.MIB, 2.0/1024),
    ])
    def test_convert_to_parametrized(self, source_value: float, source_unit: StorageUnit, 
                                   target_unit: StorageUnit, expected_value: float):
        """Test conversion between different units."""
        storage = Storage(source_value, source_unit)
        converted = storage.convert_to(target_unit)
        assert abs(converted.value - expected_value) < 1e-10
        assert converted.unit == target_unit
    
    def test_parse_from_bytes_basic(self):
        """Test basic parse_from_bytes functionality."""
        storage = Storage.parse_from_bytes(1024)
        assert storage.value == 1024.0
        assert storage.unit == StorageUnit.BYTES
    
    @pytest.mark.parametrize("bytes_value", [
        0, 1, 1024, 1048576, 999.5, 123.456789
    ])
    def test_parse_from_bytes_parametrized(self, bytes_value: float):
        """Test parse_from_bytes with various values."""
        storage = Storage.parse_from_bytes(bytes_value)
        assert storage.value == float(bytes_value)
        assert storage.unit == StorageUnit.BYTES
        assert storage.convert_to_bytes() == float(bytes_value)


class TestStorageArithmetic:
    """Test Storage arithmetic operations."""
    
    def test_addition_basic(self):
        """Test basic addition."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(512, StorageUnit.BYTES)
        result = s1 + s2
        
        assert result.convert_to_bytes() == 1536.0
        assert result.unit == StorageUnit.BYTES
    
    def test_addition_same_units(self):
        """Test addition with same units."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(1, StorageUnit.KIB)
        result = s1 + s2
        
        assert result.convert_to_bytes() == 2048.0
    
    def test_addition_with_zero(self):
        """Test addition with zero."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(0, StorageUnit.BYTES)
        result = s1 + s2
        
        assert result.convert_to_bytes() == 1024.0
    
    def test_subtraction_basic(self):
        """Test basic subtraction."""
        s1 = Storage(2, StorageUnit.KIB)
        s2 = Storage(512, StorageUnit.BYTES)
        result = s1 - s2
        
        assert result.convert_to_bytes() == 1536.0
    
    def test_subtraction_same_values(self):
        """Test subtraction resulting in zero."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(1024, StorageUnit.BYTES)
        result = s1 - s2
        
        assert result.convert_to_bytes() == 0.0
    
    def test_subtraction_negative_result_error(self):
        """Test that subtraction resulting in negative raises ValueError."""
        s1 = Storage(512, StorageUnit.BYTES)
        s2 = Storage(1, StorageUnit.KIB)
        
        with pytest.raises(ValueError, match="Storage subtraction result cannot be negative"):
            s1 - s2
    
    def test_multiplication_basic(self):
        """Test basic multiplication."""
        storage = Storage(1, StorageUnit.KIB)
        result = storage * 2
        
        assert result.value == 2.0
        assert result.unit == StorageUnit.KIB
    
    def test_multiplication_by_float(self):
        """Test multiplication by float."""
        storage = Storage(2, StorageUnit.KIB)
        result = storage * 0.5
        
        assert result.value == 1.0
        assert result.unit == StorageUnit.KIB
    
    def test_multiplication_by_zero(self):
        """Test multiplication by zero."""
        storage = Storage(1, StorageUnit.KIB)
        result = storage * 0
        
        assert result.value == 0.0
        assert result.unit == StorageUnit.KIB
    
    def test_right_multiplication(self):
        """Test right multiplication (factor * storage)."""
        storage = Storage(1, StorageUnit.KIB)
        result = 2 * storage
        
        assert result.value == 2.0
        assert result.unit == StorageUnit.KIB
    
    def test_multiplication_negative_factor_error(self):
        """Test that multiplication by negative factor raises ValueError."""
        storage = Storage(1, StorageUnit.KIB)
        
        with pytest.raises(ValueError, match="Cannot multiply storage by negative factor"):
            storage * -1
    
    def test_division_by_number_basic(self):
        """Test basic division by number."""
        storage = Storage(2, StorageUnit.KIB)
        result = storage / 2
        
        assert result.value == 1.0
        assert result.unit == StorageUnit.KIB
    
    def test_division_by_float(self):
        """Test division by float."""
        storage = Storage(1, StorageUnit.KIB)
        result = storage / 0.5
        
        assert result.value == 2.0
        assert result.unit == StorageUnit.KIB
    
    def test_division_by_storage(self):
        """Test division by storage (ratio)."""
        s1 = Storage(2, StorageUnit.KIB)
        s2 = Storage(1, StorageUnit.KIB)
        result = s1 / s2
        
        assert result == 2.0
        assert isinstance(result, float)
    
    def test_division_by_storage_different_units(self):
        """Test division by storage with different units."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(512, StorageUnit.BYTES)
        result = s1 / s2
        
        assert result == 2.0
    
    def test_division_by_zero_error(self):
        """Test that division by zero raises ZeroDivisionError."""
        storage = Storage(1, StorageUnit.KIB)
        
        with pytest.raises(ZeroDivisionError, match="Cannot divide storage by zero"):
            storage / 0
    
    def test_division_by_zero_storage_error(self):
        """Test that division by zero storage raises ZeroDivisionError."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(0, StorageUnit.BYTES)
        
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero storage"):
            s1 / s2
    
    def test_floor_division(self):
        """Test floor division."""
        storage = Storage(5, StorageUnit.KIB)
        result = storage // 2
        
        assert result.value == 2.0
        assert result.unit == StorageUnit.KIB
    
    def test_modulo_operation(self):
        """Test modulo operation."""
        storage = Storage(5, StorageUnit.KIB)
        result = storage % 2
        
        assert result.value == 1.0
        assert result.unit == StorageUnit.KIB
    
    @pytest.mark.parametrize("s1,s2,operation,expected", [
        (Storage(1, StorageUnit.KIB), Storage(512, StorageUnit.BYTES), "add", 1536.0),
        (Storage(2, StorageUnit.KIB), Storage(512, StorageUnit.BYTES), "sub", 1536.0),
        (Storage(1, StorageUnit.KIB), 2, "mul", Storage(2, StorageUnit.KIB)),
        (Storage(2, StorageUnit.KIB), 2, "truediv", Storage(1, StorageUnit.KIB)),
        (Storage(2, StorageUnit.KIB), Storage(1, StorageUnit.KIB), "truediv", 2.0),
    ])
    def test_arithmetic_parametrized(self, s1: Storage, s2: Union[Storage, float], 
                                   operation: str, expected: Union[Storage, float]):
        """Test arithmetic operations with parametrized data."""
        if operation == "add":
            result = s1 + s2
            assert result.convert_to_bytes() == expected
        elif operation == "sub":
            result = s1 - s2
            assert result.convert_to_bytes() == expected
        elif operation == "mul":
            result = s1 * s2
            assert result.value == expected.value
            assert result.unit == expected.unit
        elif operation == "truediv":
            result = s1 / s2
            if isinstance(expected, Storage):
                assert result.value == expected.value
                assert result.unit == expected.unit
            else:
                assert result == expected


class TestStorageComparisons:
    """Test Storage comparison operations."""
    
    def test_equality_same_units(self):
        """Test equality with same units."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(1, StorageUnit.KIB)
        assert s1 == s2
    
    def test_equality_different_units(self):
        """Test equality with different units."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(1024, StorageUnit.BYTES)
        assert s1 == s2
    
    def test_equality_different_values(self):
        """Test equality with different values."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(2, StorageUnit.KIB)
        assert not (s1 == s2)
    
    def test_equality_with_non_storage(self):
        """Test equality with non-Storage object."""
        storage = Storage(1, StorageUnit.KIB)
        assert not (storage == "not a storage")
        assert not (storage == 1024)
    
    def test_less_than(self):
        """Test less than comparison."""
        s1 = Storage(512, StorageUnit.BYTES)
        s2 = Storage(1, StorageUnit.KIB)
        assert s1 < s2
        assert not (s2 < s1)
    
    def test_less_than_equal_values(self):
        """Test less than with equal values."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(1024, StorageUnit.BYTES)
        assert not (s1 < s2)
        assert not (s2 < s1)
    
    def test_less_than_or_equal(self):
        """Test less than or equal comparison."""
        s1 = Storage(512, StorageUnit.BYTES)
        s2 = Storage(1, StorageUnit.KIB)
        s3 = Storage(1024, StorageUnit.BYTES)
        
        assert s1 <= s2
        assert s2 <= s3
        assert s3 <= s2  # Equal values
    
    def test_greater_than(self):
        """Test greater than comparison."""
        s1 = Storage(2, StorageUnit.KIB)
        s2 = Storage(1, StorageUnit.KIB)
        assert s1 > s2
        assert not (s2 > s1)
    
    def test_greater_than_or_equal(self):
        """Test greater than or equal comparison."""
        s1 = Storage(2, StorageUnit.KIB)
        s2 = Storage(1, StorageUnit.KIB)
        s3 = Storage(1024, StorageUnit.BYTES)
        
        assert s1 >= s2
        assert s2 >= s3  # Equal values
        assert s3 >= s2  # Equal values
    
    def test_not_equal(self):
        """Test not equal comparison."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(2, StorageUnit.KIB)
        s3 = Storage(1024, StorageUnit.BYTES)
        
        assert s1 != s2
        assert not (s1 != s3)  # Equal values
    
    @pytest.mark.parametrize("s1,s2,comparison,expected", [
        (Storage(1, StorageUnit.KIB), Storage(1024, StorageUnit.BYTES), "eq", True),
        (Storage(1, StorageUnit.KIB), Storage(2, StorageUnit.KIB), "eq", False),
        (Storage(512, StorageUnit.BYTES), Storage(1, StorageUnit.KIB), "lt", True),
        (Storage(1, StorageUnit.KIB), Storage(512, StorageUnit.BYTES), "lt", False),
        (Storage(512, StorageUnit.BYTES), Storage(1, StorageUnit.KIB), "le", True),
        (Storage(1, StorageUnit.KIB), Storage(1024, StorageUnit.BYTES), "le", True),
        (Storage(2, StorageUnit.KIB), Storage(1, StorageUnit.KIB), "gt", True),
        (Storage(1, StorageUnit.KIB), Storage(2, StorageUnit.KIB), "gt", False),
        (Storage(2, StorageUnit.KIB), Storage(1, StorageUnit.KIB), "ge", True),
        (Storage(1, StorageUnit.KIB), Storage(1024, StorageUnit.BYTES), "ge", True),
    ])
    def test_comparisons_parametrized(self, s1: Storage, s2: Storage, comparison: str, expected: bool):
        """Test comparison operations with parametrized data."""
        if comparison == "eq":
            assert (s1 == s2) == expected
        elif comparison == "lt":
            assert (s1 < s2) == expected
        elif comparison == "le":
            assert (s1 <= s2) == expected
        elif comparison == "gt":
            assert (s1 > s2) == expected
        elif comparison == "ge":
            assert (s1 >= s2) == expected


class TestStorageStringParsing:
    """Test Storage string parsing functionality."""
    
    def test_basic_parsing(self):
        """Test basic string parsing."""
        storage = Storage.parse("1.5 MB")
        assert storage.value == 1.5
        assert storage.unit == StorageUnit.MB
    
    def test_case_insensitive_parsing(self):
        """Test case insensitive parsing."""
        test_cases = [
            "1.5 mb",
            "1.5 Mb",
            "1.5 mB",
            "1.5 MB",
        ]
        
        for case in test_cases:
            storage = Storage.parse(case)
            assert storage.value == 1.5
            assert storage.unit == StorageUnit.MB
    
    def test_comma_decimal_separator(self):
        """Test parsing with comma as decimal separator."""
        storage = Storage.parse("1,5 MB")
        assert storage.value == 1.5
        assert storage.unit == StorageUnit.MB
    
    def test_no_space_parsing(self):
        """Test parsing without space between value and unit."""
        storage = Storage.parse("1.5MB")
        assert storage.value == 1.5
        assert storage.unit == StorageUnit.MB
    
    def test_default_unit_bytes(self):
        """Test parsing with default unit (bytes)."""
        storage = Storage.parse("1024")
        assert storage.value == 1024.0
        assert storage.unit == StorageUnit.BYTES
    
    def test_custom_default_unit(self):
        """Test parsing with custom default unit."""
        storage = Storage.parse("1024", default_unit=StorageUnit.KIB)
        assert storage.value == 1024.0
        assert storage.unit == StorageUnit.KIB
    
    def test_parsing_zero(self):
        """Test parsing zero values."""
        storage = Storage.parse("0 MB")
        assert storage.value == 0.0
        assert storage.unit == StorageUnit.MB
    
    def test_parsing_decimal_values(self):
        """Test parsing decimal values."""
        storage = Storage.parse("3.14159 GB")
        assert storage.value == 3.14159
        assert storage.unit == StorageUnit.GB
    
    @pytest.mark.parametrize("input_string,expected_value,expected_unit", [
        ("1 MB", 1.0, StorageUnit.MB),
        ("1.5 GB", 1.5, StorageUnit.GB),
        ("1024 bytes", 1024.0, StorageUnit.BYTES),
        ("1 mb", 1.0, StorageUnit.MB),
        ("1MB", 1.0, StorageUnit.MB),
        ("1,5 MB", 1.5, StorageUnit.MB),
        ("1 KiB", 1.0, StorageUnit.KIB),
        ("8 bits", 8.0, StorageUnit.BITS),
        ("1000", 1000.0, StorageUnit.BYTES),
        ("0.5", 0.5, StorageUnit.BYTES),
    ])
    def test_parsing_parametrized(self, input_string: str, expected_value: float, expected_unit: StorageUnit):
        """Test string parsing with parametrized data."""
        storage = Storage.parse(input_string)
        assert storage.value == expected_value
        assert storage.unit == expected_unit
    
    def test_parsing_error_empty_string(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="Input string cannot be empty"):
            Storage.parse("")
    
    def test_parsing_error_whitespace_only(self):
        """Test that whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Input string cannot be empty"):
            Storage.parse("   ")
    
    def test_parsing_error_invalid_format(self):
        """Test that invalid format raises ValueError."""
        invalid_cases = [
            "abc",
            "1.2.3 MB",
            "MB 1",
            "1 2 MB",
            "invalid format",
        ]
        
        for case in invalid_cases:
            with pytest.raises(ValueError, match="Invalid format"):
                Storage.parse(case)
    
    def test_parsing_error_invalid_value(self):
        """Test that invalid numeric value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid format"):
            Storage.parse("abc MB")
    
    def test_parsing_error_non_string_input(self):
        """Test that non-string input raises TypeError."""
        with pytest.raises(TypeError, match="Input must be a string"):
            Storage.parse(123)


class TestStorageStringRepresentations:
    """Test Storage string representation methods."""
    
    def test_str_representation(self):
        """Test __str__ method."""
        storage = Storage(1.5, StorageUnit.MB)
        assert str(storage) == "1.5 MB"
    
    def test_str_representation_integer_value(self):
        """Test __str__ with integer value."""
        storage = Storage(1, StorageUnit.KIB)
        assert str(storage) == "1 KIB"
    
    def test_str_representation_zero(self):
        """Test __str__ with zero value."""
        storage = Storage(0, StorageUnit.BYTES)
        assert str(storage) == "0 BYTES"
    
    def test_repr_representation(self):
        """Test __repr__ method."""
        storage = Storage(1.5, StorageUnit.MB)
        repr_str = repr(storage)
        assert "Storage" in repr_str
        assert "1.5" in repr_str
        assert "MB" in repr_str
    
    def test_format_basic(self):
        """Test __format__ method."""
        storage = Storage(1.23456, StorageUnit.MB)
        formatted = f"{storage:.2f}"
        assert formatted == "1.23 MB"
    
    def test_format_no_spec(self):
        """Test __format__ with no format specification."""
        storage = Storage(1.5, StorageUnit.MB)
        formatted = f"{storage}"
        assert formatted == "1.5 MB"
    
    @pytest.mark.parametrize("value,unit,format_spec,expected", [
        (1.23456, StorageUnit.MB, ".2f", "1.23 MB"),
        (1234, StorageUnit.BYTES, ".1f", "1234.0 BYTES"),
        (1, StorageUnit.KIB, ".0f", "1 KIB"),
        (1.5, StorageUnit.GB, ".0f", "2 GB"),
    ])
    def test_format_parametrized(self, value: float, unit: StorageUnit, format_spec: str, expected: str):
        """Test formatting with various format specifications."""
        storage = Storage(value, unit)
        formatted = format(storage, format_spec)
        assert formatted == expected


class TestStorageFileOperations:
    """Test Storage file system operations."""
    
    def test_get_size_from_path_file(self, temp_file_with_content):
        """Test getting size from a file path."""
        temp_path, expected_size = temp_file_with_content
        
        # Test with Path object
        file_size = Storage.get_size_from_path(temp_path)
        assert file_size.value == expected_size
        assert file_size.unit == StorageUnit.BYTES
        
        # Test with string path
        file_size_str = Storage.get_size_from_path(str(temp_path))
        assert file_size_str.value == expected_size
        assert file_size_str.unit == StorageUnit.BYTES
    
    def test_get_size_from_path_directory(self, temp_directory_with_files):
        """Test getting size from a directory path."""
        temp_path, expected_size = temp_directory_with_files
        
        dir_size = Storage.get_size_from_path(temp_path)
        assert dir_size.value == expected_size
        assert dir_size.unit == StorageUnit.BYTES
    
    def test_get_size_from_path_nonexistent(self):
        """Test that nonexistent path raises FileNotFoundError."""
        nonexistent_path = Path("/nonexistent/path/file.txt")
        
        with pytest.raises(FileNotFoundError, match="Path does not exist"):
            Storage.get_size_from_path(nonexistent_path)
    
    def test_get_platform_storage(self):
        """Test getting platform-specific storage."""
        platform_storage = Storage.get_platform_storage()
        assert platform_storage is not None
        
        # Test that it has the expected methods
        assert hasattr(platform_storage, 'get_size_from_path')
        assert hasattr(platform_storage, 'get_platform_info')
    
    def test_get_platform_storage_info(self):
        """Test platform storage info."""
        platform_storage = Storage.get_platform_storage()
        info = platform_storage.get_platform_info()
        
        assert isinstance(info, dict)
        assert 'platform' in info
        assert info['platform'] in ['Windows', 'Linux', 'macOS']


class TestStorageUtilityMethods:
    """Test Storage utility methods."""
    
    def test_auto_scale_binary_basic(self):
        """Test auto scale with binary preference."""
        storage = Storage(1536, StorageUnit.BYTES)
        scaled = storage.auto_scale(prefer_binary=True)
        
        assert scaled.value == 1.5
        assert scaled.unit == StorageUnit.KIB
    
    def test_auto_scale_decimal_basic(self):
        """Test auto scale with decimal preference."""
        storage = Storage(1500, StorageUnit.BYTES)
        scaled = storage.auto_scale(prefer_binary=False)
        
        assert scaled.value == 1.5
        assert scaled.unit == StorageUnit.KB
    
    def test_auto_scale_zero(self):
        """Test auto scale with zero value."""
        storage = Storage(0, StorageUnit.BYTES)
        scaled_binary = storage.auto_scale(prefer_binary=True)
        scaled_decimal = storage.auto_scale(prefer_binary=False)
        
        assert scaled_binary.value == 0
        assert scaled_binary.unit == StorageUnit.BYTES
        assert scaled_decimal.value == 0
        assert scaled_decimal.unit == StorageUnit.BYTES
    
    @pytest.mark.parametrize("bytes_value,prefer_binary,expected_unit", [
        (1024, True, StorageUnit.KIB),
        (1048576, True, StorageUnit.MIB),
        (1073741824, True, StorageUnit.GIB),
        (1000, False, StorageUnit.KB),
        (1000000, False, StorageUnit.MB),
        (1000000000, False, StorageUnit.GB),
        (512, True, StorageUnit.BYTES),
        (500, False, StorageUnit.BYTES),
    ])
    def test_auto_scale_parametrized(self, bytes_value: int, prefer_binary: bool, expected_unit: StorageUnit):
        """Test auto scale with parametrized data."""
        storage = Storage(bytes_value, StorageUnit.BYTES)
        scaled = storage.auto_scale(prefer_binary=prefer_binary)
        
        assert scaled.unit == expected_unit
        # Verify the conversion is correct
        assert abs(scaled.convert_to_bytes() - bytes_value) < 1e-10
    
    def test_hash_functionality(self):
        """Test that Storage objects can be hashed."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(1024, StorageUnit.BYTES)
        s3 = Storage(2, StorageUnit.KIB)
        
        # Equal objects should have same hash
        assert hash(s1) == hash(s2)
        
        # Different objects should have different hash (usually)
        assert hash(s1) != hash(s3)
        
        # Test that Storage can be used in sets
        storage_set = {s1, s2, s3}
        assert len(storage_set) == 2  # s1 and s2 are equal


class TestStorageEdgeCases:
    """Test Storage edge cases and boundary conditions."""
    
    def test_very_large_values(self):
        """Test handling of very large values."""
        large_value = 1e15
        storage = Storage(large_value, StorageUnit.BYTES)
        
        assert storage.value == large_value
        assert storage.convert_to_bytes() == large_value
    
    def test_very_small_values(self):
        """Test handling of very small values."""
        small_value = 1e-10
        storage = Storage(small_value, StorageUnit.BYTES)
        
        assert storage.value == small_value
        assert storage.convert_to_bytes() == small_value
    
    def test_precision_maintenance(self):
        """Test that precision is maintained in calculations."""
        storage = Storage(1/3, StorageUnit.KIB)
        doubled = storage * 2
        tripled = storage * 3
        
        # Should maintain precision
        assert abs(tripled.value - 1.0) < 1e-15
        
        # Addition converts to bytes, so test in bytes
        added_result = doubled + storage
        expected_bytes = (1/3 * 2 + 1/3) * 1024  # 1 * 1024
        assert abs(added_result.convert_to_bytes() - expected_bytes) < 1e-10
    
    def test_bit_unit_precision(self):
        """Test precision with bit units."""
        storage = Storage(1, StorageUnit.BITS)
        assert storage.convert_to_bytes() == 0.125
        
        eight_bits = Storage(8, StorageUnit.BITS)
        assert eight_bits.convert_to_bytes() == 1.0
    
    def test_chained_operations(self):
        """Test chained arithmetic operations."""
        storage = Storage(1, StorageUnit.KIB)
        
        result = ((storage * 2) + Storage(512, StorageUnit.BYTES)) / 2
        expected_bytes = (2048 + 512) / 2  # 1280 bytes
        
        assert result.convert_to_bytes() == expected_bytes
    
    def test_sorting_storage_objects(self):
        """Test that Storage objects can be sorted."""
        storages = [
            Storage(2, StorageUnit.KIB),
            Storage(1024, StorageUnit.BYTES),
            Storage(3, StorageUnit.KIB),
            Storage(512, StorageUnit.BYTES),
        ]
        
        sorted_storages = sorted(storages)
        
        # Should be sorted by byte value
        byte_values = [s.convert_to_bytes() for s in sorted_storages]
        assert byte_values == sorted(byte_values)
    
    def test_not_implemented_operations(self):
        """Test operations that should return NotImplemented."""
        storage = Storage(1, StorageUnit.KIB)
        
        # Arithmetic with incompatible types
        assert storage.__add__("invalid") == NotImplemented
        assert storage.__sub__("invalid") == NotImplemented
        assert storage.__mul__("invalid") == NotImplemented
        assert storage.__truediv__("invalid") == NotImplemented
        assert storage.__floordiv__("invalid") == NotImplemented
        assert storage.__mod__("invalid") == NotImplemented
        
        # Comparisons with incompatible types
        assert storage.__lt__("invalid") == NotImplemented
        assert storage.__le__("invalid") == NotImplemented
        assert storage.__gt__("invalid") == NotImplemented
        assert storage.__ge__("invalid") == NotImplemented