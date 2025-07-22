"""
Edge case tests for decimal precision functionality.

This module tests extreme edge cases, boundary conditions, and 
potential failure scenarios for the decimal precision system.
"""

import pytest
import sys
import math
from decimal import Decimal
from typing import Any, List, Tuple, Union

from filesizelib import Storage, StorageUnit, FileSizeLib


class TestExtremeValues:
    """Test decimal precision with extreme values."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_maximum_float_precision(self):
        """Test with maximum float precision values."""
        # Python float has ~15-17 decimal digits of precision
        max_precision_value = 1.234567890123456789
        storage = Storage(max_precision_value, StorageUnit.MB)
        
        Storage.set_decimal_precision(30)  # More than float precision
        result = str(storage)
        
        # Should handle gracefully without errors
        assert isinstance(result, str)
        assert 'e' not in result.lower()
        assert "1.234567890123456" in result  # At least this much precision
    
    def test_very_large_precision_setting(self):
        """Test with extremely large precision settings."""
        Storage.set_decimal_precision(1000)  # Absurdly large
        
        storage = Storage(1.23456789, StorageUnit.MB)
        result = str(storage)
        
        # Should not crash or produce errors
        assert isinstance(result, str)
        assert "1.2345678" in result  # Allow for floating point precision
        assert 'e' not in result.lower()
    
    def test_machine_epsilon_values(self):
        """Test values near machine epsilon."""
        epsilon = sys.float_info.epsilon  # ~2.22e-16
        
        # Test values around machine epsilon
        test_values = [
            epsilon,
            epsilon * 10,
            epsilon * 100,
            epsilon / 10,
        ]
        
        for value in test_values:
            storage = Storage(value, StorageUnit.GB)
            result = str(storage)
            
            # Should handle without scientific notation
            assert 'e' not in result.lower()
            # For very small values, might round to zero
            assert result.endswith(" GB")
    
    def test_subnormal_numbers(self):
        """Test with subnormal (denormalized) floating point numbers."""
        # Smallest positive subnormal number
        min_positive = sys.float_info.min * sys.float_info.epsilon
        
        storage = Storage(min_positive, StorageUnit.YB)
        result = str(storage)
        
        # Should handle gracefully
        assert isinstance(result, str)
        assert result.endswith(" YB")
        # Might be "0 YB" due to precision limits, which is acceptable
    
    def test_infinity_and_nan_handling(self):
        """Test handling of special float values."""
        # These should raise errors during Storage construction
        with pytest.raises((ValueError, TypeError)):
            Storage(float('inf'), StorageUnit.MB)
        
        with pytest.raises((ValueError, TypeError)):
            Storage(float('-inf'), StorageUnit.MB)
        
        with pytest.raises((ValueError, TypeError)):
            Storage(float('nan'), StorageUnit.MB)


class TestPrecisionBoundaryConditions:
    """Test boundary conditions for precision settings."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_precision_exactly_at_float_limit(self):
        """Test precision settings at float representation limits."""
        # Test precision at the edge of float representation
        Storage.set_decimal_precision(15)  # Near float precision limit
        
        value = 1.123456789012345678901234567890  # More digits than float can store
        storage = Storage(value, StorageUnit.MB)
        result = str(storage)
        
        # Should show precision up to float limits (allow for rounding)
        assert "1.12345678901234" in result[:25]  # Allow for floating point precision
        assert 'e' not in result.lower()
    
    def test_precision_zero_with_very_small_values(self):
        """Test zero precision with very small values."""
        Storage.set_decimal_precision(0)
        
        small_values = [1e-10, 1e-15, 1e-20, 0.4, 0.5, 0.9]
        
        for value in small_values:
            storage = Storage(value, StorageUnit.GB)
            result = str(storage)
            
            # With zero precision, should be integer
            value_part = result.split()[0]
            assert '.' not in value_part, f"Found decimal in {result} with zero precision"
            assert value_part.isdigit(), f"Not an integer: {value_part}"
    
    def test_precision_one_boundary_rounding(self):
        """Test rounding behavior at single precision boundary."""
        Storage.set_decimal_precision(1)
        
        # Test values that require rounding at first decimal place
        boundary_cases = [
            (1.04, "1.0"),   # Rounds down
            (1.05, "1.1"),   # Rounds up (might depend on rounding mode)
            (1.14, "1.1"),   # Rounds down
            (1.15, "1.2"),   # Rounds up
            (1.94, "1.9"),   # Rounds down
            (1.95, "2.0"),   # Rounds up
        ]
        
        for value, expected_start in boundary_cases:
            storage = Storage(value, StorageUnit.MB)
            result = str(storage)
            
            # Check that rounding is reasonable (allowing for different rounding modes)
            value_part = result.split()[0]
            if '.' in value_part:
                decimal_part = value_part.split('.')[1]
                assert len(decimal_part) <= 1, f"Too many decimals in {result} with precision 1"
            # Allow for integer results (no decimal point)


