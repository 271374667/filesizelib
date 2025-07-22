"""
Comprehensive tests for the StorageUnit enum.

This module tests all functionality of the StorageUnit enum including
unit values, aliases, classifications, and utility methods.
"""

import pytest
from typing import Set

from bytesize.storage_unit import StorageUnit


class TestStorageUnitValues:
    """Test StorageUnit enum values and basic properties."""
    
    def test_bytes_units(self):
        """Test byte unit values."""
        assert StorageUnit.BYTES.value == 1
        assert StorageUnit.BYTE.value == 1
    
    @pytest.mark.parametrize("unit,expected_value", [
        (StorageUnit.KIB, 1024),
        (StorageUnit.MIB, 1024 ** 2),
        (StorageUnit.GIB, 1024 ** 3),
        (StorageUnit.TIB, 1024 ** 4),
        (StorageUnit.PIB, 1024 ** 5),
        (StorageUnit.EIB, 1024 ** 6),
        (StorageUnit.ZIB, 1024 ** 7),
        (StorageUnit.YIB, 1024 ** 8),
    ])
    def test_binary_unit_values(self, unit: StorageUnit, expected_value: int):
        """Test binary unit values (powers of 1024)."""
        assert unit.value == expected_value
    
    @pytest.mark.parametrize("unit,expected_value", [
        (StorageUnit.KB, 1000),
        (StorageUnit.MB, 1000 ** 2),
        (StorageUnit.GB, 1000 ** 3),
        (StorageUnit.TB, 1000 ** 4),
        (StorageUnit.PB, 1000 ** 5),
        (StorageUnit.EB, 1000 ** 6),
        (StorageUnit.ZB, 1000 ** 7),
        (StorageUnit.YB, 1000 ** 8),
    ])
    def test_decimal_unit_values(self, unit: StorageUnit, expected_value: int):
        """Test decimal unit values (powers of 1000)."""
        assert unit.value == expected_value
    
    @pytest.mark.parametrize("unit,expected_value", [
        (StorageUnit.BITS, 1/8),
        (StorageUnit.BIT, 1/8),
        (StorageUnit.KILOBITS, 1000/8),
        (StorageUnit.MEGABITS, (1000 ** 2)/8),
        (StorageUnit.GIGABITS, (1000 ** 3)/8),
        (StorageUnit.TERABITS, (1000 ** 4)/8),
        (StorageUnit.PETABITS, (1000 ** 5)/8),
        (StorageUnit.EXABITS, (1000 ** 6)/8),
        (StorageUnit.ZETTABITS, (1000 ** 7)/8),
        (StorageUnit.YOTTABITS, (1000 ** 8)/8),
    ])
    def test_bit_unit_values(self, unit: StorageUnit, expected_value: float):
        """Test bit unit values."""
        assert unit.value == expected_value


class TestStorageUnitAliases:
    """Test StorageUnit alias functionality."""
    
    def test_get_unit_aliases_returns_dict(self):
        """Test that get_unit_aliases returns a dictionary."""
        aliases = StorageUnit.get_unit_aliases()
        assert isinstance(aliases, dict)
        assert len(aliases) > 0
    
    def test_basic_aliases(self):
        """Test basic unit aliases."""
        aliases = StorageUnit.get_unit_aliases()
        
        # Test byte aliases
        assert aliases['b'] == StorageUnit.BYTES
        assert aliases['byte'] == StorageUnit.BYTES
        assert aliases['bytes'] == StorageUnit.BYTES
        
        # Test binary aliases
        assert aliases['kib'] == StorageUnit.KIB
        assert aliases['mib'] == StorageUnit.MIB
        assert aliases['gib'] == StorageUnit.GIB
        
        # Test decimal aliases
        assert aliases['kb'] == StorageUnit.KB
        assert aliases['mb'] == StorageUnit.MB
        assert aliases['gb'] == StorageUnit.GB
        
        # Test bit aliases
        assert aliases['bit'] == StorageUnit.BITS
        assert aliases['bits'] == StorageUnit.BITS
        assert aliases['kilobit'] == StorageUnit.KILOBITS
    
    @pytest.mark.parametrize("alias,expected_unit", [
        ('k', StorageUnit.KB),
        ('m', StorageUnit.MB),
        ('g', StorageUnit.GB),
        ('ki', StorageUnit.KIB),
        ('mi', StorageUnit.MIB),
        ('gi', StorageUnit.GIB),
        ('kibibyte', StorageUnit.KIB),
        ('mebibyte', StorageUnit.MIB),
        ('gibibyte', StorageUnit.GIB),
        ('kilobyte', StorageUnit.KB),
        ('megabyte', StorageUnit.MB),
        ('gigabyte', StorageUnit.GB),
    ])
    def test_specific_aliases(self, alias: str, expected_unit: StorageUnit):
        """Test specific aliases map to correct units."""
        aliases = StorageUnit.get_unit_aliases()
        assert aliases[alias] == expected_unit
    
    def test_case_insensitive_aliases(self):
        """Test that all aliases are lowercase."""
        aliases = StorageUnit.get_unit_aliases()
        for alias in aliases.keys():
            assert alias == alias.lower(), f"Alias '{alias}' should be lowercase"
    
    def test_comprehensive_bit_aliases(self):
        """Test comprehensive bit unit aliases."""
        aliases = StorageUnit.get_unit_aliases()
        
        bit_aliases = [
            ('kbit', StorageUnit.KILOBITS),
            ('mbit', StorageUnit.MEGABITS),
            ('gbit', StorageUnit.GIGABITS),
            ('tbit', StorageUnit.TERABITS),
            ('pbit', StorageUnit.PETABITS),
            ('ebit', StorageUnit.EXABITS),
            ('zbit', StorageUnit.ZETTABITS),
            ('ybit', StorageUnit.YOTTABITS),
        ]
        
        for alias, expected_unit in bit_aliases:
            assert aliases[alias] == expected_unit


