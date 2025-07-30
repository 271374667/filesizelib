"""
Tests for new features added to filesizelib.

This module tests:
1. FileSize alias
2. int() and float() magic methods
3. Property-based conversion (e.g., storage.MB)
4. String initialization with automatic parsing
"""

import pytest
from filesizelib import Storage, StorageUnit, FileSizeLib, FileSize


class TestFileSizeAlias:
    """Test the new FileSize alias."""
    
    def test_filesize_alias_basic(self):
        """Test FileSize is an alias for Storage."""
        storage1 = Storage(1024, StorageUnit.BYTES)
        storage2 = FileSize(1024, StorageUnit.BYTES)
        
        assert type(storage1) == type(storage2)
        assert storage1 == storage2
        assert str(storage1) == str(storage2)
    
    def test_filesize_alias_functionality(self):
        """Test FileSize has all Storage functionality."""
        filesize = FileSize("1.5 MB")
        
        assert filesize.value == 1.5
        assert filesize.unit == StorageUnit.MB
        assert filesize.convert_to_bytes() == 1500000.0
        
        # Test arithmetic
        filesize2 = FileSize("0.5 MB")
        total = filesize + filesize2
        assert total == FileSize(2.0, StorageUnit.MB)
    
    def test_all_aliases_equivalent(self):
        """Test all aliases (Storage, FileSizeLib, FileSize) are equivalent."""
        value = 2048
        unit = StorageUnit.BYTES
        
        storage = Storage(value, unit)
        filesizelib = FileSizeLib(value, unit)
        filesize = FileSize(value, unit)
        
        assert storage == filesizelib == filesize
        assert str(storage) == str(filesizelib) == str(filesize)


class TestMagicMethods:
    """Test int() and float() magic methods."""
    
    def test_int_conversion(self):
        """Test int() conversion returns bytes as integer."""
        storage = Storage(1.5, StorageUnit.KIB)
        assert int(storage) == 1536
        
        storage2 = Storage(1024.9, StorageUnit.BYTES)
        assert int(storage2) == 1024
        
        storage3 = Storage(2.5, StorageUnit.MB)
        assert int(storage3) == 2500000
    
    def test_float_conversion(self):
        """Test float() conversion returns bytes as float."""
        storage = Storage(1.5, StorageUnit.KIB)
        assert float(storage) == 1536.0
        
        storage2 = Storage(1024, StorageUnit.BYTES)
        assert float(storage2) == 1024.0
        
        storage3 = Storage(2.5, StorageUnit.MB)
        assert float(storage3) == 2500000.0
    
    def test_conversion_edge_cases(self):
        """Test conversion edge cases."""
        # Zero
        storage = Storage(0, StorageUnit.GB)
        assert int(storage) == 0
        assert float(storage) == 0.0
        
        # Very small values
        storage = Storage(1, StorageUnit.BITS)
        assert float(storage) == 0.125  # 1/8 byte
        assert int(storage) == 0  # Truncated
        
        # Very large values
        storage = Storage(1, StorageUnit.TB)
        expected = 1000000000000.0
        assert float(storage) == expected
        assert int(storage) == int(expected)


class TestPropertyConversions:
    """Test property-based conversions (e.g., storage.MB)."""
    
    def test_binary_properties(self):
        """Test binary unit properties."""
        storage = Storage(2048, StorageUnit.BYTES)
        
        assert storage.KIB.value == 2.0
        assert storage.KIB.unit == StorageUnit.KIB
        
        assert storage.MIB.value == 2.0 / 1024
        assert storage.MIB.unit == StorageUnit.MIB
    
    def test_decimal_properties(self):
        """Test decimal unit properties."""
        storage = Storage(3000, StorageUnit.BYTES)
        
        assert storage.KB.value == 3.0
        assert storage.KB.unit == StorageUnit.KB
        
        assert storage.MB.value == 0.003
        assert storage.MB.unit == StorageUnit.MB
        
        assert storage.GB.value == 0.000003
        assert storage.GB.unit == StorageUnit.GB
    
    def test_bit_properties(self):
        """Test bit unit properties."""
        storage = Storage(1, StorageUnit.BYTES)
        
        assert storage.BITS.value == 8.0
        assert storage.BITS.unit == StorageUnit.BITS
        
        storage2 = Storage(1000, StorageUnit.BYTES)
        assert storage2.KILOBITS.value == 8.0
        assert storage2.KILOBITS.unit == StorageUnit.KILOBITS
    
    def test_all_properties_available(self):
        """Test all conversion properties are available."""
        storage = Storage(1024, StorageUnit.BYTES)
        
        # Test all properties exist and return Storage objects
        properties = [
            'BYTES', 'KIB', 'MIB', 'GIB', 'TIB', 'PIB', 'EIB', 'ZIB', 'YIB',
            'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB',
            'BITS', 'KILOBITS', 'MEGABITS', 'GIGABITS', 'TERABITS'
        ]
        
        for prop in properties:
            assert hasattr(storage, prop)
            result = getattr(storage, prop)
            assert isinstance(result, Storage)
    
    def test_property_chaining(self):
        """Test properties can be chained."""
        storage = Storage(1, StorageUnit.GIB)
        
        # Convert GiB -> MiB -> KiB
        result = storage.MIB.KIB
        expected = Storage(1024 * 1024, StorageUnit.KIB)  # 1 GiB = 1024 MiB = 1024*1024 KiB
        assert result == expected


