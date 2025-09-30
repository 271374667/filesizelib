"""
Core storage value management module.

This module provides the StorageValue class which handles the fundamental
storage value representation and precision management.
"""

import math
import re
import threading
from decimal import Decimal, getcontext
from typing import Union, Dict, Optional
from .storage_unit import StorageUnit

# Set high precision for decimal operations
getcontext().prec = 50

# Cache commonly used Decimal constants for performance
_DECIMAL_ONE = Decimal('1')
_DECIMAL_POINT_ONE = Decimal('0.1')


class StorageValue:
    """
    Core storage value management with exact decimal precision.

    This class handles the fundamental representation and management of storage values,
    providing exact decimal precision and validation. It serves as the foundation
    for all storage operations.

    Attributes:
        decimal_value (Decimal): The exact decimal value with full precision.
        unit (StorageUnit): The unit of the storage value.

    Examples:
        >>> value = StorageValue(Decimal("1.5"), StorageUnit.MB)
        >>> print(value.decimal_value)
        Decimal('1.5')
        >>> print(value.unit)
        StorageUnit.MB

        >>> # Convert to bytes for calculations
        >>> bytes_value = value.to_bytes()
        >>> print(bytes_value)
        Decimal('1500000')
    """

    def __init__(self, value: Union[int, float, str, Decimal], unit: StorageUnit) -> None:
        """
        Initialize the storage value with exact precision.

        Args:
            value: The numerical value (int, float, str, or Decimal).
            unit: The storage unit.

        Raises:
            TypeError: If value is not a valid type.
            ValueError: If value is negative.

        Examples:
            >>> v1 = StorageValue(1024, StorageUnit.BYTES)
            >>> v2 = StorageValue("1.5", StorageUnit.MB)
            >>> v3 = StorageValue(Decimal("6.682"), StorageUnit.GB)
        """
        if not isinstance(unit, StorageUnit):
            raise TypeError(f"Unit must be a StorageUnit, got {type(unit).__name__}")

        if value < 0:
            raise ValueError(f"Storage value cannot be negative: {value}")

        # Convert to Decimal for exact precision
        if isinstance(value, float):
            if not math.isfinite(value):
                raise ValueError(f"Storage value must be finite, got: {value}")
            # Convert float to string first to avoid precision loss
            self.decimal_value = Decimal(str(value))
        elif isinstance(value, (int, Decimal)):
            self.decimal_value = Decimal(value)
        elif isinstance(value, str):
            try:
                self.decimal_value = Decimal(value)
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid numeric value: '{value}'") from e
        else:
            raise TypeError(f"Value must be a number or string, got {type(value).__name__}")

        self.unit = unit

    def to_bytes(self) -> Decimal:
        """
        Convert the storage value to bytes with exact precision.

        Returns:
            Decimal: The value in bytes with exact precision.

        Examples:
            >>> value = StorageValue(1, StorageUnit.KIB)
            >>> value.to_bytes()
            Decimal('1024')
        """
        return self.decimal_value * Decimal(str(self.unit.value))

    def to_unit(self, target_unit: StorageUnit) -> Decimal:
        """
        Convert the storage value to a different unit.

        Args:
            target_unit: The target unit for conversion.

        Returns:
            Decimal: The converted value in the target unit.

        Examples:
            >>> value = StorageValue(1024, StorageUnit.BYTES)
            >>> value.to_unit(StorageUnit.KIB)
            Decimal('1')
        """
        if self.unit == target_unit:
            return self.decimal_value

        bytes_value = self.to_bytes()
        return bytes_value / Decimal(str(target_unit.value))

    def is_same_type(self, other: 'StorageValue') -> bool:
        """
        Check if another StorageValue has the same unit.

        Args:
            other: The other StorageValue to compare.

        Returns:
            bool: True if both values have the same unit.
        """
        return self.unit == other.unit

    def __repr__(self) -> str:
        """Return a detailed string representation for debugging."""
        return f"StorageValue({self.decimal_value}, {self.unit!r})"


