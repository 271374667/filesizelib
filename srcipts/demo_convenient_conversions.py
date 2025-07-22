#!/usr/bin/env python3
"""
Demonstration of convenient conversion methods in the bytesize library.

This script showcases the new convenient conversion methods that provide
shortcuts for common unit conversions.
"""

from bytesize import Storage, StorageUnit

def demo_binary_conversions():
    """Demonstrate binary unit conversion methods."""
    print("📊 Binary Unit Conversions")
    print("=" * 50)
    
    # Create storage instances
    storage = Storage(2, StorageUnit.GIB)
    print(f"Original: {storage}")
    
    # Use convenient binary conversion methods
    print(f"As MiB:   {storage.convert_to_mib()}")
    print(f"As KiB:   {storage.convert_to_kib()}")
    print(f"As TiB:   {storage.convert_to_tib()}")
    
    # Compare with traditional method
    print(f"\nTraditional method:")
    print(f"As MiB:   {storage.convert_to(StorageUnit.MIB)}")
    print()

def demo_decimal_conversions():
    """Demonstrate decimal unit conversion methods."""
    print("📈 Decimal Unit Conversions")
    print("=" * 50)
    
    # Create storage instance
    storage = Storage(1.5, StorageUnit.TB)
    print(f"Original: {storage}")
    
    # Use convenient decimal conversion methods
    print(f"As GB:    {storage.convert_to_gb()}")
    print(f"As MB:    {storage.convert_to_mb()}")
    print(f"As KB:    {storage.convert_to_kb()}")
    
    # Show precision
    print(f"As bytes: {storage.convert_to_bytes():,.0f} bytes")
    print()

def demo_bit_conversions():
    """Demonstrate bit unit conversion methods."""
    print("🔥 Bit Unit Conversions")
    print("=" * 50)
    
    # Create storage instance
    storage = Storage(100, StorageUnit.MB)
    print(f"Original:     {storage}")
    
    # Use convenient bit conversion methods
    print(f"As megabits:  {storage.convert_to_megabits()}")
    print(f"As kilobits:  {storage.convert_to_kilobits()}")
    print(f"As gigabits:  {storage.convert_to_gigabits()}")
    print(f"As bits:      {storage.convert_to_bits():,.0f} bits")
    print()

def demo_chaining_conversions():
    """Demonstrate chaining conversions."""
    print("🔗 Chaining Conversions")
    print("=" * 50)
    
    # Start with a storage value
    original = Storage(4096, StorageUnit.MIB)
    print(f"Original:      {original}")
    
    # Chain multiple conversions
    result = (original
              .convert_to_gib()    # Convert to GiB
              .convert_to_gb()     # Convert to GB
              .convert_to_mb())    # Convert to MB
    
    print(f"After chain:   {result}")
    print(f"Bytes check:   {abs(original.convert_to_bytes() - result.convert_to_bytes()) < 1e-6}")
    print()

def demo_arithmetic_with_conversions():
    """Demonstrate arithmetic operations with converted values."""
    print("🧮 Arithmetic with Conversions")
    print("=" * 50)
    
    # Create storage instances
    file1 = Storage(1.5, StorageUnit.GIB).convert_to_mib()
    file2 = Storage(512, StorageUnit.MIB)
    
    print(f"File 1:        {file1}")
    print(f"File 2:        {file2}")
    
    # Perform arithmetic
    total = file1 + file2
    difference = file1 - file2
    ratio = file1 / file2
    
    print(f"Total:         {total}")
    print(f"Difference:    {difference}")
    print(f"Ratio:         {ratio:.2f}")
    print()

def demo_real_world_examples():
    """Demonstrate real-world usage examples."""
    print("🌍 Real-World Examples")
    print("=" * 50)
    
    # Download scenario
    print("💾 Download Scenario:")
    video_file = Storage.parse("1.4 GB")
    print(f"Video file:    {video_file}")
    print(f"In MiB:        {video_file.convert_to_mib()}")
    print(f"In megabits:   {video_file.convert_to_megabits()}")
    
    # Storage capacity scenario
    print("\n💿 Storage Capacity:")
    photos = Storage.parse("2.8 MiB") * 1000  # 1000 photos
    music = Storage.parse("4.5 MB") * 300     # 300 songs
    
    print(f"1000 photos:   {photos.convert_to_gib()}")
    print(f"300 songs:     {music.convert_to_gb()}")
    
    total_media = photos + music
    print(f"Total:         {total_media.auto_scale()}")
    
    # Available storage
    ssd_capacity = Storage(500, StorageUnit.GB)
    remaining = ssd_capacity - total_media
    print(f"Remaining:     {remaining.convert_to_gb()}")
    print()

def demo_convenience_vs_traditional():
    """Compare convenient methods vs traditional convert_to."""
    print("⚖️  Convenient vs Traditional Methods")
    print("=" * 50)
    
    storage = Storage(2048, StorageUnit.KIB)
    
    print("Convenient methods:")
    print(f"  storage.convert_to_mib()     → {storage.convert_to_mib()}")
    print(f"  storage.convert_to_gb()      → {storage.convert_to_gb()}")
    print(f"  storage.convert_to_megabits() → {storage.convert_to_megabits()}")
    
    print("\nTraditional methods:")
    print(f"  storage.convert_to(StorageUnit.MIB)      → {storage.convert_to(StorageUnit.MIB)}")
    print(f"  storage.convert_to(StorageUnit.GB)       → {storage.convert_to(StorageUnit.GB)}")
    print(f"  storage.convert_to(StorageUnit.MEGABITS) → {storage.convert_to(StorageUnit.MEGABITS)}")
    
    print("\n✅ Both methods produce identical results!")
    print()

def main():
    """Run all demonstrations."""
    print("🔢 Bytesize Library - Convenient Conversion Methods Demo")
    print("=" * 60)
    print()
    
    demo_binary_conversions()
    demo_decimal_conversions() 
    demo_bit_conversions()
    demo_chaining_conversions()
    demo_arithmetic_with_conversions()
    demo_real_world_examples()
    demo_convenience_vs_traditional()
    
    print("🎉 Demo completed! The convenient conversion methods provide")
    print("   easy-to-use shortcuts while maintaining full compatibility")
    print("   with the existing convert_to() method.")

if __name__ == "__main__":
    main()