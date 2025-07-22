"""
Tests for same-unit arithmetic operations.

This module tests the enhanced arithmetic operations that preserve the unit
when both operands have the same unit, while maintaining backward compatibility
for different unit operations.
"""

import pytest
from typing import Any, List, Tuple, Union

from byteunit import Storage, StorageUnit, ByteUnit


class TestSameUnitAddition:
    """Test addition operations with same and different units."""
    
    def test_same_unit_addition_basic(self):
        """Test basic same-unit addition."""
        s1 = Storage(1, StorageUnit.GB)
        s2 = Storage(2, StorageUnit.GB)
        result = s1 + s2
        
        assert result.value == 3.0
        assert result.unit == StorageUnit.GB
    
    def test_same_unit_addition_different_values(self):
        """Test same-unit addition with different value types."""
        s1 = Storage(1.5, StorageUnit.MB)
        s2 = Storage(2.5, StorageUnit.MB)
        result = s1 + s2
        
        assert result.value == 4.0
        assert result.unit == StorageUnit.MB
    
    def test_same_unit_addition_zero(self):
        """Test same-unit addition with zero values."""
        s1 = Storage(5, StorageUnit.KB)
        s2 = Storage(0, StorageUnit.KB)
        result = s1 + s2
        
        assert result.value == 5.0
        assert result.unit == StorageUnit.KB
    
    def test_same_unit_addition_decimal_precision(self):
        """Test that decimal precision is maintained in same-unit addition."""
        Storage.set_decimal_precision(3)
        
        s1 = Storage(1.111111, StorageUnit.TB)
        s2 = Storage(2.222222, StorageUnit.TB)
        result = s1 + s2
        
        assert result.unit == StorageUnit.TB
        assert abs(result.value - 3.333333) < 1e-6
        
        # Reset to default
        Storage.set_decimal_precision(20)
    
    @pytest.mark.parametrize("value1,value2,unit,expected_value", [
        (1, 2, StorageUnit.BYTES, 3),
        (1.5, 2.5, StorageUnit.KIB, 4.0),
        (0.5, 0.5, StorageUnit.MIB, 1.0),
        (10, 20, StorageUnit.GIB, 30),
        (1, 1, StorageUnit.TIB, 2),
        (2.5, 1.5, StorageUnit.KB, 4.0),
        (3.14, 2.86, StorageUnit.MB, 6.0),
        (1.1, 2.2, StorageUnit.GB, 3.3),
        (8, 8, StorageUnit.BITS, 16),
        (1000, 500, StorageUnit.KILOBITS, 1500),
    ])
    def test_same_unit_addition_parametrized(self, value1: float, value2: float, 
                                           unit: StorageUnit, expected_value: float):
        """Test same-unit addition with various units and values."""
        s1 = Storage(value1, unit)
        s2 = Storage(value2, unit)
        result = s1 + s2
        
        assert abs(result.value - expected_value) < 1e-10
        assert result.unit == unit
    
    def test_different_unit_addition_fallback(self):
        """Test that different units still convert to bytes."""
        s1 = Storage(1, StorageUnit.KB)
        s2 = Storage(1, StorageUnit.KIB)
        result = s1 + s2
        
        # Should be 1000 + 1024 = 2024 bytes
        assert result.value == 2024.0
        assert result.unit == StorageUnit.BYTES
    
    def test_binary_vs_decimal_unit_addition(self):
        """Test addition between binary and decimal units."""
        binary = Storage(1, StorageUnit.MIB)  # 1048576 bytes
        decimal = Storage(1, StorageUnit.MB)  # 1000000 bytes
        result = binary + decimal
        
        expected_bytes = 1048576 + 1000000
        assert result.value == expected_bytes
        assert result.unit == StorageUnit.BYTES
    
    def test_bit_unit_addition(self):
        """Test same-unit addition with bit units."""
        s1 = Storage(8, StorageUnit.BITS)
        s2 = Storage(16, StorageUnit.BITS)
        result = s1 + s2
        
        assert result.value == 24.0
        assert result.unit == StorageUnit.BITS
    
    def test_byteunit_alias_addition(self):
        """Test that ByteUnit alias works with same-unit addition."""
        b1 = ByteUnit(1, StorageUnit.GB)
        b2 = ByteUnit(2, StorageUnit.GB)
        result = b1 + b2
        
        assert result.value == 3.0
        assert result.unit == StorageUnit.GB
    
    def test_user_example_case(self):
        """Test the specific user example from the request."""
        a = ByteUnit.parse('53 KB').convert_to_gb()
        b = ByteUnit.parse('53 KB').convert_to_gb()
        result = a + b
        
        # Both should be in GB units
        assert a.unit == StorageUnit.GB
        assert b.unit == StorageUnit.GB
        assert result.unit == StorageUnit.GB
        
        # Value should be approximately 0.000106 GB
        expected_value = (53000 * 2) / (1000 ** 3)  # 106000 bytes in GB
        assert abs(result.value - expected_value) < 1e-10


