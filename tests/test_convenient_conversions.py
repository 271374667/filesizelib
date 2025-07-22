"""
Tests for convenient conversion methods in the filesizelib library.

This module tests the new convenient conversion methods (convert_to_kib, convert_to_mb, etc.)
that provide shortcuts for common unit conversions.
"""

import pytest
from filesizelib import Storage, StorageUnit


class TestBinaryConversionMethods:
    """Test convenient conversion methods for binary units."""
    
    def test_convert_to_kib(self):
        """Test convert_to_kib method."""
        # From bytes
        storage = Storage(1024, StorageUnit.BYTES)
        kib_storage = storage.convert_to_kib()
        assert kib_storage.value == 1.0
        assert kib_storage.unit == StorageUnit.KIB
        
        # From MiB
        storage = Storage(2, StorageUnit.MIB)
        kib_storage = storage.convert_to_kib()
        assert kib_storage.value == 2048.0
        assert kib_storage.unit == StorageUnit.KIB
        
        # Zero value
        storage = Storage(0, StorageUnit.GIB)
        kib_storage = storage.convert_to_kib()
        assert kib_storage.value == 0.0
        assert kib_storage.unit == StorageUnit.KIB
    
    def test_convert_to_mib(self):
        """Test convert_to_mib method."""
        # From KiB
        storage = Storage(1024, StorageUnit.KIB)
        mib_storage = storage.convert_to_mib()
        assert mib_storage.value == 1.0
        assert mib_storage.unit == StorageUnit.MIB
        
        # From bytes
        storage = Storage(1048576, StorageUnit.BYTES)
        mib_storage = storage.convert_to_mib()
        assert mib_storage.value == 1.0
        assert mib_storage.unit == StorageUnit.MIB
        
        # Fractional value
        storage = Storage(1536, StorageUnit.KIB)
        mib_storage = storage.convert_to_mib()
        assert mib_storage.value == 1.5
        assert mib_storage.unit == StorageUnit.MIB
    
    def test_convert_to_gib(self):
        """Test convert_to_gib method."""
        # From MiB
        storage = Storage(1024, StorageUnit.MIB)
        gib_storage = storage.convert_to_gib()
        assert gib_storage.value == 1.0
        assert gib_storage.unit == StorageUnit.GIB
        
        # From bytes
        storage = Storage(1073741824, StorageUnit.BYTES)
        gib_storage = storage.convert_to_gib()
        assert gib_storage.value == 1.0
        assert gib_storage.unit == StorageUnit.GIB
    
    def test_convert_to_tib(self):
        """Test convert_to_tib method."""
        # From GiB
        storage = Storage(1024, StorageUnit.GIB)
        tib_storage = storage.convert_to_tib()
        assert tib_storage.value == 1.0
        assert tib_storage.unit == StorageUnit.TIB
    
    def test_convert_to_pib(self):
        """Test convert_to_pib method."""
        # From TiB
        storage = Storage(1024, StorageUnit.TIB)
        pib_storage = storage.convert_to_pib()
        assert pib_storage.value == 1.0
        assert pib_storage.unit == StorageUnit.PIB
    
    def test_convert_to_eib(self):
        """Test convert_to_eib method."""
        # From PiB
        storage = Storage(1024, StorageUnit.PIB)
        eib_storage = storage.convert_to_eib()
        assert eib_storage.value == 1.0
        assert eib_storage.unit == StorageUnit.EIB
    
    def test_convert_to_zib(self):
        """Test convert_to_zib method."""
        # From EiB
        storage = Storage(1024, StorageUnit.EIB)
        zib_storage = storage.convert_to_zib()
        assert zib_storage.value == 1.0
        assert zib_storage.unit == StorageUnit.ZIB
    
    def test_convert_to_yib(self):
        """Test convert_to_yib method."""
        # From ZiB
        storage = Storage(1024, StorageUnit.ZIB)
        yib_storage = storage.convert_to_yib()
        assert yib_storage.value == 1.0
        assert yib_storage.unit == StorageUnit.YIB


