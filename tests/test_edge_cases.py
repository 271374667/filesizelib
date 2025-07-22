"""
Edge cases and error condition tests for the bytesize library.

This module tests boundary conditions, error handling, and unusual
scenarios to ensure robust behavior.
"""

import pytest
import sys
import math
from pathlib import Path
from unittest.mock import patch, MagicMock

from filesizelib import Storage, StorageUnit


class TestBoundaryValues:
    """Test boundary value conditions."""
    
    def test_zero_values(self):
        """Test handling of zero values."""
        zero_storage = Storage(0, StorageUnit.BYTES)
        
        # Basic operations with zero
        assert zero_storage.convert_to_bytes() == 0.0
        assert zero_storage.convert_to(StorageUnit.KIB).value == 0.0
        assert zero_storage.auto_scale().value == 0.0
        assert zero_storage.auto_scale().unit == StorageUnit.BYTES
        
        # Arithmetic with zero
        non_zero = Storage(1, StorageUnit.KIB)
        assert (zero_storage + non_zero) == non_zero
        assert (non_zero + zero_storage) == non_zero
        assert (non_zero - zero_storage) == non_zero
        assert (zero_storage * 100).value == 0.0
        
        # Comparisons with zero
        assert zero_storage == Storage(0, StorageUnit.GIB)
        assert zero_storage < non_zero
        assert not (zero_storage > non_zero)
    
    def test_very_large_values(self):
        """Test handling of very large values."""
        # Test with maximum safe values
        large_value = sys.float_info.max / 1e10  # Avoid overflow
        large_storage = Storage(large_value, StorageUnit.BYTES)
        
        assert large_storage.value == large_value
        assert large_storage.convert_to_bytes() == large_value
        
        # Arithmetic should work
        doubled = large_storage * 2
        assert doubled.value == large_value * 2
        
        halved = large_storage / 2
        assert halved.value == large_value / 2
    
    def test_very_small_values(self):
        """Test handling of very small values."""
        # Test with very small positive values
        small_value = sys.float_info.min * 1e10
        small_storage = Storage(small_value, StorageUnit.BYTES)
        
        assert small_storage.value == small_value
        assert small_storage.convert_to_bytes() == small_value
        
        # Should maintain precision
        doubled = small_storage * 2
        assert doubled.value == small_value * 2
    
    def test_precision_limits(self):
        """Test floating point precision limits."""
        # Test precision with very small differences
        storage1 = Storage(1.0000000000000001, StorageUnit.BYTES)
        storage2 = Storage(1.0, StorageUnit.BYTES)
        
        # Should handle floating point precision correctly
        # (may be equal due to floating point limitations)
        diff = abs(storage1.convert_to_bytes() - storage2.convert_to_bytes())
        assert diff < 1e-10 or storage1 == storage2
    
    def test_fractional_bit_values(self):
        """Test handling of fractional bit values."""
        # 1 bit = 0.125 bytes
        quarter_bit = Storage(0.25, StorageUnit.BITS)
        assert quarter_bit.convert_to_bytes() == 0.03125
        
        # Should handle fractional operations
        doubled = quarter_bit * 2
        assert doubled.value == 0.5
        assert doubled.unit == StorageUnit.BITS