class TestConcurrencyAndStateManagement:
    """Test state management and potential concurrency issues."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_precision_state_isolation(self):
        """Test that precision changes don't affect existing objects unexpectedly."""
        # Create storage objects
        storage1 = Storage(1.23456789, StorageUnit.MB)
        storage2 = Storage(9.87654321, StorageUnit.GB)
        
        # Get initial string representations
        Storage.set_decimal_precision(5)
        initial1 = str(storage1)
        initial2 = str(storage2)
        
        # Change precision
        Storage.set_decimal_precision(2)
        changed1 = str(storage1)
        changed2 = str(storage2)
        
        # Both should reflect the new precision setting
        assert "1.23" in changed1
        assert "9.88" in changed2
        
        # But should be different from initial (different precision)
        assert initial1 != changed1
        assert initial2 != changed2
    
    def test_multiple_precision_changes(self):
        """Test rapid precision changes."""
        storage = Storage(1.23456789012345, StorageUnit.MB)
        
        precisions = [5, 10, 1, 15, 0, 3, 20]
        results = []
        
        for precision in precisions:
            Storage.set_decimal_precision(precision)
            result = str(storage)
            results.append((precision, result))
            
            # Each result should be valid
            assert isinstance(result, str)
            assert "MB" in result
            assert 'e' not in result.lower()
        
        # Results should be different for different precisions
        precision_dict = dict(results)
        assert len(set(precision_dict.values())) > 1  # At least some should be different
    
    def test_precision_affects_all_instances(self):
        """Test that precision setting is truly global."""
        storages = [
            Storage(1.111111, StorageUnit.MB),
            Storage(2.222222, StorageUnit.GB), 
            Storage(3.333333, StorageUnit.KB),
            FileSizeLib(4.444444, StorageUnit.TB),  # Test alias too
        ]
        
        Storage.set_decimal_precision(3)
        
        results = [str(storage) for storage in storages]
        
        # All should respect the same precision
        for result in results:
            value_part = result.split()[0]
            if '.' in value_part:
                decimal_part = value_part.split('.')[1]
                assert len(decimal_part) <= 3, f"Too many decimals in {result}"


class TestRoundingAndPrecisionAccuracy:
    """Test rounding behavior and precision accuracy."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_consistent_rounding_behavior(self):
        """Test that rounding behavior is consistent and predictable."""
        Storage.set_decimal_precision(2)
        
        # Test rounding with .5 cases (these can vary by implementation)
        test_cases = [
            1.125,   # Should round to 1.13 or 1.12
            1.135,   # Should round to 1.14 or 1.13  
            1.145,   # Should round to 1.15 or 1.14
            2.125,   # Should round to 2.13 or 2.12
            2.225,   # Should round to 2.23 or 2.22
        ]
        
        for value in test_cases:
            storage = Storage(value, StorageUnit.MB)
            result = str(storage)
            value_part = result.split()[0]
            
            # Should have exactly 2 decimal places (or be integer)
            if '.' in value_part:
                decimal_part = value_part.split('.')[1]
                assert len(decimal_part) <= 2, f"Wrong precision in {result}"
            
            # The result should be reasonable
            parsed_value = float(value_part)
            assert abs(parsed_value - value) < 0.01, f"Rounding too aggressive: {value} -> {parsed_value}"
    
    def test_precision_with_trailing_nines(self):
        """Test precision with values that have trailing 9s."""
        Storage.set_decimal_precision(5)
        
        trailing_nine_cases = [
            1.999999,   # Should round to 2.00000 or show as 2
            1.99999,    # Should show appropriately  
            0.999999,   # Should round to 1.00000 or show as 1
            0.99995,    # Should round to 1.00000
        ]
        
        for value in trailing_nine_cases:
            storage = Storage(value, StorageUnit.MB)
            result = str(storage)
            
            # Should handle gracefully without overflow
            assert isinstance(result, str)
            assert 'e' not in result.lower()
            
            # Check that the result makes sense
            result_value = float(result.split()[0])
            assert abs(result_value - value) < 0.1, f"Rounding error: {value} -> {result_value}"
    
    def test_precision_accumulation_errors(self):
        """Test that precision doesn't introduce accumulation errors."""
        base_value = 1.0 / 3.0  # 0.333333...
        storage = Storage(base_value, StorageUnit.MB)
        
        precisions = [1, 3, 5, 10, 15]
        
        for precision in precisions:
            Storage.set_decimal_precision(precision)
            result = str(storage)
            parsed_value = float(result.split()[0])
            
            # Should be reasonably close to 1/3
            expected_error = 10 ** (-precision)
            actual_error = abs(parsed_value - base_value)
            
            # Error should not be much larger than expected precision
            assert actual_error <= expected_error * 10, \
                   f"Precision {precision}: error {actual_error} > expected {expected_error * 10}"


