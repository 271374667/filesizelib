"""
Core storage class implementation.

This module contains the main Storage class that provides storage unit
conversion, arithmetic operations, and parsing functionality.
"""

import re
import platform
from pathlib import Path
from typing import Union, Optional, overload
from .storage_unit import StorageUnit


class Storage:
    """
    A class representing storage with different units.

    This class provides methods for converting between different storage units,
    performing arithmetic operations, and comparing storage sizes.
    It also includes methods for getting the size of files or directories
    and parsing storage values from strings.

    Attributes:
        value (float): The numerical value of the storage.
        unit (StorageUnit): The unit of the storage value.

    Examples:
        >>> storage = Storage(1, StorageUnit.KIB)
        >>> print(storage.convert_to_bytes())
        1024.0
        
        >>> total = Storage(512, StorageUnit.BYTES) + Storage(1, StorageUnit.KIB)
        >>> print(total)
        1536.0 BYTES
        
        >>> parsed = Storage.parse("1.5 MB")
        >>> print(parsed)
        1.5 MB
    """

    def __init__(self, value: Union[int, float], unit: StorageUnit) -> None:
        """
        Initialize the storage with a value and a unit.

        Args:
            value: The numerical value of the storage.
            unit: The unit of the storage value.

        Raises:
            TypeError: If value is not a number or unit is not a StorageUnit.
            ValueError: If value is negative.
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"Value must be a number, got {type(value).__name__}")
        
        if not isinstance(unit, StorageUnit):
            raise TypeError(f"Unit must be a StorageUnit, got {type(unit).__name__}")
        
        if value < 0:
            raise ValueError("Storage value cannot be negative")
        
        self.value = float(value)
        self.unit = unit

    @classmethod
    def parse_from_bytes(cls, value: Union[int, float]) -> 'Storage':
        """
        Create a Storage instance from a value in bytes.

        Args:
            value: The value in bytes.

        Returns:
            Storage: A Storage instance with the value in bytes.

        Raises:
            TypeError: If value is not a number.
            ValueError: If value is negative.

        Examples:
            >>> storage = Storage.parse_from_bytes(1024)
            >>> print(storage)
            1024.0 BYTES
        """
        return cls(value, StorageUnit.BYTES)

    def convert_to_bytes(self) -> float:
        """
        Convert the storage value to bytes.

        Returns:
            float: The value in bytes.

        Examples:
            >>> storage = Storage(1, StorageUnit.KIB)
            >>> print(storage.convert_to_bytes())
            1024.0
        """
        return self.value * self.unit.value

    def convert_to(self, target_unit: StorageUnit) -> 'Storage':
        """
        Convert the storage to a different unit.

        Args:
            target_unit: The unit to convert to.

        Returns:
            Storage: A new Storage instance with the converted value.

        Examples:
            >>> storage = Storage(1024, StorageUnit.BYTES)
            >>> converted = storage.convert_to(StorageUnit.KIB)
            >>> print(converted)
            1.0 KIB
        """
        bytes_value = self.convert_to_bytes()
        new_value = bytes_value / target_unit.value
        return Storage(new_value, target_unit)

    # Convenient conversion methods for binary units
    def convert_to_kib(self) -> 'Storage':
        """Convert to kibibytes (KiB)."""
        return self.convert_to(StorageUnit.KIB)
    
    def convert_to_mib(self) -> 'Storage':
        """Convert to mebibytes (MiB)."""
        return self.convert_to(StorageUnit.MIB)
    
    def convert_to_gib(self) -> 'Storage':
        """Convert to gibibytes (GiB)."""
        return self.convert_to(StorageUnit.GIB)
    
    def convert_to_tib(self) -> 'Storage':
        """Convert to tebibytes (TiB)."""
        return self.convert_to(StorageUnit.TIB)
    
    def convert_to_pib(self) -> 'Storage':
        """Convert to pebibytes (PiB)."""
        return self.convert_to(StorageUnit.PIB)
    
    def convert_to_eib(self) -> 'Storage':
        """Convert to exbibytes (EiB)."""
        return self.convert_to(StorageUnit.EIB)
    
    def convert_to_zib(self) -> 'Storage':
        """Convert to zebibytes (ZiB)."""
        return self.convert_to(StorageUnit.ZIB)
    
    def convert_to_yib(self) -> 'Storage':
        """Convert to yobibytes (YiB)."""
        return self.convert_to(StorageUnit.YIB)

    # Convenient conversion methods for decimal units
    def convert_to_kb(self) -> 'Storage':
        """Convert to kilobytes (KB)."""
        return self.convert_to(StorageUnit.KB)
    
    def convert_to_mb(self) -> 'Storage':
        """Convert to megabytes (MB)."""
        return self.convert_to(StorageUnit.MB)
    
    def convert_to_gb(self) -> 'Storage':
        """Convert to gigabytes (GB)."""
        return self.convert_to(StorageUnit.GB)
    
    def convert_to_tb(self) -> 'Storage':
        """Convert to terabytes (TB)."""
        return self.convert_to(StorageUnit.TB)
    
    def convert_to_pb(self) -> 'Storage':
        """Convert to petabytes (PB)."""
        return self.convert_to(StorageUnit.PB)
    
    def convert_to_eb(self) -> 'Storage':
        """Convert to exabytes (EB)."""
        return self.convert_to(StorageUnit.EB)
    
    def convert_to_zb(self) -> 'Storage':
        """Convert to zettabytes (ZB)."""
        return self.convert_to(StorageUnit.ZB)
    
    def convert_to_yb(self) -> 'Storage':
        """Convert to yottabytes (YB)."""
        return self.convert_to(StorageUnit.YB)

    # Convenient conversion methods for bit units
    def convert_to_bits(self) -> 'Storage':
        """Convert to bits."""
        return self.convert_to(StorageUnit.BITS)
    
    def convert_to_kilobits(self) -> 'Storage':
        """Convert to kilobits."""
        return self.convert_to(StorageUnit.KILOBITS)
    
    def convert_to_megabits(self) -> 'Storage':
        """Convert to megabits."""
        return self.convert_to(StorageUnit.MEGABITS)
    
    def convert_to_gigabits(self) -> 'Storage':
        """Convert to gigabits."""
        return self.convert_to(StorageUnit.GIGABITS)
    
    def convert_to_terabits(self) -> 'Storage':
        """Convert to terabits."""
        return self.convert_to(StorageUnit.TERABITS)

    @classmethod
    def parse(cls, string: str, default_unit: Optional[StorageUnit] = None) -> 'Storage':
        """
        Parse a string to create a Storage instance.

        The string should be in the format "value unit", where value is a number
        and unit is one of the supported storage units. The parsing is:
        - Case insensitive
        - Supports both '.' and ',' as decimal separators  
        - Supports spaces and no spaces between value and unit
        - Uses bytes as default unit if unit is not recognized or provided

        Args:
            string: A string representing the storage value.
            default_unit: The unit to use if no unit is found or recognized.
                         Defaults to StorageUnit.BYTES.

        Returns:
            Storage: A Storage instance.

        Raises:
            ValueError: If the input string is invalid or cannot be parsed.

        Examples:
            >>> storage = Storage.parse("1.5 MB")
            >>> print(storage)
            1.5 MB
            
            >>> storage = Storage.parse("1,024 KiB")
            >>> print(storage) 
            1024.0 KIB
            
            >>> storage = Storage.parse("500")  # defaults to bytes
            >>> print(storage)
            500.0 BYTES
        """
        if not isinstance(string, str):
            raise TypeError(f"Input must be a string, got {type(string).__name__}")
        
        if not string.strip():
            raise ValueError("Input string cannot be empty")
        
        if default_unit is None:
            default_unit = StorageUnit.BYTES
        
        # Normalize the string: strip whitespace, convert to lowercase
        normalized = string.strip().lower()
        
        # Replace comma with dot for decimal separator
        normalized = normalized.replace(',', '.')
        
        # Pattern to match number and optional unit with optional whitespace
        # Supports: "123", "123.45", "123 mb", "123.45mb", "123,45 gb", etc.
        pattern = r'^([0-9]*\.?[0-9]+)\s*([a-z]*)?$'
        match = re.match(pattern, normalized)
        
        if not match:
            raise ValueError(f"Invalid format: '{string}'. Expected format: 'number [unit]'")
        
        value_str = match.group(1)
        unit_str = match.group(2) or ''
        
        # Parse the numeric value
        try:
            value = float(value_str)
        except ValueError:
            raise ValueError(f"Invalid numeric value: '{value_str}'")
        
        # Get unit aliases mapping
        unit_aliases = StorageUnit.get_unit_aliases()
        
        # Find the unit, default to provided default_unit if not found
        unit = unit_aliases.get(unit_str, default_unit)
        
        return cls(value, unit)

    # Arithmetic operations
    def __add__(self, other: 'Storage') -> 'Storage':
        """
        Add two storage values.

        Args:
            other: The other Storage instance.

        Returns:
            Storage: A new Storage instance with the summed value in bytes.

        Examples:
            >>> s1 = Storage(1, StorageUnit.KIB)
            >>> s2 = Storage(512, StorageUnit.BYTES)
            >>> total = s1 + s2
            >>> print(total)
            1536.0 BYTES
        """
        if not isinstance(other, Storage):
            return NotImplemented
        
        total_bytes = self.convert_to_bytes() + other.convert_to_bytes()
        return Storage.parse_from_bytes(total_bytes)

    def __sub__(self, other: 'Storage') -> 'Storage':
        """
        Subtract two storage values.

        Args:
            other: The other Storage instance.

        Returns:
            Storage: A new Storage instance with the difference in bytes.

        Raises:
            ValueError: If the result would be negative.

        Examples:
            >>> s1 = Storage(2, StorageUnit.KIB)
            >>> s2 = Storage(512, StorageUnit.BYTES)
            >>> diff = s1 - s2
            >>> print(diff)
            1536.0 BYTES
        """
        if not isinstance(other, Storage):
            return NotImplemented
        
        result_bytes = self.convert_to_bytes() - other.convert_to_bytes()
        if result_bytes < 0:
            raise ValueError("Storage subtraction result cannot be negative")
        
        return Storage.parse_from_bytes(result_bytes)

    def __mul__(self, factor: Union[int, float]) -> 'Storage':
        """
        Multiply storage by a numeric factor.

        Args:
            factor: The numeric factor to multiply by.

        Returns:
            Storage: A new Storage instance with the multiplied value.

        Examples:
            >>> storage = Storage(1, StorageUnit.KIB)
            >>> doubled = storage * 2
            >>> print(doubled)
            2.0 KIB
        """
        if not isinstance(factor, (int, float)):
            return NotImplemented
        
        if factor < 0:
            raise ValueError("Cannot multiply storage by negative factor")
        
        return Storage(self.value * factor, self.unit)

    def __rmul__(self, factor: Union[int, float]) -> 'Storage':
        """
        Right multiplication (factor * storage).

        Args:
            factor: The numeric factor to multiply by.

        Returns:
            Storage: A new Storage instance with the multiplied value.
        """
        return self.__mul__(factor)

    def __truediv__(self, divisor: Union[int, float, 'Storage']) -> Union['Storage', float]:
        """
        Divide storage by a number or another storage value.

        Args:
            divisor: The divisor (number or Storage instance).

        Returns:
            Storage: If divisor is a number, returns new Storage with divided value.
            float: If divisor is Storage, returns the ratio as a float.

        Raises:
            ZeroDivisionError: If divisor is zero.

        Examples:
            >>> storage = Storage(2, StorageUnit.KIB)
            >>> half = storage / 2
            >>> print(half)
            1.0 KIB
            
            >>> ratio = Storage(2, StorageUnit.KIB) / Storage(1, StorageUnit.KIB)
            >>> print(ratio)
            2.0
        """
        if isinstance(divisor, (int, float)):
            if divisor == 0:
                raise ZeroDivisionError("Cannot divide storage by zero")
            return Storage(self.value / divisor, self.unit)
        
        elif isinstance(divisor, Storage):
            divisor_bytes = divisor.convert_to_bytes()
            if divisor_bytes == 0:
                raise ZeroDivisionError("Cannot divide by zero storage")
            return self.convert_to_bytes() / divisor_bytes
        
        return NotImplemented

    def __floordiv__(self, divisor: Union[int, float]) -> 'Storage':
        """
        Floor division of storage by a number.

        Args:
            divisor: The numeric divisor.

        Returns:
            Storage: A new Storage instance with the floor divided value.

        Examples:
            >>> storage = Storage(5, StorageUnit.KIB)
            >>> result = storage // 2
            >>> print(result)
            2.0 KIB
        """
        if not isinstance(divisor, (int, float)):
            return NotImplemented
        
        if divisor == 0:
            raise ZeroDivisionError("Cannot divide storage by zero")
        
        return Storage(self.value // divisor, self.unit)

    def __mod__(self, divisor: Union[int, float]) -> 'Storage':
        """
        Modulo operation on storage.

        Args:
            divisor: The numeric divisor.

        Returns:
            Storage: A new Storage instance with the remainder.

        Examples:
            >>> storage = Storage(5, StorageUnit.KIB)
            >>> remainder = storage % 2
            >>> print(remainder)
            1.0 KIB
        """
        if not isinstance(divisor, (int, float)):
            return NotImplemented
        
        if divisor == 0:
            raise ZeroDivisionError("Cannot perform modulo with zero")
        
        return Storage(self.value % divisor, self.unit)

    # Comparison operations
    def __eq__(self, other: object) -> bool:
        """
        Check if two storage values are equal.

        Args:
            other: The other object to compare with.

        Returns:
            bool: True if both storage values are equal in bytes.

        Examples:
            >>> s1 = Storage(1, StorageUnit.KIB)
            >>> s2 = Storage(1024, StorageUnit.BYTES)
            >>> print(s1 == s2)
            True
        """
        if not isinstance(other, Storage):
            return False
        
        return abs(self.convert_to_bytes() - other.convert_to_bytes()) < 1e-10

    def __lt__(self, other: 'Storage') -> bool:
        """
        Check if this storage is less than another.

        Args:
            other: The other Storage instance.

        Returns:
            bool: True if this storage is less than the other.

        Examples:
            >>> s1 = Storage(512, StorageUnit.BYTES)
            >>> s2 = Storage(1, StorageUnit.KIB)
            >>> print(s1 < s2)
            True
        """
        if not isinstance(other, Storage):
            return NotImplemented
        
        return self.convert_to_bytes() < other.convert_to_bytes()

    def __le__(self, other: 'Storage') -> bool:
        """
        Check if this storage is less than or equal to another.

        Args:
            other: The other Storage instance.

        Returns:
            bool: True if this storage is less than or equal to the other.
        """
        if not isinstance(other, Storage):
            return NotImplemented
        
        return self.convert_to_bytes() <= other.convert_to_bytes()

    def __gt__(self, other: 'Storage') -> bool:
        """
        Check if this storage is greater than another.

        Args:
            other: The other Storage instance.

        Returns:
            bool: True if this storage is greater than the other.

        Examples:
            >>> s1 = Storage(2, StorageUnit.KIB)
            >>> s2 = Storage(1024, StorageUnit.BYTES)
            >>> print(s1 > s2)
            True
        """
        if not isinstance(other, Storage):
            return NotImplemented
        
        return self.convert_to_bytes() > other.convert_to_bytes()

    def __ge__(self, other: 'Storage') -> bool:
        """
        Check if this storage is greater than or equal to another.

        Args:
            other: The other Storage instance.

        Returns:
            bool: True if this storage is greater than or equal to the other.
        """
        if not isinstance(other, Storage):
            return NotImplemented
        
        return self.convert_to_bytes() >= other.convert_to_bytes()

    def __hash__(self) -> int:
        """
        Return hash of the storage for use in sets and dictionaries.

        Returns:
            int: Hash value based on the byte representation.
        """
        return hash(self.convert_to_bytes())

    # String representations
    def __str__(self) -> str:
        """
        Return a human-readable string representation.

        Returns:
            str: A string representation of the storage.

        Examples:
            >>> storage = Storage(1.5, StorageUnit.MB)
            >>> print(str(storage))
            1.5 MB
        """
        # Format the value to remove unnecessary decimal places
        if self.value == int(self.value):
            value_str = str(int(self.value))
        else:
            value_str = f"{self.value:.10g}"  # Remove trailing zeros
        
        return f"{value_str} {self.unit.name}"

    def __repr__(self) -> str:
        """
        Return a detailed string representation for debugging.

        Returns:
            str: A detailed string representation.

        Examples:
            >>> storage = Storage(1, StorageUnit.KIB)
            >>> print(repr(storage))
            Storage(1.0, StorageUnit.KIB)
        """
        return f"Storage({self.value}, {self.unit!r})"

    def __format__(self, format_spec: str) -> str:
        """
        Format the storage value according to the format specification.

        Args:
            format_spec: The format specification string.

        Returns:
            str: The formatted storage string.

        Examples:
            >>> storage = Storage(1234.5, StorageUnit.BYTES)
            >>> print(f"{storage:.2f}")
            1234.50 BYTES
        """
        if format_spec:
            formatted_value = format(self.value, format_spec)
        else:
            formatted_value = str(self.value)
        
        return f"{formatted_value} {self.unit.name}"

    # File system operations
    @staticmethod
    def get_size_from_path(path: Union[str, Path]) -> 'Storage':
        """
        Get the size of a file or directory from the given path.

        This method calculates the total size of a file or directory
        (including all subdirectories and files) using pathlib.

        Args:
            path: The path to the file or directory (string or Path object).

        Returns:
            Storage: A Storage instance representing the total size in bytes.

        Raises:
            FileNotFoundError: If the path does not exist.
            PermissionError: If access to the path is denied.
            OSError: If an OS-level error occurs while accessing the path.

        Examples:
            >>> size = Storage.get_size_from_path("/path/to/file.txt")
            >>> print(size)
            1024.0 BYTES
            
            >>> dir_size = Storage.get_size_from_path("/path/to/directory")
            >>> print(dir_size.auto_scale())
            15.2 MIB
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise FileNotFoundError(f"Path does not exist: {path}")
        
        try:
            if path_obj.is_file():
                # For files, get the file size directly
                size = path_obj.stat().st_size
            elif path_obj.is_dir():
                # For directories, sum all file sizes recursively
                size = 0
                for file_path in path_obj.rglob('*'):
                    if file_path.is_file():
                        try:
                            size += file_path.stat().st_size
                        except (PermissionError, FileNotFoundError, OSError):
                            # Skip files that can't be accessed
                            continue
            else:
                # Handle special files (symlinks, devices, etc.)
                size = path_obj.stat().st_size
        
        except PermissionError:
            raise PermissionError(f"Permission denied accessing: {path}")
        except OSError as e:
            raise OSError(f"Error accessing path {path}: {e}")
        
        return Storage.parse_from_bytes(size)

    @staticmethod
    def get_platform_storage():
        """
        Get the appropriate platform-specific storage instance.

        This method automatically detects the current platform and returns
        the corresponding storage handler that may include platform-specific
        optimizations for file size retrieval.

        Returns:
            Storage subclass: A platform-specific storage instance.

        Raises:
            ValueError: If the platform is not supported.

        Examples:
            >>> platform_storage = Storage.get_platform_storage()
            >>> size = platform_storage.get_size_from_path("/some/path")
        """
        # Import here to avoid circular imports
        from .platform_storage import WindowsStorage, LinuxStorage, MacStorage
        
        system = platform.system()
        if system == 'Windows':
            return WindowsStorage()
        elif system == 'Linux':
            return LinuxStorage()
        elif system == 'Darwin':  # macOS
            return MacStorage()
        else:
            raise ValueError(f"Unsupported platform: {system}")

    # Additional utility methods
    def auto_scale(self, prefer_binary: bool = True) -> 'Storage':
        """
        Automatically scale the storage to the most appropriate unit.

        This method converts the storage to a unit that results in a value
        between 1 and 1024 (for binary) or 1000 (for decimal), making it
        more human-readable.

        Args:
            prefer_binary: If True, prefer binary units (KiB, MiB, etc.).
                          If False, prefer decimal units (KB, MB, etc.).

        Returns:
            Storage: A new Storage instance with an appropriate unit.

        Examples:
            >>> storage = Storage(1536, StorageUnit.BYTES)
            >>> scaled = storage.auto_scale()
            >>> print(scaled)
            1.5 KIB
        """
        bytes_value = self.convert_to_bytes()
        
        if bytes_value == 0:
            return Storage(0, StorageUnit.BYTES)
        
        # Choose unit set based on preference
        if prefer_binary:
            units = [
                StorageUnit.BYTES, StorageUnit.KIB, StorageUnit.MIB, StorageUnit.GIB,
                StorageUnit.TIB, StorageUnit.PIB, StorageUnit.EIB, StorageUnit.ZIB, StorageUnit.YIB
            ]
            threshold = 1024
        else:
            units = [
                StorageUnit.BYTES, StorageUnit.KB, StorageUnit.MB, StorageUnit.GB,
                StorageUnit.TB, StorageUnit.PB, StorageUnit.EB, StorageUnit.ZB, StorageUnit.YB
            ]
            threshold = 1000
        
        # Find the most appropriate unit
        for i, unit in enumerate(units[:-1]):
            if bytes_value < units[i + 1].value:
                break
        else:
            unit = units[-1]  # Use the largest unit if value is very large
        
        # Convert to the chosen unit
        return self.convert_to(unit)