class TestErrorConditions:
    """Test error conditions and exception handling."""
    
    def test_negative_value_initialization(self):
        """Test that negative values raise ValueError."""
        with pytest.raises(ValueError, match="Storage value cannot be negative"):
            Storage(-1, StorageUnit.BYTES)
        
        with pytest.raises(ValueError, match="Storage value cannot be negative"):
            Storage(-0.1, StorageUnit.KIB)
        
        with pytest.raises(ValueError, match="Storage value cannot be negative"):
            Storage(-1e-10, StorageUnit.MB)
    
    def test_invalid_type_initialization(self):
        """Test that invalid types raise TypeError."""
        # Invalid value types
        with pytest.raises(TypeError, match="Value must be a number"):
            Storage("1", StorageUnit.BYTES)
        
        with pytest.raises(TypeError, match="Value must be a number"):
            Storage(None, StorageUnit.BYTES)
        
        with pytest.raises(TypeError, match="Value must be a number"):
            Storage([], StorageUnit.BYTES)
        
        # Invalid unit types
        with pytest.raises(TypeError, match="Unit must be a StorageUnit"):
            Storage(1, "bytes")
        
        with pytest.raises(TypeError, match="Unit must be a StorageUnit"):
            Storage(1, 1024)
        
        with pytest.raises(TypeError, match="Unit must be a StorageUnit"):
            Storage(1, None)
    
    def test_arithmetic_type_errors(self):
        """Test arithmetic operations with invalid types."""
        storage = Storage(1, StorageUnit.KIB)
        
        # Addition with invalid types
        with pytest.raises(TypeError):
            storage + "invalid"
        
        with pytest.raises(TypeError):
            storage + 1024  # Should be Storage, not int
        
        # Subtraction with invalid types
        with pytest.raises(TypeError):
            storage - "invalid"
        
        with pytest.raises(TypeError):
            storage - 1024
        
        # Multiplication with invalid types should return NotImplemented
        assert storage.__mul__("invalid") == NotImplemented
        assert storage.__mul__(None) == NotImplemented
        assert storage.__mul__([]) == NotImplemented
        
        # Division with invalid types should return NotImplemented
        assert storage.__truediv__("invalid") == NotImplemented
        assert storage.__truediv__(None) == NotImplemented
    
    def test_division_by_zero_errors(self):
        """Test division by zero errors."""
        storage = Storage(1, StorageUnit.KIB)
        
        # Division by zero number
        with pytest.raises(ZeroDivisionError, match="Cannot divide storage by zero"):
            storage / 0
        
        with pytest.raises(ZeroDivisionError, match="Cannot divide storage by zero"):
            storage / 0.0
        
        # Division by zero storage
        zero_storage = Storage(0, StorageUnit.BYTES)
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero storage"):
            storage / zero_storage
        
        # Floor division by zero
        with pytest.raises(ZeroDivisionError, match="Cannot divide storage by zero"):
            storage // 0
        
        # Modulo by zero
        with pytest.raises(ZeroDivisionError, match="Cannot perform modulo with zero"):
            storage % 0
    
    def test_negative_arithmetic_results(self):
        """Test arithmetic operations that would result in negative values."""
        small = Storage(1, StorageUnit.BYTES)
        large = Storage(1, StorageUnit.KIB)
        
        # Subtraction resulting in negative
        with pytest.raises(ValueError, match="Storage subtraction result cannot be negative"):
            small - large
        
        # Multiplication by negative factor
        with pytest.raises(ValueError, match="Cannot multiply storage by negative factor"):
            large * -1
        
        with pytest.raises(ValueError, match="Cannot multiply storage by negative factor"):
            large * -0.5
    
    def test_comparison_type_errors(self):
        """Test comparison operations with invalid types."""
        storage = Storage(1, StorageUnit.KIB)
        
        # Comparisons with invalid types should return NotImplemented
        assert storage.__lt__("invalid") == NotImplemented
        assert storage.__le__(123) == NotImplemented
        assert storage.__gt__(None) == NotImplemented
        assert storage.__ge__([]) == NotImplemented
        
        # Equality with invalid types should return False
        assert not (storage == "invalid")
        assert not (storage == 1024)
        assert not (storage == None)
    
    def test_string_parsing_errors(self):
        """Test string parsing error conditions."""
        # Empty and whitespace strings
        with pytest.raises(ValueError, match="Input string cannot be empty"):
            Storage.parse("")
        
        with pytest.raises(ValueError, match="Input string cannot be empty"):
            Storage.parse("   ")
        
        with pytest.raises(ValueError, match="Input string cannot be empty"):
            Storage.parse("\t\n")
        
        # Invalid formats
        with pytest.raises(ValueError, match="Invalid format"):
            Storage.parse("abc")
        
        with pytest.raises(ValueError, match="Invalid format"):
            Storage.parse("1.2.3 MB")
        
        with pytest.raises(ValueError, match="Invalid format"):
            Storage.parse("MB 1")
        
        with pytest.raises(ValueError, match="Invalid format"):
            Storage.parse("1 2 MB")
        
        # Invalid numeric values
        with pytest.raises(ValueError, match="Invalid format"):
            Storage.parse("abc MB")
        
        with pytest.raises(ValueError, match="Invalid format"):
            Storage.parse("1..5 MB")
        
        with pytest.raises(ValueError, match="Invalid format"):
            Storage.parse("1,,5 MB")
        
        # Non-string input
        with pytest.raises(TypeError, match="Input must be a string"):
            Storage.parse(123)
        
        with pytest.raises(TypeError, match="Input must be a string"):
            Storage.parse(None)
        
        with pytest.raises(TypeError, match="Input must be a string"):
            Storage.parse([])
    
    def test_file_operation_errors(self):
        """Test file operation error conditions."""
        # Nonexistent file
        nonexistent = Path("/nonexistent/file.txt")
        with pytest.raises(FileNotFoundError, match="Path does not exist"):
            Storage.get_size_from_path(nonexistent)
        
        # Test with platform storage
        platform_storage = Storage.get_platform_storage()
        with pytest.raises(FileNotFoundError):
            platform_storage.get_size_from_path(nonexistent)


