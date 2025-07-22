"""
Performance tests for convenient conversion methods in the filesizelib library.

This module tests the performance characteristics of the new convenient
conversion methods to ensure they don't introduce significant overhead.
"""

import pytest
import time
from filesizelib import Storage, StorageUnit


class TestConversionMethodsPerformance:
    """Test performance of convenient conversion methods."""
    
    def test_binary_conversion_performance(self):
        """Test performance of binary conversion methods."""
        storage = Storage(1024, StorageUnit.MIB)
        iterations = 1000
        
        # Time convenient methods
        start_time = time.perf_counter()
        for _ in range(iterations):
            result = storage.convert_to_gib()
        convenient_time = time.perf_counter() - start_time
        
        # Time traditional method
        start_time = time.perf_counter()
        for _ in range(iterations):
            result = storage.convert_to(StorageUnit.GIB)
        traditional_time = time.perf_counter() - start_time
        
        # Performance should be comparable (within 100% overhead)
        overhead_ratio = convenient_time / traditional_time
        assert overhead_ratio < 2.0, f"Convenient method overhead too high: {overhead_ratio:.2f}x"
        
        # Both should be fast (< 1ms per conversion)
        assert convenient_time / iterations < 0.001, "Convenient method too slow"
        assert traditional_time / iterations < 0.001, "Traditional method too slow"
    
    def test_decimal_conversion_performance(self):
        """Test performance of decimal conversion methods."""
        storage = Storage(1000, StorageUnit.MB)
        iterations = 1000
        
        # Time convenient methods
        start_time = time.perf_counter()
        for _ in range(iterations):
            result = storage.convert_to_gb()
        convenient_time = time.perf_counter() - start_time
        
        # Time traditional method
        start_time = time.perf_counter()
        for _ in range(iterations):
            result = storage.convert_to(StorageUnit.GB)
        traditional_time = time.perf_counter() - start_time
        
        # Performance should be comparable
        overhead_ratio = convenient_time / traditional_time
        assert overhead_ratio < 1.5, f"Convenient method overhead too high: {overhead_ratio:.2f}x"
    
    def test_bit_conversion_performance(self):
        """Test performance of bit conversion methods."""
        storage = Storage(1, StorageUnit.GB)
        iterations = 1000
        
        # Time convenient methods
        start_time = time.perf_counter()
        for _ in range(iterations):
            result = storage.convert_to_megabits()
        convenient_time = time.perf_counter() - start_time
        
        # Time traditional method
        start_time = time.perf_counter()
        for _ in range(iterations):
            result = storage.convert_to(StorageUnit.MEGABITS)
        traditional_time = time.perf_counter() - start_time
        
        # Performance should be comparable
        overhead_ratio = convenient_time / traditional_time
        assert overhead_ratio < 1.5, f"Convenient method overhead too high: {overhead_ratio:.2f}x"
    
    def test_chained_conversion_performance(self):
        """Test performance of chained conversions."""
        storage = Storage(1, StorageUnit.TIB)
        iterations = 100
        
        # Time chained convenient methods
        start_time = time.perf_counter()
        for _ in range(iterations):
            result = storage.convert_to_gib().convert_to_mib().convert_to_kib()
        chained_time = time.perf_counter() - start_time
        
        # Time traditional chained methods
        start_time = time.perf_counter()
        for _ in range(iterations):
            result = (storage.convert_to(StorageUnit.GIB)
                           .convert_to(StorageUnit.MIB)
                           .convert_to(StorageUnit.KIB))
        traditional_time = time.perf_counter() - start_time
        
        # Performance should be comparable
        overhead_ratio = chained_time / traditional_time
        assert overhead_ratio < 1.5, f"Chained method overhead too high: {overhead_ratio:.2f}x"
        
        # Should be reasonably fast (< 10ms per chain)
        assert chained_time / iterations < 0.01, "Chained conversions too slow"
    
    def test_memory_usage(self):
        """Test that convenient methods don't create excessive objects."""
        import gc
        
        storage = Storage(1, StorageUnit.GIB)
        
        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many conversions
        results = []
        for i in range(100):
            results.append(storage.convert_to_mib())
            results.append(storage.convert_to_gb())
            results.append(storage.convert_to_bits())
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Should not create excessive objects (allow some growth)
        object_growth = final_objects - initial_objects
        assert object_growth < 1000, f"Too many objects created: {object_growth}"
    
    def test_bulk_conversion_performance(self):
        """Test performance with bulk operations."""
        storages = [Storage(i, StorageUnit.KIB) for i in range(1, 1001)]
        
        # Time bulk convenient conversions
        start_time = time.perf_counter()
        results = [s.convert_to_mb() for s in storages]
        convenient_time = time.perf_counter() - start_time
        
        # Time bulk traditional conversions
        start_time = time.perf_counter()
        results = [s.convert_to(StorageUnit.MB) for s in storages]
        traditional_time = time.perf_counter() - start_time
        
        # Should be comparable performance
        overhead_ratio = convenient_time / traditional_time
        assert overhead_ratio < 1.5, f"Bulk conversion overhead too high: {overhead_ratio:.2f}x"
        
        # Should complete within reasonable time (< 100ms for 1000 conversions)
        assert convenient_time < 0.1, "Bulk conversions too slow"