class TestDecimalConversionMethods:
    """Test convenient conversion methods for decimal units."""
    
    def test_convert_to_kb(self):
        """Test convert_to_kb method."""
        # From bytes
        storage = Storage(1000, StorageUnit.BYTES)
        kb_storage = storage.convert_to_kb()
        assert kb_storage.value == 1.0
        assert kb_storage.unit == StorageUnit.KB
        
        # From MB
        storage = Storage(2, StorageUnit.MB)
        kb_storage = storage.convert_to_kb()
        assert kb_storage.value == 2000.0
        assert kb_storage.unit == StorageUnit.KB
        
        # Zero value
        storage = Storage(0, StorageUnit.GB)
        kb_storage = storage.convert_to_kb()
        assert kb_storage.value == 0.0
        assert kb_storage.unit == StorageUnit.KB
    
    def test_convert_to_mb(self):
        """Test convert_to_mb method."""
        # From KB
        storage = Storage(1000, StorageUnit.KB)
        mb_storage = storage.convert_to_mb()
        assert mb_storage.value == 1.0
        assert mb_storage.unit == StorageUnit.MB
        
        # From bytes
        storage = Storage(1000000, StorageUnit.BYTES)
        mb_storage = storage.convert_to_mb()
        assert mb_storage.value == 1.0
        assert mb_storage.unit == StorageUnit.MB
        
        # Fractional value
        storage = Storage(1500, StorageUnit.KB)
        mb_storage = storage.convert_to_mb()
        assert mb_storage.value == 1.5
        assert mb_storage.unit == StorageUnit.MB
    
    def test_convert_to_gb(self):
        """Test convert_to_gb method."""
        # From MB
        storage = Storage(1000, StorageUnit.MB)
        gb_storage = storage.convert_to_gb()
        assert gb_storage.value == 1.0
        assert gb_storage.unit == StorageUnit.GB
        
        # From bytes
        storage = Storage(1000000000, StorageUnit.BYTES)
        gb_storage = storage.convert_to_gb()
        assert gb_storage.value == 1.0
        assert gb_storage.unit == StorageUnit.GB
    
    def test_convert_to_tb(self):
        """Test convert_to_tb method."""
        # From GB
        storage = Storage(1000, StorageUnit.GB)
        tb_storage = storage.convert_to_tb()
        assert tb_storage.value == 1.0
        assert tb_storage.unit == StorageUnit.TB
    
    def test_convert_to_pb(self):
        """Test convert_to_pb method."""
        # From TB
        storage = Storage(1000, StorageUnit.TB)
        pb_storage = storage.convert_to_pb()
        assert pb_storage.value == 1.0
        assert pb_storage.unit == StorageUnit.PB
    
    def test_convert_to_eb(self):
        """Test convert_to_eb method."""
        # From PB
        storage = Storage(1000, StorageUnit.PB)
        eb_storage = storage.convert_to_eb()
        assert eb_storage.value == 1.0
        assert eb_storage.unit == StorageUnit.EB
    
    def test_convert_to_zb(self):
        """Test convert_to_zb method."""
        # From EB
        storage = Storage(1000, StorageUnit.EB)
        zb_storage = storage.convert_to_zb()
        assert zb_storage.value == 1.0
        assert zb_storage.unit == StorageUnit.ZB
    
    def test_convert_to_yb(self):
        """Test convert_to_yb method."""
        # From ZB
        storage = Storage(1000, StorageUnit.ZB)
        yb_storage = storage.convert_to_yb()
        assert yb_storage.value == 1.0
        assert yb_storage.unit == StorageUnit.YB


class TestBitConversionMethods:
    """Test convenient conversion methods for bit units."""
    
    def test_convert_to_bits(self):
        """Test convert_to_bits method."""
        # From bytes
        storage = Storage(1, StorageUnit.BYTES)
        bits_storage = storage.convert_to_bits()
        assert bits_storage.value == 8.0
        assert bits_storage.unit == StorageUnit.BITS
        
        # From KiB
        storage = Storage(1, StorageUnit.KIB)
        bits_storage = storage.convert_to_bits()
        assert bits_storage.value == 8192.0
        assert bits_storage.unit == StorageUnit.BITS
        
        # Zero value
        storage = Storage(0, StorageUnit.MB)
        bits_storage = storage.convert_to_bits()
        assert bits_storage.value == 0.0
        assert bits_storage.unit == StorageUnit.BITS
    
    def test_convert_to_kilobits(self):
        """Test convert_to_kilobits method."""
        # From bits
        storage = Storage(1000, StorageUnit.BITS)
        kilobits_storage = storage.convert_to_kilobits()
        assert kilobits_storage.value == 1.0
        assert kilobits_storage.unit == StorageUnit.KILOBITS
        
        # From bytes
        storage = Storage(125, StorageUnit.BYTES)  # 125 bytes = 1000 bits = 1 kilobit
        kilobits_storage = storage.convert_to_kilobits()
        assert kilobits_storage.value == 1.0
        assert kilobits_storage.unit == StorageUnit.KILOBITS
    
    def test_convert_to_megabits(self):
        """Test convert_to_megabits method."""
        # From kilobits
        storage = Storage(1000, StorageUnit.KILOBITS)
        megabits_storage = storage.convert_to_megabits()
        assert megabits_storage.value == 1.0
        assert megabits_storage.unit == StorageUnit.MEGABITS
        
        # From MB
        storage = Storage(1, StorageUnit.MB)  # 1 MB = 8 Megabits
        megabits_storage = storage.convert_to_megabits()
        assert megabits_storage.value == 8.0
        assert megabits_storage.unit == StorageUnit.MEGABITS
    
    def test_convert_to_gigabits(self):
        """Test convert_to_gigabits method."""
        # From megabits
        storage = Storage(1000, StorageUnit.MEGABITS)
        gigabits_storage = storage.convert_to_gigabits()
        assert gigabits_storage.value == 1.0
        assert gigabits_storage.unit == StorageUnit.GIGABITS
    
    def test_convert_to_terabits(self):
        """Test convert_to_terabits method."""
        # From gigabits
        storage = Storage(1000, StorageUnit.GIGABITS)
        terabits_storage = storage.convert_to_terabits()
        assert terabits_storage.value == 1.0
        assert terabits_storage.unit == StorageUnit.TERABITS


