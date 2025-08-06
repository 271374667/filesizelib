"""
Core storage class implementation.

This module contains the main Storage class that provides storage unit
conversion, arithmetic operations, and parsing functionality.
"""

import math
import re
import platform
import threading
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Union, Optional
from .storage_unit import StorageUnit

# Set high precision for decimal operations
getcontext().prec = 50

# Cache commonly used Decimal constants for performance
_DECIMAL_ONE = Decimal('1')
_DECIMAL_POINT_ONE = Decimal('0.1')


class Storage:
    """
    A class representing storage with different units.

    This class provides methods for converting between different storage units,
    performing arithmetic operations, and comparing storage sizes.
    It also includes methods for getting the size of files or directories
    and parsing storage values from strings.

    Attributes:
        value (float): The numerical value of the storage as float (backward compatibility).
        decimal_value (Decimal): The exact decimal value with full precision.
        unit (StorageUnit): The unit of the storage value.

    Class Attributes:
        _decimal_precision (int): Maximum number of decimal places to display (default: 20).

    Decimal Precision:
        The Storage class uses Python's Decimal module internally to provide exact
        decimal precision, eliminating floating-point rounding errors. This ensures
        that values like "6.682" are stored and displayed exactly as "6.682" rather
        than "6.68200000000000038369".
        
        - value property: Returns float for backward compatibility
        - decimal_value property: Returns exact Decimal for precision-critical applications
        - String representations use exact decimal formatting

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
        
        >>> # Exact decimal precision examples
        >>> precise = Storage("6.682", StorageUnit.MB)
        >>> print(precise)  # Exact output: 6.682 MB
        6.682 MB
        >>> precise.decimal_value  # Exact decimal
        Decimal('6.682')
        >>> precise.value  # Float for compatibility
        6.682
        
        >>> # Decimal arithmetic maintains precision
        >>> a = Storage("1.1", StorageUnit.GB)
        >>> b = Storage("2.2", StorageUnit.GB)
        >>> result = a + b
        >>> print(result)  # Exact: 3.3 GB
        3.3 GB
        >>> result.decimal_value
        Decimal('3.3')
        
        >>> # Configure decimal precision for display
        >>> Storage.set_decimal_precision(10)
        >>> small = Storage("0.000123456789012345", StorageUnit.GB)
        >>> print(small)  # Will show up to 10 decimal places
        0.0001234567890 GB
    """
    
    # Class variables for configuration
    _decimal_precision: int = 20
    _comparison_tolerance: Decimal = Decimal('1e-10')  # Tolerance for equality comparisons
    _lock = threading.RLock()  # Thread safety for class variable modifications
    
    @classmethod
    def _ensure_decimal_context(cls) -> None:
        """Ensure decimal context is properly configured."""
        if getcontext().prec < 50:
            getcontext().prec = 50

    def __init__(self, value: Union[int, float, str, Decimal], unit: StorageUnit = StorageUnit.AUTO) -> None:
        """
        Initialize the storage with a value and a unit.

        Args:
            value: The numerical value of the storage, or a string to parse (e.g., "1MB").
                  Can be int, float, str, or Decimal for exact precision.
            unit: The unit of the storage value. Defaults to StorageUnit.AUTO for automatic parsing.

        Raises:
            TypeError: If value is not a number or string, or unit is not a StorageUnit.
            ValueError: If value is negative or parsing fails.

        Examples:
            >>> storage = Storage(1024, StorageUnit.BYTES)
            >>> print(storage)
            1024 BYTES
            
            >>> storage = Storage("1.5 MB")  # Automatic parsing
            >>> print(storage)
            1.5 MB
            
            >>> storage = Storage("2048")  # Defaults to bytes when no unit specified
            >>> print(storage)
            2048 BYTES
            
            >>> # Using Decimal for exact precision
            >>> from decimal import Decimal
            >>> storage = Storage(Decimal("6.682"), StorageUnit.MB)
            >>> print(storage)
            6.682 MB
            >>> storage.decimal_value
            Decimal('6.682')
        """
        # Ensure decimal context is configured
        self._ensure_decimal_context()
        
        # Handle string input with automatic parsing
        if isinstance(value, str):
            if unit != StorageUnit.AUTO:
                # If unit is explicitly provided with string input, ignore AUTO and use parse
                parsed = self.parse(value, unit if unit != StorageUnit.AUTO else None)
            else:
                # Use automatic parsing
                parsed = self.parse(value)
            self._decimal_value = parsed._decimal_value
            self.unit = parsed.unit
            return
        
        # Handle numeric input
        if not isinstance(value, (int, float, Decimal)):
            raise TypeError(f"Value must be a number or string, got {type(value).__name__}")
        
        if unit == StorageUnit.AUTO:
            # If AUTO is specified with numeric input, default to bytes
            unit = StorageUnit.BYTES
        
        if not isinstance(unit, StorageUnit):
            raise TypeError(f"Unit must be a StorageUnit, got {type(unit).__name__}")
        
        if value < 0:
            raise ValueError(f"Storage value cannot be negative: {value}")
        
        # Convert to Decimal for exact precision
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError(f"Storage value must be finite, got: {value}")
            # Convert float to string first to avoid precision loss
            self._decimal_value = Decimal(str(value))
        elif isinstance(value, (int, Decimal)):
            self._decimal_value = Decimal(value)
        else:
            # This shouldn't happen due to the type check above
            self._decimal_value = Decimal(str(value))
        
        self.unit = unit

    @property
    def value(self) -> float:
        """
        Get the storage value as a float for backward compatibility.
        
        This property maintains backward compatibility with existing code that expects
        float values. For applications requiring exact decimal precision, use the
        decimal_value property instead.
        
        Returns:
            float: The storage value converted to float.
            
        Note:
            Converting to float may introduce small precision errors for values that
            cannot be exactly represented in IEEE 754 floating-point format.
            Use decimal_value for exact precision.
            
        Examples:
            >>> storage = Storage("6.682", StorageUnit.MB)
            >>> storage.value  # Returns float (may have tiny precision loss)
            6.682
            >>> storage.decimal_value  # Returns exact Decimal
            Decimal('6.682')
        """
        return float(self._decimal_value)
    
    @property 
    def decimal_value(self) -> Decimal:
        """
        Get the exact decimal value with full precision.
        
        This property provides access to the internal Decimal representation that
        maintains exact precision for all decimal operations. Use this when you
        need guaranteed precision without any floating-point rounding errors.
        
        Returns:
            Decimal: The exact decimal value without precision loss.
        
        Raises:
            AttributeError: If the internal decimal value is not initialized.
            
        Examples:
            >>> storage = Storage("6.682", StorageUnit.MB)
            >>> storage.decimal_value
            Decimal('6.682')
            >>> 
            >>> # Decimal arithmetic maintains exact precision
            >>> a = Storage("1.1", StorageUnit.GB)
            >>> b = Storage("2.2", StorageUnit.GB)
            >>> (a + b).decimal_value
            Decimal('3.3')
            >>>
            >>> # Compare with float precision
            >>> (a + b).value  # May show: 3.3000000000000003
            3.3
            
        Note:
            This is the recommended property for financial calculations,
            scientific applications, or any context where exact decimal
            precision is required.
        """
        if not hasattr(self, '_decimal_value'):
            raise AttributeError("Internal decimal value not initialized")
        return self._decimal_value

    @classmethod
    def set_decimal_precision(cls, precision: int) -> None:
        """
        Set the maximum number of decimal places to display in string representations.
        
        This affects how numbers are formatted when converting Storage objects to strings,
        preventing scientific notation and allowing for precise decimal display.
        
        Args:
            precision: Maximum number of decimal places to display. Must be >= 0.
        
        Raises:
            TypeError: If precision is not an integer.
            ValueError: If precision is negative.
        
        Examples:
            >>> Storage.set_decimal_precision(5)
            >>> small = Storage(0.000123456789, StorageUnit.GB)  
            >>> print(small)  # Will show: 0.00012 GB
            
            >>> Storage.set_decimal_precision(15)
            >>> print(small)  # Will show: 0.000123456789000 GB
        """
        if not isinstance(precision, int):
            raise TypeError(f"Precision must be an integer, got {type(precision).__name__}")
        
        if precision < 0:
            raise ValueError("Precision cannot be negative")
        
        with cls._lock:
            cls._decimal_precision = precision
    
    @classmethod
    def get_decimal_precision(cls) -> int:
        """
        Get the current maximum number of decimal places used in string representations.
        
        Returns:
            int: Current decimal precision setting.
            
        Examples:
            >>> Storage.set_decimal_precision(10)
            >>> print(Storage.get_decimal_precision())
            10
        """
        return cls._decimal_precision
    
    def _format_value(self, value: Decimal) -> str:
        """
        Format a Decimal value avoiding scientific notation and respecting decimal precision.
        
        Args:
            value: The Decimal value to format.
            
        Returns:
            str: The formatted value as a string.
        """
        # Handle special case of zero precision
        if self._decimal_precision == 0:
            # Round to nearest integer
            return str(int(value.quantize(_DECIMAL_ONE)))
        
        # Handle integer values
        if value % 1 == 0:
            return str(int(value))
        
        # Force normal notation (no scientific notation)
        # Create a context that doesn't use scientific notation
        formatted = format(value, 'f')
        
        # If the result is too long, apply precision limit
        if '.' in formatted:
            integer_part, decimal_part = formatted.split('.')
            if len(decimal_part) > self._decimal_precision:
                # Use quantize to limit decimal places
                quantizer = _DECIMAL_POINT_ONE ** self._decimal_precision
                value = value.quantize(quantizer)
                formatted = format(value, 'f')
            
            # Remove trailing zeros
            formatted = formatted.rstrip('0').rstrip('.')
        
        return formatted

    @classmethod
    def parse_from_bytes(cls, value: Union[int, float, Decimal]) -> 'Storage':
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
            1024 BYTES
        """
        return cls(value, StorageUnit.BYTES)

    def convert_to_bytes(self) -> Decimal:
        """
        Convert the storage value to bytes with exact decimal precision.

        This method returns a Decimal object to maintain exact precision during
        conversion operations. For backward compatibility with code expecting
        float values, you can convert the result using float().

        Returns:
            Decimal: The value in bytes with exact precision.

        Examples:
            >>> storage = Storage(1, StorageUnit.KIB)
            >>> storage.convert_to_bytes()
            Decimal('1024')
            >>> 
            >>> # For float compatibility
            >>> float(storage.convert_to_bytes())
            1024.0
            >>>
            >>> # Exact decimal precision maintained
            >>> precise = Storage("1.5", StorageUnit.KB)
            >>> precise.convert_to_bytes()
            Decimal('1500')
        """
        return self._decimal_value * Decimal(str(self.unit.value))

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
        new_value = bytes_value / Decimal(str(target_unit.value))
        return Storage(new_value, target_unit)

    # Convenient conversion methods for binary units
    def convert_to_kib(self) -> 'Storage':
        """
        Convert to kibibytes (KiB) - binary unit (1024 bytes).
        
        Returns:
            Storage: New Storage object with value in KiB.
            
        Example:
            >>> storage = Storage(2048, StorageUnit.BYTES)
            >>> kib_storage = storage.convert_to_kib()
            >>> print(kib_storage)
            2.0 KIB
        """
        return self.convert_to(StorageUnit.KIB)
    
    def convert_to_mib(self) -> 'Storage':
        """
        Convert to mebibytes (MiB) - binary unit (1024^2 bytes).
        
        Returns:
            Storage: New Storage object with value in MiB.
            
        Example:
            >>> storage = Storage(1, StorageUnit.GIB)
            >>> mib_storage = storage.convert_to_mib()
            >>> print(mib_storage)
            1024.0 MIB
        """
        return self.convert_to(StorageUnit.MIB)
    
    def convert_to_gib(self) -> 'Storage':
        """
        Convert to gibibytes (GiB) - binary unit (1024^3 bytes).
        
        Returns:
            Storage: New Storage object with value in GiB.
            
        Example:
            >>> storage = Storage(2048, StorageUnit.MIB)
            >>> gib_storage = storage.convert_to_gib()
            >>> print(gib_storage)
            2.0 GIB
        """
        return self.convert_to(StorageUnit.GIB)
    
    def convert_to_tib(self) -> 'Storage':
        """
        Convert to tebibytes (TiB) - binary unit (1024^4 bytes).
        
        Returns:
            Storage: New Storage object with value in TiB.
            
        Example:
            >>> storage = Storage(1024, StorageUnit.GIB)
            >>> tib_storage = storage.convert_to_tib()
            >>> print(tib_storage)
            1.0 TIB
        """
        return self.convert_to(StorageUnit.TIB)
    
    def convert_to_pib(self) -> 'Storage':
        """
        Convert to pebibytes (PiB) - binary unit (1024^5 bytes).
        
        Returns:
            Storage: New Storage object with value in PiB.
            
        Example:
            >>> storage = Storage(1024, StorageUnit.TIB)
            >>> pib_storage = storage.convert_to_pib()
            >>> print(pib_storage)
            1.0 PIB
        """
        return self.convert_to(StorageUnit.PIB)
    
    def convert_to_eib(self) -> 'Storage':
        """
        Convert to exbibytes (EiB) - binary unit (1024^6 bytes).
        
        Returns:
            Storage: New Storage object with value in EiB.
            
        Example:
            >>> storage = Storage(1024, StorageUnit.PIB)
            >>> eib_storage = storage.convert_to_eib()
            >>> print(eib_storage)
            1.0 EIB
        """
        return self.convert_to(StorageUnit.EIB)
    
    def convert_to_zib(self) -> 'Storage':
        """
        Convert to zebibytes (ZiB) - binary unit (1024^7 bytes).
        
        Returns:
            Storage: New Storage object with value in ZiB.
            
        Example:
            >>> storage = Storage(1024, StorageUnit.EIB)
            >>> zib_storage = storage.convert_to_zib()
            >>> print(zib_storage)
            1.0 ZIB
        """
        return self.convert_to(StorageUnit.ZIB)
    
    def convert_to_yib(self) -> 'Storage':
        """
        Convert to yobibytes (YiB) - binary unit (1024^8 bytes).
        
        Returns:
            Storage: New Storage object with value in YiB.
            
        Example:
            >>> storage = Storage(1024, StorageUnit.ZIB)
            >>> yib_storage = storage.convert_to_yib()
            >>> print(yib_storage)
            1.0 YIB
        """
        return self.convert_to(StorageUnit.YIB)

    # Convenient conversion methods for decimal units
    def convert_to_kb(self) -> 'Storage':
        """
        Convert to kilobytes (KB) - decimal unit (1000 bytes).
        
        Returns:
            Storage: New Storage object with value in KB.
            
        Example:
            >>> storage = Storage(2000, StorageUnit.BYTES)
            >>> kb_storage = storage.convert_to_kb()
            >>> print(kb_storage)
            2.0 KB
        """
        return self.convert_to(StorageUnit.KB)
    
    def convert_to_mb(self) -> 'Storage':
        """
        Convert to megabytes (MB) - decimal unit (1000^2 bytes).
        
        Returns:
            Storage: New Storage object with value in MB.
            
        Example:
            >>> storage = Storage(1, StorageUnit.GB)
            >>> mb_storage = storage.convert_to_mb()
            >>> print(mb_storage)
            1000.0 MB
        """
        return self.convert_to(StorageUnit.MB)
    
    def convert_to_gb(self) -> 'Storage':
        """
        Convert to gigabytes (GB) - decimal unit (1000^3 bytes).
        
        Returns:
            Storage: New Storage object with value in GB.
            
        Example:
            >>> storage = Storage(2000, StorageUnit.MB)
            >>> gb_storage = storage.convert_to_gb()
            >>> print(gb_storage)
            2.0 GB
        """
        return self.convert_to(StorageUnit.GB)
    
    def convert_to_tb(self) -> 'Storage':
        """
        Convert to terabytes (TB) - decimal unit (1000^4 bytes).
        
        Returns:
            Storage: New Storage object with value in TB.
            
        Example:
            >>> storage = Storage(1000, StorageUnit.GB)
            >>> tb_storage = storage.convert_to_tb()
            >>> print(tb_storage)
            1.0 TB
        """
        return self.convert_to(StorageUnit.TB)
    
    def convert_to_pb(self) -> 'Storage':
        """
        Convert to petabytes (PB) - decimal unit (1000^5 bytes).
        
        Returns:
            Storage: New Storage object with value in PB.
            
        Example:
            >>> storage = Storage(1000, StorageUnit.TB)
            >>> pb_storage = storage.convert_to_pb()
            >>> print(pb_storage)
            1.0 PB
        """
        return self.convert_to(StorageUnit.PB)
    
    def convert_to_eb(self) -> 'Storage':
        """
        Convert to exabytes (EB) - decimal unit (1000^6 bytes).
        
        Returns:
            Storage: New Storage object with value in EB.
            
        Example:
            >>> storage = Storage(1000, StorageUnit.PB)
            >>> eb_storage = storage.convert_to_eb()
            >>> print(eb_storage)
            1.0 EB
        """
        return self.convert_to(StorageUnit.EB)
    
    def convert_to_zb(self) -> 'Storage':
        """
        Convert to zettabytes (ZB) - decimal unit (1000^7 bytes).
        
        Returns:
            Storage: New Storage object with value in ZB.
            
        Example:
            >>> storage = Storage(1000, StorageUnit.EB)
            >>> zb_storage = storage.convert_to_zb()
            >>> print(zb_storage)
            1.0 ZB
        """
        return self.convert_to(StorageUnit.ZB)
    
    def convert_to_yb(self) -> 'Storage':
        """
        Convert to yottabytes (YB) - decimal unit (1000^8 bytes).
        
        Returns:
            Storage: New Storage object with value in YB.
            
        Example:
            >>> storage = Storage(1000, StorageUnit.ZB)
            >>> yb_storage = storage.convert_to_yb()
            >>> print(yb_storage)
            1.0 YB
        """
        return self.convert_to(StorageUnit.YB)

    # Convenient conversion methods for bit units
    def convert_to_bits(self) -> 'Storage':
        """
        Convert to bits - smallest unit (1/8 byte).
        
        Returns:
            Storage: New Storage object with value in bits.
            
        Example:
            >>> storage = Storage(1, StorageUnit.BYTES)
            >>> bits_storage = storage.convert_to_bits()
            >>> print(bits_storage)
            8.0 BITS
        """
        return self.convert_to(StorageUnit.BITS)
    
    def convert_to_kilobits(self) -> 'Storage':
        """
        Convert to kilobits - decimal bit unit (1000 bits).
        
        Returns:
            Storage: New Storage object with value in kilobits.
            
        Example:
            >>> storage = Storage(1, StorageUnit.KB)
            >>> kbits_storage = storage.convert_to_kilobits()
            >>> print(kbits_storage)
            8.0 KILOBITS
        """
        return self.convert_to(StorageUnit.KILOBITS)
    
    def convert_to_megabits(self) -> 'Storage':
        """
        Convert to megabits - decimal bit unit (1000^2 bits).
        
        Returns:
            Storage: New Storage object with value in megabits.
            
        Example:
            >>> storage = Storage(1, StorageUnit.MB)
            >>> mbits_storage = storage.convert_to_megabits()
            >>> print(mbits_storage)
            8.0 MEGABITS
        """
        return self.convert_to(StorageUnit.MEGABITS)
    
    def convert_to_gigabits(self) -> 'Storage':
        """
        Convert to gigabits - decimal bit unit (1000^3 bits).
        
        Returns:
            Storage: New Storage object with value in gigabits.
            
        Example:
            >>> storage = Storage(1, StorageUnit.GB)
            >>> gbits_storage = storage.convert_to_gigabits()
            >>> print(gbits_storage)
            8.0 GIGABITS
        """
        return self.convert_to(StorageUnit.GIGABITS)
    
    def convert_to_terabits(self) -> 'Storage':
        """
        Convert to terabits - decimal bit unit (1000^4 bits).
        
        Returns:
            Storage: New Storage object with value in terabits.
            
        Example:
            >>> storage = Storage(1, StorageUnit.TB)
            >>> tbits_storage = storage.convert_to_terabits()
            >>> print(tbits_storage)
            8.0 TERABITS
        """
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
        
        # Parse the numeric value using Decimal for exact precision
        try:
            value = Decimal(value_str)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numeric value: '{value_str}'") from e
        
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
            Storage: A new Storage instance with the summed value. If both operands
            have the same unit, the result preserves that unit. Otherwise, the result
            is in bytes.

        Examples:
            >>> s1 = Storage(1, StorageUnit.KIB)
            >>> s2 = Storage(512, StorageUnit.BYTES)
            >>> total = s1 + s2
            >>> print(total)
            1536.0 BYTES
            
            >>> s3 = Storage(1, StorageUnit.GB)
            >>> s4 = Storage(2, StorageUnit.GB)
            >>> same_unit_total = s3 + s4
            >>> print(same_unit_total)
            3 GB
        """
        if not isinstance(other, Storage):
            return NotImplemented
        
        # If both operands have the same unit, preserve that unit
        if self.unit == other.unit:
            total_value = self._decimal_value + other._decimal_value
            return Storage(total_value, self.unit)
        
        # Different units: convert to bytes
        total_bytes = self.convert_to_bytes() + other.convert_to_bytes()
        return Storage.parse_from_bytes(total_bytes)

    def __sub__(self, other: 'Storage') -> 'Storage':
        """
        Subtract two storage values.

        Args:
            other: The other Storage instance.

        Returns:
            Storage: A new Storage instance with the difference. If both operands
            have the same unit, the result preserves that unit. Otherwise, the result
            is in bytes.

        Raises:
            ValueError: If the result would be negative.

        Examples:
            >>> s1 = Storage(2, StorageUnit.KIB)
            >>> s2 = Storage(512, StorageUnit.BYTES)
            >>> diff = s1 - s2
            >>> print(diff)
            1536.0 BYTES
            
            >>> s3 = Storage(5, StorageUnit.GB)
            >>> s4 = Storage(2, StorageUnit.GB)
            >>> same_unit_diff = s3 - s4
            >>> print(same_unit_diff)
            3 GB
        """
        if not isinstance(other, Storage):
            return NotImplemented
        
        # If both operands have the same unit, preserve that unit
        if self.unit == other.unit:
            result_value = self._decimal_value - other._decimal_value
            if result_value < 0:
                raise ValueError("Storage subtraction result cannot be negative")
            return Storage(result_value, self.unit)
        
        # Different units: convert to bytes
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
        
        return Storage(self._decimal_value * Decimal(str(factor)), self.unit)

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
            return Storage(self._decimal_value / Decimal(str(divisor)), self.unit)
        
        elif isinstance(divisor, Storage):
            divisor_bytes = divisor.convert_to_bytes()
            if divisor_bytes == 0:
                raise ZeroDivisionError("Cannot divide by zero storage")
            return float(self.convert_to_bytes() / divisor_bytes)
        
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
        
        return Storage(self._decimal_value // Decimal(str(divisor)), self.unit)

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
        
        return Storage(self._decimal_value % Decimal(str(divisor)), self.unit)

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
        
        return abs(self.convert_to_bytes() - other.convert_to_bytes()) < self._comparison_tolerance

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
        return hash(float(self.convert_to_bytes()))

    def __int__(self) -> int:
        """
        Convert storage to integer representation in bytes.

        Returns:
            int: The storage value converted to integer bytes.

        Examples:
            >>> storage = Storage(1.5, StorageUnit.KIB)
            >>> print(int(storage))
            1536
        """
        return int(self.convert_to_bytes())

    def __float__(self) -> float:
        """
        Convert storage to float representation in bytes.

        Returns:
            float: The storage value as float bytes.

        Examples:
            >>> storage = Storage(1.5, StorageUnit.KIB)
            >>> print(float(storage))
            1536.0
        """
        return float(self.convert_to_bytes())

    # Conversion properties for quick access
    @property
    def BYTES(self) -> 'Storage':
        """Property to convert to bytes."""
        return self.convert_to(StorageUnit.BYTES)
    
    @property
    def KIB(self) -> 'Storage':
        """Property to convert to kibibytes (KiB)."""
        return self.convert_to_kib()
    
    @property
    def MIB(self) -> 'Storage':
        """Property to convert to mebibytes (MiB)."""
        return self.convert_to_mib()
    
    @property
    def GIB(self) -> 'Storage':
        """Property to convert to gibibytes (GiB)."""
        return self.convert_to_gib()
    
    @property
    def TIB(self) -> 'Storage':
        """Property to convert to tebibytes (TiB)."""
        return self.convert_to_tib()
    
    @property
    def PIB(self) -> 'Storage':
        """Property to convert to pebibytes (PiB)."""
        return self.convert_to_pib()
    
    @property
    def EIB(self) -> 'Storage':
        """Property to convert to exbibytes (EiB)."""
        return self.convert_to_eib()
    
    @property
    def ZIB(self) -> 'Storage':
        """Property to convert to zebibytes (ZiB)."""
        return self.convert_to_zib()
    
    @property
    def YIB(self) -> 'Storage':
        """Property to convert to yobibytes (YiB)."""
        return self.convert_to_yib()
    
    @property
    def KB(self) -> 'Storage':
        """Property to convert to kilobytes (KB)."""
        return self.convert_to_kb()
    
    @property
    def MB(self) -> 'Storage':
        """Property to convert to megabytes (MB)."""
        return self.convert_to_mb()
    
    @property
    def GB(self) -> 'Storage':
        """Property to convert to gigabytes (GB)."""
        return self.convert_to_gb()
    
    @property
    def TB(self) -> 'Storage':
        """Property to convert to terabytes (TB)."""
        return self.convert_to_tb()
    
    @property
    def PB(self) -> 'Storage':
        """Property to convert to petabytes (PB)."""
        return self.convert_to_pb()
    
    @property
    def EB(self) -> 'Storage':
        """Property to convert to exabytes (EB)."""
        return self.convert_to_eb()
    
    @property
    def ZB(self) -> 'Storage':
        """Property to convert to zettabytes (ZB)."""
        return self.convert_to_zb()
    
    @property
    def YB(self) -> 'Storage':
        """Property to convert to yottabytes (YB)."""
        return self.convert_to_yb()
    
    @property
    def BITS(self) -> 'Storage':
        """Property to convert to bits."""
        return self.convert_to_bits()
    
    @property
    def KILOBITS(self) -> 'Storage':
        """Property to convert to kilobits."""
        return self.convert_to_kilobits()
    
    @property
    def MEGABITS(self) -> 'Storage':
        """Property to convert to megabits."""
        return self.convert_to_megabits()
    
    @property
    def GIGABITS(self) -> 'Storage':
        """Property to convert to gigabits."""
        return self.convert_to_gigabits()
    
    @property
    def TERABITS(self) -> 'Storage':
        """Property to convert to terabits."""
        return self.convert_to_terabits()

    # String representations
    def __str__(self) -> str:
        """
        Return a human-readable string representation.
        
        Uses the configured decimal precision to avoid scientific notation
        and provide consistent decimal formatting.

        Returns:
            str: A string representation of the storage.

        Examples:
            >>> storage = Storage(1.5, StorageUnit.MB)
            >>> print(str(storage))
            1.5 MB
            
            >>> small = Storage(9.872019291e-05, StorageUnit.GIB)
            >>> print(str(small))  # No scientific notation
            0.00009872019291 GIB
        """
        value_str = self._format_value(self._decimal_value)
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
        return f"Storage({float(self._decimal_value)}, {self.unit!r})"

    def __format__(self, format_spec: str) -> str:
        """
        Format the storage value according to the format specification.
        
        If no format specification is provided, uses the configured decimal
        precision to avoid scientific notation.

        Args:
            format_spec: The format specification string.

        Returns:
            str: The formatted storage string.

        Examples:
            >>> storage = Storage(1234.5, StorageUnit.BYTES)
            >>> print(f"{storage:.2f}")
            1234.50 BYTES
            
            >>> small = Storage(0.000123456789, StorageUnit.GB)
            >>> print(f"{small}")  # Uses configured precision
            0.000123456789 GB
        """
        if format_spec:
            # Use the provided format specification
            formatted_value = format(float(self._decimal_value), format_spec)
        else:
            # Use our custom formatting to avoid scientific notation
            formatted_value = self._format_value(self._decimal_value)
        
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
    def get_platform_storage() -> 'Storage':
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
        else:
            units = [
                StorageUnit.BYTES, StorageUnit.KB, StorageUnit.MB, StorageUnit.GB,
                StorageUnit.TB, StorageUnit.PB, StorageUnit.EB, StorageUnit.ZB, StorageUnit.YB
            ]
        
        # Find the most appropriate unit
        for i, unit in enumerate(units[:-1]):
            if bytes_value < units[i + 1].value:
                break
        else:
            unit = units[-1]  # Use the largest unit if value is very large
        
        # Convert to the chosen unit
        return self.convert_to(unit)