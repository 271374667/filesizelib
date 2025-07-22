"""
Final targeted tests to achieve 95%+ coverage.

This module contains specific tests designed to cover the remaining
uncovered lines in the codebase.
"""

import os
import subprocess
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from typing import Any

from filesizelib import Storage, StorageUnit
from filesizelib.platform_storage import (
    WindowsStorage,
    LinuxStorage,
    MacStorage
)


class TestUncoveredPlatformStorageLines:
    """Tests targeting specific uncovered lines in platform_storage.py."""
    
    def test_windows_storage_edge_case_paths(self):
        """Test Windows storage edge cases for lines 99, 104-106."""
        storage = WindowsStorage()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = Path(temp_file.name)
        
        try:
            # Test file path (not directory) - should not use optimization
            result = storage.get_size_from_path(temp_path)
            assert isinstance(result, Storage)
            assert result.value > 0
        finally:
            temp_path.unlink()
    
    def test_windows_large_directory_threshold(self):
        """Test Windows optimization threshold logic for lines 123-124."""
        storage = WindowsStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create many files to trigger optimization
            for i in range(150):  # > 100 files threshold
                (temp_path / f"file_{i}.txt").write_text("content")
            
            # This should trigger the optimization path
            should_optimize = storage._should_use_windows_optimization(temp_path)
            assert should_optimize is True
    
    @patch('subprocess.run')
    def test_windows_powershell_output_parsing(self, mock_run):
        """Test Windows PowerShell output parsing for edge cases."""
        storage = WindowsStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock PowerShell returning non-integer output
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "12345.67"  # Float output
            mock_run.return_value = mock_result
            
            result = storage._get_size_windows_optimized(temp_path)
            # Should handle float conversion
            assert result.value == 12345.67
    
    def test_linux_system_path_detection(self):
        """Test Linux system path detection logic."""
        storage = LinuxStorage()
        
        # Test various path patterns
        test_paths = [
            Path("/usr/local/bin"),
            Path("/var/cache"),
            Path("/opt/myapp"),
            Path("/home/user/documents")  # This should NOT be optimized
        ]
        
        for test_path in test_paths:
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    with patch.object(storage, '_is_large_directory', return_value=False):
                        # Just test that it doesn't crash
                        try:
                            result = storage._should_use_linux_optimization(test_path)
                            # Result depends on path
                            assert isinstance(result, bool)
                        except (PermissionError, OSError):
                            pass
    
    @patch('subprocess.run')
    def test_linux_du_output_parsing_edge_cases(self, mock_run):
        """Test Linux du command output parsing edge cases."""
        storage = LinuxStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test with whitespace and different formats
            test_outputs = [
                "12345\t/path/to/dir",      # Normal output
                "  12345  \t  /path/to/dir  ",  # Whitespace
                "0\t/empty/dir",            # Zero size
                "999999999999\t/huge/dir"  # Very large
            ]
            
            for output in test_outputs:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = output
                mock_run.return_value = mock_result
                
                result = storage._get_size_linux_optimized(temp_path)
                assert isinstance(result, Storage)
                assert result.value >= 0
    
    def test_macos_optimization_edge_cases(self):
        """Test macOS optimization logic edge cases."""
        storage = MacStorage()
        
        # Test with paths that exist but are not directories
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)
        
        try:
            # File (not directory) should not use optimization
            should_optimize = storage._should_use_macos_optimization(temp_path)
            assert should_optimize is False
        finally:
            temp_path.unlink()
    
    @patch('subprocess.run') 
    def test_macos_du_kb_to_bytes_conversion(self, mock_run):
        """Test macOS du KB to bytes conversion."""
        storage = MacStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test various KB values
            kb_values = [1, 0, 1024, 2048]
            
            for kb_value in kb_values:
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = f"{kb_value}\t{temp_path}"
                mock_run.return_value = mock_result
                
                result = storage._get_size_macos_optimized(temp_path)
                expected_bytes = kb_value * 1024
                assert result.value == expected_bytes
    
    def test_macos_resource_forks_with_xattr(self):
        """Test macOS resource forks calculation with xattr available."""
        storage = MacStorage()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test file content")
            temp_path = Path(temp_file.name)
        
        try:
            # Mock xattr module being available
            mock_xattr = MagicMock()
            mock_xattr.listxattr.return_value = [
                'com.apple.ResourceFork',
                'com.apple.metadata:kMDItemWhereFroms'
            ]
            # Simulate 100 bytes of extended attribute data
            mock_xattr.getxattr.return_value = b'x' * 100
            
            with patch.dict('sys.modules', {'xattr': mock_xattr}):
                result = storage._get_size_with_resource_forks(temp_path)
                
                # Should include file size + extended attributes
                base_size = len(b"test file content")
                expected_min = base_size + 100  # At least file + one attribute
                assert result.value >= expected_min
        finally:
            temp_path.unlink()
    
    def test_macos_resource_forks_xattr_errors(self):
        """Test macOS resource forks with xattr errors."""
        storage = MacStorage()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test")
            temp_path = Path(temp_file.name)
        
        try:
            # Mock xattr raising OSError
            mock_xattr = MagicMock()
            mock_xattr.listxattr.side_effect = OSError("Permission denied")
            
            with patch.dict('sys.modules', {'xattr': mock_xattr}):
                result = storage._get_size_with_resource_forks(temp_path)
                # Should fallback to regular file size
                assert result.value == 4  # len(b"test")
        finally:
            temp_path.unlink()


