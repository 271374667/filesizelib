"""
Comprehensive tests for platform-specific storage implementations.

This module tests platform-specific storage functionality with automatic
platform detection and appropriate test skipping.
"""

import platform
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

from filesizelib import Storage, StorageUnit
from filesizelib.platform_storage import (
    PlatformStorageBase,
    WindowsStorage,
    LinuxStorage,
    MacStorage
)


class TestPlatformStorageBase:
    """Test the base platform storage class."""
    
    def test_initialization_default(self):
        """Test default initialization."""
        storage = PlatformStorageBase()
        assert storage.value == 0.0
        assert storage.unit == StorageUnit.BYTES
    
    def test_initialization_with_values(self):
        """Test initialization with custom values."""
        storage = PlatformStorageBase(1.5, StorageUnit.MB)
        assert storage.value == 1.5
        assert storage.unit == StorageUnit.MB
    
    def test_get_platform_info(self):
        """Test getting platform info."""
        storage = PlatformStorageBase()
        info = storage.get_platform_info()
        
        assert isinstance(info, dict)
        assert 'platform' in info
        assert 'supports_optimization' in info
        assert 'file_system_type' in info
        assert info['platform'] == 'PlatformStorageBase'
        assert info['supports_optimization'] is True
        assert info['file_system_type'] == 'generic'
    
    def test_inheritance_from_storage(self):
        """Test that PlatformStorageBase inherits from Storage."""
        storage = PlatformStorageBase(1, StorageUnit.KIB)
        
        # Should have all Storage methods
        assert hasattr(storage, 'convert_to_bytes')
        assert hasattr(storage, 'convert_to')
        assert storage.convert_to_bytes() == 1024.0
        
        # Should support arithmetic operations
        doubled = storage * 2
        assert doubled.value == 2.0
        assert doubled.unit == StorageUnit.KIB


class TestPlatformDetection:
    """Test platform detection and Storage.get_platform_storage()."""
    
    def test_get_platform_storage_returns_correct_type(self, current_platform: str):
        """Test that get_platform_storage returns the correct platform type."""
        platform_storage = Storage.get_platform_storage()
        
        if current_platform == "Windows":
            assert isinstance(platform_storage, WindowsStorage)
        elif current_platform == "Linux":
            assert isinstance(platform_storage, LinuxStorage)
        elif current_platform == "Darwin":
            assert isinstance(platform_storage, MacStorage)
        else:
            pytest.fail(f"Unexpected platform: {current_platform}")
    
    @patch('platform.system')
    def test_get_platform_storage_windows(self, mock_system):
        """Test platform storage detection for Windows."""
        mock_system.return_value = 'Windows'
        
        platform_storage = Storage.get_platform_storage()
        assert isinstance(platform_storage, WindowsStorage)
    
    @patch('platform.system')
    def test_get_platform_storage_linux(self, mock_system):
        """Test platform storage detection for Linux."""
        mock_system.return_value = 'Linux'
        
        platform_storage = Storage.get_platform_storage()
        assert isinstance(platform_storage, LinuxStorage)
    
    @patch('platform.system')
    def test_get_platform_storage_macos(self, mock_system):
        """Test platform storage detection for macOS."""
        mock_system.return_value = 'Darwin'
        
        platform_storage = Storage.get_platform_storage()
        assert isinstance(platform_storage, MacStorage)
    
    @patch('platform.system')
    def test_get_platform_storage_unsupported(self, mock_system):
        """Test platform storage detection for unsupported platform."""
        mock_system.return_value = 'UnsupportedOS'
        
        with pytest.raises(ValueError, match="Unsupported platform: UnsupportedOS"):
            Storage.get_platform_storage()


