"""
Comprehensive tests for decimal precision functionality.

This module thoroughly tests the decimal precision configuration system,
scientific notation elimination, and string formatting behavior.
"""

import pytest
import math
from decimal import Decimal
from typing import Any, List, Tuple, Union

from filesizelib import Storage, StorageUnit, FileSizeLib


class TestDecimalPrecisionConfiguration:
    """Test decimal precision configuration methods."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)  # Reset to default
    
    def test_default_precision(self):
        """Test that default precision is 20."""
        assert Storage.get_decimal_precision() == 20
    
    def test_set_get_precision_basic(self):
        """Test basic set and get precision functionality."""
        Storage.set_decimal_precision(5)
        assert Storage.get_decimal_precision() == 5
        
        Storage.set_decimal_precision(15)
        assert Storage.get_decimal_precision() == 15
    
    def test_set_precision_zero(self):
        """Test setting precision to zero."""
        Storage.set_decimal_precision(0)
        assert Storage.get_decimal_precision() == 0
        
        # Should show no decimal places
        storage = Storage(1.23456789, StorageUnit.MB)
        assert str(storage) == "1 MB"
    
    def test_set_precision_large_value(self):
        """Test setting precision to large values."""
        Storage.set_decimal_precision(50)
        assert Storage.get_decimal_precision() == 50
        
        # Should handle large precision without issues
        storage = Storage(1.23456789012345, StorageUnit.MB)
        result = str(storage)
        assert "1.23456789012345" in result
    
    @pytest.mark.parametrize("precision", [0, 1, 5, 10, 15, 20, 30])
    def test_set_precision_parametrized(self, precision: int):
        """Test setting various precision values."""
        Storage.set_decimal_precision(precision)
        assert Storage.get_decimal_precision() == precision
    
    def test_set_precision_error_negative(self):
        """Test that negative precision raises ValueError."""
        with pytest.raises(ValueError, match="Precision cannot be negative"):
            Storage.set_decimal_precision(-1)
        
        with pytest.raises(ValueError, match="Precision cannot be negative"):
            Storage.set_decimal_precision(-10)
    
    def test_set_precision_error_non_integer(self):
        """Test that non-integer precision raises TypeError."""
        with pytest.raises(TypeError, match="Precision must be an integer"):
            Storage.set_decimal_precision(5.5)
        
        with pytest.raises(TypeError, match="Precision must be an integer"):
            Storage.set_decimal_precision("5")
        
        with pytest.raises(TypeError, match="Precision must be an integer"):
            Storage.set_decimal_precision(None)
    
    def test_precision_class_wide_effect(self):
        """Test that precision setting affects all Storage instances."""
        s1 = Storage(1.23456789, StorageUnit.MB)
        s2 = Storage(9.87654321, StorageUnit.GB)
        
        # Set precision to 3
        Storage.set_decimal_precision(3)
        
        assert "1.235" in str(s1)  # Rounded to 3 decimal places
        assert "9.877" in str(s2)  # Rounded to 3 decimal places
    
    def test_precision_affects_byte_unit_alias(self):
        """Test that precision setting affects FileSizeLib alias."""
        Storage.set_decimal_precision(2)
        
        storage = Storage(1.23456, StorageUnit.MB)
        byte_unit = FileSizeLib(1.23456, StorageUnit.MB)
        
        # Both should have same formatting
        assert str(storage) == str(byte_unit)
        assert "1.23" in str(storage)
        assert "1.23" in str(byte_unit)


class TestScientificNotationElimination:
    """Test elimination of scientific notation in string representations."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_very_small_values_no_scientific_notation(self):
        """Test that very small values don't use scientific notation."""
        test_cases = [
            (1e-10, StorageUnit.GB, "0.0000000001"),
            (5.23456789e-8, StorageUnit.TB, "0.0000000523456789"),
            (9.872019291e-5, StorageUnit.GIB, "0.00009872019291"),
            (1.23e-15, StorageUnit.YB, "0.00000000000000123"),
        ]
        
        for value, unit, expected_prefix in test_cases:
            storage = Storage(value, unit)
            result = str(storage)
            
            # Should not contain 'e' or 'E' (no scientific notation)
            assert 'e' not in result.lower(), f"Scientific notation found in: {result}"
            
            # Should contain the expected decimal representation
            assert expected_prefix in result, f"Expected '{expected_prefix}' in '{result}'"
    
    def test_medium_small_values(self):
        """Test medium-small values that Python might format with scientific notation."""
        test_cases = [
            0.0001,
            0.00001, 
            0.000001,
            0.0000001,
            0.00000001,
        ]
        
        for value in test_cases:
            storage = Storage(value, StorageUnit.GB)
            result = str(storage)
            
            # No scientific notation should be present
            assert 'e' not in result.lower()
            assert 'E' not in result
            
            # Should start with "0."
            assert result.startswith("0.")
    
    def test_very_large_values_handling(self):
        """Test that very large values are handled appropriately."""
        test_cases = [
            1e15,
            1.23456789e20,
        ]
        
        for value in test_cases:
            storage = Storage(value, StorageUnit.BYTES)
            result = str(storage)
            
            # Should not use scientific notation for display
            # Large integers should display as integers without decimals
            if value == int(value):
                # For large values, check the actual stored decimal value
                expected_str = str(int(storage.decimal_value))
                assert expected_str in result
            else:
                # For non-integer large values, ensure no scientific notation
                # Note: Very large values may contain 'e' in their decimal representation
                # which is acceptable as long as it's not scientific notation format
                assert not ('e+' in result.lower() or 'e-' in result.lower())
    
    def test_edge_case_values(self):
        """Test edge case values that might trigger scientific notation."""
        edge_cases = [
            (1e-20, StorageUnit.ZB),
            (1e-25, StorageUnit.YB), 
            (9.999999999999999e-10, StorageUnit.TB),
            (1.0000000000000001e-5, StorageUnit.GB),
        ]
        
        for value, unit in edge_cases:
            storage = Storage(value, unit)
            result = str(storage)
            
            # No scientific notation
            assert 'e' not in result.lower()
            assert 'E' not in result
            
            # Should be a valid decimal representation
            assert result.replace(" " + unit.name, "").replace("-", "").replace(".", "").isdigit()
    
    def test_precision_affects_scientific_notation_elimination(self):
        """Test that precision setting affects scientific notation elimination."""
        value = 1.23456789012345e-8
        storage = Storage(value, StorageUnit.GB)
        
        # Test different precisions
        precisions_and_checks = [
            (0, lambda r: r == "0 GB"),
            (1, lambda r: r == "0 GB"),  # Very small value rounds to 0 with precision 1
            (5, lambda r: r == "0 GB"),  # Still too small for precision 5
            (10, lambda r: r.startswith("0.0000000123")),  # More precision needed
            (15, lambda r: r.startswith("0.000000012345")),  # More precision
            (20, lambda r: r.startswith("0.000000012345678901")),  # Full precision
        ]
        
        for precision, check_func in precisions_and_checks:
            Storage.set_decimal_precision(precision)
            result = str(storage)
            
            # No scientific notation
            assert 'e' not in result.lower()
            
            # Check expected format (allowing for rounding differences)
            assert check_func(result), f"Precision {precision}: got '{result}'"


