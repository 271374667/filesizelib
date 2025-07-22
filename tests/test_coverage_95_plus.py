"""
Final push to achieve 95%+ test coverage.

Targeted tests for the last remaining uncovered lines.
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from filesizelib import Storage, StorageUnit
from filesizelib.platform_storage import WindowsStorage, LinuxStorage, MacStorage


class TestFinalCoverageTarget:
    """Tests to push coverage to 95%+."""
    
    def test_windows_exception_in_optimization_check(self):
        """Test Windows optimization with exception during path check."""
        storage = WindowsStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock os.listdir to raise an exception
            with patch('os.listdir', side_effect=OSError("Mocked error")):
                # Should handle exception gracefully and return False
                should_optimize = storage._should_use_windows_optimization(temp_path)
                assert should_optimize is False
    
    def test_windows_powershell_failure_fallback(self):
        """Test Windows PowerShell failure with proper fallback."""
        storage = WindowsStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Create a test file
            (temp_path / "test.txt").write_text("test content")
            
            # Mock PowerShell to fail
            with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'powershell')):
                result = storage._get_size_windows_optimized(temp_path)
                # Should fallback to standard method and get actual size
                assert result.value > 0
    
    def test_linux_mac_exception_handling_in_optimization(self):
        """Test Linux and Mac exception handling during optimization checks."""
        storages = [LinuxStorage(), MacStorage()]
        
        for storage in storages:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Mock os.listdir to raise an exception during large directory check
                with patch('os.listdir', side_effect=PermissionError("Access denied")):
                    # Should handle exception and return False
                    is_large = storage._is_large_directory(temp_path)
                    assert is_large is False
    
    def test_macos_subprocess_failure_resource_fork_fallback(self):
        """Test macOS subprocess failure with resource fork fallback."""
        storage = MacStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.txt").write_text("test content")
            
            # Mock subprocess to fail, then test resource fork method
            with patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'du')):
                # This should trigger the resource fork fallback path
                result = storage._get_size_macos_optimized(temp_path)
                assert result.value > 0
    
    def test_storage_format_edge_cases(self):
        """Test storage format method edge cases."""
        storage = Storage(1.23456, StorageUnit.MB)
        
        # Test with empty format spec
        result = storage.__format__("")
        assert isinstance(result, str)
        assert "MB" in result
        
        # Test with just precision
        result = storage.__format__(".2f")
        assert "1.23" in result
        assert "MB" in result
        
        # Test format spec parsing edge cases
        test_specs = ["", ".0f", ".5f", "g", "e"]
        for spec in test_specs:
            result = storage.__format__(spec)
            assert isinstance(result, str)
            assert "MB" in result
    
    def test_storage_get_set_decimal_precision_edge_cases(self):
        """Test decimal precision getter/setter edge cases."""
        original = Storage.get_decimal_precision()
        
        try:
            # Test setting various precision values
            test_values = [0, 1, 2, 5, 10, 15, 20, 100]
            
            for precision in test_values:
                Storage.set_decimal_precision(precision)
                retrieved = Storage.get_decimal_precision()
                assert retrieved == precision
                
                # Test that formatting uses this precision
                storage = Storage(1.123456789, StorageUnit.MB)
                result = str(storage)
                assert isinstance(result, str)
                
        finally:
            Storage.set_decimal_precision(original)
    
    def test_platform_optimization_file_vs_directory_paths(self):
        """Test platform optimization logic for files vs directories."""
        storages = [WindowsStorage(), LinuxStorage(), MacStorage()]
        
        for storage in storages:
            # Test with a file (should not optimize)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(b"content")
                file_path = Path(temp_file.name)
            
            try:
                result = storage.get_size_from_path(file_path)
                assert isinstance(result, Storage)
                assert result.value > 0
            finally:
                file_path.unlink()
            
            # Test with empty directory (should handle gracefully)
            with tempfile.TemporaryDirectory() as temp_dir:
                dir_path = Path(temp_dir)
                result = storage.get_size_from_path(dir_path)
                assert isinstance(result, Storage)
                assert result.value == 0  # Empty directory
    
    def test_storage_unit_classification_methods(self):
        """Test storage unit classification methods."""
        # Test that classification methods work
        binary_units = StorageUnit.get_binary_units()
        decimal_units = StorageUnit.get_decimal_units()
        bit_units = StorageUnit.get_bit_units()
        
        # Ensure they return sets
        assert isinstance(binary_units, set)
        assert isinstance(decimal_units, set)
        assert isinstance(bit_units, set)
        
        # Test individual unit classification
        assert StorageUnit.KIB.is_binary()
        assert not StorageUnit.KIB.is_decimal()
        assert not StorageUnit.KIB.is_bit_unit()
        
        assert StorageUnit.MB.is_decimal()
        assert not StorageUnit.MB.is_binary()
        assert not StorageUnit.MB.is_bit_unit()
        
        assert StorageUnit.BITS.is_bit_unit()
        assert not StorageUnit.BITS.is_binary()
        assert not StorageUnit.BITS.is_decimal()
    
    def test_error_conditions_not_covered(self):
        """Test error conditions that may not be covered."""
        # Test storage creation with edge case values
        storage = Storage(0.0, StorageUnit.BYTES)
        assert storage.value == 0.0
        
        # Test string representation of zero
        result = str(storage)
        assert "0" in result
        assert "BYTES" in result
        
        # Test arithmetic with zero
        non_zero = Storage(1, StorageUnit.KB)
        result = storage + non_zero
        assert result == non_zero
        
        result = non_zero - non_zero
        assert result.value == 0.0
    
    def test_comprehensive_method_coverage(self):
        """Comprehensive method coverage test."""
        storage = Storage(1536, StorageUnit.BYTES)
        
        # Test auto_scale with different preferences
        binary_scaled = storage.auto_scale(prefer_binary=True)
        decimal_scaled = storage.auto_scale(prefer_binary=False)
        
        assert binary_scaled.unit == StorageUnit.KIB
        assert binary_scaled.value == 1.5
        
        assert decimal_scaled.unit == StorageUnit.KB
        assert decimal_scaled.value == 1.536
        
        # Test all conversion methods work
        as_mib = storage.convert_to(StorageUnit.MIB)
        assert as_mib.value == 1536 / (1024 * 1024)
        
        # Test hash works
        hash_val = hash(storage)
        assert isinstance(hash_val, int)
        
        # Test repr
        repr_str = repr(storage)
        assert "Storage" in repr_str
        assert "1536" in repr_str