class TestStringInitialization:
    """Test string initialization with automatic parsing."""
    
    def test_string_init_basic(self):
        """Test basic string initialization."""
        storage = Storage("1.5 MB")
        assert storage.value == 1.5
        assert storage.unit == StorageUnit.MB
        
        storage2 = Storage("2048 bytes")
        assert storage2.value == 2048.0
        assert storage2.unit == StorageUnit.BYTES
    
    def test_string_init_no_unit(self):
        """Test string initialization without unit defaults to bytes."""
        storage = Storage("1024")
        assert storage.value == 1024.0
        assert storage.unit == StorageUnit.BYTES
    
    def test_string_init_various_formats(self):
        """Test various string formats."""
        # Case insensitive
        storage1 = Storage("1 mb")
        storage2 = Storage("1 MB")
        storage3 = Storage("1 Mb")
        assert storage1 == storage2 == storage3
        
        # With and without spaces
        storage4 = Storage("1MB")
        storage5 = Storage("1 MB")
        assert storage4 == storage5
        
        # Decimal comma
        storage6 = Storage("1,5 MB")
        assert storage6.value == 1.5
    
    def test_string_init_with_explicit_unit(self):
        """Test string initialization with explicit unit override."""
        # When string has unit but explicit unit is provided
        # The parsing should still work (explicit unit is ignored for strings)
        storage = Storage("1.5 MB", StorageUnit.GB)
        assert storage.value == 1.5
        assert storage.unit == StorageUnit.MB  # From string, not explicit unit
    
    def test_auto_unit_with_numeric(self):
        """Test AUTO unit with numeric values defaults to bytes."""
        storage = Storage(1024, StorageUnit.AUTO)
        assert storage.value == 1024.0
        assert storage.unit == StorageUnit.BYTES
        
        storage2 = Storage(1024)  # Default to AUTO
        assert storage2.value == 1024.0
        assert storage2.unit == StorageUnit.BYTES
    
    def test_mixed_initialization_types(self):
        """Test different initialization types produce equivalent results."""
        # These should be equivalent
        storage1 = Storage(1.5, StorageUnit.MB)
        storage2 = Storage("1.5 MB")
        storage3 = FileSize("1.5 MB")
        
        assert storage1 == storage2 == storage3
        assert str(storage1) == str(storage2) == str(storage3)
    
    def test_string_init_error_cases(self):
        """Test string initialization error cases."""
        with pytest.raises(ValueError):
            Storage("invalid")
        
        with pytest.raises(ValueError):
            Storage("")
        
        with pytest.raises(ValueError):
            Storage("1.5 invalid_unit")


class TestBackwardCompatibility:
    """Test that new features don't break existing functionality."""
    
    def test_existing_numeric_init(self):
        """Test existing numeric initialization still works."""
        storage = Storage(1024, StorageUnit.BYTES)
        assert storage.value == 1024.0
        assert storage.unit == StorageUnit.BYTES
    
    def test_existing_parse_method(self):
        """Test existing parse class method still works."""
        storage = Storage.parse("1.5 MB")
        assert storage.value == 1.5
        assert storage.unit == StorageUnit.MB
    
    def test_existing_conversion_methods(self):
        """Test existing conversion methods still work."""
        storage = Storage(1024, StorageUnit.BYTES)
        
        kib = storage.convert_to_kib()
        assert kib.value == 1.0
        assert kib.unit == StorageUnit.KIB
        
        mb = storage.convert_to_mb()
        assert mb.value == 0.001024
        assert mb.unit == StorageUnit.MB
    
    def test_existing_arithmetic(self):
        """Test existing arithmetic operations still work."""
        s1 = Storage(1, StorageUnit.KIB)
        s2 = Storage(512, StorageUnit.BYTES)
        
        total = s1 + s2
        assert total.convert_to_bytes() == 1536.0
        
        diff = s1 - s2
        assert diff.convert_to_bytes() == 512.0
        
        doubled = s1 * 2
        assert doubled.value == 2.0
        assert doubled.unit == StorageUnit.KIB


class TestIntegration:
    """Integration tests combining multiple new features."""
    
    def test_all_features_together(self):
        """Test using all new features together."""
        # Create using string initialization
        storage = FileSize("2.5 GiB")
        
        # Use property conversion
        in_mb = storage.MB
        
        # Use magic methods
        bytes_as_int = int(storage)
        bytes_as_float = float(storage)
        
        # Verify results
        expected_bytes = 2.5 * (1024 ** 3)  # 2.5 GiB in bytes
        assert bytes_as_float == expected_bytes
        assert bytes_as_int == int(expected_bytes)
        
        # MB conversion should be approximately correct
        expected_mb = expected_bytes / (1000 ** 2)
        assert abs(in_mb.value - expected_mb) < 0.001
    
    def test_property_with_magic_methods(self):
        """Test properties work with magic methods."""
        storage = Storage("1 KiB")
        
        # Convert to MB using property, then to int
        # int() returns the byte representation of the Storage object
        mb_as_int = int(storage.MB)
        expected = 1024  # 1 KiB = 1024 bytes, regardless of the MB representation
        assert mb_as_int == expected
        
        # Convert to KB using property, then to float
        # float() returns the byte representation of the Storage object
        kb_as_float = float(storage.KB)
        expected_float = 1024.0  # 1 KiB = 1024 bytes, regardless of KB representation
        assert kb_as_float == expected_float