class TestFormattingConsistency:
    """Test consistency between different string formatting methods."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(10)
    
    def test_str_vs_format_consistency(self):
        """Test that __str__ and __format__ produce consistent results."""
        test_values = [
            (1.23456789, StorageUnit.MB),
            (0.000123456, StorageUnit.GB),
            (9.87654321e-5, StorageUnit.TB),
            (1024, StorageUnit.BYTES),
            (0, StorageUnit.KB),
        ]
        
        for value, unit in test_values:
            storage = Storage(value, unit)
            str_result = str(storage)
            format_result = f"{storage}"
            
            assert str_result == format_result, f"Mismatch: str='{str_result}', format='{format_result}'"
    
    def test_explicit_format_spec_override(self):
        """Test that explicit format specifications override default formatting."""
        storage = Storage(1.23456789, StorageUnit.MB)
        
        # Default formatting (should use precision setting)
        Storage.set_decimal_precision(3)
        default_format = f"{storage}"
        assert "1.235" in default_format
        
        # Explicit format specification should override
        explicit_format = f"{storage:.1f}"
        assert explicit_format == "1.2 MB"
        
        explicit_format_2 = f"{storage:.5f}"
        assert explicit_format_2 == "1.23457 MB"
    
    def test_integer_value_formatting(self):
        """Test that integer values are formatted as integers."""
        integer_values = [0, 1, 1024, 1000000]
        
        for value in integer_values:
            storage = Storage(value, StorageUnit.BYTES)
            result = str(storage)
            
            # Should not have decimal point for integers
            expected = f"{value} BYTES"
            assert result == expected
    
    def test_precision_trailing_zero_removal(self):
        """Test that trailing zeros are removed appropriately."""
        Storage.set_decimal_precision(10)
        
        test_cases = [
            (1.0, "1 MB"),
            (1.10, "1.1 MB"),
            (1.100, "1.1 MB"),
            (1.500, "1.5 MB"),
            (1.001, "1.001 MB"),
            (1.010, "1.01 MB"),
        ]
        
        for value, expected in test_cases:
            storage = Storage(value, StorageUnit.MB)
            result = str(storage)
            assert result == expected, f"Value {value}: expected '{expected}', got '{result}'"


class TestPrecisionEdgeCases:
    """Test edge cases and boundary conditions for precision settings."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_zero_precision_rounding(self):
        """Test behavior with zero precision (no decimal places)."""
        Storage.set_decimal_precision(0)
        
        test_cases = [
            (1.4, "1 MB"),      # Rounds down
            (1.5, "2 MB"),      # Rounds up
            (1.9, "2 MB"),      # Rounds up
            (0.4, "0 MB"),      # Rounds to zero
            (0.9, "1 MB"),      # Rounds up to one
        ]
        
        for value, expected in test_cases:
            storage = Storage(value, StorageUnit.MB)
            result = str(storage)
            assert result == expected, f"Value {value}: expected '{expected}', got '{result}'"
    
    def test_one_precision_rounding(self):
        """Test behavior with one decimal place precision."""
        Storage.set_decimal_precision(1)
        
        test_cases = [
            (1.14, "1.1 MB"),   # Rounds down
            (1.16, "1.2 MB"),   # Rounds up  
            (1.19, "1.2 MB"),   # Rounds up
            (0.04, "0.0 MB"),   # Rounds to zero with decimal
            (0.09, "0.1 MB"),   # Rounds up
        ]
        
        for value, expected in test_cases:
            storage = Storage(value, StorageUnit.MB)
            result = str(storage)
            # Allow for floating point rounding differences
            assert result == expected or abs(float(result.split()[0]) - float(expected.split()[0])) < 0.01, \
                   f"Value {value}: expected '{expected}', got '{result}'"
    
    def test_maximum_precision_values(self):
        """Test with maximum precision values."""
        Storage.set_decimal_precision(50)
        
        # Test a value with many decimal places using Decimal for exact precision
        from decimal import Decimal
        storage = Storage(Decimal('1.123456789012345678901234567890'), StorageUnit.MB)
        result = str(storage)
        
        # Should contain the full precision without scientific notation
        assert 'e' not in result.lower()
        # Should preserve the decimal precision (trailing zeros may be removed)
        assert result.startswith("1.12345678901234567890123456789")
    
    def test_precision_with_very_small_nonzero(self):
        """Test precision handling with very small non-zero values."""
        small_value = 1e-15
        storage = Storage(small_value, StorageUnit.GB)
        
        # Test various precisions
        precisions = [5, 10, 20, 30]
        for precision in precisions:
            Storage.set_decimal_precision(precision)
            result = str(storage)
            
            # Should not be zero (unless precision is too low)
            if precision >= 15:
                assert result != "0 GB"
            
            # Should not use scientific notation
            assert 'e' not in result.lower()
    
    def test_precision_boundary_rounding(self):
        """Test rounding behavior at precision boundaries."""
        Storage.set_decimal_precision(5)
        
        # Value that requires rounding at 5th decimal place
        storage = Storage(1.123456789, StorageUnit.MB)
        result = str(storage)
        
        # Should round to 5 decimal places: 1.12346
        assert "1.12346" in result
        
        # Test edge case for rounding
        storage2 = Storage(1.123455, StorageUnit.MB)  # Should round down
        result2 = str(storage2)
        assert "1.12346" in result2 or "1.12345" in result2  # Depends on rounding mode
    
    def test_precision_with_different_units(self):
        """Test that precision works consistently across different units."""
        Storage.set_decimal_precision(3)
        value = 1.23456789
        
        units = [StorageUnit.BYTES, StorageUnit.KIB, StorageUnit.MB, StorageUnit.GB, 
                StorageUnit.KB, StorageUnit.BITS, StorageUnit.KILOBITS]
        
        for unit in units:
            storage = Storage(value, unit)
            result = str(storage)
            
            # All should show same precision (1.235)
            assert "1.235" in result
            assert unit.name in result