class TestEdgeCaseOperations:
    """Test edge cases in operations."""
    
    def test_chained_operations(self):
        """Test complex chained operations."""
        # Start with a storage value
        storage = Storage(1, StorageUnit.KIB)
        
        # Perform a series of operations
        result = ((storage * 2) + Storage(512, StorageUnit.BYTES)) / 2 - Storage(256, StorageUnit.BYTES)
        
        # Expected: ((1024 * 2) + 512) / 2 - 256 = (2048 + 512) / 2 - 256 = 1280 - 256 = 1024 bytes
        assert result.convert_to_bytes() == 1024.0
    
    def test_self_operations(self):
        """Test operations with self."""
        storage = Storage(2, StorageUnit.KIB)
        
        # Addition with self
        doubled = storage + storage
        assert doubled.convert_to_bytes() == 4096.0
        
        # Subtraction with self (should be zero)
        zero_result = storage - storage
        assert zero_result.convert_to_bytes() == 0.0
        
        # Division with self (should be 1.0)
        ratio = storage / storage
        assert ratio == 1.0
    
    def test_operation_order_independence(self):
        """Test that mathematically equivalent operations produce same results."""
        a = Storage(1, StorageUnit.KIB)
        b = Storage(512, StorageUnit.BYTES)
        c = Storage(256, StorageUnit.BYTES)
        
        # Test associativity: (a + b) + c == a + (b + c)
        left_assoc = (a + b) + c
        right_assoc = a + (b + c)
        assert left_assoc == right_assoc
        
        # Test commutativity: a + b == b + a
        forward = a + b
        backward = b + a
        assert forward == backward
    
    def test_unit_boundary_conversions(self):
        """Test conversions at unit boundaries."""
        # Exactly 1024 bytes to KiB
        exactly_kib = Storage(1024, StorageUnit.BYTES)
        converted = exactly_kib.convert_to(StorageUnit.KIB)
        assert converted.value == 1.0
        assert converted.unit == StorageUnit.KIB
        
        # Just under 1024 bytes
        under_kib = Storage(1023, StorageUnit.BYTES)
        converted_under = under_kib.convert_to(StorageUnit.KIB)
        assert converted_under.value == 1023/1024
        
        # Just over 1024 bytes
        over_kib = Storage(1025, StorageUnit.BYTES)
        converted_over = over_kib.convert_to(StorageUnit.KIB)
        assert converted_over.value == 1025/1024
    
    def test_auto_scaling_edge_cases(self):
        """Test auto scaling at boundaries."""
        # Exactly at unit boundary
        boundary = Storage(1024, StorageUnit.BYTES)
        scaled = boundary.auto_scale(prefer_binary=True)
        assert scaled.value == 1.0
        assert scaled.unit == StorageUnit.KIB
        
        # Just under boundary
        under_boundary = Storage(1023, StorageUnit.BYTES)
        scaled_under = under_boundary.auto_scale(prefer_binary=True)
        assert scaled_under.value == 1023
        assert scaled_under.unit == StorageUnit.BYTES
        
        # Very large value that exceeds all predefined units
        very_large = Storage(1e30, StorageUnit.BYTES)
        scaled_large = very_large.auto_scale(prefer_binary=True)
        # Should use the largest available unit
        assert scaled_large.unit == StorageUnit.YIB


class TestConcurrencyAndThreadSafety:
    """Test behavior under concurrent access (basic checks)."""
    
    def test_immutability_of_operations(self):
        """Test that operations don't modify original objects."""
        original = Storage(1, StorageUnit.KIB)
        original_value = original.value
        original_unit = original.unit
        
        # Perform operations
        result1 = original + Storage(512, StorageUnit.BYTES)
        result2 = original * 2
        result3 = original.convert_to(StorageUnit.BYTES)
        result4 = original.auto_scale()
        
        # Original should be unchanged
        assert original.value == original_value
        assert original.unit == original_unit
    
    def test_enum_immutability(self):
        """Test that StorageUnit enum is immutable."""
        original_bytes_value = StorageUnit.BYTES.value
        original_kib_value = StorageUnit.KIB.value
        
        # Try to modify (should not be possible)
        try:
            StorageUnit.BYTES.value = 999
        except AttributeError:
            pass  # Expected - enums should be immutable
        
        # Values should be unchanged
        assert StorageUnit.BYTES.value == original_bytes_value
        assert StorageUnit.KIB.value == original_kib_value


