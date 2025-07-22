"""
Comprehensive tests for platform-specific storage to achieve 95%+ coverage.

This module provides additional tests to cover all code paths in platform_storage.py
that were not covered by the existing tests.
"""

import os
import platform
import subprocess
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from typing import Any, Dict

from filesizelib import Storage, StorageUnit
from filesizelib.platform_storage import (
    PlatformStorageBase,
    WindowsStorage,
    LinuxStorage,
    MacStorage
)


class TestPlatformStorageComprehensive:
    """Comprehensive tests for platform storage implementations."""
    
    def test_platform_storage_base_comprehensive(self):
        """Test comprehensive PlatformStorageBase functionality."""
        # Test with various initialization parameters
        storage1 = PlatformStorageBase()
        assert storage1.value == 0.0
        assert storage1.unit == StorageUnit.BYTES
        
        storage2 = PlatformStorageBase(2.5, StorageUnit.GIB)
        assert storage2.value == 2.5
        assert storage2.unit == StorageUnit.GIB
        
        # Test platform info
        info = storage1.get_platform_info()
        assert info['platform'] == 'PlatformStorageBase'
        assert info['supports_optimization'] is True
        assert info['file_system_type'] == 'generic'


class TestWindowsStorageComprehensive:
    """Comprehensive Windows storage tests."""
    
    @patch('platform.system')
    def test_windows_storage_nonexistent_path(self, mock_system):
        """Test Windows storage with non-existent path."""
        mock_system.return_value = 'Windows'
        
        storage = WindowsStorage()
        nonexistent_path = Path("/non/existent/path/file.txt")
        
        # Should raise FileNotFoundError
        with pytest.raises(FileNotFoundError, match="Path does not exist"):
            storage.get_size_from_path(nonexistent_path)
    
    @patch('platform.system')
    def test_windows_storage_exception_fallback(self, mock_system):
        """Test Windows storage falls back on exception."""
        mock_system.return_value = 'Windows'
        
        storage = WindowsStorage()
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = Path(temp_file.name)
        
        try:
            # Mock _should_use_windows_optimization to raise an exception
            with patch.object(storage, '_should_use_windows_optimization', side_effect=Exception("Test error")):
                # Should fall back to Storage.get_size_from_path and not raise
                result = storage.get_size_from_path(temp_path)
                assert isinstance(result, Storage)
                assert result.value > 0
        finally:
            temp_path.unlink()
    
    @patch('platform.system')
    def test_windows_optimization_heuristics(self, mock_system):
        """Test Windows optimization decision heuristics."""
        mock_system.return_value = 'Windows'
        
        storage = WindowsStorage()
        
        # Test with a directory that exists but is small
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a few files
            for i in range(3):
                (temp_path / f"file_{i}.txt").write_text(f"content {i}")
            
            # Should not use optimization for small directory
            should_optimize = storage._should_use_windows_optimization(temp_path)
            assert should_optimize is False
    
    @patch('platform.system')
    def test_windows_optimization_large_directory_mock(self, mock_system):
        """Test Windows optimization for large directory using mocks."""
        mock_system.return_value = 'Windows'
        
        storage = WindowsStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock the directory to appear large
            with patch('os.listdir') as mock_listdir:
                # Simulate a large directory (>100 files)
                mock_listdir.return_value = [f"file_{i}.txt" for i in range(150)]
                
                should_optimize = storage._should_use_windows_optimization(temp_path)
                assert should_optimize is True
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_windows_optimized_powershell_success(self, mock_run, mock_system):
        """Test Windows PowerShell optimization success."""
        mock_system.return_value = 'Windows'
        
        storage = WindowsStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            expected_size = 12345
            
            # Mock successful PowerShell execution
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = str(expected_size)
            mock_run.return_value = mock_result
            
            result = storage._get_size_windows_optimized(temp_path)
            assert result.value == expected_size
            assert result.unit == StorageUnit.BYTES
            
            # Verify PowerShell was called correctly
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert 'powershell' in args[0].lower()
    
    @patch('platform.system')
    @patch('subprocess.run')
    def test_windows_optimized_powershell_failure(self, mock_run, mock_system):
        """Test Windows PowerShell optimization failure and fallback."""
        mock_system.return_value = 'Windows'
        
        storage = WindowsStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.txt").write_text("test content")
            
            # Mock failed PowerShell execution
            mock_run.side_effect = subprocess.CalledProcessError(1, 'powershell')
            
            # Should fall back to standard method without raising exception
            result = storage._get_size_windows_optimized(temp_path)
            assert isinstance(result, Storage)
            assert result.value > 0  # Should get the size from fallback
    
    @patch('platform.system')
    def test_windows_platform_info(self, mock_system):
        """Test Windows platform info."""
        mock_system.return_value = 'Windows'
        
        storage = WindowsStorage()
        info = storage.get_platform_info()
        
        assert info['platform'] == 'Windows'
        assert info['file_system_type'] == 'NTFS/FAT32'
        assert info['supports_compression'] is True
        assert info['supports_sparse_files'] is True
        assert info['supports_junctions'] is True
        assert 'PowerShell/Win32' in info['api_optimization']