class ConversionEngine:
    """
    High-performance conversion engine for storage unit transformations.

    This class handles all unit conversion operations with optimized caching
    and thread-safe performance. It serves as the specialized component
    for storage unit conversions within the refactored architecture.

    Attributes:
        storage_value (StorageValue): The core storage value to convert from.

    Examples:
        >>> value = StorageValue(Decimal("1024"), StorageUnit.BYTES)
        >>> engine = ConversionEngine(value)
        >>> result = engine.convert_to(StorageUnit.KIB)
        >>> print(result)
        StorageValue(Decimal('1'), StorageUnit.KIB)
    """

    def __init__(self, storage_value: StorageValue) -> None:
        """
        Initialize the conversion engine with a storage value.

        Args:
            storage_value: The core storage value to convert from.

        Raises:
            TypeError: If storage_value is not a StorageValue instance.
        """
        if not isinstance(storage_value, StorageValue):
            raise TypeError(f"ConversionEngine requires StorageValue, got {type(storage_value).__name__}")

        self.storage_value = storage_value
        self._conversion_cache: Dict[str, StorageValue] = {}
        self._cache_lock = threading.RLock()

    def convert_to(self, target_unit: StorageUnit) -> StorageValue:
        """
        Convert to a different storage unit.

        Args:
            target_unit: The target unit for conversion.

        Returns:
            StorageValue: New storage value in the target unit.

        Examples:
            >>> value = StorageValue(Decimal("1024"), StorageUnit.BYTES)
            >>> engine = ConversionEngine(value)
            >>> result = engine.convert_to(StorageUnit.KIB)
            >>> print(result.decimal_value)
            Decimal('1')
        """
        if self.storage_value.unit == target_unit:
            return self.storage_value

        cache_key = f"{self.storage_value.unit.name}_to_{target_unit.name}"

        # Check cache first
        if cache_key in self._conversion_cache:
            return self._conversion_cache[cache_key]

        # Perform conversion
        bytes_value = self.storage_value.to_bytes()
        target_decimal_value = bytes_value / Decimal(str(target_unit.value))

        # Create new StorageValue
        result = StorageValue(target_decimal_value, target_unit)

        # Cache result
        with self._cache_lock:
            self._conversion_cache[cache_key] = result

        return result

    def convert_to_bytes(self) -> Decimal:
        """
        Convert the storage value to bytes with exact precision.

        Returns:
            Decimal: The value in bytes with exact precision.

        Examples:
            >>> value = StorageValue(Decimal("1"), StorageUnit.KIB)
            >>> engine = ConversionEngine(value)
            >>> engine.convert_to_bytes()
            Decimal('1024')
        """
        return self.storage_value.to_bytes()

    def get_conversion_properties(self) -> Dict[str, 'Storage']:
        """
        Get all conversion properties as Storage objects (backward compatibility).

        This method generates Storage objects for all unit conversions,
        maintaining backward compatibility with the original Storage class.

        Returns:
            Dict[str, Storage]: Dictionary mapping unit names to Storage objects.

        Note:
            This method is provided for backward compatibility and creates
            Storage objects using the current Storage class implementation.
        """
        from .storage import Storage  # Import here to avoid circular imports

        properties = {}

        # Binary units
        binary_units = [
            ('BYTES', StorageUnit.BYTES),
            ('KIB', StorageUnit.KIB), ('MIB', StorageUnit.MIB), ('GIB', StorageUnit.GIB),
            ('TIB', StorageUnit.TIB), ('PIB', StorageUnit.PIB), ('EIB', StorageUnit.EIB),
            ('ZIB', StorageUnit.ZIB), ('YIB', StorageUnit.YIB)
        ]

        # Decimal units
        decimal_units = [
            ('KB', StorageUnit.KB), ('MB', StorageUnit.MB), ('GB', StorageUnit.GB),
            ('TB', StorageUnit.TB), ('PB', StorageUnit.PB), ('EB', StorageUnit.EB),
            ('ZB', StorageUnit.ZB), ('YB', StorageUnit.YB)
        ]

        # Bit units
        bit_units = [
            ('BITS', StorageUnit.BITS), ('KIBITS', StorageUnit.KIBITS),
            ('MIBITS', StorageUnit.MIBITS), ('GIBITS', StorageUnit.GIBITS),
            ('TIBITS', StorageUnit.TIBITS), ('PIBITS', StorageUnit.PIBITS),
            ('EIBITS', StorageUnit.EIBITS), ('ZIBITS', StorageUnit.ZIBITS),
            ('YIBITS', StorageUnit.YIBITS), ('KIBITS', StorageUnit.KBITS),
            ('MBITS', StorageUnit.MBITS), ('GBITS', StorageUnit.GBITS),
            ('TBITS', StorageUnit.TBITS), ('PBITS', StorageUnit.PBITS),
            ('EBITS', StorageUnit.EBITS), ('ZBITS', StorageUnit.ZBITS),
            ('YBITS', StorageUnit.YBITS)
        ]

        # Create Storage objects for all units
        for prop_name, unit in binary_units + decimal_units + bit_units:
            converted_value = self.convert_to(unit)
            # Create Storage object using the current constructor
            properties[prop_name] = Storage(
                converted_value.decimal_value,
                unit
            )

        return properties

    def clear_cache(self) -> None:
        """Clear the conversion cache to free memory."""
        with self._cache_lock:
            self._conversion_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics for monitoring.

        Returns:
            Dict[str, int]: Dictionary with cache size and related stats.
        """
        return {
            'cache_size': len(self._conversion_cache),
            'cache_entries': list(self._conversion_cache.keys())
        }


class StringParser:
    """
    Specialized parser for storage value string representations.

    This class handles the parsing of storage value strings with robust
    error handling and format validation. It serves as the focused
    component for string parsing within the refactored architecture.

    Examples:
        >>> parser = StringParser()
        >>> value, unit = parser.parse("1.5 MB")
        >>> print(value)
        Decimal('1.5')
        >>> print(unit)
        StorageUnit.MB
    """

    def __init__(self) -> None:
        """Initialize the string parser with compiled patterns."""
        # Pattern to match number and optional unit with optional whitespace
        # Supports: "123", "123.45", "123 mb", "123.45mb", "123,45 gb", etc.
        self._pattern = re.compile(r'^([0-9]*\.?[0-9]+)\s*([a-z]*)$', re.IGNORECASE)
        self._unit_aliases = StorageUnit.get_unit_aliases()

    def parse(self, string: str, default_unit: Optional[StorageUnit] = None) -> tuple[Decimal, StorageUnit]:
        """
        Parse a storage value string into decimal value and unit.

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
            tuple[Decimal, StorageUnit]: The parsed decimal value and storage unit.

        Raises:
            TypeError: If input is not a string.
            ValueError: If the input string is invalid or cannot be parsed.

        Examples:
            >>> parser = StringParser()
            >>> value, unit = parser.parse("1.5 MB")
            >>> print(value)
            Decimal('1.5')
            >>> print(unit)
            StorageUnit.MB

            >>> value, unit = parser.parse("1,024 KiB")
            >>> print(value)
            Decimal('1024')
            >>> print(unit)
            StorageUnit.KIB

            >>> value, unit = parser.parse("500")  # defaults to bytes
            >>> print(value)
            Decimal('500')
            >>> print(unit)
            StorageUnit.BYTES
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

        # Match the pattern
        match = self._pattern.match(normalized)

        if not match:
            raise ValueError(f"Invalid format: '{string}'. Expected format: 'number [unit]'")

        value_str = match.group(1)
        unit_str = match.group(2) or ''

        # Parse the numeric value using Decimal for exact precision
        try:
            value = Decimal(value_str)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid numeric value: '{value_str}'") from e

        # Find the unit, default to provided default_unit if not found
        unit = self._unit_aliases.get(unit_str.lower(), default_unit)

        return value, unit

    def parse_to_storage_value(self, string: str, default_unit: Optional[StorageUnit] = None) -> StorageValue:
        """
        Parse a string directly into a StorageValue object.

        Args:
            string: A string representing the storage value.
            default_unit: The unit to use if no unit is found or recognized.

        Returns:
            StorageValue: A new StorageValue instance.

        Examples:
            >>> parser = StringParser()
            >>> storage_value = parser.parse_to_storage_value("1.5 MB")
            >>> print(storage_value.decimal_value)
            Decimal('1.5')
            >>> print(storage_value.unit)
            StorageUnit.MB
        """
        value, unit = self.parse(string, default_unit)
        return StorageValue(value, unit)

    def is_valid_format(self, string: str) -> bool:
        """
        Check if a string has a valid storage value format.

        Args:
            string: The string to validate.

        Returns:
            bool: True if the string format is valid, False otherwise.

        Examples:
            >>> parser = StringParser()
            >>> parser.is_valid_format("1.5 MB")
            True
            >>> parser.is_valid_format("invalid")
            False
        """
        try:
            self.parse(string)
            return True
        except (TypeError, ValueError):
            return False

    def get_normalized_string(self, string: str) -> str:
        """
        Get a normalized version of the storage string.

        Args:
            string: The input string to normalize.

        Returns:
            str: Normalized string with standard formatting.

        Examples:
            >>> parser = StringParser()
            >>> parser.get_normalized_string("1,5 mb")
            '1.5 mb'
        """
        if not isinstance(string, str):
            raise TypeError(f"Input must be a string, got {type(string).__name__}")

        # Normalize: strip whitespace, convert to lowercase, replace comma with dot
        normalized = string.strip().lower().replace(',', '.')
        return normalized

    def update_unit_aliases(self) -> None:
        """
        Update the cached unit aliases mapping.

        This method should be called if the StorageUnit enum is modified
        at runtime to ensure the parser has the latest aliases.
        """
        self._unit_aliases = StorageUnit.get_unit_aliases()