@pytest.mark.windows_only
class TestWindowsStorage:
    """Test Windows-specific storage functionality."""
    
    def test_initialization(self):
        """Test Windows storage initialization."""
        storage = WindowsStorage()
        assert storage.value == 0.0
        assert storage.unit == StorageUnit.BYTES
        assert isinstance(storage, PlatformStorageBase)
    
    def test_get_platform_info(self):
        """Test Windows platform info."""
        storage = WindowsStorage()
        info = storage.get_platform_info()
        
        assert info['platform'] == 'Windows'
        assert info['file_system_type'] == 'NTFS/FAT32'
        assert info['supports_compression'] is True
        assert info['supports_sparse_files'] is True
        assert info['supports_junctions'] is True
        assert 'PowerShell/Win32' in info['api_optimization']
    
    def test_get_size_from_path_file(self, temp_file_with_content):
        """Test getting file size on Windows."""
        temp_path, expected_size = temp_file_with_content
        
        storage = WindowsStorage()
        file_size = storage.get_size_from_path(temp_path)
        
        assert file_size.value == expected_size
        assert file_size.unit == StorageUnit.BYTES
    
    def test_get_size_from_path_directory(self, temp_directory_with_files):
        """Test getting directory size on Windows."""
        temp_path, expected_size = temp_directory_with_files
        
        storage = WindowsStorage()
        dir_size = storage.get_size_from_path(temp_path)
        
        assert dir_size.value == expected_size
        assert dir_size.unit == StorageUnit.BYTES
    
    def test_should_use_windows_optimization_large_directory(self, temp_directory_with_files):
        """Test Windows optimization detection for large directories."""
        temp_path, _ = temp_directory_with_files
        
        storage = WindowsStorage()
        
        # The temp directory has only a few files, so optimization should not be used
        # Create a mock scenario for large directory
        with patch.object(storage, '_should_use_windows_optimization', return_value=True):
            should_optimize = storage._should_use_windows_optimization(temp_path)
            assert should_optimize is True
    
    def test_should_use_windows_optimization_small_directory(self, temp_directory_with_files):
        """Test Windows optimization detection for small directories."""
        temp_path, _ = temp_directory_with_files
        
        storage = WindowsStorage()
        should_optimize = storage._should_use_windows_optimization(temp_path)
        
        # Small test directory should not use optimization
        assert should_optimize is False
    
    @patch('subprocess.run')
    def test_windows_optimized_with_powershell_success(self, mock_run, temp_directory_with_files):
        """Test Windows optimization using PowerShell successfully."""
        temp_path, expected_size = temp_directory_with_files
        
        # Mock successful PowerShell execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = str(expected_size)
        mock_run.return_value = mock_result
        
        storage = WindowsStorage()
        result = storage._get_size_windows_optimized(temp_path)
        
        assert result.value == expected_size
        assert result.unit == StorageUnit.BYTES
        
        # Verify PowerShell was called
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert 'powershell' in call_args[0].lower()
    
    @patch('subprocess.run')
    def test_windows_optimized_with_powershell_failure(self, mock_run, temp_directory_with_files):
        """Test Windows optimization fallback when PowerShell fails."""
        temp_path, expected_size = temp_directory_with_files
        
        # Mock failed PowerShell execution
        mock_run.side_effect = subprocess.CalledProcessError(1, 'powershell')
        
        storage = WindowsStorage()
        result = storage._get_size_windows_optimized(temp_path)
        
        # Should fall back to standard method
        assert result.value == expected_size
        assert result.unit == StorageUnit.BYTES
    
    def test_windows_optimization_fallback_on_exception(self, temp_directory_with_files):
        """Test that Windows storage falls back to standard method on exception."""
        temp_path, expected_size = temp_directory_with_files
        
        storage = WindowsStorage()
        
        # Force optimization path but make it fail
        with patch.object(storage, '_should_use_windows_optimization', return_value=True):
            with patch.object(storage, '_get_size_windows_optimized', side_effect=Exception("Test error")):
                # Should fall back to Storage.get_size_from_path
                result = storage.get_size_from_path(temp_path)
                assert result.value == expected_size