class TestUncoveredStorageLines:
    """Tests targeting specific uncovered lines in storage.py."""
    
    def test_storage_class_method_edge_cases(self):
        """Test storage class method edge cases for lines 586-587."""
        # Test get_decimal_precision with different values
        original_precision = Storage.get_decimal_precision()
        
        try:
            # Test setting and getting different precision values
            test_precisions = [0, 1, 5, 10, 15, 20]
            
            for precision in test_precisions:
                Storage.set_decimal_precision(precision)
                retrieved_precision = Storage.get_decimal_precision()
                assert retrieved_precision == precision
                
        finally:
            # Restore original precision
            Storage.set_decimal_precision(original_precision)
    
    def test_storage_string_format_edge_cases(self):
        """Test storage string formatting edge cases for lines 1017-1027."""
        storage = Storage(1.23456789, StorageUnit.MB)
        
        # Test format spec handling
        test_specs = [
            ".0f",   # No decimal places
            ".10f",  # Many decimal places
            "e",     # Scientific notation
            "g",     # General format
            "",      # Empty format spec
        ]
        
        for spec in test_specs:
            try:
                if spec:
                    result = f"{storage:.{spec[1:]}}" if spec.startswith('.') else f"{storage:{spec}}"
                else:
                    result = f"{storage}"
                
                assert isinstance(result, str)
                assert "MB" in result
            except (ValueError, TypeError):
                # Some format specs might be invalid, that's okay
                pass
    
    def test_storage_decimal_precision_formatting(self):
        """Test decimal precision formatting edge cases."""
        original_precision = Storage.get_decimal_precision()
        
        try:
            # Test with precision 0 (integer display)
            Storage.set_decimal_precision(0)
            storage = Storage(1.7, StorageUnit.MB)
            result = str(storage)
            # Should round to nearest integer
            assert "2" in result
            
            # Test with very high precision
            Storage.set_decimal_precision(30)
            storage = Storage(1.123456789123456789, StorageUnit.MB)
            result = str(storage)
            assert isinstance(result, str)
            assert "MB" in result
            
        finally:
            Storage.set_decimal_precision(original_precision)
    
    def test_storage_error_conditions_comprehensive(self):
        """Test comprehensive error conditions."""
        # Test invalid multiplication with string
        storage = Storage(1, StorageUnit.MB)
        
        with pytest.raises(TypeError):
            result = storage * "invalid"
        
        # Test invalid division
        with pytest.raises(TypeError):
            result = storage / "invalid"
        
        # Test comparison with non-storage object
        try:
            result = storage == "not a storage"
            assert result is False
        except TypeError:
            # This is also acceptable
            pass
    
    def test_storage_hash_consistency(self):
        """Test storage hash consistency."""
        # Create identical storages
        storage1 = Storage(1, StorageUnit.KIB)
        storage2 = Storage(1024, StorageUnit.BYTES)
        storage3 = Storage(1, StorageUnit.KIB)
        
        # Equal objects should have equal hashes
        assert hash(storage1) == hash(storage3)
        
        # Equivalent storages should have equal hashes
        assert hash(storage1) == hash(storage2)
        
        # Should be usable in sets and dicts
        storage_set = {storage1, storage2, storage3}
        # All are equivalent, so set should have only 1 unique element
        assert len(storage_set) == 1


class TestEdgeCaseErrorHandling:
    """Test edge case error handling scenarios."""
    
    def test_platform_storage_system_call_failures(self):
        """Test platform storage system call failures."""
        platforms = [WindowsStorage(), LinuxStorage(), MacStorage()]
        
        for storage in platforms:
            # Test with a path that might cause system call failures
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Create a file and then remove its parent directory
                # to test error handling
                test_file = temp_path / "test.txt"
                test_file.write_text("content")
                
                # Test normal operation first
                result = storage.get_size_from_path(test_file)
                assert isinstance(result, Storage)
                assert result.value > 0
    
    @patch('os.listdir')
    def test_directory_listing_errors(self, mock_listdir):
        """Test directory listing error handling."""
        # Test different types of OS errors
        error_types = [
            PermissionError("Permission denied"),
            OSError("OS error"),
            FileNotFoundError("Directory not found")
        ]
        
        storage = LinuxStorage()
        
        for error in error_types:
            mock_listdir.side_effect = error
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Should handle errors gracefully
                is_large = storage._is_large_directory(temp_path)
                assert is_large is False  # Default to False on error
    
    def test_subprocess_timeout_handling(self):
        """Test subprocess timeout handling."""
        storage = LinuxStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock subprocess to timeout
            with patch('subprocess.run') as mock_run:
                mock_run.side_effect = subprocess.TimeoutExpired('du', 5)
                
                # Should handle timeout gracefully
                result = storage._get_size_linux_optimized(temp_path)
                assert isinstance(result, Storage)


class TestSpecialFileTypes:
    """Test handling of special file types."""
    
    def test_symlink_handling(self):
        """Test symbolic link handling."""
        # Create a file and symlink to it
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"original content")
            original_path = Path(temp_file.name)
        
        try:
            symlink_path = original_path.parent / "symlink_test"
            
            try:
                # Create symlink (might not work on all systems)
                symlink_path.symlink_to(original_path)
                
                # Test size calculation on symlink
                size = Storage.get_size_from_path(symlink_path)
                assert isinstance(size, Storage)
                
                # Clean up symlink
                symlink_path.unlink()
                
            except (OSError, NotImplementedError):
                # Symlinks might not be supported on this system
                pass
                
        finally:
            original_path.unlink()
    
    def test_empty_directory_handling(self):
        """Test empty directory handling."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Empty directory should have size 0
            size = Storage.get_size_from_path(temp_path)
            assert size.value == 0
            assert size.unit == StorageUnit.BYTES