class TestConversionMethodsEquivalence:
    """Test that convenient methods are equivalent to convert_to()."""
    
    @pytest.mark.parametrize("value,unit", [
        (1024, StorageUnit.BYTES),
        (1.5, StorageUnit.MIB),
        (2048, StorageUnit.KIB),
        (0, StorageUnit.GB),
        (0.5, StorageUnit.TB),
    ])
    def test_binary_methods_equivalent_to_convert_to(self, value, unit):
        """Test that binary conversion methods are equivalent to convert_to()."""
        storage = Storage(value, unit)
        
        # Test all binary units
        assert storage.convert_to_kib() == storage.convert_to(StorageUnit.KIB)
        assert storage.convert_to_mib() == storage.convert_to(StorageUnit.MIB)
        assert storage.convert_to_gib() == storage.convert_to(StorageUnit.GIB)
        assert storage.convert_to_tib() == storage.convert_to(StorageUnit.TIB)
        assert storage.convert_to_pib() == storage.convert_to(StorageUnit.PIB)
        assert storage.convert_to_eib() == storage.convert_to(StorageUnit.EIB)
        assert storage.convert_to_zib() == storage.convert_to(StorageUnit.ZIB)
        assert storage.convert_to_yib() == storage.convert_to(StorageUnit.YIB)
    
    @pytest.mark.parametrize("value,unit", [
        (1000, StorageUnit.BYTES),
        (1.5, StorageUnit.MB),
        (2000, StorageUnit.KB),
        (0, StorageUnit.GB),
        (0.5, StorageUnit.TB),
    ])
    def test_decimal_methods_equivalent_to_convert_to(self, value, unit):
        """Test that decimal conversion methods are equivalent to convert_to()."""
        storage = Storage(value, unit)
        
        # Test all decimal units
        assert storage.convert_to_kb() == storage.convert_to(StorageUnit.KB)
        assert storage.convert_to_mb() == storage.convert_to(StorageUnit.MB)
        assert storage.convert_to_gb() == storage.convert_to(StorageUnit.GB)
        assert storage.convert_to_tb() == storage.convert_to(StorageUnit.TB)
        assert storage.convert_to_pb() == storage.convert_to(StorageUnit.PB)
        assert storage.convert_to_eb() == storage.convert_to(StorageUnit.EB)
        assert storage.convert_to_zb() == storage.convert_to(StorageUnit.ZB)
        assert storage.convert_to_yb() == storage.convert_to(StorageUnit.YB)
    
    @pytest.mark.parametrize("value,unit", [
        (8, StorageUnit.BITS),
        (1000, StorageUnit.KILOBITS),
        (1, StorageUnit.BYTES),
        (0, StorageUnit.MEGABITS),
        (0.5, StorageUnit.GIGABITS),
    ])
    def test_bit_methods_equivalent_to_convert_to(self, value, unit):
        """Test that bit conversion methods are equivalent to convert_to()."""
        storage = Storage(value, unit)
        
        # Test all bit units
        assert storage.convert_to_bits() == storage.convert_to(StorageUnit.BITS)
        assert storage.convert_to_kilobits() == storage.convert_to(StorageUnit.KILOBITS)
        assert storage.convert_to_megabits() == storage.convert_to(StorageUnit.MEGABITS)
        assert storage.convert_to_gigabits() == storage.convert_to(StorageUnit.GIGABITS)
        assert storage.convert_to_terabits() == storage.convert_to(StorageUnit.TERABITS)