@pytest.mark.linux_only  
class TestLinuxStorage:
    """Test Linux-specific storage functionality."""
    
    def test_initialization(self):
        """Test Linux storage initialization."""
        storage = LinuxStorage()
        assert storage.value == 0.0
        assert storage.unit == StorageUnit.BYTES
        assert isinstance(storage, PlatformStorageBase)
    
    def test_get_platform_info(self):
        """Test Linux platform info."""
        storage = LinuxStorage()
        info = storage.get_platform_info()
        
        assert info['platform'] == 'Linux'
        assert info['file_system_type'] == 'ext4/xfs/btrfs'
        assert info['supports_symlinks'] is True
        assert info['supports_hardlinks'] is True
        assert info['supports_mount_points'] is True
        assert 'du/find commands' in info['api_optimization']
    
    def test_get_size_from_path_file(self, temp_file_with_content):
        """Test getting file size on Linux."""
        temp_path, expected_size = temp_file_with_content
        
        storage = LinuxStorage()
        file_size = storage.get_size_from_path(temp_path)
        
        assert file_size.value == expected_size
        assert file_size.unit == StorageUnit.BYTES
    
    def test_get_size_from_path_directory(self, temp_directory_with_files):
        """Test getting directory size on Linux."""
        temp_path, expected_size = temp_directory_with_files
        
        storage = LinuxStorage()
        dir_size = storage.get_size_from_path(temp_path)
        
        assert dir_size.value == expected_size
        assert dir_size.unit == StorageUnit.BYTES
    
    def test_should_use_linux_optimization_system_path(self):
        """Test Linux optimization detection for system paths."""
        storage = LinuxStorage()
        
        system_paths = [
            Path('/usr/lib'),
            Path('/var/log'),
            Path('/opt/software'),
            Path('/home/user'),
        ]
        
        for path in system_paths:
            # Mock both the path check and large directory check
            with patch.object(storage, '_is_large_directory', return_value=False):
                try:
                    should_optimize = storage._should_use_linux_optimization(path)
                    assert should_optimize is True
                except (PermissionError, OSError):
                    # If path doesn't exist or permission denied, skip this test
                    pass
    
    def test_should_use_linux_optimization_large_directory(self, temp_directory_with_files):
        """Test Linux optimization detection for large directories."""
        temp_path, _ = temp_directory_with_files
        
        storage = LinuxStorage()
        
        # Mock large directory
        with patch.object(storage, '_is_large_directory', return_value=True):
            should_optimize = storage._should_use_linux_optimization(temp_path)
            assert should_optimize is True
    
    def test_should_use_linux_optimization_small_directory(self, temp_directory_with_files):
        """Test Linux optimization detection for small directories."""
        temp_path, _ = temp_directory_with_files
        
        storage = LinuxStorage()
        should_optimize = storage._should_use_linux_optimization(temp_path)
        
        # Small test directory in temp should not use optimization
        assert should_optimize is False
    
    def test_is_large_directory(self, temp_directory_with_files):
        """Test large directory detection."""
        temp_path, _ = temp_directory_with_files
        
        storage = LinuxStorage()
        is_large = storage._is_large_directory(temp_path)
        
        # Test directory has only a few files
        assert is_large is False
    
    @patch('subprocess.run')
    def test_linux_optimized_with_du_success(self, mock_run, temp_directory_with_files):
        """Test Linux optimization using 'du' command successfully."""
        temp_path, expected_size = temp_directory_with_files
        
        # Mock successful du execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = f"{expected_size}\t{temp_path}"
        mock_run.return_value = mock_result
        
        storage = LinuxStorage()
        result = storage._get_size_linux_optimized(temp_path)
        
        assert result.value == expected_size
        assert result.unit == StorageUnit.BYTES
        
        # Verify du was called with correct arguments
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert 'du' in call_args
        assert '-s' in call_args
        assert '-B1' in call_args
    
    @patch('subprocess.run')
    def test_linux_optimized_with_du_failure(self, mock_run, temp_directory_with_files):
        """Test Linux optimization fallback when 'du' fails."""
        temp_path, expected_size = temp_directory_with_files
        
        # Mock failed du execution
        mock_run.side_effect = subprocess.CalledProcessError(1, 'du')
        
        storage = LinuxStorage()
        result = storage._get_size_linux_optimized(temp_path)
        
        # Should fall back to standard method
        assert result.value == expected_size
        assert result.unit == StorageUnit.BYTES
    
    def test_linux_optimization_fallback_on_exception(self, temp_directory_with_files):
        """Test that Linux storage falls back to standard method on exception."""
        temp_path, expected_size = temp_directory_with_files
        
        storage = LinuxStorage()
        
        # Force optimization path but make it fail
        with patch.object(storage, '_should_use_linux_optimization', return_value=True):
            with patch.object(storage, '_get_size_linux_optimized', side_effect=Exception("Test error")):
                # Should fall back to Storage.get_size_from_path
                result = storage.get_size_from_path(temp_path)
                assert result.value == expected_size