class TestSameUnitSubtraction:
    """Test subtraction operations with same and different units."""
    
    def test_same_unit_subtraction_basic(self):
        """Test basic same-unit subtraction."""
        s1 = Storage(5, StorageUnit.GB)
        s2 = Storage(2, StorageUnit.GB)
        result = s1 - s2
        
        assert result.value == 3.0
        assert result.unit == StorageUnit.GB
    
    def test_same_unit_subtraction_equal_values(self):
        """Test same-unit subtraction resulting in zero."""
        s1 = Storage(3, StorageUnit.MB)
        s2 = Storage(3, StorageUnit.MB)
        result = s1 - s2
        
        assert result.value == 0.0
        assert result.unit == StorageUnit.MB
    
    def test_same_unit_subtraction_decimal(self):
        """Test same-unit subtraction with decimal values."""
        s1 = Storage(5.5, StorageUnit.KIB)
        s2 = Storage(2.3, StorageUnit.KIB)
        result = s1 - s2
        
        assert abs(result.value - 3.2) < 1e-10
        assert result.unit == StorageUnit.KIB
    
    def test_same_unit_subtraction_negative_error(self):
        """Test that same-unit subtraction raises error for negative results."""
        s1 = Storage(1, StorageUnit.TB)
        s2 = Storage(2, StorageUnit.TB)
        
        with pytest.raises(ValueError, match="Storage subtraction result cannot be negative"):
            s1 - s2
    
    @pytest.mark.parametrize("value1,value2,unit,expected_value", [
        (10, 3, StorageUnit.BYTES, 7),
        (5.5, 2.5, StorageUnit.KIB, 3.0),
        (1.0, 0.5, StorageUnit.MIB, 0.5),
        (100, 30, StorageUnit.GIB, 70),
        (5, 2, StorageUnit.TIB, 3),
        (10.5, 5.5, StorageUnit.KB, 5.0),
        (7.77, 3.33, StorageUnit.MB, 4.44),
        (2.5, 0.5, StorageUnit.GB, 2.0),
        (16, 8, StorageUnit.BITS, 8),
        (2000, 500, StorageUnit.KILOBITS, 1500),
    ])
    def test_same_unit_subtraction_parametrized(self, value1: float, value2: float,
                                              unit: StorageUnit, expected_value: float):
        """Test same-unit subtraction with various units and values."""
        s1 = Storage(value1, unit)
        s2 = Storage(value2, unit)
        result = s1 - s2
        
        assert abs(result.value - expected_value) < 1e-10
        assert result.unit == unit
    
    def test_different_unit_subtraction_fallback(self):
        """Test that different units still convert to bytes."""
        s1 = Storage(2, StorageUnit.KIB)  # 2048 bytes
        s2 = Storage(1, StorageUnit.KB)   # 1000 bytes
        result = s1 - s2
        
        # Should be 2048 - 1000 = 1048 bytes
        assert result.value == 1048.0
        assert result.unit == StorageUnit.BYTES
    
    def test_same_unit_subtraction_precision_edge_case(self):
        """Test same-unit subtraction with precision edge cases."""
        # Test very small differences
        s1 = Storage(1.0000001, StorageUnit.GB)
        s2 = Storage(1.0, StorageUnit.GB)
        result = s1 - s2
        
        assert result.unit == StorageUnit.GB
        assert abs(result.value - 0.0000001) < 1e-15