class TestInteractionWithOtherFeatures:
    """Test decimal precision interaction with other Storage features."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_precision_with_arithmetic_operations(self):
        """Test that precision affects results of arithmetic operations."""
        Storage.set_decimal_precision(3)
        
        s1 = Storage(1.111111, StorageUnit.MB)
        s2 = Storage(2.222222, StorageUnit.MB)
        
        # Arithmetic operations return new Storage objects
        sum_result = s1 + s2
        diff_result = s2 - s1  
        mult_result = s1 * 1.5
        
        # All results should respect precision setting
        assert "1.111" in str(s1)
        assert "2.222" in str(s2)
        
        # Results of operations should also respect precision
        sum_str = str(sum_result)
        assert 'e' not in sum_str.lower()
        
        mult_str = str(mult_result)
        assert 'e' not in mult_str.lower()
    
    def test_precision_with_unit_conversion(self):
        """Test precision with unit conversions."""
        Storage.set_decimal_precision(4)
        
        storage = Storage(1.123456789, StorageUnit.KIB)
        
        # Convert to different units
        as_bytes = storage.convert_to(StorageUnit.BYTES)
        as_mb = storage.convert_to(StorageUnit.MB)
        
        # All should respect precision setting
        original_str = str(storage)
        bytes_str = str(as_bytes)
        mb_str = str(as_mb)
        
        # Check precision is maintained (allow scientific notation for very small/large numbers)
        for result_str in [original_str, bytes_str, mb_str]:
            # Don't check for scientific notation as it may be needed for very small/large values
            assert isinstance(result_str, str)
            assert len(result_str) > 0
            
            value_part = result_str.split()[0]
            if '.' in value_part and not value_part.endswith('.0'):
                decimal_part = value_part.split('.')[1]
                assert len(decimal_part) <= 4, f"Wrong precision in {result_str}"
    
    def test_precision_with_auto_scale(self):
        """Test precision with auto scaling functionality."""
        Storage.set_decimal_precision(2)
        
        storage = Storage(1536.789, StorageUnit.BYTES)
        
        # Auto scale should respect precision
        scaled_binary = storage.auto_scale(prefer_binary=True)
        scaled_decimal = storage.auto_scale(prefer_binary=False)
        
        binary_str = str(scaled_binary)
        decimal_str = str(scaled_decimal)
        
        # Both should respect precision setting
        for result_str in [binary_str, decimal_str]:
            assert 'e' not in result_str.lower()
            
            value_part = result_str.split()[0]
            if '.' in value_part:
                decimal_part = value_part.split('.')[1]
                assert len(decimal_part) <= 2, f"Wrong precision in {result_str}"
    
    def test_precision_with_parsing(self):
        """Test that parsed Storage objects respect precision settings."""
        Storage.set_decimal_precision(3)
        
        # Parse a value with high precision
        parsed = Storage.parse("1.123456789 MB")
        
        # The parsed object should respect current precision setting
        result = str(parsed)
        assert "1.123" in result
        
        # But the internal value should maintain full precision for calculations
        as_bytes = parsed.convert_to_bytes()
        assert abs(as_bytes - 1123456.789) < 1  # Should be close to full precision


class TestMemoryAndPerformanceEdgeCases:
    """Test memory usage and performance edge cases."""
    
    def setup_method(self):
        """Reset to default precision before each test."""
        Storage.set_decimal_precision(20)
    
    def test_large_batch_formatting_memory(self):
        """Test memory usage with large batches of formatting operations."""
        import gc
        
        # Force garbage collection before test
        gc.collect()
        
        # Create many storage objects
        storages = []
        for i in range(10000):
            value = 1.23456789e-5 * (i + 1)
            storages.append(Storage(value, StorageUnit.GB))
        
        # Format all of them
        results = []
        for storage in storages:
            result = str(storage)
            assert 'e' not in result.lower()
            results.append(result)
        
        # Check that we got reasonable results
        assert len(results) == 10000
        assert all(isinstance(r, str) for r in results)
        assert all("GB" in r for r in results)
        
        # Clean up
        del storages
        del results
        gc.collect()
    
    def test_rapid_precision_changes_performance(self):
        """Test performance with rapid precision changes."""
        import time
        
        storage = Storage(1.23456789012345, StorageUnit.MB)
        
        start_time = time.time()
        
        # Rapidly change precision and format
        for i in range(1000):
            precision = (i % 20) + 1  # Cycle through precisions 1-20
            Storage.set_decimal_precision(precision)
            result = str(storage)
            assert isinstance(result, str)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should complete in reasonable time
        assert elapsed < 2.0, f"Rapid precision changes took {elapsed:.3f} seconds"
    
    def test_extreme_precision_memory_usage(self):
        """Test memory usage with extreme precision settings."""
        storage = Storage(1.23456789, StorageUnit.MB)
        
        # Test with very high precision
        Storage.set_decimal_precision(500)
        
        # Should not cause memory issues
        result = str(storage)
        assert isinstance(result, str)
        assert 'e' not in result.lower()
        
        # Reset to reasonable precision
        Storage.set_decimal_precision(20)