class ArithmeticEngine:
    """
    Specialized engine for storage arithmetic operations.

    This class handles all arithmetic operations between storage values
    with proper validation, unit handling, and exact precision. It serves
    as the focused component for arithmetic within the refactored architecture.

    Attributes:
        left_value (StorageValue): The left operand for arithmetic operations.

    Examples:
        >>> value1 = StorageValue(Decimal("1024"), StorageUnit.BYTES)
        >>> value2 = StorageValue(Decimal("1024"), StorageUnit.BYTES)
        >>> engine = ArithmeticEngine(value1)
        >>> result = engine.add(value2)
        >>> print(result.decimal_value)
        Decimal('2048')
    """

    def __init__(self, left_value: StorageValue) -> None:
        """
        Initialize the arithmetic engine with a left operand value.

        Args:
            left_value: The left operand StorageValue for arithmetic operations.

        Raises:
            TypeError: If left_value is not a StorageValue instance.
        """
        if not isinstance(left_value, StorageValue):
            raise TypeError(f"ArithmeticEngine requires StorageValue, got {type(left_value).__name__}")

        self.left_value = left_value

    def add(self, right_value: StorageValue) -> StorageValue:
        """
        Add another storage value to this one.

        Args:
            right_value: The StorageValue to add.

        Returns:
            StorageValue: A new StorageValue with the summed value.

        Raises:
            TypeError: If right_value is not a StorageValue.

        Examples:
            >>> value1 = StorageValue(Decimal("1"), StorageUnit.KIB)
            >>> value2 = StorageValue(Decimal("512"), StorageUnit.BYTES)
            >>> engine = ArithmeticEngine(value1)
            >>> result = engine.add(value2)
            >>> print(result.decimal_value)
            Decimal('1536')
        """
        if not isinstance(right_value, StorageValue):
            raise TypeError(f"Can only add StorageValue, got {type(right_value).__name__}")

        # If both operands have the same unit, preserve that unit
        if self.left_value.unit == right_value.unit:
            total_value = self.left_value.decimal_value + right_value.decimal_value
            return StorageValue(total_value, self.left_value.unit)

        # Different units: convert to bytes
        left_bytes = self.left_value.to_bytes()
        right_bytes = right_value.to_bytes()
        total_bytes = left_bytes + right_bytes

        return StorageValue(total_bytes, StorageUnit.BYTES)

    def subtract(self, right_value: StorageValue) -> StorageValue:
        """
        Subtract another storage value from this one.

        Args:
            right_value: The StorageValue to subtract.

        Returns:
            StorageValue: A new StorageValue with the difference.

        Raises:
            TypeError: If right_value is not a StorageValue.
            ValueError: If result would be negative.

        Examples:
            >>> value1 = StorageValue(Decimal("2"), StorageUnit.KIB)
            >>> value2 = StorageValue(Decimal("512"), StorageUnit.BYTES)
            >>> engine = ArithmeticEngine(value1)
            >>> result = engine.subtract(value2)
            >>> print(result.decimal_value)
            Decimal('1536')
        """
        if not isinstance(right_value, StorageValue):
            raise TypeError(f"Can only subtract StorageValue, got {type(right_value).__name__}")

        # If both operands have the same unit, preserve that unit
        if self.left_value.unit == right_value.unit:
            result_value = self.left_value.decimal_value - right_value.decimal_value
            if result_value < 0:
                raise ValueError("Storage subtraction result cannot be negative")
            return StorageValue(result_value, self.left_value.unit)

        # Different units: convert to bytes
        left_bytes = self.left_value.to_bytes()
        right_bytes = right_value.to_bytes()
        result_bytes = left_bytes - right_bytes

        if result_bytes < Decimal('0'):
            raise ValueError("Storage subtraction result cannot be negative")

        return StorageValue(result_bytes, StorageUnit.BYTES)

    def multiply(self, factor: Union[int, float, Decimal]) -> StorageValue:
        """
        Multiply this storage value by a numeric factor.

        Args:
            factor: The numeric factor to multiply by.

        Returns:
            StorageValue: A new StorageValue with the multiplied value.

        Raises:
            TypeError: If factor is not a numeric type.
            ValueError: If factor is negative.

        Examples:
            >>> value = StorageValue(Decimal("1"), StorageUnit.KIB)
            >>> engine = ArithmeticEngine(value)
            >>> result = engine.multiply(2)
            >>> print(result.decimal_value)
            Decimal('2')
        """
        if not isinstance(factor, (int, float, Decimal)):
            raise TypeError(f"Factor must be numeric, got {type(factor).__name__}")

        if factor < 0:
            raise ValueError("Cannot multiply storage by negative factor")

        # Convert factor to Decimal for exact precision
        if isinstance(factor, float):
            factor = Decimal(str(factor))
        elif isinstance(factor, int):
            factor = Decimal(factor)

        result_value = self.left_value.decimal_value * factor
        return StorageValue(result_value, self.left_value.unit)

    def divide(self, divisor: Union[int, float, Decimal]) -> StorageValue:
        """
        Divide this storage value by a numeric divisor.

        Args:
            divisor: The numeric divisor to divide by.

        Returns:
            StorageValue: A new StorageValue with the divided value.

        Raises:
            TypeError: If divisor is not a numeric type.
            ValueError: If divisor is zero or negative.

        Examples:
            >>> value = StorageValue(Decimal("2"), StorageUnit.KIB)
            >>> engine = ArithmeticEngine(value)
            >>> result = engine.divide(2)
            >>> print(result.decimal_value)
            Decimal('1')
        """
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError(f"Divisor must be numeric, got {type(divisor).__name__}")

        if divisor <= 0:
            raise ValueError("Divisor must be positive")

        # Convert divisor to Decimal for exact precision
        if isinstance(divisor, float):
            divisor = Decimal(str(divisor))
        elif isinstance(divisor, int):
            divisor = Decimal(divisor)

        result_value = self.left_value.decimal_value / divisor
        return StorageValue(result_value, self.left_value.unit)

    def divide_by_storage(self, divisor: StorageValue) -> Decimal:
        """
        Divide this storage value by another storage value.

        Args:
            divisor: The StorageValue to divide by.

        Returns:
            Decimal: The ratio as a Decimal.

        Raises:
            TypeError: If divisor is not a StorageValue.
            ValueError: If divisor is zero.

        Examples:
            >>> value1 = StorageValue(Decimal("2"), StorageUnit.KIB)
            >>> value2 = StorageValue(Decimal("1"), StorageUnit.KIB)
            >>> engine = ArithmeticEngine(value1)
            >>> result = engine.divide_by_storage(value2)
            >>> print(result)
            Decimal('2')
        """
        if not isinstance(divisor, StorageValue):
            raise TypeError(f"Can only divide by StorageValue, got {type(divisor).__name__}")

        if divisor.decimal_value == Decimal('0'):
            raise ValueError("Cannot divide by zero storage value")

        # Convert both to bytes for division
        left_bytes = self.left_value.to_bytes()
        right_bytes = divisor.to_bytes()

        return left_bytes / right_bytes

    def floor_divide(self, divisor: Union[int, float, Decimal]) -> StorageValue:
        """
        Perform floor division of this storage value by a numeric divisor.

        Args:
            divisor: The numeric divisor to divide by.

        Returns:
            StorageValue: A new StorageValue with the floored result.

        Raises:
            TypeError: If divisor is not a numeric type.
            ValueError: If divisor is zero or negative.

        Examples:
            >>> value = StorageValue(Decimal("3"), StorageUnit.KIB)
            >>> engine = ArithmeticEngine(value)
            >>> result = engine.floor_divide(2)
            >>> print(result.decimal_value)
            Decimal('1')
        """
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError(f"Divisor must be numeric, got {type(divisor).__name__}")

        if divisor <= 0:
            raise ValueError("Divisor must be positive")

        # Convert divisor to Decimal for exact precision
        if isinstance(divisor, float):
            divisor = Decimal(str(divisor))
        elif isinstance(divisor, int):
            divisor = Decimal(divisor)

        result_value = self.left_value.decimal_value // divisor
        return StorageValue(result_value, self.left_value.unit)

    def modulo(self, divisor: Union[int, float, Decimal]) -> StorageValue:
        """
        Get the remainder after division of this storage value by a numeric divisor.

        Args:
            divisor: The numeric divisor to divide by.

        Returns:
            StorageValue: A new StorageValue with the remainder.

        Raises:
            TypeError: If divisor is not a numeric type.
            ValueError: If divisor is zero or negative.

        Examples:
            >>> value = StorageValue(Decimal("3"), StorageUnit.KIB)
            >>> engine = ArithmeticEngine(value)
            >>> result = engine.modulo(2)
            >>> print(result.decimal_value)
            Decimal('1')
        """
        if not isinstance(divisor, (int, float, Decimal)):
            raise TypeError(f"Divisor must be numeric, got {type(divisor).__name__}")

        if divisor <= 0:
            raise ValueError("Divisor must be positive")

        # Convert divisor to Decimal for exact precision
        if isinstance(divisor, float):
            divisor = Decimal(str(divisor))
        elif isinstance(divisor, int):
            divisor = Decimal(divisor)

        result_value = self.left_value.decimal_value % divisor
        return StorageValue(result_value, self.left_value.unit)