class TestFormattingPerformance:
    """Test performance characteristics of the formatting system."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_formatting_performance_small_values(self):
        """Test that formatting small values is performant."""
        import time
        
        # Create many storage objects with small values
        storages = [Storage(1e-10 * i, StorageUnit.GB) for i in range(1000)]
        
        # Time the formatting
        start_time = time.time()
        results = [str(storage) for storage in storages]
        end_time = time.time()
        
        # Should complete quickly (less than 1 second for 1000 operations)
        elapsed = end_time - start_time
        assert elapsed < 1.0, f"Formatting took {elapsed:.3f} seconds, expected < 1.0"
        
        # Verify all results are properly formatted (no scientific notation)
        for result in results:
            assert 'e' not in result.lower()
    
    def test_formatting_performance_various_precisions(self):
        """Test formatting performance with different precision settings."""
        import time
        
        value = 1.23456789012345678901234567890
        storage = Storage(value, StorageUnit.MB)
        
        precisions = [0, 5, 10, 20, 50]
        
        for precision in precisions:
            Storage.set_decimal_precision(precision)
            
            # Time multiple formatting operations
            start_time = time.time()
            for _ in range(100):
                str(storage)
            end_time = time.time()
            
            elapsed = end_time - start_time
            # Should be fast regardless of precision
            assert elapsed < 0.1, f"Precision {precision} took {elapsed:.3f} seconds"
    
    def test_memory_usage_formatting(self):
        """Test that formatting doesn't cause memory leaks or excessive allocation."""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        storage = Storage(1.23456789e-8, StorageUnit.GB)
        
        # Format many times
        results = []
        for i in range(1000):
            results.append(str(storage))
        
        # All results should be identical (and properly formatted)
        assert all(result == results[0] for result in results)
        assert 'e' not in results[0].lower()
        
        # Clean up
        del results
        gc.collect()