class TestConversionMethodsStress:
    """Stress tests for convenient conversion methods."""
    
    def test_large_value_conversions(self):
        """Test conversions with very large values."""
        large_storage = Storage(1e15, StorageUnit.BYTES)
        
        # Should handle large values without issues
        result = large_storage.convert_to_yb()
        assert result.value > 0
        assert result.unit == StorageUnit.YB
        
        # Should maintain precision
        back_converted = result.convert_to(StorageUnit.BYTES)
        relative_error = abs(back_converted.value - large_storage.value) / large_storage.value
        assert relative_error < 1e-10, "Large value precision loss"
    
    def test_small_value_conversions(self):
        """Test conversions with very small values."""
        small_storage = Storage(1e-10, StorageUnit.BYTES)
        
        # Should handle small values without issues
        result = small_storage.convert_to_bits()
        assert result.value > 0
        assert result.unit == StorageUnit.BITS
        
        # Should maintain precision
        back_converted = result.convert_to(StorageUnit.BYTES)
        relative_error = abs(back_converted.value - small_storage.value) / small_storage.value
        assert relative_error < 1e-10, "Small value precision loss"
    
    def test_repeated_conversions(self):
        """Test repeated conversions for consistency."""
        storage = Storage(1.5, StorageUnit.GIB)
        
        # Perform same conversion many times
        results = []
        for _ in range(1000):
            result = storage.convert_to_mb()
            results.append(result.value)
        
        # All results should be identical
        assert all(r == results[0] for r in results), "Inconsistent conversion results"
        
        # Should match traditional method
        traditional_result = storage.convert_to(StorageUnit.MB)
        assert results[0] == traditional_result.value, "Mismatch with traditional method"
    
    def test_extreme_chaining(self):
        """Test extreme method chaining."""
        storage = Storage(1, StorageUnit.TB)
        
        # Chain many conversions
        result = (storage
                 .convert_to_gb()
                 .convert_to_mb()
                 .convert_to_kb()
                 .convert_to(StorageUnit.BYTES)
                 .convert_to_bits()
                 .convert_to_kilobits()
                 .convert_to_megabits()
                 .convert_to_gigabits()
                 .convert_to(StorageUnit.TERABITS))
        
        # Should maintain reasonable precision
        original_bits = storage.convert_to(StorageUnit.TERABITS)
        relative_error = abs(result.value - original_bits.value) / original_bits.value
        assert relative_error < 1e-6, "Extreme chaining precision loss"


class TestConversionMethodsConcurrency:
    """Test convenient conversion methods under concurrent access."""
    
    def test_thread_safety(self):
        """Test that conversions are thread-safe."""
        import threading
        import concurrent.futures
        
        storage = Storage(1, StorageUnit.GIB)
        results = []
        errors = []
        
        def convert_worker():
            try:
                result = storage.convert_to_mib()
                results.append(result.value)
            except Exception as e:
                errors.append(e)
        
        # Run concurrent conversions
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(convert_worker) for _ in range(100)]
            concurrent.futures.wait(futures)
        
        # Should have no errors
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        
        # All results should be identical
        assert len(results) == 100, "Missing results"
        assert all(r == results[0] for r in results), "Inconsistent concurrent results"
        
        # Should match expected value
        expected = 1024.0  # 1 GiB = 1024 MiB
        assert results[0] == expected, f"Incorrect concurrent result: {results[0]}"