class TestStorageUnitClassifications:
    """Test StorageUnit classification methods."""
    
    def test_get_binary_units(self, binary_units: list):
        """Test get_binary_units method."""
        binary_set = StorageUnit.get_binary_units()
        
        assert isinstance(binary_set, set)
        assert len(binary_set) == len(binary_units)
        
        for unit in binary_units:
            assert unit in binary_set
    
    def test_get_decimal_units(self, decimal_units: list):
        """Test get_decimal_units method."""
        decimal_set = StorageUnit.get_decimal_units()
        
        assert isinstance(decimal_set, set)
        assert len(decimal_set) == len(decimal_units)
        
        for unit in decimal_units:
            assert unit in decimal_set
    
    def test_get_bit_units(self, bit_units: list):
        """Test get_bit_units method."""
        bit_set = StorageUnit.get_bit_units()
        
        assert isinstance(bit_set, set)
        assert len(bit_set) == len(bit_units)
        
        for unit in bit_units:
            assert unit in bit_set
    
    def test_unit_sets_are_disjoint(self, binary_units: list, decimal_units: list, bit_units: list):
        """Test that unit classification sets are disjoint."""
        binary_set = set(binary_units)
        decimal_set = set(decimal_units)
        bit_set = set(bit_units)
        
        # Binary and decimal should be disjoint
        assert binary_set.isdisjoint(decimal_set)
        
        # Binary and bit should be disjoint  
        assert binary_set.isdisjoint(bit_set)
        
        # Decimal and bit should be disjoint
        assert decimal_set.isdisjoint(bit_set)
    
    def test_bytes_in_binary_classification(self):
        """Test that BYTES is classified as binary."""
        binary_units = StorageUnit.get_binary_units()
        assert StorageUnit.BYTES in binary_units
        assert StorageUnit.BYTE in binary_units


class TestStorageUnitInstanceMethods:
    """Test StorageUnit instance classification methods."""
    
    @pytest.mark.parametrize("unit", [
        StorageUnit.BYTES,
        StorageUnit.KIB,
        StorageUnit.MIB,
        StorageUnit.GIB,
        StorageUnit.TIB,
        StorageUnit.PIB,
        StorageUnit.EIB,
        StorageUnit.ZIB,
        StorageUnit.YIB,
    ])
    def test_is_binary_true(self, unit: StorageUnit):
        """Test is_binary() returns True for binary units."""
        assert unit.is_binary() is True
        assert unit.is_decimal() is False
        assert unit.is_bit_unit() is False
    
    @pytest.mark.parametrize("unit", [
        StorageUnit.KB,
        StorageUnit.MB,
        StorageUnit.GB,
        StorageUnit.TB,
        StorageUnit.PB,
        StorageUnit.EB,
        StorageUnit.ZB,
        StorageUnit.YB,
    ])
    def test_is_decimal_true(self, unit: StorageUnit):
        """Test is_decimal() returns True for decimal units."""
        assert unit.is_decimal() is True
        assert unit.is_binary() is False
        assert unit.is_bit_unit() is False
    
    @pytest.mark.parametrize("unit", [
        StorageUnit.BITS,
        StorageUnit.BIT,
        StorageUnit.KILOBITS,
        StorageUnit.MEGABITS,
        StorageUnit.GIGABITS,
        StorageUnit.TERABITS,
        StorageUnit.PETABITS,
        StorageUnit.EXABITS,
        StorageUnit.ZETTABITS,
        StorageUnit.YOTTABITS,
    ])
    def test_is_bit_unit_true(self, unit: StorageUnit):
        """Test is_bit_unit() returns True for bit units."""
        assert unit.is_bit_unit() is True
        assert unit.is_binary() is False
        assert unit.is_decimal() is False


class TestStorageUnitEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_enum_completeness(self):
        """Test that all enum members are accounted for in classifications."""
        all_units = set(StorageUnit)
        binary_units = StorageUnit.get_binary_units()
        decimal_units = StorageUnit.get_decimal_units()
        bit_units = StorageUnit.get_bit_units()
        
        classified_units = binary_units | decimal_units | bit_units
        
        # All units should be classified
        assert classified_units == all_units
    
    def test_alias_completeness(self):
        """Test that aliases exist for all major units."""
        aliases = StorageUnit.get_unit_aliases()
        
        # Check that we have aliases for all major units
        required_aliases = [
            'b', 'bytes', 'byte',
            'kb', 'mb', 'gb', 'tb',
            'kib', 'mib', 'gib', 'tib',
            'bit', 'bits',
            'kilobit', 'megabit', 'gigabit',
        ]
        
        for alias in required_aliases:
            assert alias in aliases, f"Missing alias for '{alias}'"
    
    def test_byte_aliases_consistency(self):
        """Test that BYTE and BYTES aliases are consistent."""
        aliases = StorageUnit.get_unit_aliases()
        
        # Both should map to BYTES
        assert aliases['byte'] == StorageUnit.BYTES
        assert aliases['bytes'] == StorageUnit.BYTES
        assert aliases['b'] == StorageUnit.BYTES
    
    def test_bit_aliases_consistency(self):
        """Test that BIT and BITS aliases are consistent."""
        aliases = StorageUnit.get_unit_aliases()
        
        # Both should map to BITS
        assert aliases['bit'] == StorageUnit.BITS
        assert aliases['bits'] == StorageUnit.BITS
    
    def test_unit_value_precision(self):
        """Test that unit values maintain precision."""
        # Test bit unit precision
        assert StorageUnit.BITS.value == 0.125
        assert StorageUnit.BIT.value == 0.125
        
        # Test that large values maintain precision
        assert StorageUnit.YIB.value == 1024 ** 8
        assert StorageUnit.YB.value == 1000 ** 8
    
    def test_sorting_by_value(self):
        """Test that units can be sorted by their values."""
        units = [StorageUnit.GB, StorageUnit.MB, StorageUnit.TB, StorageUnit.KB]
        sorted_units = sorted(units, key=lambda x: x.value)
        
        expected_order = [StorageUnit.KB, StorageUnit.MB, StorageUnit.GB, StorageUnit.TB]
        assert sorted_units == expected_order
    
    def test_enum_name_consistency(self):
        """Test that enum names are consistent with expectations."""
        # Test that names match expected patterns
        assert StorageUnit.BYTES.name == "BYTES"
        assert StorageUnit.KIB.name == "KIB"
        assert StorageUnit.MB.name == "MB"
        assert StorageUnit.BITS.name == "BITS"
    
    def test_no_duplicate_values(self):
        """Test that there are no duplicate values except for intentional aliases."""
        values = {}
        
        for unit in StorageUnit:
            value = unit.value
            if value in values:
                # Only BYTE/BYTES and BIT/BITS should have duplicate values
                existing_unit = values[value]
                valid_duplicates = [
                    (StorageUnit.BYTE, StorageUnit.BYTES),
                    (StorageUnit.BYTES, StorageUnit.BYTE),
                    (StorageUnit.BIT, StorageUnit.BITS),
                    (StorageUnit.BITS, StorageUnit.BIT),
                ]
                assert (existing_unit, unit) in valid_duplicates or (unit, existing_unit) in valid_duplicates
            else:
                values[value] = unit


class TestStorageUnitDataDriven:
    """Data-driven tests for StorageUnit functionality."""
    
    @pytest.mark.parametrize("unit_name,unit_value", [
        ("BYTES", 1),
        ("KIB", 1024),
        ("MIB", 1048576),
        ("KB", 1000),
        ("MB", 1000000),
        ("BITS", 0.125),
        ("KILOBITS", 125.0),
    ])
    def test_unit_access_by_name(self, unit_name: str, unit_value: float):
        """Test accessing units by name and verifying values."""
        unit = getattr(StorageUnit, unit_name)
        assert unit.value == unit_value
    
    @pytest.mark.parametrize("binary_power,expected_unit", [
        (0, StorageUnit.BYTES),
        (1, StorageUnit.KIB),
        (2, StorageUnit.MIB),
        (3, StorageUnit.GIB),
        (4, StorageUnit.TIB),
        (5, StorageUnit.PIB),
        (6, StorageUnit.EIB),
        (7, StorageUnit.ZIB),
        (8, StorageUnit.YIB),
    ])
    def test_binary_progression(self, binary_power: int, expected_unit: StorageUnit):
        """Test that binary units follow expected progression."""
        expected_value = 1024 ** binary_power if binary_power > 0 else 1
        assert expected_unit.value == expected_value
    
    @pytest.mark.parametrize("decimal_power,expected_unit", [
        (1, StorageUnit.KB),
        (2, StorageUnit.MB),
        (3, StorageUnit.GB),
        (4, StorageUnit.TB),
        (5, StorageUnit.PB),
        (6, StorageUnit.EB),
        (7, StorageUnit.ZB),
        (8, StorageUnit.YB),
    ])
    def test_decimal_progression(self, decimal_power: int, expected_unit: StorageUnit):
        """Test that decimal units follow expected progression."""
        expected_value = 1000 ** decimal_power
        assert expected_unit.value == expected_value