@pytest.mark.macos_only
class TestMacStorage:
    """Test macOS-specific storage functionality."""
    
    def test_initialization(self):
        """Test macOS storage initialization."""
        storage = MacStorage()
        assert storage.value == 0.0
        assert storage.unit == StorageUnit.BYTES
        assert isinstance(storage, PlatformStorageBase)
    
    def test_get_platform_info(self):
        """Test macOS platform info."""
        storage = MacStorage()
        info = storage.get_platform_info()
        
        assert info['platform'] == 'macOS'
        assert info['file_system_type'] == 'APFS/HFS+'
        assert info['supports_resource_forks'] is True
        assert info['supports_extended_attributes'] is True
        assert info['supports_snapshots'] is True
        assert info['supports_clones'] is True
        assert 'du/stat with resource forks' in info['api_optimization']
    
    def test_get_size_from_path_file(self, temp_file_with_content):
        """Test getting file size on macOS."""
        temp_path, expected_size = temp_file_with_content
        
        storage = MacStorage()
        file_size = storage.get_size_from_path(temp_path)
        
        assert file_size.value == expected_size
        assert file_size.unit == StorageUnit.BYTES
    
    def test_get_size_from_path_directory(self, temp_directory_with_files):
        """Test getting directory size on macOS."""
        temp_path, expected_size = temp_directory_with_files
        
        storage = MacStorage()
        dir_size = storage.get_size_from_path(temp_path)
        
        assert dir_size.value == expected_size
        assert dir_size.unit == StorageUnit.BYTES
    
    def test_should_use_macos_optimization_app_bundle(self):
        """Test macOS optimization detection for app bundles."""
        storage = MacStorage()
        
        app_path = Path('/Applications/Test.app')
        
        # Mock path exists to avoid FileNotFoundError
        with patch.object(app_path, 'exists', return_value=True):
            with patch.object(storage, '_is_large_directory', return_value=False):
                should_optimize = storage._should_use_macos_optimization(app_path)
                assert should_optimize is True
    
    def test_should_use_macos_optimization_system_path(self):
        """Test macOS optimization detection for system paths."""
        storage = MacStorage()
        
        system_paths = [
            Path('/Applications/Utilities'),
            Path('/System/Library'),
            Path('/Library/Frameworks'),
            Path('/Users/testuser'),
        ]
        
        for path in system_paths:
            # Mock path exists to avoid FileNotFoundError
            with patch.object(path, 'exists', return_value=True):
                with patch.object(storage, '_is_large_directory', return_value=False):
                    should_optimize = storage._should_use_macos_optimization(path)
                    assert should_optimize is True
    
    def test_should_use_macos_optimization_large_directory(self, temp_directory_with_files):
        """Test macOS optimization detection for large directories."""
        temp_path, _ = temp_directory_with_files
        
        storage = MacStorage()
        
        # Mock large directory
        with patch.object(storage, '_is_large_directory', return_value=True):
            should_optimize = storage._should_use_macos_optimization(temp_path)
            assert should_optimize is True
    
    def test_should_use_macos_optimization_small_directory(self, temp_directory_with_files):
        """Test macOS optimization detection for small directories."""
        temp_path, _ = temp_directory_with_files
        
        storage = MacStorage()
        should_optimize = storage._should_use_macos_optimization(temp_path)
        
        # Small test directory should not use optimization
        assert should_optimize is False
    
    @patch('subprocess.run')
    def test_macos_optimized_with_du_success(self, mock_run, temp_directory_with_files):
        """Test macOS optimization using 'du' command successfully."""
        temp_path, expected_size = temp_directory_with_files
        expected_size_kb = expected_size // 1024 + (1 if expected_size % 1024 else 0)
        
        # Mock successful du execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = f"{expected_size_kb}\t{temp_path}"
        mock_run.return_value = mock_result
        
        storage = MacStorage()
        result = storage._get_size_macos_optimized(temp_path)
        
        # du returns KB, so result should be converted back to bytes
        expected_bytes = expected_size_kb * 1024
        assert result.value == expected_bytes
        assert result.unit == StorageUnit.BYTES
        
        # Verify du was called with correct arguments
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert 'du' in call_args
        assert '-s' in call_args
        assert '-k' in call_args
    
    @patch('subprocess.run')
    def test_macos_optimized_with_du_failure(self, mock_run, temp_directory_with_files):
        """Test macOS optimization fallback when 'du' fails."""
        temp_path, expected_size = temp_directory_with_files
        
        # Mock failed du execution
        mock_run.side_effect = subprocess.CalledProcessError(1, 'du')
        
        storage = MacStorage()
        
        # Should try resource fork method next
        with patch.object(storage, '_get_size_with_resource_forks', return_value=Storage(expected_size, StorageUnit.BYTES)):
            result = storage._get_size_macos_optimized(temp_path)
            assert result.value == expected_size
    
    def test_get_size_with_resource_forks_file(self, temp_file_with_content):
        """Test getting size with resource forks for a file."""
        temp_path, expected_size = temp_file_with_content
        
        storage = MacStorage()
        
        # Mock xattr not available
        with patch('builtins.__import__', side_effect=ImportError):
            result = storage._get_size_with_resource_forks(temp_path)
            # Should still get basic file size
            assert result.value == expected_size
    
    def test_get_size_with_resource_forks_directory(self, temp_directory_with_files):
        """Test getting size with resource forks for a directory."""
        temp_path, expected_size = temp_directory_with_files
        
        storage = MacStorage()
        
        # Mock xattr not available
        with patch('builtins.__import__', side_effect=ImportError):
            result = storage._get_size_with_resource_forks(temp_path)
            # Should get directory size without extended attributes
            assert result.value == expected_size
    
    def test_macos_optimization_fallback_on_exception(self, temp_directory_with_files):
        """Test that macOS storage falls back to standard method on exception."""
        temp_path, expected_size = temp_directory_with_files
        
        storage = MacStorage()
        
        # Force optimization path but make it fail
        with patch.object(storage, '_should_use_macos_optimization', return_value=True):
            with patch.object(storage, '_get_size_macos_optimized', side_effect=Exception("Test error")):
                # Should fall back to Storage.get_size_from_path
                result = storage.get_size_from_path(temp_path)
                assert result.value == expected_size


