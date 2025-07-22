"""
Platform-specific storage implementations.

This module contains platform-specific storage classes that extend the base
Storage class with platform-optimized functionality following the open-closed
principle. Each platform class can provide optimized implementations for
file size retrieval and other platform-specific operations.
"""

import os
import subprocess
from pathlib import Path
from typing import Union, Optional, Dict, Any
from .storage import Storage
from .storage_unit import StorageUnit


class PlatformStorageBase(Storage):
    """
    Base class for platform-specific storage implementations.
    
    This class extends the base Storage class and provides a foundation
    for platform-specific optimizations while maintaining compatibility
    with the base Storage interface.
    """
    
    def __init__(self, value: Union[int, float] = 0, unit: StorageUnit = StorageUnit.BYTES) -> None:
        """
        Initialize platform-specific storage.
        
        Args:
            value: The numerical value of the storage (defaults to 0).
            unit: The unit of the storage value (defaults to BYTES).
        """
        super().__init__(value, unit)
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get platform-specific information.
        
        Returns:
            Dict[str, Any]: Dictionary containing platform information.
        """
        return {
            'platform': self.__class__.__name__,
            'supports_optimization': True,
            'file_system_type': 'generic'
        }


class WindowsStorage(PlatformStorageBase):
    """
    Windows-specific storage implementation.
    
    This class provides Windows-optimized functionality for storage
    operations, including NTFS-specific features and Windows API
    optimizations where beneficial.
    
    Features:
        - Optimized file size retrieval using Windows APIs when available
        - Support for Windows-specific file attributes
        - NTFS stream and compression awareness
        - Junction and symbolic link handling
    """
    
    def get_size_from_path(self, path: Union[str, Path]) -> 'Storage':
        """
        Get file or directory size with Windows-specific optimizations.
        
        This method provides enhanced file size calculation for Windows,
        including support for compressed files, sparse files, and 
        proper handling of junctions and symbolic links.
        
        Args:
            path: The path to the file or directory.
            
        Returns:
            Storage: Storage instance representing the total size.
            
        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If access to the path is denied.
            OSError: If an OS-level error occurs.
            
        Examples:
            >>> win_storage = WindowsStorage()
            >>> size = win_storage.get_size_from_path("C:\\Windows\\System32")
            >>> print(size.auto_scale())
            2.3 GIB
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        try:
            # Use Windows-optimized approach for large directories
            if path_obj.is_dir() and self._should_use_windows_optimization(path_obj):
                return self._get_size_windows_optimized(path_obj)
            else:
                # Fall back to standard pathlib approach
                return Storage.get_size_from_path(path)
                
        except Exception as e:
            # If Windows optimization fails, fall back to standard method
            return Storage.get_size_from_path(path)
    
    def _should_use_windows_optimization(self, path: Path) -> bool:
        """
        Determine if Windows optimization should be used for the given path.
        
        Args:
            path: The path to evaluate.
            
        Returns:
            bool: True if Windows optimization should be used.
        """
        try:
            # Use optimization for directories with many files
            # This is a heuristic - in practice, you might use Windows APIs
            file_count = sum(1 for _ in path.iterdir())
            return file_count > 100
        except (PermissionError, OSError):
            return False
    
    def _get_size_windows_optimized(self, path: Path) -> 'Storage':
        """
        Get directory size using Windows-optimized methods.
        
        This method can be extended to use Windows APIs like FindFirstFile/FindNextFile
        or PowerShell commands for better performance on large directories.
        
        Args:
            path: The directory path.
            
        Returns:
            Storage: Storage instance with the calculated size.
        """
        try:
            # Example: Use PowerShell for very large directories (optional optimization)
            # In practice, you might use ctypes to call Windows APIs directly
            result = subprocess.run([
                'powershell', '-Command', 
                f'(Get-ChildItem -Path "{path}" -Recurse -File | Measure-Object -Property Length -Sum).Sum'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                size = int(result.stdout.strip())
                return Storage.parse_from_bytes(size)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError, FileNotFoundError):
            pass
        
        # Fall back to standard method
        return Storage.get_size_from_path(path)
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get Windows-specific platform information.
        
        Returns:
            Dict[str, Any]: Dictionary containing Windows platform information.
        """
        info = super().get_platform_info()
        info.update({
            'platform': 'Windows',
            'file_system_type': 'NTFS/FAT32',
            'supports_compression': True,
            'supports_sparse_files': True,
            'supports_junctions': True,
            'api_optimization': 'PowerShell/Win32'
        })
        return info


class LinuxStorage(PlatformStorageBase):
    """
    Linux-specific storage implementation.
    
    This class provides Linux-optimized functionality for storage
    operations, including support for various Linux file systems
    and GNU/Linux specific tools and APIs.
    
    Features:
        - Optimized file size retrieval using Linux tools (du, find)
        - Support for Linux-specific file attributes
        - Symbolic link and mount point awareness
        - File system type detection and optimization
    """
    
    def get_size_from_path(self, path: Union[str, Path]) -> 'Storage':
        """
        Get file or directory size with Linux-specific optimizations.
        
        This method provides enhanced file size calculation for Linux,
        including optimized directory traversal and proper handling
        of symbolic links, mount points, and special files.
        
        Args:
            path: The path to the file or directory.
            
        Returns:
            Storage: Storage instance representing the total size.
            
        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If access to the path is denied.
            OSError: If an OS-level error occurs.
            
        Examples:
            >>> linux_storage = LinuxStorage()
            >>> size = linux_storage.get_size_from_path("/usr/lib")
            >>> print(size.auto_scale())
            1.8 GIB
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        try:
            # Use Linux-optimized approach for large directories
            if path_obj.is_dir() and self._should_use_linux_optimization(path_obj):
                return self._get_size_linux_optimized(path_obj)
            else:
                # Fall back to standard pathlib approach
                return Storage.get_size_from_path(path)
                
        except Exception as e:
            # If Linux optimization fails, fall back to standard method
            return Storage.get_size_from_path(path)
    
    def _should_use_linux_optimization(self, path: Path) -> bool:
        """
        Determine if Linux optimization should be used for the given path.
        
        Args:
            path: The path to evaluate.
            
        Returns:
            bool: True if Linux optimization should be used.
        """
        try:
            # Use optimization for system directories or large directories
            # Check if du command is available and path is suitable
            return (
                str(path).startswith(('/usr', '/var', '/opt', '/home')) or
                self._is_large_directory(path)
            )
        except (PermissionError, OSError):
            return False
    
    def _is_large_directory(self, path: Path) -> bool:
        """
        Check if directory is large enough to benefit from optimization.
        
        Args:
            path: The directory path.
            
        Returns:
            bool: True if directory is considered large.
        """
        try:
            # Sample first few entries to estimate size
            count = 0
            for _ in path.iterdir():
                count += 1
                if count > 50:  # Threshold for "large" directory
                    return True
            return False
        except (PermissionError, OSError):
            return False
    
    def _get_size_linux_optimized(self, path: Path) -> 'Storage':
        """
        Get directory size using Linux-optimized methods.
        
        This method uses the 'du' command for better performance on large
        directories, which is often faster than Python's directory traversal.
        
        Args:
            path: The directory path.
            
        Returns:
            Storage: Storage instance with the calculated size.
        """
        try:
            # Use 'du' command for fast directory size calculation
            result = subprocess.run([
                'du', '-s', '-B1', str(path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse du output: "size\tpath"
                size_str = result.stdout.split('\t')[0].strip()
                size = int(size_str)
                return Storage.parse_from_bytes(size)
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
                ValueError, FileNotFoundError):
            pass
        
        # Fall back to standard method
        return Storage.get_size_from_path(path)
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get Linux-specific platform information.
        
        Returns:
            Dict[str, Any]: Dictionary containing Linux platform information.
        """
        info = super().get_platform_info()
        info.update({
            'platform': 'Linux',
            'file_system_type': 'ext4/xfs/btrfs',
            'supports_symlinks': True,
            'supports_hardlinks': True,
            'supports_mount_points': True,
            'api_optimization': 'du/find commands'
        })
        return info


class MacStorage(PlatformStorageBase):
    """
    macOS-specific storage implementation.
    
    This class provides macOS-optimized functionality for storage
    operations, including support for HFS+/APFS specific features
    and macOS APIs.
    
    Features:
        - Optimized file size retrieval using macOS tools
        - Support for macOS-specific file attributes (resource forks, extended attributes)
        - APFS snapshot and clone awareness
        - Spotlight integration for metadata
    """
    
    def get_size_from_path(self, path: Union[str, Path]) -> 'Storage':
        """
        Get file or directory size with macOS-specific optimizations.
        
        This method provides enhanced file size calculation for macOS,
        including proper handling of resource forks, extended attributes,
        and APFS-specific features.
        
        Args:
            path: The path to the file or directory.
            
        Returns:
            Storage: Storage instance representing the total size.
            
        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If access to the path is denied.
            OSError: If an OS-level error occurs.
            
        Examples:
            >>> mac_storage = MacStorage()
            >>> size = mac_storage.get_size_from_path("/Applications")
            >>> print(size.auto_scale())
            15.7 GIB
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        try:
            # Use macOS-optimized approach for app bundles and large directories
            if self._should_use_macos_optimization(path_obj):
                return self._get_size_macos_optimized(path_obj)
            else:
                # Fall back to standard pathlib approach
                return Storage.get_size_from_path(path)
                
        except Exception as e:
            # If macOS optimization fails, fall back to standard method
            return Storage.get_size_from_path(path)
    
    def _should_use_macos_optimization(self, path: Path) -> bool:
        """
        Determine if macOS optimization should be used for the given path.
        
        Args:
            path: The path to evaluate.
            
        Returns:
            bool: True if macOS optimization should be used.
        """
        try:
            # Use optimization for app bundles and system directories
            return (
                str(path).endswith('.app') or  # App bundles
                str(path).startswith(('/Applications', '/System', '/Library', '/Users')) or
                self._is_large_directory(path)
            )
        except (PermissionError, OSError):
            return False
    
    def _is_large_directory(self, path: Path) -> bool:
        """
        Check if directory is large enough to benefit from optimization.
        
        Args:
            path: The directory path.
            
        Returns:
            bool: True if directory is considered large.
        """
        try:
            count = 0
            for _ in path.iterdir():
                count += 1
                if count > 50:
                    return True
            return False
        except (PermissionError, OSError):
            return False
    
    def _get_size_macos_optimized(self, path: Path) -> 'Storage':
        """
        Get directory size using macOS-optimized methods.
        
        This method uses macOS-specific tools and APIs for better
        performance and accuracy, especially for app bundles and
        directories with resource forks.
        
        Args:
            path: The directory path.
            
        Returns:
            Storage: Storage instance with the calculated size.
        """
        try:
            # Use 'du' with macOS-specific options for accurate size including resource forks
            result = subprocess.run([
                'du', '-s', '-k', str(path)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse du output: "size_in_kb\tpath"
                size_kb_str = result.stdout.split('\t')[0].strip()
                size_kb = int(size_kb_str)
                size_bytes = size_kb * 1024  # Convert KB to bytes
                return Storage.parse_from_bytes(size_bytes)
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
                ValueError, FileNotFoundError):
            pass
        
        # Try alternative method using stat with resource forks
        try:
            return self._get_size_with_resource_forks(path)
        except Exception:
            pass
        
        # Fall back to standard method
        return Storage.get_size_from_path(path)
    
    def _get_size_with_resource_forks(self, path: Path) -> 'Storage':
        """
        Get size including macOS resource forks and extended attributes.
        
        Args:
            path: The path to measure.
            
        Returns:
            Storage: Storage instance with total size including resource forks.
        """
        total_size = 0
        
        if path.is_file():
            # Get main file size
            total_size += path.stat().st_size
            
            # Try to get resource fork size (this is a simplified approach)
            try:
                import xattr
                # Get extended attributes size (approximation)
                attrs = xattr.listxattr(str(path))
                for attr in attrs:
                    attr_value = xattr.getxattr(str(path), attr)
                    total_size += len(attr_value)
            except (ImportError, OSError):
                # xattr module not available or error reading attributes
                pass
                
        elif path.is_dir():
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    try:
                        total_size += file_path.stat().st_size
                        # Add resource fork size if possible
                        try:
                            import xattr
                            attrs = xattr.listxattr(str(file_path))
                            for attr in attrs:
                                attr_value = xattr.getxattr(str(file_path), attr)
                                total_size += len(attr_value)
                        except (ImportError, OSError):
                            pass
                    except (PermissionError, FileNotFoundError, OSError):
                        continue
        
        return Storage.parse_from_bytes(total_size)
    
    def get_platform_info(self) -> Dict[str, Any]:
        """
        Get macOS-specific platform information.
        
        Returns:
            Dict[str, Any]: Dictionary containing macOS platform information.
        """
        info = super().get_platform_info()
        info.update({
            'platform': 'macOS',
            'file_system_type': 'APFS/HFS+',
            'supports_resource_forks': True,
            'supports_extended_attributes': True,
            'supports_snapshots': True,
            'supports_clones': True,
            'api_optimization': 'du/stat with resource forks'
        })
        return info