class TestSameUnitArithmeticEdgeCases:
    """Test edge cases and special scenarios for same-unit arithmetic."""
    
    def test_very_small_same_unit_values(self):
        """Test arithmetic with very small values in same units."""
        s1 = Storage(1e-10, StorageUnit.YB)
        s2 = Storage(2e-10, StorageUnit.YB)
        
        result_add = s1 + s2
        assert result_add.unit == StorageUnit.YB
        assert abs(result_add.value - 3e-10) < 1e-20
        
        result_sub = s2 - s1
        assert result_sub.unit == StorageUnit.YB
        assert abs(result_sub.value - 1e-10) < 1e-20
    
    def test_very_large_same_unit_values(self):
        """Test arithmetic with very large values in same units."""
        s1 = Storage(1e15, StorageUnit.BYTES)
        s2 = Storage(2e15, StorageUnit.BYTES)
        
        result_add = s1 + s2
        assert result_add.unit == StorageUnit.BYTES
        assert result_add.value == 3e15
        
        result_sub = s2 - s1
        assert result_sub.unit == StorageUnit.BYTES
        assert result_sub.value == 1e15
    
    def test_mixed_integer_float_same_unit(self):
        """Test arithmetic with mixed integer and float values in same units."""
        s1 = Storage(5, StorageUnit.MB)      # int
        s2 = Storage(2.5, StorageUnit.MB)    # float
        
        result = s1 + s2
        assert result.unit == StorageUnit.MB
        assert result.value == 7.5
    
    def test_zero_arithmetic_same_unit(self):
        """Test arithmetic operations with zero values in same units."""
        zero = Storage(0, StorageUnit.GB)
        non_zero = Storage(5, StorageUnit.GB)
        
        # Addition with zero
        result1 = zero + non_zero
        assert result1.unit == StorageUnit.GB
        assert result1.value == 5.0
        
        result2 = non_zero + zero
        assert result2.unit == StorageUnit.GB
        assert result2.value == 5.0
        
        # Subtraction with zero
        result3 = non_zero - zero
        assert result3.unit == StorageUnit.GB
        assert result3.value == 5.0
        
        result4 = zero - zero
        assert result4.unit == StorageUnit.GB
        assert result4.value == 0.0
    
    def test_precision_preservation_same_unit(self):
        """Test that precision is preserved in same-unit operations."""
        # Use a value that would lose precision in conversion
        s1 = Storage(1.23456789012345, StorageUnit.TB)
        s2 = Storage(2.34567890123456, StorageUnit.TB)
        
        result = s1 + s2
        assert result.unit == StorageUnit.TB
        
        # The sum should preserve precision better than byte conversion
        expected = 1.23456789012345 + 2.34567890123456
        assert abs(result.value - expected) < 1e-14
    
    def test_unit_consistency_across_operations(self):
        """Test that unit consistency is maintained across multiple operations."""
        s1 = Storage(10, StorageUnit.GIB)
        s2 = Storage(5, StorageUnit.GIB)
        s3 = Storage(2, StorageUnit.GIB)
        
        # Chain operations
        result = (s1 + s2) - s3
        assert result.unit == StorageUnit.GIB
        assert result.value == 13.0
        
        # Mixed chain (should break same-unit preservation)
        s4 = Storage(1, StorageUnit.GB)  # Different unit
        mixed_result = (s1 + s2) + s4  # First part same unit, then different
        # The first operation preserves GIB, but then adding GB converts to bytes
        assert mixed_result.unit == StorageUnit.BYTES