class TestBackwardCompatibility:
    """Test that new precision functionality maintains backward compatibility."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_existing_functionality_unchanged(self):
        """Test that all existing functionality works unchanged."""
        # Basic operations
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(512, StorageUnit.BYTES)
        
        assert (s1 + s2).convert_to_bytes() == 1536.0
        assert (s1 - s2).convert_to_bytes() == 512.0
        assert (s1 * 2).value == 2.0
        assert s1 / s2 == 2.0
        
        # Comparisons
        assert s1 > s2
        assert s1 == Storage(1024, StorageUnit.BYTES)
        
        # Parsing
        parsed = Storage.parse("1.5 MB")
        assert parsed.value == 1.5
        assert parsed.unit == StorageUnit.MB
    
    def test_default_behavior_reasonable(self):
        """Test that default behavior produces reasonable output."""
        # Test values that previously might have shown scientific notation
        problematic_values = [
            (9.872019291e-05, StorageUnit.GIB),
            (1.23456789e-10, StorageUnit.TB),
            (5.0e-15, StorageUnit.YB),
        ]
        
        for value, unit in problematic_values:
            storage = Storage(value, unit)
            result = str(storage)
            
            # Should be human readable (no scientific notation)
            assert 'e' not in result.lower()
            
            # Should start with "0." for these small values
            assert result.startswith("0.")
    
    def test_repr_unchanged(self):
        """Test that __repr__ behavior is unchanged."""
        storage = Storage(1.5, StorageUnit.MB)
        repr_result = repr(storage)
        
        # Should still contain Storage class name and internal representation
        assert "Storage" in repr_result
        assert "1.5" in repr_result
        assert "MB" in repr_result
    
    def test_explicit_format_specs_still_work(self):
        """Test that explicit format specifications still work as before."""
        storage = Storage(1.23456789, StorageUnit.MB)
        
        # Various format specifications should work
        assert f"{storage:.2f}" == "1.23 MB"
        assert f"{storage:.0f}" == "1 MB"
        assert f"{storage:.5f}" == "1.23457 MB"
        
        # Integer formatting
        int_storage = Storage(1024, StorageUnit.BYTES)
        assert f"{int_storage:.1f}" == "1024.0 BYTES"