class TestLinuxStorageComprehensive:
    """Comprehensive Linux storage tests."""
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="Linux-specific test, skipping on Windows")
    @patch('platform.system')
    def test_linux_optimization_system_paths(self, mock_system):
        """Test Linux optimization for various system paths."""
        mock_system.return_value = 'Linux'
        
        storage = LinuxStorage()
        
        system_paths = [
            '/usr', '/var', '/opt', '/home'  # Only paths that are actually optimized
        ]
        
        for path_str in system_paths:
            path = Path(path_str)
            
            # Mock path existence and directory check
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    with patch.object(storage, '_is_large_directory', return_value=False):
                        try:
                            should_optimize = storage._should_use_linux_optimization(path)
                            assert should_optimize is True, f"Should optimize for {path_str}"
                        except (PermissionError, OSError):
                            # Expected for some system paths, just pass
                            pass
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="Linux-specific test, skipping on Windows")
    @patch('platform.system')
    def test_linux_large_directory_detection(self, mock_system):
        """Test Linux large directory detection."""
        mock_system.return_value = 'Linux'
        
        storage = LinuxStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Mock a large directory
            with patch('os.listdir') as mock_listdir:
                # Simulate directory with many files (>200)
                mock_listdir.return_value = [f"file_{i}" for i in range(250)]
                
                is_large = storage._is_large_directory(temp_path)
                assert is_large is True
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="Linux-specific test, skipping on Windows")
    @patch('platform.system')
    @patch('subprocess.run')
    def test_linux_du_command_success(self, mock_run, mock_system):
        """Test Linux du command success."""
        mock_system.return_value = 'Linux'
        
        storage = LinuxStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            expected_size = 98765
            
            # Mock successful du execution
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = f"{expected_size}\t{temp_path}"
            mock_run.return_value = mock_result
            
            result = storage._get_size_linux_optimized(temp_path)
            assert result.value == expected_size
            assert result.unit == StorageUnit.BYTES
            
            # Verify du was called with correct arguments
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert 'du' in args
            assert '-s' in args
            assert '-B1' in args
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="Linux-specific test, skipping on Windows")
    @patch('platform.system')
    @patch('subprocess.run')
    def test_linux_du_command_failure(self, mock_run, mock_system):
        """Test Linux du command failure and fallback."""
        mock_system.return_value = 'Linux'
        
        storage = LinuxStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.txt").write_text("test content")
            
            # Mock failed du execution
            mock_run.side_effect = subprocess.CalledProcessError(1, 'du')
            
            # Should fall back to standard method
            result = storage._get_size_linux_optimized(temp_path)
            assert isinstance(result, Storage)
            assert result.value > 0  # Should get size from fallback
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="Linux-specific test, skipping on Windows")
    @patch('platform.system')
    def test_linux_platform_info(self, mock_system):
        """Test Linux platform info."""
        mock_system.return_value = 'Linux'
        
        storage = LinuxStorage()
        info = storage.get_platform_info()
        
        assert info['platform'] == 'Linux'
        assert info['file_system_type'] == 'ext4/xfs/btrfs'
        assert info['supports_symlinks'] is True
        assert info['supports_hardlinks'] is True
        assert info['supports_mount_points'] is True
        assert 'du/find commands' in info['api_optimization']


