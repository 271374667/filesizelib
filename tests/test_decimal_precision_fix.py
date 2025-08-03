"""
Tests for decimal precision fix in Storage class.

This module tests the exact decimal precision implementation using Python's
Decimal module to eliminate floating-point precision errors.
"""

import pytest
from decimal import Decimal
from filesizelib import Storage, FileSize, StorageUnit


class TestDecimalPrecisionFix:
    """Test cases for the decimal precision fix."""
    
    def test_exact_parsing_precision(self):
        """Test that parsing preserves exact decimal values."""
        test_cases = [
            "6.682",
            "6.682 MB", 
            "1.234567890123456",
            "1.234567890123456 GB",
            "0.001",
            "0.001 TB",
            "9.999999999999999",
            "9.999999999999999 KB",
            "123.456789012345678901234567890",
            "0.000000000000000000001",
        ]
        
        for case in test_cases:
            # Parse with and without units
            if " " in case:
                value_str, unit_str = case.split(" ", 1)
                storage = Storage.parse(case)
                # Extract the expected decimal value
                expected_value = Decimal(value_str)
            else:
                storage = Storage.parse(case)
                expected_value = Decimal(case)
            
            # The internal decimal value should be exactly equal (no precision loss)
            assert storage.decimal_value == expected_value, f"Precision lost for '{case}'"
    
    def test_string_representation_precision(self):
        """Test that string representation shows exact values."""
        test_cases = [
            ("6.682 MB", "6.682 MB"),
            ("1.234567890123456 GB", "1.234567890123456 GB"),
            ("0.001 TB", "0.001 TB"),
            ("9.999999999999999 KB", "9.999999999999999 KB"),
            ("123.456 BYTES", "123.456 BYTES"),
        ]
        
        for input_str, expected_output in test_cases:
            storage = Storage.parse(input_str)
            actual_output = str(storage)
            assert actual_output == expected_output, \
                f"Expected '{expected_output}', got '{actual_output}'"
    
    def test_original_reported_case(self):
        """Test the originally reported precision issue."""
        storage = FileSize.parse('6.682 MB')
        
        # Should show exact value, not floating-point precision errors
        assert str(storage) == "6.682 MB"
        assert "6.68200000000000038369" not in str(storage)
        
        # Internal decimal value should be exact
        assert storage.decimal_value == Decimal('6.682')
    
    def test_arithmetic_precision_preservation(self):
        """Test that arithmetic operations preserve precision."""
        # Same unit arithmetic should preserve the unit and precision
        a = Storage('1.1 GB')
        b = Storage('2.2 GB')
        
        # Addition
        result = a + b
        assert str(result) == "3.3 GB"
        assert result.unit == StorageUnit.GB
        
        # Subtraction  
        result = b - a
        assert str(result) == "1.1 GB"
        assert result.unit == StorageUnit.GB
        
        # Multiplication
        result = a * 2
        assert str(result) == "2.2 GB"
        assert result.unit == StorageUnit.GB
        
        # Division
        result = b / 2
        assert str(result) == "1.1 GB"
        assert result.unit == StorageUnit.GB
    
    def test_conversion_precision(self):
        """Test that unit conversions maintain precision."""
        # Test MB to GB conversion
        storage = Storage('1500 MB')
        gb_storage = storage.convert_to_gb()
        assert str(gb_storage) == "1.5 GB"
        
        # Test GB to MB conversion
        storage = Storage('1.5 GB')
        mb_storage = storage.convert_to_mb()
        assert str(mb_storage) == "1500 MB"
        
        # Test property-based conversions
        storage = Storage('1.5 GB')
        assert str(storage.MB) == "1500 MB"
        assert str(storage.KB) == "1500000 KB"
    
    def test_decimal_input_support(self):
        """Test that Decimal objects can be used as input."""
        decimal_value = Decimal('123.456789012345678901234567890')
        storage = Storage(decimal_value, StorageUnit.MB)
        
        # Should preserve the full decimal precision internally
        assert storage.decimal_value == decimal_value
        # String representation may be limited by decimal precision setting (default 20)
        assert "123.45678901234567890123" in str(storage)
    
    def test_float_input_conversion(self):
        """Test that float inputs are converted safely."""
        # Float input should be converted to string first to minimize precision loss
        storage = Storage(6.682, StorageUnit.MB)
        
        # Should be very close to expected value (some precision loss from float is expected)
        assert abs(storage.decimal_value - Decimal('6.682')) < Decimal('0.0001')
    
    def test_edge_cases(self):
        """Test edge cases for decimal precision."""
        # Very small numbers
        storage = Storage('0.000000001 GB')
        assert str(storage) == "0.000000001 GB"
        
        # Very large numbers  
        storage = Storage('999999999999.999999999 BYTES')
        assert str(storage) == "999999999999.999999999 BYTES"
        
        # Zero
        storage = Storage('0 MB')
        assert str(storage) == "0 MB"
        
        # Integer values should display without decimal point
        storage = Storage('5 GB')
        assert str(storage) == "5 GB"
    
    def test_precision_configuration(self):
        """Test that decimal precision configuration works."""
        # Store original precision
        original_precision = Storage.get_decimal_precision()
        
        try:
            # Set low precision
            Storage.set_decimal_precision(3)
            
            # Create storage with high precision value
            storage = Storage('1.23456789012345 GB')
            formatted = storage._format_value(storage.decimal_value)
            
            # Should be limited by precision setting
            assert len(formatted.split('.')[-1]) <= 3
            
            # Set higher precision
            Storage.set_decimal_precision(10)
            formatted = storage._format_value(storage.decimal_value)
            
            # Should show more precision
            assert '1.23456789' in formatted
            
        finally:
            # Restore original precision
            Storage.set_decimal_precision(original_precision)
    
    def test_comparison_precision(self):
        """Test that comparisons work correctly with decimal precision."""
        a = Storage('1.234567890123456 GB')
        b = Storage('1.234567890123456 GB')
        c = Storage('1.234567890123457 GB')
        
        # Equal values should be equal
        assert a == b
        
        # Slightly different values should not be equal
        assert a != c
        assert b != c
        
        # Comparison operations
        assert c > a
        assert c > b
        assert a <= b
    
    def test_type_conversion_precision(self):
        """Test int() and float() conversions preserve precision in bytes."""
        storage = Storage('1.5 GB')
        
        # int() and float() should return exact byte count
        expected_bytes = 1500000000
        assert int(storage) == expected_bytes
        assert float(storage) == float(expected_bytes)
        
        # Test with decimal fractions
        storage = Storage('1.5 KB')
        expected_bytes = 1500
        assert int(storage) == expected_bytes
        assert float(storage) == float(expected_bytes)
    
    def test_backward_compatibility(self):
        """Test that the fix doesn't break existing functionality."""
        # All these should work as before
        storage1 = Storage(1024, StorageUnit.BYTES)
        storage2 = Storage.parse("1 KiB")
        
        assert storage1 == storage2
        assert str(storage1) == "1024 BYTES"
        assert str(storage2) == "1 KIB"  # Unit names are uppercase in enum
        
        # Arithmetic should still work
        total = storage1 + storage2
        assert total.convert_to_bytes() == Decimal('2048')
    
    def test_mixed_unit_arithmetic_precision(self):
        """Test arithmetic with different units maintains precision."""
        mb_storage = Storage('1.5 MB')
        kb_storage = Storage('500 KB')
        
        # Different units should convert to bytes
        total = mb_storage + kb_storage
        assert total.unit == StorageUnit.BYTES
        assert total.convert_to_bytes() == Decimal('2000000')  # 1.5MB + 0.5MB = 2MB


class TestDecimalPerformance:
    """Test performance implications of Decimal usage."""
    
    def test_large_arithmetic_operations(self):
        """Test that Decimal arithmetic works with large numbers."""
        # Create large storage values
        large1 = Storage('999999999999.999999999 TB')
        large2 = Storage('0.000000001 TB')
        
        # Arithmetic should work without overflow
        result = large1 + large2
        assert result.unit == StorageUnit.TB
        assert result.decimal_value == Decimal('1000000000000.000000000')
    
    def test_precision_with_many_operations(self):
        """Test that precision is maintained through many operations."""
        storage = Storage('1.1 GB')
        
        # Perform many operations
        for i in range(100):
            storage = storage + Storage('0.01 GB')
        
        # Should maintain precision
        expected = Decimal('1.1') + Decimal('0.01') * 100
        assert storage.decimal_value == expected
        
        # String representation should be clean
        assert str(storage) == "2.1 GB"


if __name__ == "__main__":
    pytest.main([__file__])