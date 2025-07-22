"""
Integration tests for the filesizelib library.

This module tests the integration between different components and
provides comprehensive data-driven tests for real-world scenarios.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import List, Tuple, Any

from filesizelib import Storage, StorageUnit


class TestPackageIntegration:
    """Test integration between different package components."""
    
    def test_package_imports(self):
        """Test that all expected components can be imported."""
        # Test main imports
        from filesizelib import Storage, StorageUnit
        from filesizelib.platform_storage import WindowsStorage, LinuxStorage, MacStorage
        
        # Verify classes exist and are callable
        assert callable(Storage)
        assert callable(WindowsStorage)
        assert callable(LinuxStorage)
        assert callable(MacStorage)
        
        # Verify enum exists
        assert hasattr(StorageUnit, 'BYTES')
        assert hasattr(StorageUnit, 'KIB')
        assert hasattr(StorageUnit, 'MB')
    
    def test_cross_unit_operations(self):
        """Test operations across different unit types."""
        # Mix binary, decimal, and bit units
        binary_storage = Storage(1, StorageUnit.KIB)
        decimal_storage = Storage(1, StorageUnit.KB)
        bit_storage = Storage(8192, StorageUnit.BITS)  # 1 KiB
        
        # All should work together
        total = binary_storage + decimal_storage + bit_storage
        expected_bytes = 1024 + 1000 + 1024  # 3048 bytes
        assert total.convert_to_bytes() == expected_bytes
        
        # Comparisons should work
        assert binary_storage > decimal_storage
        assert binary_storage == bit_storage
        assert decimal_storage < bit_storage
    
    def test_parsing_to_platform_operations(self):
        """Test parsing strings and using with platform operations."""
        # Parse various formats
        sizes = [
            Storage.parse("1.5 MB"),
            Storage.parse("512 KiB"),
            Storage.parse("2,5 GB"),
            Storage.parse("1024"),  # bytes
        ]
        
        # Sum them up
        total = sum(sizes[1:], sizes[0])  # Start with first, add rest
        
        # Should work with platform detection
        platform_storage = Storage.get_platform_storage()
        assert isinstance(platform_storage, Storage)
        
        # Platform storage should support all operations
        platform_total = platform_storage * 0  # Start with zero
        for size in sizes:
            platform_total = platform_total + size
        
        assert platform_total == total
    
    def test_round_trip_conversions(self):
        """Test round-trip conversions maintain precision."""
        original = Storage(1.5, StorageUnit.MB)
        
        # Convert through various units and back
        as_bytes = original.convert_to(StorageUnit.BYTES)
        as_kib = as_bytes.convert_to(StorageUnit.KIB)
        as_kb = as_kib.convert_to(StorageUnit.KB)
        back_to_mb = as_kb.convert_to(StorageUnit.MB)
        
        # Should maintain precision within tolerance
        assert abs(original.convert_to_bytes() - back_to_mb.convert_to_bytes()) < 1e-10
    
    def test_string_parsing_with_auto_scaling(self):
        """Test parsing strings and auto-scaling integration."""
        large_string = "1536000000 bytes"
        parsed = Storage.parse(large_string)
        
        # Auto-scale to human readable
        binary_scaled = parsed.auto_scale(prefer_binary=True)
        decimal_scaled = parsed.auto_scale(prefer_binary=False)
        
        # Should be properly scaled
        assert binary_scaled.unit in [StorageUnit.GIB, StorageUnit.MIB]
        assert decimal_scaled.unit in [StorageUnit.GB, StorageUnit.MB]
        
        # Should maintain byte equivalence
        assert abs(parsed.convert_to_bytes() - binary_scaled.convert_to_bytes()) < 1e-10
        assert abs(parsed.convert_to_bytes() - decimal_scaled.convert_to_bytes()) < 1e-10


class TestDataDrivenArithmetic:
    """Data-driven tests for arithmetic operations."""
    
    @pytest.mark.parametrize("value1,unit1,value2,unit2,operation,expected_bytes", [
        # Binary + Binary
        (1, StorageUnit.KIB, 1, StorageUnit.KIB, "add", 2048),
        (2, StorageUnit.MIB, 1, StorageUnit.MIB, "add", 3145728),
        (1, StorageUnit.GIB, 512, StorageUnit.MIB, "add", 1610612736),
        
        # Decimal + Decimal
        (1, StorageUnit.KB, 1, StorageUnit.KB, "add", 2000),
        (2, StorageUnit.MB, 1, StorageUnit.MB, "add", 3000000),
        (1, StorageUnit.GB, 500, StorageUnit.MB, "add", 1500000000),
        
        # Binary + Decimal
        (1, StorageUnit.KIB, 1, StorageUnit.KB, "add", 2024),
        (1, StorageUnit.MIB, 1, StorageUnit.MB, "add", 2048576),
        
        # Bit units
        (8, StorageUnit.BITS, 1, StorageUnit.BYTES, "add", 2),
        (1024, StorageUnit.KILOBITS, 1, StorageUnit.KB, "add", 129000),
        
        # Subtraction
        (2, StorageUnit.KIB, 1, StorageUnit.KIB, "sub", 1024),
        (1, StorageUnit.MB, 500, StorageUnit.KB, "sub", 500000),
        (1, StorageUnit.GIB, 1, StorageUnit.GB, "sub", 73741824),
        
        # Zero operations
        (1, StorageUnit.KIB, 0, StorageUnit.BYTES, "add", 1024),
        (1, StorageUnit.KIB, 0, StorageUnit.BYTES, "sub", 1024),
        (0, StorageUnit.BYTES, 1, StorageUnit.KIB, "add", 1024),
    ])
    def test_arithmetic_operations_comprehensive(self, value1: float, unit1: StorageUnit, 
                                               value2: float, unit2: StorageUnit,
                                               operation: str, expected_bytes: float):
        """Test arithmetic operations with comprehensive data."""
        s1 = Storage(value1, unit1)
        s2 = Storage(value2, unit2)
        
        if operation == "add":
            result = s1 + s2
        elif operation == "sub":
            result = s1 - s2
        else:
            pytest.fail(f"Unknown operation: {operation}")
        
        assert abs(result.convert_to_bytes() - expected_bytes) < 1e-10
    
    @pytest.mark.parametrize("value,unit,factor,expected_value,expected_unit", [
        # Basic multiplication
        (1, StorageUnit.KIB, 2, 2, StorageUnit.KIB),
        (1.5, StorageUnit.MB, 3, 4.5, StorageUnit.MB),
        (2, StorageUnit.GB, 0.5, 1, StorageUnit.GB),
        
        # Multiplication by zero
        (100, StorageUnit.GIB, 0, 0, StorageUnit.GIB),
        
        # Multiplication by one
        (42, StorageUnit.TB, 1, 42, StorageUnit.TB),
        
        # Fractional multiplication
        (4, StorageUnit.MIB, 0.25, 1, StorageUnit.MIB),
        (3, StorageUnit.KB, 1/3, 1, StorageUnit.KB),
    ])
    def test_multiplication_comprehensive(self, value: float, unit: StorageUnit, factor: float,
                                        expected_value: float, expected_unit: StorageUnit):
        """Test multiplication with comprehensive data."""
        storage = Storage(value, unit)
        result = storage * factor
        
        assert abs(result.value - expected_value) < 1e-10
        assert result.unit == expected_unit
    
    @pytest.mark.parametrize("value,unit,divisor,expected_value,expected_unit", [
        # Basic division
        (2, StorageUnit.KIB, 2, 1, StorageUnit.KIB),
        (4.5, StorageUnit.MB, 3, 1.5, StorageUnit.MB),
        (1, StorageUnit.GB, 0.5, 2, StorageUnit.GB),
        
        # Division by one
        (42, StorageUnit.TB, 1, 42, StorageUnit.TB),
        
        # Fractional division
        (1, StorageUnit.MIB, 0.25, 4, StorageUnit.MIB),
        (1, StorageUnit.KB, 1/3, 3, StorageUnit.KB),
    ])
    def test_division_comprehensive(self, value: float, unit: StorageUnit, divisor: float,
                                  expected_value: float, expected_unit: StorageUnit):
        """Test division with comprehensive data."""
        storage = Storage(value, unit)
        result = storage / divisor
        
        assert abs(result.value - expected_value) < 1e-10
        assert result.unit == expected_unit


class TestDataDrivenComparisons:
    """Data-driven tests for comparison operations."""
    
    @pytest.mark.parametrize("value1,unit1,value2,unit2,expected_eq,expected_lt,expected_gt", [
        # Equal values in same units
        (1, StorageUnit.KIB, 1, StorageUnit.KIB, True, False, False),
        (2.5, StorageUnit.MB, 2.5, StorageUnit.MB, True, False, False),
        
        # Equal values in different units
        (1, StorageUnit.KIB, 1024, StorageUnit.BYTES, True, False, False),
        (1, StorageUnit.MB, 1000, StorageUnit.KB, True, False, False),
        (8, StorageUnit.BITS, 1, StorageUnit.BYTES, True, False, False),
        
        # Different values, same units
        (1, StorageUnit.KIB, 2, StorageUnit.KIB, False, True, False),
        (3, StorageUnit.MB, 1, StorageUnit.MB, False, False, True),
        
        # Different values, different units
        (1, StorageUnit.KIB, 500, StorageUnit.BYTES, False, False, True),
        (500, StorageUnit.KB, 1, StorageUnit.MB, False, True, False),
        (1, StorageUnit.GIB, 1, StorageUnit.GB, False, False, True),
        
        # Zero comparisons
        (0, StorageUnit.BYTES, 0, StorageUnit.KIB, True, False, False),
        (1, StorageUnit.BYTES, 0, StorageUnit.MB, False, False, True),
        (0, StorageUnit.GB, 1, StorageUnit.BYTES, False, True, False),
        
        # Bit unit comparisons
        (16, StorageUnit.BITS, 2, StorageUnit.BYTES, True, False, False),
        (4, StorageUnit.BITS, 1, StorageUnit.BYTES, False, True, False),
        (1, StorageUnit.KILOBITS, 100, StorageUnit.BYTES, False, False, True),
    ])
    def test_comparisons_comprehensive(self, value1: float, unit1: StorageUnit,
                                     value2: float, unit2: StorageUnit,
                                     expected_eq: bool, expected_lt: bool, expected_gt: bool):
        """Test comparisons with comprehensive data."""
        s1 = Storage(value1, unit1)
        s2 = Storage(value2, unit2)
        
        assert (s1 == s2) == expected_eq
        assert (s1 < s2) == expected_lt
        assert (s1 > s2) == expected_gt
        
        # Derived comparisons
        assert (s1 != s2) == (not expected_eq)
        assert (s1 <= s2) == (expected_eq or expected_lt)
        assert (s1 >= s2) == (expected_eq or expected_gt)


class TestDataDrivenStringParsing:
    """Data-driven tests for string parsing functionality."""
    
    @pytest.mark.parametrize("input_string,expected_value,expected_unit", [
        # Basic units with spaces
        ("1 B", 1, StorageUnit.BYTES),
        ("1 byte", 1, StorageUnit.BYTES),
        ("1 bytes", 1, StorageUnit.BYTES),
        
        # Binary units
        ("1 KiB", 1, StorageUnit.KIB),
        ("1 MiB", 1, StorageUnit.MIB),
        ("1 GiB", 1, StorageUnit.GIB),
        ("1 TiB", 1, StorageUnit.TIB),
        
        # Decimal units
        ("1 KB", 1, StorageUnit.KB),
        ("1 MB", 1, StorageUnit.MB),
        ("1 GB", 1, StorageUnit.GB),
        ("1 TB", 1, StorageUnit.TB),
        
        # Bit units
        ("1 bit", 1, StorageUnit.BITS),
        ("8 bits", 8, StorageUnit.BITS),
        ("1 kilobit", 1, StorageUnit.KILOBITS),
        ("1 megabit", 1, StorageUnit.MEGABITS),
        
        # Case variations
        ("1 kb", 1, StorageUnit.KB),
        ("1 Kb", 1, StorageUnit.KB),
        ("1 kB", 1, StorageUnit.KB),
        ("1 KB", 1, StorageUnit.KB),
        ("1 kib", 1, StorageUnit.KIB),
        ("1 KIB", 1, StorageUnit.KIB),
        
        # No spaces
        ("1KB", 1, StorageUnit.KB),
        ("1MB", 1, StorageUnit.MB),
        ("1GB", 1, StorageUnit.GB),
        ("1KiB", 1, StorageUnit.KIB),
        ("1MiB", 1, StorageUnit.MIB),
        
        # Decimal values with dot
        ("1.5 MB", 1.5, StorageUnit.MB),
        ("2.75 GB", 2.75, StorageUnit.GB),
        ("0.5 KiB", 0.5, StorageUnit.KIB),
        ("3.14159 TB", 3.14159, StorageUnit.TB),
        
        # Decimal values with comma
        ("1,5 MB", 1.5, StorageUnit.MB),
        ("2,75 GB", 2.75, StorageUnit.GB),
        ("0,5 KiB", 0.5, StorageUnit.KIB),
        
        # Numbers without units (default to bytes)
        ("0", 0, StorageUnit.BYTES),
        ("1", 1, StorageUnit.BYTES),
        ("1024", 1024, StorageUnit.BYTES),
        ("1.5", 1.5, StorageUnit.BYTES),
        ("1,5", 1.5, StorageUnit.BYTES),
        
        # Short aliases
        ("1 k", 1, StorageUnit.KB),
        ("1 m", 1, StorageUnit.MB),
        ("1 g", 1, StorageUnit.GB),
        ("1 t", 1, StorageUnit.TB),
        ("1 ki", 1, StorageUnit.KIB),
        ("1 mi", 1, StorageUnit.MIB),
        ("1 gi", 1, StorageUnit.GIB),
        
        # Full names
        ("1 kilobyte", 1, StorageUnit.KB),
        ("1 megabyte", 1, StorageUnit.MB),
        ("1 gigabyte", 1, StorageUnit.GB),
        ("1 kibibyte", 1, StorageUnit.KIB),
        ("1 mebibyte", 1, StorageUnit.MIB),
        ("1 gibibyte", 1, StorageUnit.GIB),
        
        # Plural forms
        ("2 kilobytes", 2, StorageUnit.KB),
        ("3 megabytes", 3, StorageUnit.MB),
        ("4 kibibytes", 4, StorageUnit.KIB),
        ("5 mebibytes", 5, StorageUnit.MIB),
    ])
    def test_string_parsing_comprehensive(self, input_string: str, expected_value: float, expected_unit: StorageUnit):
        """Test string parsing with comprehensive data."""
        parsed = Storage.parse(input_string)
        assert parsed.value == expected_value
        assert parsed.unit == expected_unit
    
    @pytest.mark.parametrize("invalid_string", [
        "",           # Empty string
        "   ",        # Whitespace only
        "abc",        # No number
        "1.2.3 MB",   # Invalid number
        "MB 1",       # Wrong order
        "1 2 MB",     # Extra number
        "1..5 MB",    # Double dots
        "1,,5 MB",    # Double commas
        "invalid format",  # Invalid format
        "1. MB",      # Incomplete decimal
    ])
    def test_string_parsing_invalid_comprehensive(self, invalid_string: str):
        """Test that invalid strings raise appropriate errors."""
        with pytest.raises(ValueError):
            Storage.parse(invalid_string)


class TestDataDrivenAutoScaling:
    """Data-driven tests for auto-scaling functionality."""
    
    @pytest.mark.parametrize("bytes_value,prefer_binary,expected_value,expected_unit", [
        # Binary scaling (powers of 1024)
        (1024, True, 1, StorageUnit.KIB),
        (1536, True, 1.5, StorageUnit.KIB),
        (1048576, True, 1, StorageUnit.MIB),
        (1610612736, True, 1.5, StorageUnit.GIB),
        (1099511627776, True, 1, StorageUnit.TIB),
        
        # Decimal scaling (powers of 1000)
        (1000, False, 1, StorageUnit.KB),
        (1500, False, 1.5, StorageUnit.KB),
        (1000000, False, 1, StorageUnit.MB),
        (1500000000, False, 1.5, StorageUnit.GB),
        (1000000000000, False, 1, StorageUnit.TB),
        
        # Edge cases
        (0, True, 0, StorageUnit.BYTES),
        (0, False, 0, StorageUnit.BYTES),
        (1, True, 1, StorageUnit.BYTES),
        (1, False, 1, StorageUnit.BYTES),
        (512, True, 512, StorageUnit.BYTES),
        (500, False, 500, StorageUnit.BYTES),
        
        # Large values
        (1125899906842624, True, 1, StorageUnit.PIB),  # 1 PiB
        (1000000000000000, False, 1, StorageUnit.PB),   # 1 PB
        
        # Very large values that should use highest unit
        (1208925819614629174706176, True, 1, StorageUnit.YIB),  # 1 YiB
    ])
    def test_auto_scaling_comprehensive(self, bytes_value: int, prefer_binary: bool,
                                      expected_value: float, expected_unit: StorageUnit):
        """Test auto-scaling with comprehensive data."""
        storage = Storage(bytes_value, StorageUnit.BYTES)
        scaled = storage.auto_scale(prefer_binary=prefer_binary)
        
        assert abs(scaled.value - expected_value) < 1e-10
        assert scaled.unit == expected_unit
        
        # Verify byte equivalence
        assert abs(storage.convert_to_bytes() - scaled.convert_to_bytes()) < 1e-10


class TestDataDrivenConversions:
    """Data-driven tests for unit conversions."""
    
    @pytest.mark.parametrize("source_value,source_unit,target_unit,expected_value", [
        # Binary to binary conversions
        (1, StorageUnit.KIB, StorageUnit.BYTES, 1024),
        (1, StorageUnit.MIB, StorageUnit.KIB, 1024),
        (1, StorageUnit.GIB, StorageUnit.MIB, 1024),
        (1024, StorageUnit.BYTES, StorageUnit.KIB, 1),
        (2048, StorageUnit.KIB, StorageUnit.MIB, 2),
        
        # Decimal to decimal conversions
        (1, StorageUnit.KB, StorageUnit.BYTES, 1000),
        (1, StorageUnit.MB, StorageUnit.KB, 1000),
        (1, StorageUnit.GB, StorageUnit.MB, 1000),
        (1000, StorageUnit.BYTES, StorageUnit.KB, 1),
        (2000, StorageUnit.KB, StorageUnit.MB, 2),
        
        # Binary to decimal conversions
        (1, StorageUnit.KIB, StorageUnit.KB, 1.024),
        (1, StorageUnit.MIB, StorageUnit.MB, 1.048576),
        (1, StorageUnit.GIB, StorageUnit.GB, 1.073741824),
        
        # Decimal to binary conversions  
        (1, StorageUnit.KB, StorageUnit.KIB, 1000/1024),
        (1, StorageUnit.MB, StorageUnit.MIB, 1000000/1048576),
        (1, StorageUnit.GB, StorageUnit.GIB, 1000000000/1073741824),
        
        # Bit conversions
        (8, StorageUnit.BITS, StorageUnit.BYTES, 1),
        (1, StorageUnit.BYTES, StorageUnit.BITS, 8),
        (1, StorageUnit.KILOBITS, StorageUnit.BYTES, 125),
        (1000, StorageUnit.BYTES, StorageUnit.KILOBITS, 8),
        (1, StorageUnit.MEGABITS, StorageUnit.MB, 0.125),
        
        # Zero conversions
        (0, StorageUnit.KIB, StorageUnit.BYTES, 0),
        (0, StorageUnit.MB, StorageUnit.KB, 0),
        (0, StorageUnit.BITS, StorageUnit.BYTES, 0),
        
        # Fractional conversions
        (0.5, StorageUnit.KIB, StorageUnit.BYTES, 512),
        (1.5, StorageUnit.MB, StorageUnit.BYTES, 1500000),
        (2.5, StorageUnit.GIB, StorageUnit.MIB, 2560),
    ])
    def test_conversions_comprehensive(self, source_value: float, source_unit: StorageUnit,
                                     target_unit: StorageUnit, expected_value: float):
        """Test unit conversions with comprehensive data."""
        storage = Storage(source_value, source_unit)
        converted = storage.convert_to(target_unit)
        
        assert abs(converted.value - expected_value) < 1e-10
        assert converted.unit == target_unit
        
        # Verify round-trip conversion maintains precision
        back_converted = converted.convert_to(source_unit)
        assert abs(back_converted.value - source_value) < 1e-10


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_download_time_calculation(self):
        """Test calculating download times for files."""
        # File sizes
        song = Storage.parse("4.5 MB")
        photo = Storage.parse("2.8 MiB")
        movie = Storage.parse("1.4 GB")
        game = Storage.parse("50 GiB")
        
        # Network speeds (in bits per second)
        broadband = Storage.parse("50 Megabits")  # 50 Mbps
        fiber = Storage.parse("1 Gigabit")        # 1 Gbps
        
        # Calculate download times
        song_time_broadband = song / broadband
        movie_time_fiber = movie / fiber
        game_time_broadband = game / broadband
        
        # Verify calculations make sense
        assert song_time_broadband > 0
        assert movie_time_fiber > 0
        assert game_time_broadband > movie_time_fiber  # Game should take longer
        assert song_time_broadband < movie_time_fiber  # Song should be faster
    
    def test_storage_capacity_planning(self):
        """Test planning storage capacity for different media."""
        # Calculate storage needs
        photos = Storage.parse("2.8 MiB") * 2000      # 2000 photos
        music = Storage.parse("4.5 MB") * 500         # 500 songs
        videos = Storage.parse("1.2 GB") * 50         # 50 videos
        documents = Storage.parse("250 KB") * 1000    # 1000 documents
        
        total_needed = photos + music + videos + documents
        
        # Available storage options
        options = [
            Storage.parse("128 GB"),  # Small SSD
            Storage.parse("500 GB"),  # Medium SSD
            Storage.parse("1 TB"),    # Large SSD
            Storage.parse("2 TB"),    # HDD
        ]
        
        # Find sufficient options
        sufficient = [opt for opt in options if opt > total_needed]
        
        assert len(sufficient) > 0  # Should have some options
        assert total_needed.convert_to_bytes() > 0  # Should need some storage
    
    def test_network_bandwidth_analysis(self):
        """Test analyzing network bandwidth requirements."""
        # Different quality video streams
        low_quality = Storage.parse("500 Kilobits")    # 500 Kbps
        standard_quality = Storage.parse("2 Megabits") # 2 Mbps  
        hd_quality = Storage.parse("5 Megabits")       # 5 Mbps
        uhd_quality = Storage.parse("25 Megabits")     # 25 Mbps
        
        # Available bandwidth
        home_internet = Storage.parse("100 Megabits")  # 100 Mbps
        
        # Calculate how many streams of each quality
        low_streams = int(home_internet / low_quality)
        standard_streams = int(home_internet / standard_quality)
        hd_streams = int(home_internet / hd_quality)
        uhd_streams = int(home_internet / uhd_quality)
        
        # Verify calculations make sense
        assert low_streams > standard_streams > hd_streams > uhd_streams
        assert uhd_streams >= 1  # Should support at least one UHD stream
    
    def test_file_compression_analysis(self):
        """Test analyzing file compression ratios."""
        # Original file sizes
        document_original = Storage.parse("10 MB")
        image_original = Storage.parse("5 MiB")
        video_original = Storage.parse("1 GB")
        
        # Compressed sizes (simulated compression ratios)
        document_compressed = document_original * 0.9   # 10% compression
        image_compressed = image_original * 0.8         # 20% compression
        video_compressed = video_original * 0.7         # 30% compression
        
        # Calculate space saved
        document_saved = document_original - document_compressed
        image_saved = image_original - image_compressed
        video_saved = video_original - video_compressed
        
        total_saved = document_saved + image_saved + video_saved
        
        # Verify savings (video has most compression now)
        assert video_saved > image_saved > document_saved
        assert total_saved > Storage(0, StorageUnit.BYTES)
        assert total_saved < (document_original + image_original + video_original)