class TestMemoryAndPerformance:
    """Test memory usage and performance characteristics."""
    
    def test_large_number_of_objects(self):
        """Test creating large numbers of Storage objects."""
        # Create many Storage objects
        storages = []
        for i in range(1000):
            storage = Storage(i, StorageUnit.BYTES)
            storages.append(storage)
        
        # Should be able to create and use them
        assert len(storages) == 1000
        assert storages[0].value == 0
        assert storages[999].value == 999
        
        # Should be able to sum them
        total = sum(storages[1:], storages[0])
        expected = sum(range(1000))
        assert total.convert_to_bytes() == expected
    
    def test_deep_operation_chains(self):
        """Test deeply chained operations."""
        storage = Storage(1, StorageUnit.BYTES)
        
        # Chain many operations
        for i in range(100):
            storage = storage + Storage(1, StorageUnit.BYTES)
        
        # Should result in 101 bytes
        assert storage.convert_to_bytes() == 101.0
    
    def test_string_representation_performance(self):
        """Test string representations don't cause issues."""
        storage = Storage(1.23456789, StorageUnit.MB)
        
        # Should be able to call string methods multiple times
        for _ in range(100):
            str(storage)
            repr(storage)
            f"{storage:.2f}"
        
        # Should maintain consistency (allow for floating point precision)
        result = str(storage)
        assert "1.2345678" in result and "MB" in result


class TestMockingAndPatching:
    """Test behavior under mocked conditions."""
    
    @patch('platform.system')
    def test_platform_detection_edge_cases(self, mock_system):
        """Test platform detection with unusual platform names."""
        # Test case sensitivity
        mock_system.return_value = 'windows'  # lowercase
        with pytest.raises(ValueError):
            Storage.get_platform_storage()
        
        mock_system.return_value = 'LINUX'    # uppercase
        with pytest.raises(ValueError):
            Storage.get_platform_storage()
        
        # Test empty string
        mock_system.return_value = ''
        with pytest.raises(ValueError):
            Storage.get_platform_storage()
        
        # Test None
        mock_system.return_value = None
        with pytest.raises(ValueError):
            Storage.get_platform_storage()
    
    def test_file_operations_with_permission_errors(self, temp_file_with_content):
        """Test file operations when permission errors occur."""
        temp_path, _ = temp_file_with_content
        
        # Mock permission error more specifically
        with patch.object(Path, 'stat', side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError, match="Access denied"):
                Storage.get_size_from_path(temp_path)
    
    def test_file_operations_with_os_errors(self, temp_file_with_content):
        """Test file operations when OS errors occur."""
        temp_path, _ = temp_file_with_content
        
        # Mock OS error more specifically
        with patch.object(Path, 'stat', side_effect=OSError("System error")):
            with pytest.raises(OSError, match="System error"):
                Storage.get_size_from_path(temp_path)


class TestSpecialValues:
    """Test handling of special floating point values."""
    
    def test_infinity_handling(self):
        """Test behavior with infinity values."""
        # Should handle infinite values (they pass basic validation)
        # but may cause issues in operations
        try:
            inf_storage = Storage(float('inf'), StorageUnit.BYTES)
            assert inf_storage.value == float('inf')
        except (ValueError, TypeError):
            # If implementation rejects infinity, that's also acceptable
            pass
        
        # Negative infinity should still fail due to negative check
        with pytest.raises(ValueError, match="Storage value cannot be negative"):
            Storage(float('-inf'), StorageUnit.BYTES)
    
    def test_nan_handling(self):
        """Test behavior with NaN values."""
        # NaN values might be accepted but cause issues in operations
        try:
            nan_storage = Storage(float('nan'), StorageUnit.BYTES)
            # NaN comparisons always return False
            assert not (nan_storage.value == nan_storage.value)  # NaN != NaN
        except (ValueError, TypeError):
            # If implementation rejects NaN, that's also acceptable
            pass
    
    def test_very_long_decimal_precision(self):
        """Test with very high precision decimal values."""
        # Very precise value
        precise_value = 1.123456789012345678901234567890
        storage = Storage(precise_value, StorageUnit.BYTES)
        
        # Should handle reasonable precision
        assert storage.value == precise_value
        assert storage.convert_to_bytes() == precise_value