class PerformanceManager:
    """
    Centralized performance optimization and caching manager.

    This class manages all performance-related optimizations including
    decimal caching, memory management, and performance monitoring.
    It serves as the focused component for performance within the
    refactored architecture.

    Attributes:
        max_cache_size (int): Maximum size for decimal caches.
        cache_stats (Dict[str, int]): Statistics for cache monitoring.

    Examples:
        >>> manager = PerformanceManager()
        >>> decimal_value = manager.get_cached_decimal("123.45")
        >>> stats = manager.get_cache_stats()
        >>> print(stats['decimal_cache_size'])
        1
    """

    def __init__(self, max_cache_size: int = 1000) -> None:
        """
        Initialize the performance manager.

        Args:
            max_cache_size: Maximum size for decimal caches.
        """
        self.max_cache_size = max_cache_size

        # Decimal caching for performance
        self._decimal_cache: Dict[str, Decimal] = {}
        self._decimal_cache_lock = threading.RLock()

        # Performance statistics
        self._stats = {
            'decimal_cache_hits': 0,
            'decimal_cache_misses': 0,
            'conversion_cache_hits': 0,
            'conversion_cache_misses': 0
        }

    def get_cached_decimal(self, value_str: str) -> Decimal:
        """
        Get a cached Decimal value or create and cache it.

        This method improves performance by caching frequently used Decimal values
        to avoid repeated string-to-Decimal conversions.

        Args:
            value_str: String representation of the decimal value.

        Returns:
            Decimal: The cached or newly created Decimal value.

        Examples:
            >>> manager = PerformanceManager()
            >>> value = manager.get_cached_decimal("123.45")
            >>> print(value)
            Decimal('123.45')
        """
        with self._decimal_cache_lock:
            if value_str in self._decimal_cache:
                self._stats['decimal_cache_hits'] += 1
                return self._decimal_cache[value_str]

            # Cache miss - create new Decimal and cache it
            self._stats['decimal_cache_misses'] += 1
            decimal_value = Decimal(value_str)

            # Simple cache eviction if cache is full
            if len(self._decimal_cache) >= self.max_cache_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self._decimal_cache))
                del self._decimal_cache[oldest_key]

            self._decimal_cache[value_str] = decimal_value
            return decimal_value

    def clear_decimal_cache(self) -> None:
        """Clear the decimal cache to free memory."""
        with self._decimal_cache_lock:
            self._decimal_cache.clear()

    def get_cache_stats(self) -> Dict[str, any]:
        """
        Get comprehensive cache statistics.

        Returns:
            Dict[str, any]: Dictionary containing all cache statistics.

        Examples:
            >>> manager = PerformanceManager()
            >>> stats = manager.get_cache_stats()
            >>> print(f"Cache hit rate: {stats['decimal_cache_hit_rate']:.2%}")
        """
        decimal_hits = self._stats['decimal_cache_hits']
        decimal_misses = self._stats['decimal_cache_misses']
        decimal_total = decimal_hits + decimal_misses

        return {
            'decimal_cache_size': len(self._decimal_cache),
            'decimal_cache_hits': decimal_hits,
            'decimal_cache_misses': decimal_misses,
            'decimal_cache_hit_rate': decimal_hits / decimal_total if decimal_total > 0 else 0.0,
            'conversion_cache_hits': self._stats['conversion_cache_hits'],
            'conversion_cache_misses': self._stats['conversion_cache_misses'],
            'max_cache_size': self.max_cache_size
        }

    def reset_stats(self) -> None:
        """Reset all performance statistics."""
        with self._decimal_cache_lock:
            self._stats = {
                'decimal_cache_hits': 0,
                'decimal_cache_misses': 0,
                'conversion_cache_hits': 0,
                'conversion_cache_misses': 0
            }

    def optimize_memory_usage(self) -> None:
        """
        Optimize memory usage by clearing caches if they're too large.

        This method checks cache sizes and clears them if they exceed
        certain thresholds to prevent memory bloat.
        """
        with self._decimal_cache_lock:
            # Clear decimal cache if it's getting too large
            if len(self._decimal_cache) > self.max_cache_size * 0.8:
                # Keep only the most recently used items
                items = list(self._decimal_cache.items())
                keep_count = int(self.max_cache_size * 0.5)  # Keep 50% of max

                self._decimal_cache.clear()
                for key, value in items[-keep_count:]:  # Keep most recent
                    self._decimal_cache[key] = value

    def get_performance_report(self) -> str:
        """
        Generate a human-readable performance report.

        Returns:
            str: Formatted performance report.

        Examples:
            >>> manager = PerformanceManager()
            >>> report = manager.get_performance_report()
            >>> print(report)
            Performance Report:
            - Decimal Cache: 100 entries, 85% hit rate
            - Memory Usage: Optimized
        """
        stats = self.get_cache_stats()
        decimal_rate = stats['decimal_cache_hit_rate']

        report = [
            "Performance Report:",
            f"- Decimal Cache: {stats['decimal_cache_size']} entries, {decimal_rate:.1%} hit rate",
            f"- Max Cache Size: {stats['max_cache_size']} entries"
        ]

        if stats['decimal_cache_size'] > stats['max_cache_size'] * 0.8:
            report.append("- Memory Usage: High (consider clearing cache)")
        else:
            report.append("- Memory Usage: Optimized")

        return "\n".join(report)

    def record_conversion_hit(self) -> None:
        """Record a conversion cache hit for statistics."""
        self._stats['conversion_cache_hits'] += 1

    def record_conversion_miss(self) -> None:
        """Record a conversion cache miss for statistics."""
        self._stats['conversion_cache_misses'] += 1

    @property
    def cache_hit_rate(self) -> float:
        """
        Get the overall cache hit rate.

        Returns:
            float: Overall cache hit rate as a percentage.
        """
        total_hits = self._stats['decimal_cache_hits'] + self._stats['conversion_cache_hits']
        total_misses = self._stats['decimal_cache_misses'] + self._stats['conversion_cache_misses']
        total_operations = total_hits + total_misses

        return total_hits / total_operations if total_operations > 0 else 0.0