class TestMacStorageComprehensive:
    """Comprehensive macOS storage tests."""
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="macOS-specific test, skipping on Windows")
    @patch('platform.system')
    def test_macos_optimization_app_bundles(self, mock_system):
        """Test macOS optimization for app bundles."""
        mock_system.return_value = 'Darwin'
        
        storage = MacStorage()
        
        app_paths = [
            '/Applications/Safari.app',
            '/Applications/Utilities/Terminal.app',
            '/System/Applications/Calculator.app'
        ]
        
        for path_str in app_paths:
            path = Path(path_str)
            
            # Mock path existence and directory check
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.is_dir', return_value=True):
                    with patch.object(storage, '_is_large_directory', return_value=False):
                        try:
                            should_optimize = storage._should_use_macos_optimization(path)
                            assert should_optimize is True, f"Should optimize for {path_str}"
                        except (PermissionError, OSError):
                            # Expected for some system paths, just pass
                            pass
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="macOS-specific test, skipping on Windows")
    @patch('platform.system')
    @patch('subprocess.run')
    def test_macos_du_command_success(self, mock_run, mock_system):
        """Test macOS du command success."""
        mock_system.return_value = 'Darwin'
        
        storage = MacStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            expected_size_kb = 1234
            
            # Mock successful du execution
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = f"{expected_size_kb}\t{temp_path}"
            mock_run.return_value = mock_result
            
            result = storage._get_size_macos_optimized(temp_path)
            # du returns KB, so should be converted to bytes
            expected_bytes = expected_size_kb * 1024
            assert result.value == expected_bytes
            assert result.unit == StorageUnit.BYTES
            
            # Verify du was called with correct arguments
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert 'du' in args
            assert '-s' in args
            assert '-k' in args
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="macOS-specific test, skipping on Windows")
    @patch('platform.system')
    @patch('subprocess.run')
    def test_macos_du_failure_fallback_to_resource_forks(self, mock_run, mock_system):
        """Test macOS du failure and fallback to resource fork method."""
        mock_system.return_value = 'Darwin'
        
        storage = MacStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            expected_size = 5678
            
            # Mock failed du execution
            mock_run.side_effect = subprocess.CalledProcessError(1, 'du')
            
            # Mock successful resource fork method
            expected_storage = Storage(expected_size, StorageUnit.BYTES)
            with patch.object(storage, '_get_size_with_resource_forks', return_value=expected_storage):
                result = storage._get_size_macos_optimized(temp_path)
                assert result.value == expected_size
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="macOS-specific test, skipping on Windows")
    @patch('platform.system')
    def test_macos_resource_forks_no_xattr(self, mock_system):
        """Test macOS resource forks when xattr is not available."""
        mock_system.return_value = 'Darwin'
        
        storage = MacStorage()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = Path(temp_file.name)
        
        try:
            # Mock xattr import failure
            with patch('builtins.__import__', side_effect=ImportError):
                result = storage._get_size_with_resource_forks(temp_path)
                # Should still get file size without extended attributes
                assert isinstance(result, Storage)
                assert result.value > 0
        finally:
            temp_path.unlink()
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="macOS-specific test, skipping on Windows")
    @patch('platform.system')
    def test_macos_resource_forks_with_xattr_mock(self, mock_system):
        """Test macOS resource forks with mocked xattr."""
        mock_system.return_value = 'Darwin'
        
        storage = MacStorage()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"test content")
            temp_path = Path(temp_file.name)
        
        try:
            # Mock xattr module
            mock_xattr = MagicMock()
            mock_xattr.listxattr.return_value = ['com.apple.ResourceFork']
            mock_xattr.getxattr.return_value = b'resource fork data' * 10  # 200 bytes
            
            with patch.dict('sys.modules', {'xattr': mock_xattr}):
                result = storage._get_size_with_resource_forks(temp_path)
                # Should include both file size and resource fork size
                assert isinstance(result, Storage)
                assert result.value >= len(b"test content")  # At least the file size
        finally:
            temp_path.unlink()
    
    @pytest.mark.skipif(platform.system() == 'Windows', reason="macOS-specific test, skipping on Windows")
    @patch('platform.system')
    def test_macos_platform_info(self, mock_system):
        """Test macOS platform info."""
        mock_system.return_value = 'Darwin'
        
        storage = MacStorage()
        info = storage.get_platform_info()
        
        assert info['platform'] == 'macOS'
        assert info['file_system_type'] == 'APFS/HFS+'
        assert info['supports_resource_forks'] is True
        assert info['supports_extended_attributes'] is True
        assert info['supports_snapshots'] is True
        assert info['supports_clones'] is True
        assert 'du/stat with resource forks' in info['api_optimization']


class TestPlatformStorageEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_all_platform_storage_exception_handling(self):
        """Test exception handling in all platform storage classes."""
        platforms = [WindowsStorage, LinuxStorage, MacStorage]
        
        for PlatformClass in platforms:
            storage = PlatformClass()
            
            # Test with invalid path types
            with pytest.raises((TypeError, AttributeError)):
                storage.get_size_from_path(None)
    
    def test_platform_storage_inheritance_chain(self):
        """Test complete inheritance chain."""
        platforms = [WindowsStorage, LinuxStorage, MacStorage]
        
        for PlatformClass in platforms:
            storage = PlatformClass(1.5, StorageUnit.MB)
            
            # Should inherit from PlatformStorageBase
            assert isinstance(storage, PlatformStorageBase)
            
            # Should inherit from Storage
            assert isinstance(storage, Storage)
            
            # Should maintain initialization values
            assert storage.value == 1.5
            assert storage.unit == StorageUnit.MB
            
            # Should support Storage methods
            assert storage.convert_to_bytes() == 1500000.0
    
    @patch('os.listdir')
    def test_os_listdir_permission_error(self, mock_listdir):
        """Test handling of permission errors during directory listing."""
        mock_listdir.side_effect = PermissionError("Permission denied")
        
        storage = LinuxStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Should handle permission error gracefully
            is_large = storage._is_large_directory(temp_path)
            assert is_large is False  # Should default to False on error
    
    @patch('os.listdir')
    def test_os_listdir_os_error(self, mock_listdir):
        """Test handling of OS errors during directory listing."""
        mock_listdir.side_effect = OSError("OS error")
        
        storage = MacStorage()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Should handle OS error gracefully
            is_large = storage._is_large_directory(temp_path)
            assert is_large is False  # Should default to False on error


class TestStorageGetPlatformStorage:
    """Test Storage.get_platform_storage() method comprehensively."""
    
    @patch('platform.system')
    def test_get_platform_storage_all_platforms(self, mock_system):
        """Test get_platform_storage for all supported platforms."""
        test_cases = [
            ('Windows', WindowsStorage),
            ('Linux', LinuxStorage),
            ('Darwin', MacStorage),
        ]
        
        for platform_name, expected_class in test_cases:
            mock_system.return_value = platform_name
            
            platform_storage = Storage.get_platform_storage()
            assert isinstance(platform_storage, expected_class)
            assert isinstance(platform_storage, PlatformStorageBase)
            assert isinstance(platform_storage, Storage)
    
    @patch('platform.system')
    def test_get_platform_storage_unsupported_platforms(self, mock_system):
        """Test get_platform_storage with unsupported platforms."""
        unsupported_platforms = [
            'FreeBSD', 'OpenBSD', 'NetBSD', 'SunOS', 'AIX', 'UnknownOS'
        ]
        
        for platform_name in unsupported_platforms:
            mock_system.return_value = platform_name
            
            with pytest.raises(ValueError, match=f"Unsupported platform: {platform_name}"):
                Storage.get_platform_storage()
    
    @patch('platform.system')
    def test_get_platform_storage_case_sensitivity(self, mock_system):
        """Test platform detection case sensitivity."""
        # These should work (exact matches)
        test_cases = [
            ('Windows', WindowsStorage),
            ('Linux', LinuxStorage),
            ('Darwin', MacStorage),
        ]
        
        for platform_name, expected_class in test_cases:
            mock_system.return_value = platform_name
            platform_storage = Storage.get_platform_storage()
            assert isinstance(platform_storage, expected_class)
        
        # These should fail (case mismatches)
        invalid_cases = ['windows', 'WINDOWS', 'linux', 'LINUX', 'darwin', 'DARWIN']
        
        for invalid_platform in invalid_cases:
            mock_system.return_value = invalid_platform
            with pytest.raises(ValueError):
                Storage.get_platform_storage()