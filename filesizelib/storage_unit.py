"""
Storage unit enumeration module.

This module defines the StorageUnit enum which represents all supported
storage units with their conversion factors to bytes.
"""

from enum import Enum
from typing import Dict, Set


class StorageUnit(Enum):
    """
    Enumeration of storage units with their byte conversion factors.
    
    This enum defines both binary (base 1024) and decimal (base 1000) 
    storage units commonly used in computing and storage devices.
    
    Binary units (powers of 1024):
        - BYTES, KIB, MIB, GIB, TIB, PIB, EIB, ZIB, YIB
    
    Decimal units (powers of 1000):
        - KB, MB, GB, TB, PB, EB, ZB, YB
    
    Bit units:
        - BITS, KILOBITS, MEGABITS, GIGABITS, TERABITS
    
    Each enum value represents the number of bytes in one unit.
    """
    
    # Special units
    AUTO = -1  # Special value for automatic parsing
    
    # Byte units
    BYTES = 1
    BYTE = 1  # Alias for BYTES
    
    # Binary units (powers of 1024)
    KIB = 1024  # Kibibyte
    MIB = 1024 ** 2  # Mebibyte  
    GIB = 1024 ** 3  # Gibibyte
    TIB = 1024 ** 4  # Tebibyte
    PIB = 1024 ** 5  # Pebibyte
    EIB = 1024 ** 6  # Exbibyte
    ZIB = 1024 ** 7  # Zebibyte
    YIB = 1024 ** 8  # Yobibyte
    
    # Decimal units (powers of 1000)
    KB = 1000  # Kilobyte
    MB = 1000 ** 2  # Megabyte
    GB = 1000 ** 3  # Gigabyte
    TB = 1000 ** 4  # Terabyte
    PB = 1000 ** 5  # Petabyte
    EB = 1000 ** 6  # Exabyte
    ZB = 1000 ** 7  # Zettabyte
    YB = 1000 ** 8  # Yottabyte
    
    # Bit units (8 bits = 1 byte)
    BITS = 1 / 8
    BIT = 1 / 8  # Alias for BITS
    KILOBITS = 1000 / 8  # Kilobit
    MEGABITS = (1000 ** 2) / 8  # Megabit
    GIGABITS = (1000 ** 3) / 8  # Gigabit
    TERABITS = (1000 ** 4) / 8  # Terabit
    PETABITS = (1000 ** 5) / 8  # Petabit
    EXABITS = (1000 ** 6) / 8  # Exabit
    ZETTABITS = (1000 ** 7) / 8  # Zettabit
    YOTTABITS = (1000 ** 8) / 8  # Yottabit
    
    @classmethod
    def get_unit_aliases(cls) -> Dict[str, 'StorageUnit']:
        """
        Get a mapping of unit name aliases to StorageUnit enum values.
        
        This mapping supports case-insensitive parsing of unit names
        including common abbreviations and alternative spellings.
        
        Returns:
            Dict[str, StorageUnit]: Mapping of lowercase unit names to enum values.
        """
        aliases = {
            # Bytes
            'b': cls.BYTES,
            'byte': cls.BYTES,
            'bytes': cls.BYTES,
            
            # Binary units
            'kib': cls.KIB,
            'ki': cls.KIB,
            'kibibyte': cls.KIB,
            'kibibytes': cls.KIB,
            
            'mib': cls.MIB,
            'mi': cls.MIB,
            'mebibyte': cls.MIB,
            'mebibytes': cls.MIB,
            
            'gib': cls.GIB,
            'gi': cls.GIB,
            'gibibyte': cls.GIB,
            'gibibytes': cls.GIB,
            
            'tib': cls.TIB,
            'ti': cls.TIB,
            'tebibyte': cls.TIB,
            'tebibytes': cls.TIB,
            
            'pib': cls.PIB,
            'pi': cls.PIB,
            'pebibyte': cls.PIB,
            'pebibytes': cls.PIB,
            
            'eib': cls.EIB,
            'ei': cls.EIB,
            'exbibyte': cls.EIB,
            'exbibytes': cls.EIB,
            
            'zib': cls.ZIB,
            'zi': cls.ZIB,
            'zebibyte': cls.ZIB,
            'zebibytes': cls.ZIB,
            
            'yib': cls.YIB,
            'yi': cls.YIB,
            'yobibyte': cls.YIB,
            'yobibytes': cls.YIB,
            
            # Decimal units
            'kb': cls.KB,
            'k': cls.KB,
            'kilobyte': cls.KB,
            'kilobytes': cls.KB,
            
            'mb': cls.MB,
            'm': cls.MB,
            'megabyte': cls.MB,
            'megabytes': cls.MB,
            
            'gb': cls.GB,
            'g': cls.GB,
            'gigabyte': cls.GB,
            'gigabytes': cls.GB,
            
            'tb': cls.TB,
            't': cls.TB,
            'terabyte': cls.TB,
            'terabytes': cls.TB,
            
            'pb': cls.PB,
            'p': cls.PB,
            'petabyte': cls.PB,
            'petabytes': cls.PB,
            
            'eb': cls.EB,
            'e': cls.EB,
            'exabyte': cls.EB,
            'exabytes': cls.EB,
            
            'zb': cls.ZB,
            'z': cls.ZB,
            'zettabyte': cls.ZB,
            'zettabytes': cls.ZB,
            
            'yb': cls.YB,
            'y': cls.YB,
            'yottabyte': cls.YB,
            'yottabytes': cls.YB,
            
            # Bit units
            'bit': cls.BITS,
            'bits': cls.BITS,
            
            'kilobit': cls.KILOBITS,
            'kilobits': cls.KILOBITS,
            'kbit': cls.KILOBITS,
            'kbits': cls.KILOBITS,
            
            'megabit': cls.MEGABITS,
            'megabits': cls.MEGABITS,
            'mbit': cls.MEGABITS,
            'mbits': cls.MEGABITS,
            
            'gigabit': cls.GIGABITS,
            'gigabits': cls.GIGABITS,
            'gbit': cls.GIGABITS,
            'gbits': cls.GIGABITS,
            
            'terabit': cls.TERABITS,
            'terabits': cls.TERABITS,
            'tbit': cls.TERABITS,
            'tbits': cls.TERABITS,
            
            'petabit': cls.PETABITS,
            'petabits': cls.PETABITS,
            'pbit': cls.PETABITS,
            'pbits': cls.PETABITS,
            
            'exabit': cls.EXABITS,
            'exabits': cls.EXABITS,
            'ebit': cls.EXABITS,
            'ebits': cls.EXABITS,
            
            'zettabit': cls.ZETTABITS,
            'zettabits': cls.ZETTABITS,
            'zbit': cls.ZETTABITS,
            'zbits': cls.ZETTABITS,
            
            'yottabit': cls.YOTTABITS,
            'yottabits': cls.YOTTABITS,
            'ybit': cls.YOTTABITS,
            'ybits': cls.YOTTABITS,
        }
        
        return aliases
    
    @classmethod
    def get_binary_units(cls) -> Set['StorageUnit']:
        """
        Get a set of binary storage units (powers of 1024).
        
        Returns:
            Set[StorageUnit]: Set of binary storage units.
        """
        return {
            cls.BYTES, cls.KIB, cls.MIB, cls.GIB, 
            cls.TIB, cls.PIB, cls.EIB, cls.ZIB, cls.YIB
        }
    
    @classmethod
    def get_decimal_units(cls) -> Set['StorageUnit']:
        """
        Get a set of decimal storage units (powers of 1000).
        
        Returns:
            Set[StorageUnit]: Set of decimal storage units.
        """
        return {
            cls.KB, cls.MB, cls.GB, cls.TB, 
            cls.PB, cls.EB, cls.ZB, cls.YB
        }
    
    @classmethod  
    def get_bit_units(cls) -> Set['StorageUnit']:
        """
        Get a set of bit-based storage units.
        
        Returns:
            Set[StorageUnit]: Set of bit storage units.
        """
        return {
            cls.BITS, cls.KILOBITS, cls.MEGABITS, cls.GIGABITS,
            cls.TERABITS, cls.PETABITS, cls.EXABITS, 
            cls.ZETTABITS, cls.YOTTABITS
        }
    
    @classmethod  
    def get_special_units(cls) -> Set['StorageUnit']:
        """
        Get a set of special storage units (e.g., AUTO).
        
        Returns:
            Set[StorageUnit]: Set of special storage units.
        """
        return {cls.AUTO}
    
    def is_binary(self) -> bool:
        """
        Check if this unit is a binary unit (power of 1024).
        
        Returns:
            bool: True if this is a binary unit, False otherwise.
        """
        return self in self.get_binary_units()
    
    def is_decimal(self) -> bool:
        """
        Check if this unit is a decimal unit (power of 1000).
        
        Returns:
            bool: True if this is a decimal unit, False otherwise.
        """
        return self in self.get_decimal_units()
    
    def is_bit_unit(self) -> bool:
        """
        Check if this unit is a bit-based unit.
        
        Returns:
            bool: True if this is a bit unit, False otherwise.
        """
        return self in self.get_bit_units()