class TestBackwardCompatibility:
    """Test that the improvements don't break existing functionality."""
    
    def test_existing_different_unit_behavior_unchanged(self):
        """Test that different unit arithmetic still works as before."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(512, StorageUnit.BYTES)
        
        result_add = s1 + s2
        assert result_add.unit == StorageUnit.BYTES
        assert result_add.value == 1536.0
        
        result_sub = s1 - s2
        assert result_sub.unit == StorageUnit.BYTES
        assert result_sub.value == 512.0
    
    def test_existing_error_conditions_unchanged(self):
        """Test that error conditions still work as before."""
        s1 = Storage(1, StorageUnit.MB)
        s2 = Storage(2, StorageUnit.MB)
        
        # Should still raise ValueError for negative results
        with pytest.raises(ValueError, match="Storage subtraction result cannot be negative"):
            s1 - s2
        
        # Should still return NotImplemented for invalid types
        assert s1.__add__("invalid") == NotImplemented
        assert s1.__sub__("invalid") == NotImplemented
    
    def test_existing_tests_still_pass(self):
        """Test that examples from existing documentation still work."""
        # From the original docstring examples
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(512, StorageUnit.BYTES)
        
        # This should still work as documented (different units → bytes)
        total = s1 + s2
        assert total.unit == StorageUnit.BYTES
        
        s3 = Storage(2, StorageUnit.KIB)
        s4 = Storage(512, StorageUnit.BYTES)
        diff = s3 - s4
        assert diff.unit == StorageUnit.BYTES
    
    def test_type_checking_unchanged(self):
        """Test that type checking behavior is unchanged."""
        storage = Storage(1, StorageUnit.MB)
        
        # Should still return NotImplemented for wrong types
        assert storage.__add__(5) == NotImplemented
        assert storage.__sub__("test") == NotImplemented
        assert storage.__add__(None) == NotImplemented
    
    def test_multiplication_division_unchanged(self):
        """Test that multiplication and division are not affected."""
        storage = Storage(2, StorageUnit.GB)
        
        # Multiplication should still preserve original unit
        doubled = storage * 2
        assert doubled.unit == StorageUnit.GB
        assert doubled.value == 4.0
        
        # Division should still preserve original unit
        halved = storage / 2
        assert halved.unit == StorageUnit.GB
        assert halved.value == 1.0


class TestStringRepresentationWithSameUnits:
    """Test string representations work correctly with same-unit arithmetic."""
    
    def test_string_representation_same_unit_result(self):
        """Test string representation of same-unit arithmetic results."""
        s1 = Storage(1.5, StorageUnit.MB)
        s2 = Storage(2.5, StorageUnit.MB)
        result = s1 + s2
        
        assert str(result) == "4 MB"  # Integer values should not show decimals
    
    def test_decimal_precision_same_unit_result(self):
        """Test decimal precision affects same-unit arithmetic results."""
        Storage.set_decimal_precision(2)
        
        s1 = Storage(1.111, StorageUnit.GB)
        s2 = Storage(2.222, StorageUnit.GB)
        result = s1 + s2
        
        # Should respect precision setting
        result_str = str(result)
        assert "3.33" in result_str
        assert result_str == "3.33 GB"
        
        # Reset to default
        Storage.set_decimal_precision(20)
    
    def test_scientific_notation_elimination_same_unit(self):
        """Test that scientific notation is eliminated in same-unit results."""
        s1 = Storage(1e-8, StorageUnit.YB)
        s2 = Storage(2e-8, StorageUnit.YB)
        result = s1 + s2
        
        result_str = str(result)
        # Should not contain scientific notation
        assert 'e' not in result_str.lower()
        assert result_str.endswith(" YB")