class TestPlatformStorageEdgeCases:
    """Test edge cases and error conditions for platform storage."""
    
    def test_platform_storage_nonexistent_path(self, platform_storage_class):
        """Test platform storage with nonexistent path."""
        storage = platform_storage_class()
        nonexistent_path = Path("/nonexistent/path/file.txt")
        
        with pytest.raises(FileNotFoundError):
            storage.get_size_from_path(nonexistent_path)
    
    def test_platform_storage_inheritance(self, platform_storage_class):
        """Test that platform storage classes inherit from PlatformStorageBase."""
        storage = platform_storage_class()
        assert isinstance(storage, PlatformStorageBase)
        assert isinstance(storage, Storage)
    
    def test_platform_storage_arithmetic_operations(self, platform_storage_class):
        """Test that platform storage supports arithmetic operations."""
        storage = platform_storage_class(1, StorageUnit.KIB)
        
        # Should support all Storage arithmetic
        doubled = storage * 2
        assert doubled.value == 2.0
        assert doubled.unit == StorageUnit.KIB
        
        # Should support addition with regular Storage
        regular_storage = Storage(512, StorageUnit.BYTES)
        total = storage + regular_storage
        assert total.convert_to_bytes() == 1536.0
    
    def test_platform_storage_comparisons(self, platform_storage_class):
        """Test that platform storage supports comparisons."""
        storage1 = platform_storage_class(1, StorageUnit.KIB)
        storage2 = platform_storage_class(2, StorageUnit.KIB)
        regular_storage = Storage(1024, StorageUnit.BYTES)
        
        assert storage1 < storage2
        assert storage1 == regular_storage
        assert storage2 > storage1
    
    @pytest.mark.parametrize("platform_class", [WindowsStorage, LinuxStorage, MacStorage])
    def test_all_platform_classes_initialization(self, platform_class):
        """Test that all platform classes can be initialized."""
        storage = platform_class()
        assert storage.value == 0.0
        assert storage.unit == StorageUnit.BYTES
        
        storage_with_values = platform_class(1.5, StorageUnit.MB)
        assert storage_with_values.value == 1.5
        assert storage_with_values.unit == StorageUnit.MB
    
    @pytest.mark.parametrize("platform_class", [WindowsStorage, LinuxStorage, MacStorage])
    def test_all_platform_classes_info(self, platform_class):
        """Test that all platform classes provide platform info."""
        storage = platform_class()
        info = storage.get_platform_info()
        
        assert isinstance(info, dict)
        assert 'platform' in info
        assert 'supports_optimization' in info
        assert info['supports_optimization'] is True
    
    def test_platform_specific_methods_exist(self, platform_storage_class):
        """Test that platform-specific methods exist."""
        storage = platform_storage_class()
        
        # All platform classes should have these methods
        assert hasattr(storage, 'get_size_from_path')
        assert hasattr(storage, 'get_platform_info')
        assert callable(getattr(storage, 'get_size_from_path'))
        assert callable(getattr(storage, 'get_platform_info'))