class TestConversionMethodsChaining:
    """Test chaining of conversion methods."""
    
    def test_chain_binary_conversions(self):
        """Test chaining binary conversion methods."""
        storage = Storage(1, StorageUnit.GIB)
        
        # Chain conversions
        result = storage.convert_to_mib().convert_to_kib().convert_to(StorageUnit.BYTES)
        
        # Should maintain equivalence
        assert abs(result.convert_to_bytes() - storage.convert_to_bytes()) < 1e-10
    
    def test_chain_decimal_conversions(self):
        """Test chaining decimal conversion methods."""
        storage = Storage(1, StorageUnit.GB)
        
        # Chain conversions
        result = storage.convert_to_mb().convert_to_kb().convert_to(StorageUnit.BYTES)
        
        # Should maintain equivalence
        assert abs(result.convert_to_bytes() - storage.convert_to_bytes()) < 1e-10
    
    def test_chain_bit_conversions(self):
        """Test chaining bit conversion methods."""
        storage = Storage(1, StorageUnit.GIGABITS)
        
        # Chain conversions
        result = storage.convert_to_megabits().convert_to_kilobits().convert_to_bits()
        
        # Should maintain equivalence
        assert abs(result.convert_to_bytes() - storage.convert_to_bytes()) < 1e-10
    
    def test_chain_mixed_conversions(self):
        """Test chaining mixed unit type conversions."""
        storage = Storage(1, StorageUnit.GIB)
        
        # Convert binary -> decimal -> bit -> back to binary
        result = (storage.convert_to_gb()
                        .convert_to_megabits()
                        .convert_to_bits()
                        .convert_to(StorageUnit.BYTES)
                        .convert_to_kib())
        
        # Should maintain equivalence within reasonable precision
        original_bytes = storage.convert_to_bytes()
        result_bytes = result.convert_to_bytes()
        assert abs(original_bytes - result_bytes) < 1e-6  # Allow for floating point errors


class TestConversionMethodsArithmetic:
    """Test arithmetic operations with convenient conversion methods."""
    
    def test_arithmetic_with_converted_values(self):
        """Test arithmetic operations with converted values."""
        storage1 = Storage(1, StorageUnit.GIB).convert_to_mib()
        storage2 = Storage(512, StorageUnit.MIB)
        
        # Addition
        total = storage1 + storage2
        expected_mib = 1024 + 512  # 1 GiB = 1024 MiB
        assert total.convert_to_mib().value == expected_mib
        
        # Subtraction
        diff = storage1 - storage2
        expected_diff_mib = 1024 - 512
        assert diff.convert_to_mib().value == expected_diff_mib
        
        # Multiplication
        doubled = storage2 * 2
        assert doubled.convert_to_mib().value == 1024
        
        # Division
        ratio = storage1 / storage2
        assert ratio == 2.0  # 1024 MiB / 512 MiB = 2
    
    def test_comparisons_with_converted_values(self):
        """Test comparison operations with converted values."""
        storage1 = Storage(1, StorageUnit.GIB).convert_to_mib()
        storage2 = Storage(1024, StorageUnit.MIB)
        storage3 = Storage(512, StorageUnit.MIB)
        
        # Equality
        assert storage1 == storage2
        assert storage1 != storage3
        
        # Ordering
        assert storage1 > storage3
        assert storage3 < storage1
        assert storage1 >= storage2
        assert storage2 <= storage1


class TestConversionMethodsEdgeCases:
    """Test edge cases for convenient conversion methods."""
    
    def test_zero_conversions(self):
        """Test conversions with zero values."""
        zero_bytes = Storage(0, StorageUnit.BYTES)
        
        # All conversions should work with zero
        assert zero_bytes.convert_to_kib().value == 0.0
        assert zero_bytes.convert_to_mb().value == 0.0
        assert zero_bytes.convert_to_bits().value == 0.0
        assert zero_bytes.convert_to_gigabits().value == 0.0
    
    def test_fractional_conversions(self):
        """Test conversions with fractional values."""
        storage = Storage(1.5, StorageUnit.KIB)
        
        # Should handle fractional values correctly
        bytes_result = storage.convert_to_bytes()
        assert bytes_result == 1536.0  # 1.5 * 1024
        
        mib_result = storage.convert_to_mib()
        assert abs(mib_result.value - (1.5 / 1024)) < 1e-10
    
    def test_very_large_conversions(self):
        """Test conversions with very large values."""
        large_storage = Storage(1e6, StorageUnit.TIB)
        
        # Should handle very large values
        yib_result = large_storage.convert_to_yib()
        assert yib_result.value > 0
        assert yib_result.unit == StorageUnit.YIB
        
        # Verify equivalence
        original_bytes = large_storage.convert_to_bytes()
        converted_bytes = yib_result.convert_to_bytes()
        assert abs(original_bytes - converted_bytes) < 1e-6
    
    def test_very_small_conversions(self):
        """Test conversions with very small values."""
        small_storage = Storage(1e-6, StorageUnit.BYTES)
        
        # Should handle very small values
        bits_result = small_storage.convert_to_bits()
        assert bits_result.value == 8e-6
        assert bits_result.unit == StorageUnit.BITS
        
        # Convert back and verify
        bytes_result = bits_result.convert_to(StorageUnit.BYTES)
        assert abs(bytes_result.value - small_storage.value) < 1e-15